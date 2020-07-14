# -*- coding: utf-8 -*-
import logging
import math
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger("_name_")


def roundup(val, round_val):
    return math.ceil(val / round_val) * round_val


class PropertyVendorGroup(models.Model):
    _name = 'property.vendor.group'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    broker = fields.Boolean(string="A Broker?")
    agent = fields.Boolean(string="An Agent?")
    vendor_group_id = fields.Many2one('property.vendor.group', string="Vendor Group")



class CRMLead(models.Model):
    _inherit = 'crm.lead'
    
    property_reservation = fields.Boolean(string="Is a Property Reservation", track_visibility="always", default=True)
    reservation_type = fields.Selection([('online', 'Online'), ('onsite', 'Onsite')], string="Type of Reservation",
                                        track_visibility="always")
    broker_partner_id = fields.Many2one('res.partner', string="Broker",
                                        context="{'default_broker': 1, 'default_vendor_group_id': vendor_group_id, 'default_company_type': 'company'}")
    agent_partner_id = fields.Many2one('res.partner', string="Agent")
    sales_manager_partner_id = fields.Many2one('res.partner', string="Sales Manager")
    sales_team_lead_partner_id = fields.Many2one('res.users', string="Sales Team Lead", related="team_id.user_id",
                                                 store=True, track_visibility="always")
    vendor_group_id = fields.Many2one('property.vendor.group', string="Vendor Group")
    property_id = fields.Many2one('property.detail', string="Property", compute="_get_property_detail",
                                  inverse="_inverse_property_detail", store=True, track_visibility="always")
    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision", compute="_get_property_detail",
                                     inverse="_inverse_property_detail", store=True, track_visibility="always",
                                     required=True)
    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase", compute="_get_property_detail",
                                           inverse="_inverse_property_detail", store=True, track_visibility="always",
                                           required=True)
    house_model_id = fields.Many2one('housing.model', string="Unit/House Model", compute="_get_property_detail",
                                     inverse="_inverse_property_detail", store=True, track_visibility="always")
    property_subdivision_phase_unit_ids = fields.Many2many('housing.model', 'crm_property_house_unit_rel',
                                                           'property_id', 'unit_id',
                                                           compute="_get_subdivision_phase_unit")
    brand_id = fields.Many2one('product.brand', string='Property Brand', store=True, related="house_model_id.brand_id")
    model_type_id = fields.Many2one("property.model.type", string="Model Type", store=True,
                                    related="property_id.model_type_id")
    floor_area = fields.Float(string="Floor Area", store=True, related="property_id.floor_area")
    lot_area = fields.Float(string="Lot Area", store=True, related="property_id.lot_area")
    property_type = fields.Selection([
        ('House', 'House and Lot'),
        ('Condo', 'Condo Unit')],
        string="Property Type", related="house_model_id.property_type", store=True)
    branch_id = fields.Many2one('res.branch', string="Branch", related="subdivision_id.branch_id")
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
    property_price_range_id = fields.Many2one('property.price.range', string="Price Range",
                                              compute="_get_property_price", inverse="_inverse_property_price",
                                              store=True)
    inquiry_date = fields.Date(string="Inquiry Date", default=fields.Date.context_today)
    religion_id = fields.Many2one('res.partner.religion', string="Religion")
    nationality_country_id = fields.Many2one('res.country', string="Nationality")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age")
    age_range_id = fields.Many2one('res.partner.age.range', string="Age Range")
    employment_status_id = fields.Many2one('res.partner.employment.status', string="Employment Status")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", tracking=True)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced'),
        ('separated', 'Separated'),
        ('annulled', 'Annulled')
    ], string='Marital Status', tracking=True)

    @api.constrains('inquiry_date')
    def _validate_inquiry_date(self):
        if self.inquiry_date and self.inquiry_date > date.today():
            raise UserError(_('Inquiry Date must be not greater today!'))

    @api.depends('product_id')
    def _get_property_detail(self):
        for i in self:
            if i.product_id and i.product_id.is_property:
                property_data = i.product_id.property_id
                i.property_id = property_data.id
                i.subdivision_id = property_data.subdivision_id.id
                i.subdivision_phase_id = property_data.subdivision_phase_id.id
                i.house_model_id = property_data.house_model_id.id

    def _inverse_property_detail(self):
        for i in self:
            if not i.product_id or not i.product_id.is_property:
                continue

    def action_view_sale_quotation(self):
        res = super(CRMLead, self).action_view_sale_quotation()
        if self.product_id:
            order_lines = []
            _logger.info(f"\n\nContecxt: {self._context}\n\n")
            for order_line in self.order_line:
                order_lines.append([0, 0, {'product_id': order_line.product_id.id,
                                           'name': order_line.name,
                                           'product_uom_qty': order_line.product_uom_qty,
                                           'price_unit': order_line.price_unit,
                                           'tax_id': [(6, 0, order_line.tax_id.ids)],
                                           'price_subtotal': order_line.price_subtotal,
                                           'product_uom_id': order_line.product_id.id,
                                           }])
            res['context']['default_order_line'] = order_lines
        return res

    def action_new_quotation(self):
        res = super(CRMLead, self).action_new_quotation()
        if self.product_id:
            order_lines = []
            _logger.info(f"\n\nContecxt: {self._context}\n\n")
            for order_line in self.order_line:
                order_lines.append([0, 0, {'product_id': order_line.product_id.id,
                                           'name': order_line.name,
                                           'product_uom_qty': order_line.product_uom_qty,
                                           'price_unit': order_line.price_unit,
                                           'tax_id': [(6, 0, order_line.tax_id.ids)],
                                           'price_subtotal': order_line.price_subtotal,
                                           'product_uom_id': order_line.product_id.id,
                                           }])
            res['context']['default_order_line'] = order_lines
        return res

    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        """ extract data from lead to create a partner
            :param name : furtur name of the partner
            :param is_company : True if the partner is a company
            :param parent_id : id of the parent partner (False if no parent)
            :returns res.partner record
        """
        res = super(CRMLead, self)._create_lead_partner_data(name, is_company, parent_id)
        res.update({
            'religion_id': self.religion_id.id,
            'nationality_country_id': self.nationality_country_id.id,
            'date_of_birth': self.date_of_birth,
            'age': self.age,
            'age_range_id': self.age_range_id.id,
            'employment_status_id': self.employment_status_id.id,
            'gender': self.gender,
            'marital': self.marital
        })
        return res

    @api.onchange('date_of_birth')
    def onchange_dob(self):
        if self.date_of_birth:
            age = date.today().year - self.date_of_birth.year
            self.age = age
            age_range = self.env['res.partner.age.range'].search([('range_from', '<=', age), ('range_to', '>=', age)],
                                                                 limit=1)
            # _logger.info(f'\n\nAge: {age}\tRange: {age_range.id}\n\n\n')
            self.age_range_id = age_range[:1] and age_range.id or False

    @api.depends('house_model_id', 'property_id')
    def _get_property_price(self):
        for i in self:
            tcp = 0
            if i.house_model_id and i.property_id:
                house_price = roundup(i.property_id.floor_area * i.property_id.floor_area_price, 10)
                lot_price = roundup(i.property_id.lot_area * i.property_id.lot_area_price, 10)
                ntcp = sum([house_price, lot_price])
                miscellaneous_amount = roundup(
                    (ntcp * (i.property_id.miscellaneous_charge / 100)) + i.property_id.miscellaneous_value, 10)
                tcp = roundup(sum([ntcp, miscellaneous_amount]), 10)
            elif i.house_model_id and not i.property_id:
                house_model = self.env['property.subdivision.phase.unit.model'].search(
                    [('house_model_id', '=', i.house_model_id.id),
                     ('subdivision_phase_id', '=', i.subdivision_phase_id.id)], limit=1)
                if house_model[:1]:
                    house_price = roundup(house_model.floor_area * house_model.floor_area_price, 10)
                    lot_price = roundup(house_model.lot_area * house_model.lot_area_price, 10)
                    ntcp = sum([house_price, lot_price])
                    miscellaneous_amount = roundup(
                        (ntcp * (house_model.miscellaneous_charge / 100)) + house_model.miscellaneous_value, 10)
                    tcp = roundup(sum([ntcp, miscellaneous_amount]), 10)
            price_range = self.env['property.price.range'].search([('range_from', '<=', tcp), ('range_to', '>=', tcp)],
                                                                  limit=1)
            i.property_price_range_id = price_range[:1] and price_range.id or False

    def _inverse_property_price(self):
        for i in self:
            if not i.house_model_id and not i.property_id:
                continue

    @api.depends('subdivision_phase_id')
    def _get_subdivision_phase_unit(self):
        for i in self:
            i.property_subdivision_phase_unit_ids = []
            if i.subdivision_phase_id:
                i.property_subdivision_phase_unit_ids = [rec.house_model_id.id for rec in
                                                         i.subdivision_phase_id.unit_model_ids]

    @api.onchange('broker_partner_id')
    def _onchange_broker(self):
        if self.broker_partner_id:
            self.vendor_group_id = self.broker_partner_id.vendor_group_id and self.broker_partner_id.vendor_group_id.id or False
