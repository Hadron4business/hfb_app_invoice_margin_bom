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
"""	@version	17.0.1.0.0
	@owner  Hadron for Business
	@author Hadron for Business sp. z o.o.
	@date   2026.10.07

	Invoice Cost & Margin - operations
	Cost of the operations of one run of a bill of materials (cycles by work
	center capacity, cycle time, efficiency, setup and cleanup time, cost per
	hour).
"""
from odoo import models
from odoo.tools import float_round


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def _bom_margin_operations_cost(self, product):
        """Cost of the operations of one run of this bill of materials, in the company currency.

        Same duration formula as Odoo's BoM Structure & Cost report.
        """
        self.ensure_one()
        total = 0.0
        for operation in self.operation_ids:
            if operation._skip_operation_line(product):
                continue
            workcenter = operation.workcenter_id
            capacity = workcenter._get_capacity(product) or 1.0
            cycles = float_round(self.product_qty / capacity, precision_rounding=1, rounding_method='UP')
            duration = cycles * operation.time_cycle * 100.0 / (workcenter.time_efficiency or 100.0) \
                + workcenter._get_expected_duration(product)
            total += duration / 60.0 * workcenter.costs_hour
        return total

#EoF
