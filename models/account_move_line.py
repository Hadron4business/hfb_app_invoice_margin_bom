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
"""	@version	20.0.1.0.0
	@owner  Hadron for Business
	@author Hadron for Business sp. z o.o.
	@date   2026.10.07

	Invoice Cost & Margin - invoice lines
	Cost, margin and cost source stored on each invoice line (a snapshot taken
	when the cost is computed); the cost is converted to the invoice currency at
	the invoice date.
"""
from odoo import fields, models

from .product import COST_SOURCES


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Snapshot written by account.move.action_bom_margin_compute(), not computed fields:
    # later changes of prices or bills of materials must not rewrite the margin of past invoices.
    bom_cost_unit = fields.Monetary(string="Unit Cost", currency_field='currency_id', readonly=True, copy=False)
    bom_cost = fields.Monetary(string="Cost", currency_field='currency_id', readonly=True, copy=False)
    bom_margin = fields.Monetary(string="Margin", currency_field='currency_id', readonly=True, copy=False)
    bom_margin_percent = fields.Float(string="Margin (%)", digits=(16, 2), readonly=True, copy=False)
    bom_cost_source = fields.Selection(COST_SOURCES, string="Cost Source", readonly=True, copy=False)

    def _bom_margin_compute(self):
        """Compute and store cost and margin of the lines; return the warnings."""
        warnings = []
        for line in self:
            move = line.move_id
            company = move.company_id
            date = move.invoice_date or fields.Date.context_today(line)
            cost, source = 0.0, 'none'
            if line.product_id:
                cost, source, line_warnings = line.product_id._bom_margin_cost(
                    line.quantity, line.product_uom_id, date, company)
                warnings += line_warnings
            if move.currency_id != company.currency_id:
                cost = company.currency_id._convert(cost, move.currency_id, company, date)
            margin = line.price_subtotal - cost
            line.write({
                'bom_cost': cost,
                'bom_cost_unit': cost / line.quantity if line.quantity else 0.0,
                'bom_margin': margin,
                'bom_margin_percent': margin / line.price_subtotal * 100.0 if line.price_subtotal else 0.0,
                'bom_cost_source': source,
            })
        return warnings

#EoF
