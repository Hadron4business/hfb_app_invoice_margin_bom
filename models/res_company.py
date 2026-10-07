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

	Invoice Cost & Margin - company settings
	When to compute the invoice cost, whether bill of materials operations are
	included and how purchased components (without a bill of materials) are
	costed.
"""
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    bom_margin_auto = fields.Boolean(
        string="Compute Invoice Cost on Confirmation", default=True)
    bom_margin_operations = fields.Boolean(
        string="Include Operations in BoM Cost", default=True)
    bom_margin_leaf_source = fields.Selection(
        [('standard', "Product Cost"), ('last_purchase', "Last Purchase Price")],
        string="Cost of Purchased Products", default='standard', required=True)

#EoF
