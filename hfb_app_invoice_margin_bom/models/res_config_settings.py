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
"""	@version	20.0.1.0.2
	@owner  Hadron for Business
	@author Hadron for Business sp. z o.o.
	@date   2026.10.07

	Invoice Cost & Margin - settings
	Exposes the company options in Invoicing > Configuration > Settings.
"""
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bom_margin_auto = fields.Boolean(related='company_id.bom_margin_auto', readonly=False)
    bom_margin_operations = fields.Boolean(related='company_id.bom_margin_operations', readonly=False)
    bom_margin_leaf_source = fields.Selection(related='company_id.bom_margin_leaf_source', readonly=False)

#EoF
