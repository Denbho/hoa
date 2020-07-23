# -*- coding: utf-8 -*-
import locale
import math

from odoo import api, fields, models
from odoo.osv import expression


def roundup(val, round_val):
    return math.ceil(val / round_val) * round_val


class PropertyModelType(models.Model):
    _name = 'property.model.type'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")


class PropertyPriceRange(models.Model):
    _name = 'property.price.range'

    range_from = fields.Float(string="From", required=True)
    range_to = fields.Float(string="To", required=True)
    name = fields.Char(string="Display Range", store=True, compute="_get_range_name")

    @api.depends('range_from', 'range_to')
    def _get_range_name(self):
        for i in self:
            if i.range_from and i.range_to:
                i.name = f"Php {locale.format('%0.2f', i.range_from, grouping=True)} - Php {locale.format('%0.2f', i.range_to, grouping=True)}"

    @api.constrains('range_from', 'range_to')
    def _check_range(self):
        if self.range_from >= self.range_to:
            raise ValidationError(_('"Range To" must greate than "Range From" value.'))


class HousingModel(models.Model):
    _name = 'housing.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Model", required=True, track_visibility="always")
    floor_area = fields.Float(string="Floor Area", track_visibility="always")
    lot_area = fields.Float(string="Lot Area", track_visibility="always")
    lot_area_price = fields.Monetary(string="Lot Area Price", help="Lot Area Price")
    floor_area_price = fields.Monetary(string="Floor Area Price", help="Floor Area Price", track_visibility="always")
    miscellaneous_value = fields.Monetary(string="MCC2", default=9, help="Miscellaneous Absolute Value")
    miscellaneous_charge = fields.Float(string="MCC", default=9, help="Miscellaneous Charge (%)")
    reservation_fee = fields.Monetary(string="Reservation Fee")
    downpayment_percent = fields.Float(string="Downpayment", default="15", help="Downpayment Term (%)")
    # downpayment_term = fields.Integer(string="DP Term", default="12", help="Downpayment Term")
    property_type = fields.Selection([
        ('House', 'House and Lot'),
        ('Condo', 'Condo Unit')], string="Property Type", default="House", required=True)

    model_type_id = fields.Many2one("property.model.type", string="Model Type", track_visibility="always")
    description = fields.Text(string="Description", track_visibility="always")
    year_month = fields.Char(string="Year Month", track_visibility="always")
    model_blue_print = fields.Binary(string="Plan", track_visibility="always")
    house_model_image_ids = fields.One2many('product.image', 'housing_model_tmpl_id', string='Images')
    brand_id = fields.Many2one('product.brand', string='Brand')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")

    def unlink(self):
        for rec in self:
            property = rec.env['property.detail'].search([('house_model_id', '=', rec.id)]).ids
            property += rec.env['property.subdivision.phase.unit.model'].search([('house_model_id', '=', rec.id)]).ids
            if property:
                raise ValidationError(_('Delete first the property associated to this Subdivision Phase'))
        return super(HousingModel, self).unlink()


class HousingProjectModelImage(models.Model):
    _inherit = 'product.image'
    _description = 'House Model Image'

    housing_model_tmpl_id = fields.Many2one('housing.model', string='Related Models', copy=True)


class PropertySaleRemark(models.Model):
    _name = "property.sale.remark"

    name = fields.Char(string="Remark", required=True)
    description = fields.Text(string="Description")


class PropertyFinancingTypeTerm(models.Model):
    _name = "property.financing.type.term"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    financing_type_id = fields.Many2one('property.financing.type', string="Financing Type")
    name = fields.Char(string="Display Name", store=True, compute="_get_name")
    year = fields.Integer(string="Years", help="Number of Years to Pay", track_visibility="always")
    interest_rate = fields.Float(string="Interest Rate (%)", track_visibility="always")
    payment_term_id = fields.Many2one('account.payment.term', string="Accounting Payment Term")

    @api.depends('year', 'interest_rate')
    def _get_name(self):
        for i in self:
            if i.year and i.interest_rate:
                i.name = f"{i.year}YEARS @ {i.interest_rate}% INTEREST"


