# -*- coding: utf-8 -*-
# vim: tabstop=4 softtabstop=0 shiftwidth=4 smarttab expandtab fileformat=unix
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
{
    'name': "Invoice Cost & Margin (Bill of Materials)",
    'summary': "Real cost and margin on every customer invoice - manufactured products costed by exploding their bill of "
               "materials, plus extra costs such as freight or customs",
    'description': """
Invoice Cost & Margin (Bill of Materials)
=========================================

Odoo shows a margin on sales orders, computed from the product Cost field. It
does not show any margin on invoices, and for manufactured products the Cost
field is often outdated.

This app computes the cost and the margin of each customer invoice and credit
note, line by line:

* manufactured products: the bill of materials is exploded on all levels,
  operations included (same formula as Odoo's BoM Structure & Cost report),
* purchased products: product Cost or the last purchase price,
* per product: skip it, use a fixed cost (in any currency) or do not explode
  its bill of materials,
* extra costs on the invoice (freight, customs, subcontracting) in their own
  currency,
* average margin of all the invoices of the same sales orders.

The cost is a snapshot: computed when the invoice is confirmed (optional) or
with a button, so later price changes do not rewrite history. A scheduled
action can backfill older invoices.
""",
    'version': "20.0.1.0.0",
    'author': "Hadron for Business sp. z o.o.",
    'website': "http://hadronforbusiness.com",
    'license': "OPL-1",
    'category': "Accounting/Accounting",
    'depends': [
        'sale',
        'mrp',
    ],
    'data': [
        'security/invoice_margin_security.xml',
        'security/ir.access.csv',
        'data/ir_cron_data.xml',
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'views/account_move_views.xml',
    ],
    'images': [
        'static/description/banner_screenshot.png',
    ],
    'installable': True,
    'application': False,
}
