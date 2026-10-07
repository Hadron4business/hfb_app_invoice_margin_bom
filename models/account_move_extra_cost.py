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
"""	@version	19.0.1.0.0
	@owner  Hadron for Business
	@author Hadron for Business sp. z o.o.
	@date   2026.10.07

	Invoice Cost & Margin - extra costs
	Extra costs of an invoice (freight, customs, subcontracting) in their own
	currency, converted to the invoice currency at the invoice date.
"""
from odoo import api, fields, models


class AccountMoveExtraCost(models.Model):
    _name = 'account.move.extra.cost'
    _description = "Invoice Extra Cost"
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    move_id = fields.Many2one('account.move', string="Invoice", required=True, ondelete='cascade', index=True)
    name = fields.Char(string="Description", required=True)
    currency_id = fields.Many2one(
        'res.currency', string="Currency", required=True, default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(string="Amount", currency_field='currency_id')
    move_currency_id = fields.Many2one(related='move_id.currency_id', string="Invoice Currency")
    amount_move_currency = fields.Monetary(
        string="Amount in Invoice Currency", currency_field='move_currency_id',
        compute='_compute_amount_move_currency', store=True)

    @api.depends('amount', 'currency_id', 'move_id.currency_id', 'move_id.invoice_date', 'move_id.company_id')
    def _compute_amount_move_currency(self):
        for cost in self:
            move = cost.move_id
            if not move.currency_id or cost.currency_id == move.currency_id:
                cost.amount_move_currency = cost.amount
            else:
                cost.amount_move_currency = cost.currency_id._convert(
                    cost.amount, move.currency_id, move.company_id, move.invoice_date or fields.Date.context_today(cost))

#EoF
