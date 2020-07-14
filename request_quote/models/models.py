# # -*- coding: utf-8 -*-
from itertools import groupby
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
import logging

_logger = logging.getLogger("_name_")

import odoo.addons.decimal_precision as dp


class Quote_Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * \
                            (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(
                        price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id,
                        partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0)
                                      for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })


    order_line = fields.One2many('request.order.line', 'order_id', string='Order Lines', copy=True)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True, required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=False, readonly=True, help="Pricelist for current sales order.")
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    note = fields.Text('Terms and conditions')
    fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=False)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_name = fields.Text('Product Name')
    company_name = fields.Char(string='Your Company Name')
    question = fields.Text(string='Your Question')

    @api.model
    def create(self, values):
        """ Create Order Line from Web Quotation"""
        order_line = []
        if values.get('product_id'):
            if self.product_id not in values:
                if 'product_id' in values.keys():
                    order_line = {'product_id': values['product_id']}

            if self.product_uom_qty not in values:
                if 'product_uom_qty' in values.keys():
                    data = {'product_uom_qty': values['product_uom_qty']}
                    order_line.update(data)

            if self.product_id not in values:
                if 'product_uom_qty' in values.keys():
                    values['order_line'] = [[0, 0, order_line]]

            if 'email_from' in values.keys():
                email_from = values['email_from']
                if self.env['res.partner'].search([('email', '=', email_from)]):
                    values['partner_id'] = self.env['res.partner'].search(
                        [('email', '=', email_from)],limit=1).id
                # else:
                #     res_partner_obj = self.env['res.partner']
                #     if 'phone' in values.keys():
                #        phone = values['phone']
                #     else:
                #        phone = None
                #     partner_data = {
                #         'name': values['contact_name'],
                #         'email': values['email_from'],
                #         'phone': phone,
                #     }
                #     partner = res_partner_obj.create(partner_data)
                #     values['partner_id'] = partner.id
        return super(Quote_Lead, self).create(values)

    def button_dummy(self):
        return True


class RequestOrderLine(models.Model):
    _name = 'request.order.line'
    _description = 'Request Order Line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id,
                partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    sequence = fields.Integer(string='Sequence', default=10)
    order_id = fields.Many2one('crm.lead', string='Request Reference',
                               required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[(
        'sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    name = fields.Text(string='Description', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one(
        'product.uom', string='Unit of Measure', required=True)
    discount = fields.Float(string='Discount (%)',
                            digits=dp.get_precision('Discount'), default=0.0)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision(
        'Product Price'), default=0.0)
    price_subtotal = fields.Monetary(
        compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Monetary(
        compute='_compute_amount', string='Taxes', readonly=True, store=True)
    price_total = fields.Monetary(
        compute='_compute_amount', string='Total', readonly=True, store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=[
        '|', ('active', '=', False), ('active', '=', True)])
    currency_id = fields.Many2one(
        related='order_id.currency_id', store=True, string='Currency', readonly=True)
    company_id = fields.Many2one(
        related='order_id.company_id', string='Company', store=True, readonly=True)


    @api.onchange('product_id')
    def product_id_change(self):

        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id.id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        price_unit = 0.0
        if product.list_price:
            price_unit = product.list_price
        vals['price_unit'] = price_unit

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(
                self._get_display_price(product), product.taxes_id, self.tax_id)
        self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {'warning': warning}
        return {'domain': domain}


    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            taxes = line.product_id.taxes_id.filtered(
                lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(
                taxes, line.product_id, line.order_id.partner_id) if fpos else taxes

    @api.model
    def create(self, values):
        onchange_fields = ['name', 'price_unit',
                           'product_uom', 'product_uom_qty', 'tax_id']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.product_id_change()
            for field in onchange_fields:
                if field not in values:
                    values[field] = line._fields[
                        field].convert_to_write(line[field], line)

        line = super(RequestOrderLine, self).create(values)
        return line

class product_product(models.Model):
    _inherit='product.product'
