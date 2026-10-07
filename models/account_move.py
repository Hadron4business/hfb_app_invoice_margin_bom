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
"""	@version	18.0.1.0.2
	@owner  Hadron for Business
	@author Hadron for Business sp. z o.o.
	@date   2026.10.07

	Invoice Cost & Margin - invoices
	Totals of cost and margin per invoice (extra costs included), average margin
	of all the invoices of the same sales orders, compute button, automatic
	computation on confirmation and backfill cron.
"""
from odoo import _, api, fields, models

INVOICE_TYPES = ('out_invoice', 'out_refund')


class AccountMove(models.Model):
    _inherit = 'account.move'

    bom_extra_cost_ids = fields.One2many('account.move.extra.cost', 'move_id', string="Extra Costs", copy=True)
    bom_line_ids = fields.One2many(
        'account.move.line', string="Cost per Line", compute='_compute_bom_line_ids',
        help="Product lines of the invoice with their cost and margin.")
    bom_cost_products = fields.Monetary(string="Products Cost", compute='_compute_bom_margin', store=True)
    bom_cost_extra = fields.Monetary(string="Extra Costs Total", compute='_compute_bom_margin', store=True)
    bom_cost_total = fields.Monetary(string="Total Cost", compute='_compute_bom_margin', store=True)
    bom_margin = fields.Monetary(
        string="Margin", compute='_compute_bom_margin', store=True,
        help="Untaxed amount minus total cost.")
    bom_margin_percent = fields.Float(
        string="Margin (%)", digits=(16, 2), compute='_compute_bom_margin', store=True)
    bom_margin_signed = fields.Monetary(
        string="Margin (Company Currency)", currency_field='company_currency_id',
        compute='_compute_bom_margin', store=True,
        help="Margin in the company currency, negative for credit notes - for totals in lists and reports.")
    bom_cost_date = fields.Datetime(string="Cost Computed On", readonly=True, copy=False)
    bom_cost_uid = fields.Many2one('res.users', string="Cost Computed By", readonly=True, copy=False)
    bom_cost_warning = fields.Text(string="Cost Warnings", readonly=True, copy=False)

    bom_so_names = fields.Char(string="Sales Orders", compute='_compute_bom_so_margin')
    bom_so_invoice_ids = fields.Many2many(
        'account.move', 'account_move_bom_so_invoice_rel', 'move_id', 'so_move_id',
        string="Order Invoices", compute='_compute_bom_so_margin')
    bom_so_invoice_count = fields.Integer(string="Order Invoices Count", compute='_compute_bom_so_margin')
    bom_so_amount_untaxed = fields.Monetary(string="Orders Untaxed Amount", compute='_compute_bom_so_margin')
    bom_so_cost = fields.Monetary(string="Orders Total Cost", compute='_compute_bom_so_margin')
    bom_so_margin = fields.Monetary(string="Orders Margin", compute='_compute_bom_so_margin')
    bom_so_margin_percent = fields.Float(
        string="Orders Average Margin (%)", digits=(16, 2), compute='_compute_bom_so_margin')
    bom_so_warning = fields.Char(string="Orders Margin Warning", compute='_compute_bom_so_margin')

    @api.depends('invoice_line_ids')
    def _compute_bom_line_ids(self):
        for move in self:
            move.bom_line_ids = move.invoice_line_ids.filtered(lambda l: l.display_type == 'product')

    @api.depends('invoice_line_ids.bom_cost', 'bom_extra_cost_ids.amount_move_currency', 'amount_untaxed',
                 'currency_id', 'invoice_date', 'move_type')
    def _compute_bom_margin(self):
        for move in self:
            products = sum(move.invoice_line_ids.mapped('bom_cost'))
            extra = sum(move.bom_extra_cost_ids.mapped('amount_move_currency'))
            margin = move.amount_untaxed - products - extra
            move.bom_cost_products = products
            move.bom_cost_extra = extra
            move.bom_cost_total = products + extra
            move.bom_margin = margin
            move.bom_margin_percent = margin / move.amount_untaxed * 100.0 if move.amount_untaxed else 0.0
            signed = move.currency_id._convert(
                margin, move.company_currency_id, move.company_id,
                move.invoice_date or fields.Date.context_today(move)) if move.currency_id else margin
            move.bom_margin_signed = -signed if move.move_type == 'out_refund' else signed

    def _bom_so_invoices(self):
        """Sales orders of this invoice and all their (not cancelled) customer invoices and credit notes."""
        self.ensure_one()
        orders = self.sudo().invoice_line_ids.sale_line_ids.order_id
        invoices = orders.invoice_ids.filtered(lambda m: m.move_type in INVOICE_TYPES and m.state != 'cancel')
        return orders, self.browse(invoices.ids)

    @api.depends('invoice_line_ids.sale_line_ids')
    def _compute_bom_so_margin(self):
        for move in self:
            orders, invoices = move._bom_so_invoices() if move.id else (self.env['sale.order'], self.browse())
            untaxed = cost = 0.0
            missing = []
            for invoice in invoices.sudo():
                if not invoice.bom_cost_date:
                    missing.append(invoice.name or invoice.display_name)
                    continue
                sign = -1.0 if invoice.move_type == 'out_refund' else 1.0
                amount, inv_cost = invoice.amount_untaxed, invoice.bom_cost_total
                if invoice.currency_id != move.currency_id:
                    date = invoice.invoice_date or fields.Date.context_today(move)
                    amount = invoice.currency_id._convert(amount, move.currency_id, move.company_id, date)
                    inv_cost = invoice.currency_id._convert(inv_cost, move.currency_id, move.company_id, date)
                untaxed += sign * amount
                cost += sign * inv_cost
            margin = untaxed - cost
            move.bom_so_names = ", ".join(orders.mapped('name')) or False
            move.bom_so_invoice_ids = invoices
            move.bom_so_invoice_count = len(invoices)
            move.bom_so_amount_untaxed = untaxed
            move.bom_so_cost = cost
            move.bom_so_margin = margin
            move.bom_so_margin_percent = margin / untaxed * 100.0 if untaxed else 0.0
            move.bom_so_warning = _("Not included (cost not computed yet): %s", ", ".join(missing)) if missing else False

    def action_bom_margin_compute(self):
        for move in self.filtered(lambda m: m.move_type in INVOICE_TYPES):
            warnings = move.invoice_line_ids.filtered(lambda l: l.display_type == 'product')._bom_margin_compute()
            move.write({
                'bom_cost_date': fields.Datetime.now(),
                'bom_cost_uid': self.env.uid,
                'bom_cost_warning': "\n".join(dict.fromkeys(warnings)) or False,
            })
        return True

    def action_bom_margin_compute_orders(self):
        invoices = self.browse()
        for move in self:
            invoices |= move._bom_so_invoices()[1]
        return (invoices | self).action_bom_margin_compute()

    def action_bom_margin_open_invoices(self):
        self.ensure_one()
        return {
            'name': _("Order Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.bom_so_invoice_ids.ids)],
        }

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        posted.filtered(
            lambda m: m.move_type in INVOICE_TYPES and m.company_id.bom_margin_auto
        ).sudo().action_bom_margin_compute()
        return posted

    @api.model
    def _cron_bom_margin_compute(self, limit=200):
        """Backfill: compute the cost of posted customer invoices that have none yet, `limit` per run."""
        self.search([
            ('move_type', 'in', INVOICE_TYPES),
            ('state', '=', 'posted'),
            ('bom_cost_date', '=', False),
        ], limit=limit, order='id').action_bom_margin_compute()

#EoF