class PropertyFinancingType(models.Model):
    _name = "property.financing.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Financing Type", required=True, track_visibility="always")
    code = fields.Char(string="Code", required=True, track_visibility="always")
    description = fields.Text(string="Description", track_visibility="always")
    financing_term_ids = fields.One2many('property.financing.type.term', 'financing_type_id',
                                         string="Payment Terms and Interest Rates")

    # payment_term_id = fields.Many2one('account.payment.term', string="Payment Term")

    def name_get(self):
        res = super(PropertyFinancingType, self).name_get()
        data = []
        for i in self:
            display_value = f"{i.name} [{i.code}]"
            data.append((i.id, display_value))
        return data

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', '|', ('code', operator, name), ('name', operator, name), ('description', operator, name)]
        return super(PropertyFinancingType, self).search(expression.AND([args, domain]), limit=limit).name_get()


class PropertyDownpaymentTerm(models.Model):
    _name = "property.downpayment.term"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Display Name", store=True, compute="_get_name")
    month = fields.Integer(string="Months", help="Number of Month to Pay", track_visibility="always")
    interest_rate = fields.Float(string="Interest Rate", track_visibility="always")
    payment_term_id = fields.Many2one('account.payment.term', string="Accounting Payment Term")

    @api.depends('month', 'interest_rate')
    def _get_name(self):
        for i in self:
            i.name = f"{i.month}Months @ {i.interest_rate}% INTEREST"


