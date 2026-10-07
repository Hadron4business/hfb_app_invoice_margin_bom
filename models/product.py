# -*- coding: utf-8 -*-
#################################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2017-2026 Hadron for Business sp. z o.o. (http://hadronforbusiness.com)
#
# This program is proprietary software, licensed under the Odoo Proprietary
# License v1.0 (OPL-1). Its use is governed by the Odoo Apps terms available
# at https://www.odoo.com/documentation/user/legal/licenses.html and the
# license agreement accepted at purchase / installation.
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the
# Software or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in
# all copies or substantial portions of the Software.
#
#################################################################################
"""	@version	17.0.1.0.2
	@owner  Hadron for Business
	@author Hadron for Business sp. z o.o.
	@date   2026.10.07

	Invoice Cost & Margin - product cost engine
	Cost of a product in the company currency: skipped, fixed cost, multi-level
	explosion of the bill of materials (with operations) or, for purchased
	products, the product Cost or the last purchase price. Per-product
	exceptions are set on the product template.
"""
from odoo import _, fields, models

BOM_MAX_DEPTH = 20

COST_SOURCES = [
    ('none', "No Product"),
    ('skipped', "Skipped"),
    ('fixed', "Fixed Cost"),
    ('standard', "Product Cost"),
    ('last_purchase', "Last Purchase Price"),
    ('bom', "Bill of Materials"),
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bom_cost_skip = fields.Boolean(
        string="Exclude from Invoice Cost",
        help="Cost 0 in the invoice margin, both as an invoice line and as a component of a bill of materials "
             "(e.g. a re-invoiced service).")
    bom_cost_no_explode = fields.Boolean(
        string="Do Not Explode Bill of Materials",
        help="Use the product Cost even if the product has a bill of materials.")
    bom_cost_fixed_ok = fields.Boolean(
        string="Use a Fixed Cost",
        help="Use the fixed unit cost below instead of the bill of materials or the product Cost.")
    bom_cost_fixed = fields.Monetary(
        string="Fixed Cost", currency_field='bom_cost_fixed_currency_id',
        help="Fixed cost per unit of the product unit of measure.")
    bom_cost_fixed_currency_id = fields.Many2one(
        'res.currency', string="Fixed Cost Currency",
        default=lambda self: self.env.company.currency_id,
        help="Converted to the company currency at the invoice date.")
    bom_cost_leaf_source = fields.Selection(
        [('default', "Company Setting"), ('standard', "Product Cost"), ('last_purchase', "Last Purchase Price")],
        string="Cost when Purchased", default='default', required=True,
        help="How the product is costed when it has no bill of materials to explode.")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _bom_margin_cost(self, quantity, uom, date, company, visited=(), depth=0):
        """Cost of `quantity` (in `uom`) of this product, in the company currency.

        :return: (cost, source, warnings)
        """
        self.ensure_one()
        product = self.with_company(company)
        warnings = []
        if uom and uom != product.uom_id:
            quantity = uom._compute_quantity(quantity, product.uom_id)

        if product.bom_cost_skip:
            return 0.0, 'skipped', warnings

        if product.bom_cost_fixed_ok:
            unit_cost = product.bom_cost_fixed
            currency = product.bom_cost_fixed_currency_id or company.currency_id
            if currency != company.currency_id:
                unit_cost = currency._convert(unit_cost, company.currency_id, company, date)
            if not unit_cost:
                warnings.append(_("%s: the fixed cost is 0.", product.display_name))
            return unit_cost * quantity, 'fixed', warnings

        if not product.bom_cost_no_explode:
            bom = self.env['mrp.bom'].sudo()._bom_find(product, company_id=company.id)[product]
            if bom:
                if bom.id in visited or depth >= BOM_MAX_DEPTH:
                    warnings.append(_("%s: recursive or too deep bill of materials - product Cost used instead.",
                                      product.display_name))
                else:
                    return product._bom_margin_bom_cost(bom, quantity, date, company, visited + (bom.id,), depth)

        mode = product.bom_cost_leaf_source
        if mode == 'default':
            mode = company.bom_margin_leaf_source
        if mode == 'last_purchase':
            unit_cost = product._bom_margin_last_purchase_price(company)
            if unit_cost:
                return unit_cost * quantity, 'last_purchase', warnings
            warnings.append(_("%s: no confirmed purchase order - product Cost used instead.", product.display_name))

        unit_cost = product.standard_price
        if not unit_cost:
            warnings.append(_("%s: no Cost and no bill of materials.", product.display_name))
        return unit_cost * quantity, 'standard', warnings

    def _bom_margin_bom_cost(self, bom, quantity, date, company, visited, depth):
        self.ensure_one()
        warnings = []
        bom_qty = bom.product_uom_id._compute_quantity(bom.product_qty, self.uom_id)
        if not bom_qty:
            warnings.append(_("%s: the bill of materials produces 0 - 1 assumed.", self.display_name))
            bom_qty = 1.0
        factor = quantity / bom_qty
        total = 0.0
        for line in bom.bom_line_ids:
            if not line.product_id or line._skip_bom_line(self):
                continue
            cost, _source, line_warnings = line.product_id._bom_margin_cost(
                line.product_qty * factor, line.product_uom_id, date, company, visited, depth + 1)
            total += cost
            warnings += line_warnings
        if company.bom_margin_operations:
            total += bom._bom_margin_operations_cost(self) * factor
        return total, 'bom', warnings

    def _bom_margin_last_purchase_price(self, company):
        """Net unit price of the last confirmed purchase order, per product unit, in the company currency."""
        self.ensure_one()
        if 'purchase.order' not in self.env:
            return 0.0
        order = self.env['purchase.order'].sudo().search([
            ('order_line.product_id', '=', self.id),
            ('state', 'in', ('purchase', 'done')),
            ('company_id', '=', company.id),
        ], order='date_order desc, id desc', limit=1)
        line = order.order_line.filtered(lambda l: l.product_id == self and l.product_qty)[-1:]
        if not line:
            return 0.0
        uom_field = next(f for f in ('product_uom', 'product_uom_id', 'uom_id') if f in line._fields)
        price = line.price_subtotal / line.product_qty
        price = line[uom_field]._compute_price(price, self.uom_id)
        return order.currency_id._convert(price, company.currency_id, company, order.date_order)

#EoF
