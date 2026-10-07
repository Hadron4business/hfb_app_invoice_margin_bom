# Invoice Cost & Margin (Bill of Materials)

Cost and margin of every customer invoice and credit note, line by line, with bills of materials exploded on all levels.

## What it does

- **Bill of materials, all levels** - Manufactured products are costed by exploding their bill of materials down to purchased components, operations included - same formula as Odoo's BoM Structure & Cost report.
- **Purchased products** - Product Cost or the price of the last confirmed purchase order - per company, overridable per product.
- **Exceptions per product** - Exclude a product (re-invoiced services), give it a fixed cost in any currency, or do not explode its bill of materials.
- **Extra costs** - Add freight, customs or subcontracting to an invoice, each in its own currency. They are included in the margin.
- **Average margin per sales order** - Down payments, partial invoices and credit notes of the same orders are combined into one weighted average margin.
- **A snapshot, not a moving target** - Computed when the invoice is confirmed (or with a button) and stored, with who and when. Later price changes do not rewrite history.

## How to use it

1. Go to Invoicing > Configuration > Settings, section Invoice Cost & Margin: compute on confirmation (on by default), include operations, cost of purchased products.
2. Optionally, on a product: tab General Information, section Invoice Cost & Margin - exclude it, give it a fixed cost or keep its bill of materials closed.
3. Confirm a customer invoice. Open the tab Cost & Margin: products cost, extra costs, margin and margin %, cost of each line and where it comes from.
4. Add Extra Costs on that tab if needed; the margin is updated at once. The invoice list has optional Margin columns for totals.

## Good to know

- Cost and margin are visible to Billing Administrators and to users given the group "Show Invoice Cost & Margin".
- Older invoices: enable the scheduled action "Invoice Cost & Margin: compute older invoices" (Settings > Technical > Scheduled Actions) or use the filter "Cost Not Computed".
- Recursive bills of materials are detected; products without cost are listed in the warnings of the invoice.
- Kits are exploded like any other bill of materials.

## Technical

- Depends on `sale` and `mrp`; the last purchase price is used when `purchase` is installed.
- Fields are prefixed `bom_` (no clash with OCA `account_invoice_margin`).
- Hook: `account.move._post()`; engine: `product.product._bom_margin_cost()`.

## Status

Odoo 20 build. Missing before publication: tests on 17/18/19/20, icon, banner.
