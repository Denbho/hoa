# -*- coding: utf-8 -*-
import locale
import logging
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang

_logger = logging.getLogger("_name_")
locale.setlocale(locale.LC_ALL, '')


class SaleCouponProgram(models.Model):
    _inherit = 'sale.coupon.program'

    property_sale = fields.Boolean(string="Property Coupon?")
    property_sale_coupon_apply_on = fields.Selection([('NTCP', 'Net Total Contract Price'), ('dp', 'Downpayment')],
                                                     string="Applied On")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                if not order.property_sale:
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
                else:
                    if line.reward_coupon_id in [False]:
                        amount_untaxed += line.price_subtotal
                        amount_tax += line.price_tax
                    elif not line.reward_coupon_id.property_sale:
                        amount_untaxed += line.price_subtotal
                        amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def _compute_amount_by_group(self, res, order, line):
        price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
        taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id,
                                        partner=order.partner_shipping_id)['taxes']
        for tax in line.tax_id:
            group = tax.tax_group_id
            res.setdefault(group, {'amount': 0.0, 'base': 0.0})
            for t in taxes:
                if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                    res[group]['amount'] += t['amount']
                    res[group]['base'] += t['base']
        return res

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                if not order.property_sale:
                    res = order._compute_amount_by_group(res, order, line)
                else:
                    if line.reward_coupon_id in [False]:
                        res = order._compute_amount_by_group(res, order, line)
                    elif not line.reward_coupon_id.property_sale:
                        res = order._compute_amount_by_group(res, order, line)
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    @api.depends('order_line.invoice_lines', 'spot_dp_invoice_id', 'turnover_balance_invoice_id', 'dp_invoice_id')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = [i.id for i in order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.type in ('out_invoice', 'out_refund'))]
            if order.spot_dp_invoice_id:
                invoices.append(order.spot_dp_invoice_id.id)
            if order.dp_invoice_id:
                invoices.append(order.dp_invoice_id.id)
            if order.turnover_balance_invoice_id:
                invoices.append(order.turnover_balance_invoice_id.id)
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    property_sale = fields.Boolean(string="Sale of Property View", compute="_get_property", store=True)
    managing_director_employee_id = fields.Many2one('hr.employee', string="Managing Director")
    marketing_lead_employee_id = fields.Many2one('hr.employee', string="Marketing Team Lead")
    broker_partner_id = fields.Many2one('res.partner', string="Broker/Realty")
    vendor_group_id = fields.Many2one('property.vendor.group', string="Vendor Group")
    type_of_sale = fields.Selection(
        [('New Sale', 'New Sale'),
         ('Recontract', 'Recontract')], default="New Sale", string="Type of Sale")
    movement_of_sale = fields.Selection(
        [('New Sale', 'New Sale'),
         ('Cancellations - Recontract', 'Cancellations - Recontract'),
         ('Cancelled', 'Cancelled'),
         ('Recontract', 'Recontract'),
         ('Recontract2', 'Recontract2'),
         ('Offsetting', 'Offsetting'),
         ('Employee', 'Employee'),
         ('Reactivated Account', 'Reactivated Account')], default="New Sale", string="Movement of Sale")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                          compute="_get_sale_analytic",
                                          inverse="_inverse_sale_analytic", store=True, track_visibility="always")
    downpayment_percent = fields.Float(string="Downpayment", default="15", help="Downpayment Term (%)")
    financing_type_id = fields.Many2one('property.financing.type', string="Financing Type", track_visibility="always",
                                        help="If no Selection Available, ask you system administrator to configure one in the property's phase subdivision")
    financing_type_term_id = fields.Many2one('property.financing.type.term',
                                             domain="[('financing_type_id', '=', financing_type_id)]",
                                             string="Financing Term", track_visibility="always",
                                             help="If no Selection Available, ask you system administrator to configure one in the property's phase subdivision")

    # hidden
    downpayment_term_ids = fields.Many2many('property.downpayment.term', 'phase_dp_term_rel', 'phase_id', 'term_id',
                                            string="Downpayment Terms", compute="_get_property")
    financing_type_ids = fields.Many2many('property.financing.type', 'phase_financingtype_rel', 'phase_id', 'term_id',
                                          string="Financing Types", compute="_get_property")
    downpayment_amount = fields.Monetary(string="DP Amount", help="Reservation has already deducted.",
                                         compute="_get_property", store=True)
    dp_discount_amount = fields.Monetary(string="DP Discount", compute="_get_property", store=True)
    ntcp_discount_amount = fields.Monetary(string="Buyers Discount", help="Computed against NTCP",
                                           compute="_get_property", store=True)
    net_of_ntcp_discount_amount = fields.Monetary(string="Net of Discount Discount", help="Computed against NTCP",
                                                  compute="_get_property", store=True)
    spot_amount = fields.Monetary(string="Spot Cash Payment")

    # Downpayment
    split_dp = fields.Boolean(string="Split DP", track_visibility="always")
    split_percent = fields.Float(string="Split Percent", track_visibility="always")
    downpayment_term_id = fields.Many2one('property.downpayment.term', string="Downpayment Term", track_visibility="always")
    dp_amount_due = fields.Monetary(string="Amount Due", compute="_get_property", store=True)
    dp_interest = fields.Monetary(string="DP Interest", compute="_get_property", store=True)
    dp_monthly_due = fields.Monetary(string="Monthly Due", compute="_get_property", store=True)

    downpayment_term2_id = fields.Many2one('property.downpayment.term', string="Downpayment Term",
                                          track_visibility="always")
    dp_amount_due2 = fields.Monetary(string="Amount Due", compute="_get_property", store=True)
    dp_interest2 = fields.Monetary(string="2nd DP Interest", compute="_get_property", store=True)
    dp_monthly_due2 = fields.Monetary(string="2nd Monthly Due", compute="_get_property", store=True)

    turned_over_balance_amount = fields.Monetary(string="Turnover Balance Amount", compute="_get_property", store=True)
    turned_over_balance_percent = fields.Float(string="Turnover Balance Percent", compute="_get_property", store=True)
    turned_over_balance_mdue = fields.Monetary(string="After Turnover Monthly Due", compute="_get_property", store=True)

    property_id = fields.Many2one('property.detail', store=True, compute="_get_property")
    house_price = fields.Monetary(string="House Price", compute="_get_property", store=True)
    lot_price = fields.Monetary(string="Lot Price", compute="_get_property", store=True)
    miscellaneous_amount = fields.Monetary(string="Miscellaneous Amount", compute="_get_property", store=True)
    reservation_fee = fields.Monetary(string="Reservation Fee", compute="_get_property", store=True)
    ntcp = fields.Monetary(string="NTCP", help="Total Net Contract Price", compute="_get_property", store=True)
    tcp = fields.Monetary(string="TPC", help="Total Contract Price", compute="_get_property", store=True)
    tcp_vat = fields.Monetary(string="TPC + Vat", help="Total Contract Price + VAT", compute="_get_property",
                              store=True)
    tcp_discount = fields.Monetary(string="TCP Discount", track_visibility="always")
    property_vat = fields.Monetary(string="VAT", compute="_get_property", store=True)
    spot_dp_invoice_id = fields.Many2one('account.move', string="Spot Cash DP Invoice", readonly=True)
    dp_invoice_id = fields.Many2one('account.move', string="Downpayment Invoice", readonly=True)
    dp_invoice2_id = fields.Many2one('account.move', string="2nd Downpayment Invoice", readonly=True)
    turnover_balance_invoice_id = fields.Many2one('account.move', string="Turnover Balance Invoice", readonly=True)

    # Property Details
    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision", related="property_id.subdivision_id",
                                     store=True)
    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase",
                                           related="property_id.subdivision_phase_id", store=True)
    house_model_id = fields.Many2one('housing.model', string="Unit/House Model", related="property_id.house_model_id",
                                     store=True)
    brand_id = fields.Many2one('product.brand', string='Property Brand', store=True,
                               related="property_id.house_model_id.brand_id")
    model_type_id = fields.Many2one("property.model.type", string="Model Type", store=True,
                                    related="property_id.model_type_id")
    floor_area = fields.Float(string="Floor Area", store=True, related="property_id.floor_area")
    lot_area = fields.Float(string="Lot Area", store=True, related="property_id.lot_area")
    property_type = fields.Selection([('House', 'House and Lot'),
                                      ('Condo', 'Condo Unit')],
                                     string="Property Type", related="property_id.house_model_id.property_type",
                                     store=True)
    property_continent_id = fields.Many2one('res.continent', string="Property Continent", store=True,
                                            related="subdivision_id.continent_id")
    property_continent_region_id = fields.Many2one('res.continent.region', string="Property Continent Region",
                                                   store=True, related="subdivision_id.continent_region_id")
    property_country_id = fields.Many2one('res.country', string="Property Country", store=True,
                                          related="subdivision_id.country_id")
    property_island_group_id = fields.Many2one('res.island.group', string="Property Island Group", store=True,
                                               related="subdivision_id.island_group_id")
    property_province_id = fields.Many2one('res.country.province', string="Property Province", store=True,
                                           related="subdivision_id.province_id")
    property_city_id = fields.Many2one('res.country.city', string="Property City", store=True,
                                       related="subdivision_id.city_id")
    property_barangay_id = fields.Many2one('res.barangay', string="Property Barangay", store=True,
                                           related="subdivision_id.barangay_id")
    property_state_id = fields.Many2one('res.country.state', string="Property Region/States", store=True,
                                        related="subdivision_id.state_id")
    property_zip = fields.Char(string="Property Zip Code", store=True, related="subdivision_id.zip")
    property_cluster_id = fields.Many2one('res.region.cluster', string="Regional Cluster I", store=True,
                                          related="subdivision_id.cluster_id")
    property_cluster2_id = fields.Many2one('res.region.cluster', string="Regional Cluster II", store=True,
                                           related="subdivision_id.cluster2_id")
    property_street = fields.Char(string="Street", store=True, related="subdivision_id.street")
    property_street2 = fields.Char(string="Street2", store=True, related="subdivision_id.street2")

    def _inverse_sale_analytic(self):
        for order in self:
            if not order.property_id:
                continue

    @api.model
    def create(self, vals):
        if vals.get('property_sale') and vals.get('property_id'):
            property_data = self.env['property.detail'].browse(vals.get('property_id'))
            vals[
                'brand_id'] = property_data.subdivision_id.branch_id and property_data.subdivision_id.branch_id or vals.get(
                'branch_id')
        return super(SaleOrder, self).create(vals)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.property_id:
            self.property_id.sudo().write({
                'sale_id': self.id,
                'state': 'Reserved',
                'sale_status': 'Outstanding'})
        return res

    @api.depends('order_line', 'order_line.product_id', 'order_line.price_unit', 'order_line.tax_id', 'split_percent',
                 'split_dp', 'tcp_discount', 'downpayment_term_id', 'downpayment_percent', 'financing_type_term_id',
                 'spot_amount', 'downpayment_term2_id')
    def _get_property(self):
        for i in self:
            i.downpayment_term_ids = []
            i.financing_type_ids = []
            i.property_id = False
            i.house_price = 0
            i.lot_price = 0
            i.miscellaneous_amount = 0
            i.reservation_fee = 0
            i.ntcp = 0
            i.tcp = 0
            i.tcp_vat = 0
            i.downpayment_amount = 0
            i.dp_discount_amount = 0
            i.ntcp_discount_amount = 0
            i.dp_amount_due = 0
            i.dp_interest = 0
            i.dp_monthly_due = 0
            i.dp_interest2 = 0
            i.dp_monthly_due2 = 0
            i.dp_amount_due2 =0
            i.turned_over_balance_amount = 0
            i.turned_over_balance_percent = 0
            i.turned_over_balance_mdue = 0
            i.property_vat = 0
            i.net_of_ntcp_discount_amount = 0
            i.analytic_account_id = False
            i.property_sale = False
            for line in i.order_line:
                if line.product_id and line.product_id.property_id and line.product_id.is_property and not line.unit_tcp_computation:
                    data = line.product_id.property_id.subdivision_phase_id
                    property_data = line.product_id.property_id
                    i.property_sale = True
                    i.analytic_account_id = property_data.subdivision_phase_id.account_analytic_id.id
                    property_tax = line.tax_id.compute_all(property_data.ntcp, line.order_id.currency_id, 1,
                                                           product=line.product_id,
                                                           partner=line.order_id.partner_shipping_id)
                    reservation_fee = line.tax_id.compute_all(property_data.reservation_fee, line.order_id.currency_id,
                                                              1, product=line.product_id,
                                                              partner=line.order_id.partner_shipping_id)
                    i.downpayment_term_ids = data.downpayment_term_ids and data.downpayment_term_ids.ids or False
                    i.financing_type_ids = data.financing_type_ids and data.financing_type_ids.ids or False
                    i.property_id = property_data.id
                    i.house_price = property_data.house_price
                    i.lot_price = property_data.lot_price
                    i.miscellaneous_amount = property_data.miscellaneous_amount
                    i.ntcp = property_data.ntcp
                    i.tcp = property_data.tcp + property_data.tcp_marketing_markup
                    i.reservation_fee = sum(
                        t.get('amount', 0.0) for t in reservation_fee.get('taxes', [])) + property_data.reservation_fee
                    i.property_vat = sum(t.get('amount', 0.0) for t in property_tax.get('taxes', []))
                    i.tcp_vat = i.property_vat + property_data.tcp
                    continue
            dp_discount, ntcp_discount = 0, 0
            for disc in i.order_line:
                if disc.reward_coupon_id and disc.reward_coupon_id.property_sale:
                    if disc.reward_coupon_id.property_sale_coupon_apply_on == 'NTCP':
                        ntcp_discount += abs(disc.price_total)
                    if disc.reward_coupon_id.property_sale_coupon_apply_on == 'dp':
                        dp_discount += abs(disc.price_total)
            if i.property_id:
                i.net_of_ntcp_discount_amount = (i.tcp_vat - ntcp_discount)
                downpayment = (i.tcp_vat - ntcp_discount) * (i.downpayment_percent / 100)
                dp_amount_due = downpayment - i.spot_amount - dp_discount - i.reservation_fee

                if i.split_dp:
                    dp_amount_due2 = dp_amount_due * ((100 - i.split_percent) / 100)
                    dp_amount_due = dp_amount_due * (i.split_percent / 100)
                    dp_interest2 = dp_amount_due2 * (i.downpayment_term2_id.interest_rate / 100)
                    dp_monthly_due2 = i.downpayment_term2_id and (
                            dp_amount_due2 + dp_interest2) / i.downpayment_term2_id.month or 0
                    i.dp_amount_due2 = dp_amount_due2
                    i.dp_interest2 = dp_interest2
                    i.dp_monthly_due2 = dp_monthly_due2
                dp_interest = dp_amount_due * (i.downpayment_term_id.interest_rate / 100)
                dp_monthly_due = i.downpayment_term_id and (
                        dp_amount_due + dp_interest) / i.downpayment_term_id.month or 0


                turned_over_balance_amount = i.tcp_vat - downpayment
                turned_over_balance_percent = turned_over_balance_amount / i.tcp_vat
                turned_over_balance_mdue = i.financing_type_term_id and (turned_over_balance_amount + (
                        turned_over_balance_amount * (i.financing_type_term_id.interest_rate / 100))) / (
                                                   i.financing_type_term_id.year * 12) or 0
                i.downpayment_amount = downpayment
                i.dp_discount_amount = dp_discount
                i.ntcp_discount_amount = ntcp_discount
                i.dp_amount_due = dp_amount_due
                i.dp_interest = dp_interest
                i.dp_monthly_due = dp_monthly_due
                i.turned_over_balance_amount = turned_over_balance_amount
                i.turned_over_balance_percent = turned_over_balance_percent
                i.turned_over_balance_mdue = turned_over_balance_mdue

    @api.onchange('tcp', 'tcp_discount', 'property_id')
    def _onchange_tcp_discount(self):
        if self.tcp_discount > 0 and self.property_id:
            self._validate_tcp_discount()

    @api.constrains('tcp', 'tcp_discount', 'property_id')
    def _validate_tcp_discount(self):
        for i in self:
            if i.tcp_discount > 0 and i.property_id:
                if i.tcp_discount > i.property_id.tcp_marketing_markup:
                    raise ValidationError(_(
                        f"TCP Discount must not be greater than Php {locale.format('%0.2f', i.property_id.tcp_marketing_markup, grouping=True)}"))

    def compute_financing_term(self, year, interest_rate, amount):
        return (amount + (amount * (interest_rate / 100))) / (year * 12)

    def _get_reward_values_discount_percentage_per_line(self, program, line):
        if program.property_sale:
            if program.property_sale_coupon_apply_on == 'NTCP':
                discount_amount = line.product_id.property_id.ntcp * (program.discount_percentage / 100)
            else:
                discount_amount = (line.product_id.property_id.tcp * (self.downpayment_percent / 100)) * (
                        program.discount_percentage / 100)
        else:
            discount_amount = line.product_uom_qty * line.price_reduce * (program.discount_percentage / 100)
        return discount_amount

    def _create_reward_line(self, program):
        reward_line = [(0, False, value) for value in self._get_reward_line_values(program)]
        reward_line[0][2]['reward_coupon_id'] = program.id
        self.write({'order_line': reward_line})

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoice_status(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.
        """
        # Ignore the status of the deposit product
        deposit_product_id = self.env['sale.advance.payment.inv']._default_product_id()
        domain_search = [('order_id', 'in', self.ids), ('product_id', '!=', deposit_product_id.id)]
        property_sale = [i.property_sale for i in self]
        if property_sale[0] and property_sale[0] == 1:
            domain_search += [('reward_coupon_id', 'in', [False])]
        line_invoice_status_all = [(d['order_id'][0], d['invoice_status']) for d in
                                   self.env['sale.order.line'].read_group(domain_search, ['order_id', 'invoice_status'],
                                                                          ['order_id', 'invoice_status'], lazy=False)]
        for order in self:
            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]
            if order.state not in ('sale', 'done'):
                order.invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                order.invoice_status = 'to invoice'
            elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                order.invoice_status = 'invoiced'
            elif line_invoice_status and all(
                    invoice_status in ('invoiced', 'upselling') for invoice_status in line_invoice_status):
                order.invoice_status = 'upselling'
            else:
                order.invoice_status = 'no'

    def create_spot_dp_invoice(self):
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']
        for order in self:
            if not order.state in ['sale', 'done']:
                raise ValidationError(_('You must confirm this sales transaction in order to proceed'))
            if order.spot_amount < 0:
                raise ValidationError(_("No Spont Amount to Invoice"))
            tax_ids = []
            uom = False
            analytic_tag = []
            for line in order.order_line:
                if not line.display_type:
                    tax_ids = line.tax_id.ids
                    uom = line.product_uom.id
                    analytic_tag = line.analytic_tag_ids.ids
                    break
            property_analytic_id = order.property_id.account_analytic_id.id
            invoice_vals = order._prepare_invoice()
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'name': f"Property Name: {order.property_id.name} \
                        \nSpot Cash Amount for Downpayment: Php {locale.format('%0.2f', order.spot_amount, grouping=True)} \
                        \nRemaining DP Balance: Php {locale.format('%0.2f', order.dp_amount_due, grouping=True)}",
                'product_uom_id': uom,
                'quantity': 1,
                'price_unit': order.spot_amount,
                # 'tax_ids': [(6, 0, tax_ids)],
                'analytic_account_id': property_analytic_id,
                'analytic_tag_ids': [(6, 0, analytic_tag)],
            }))
            moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals)
            order.write({'spot_dp_invoice_id': moves.id})
        return True

    def create_downpayment_invoice(self):
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']
        if not self._context.get('second_dp'):
            for order in self:
                if not order.state in ['sale', 'done']:
                    raise ValidationError(_('You must confirm this sales transaction in order to proceed'))
                if order.dp_amount_due < 0:
                    raise ValidationError(_("No Downpayment Due amount to Invoice"))
                if not order.downpayment_term_id.payment_term_id:
                    raise ValidationError(_('Please configure first an Accounting Payment Term on the DP Term setup.'))
                tax_ids = []
                uom = False
                analytic_tag = []
                for line in order.order_line:
                    if not line.display_type:
                        tax_ids = line.tax_id.ids
                        uom = line.product_uom.id
                        analytic_tag = line.analytic_tag_ids.ids
                        break
                property_analytic_id = order.property_id.account_analytic_id.id
                invoice_vals = order._prepare_invoice()
                invoice_vals['invoice_payment_term_id'] = order.downpayment_term_id.payment_term_id.id
                invoice_vals['invoice_line_ids'].append((0, 0, {
                    'name': f"Property Name: {order.property_id.name} \
                            \nPayment for Downpayment: Php {locale.format('%0.2f', order.dp_amount_due, grouping=True)}",
                    'product_uom_id': uom,
                    'quantity': 1,
                    'price_unit': order.dp_amount_due,
                    # 'tax_ids': [(6, 0, tax_ids)],
                    'analytic_account_id': property_analytic_id,
                    'analytic_tag_ids': [(6, 0, analytic_tag)],
                }))
                moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals)
                order.write({'dp_invoice_id': moves.id})
            else:
                for order in self:
                    if not order.state in ['sale', 'done']:
                        raise ValidationError(_('You must confirm this sales transaction in order to proceed'))
                    if order.dp_amount_due2 < 0:
                        raise ValidationError(_("No Downpayment Due amount to Invoice"))
                    if not order.downpayment_term2_id.payment_term_id:
                        raise ValidationError(
                            _('Please configure first an Accounting Payment Term on the DP Term setup.'))
                    tax_ids = []
                    uom = False
                    analytic_tag = []
                    for line in order.order_line:
                        if not line.display_type:
                            tax_ids = line.tax_id.ids
                            uom = line.product_uom.id
                            analytic_tag = line.analytic_tag_ids.ids
                            break
                    property_analytic_id = order.property_id.account_analytic_id.id
                    invoice_vals = order._prepare_invoice()
                    invoice_vals['invoice_payment_term_id'] = order.downpayment_term2_id.payment_term_id.id
                    invoice_vals['invoice_line_ids'].append((0, 0, {
                        'name': f"Property Name: {order.property_id.name} \
                                \nPayment for Downpayment: Php {locale.format('%0.2f', order.dp_amount_due2, grouping=True)}",
                        'product_uom_id': uom,
                        'quantity': 1,
                        'price_unit': order.dp_amount_due2,
                        # 'tax_ids': [(6, 0, tax_ids)],
                        'analytic_account_id': property_analytic_id,
                        'analytic_tag_ids': [(6, 0, analytic_tag)],
                    }))
                    moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(
                        invoice_vals)
                    order.write({'dp_invoice2_id': moves.id})
        return True

    def create_turnover_balance_invoice(self):
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']
        for order in self:
            if not order.state in ['sale', 'done']:
                raise ValidationError(_('You must confirm this sales transaction in order to proceed'))
            if order.turned_over_balance_amount < 0:
                raise ValidationError(_("No Turnover Balance to Invoice"))
            if not order.financing_type_term_id.payment_term_id:
                raise ValidationError(
                    _('Please configure first an Accounting Payment Term on the Financing Term setup.'))
            tax_ids = []
            uom = False
            analytic_tag = []
            for line in order.order_line:
                if not line.display_type:
                    tax_ids = line.tax_id.ids
                    uom = line.product_uom.id
                    analytic_tag = line.analytic_tag_ids.ids
                    break
            property_analytic_id = order.property_id.account_analytic_id.id
            invoice_vals = order._prepare_invoice()
            invoice_vals['invoice_payment_term_id'] = order.financing_type_term_id.payment_term_id.id
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'name': f"Property Name: {order.property_id.name} \
                        \nTCP + VAT: Php {locale.format('%0.2f', order.tcp_vat, grouping=True)} \
                        \nDownpayment: Php {locale.format('%0.2f', order.downpayment_amount, grouping=True)} \
                        \nTurnover Balance ({order.turned_over_balance_percent}Percent): Php {locale.format('%0.2f', order.turned_over_balance_amount, grouping=True)}",
                'product_uom_id': uom,
                'quantity': 1,
                'price_unit': order.turned_over_balance_amount,
                # 'tax_ids': [(6, 0, tax_ids)],
                'analytic_account_id': property_analytic_id,
                'analytic_tag_ids': [(6, 0, analytic_tag)],
            }))
            moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals)
            order.write({'turnover_balance_invoice_id': moves.id})
        return True

    # if related to property sale, this will create a reservation invoice
    # Total override the default function
    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:
            pending_section = None

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        if not order.property_sale:
                            invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                        else:
                            if line.reward_coupon_id in [False]:
                                invoice_line = pending_section._prepare_invoice_line()
                                invoice_line[
                                    'analytic_account_id'] = order.property_id.subdivision_phase_id.account_analytic_id.id
                                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line))
                            elif not line.reward_coupon_id.property_sale:
                                invoice_line = pending_section._prepare_invoice_line()
                                invoice_line[
                                    'analytic_account_id'] = order.property_id.subdivision_phase_id.account_analytic_id.id
                                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line))
                        pending_section = None
                    if not order.property_sale:
                        invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))
                    else:
                        if line.reward_coupon_id in [False]:
                            invoice_line = line._prepare_invoice_line()
                            invoice_line[
                                'analytic_account_id'] = order.property_id.subdivision_phase_id.account_analytic_id.id
                            invoice_vals['invoice_line_ids'].append((0, 0, invoice_line))
                        elif not line.reward_coupon_id.property_sale:
                            invoice_line = line._prepare_invoice_line()
                            invoice_line[
                                'analytic_account_id'] = order.property_id.subdivision_phase_id.account_analytic_id.id
                            invoice_vals['invoice_line_ids'].append((0, 0, invoice_line))

            if not invoice_vals['invoice_line_ids']:
                raise UserError(_(
                    'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            for grouping_keys, invoices in groupby(invoice_vals_list,
                                                   key=lambda x: (x.get('partner_id'), x.get('currency_id'))):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['invoice_payment_ref'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals_list)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                                        values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                                        subtype_id=self.env.ref('mail.mt_note').id
                                        )
        return moves


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    unit_tcp_computation = fields.Boolean(string="Unit TCP Computation", default=False)
    reward_coupon_id = fields.Many2one('sale.coupon.program', string="Coupon Program")