class PropertyDetail(models.Model):
    _name = "property.detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    account_analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                          help="This is link to Analytic Account", readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")
    image = fields.Binary(string="Model Image", track_visibility="always")
    name = fields.Char(string="Display Name", store=True,
                       compute="_get_display_name")  # Block-Lot - House Type (Subdivision)
    block_lot = fields.Char(string="Block-Lot", required=True, track_visibility="always")
    property_type = fields.Selection([
        ('House', 'House and Lot'),
        ('Condo', 'Condo Unit')],
        string="Property Type", related="house_model_id.property_type", store=True)
    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision", required=True,
                                     track_visibility="always",
                                     domain="[('company_id', '=', company_id)]")
    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase")
    property_subdivision_phase_ids = fields.Many2many('property.subdivision.phase', 'property_phase_rel', 'property_id',
                                                      'phase_id',
                                                      compute="_get_subdivision_phase")
    property_subdivision_phase_unit_id = fields.Many2one('property.subdivision.phase.unit.model')
    house_model_id = fields.Many2one('housing.model', string="Unit/House Model", required=True,
                                     track_visibility="always")
    property_subdivision_phase_unit_ids = fields.Many2many('housing.model', 'property_house_unit_rel', 'property_id',
                                                           'unit_id', compute="_get_subdivision_phase_unit")
    state = fields.Selection([
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
        ('Contracted', 'Contracted'),
        ('On-Hold', 'On-Hold'),
    ], string="Property Status", default="Available", track_visibility="always")
    unit_state = fields.Selection([
        ('development', 'Ongoing Development'),
        ('completed', 'Completed'),
        ('halted', 'Halted'),
        ('scrapped', 'Scrapped')
    ], string="Property Building Status", default="development",
        required=True, track_visibility="always")
    house_unit_status = fields.Selection([
        ('Lot Only', 'Lot Only'),
        ('NRFO', 'NRFO'),
        ('RFO', 'RFO')], string="House Unit Status", track_visibility="always")
    rfo = fields.Boolean(string="RFO", track_visibility="always", help="Ready for Occupancy")
    rfo_date = fields.Date(string="RFO Date", track_visibility="always")
    mobilization_date = fields.Date(string="Mobilization Date", track_visibility="always")
    completion_date = fields.Date(string="Completion Date", track_visibility="always")

    # Account Management Group
    sale_status = fields.Selection([
        ('Outstanding', 'Outstanding'),
        ('Fully Paid', 'Fully Paid'),
        ('Loan Released', 'Loan Released'),
        ('Winner', 'Awarded to Winner'),
        ('No Buyer', 'No Buyer')], string="SO Status",
        default="No Buyer", track_visibility="always")
    sale_id = fields.Many2one('sale.order', string="SO Reference Link", track_visibility="always")
    sale_reference = fields.Char(string="SO Number", compute="_get_sale_detail",
                                 inverse="_inverse_sale_details", store=True, track_visibility="always")
    reservation_date = fields.Date(string="RS Date", track_visibility="always", help="Reservation Date")
    contracted_date = fields.Date(string="CS Date", track_visibility="always", help="Contracted Date")
    sale_remark_id = fields.Many2one('property.sale.remark', string="SO Remarks")
    financing_type_id = fields.Many2one('property.financing.type', string="Financing Type", track_visibility="always")
    financing_type_term_id = fields.Many2one('property.financing.type.term',
                                             domain="[('financing_type_id', '=', financing_type_id)]",
                                             string="Financing Term", track_visibility="always")
    fully_paid = fields.Boolean(string="Fully Paid", track_visibility="always", help="Fully Paid/Loan Released")
    fully_paid_date = fields.Date(string="LR/FP Date", track_visibility="always",
                                  help="Loan Released / Fully Paid Date")
    turnover_qualified = fields.Boolean(string="Qualified for Turnover?", track_visibility="always")
    movein_kit = fields.Boolean(string="With Move In Kit", help="Admin Endorsement-(Move in Kit)",
                                track_visibility="always")
    endorsement_date = fields.Date(string="Endorsement Date", track_visibility="always")

    # Customer Care
    ccd_accepted = fields.Boolean(string="CCD Acceptance", track_visibility="always")
    customer_care_user_id = fields.Many2one('res.users', string="CCD In-Charge", help="Customer Care In-Charge")
    ccd_acceptance_date = fields.Date(string="CCD Acceptance Date", track_visibility="always")
    partner_id = fields.Many2one('res.partner', string="Customer/Buyer", compute="_get_sale_detail",
                                 inverse="_inverse_sale_details", store=True, track_visibility="always")
    turned_over = fields.Boolean(string="Turned Over?", track_visibility="always")
    turnover_date = fields.Date(string="Turnover Date", track_visibility="always")
    turnover_remark_id = fields.Many2one('property.sale.remark', string="Turnover Remarks")
    moved_in = fields.Boolean(string="Moved In?", track_visibility="always")
    movein_date = fields.Date(string="Move In Date", track_visibility="always")
    movein_remark_id = fields.Many2one('property.sale.remark', string="Move In Remarks")

    atmi = fields.Boolean(string="ATMI", help="Autority to Move-In", track_visibility="always")
    atmi_date = fields.Date(string="ATMI Date", help="Autority to Move-In Date", track_visibility="always")
    pdc = fields.Boolean(string="PDC", help="Post Dated Check", track_visibility="always")
    deed_absolute_sale_attachment = fields.Binary(string="Deed of Absolute Sale", track_visibility="always")
    das = fields.Boolean(string="DAS", track_visibility="always")
    das_date = fields.Date(string="DAS Date", track_visibility="always")

    # Property Details
    sale_category = fields.Selection([('economic', 'Economic'), ('socialized', 'Socialized')], string="Sale Category",
                                     track_visibility="always")
    miscellaneous_charge = fields.Float(string="Miscellaneous Charge", default=9, track_visibility="always")
    lot_area_price = fields.Monetary(string="Lot Area Price", track_visibility="always")
    floor_area_price = fields.Monetary(string="Floor Area Price", track_visibility="always")
    model_type_id = fields.Many2one("property.model.type", string="Model Type", store=True, compute="_get_display_name")
    floor_area = fields.Float(string="Floor Area", track_visibility="always")
    lot_area = fields.Float(string="Lot Area", track_visibility="always")
    phase_type = fields.Selection([('House', 'House and Lot'), ('Condo', 'Condo Unit')], string="Type",
                                  store=True, related="subdivision_phase_id.phase_type")
    miscellaneous_value = fields.Monetary(string="MCC2", default=9, help="Miscellaneous Absolute Value")
    reservation_fee = fields.Monetary(string="Reservation Fee")
    downpayment_percent = fields.Float(string="Downpayment", default="15", help="Downpayment Term (%)")
    downpayment_term_id = fields.Many2one('property.downpayment.term', string="Downpayment Term")
    house_price = fields.Monetary(string="House Price", compute="_get_contract_price", store=True)
    lot_price = fields.Monetary(string="Lot Price", compute="_get_contract_price", store=True)
    miscellaneous_amount = fields.Monetary(string="Miscellaneous Amount", compute="_get_contract_price", store=True)
    ntcp = fields.Monetary(string="NTCP", help="Total Net Contract Price", compute="_get_contract_price", store=True)
    tcp = fields.Monetary(string="TPC", help="Total Contract Price", compute="_get_contract_price", store=True)
    price_range_id = fields.Many2one('property.price.range', string="Price Range", compute="_get_contract_price",
                                     store=True)

    water_meter = fields.Char(string="Water Meter")
    electricity_meter = fields.Char(string="Electricity Meter")
    internet = fields.Boolean(string="With Internet?")
    internet_provider_contact_id = fields.Many2one('res.partner', string="Internet Provider (ISP)")
    cable = fields.Boolean(string="With Cable?")
    cable_provider_partner_id = fields.Many2one('res.partner', string="Cable Service Provider (CSP)")
    house_plate = fields.Char(string="House Plate")
    title_owner_partner_id = fields.Many2one('res.partner', string="Title Owner")
    home_owner_membership_date = fields.Date(string="HOA Membership Date", help="Home Owners Association Membership Date")

    @api.model
    def create(self, vals):
        res = super(PropertyDetail, self).create(vals)
        analytic = self.env['account.analytic.account'].create({
            'name': res.name,
            'group_id': res.subdivision_phase_id.account_analytic_group_set_id.id
        })
        res.write({'account_analytic_id': analytic.id})
        return res

    # trigered via CRONJob
    def create_analytic_account(self):
        rec = self.search([('account_analytic_id', 'in', [False])])
        for i in rec:
            analytic = self.env['account.analytic.account'].create({
                'name': i.name,
                'group_id': i.subdivision_phase_id.account_analytic_group_set_id.id
            })
            i.write({'account_analytic_id': analytic.id})

    @api.depends('floor_area', 'floor_area_price', 'lot_area', 'lot_area_price',
                 'miscellaneous_value', 'miscellaneous_charge')
    def _get_contract_price(self):
        for i in self:
            house_price = roundup(i.floor_area * i.floor_area_price, 10)
            lot_price = roundup(i.lot_area * i.lot_area_price, 10)
            ntcp = sum([house_price, lot_price])
            miscellaneous_amount = ntcp * (i.miscellaneous_charge / 100)
            i.house_price = house_price
            i.lot_price = lot_price
            i.ntcp = ntcp
            i.miscellaneous_amount = roundup(miscellaneous_amount + i.miscellaneous_value, 10)
            i.tcp = roundup(sum([ntcp, miscellaneous_amount, i.miscellaneous_value]), 10)
            price_range = self.env['property.price.range'].search(
                [('range_from', '<=', i.tcp), ('range_to', '>=', i.tcp)], limit=1)
            i.price_range_id = price_range[:1] and price_range.id or False

    @api.depends('subdivision_phase_id')
    def _get_subdivision_phase_unit(self):
        for i in self:
            i.property_subdivision_phase_unit_ids = []
            if i.subdivision_phase_id:
                i.property_subdivision_phase_unit_ids = [rec.house_model_id.id for rec in
                                                         i.subdivision_phase_id.unit_model_ids]

    @api.depends('subdivision_id')
    def _get_subdivision_phase(self):
        for i in self:
            i.property_subdivision_phase_ids = i.subdivision_id.subdivision_phase_ids.ids

    @api.onchange('house_model_id')
    def _onchange_house_model(self):
        if self.house_model_id and self.subdivision_phase_id:
            data = self.env['property.subdivision.phase.unit.model'].search([
                ('house_model_id', '=', self.house_model_id.id),
                ('subdivision_phase_id', '=', self.subdivision_phase_id.id)], limit=1)
            if not data[:1]:
                data = self.house_model_id
            self.floor_area = data.floor_area
            self.floor_area_price = data.floor_area_price
            self.lot_area = data.lot_area
            self.lot_area_price = data.lot_area_price
            self.miscellaneous_charge = data.miscellaneous_charge
            self.miscellaneous_value = data.miscellaneous_value
            # self.downpayment_term = data.downpayment_term
            # self.downpayment_percent = data.downpayment_percent
            self.reservation_fee = data.reservation_fee

    @api.depends('block_lot',
                 'house_model_id', 'house_model_id.name',
                 'subdivision_id', 'subdivision_id.name',
                 'house_model_id.model_type_id',
                 'subdivision_phase_id', 'subdivision_phase_id.name')
    def _get_display_name(self):
        for i in self:
            if i.block_lot and i.house_model_id and i.subdivision_id and i.subdivision_phase_id:
                i.name = f"{i.block_lot} - {i.house_model_id.name} ({i.subdivision_id.name} - {i.subdivision_phase_id.name})"
                i.model_type_id = i.house_model_id.model_type_id and i.house_model_id.model_type_id.id or False

    @api.depends('sale_id')
    def _get_sale_detail(self):
        for i in self:
            i.sale_reference = i.sale_id and i.sale_id.name or False
            i.partner_id = i.sale_id and i.sale_id.partner_id.id or False

    def _inverse_sale_details(self):
        for i in self:
            if not i.sale_id:
                continue
