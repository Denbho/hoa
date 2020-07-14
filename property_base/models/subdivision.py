# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PropertySubdivisionPhaseUnitModel(models.Model):
    _name = "property.subdivision.phase.unit.model"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "house_model_id"

    company_id = fields.Many2one('res.company', 'Company', related="subdivision_phase_id.subdivision_id.company_id", store=True)
    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision")

    currency_id = fields.Many2one('res.currency', string="Currency", related="subdivision_phase_id.subdivision_id.company_id.currency_id")
    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase", ondelete="cascade")
    house_model_id = fields.Many2one('housing.model', string="House Model", required=True, track_visibility="always", domain="[('company_id', '=', company_id)]")
    property_type = fields.Selection([
        ('House', 'House and Lot'),
        ('Condo', 'Condo Unit')], string="Property Type", related="house_model_id.property_type", store=True)
    phase_type = fields.Selection([
        ('House', 'House and Lot'),
        ('Condo', 'Condo Unit'),
        ('House and Condo', 'House and Condo')], string="Phase Type", related="subdivision_phase_id.phase_type", store=True)
    model_type_id = fields.Many2one("property.model.type", string="Model Type", related="house_model_id.model_type_id", store=True)
    floor_area = fields.Float(string="Floor Area", track_visibility="always")
    lot_area = fields.Float(string="Lot Area", track_visibility="always")
    floor_area_price = fields.Monetary(string="Floor Area Price", help="Floor Area Price", track_visibility="always")
    lot_area_price = fields.Monetary(string="Lot Area Price", help="Lot Area Price", track_visibility="always")
    miscellaneous_value = fields.Monetary(string="MCC2", default=9, help="Miscellaneous Absolute Value")
    miscellaneous_charge = fields.Float(string="MCC", default=9, help="Miscellaneous Charge (%)")
    reservation_fee = fields.Monetary(string="Reservation Fee")
    downpayment_percent = fields.Float(string="Downpayment", default="15", help="Downpayment Term (%)")
    # downpayment_term = fields.Integer(string="DP Term", default="12", help="Downpayment Term")

    @api.onchange('house_model_id')
    def _onchange_house_model(self):
        if self.house_model_id:
            data = self.house_model_id
            self.floor_area = data.floor_area
            self.floor_area_price = data.floor_area_price
            self.lot_area = data.lot_area
            self.lot_area_price = data.lot_area_price
            self.miscellaneous_value = data.miscellaneous_value
            self.miscellaneous_charge = data.miscellaneous_charge
            self.reservation_fee = data.reservation_fee
            self.downpayment_percent = data.downpayment_percent


class PropertySubdivisionPhase(models.Model):
    _name = "property.subdivision.phase"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", related="account_analytic_id.name", store=True, default="/")
    account_analytic_group_set_id = fields.Many2one('account.analytic.group', string="Analytic Group")
    account_analytic_id = fields.Many2one('account.analytic.account', string="Subdivision Phase (Project Name)", required="1", help="This is link to Analytic Account")
    account_analytic_group_id = fields.Many2one('account.analytic.group', string="Business Entity", store=True, related="subdivision_id.account_analytic_group_id")
    company_id = fields.Many2one('res.company', 'Company', related="subdivision_id.company_id", store=True)
    description = fields.Text(string="Description")
    currency_id = fields.Many2one('res.currency', string="Currency", related="subdivision_id.company_id.currency_id")
    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision", ondelete="cascade", required=True)
    phase_type = fields.Selection([
        ('House', 'House and Lot'),
        ('Condo', 'Condo Unit')], string="Type", required=True)
    unit_model_ids = fields.One2many('property.subdivision.phase.unit.model', 'subdivision_phase_id', string="Unit Model")

    # trigered via CRONJob
    def create_analytic_group(self):
        rec = self.search([('account_analytic_group_set_id', 'in', [False])])
        for i in rec:
            group = self.env['account.analytic.group'].create({
                'name': i.name,
                'parent_id': i.account_analytic_group_id.id
            })
            i.write({'account_analytic_group_set_id': group.id})
            i.account_analytic_id.write({'group_id': group.id})


    @api.model
    def create(self, vals):
        res = super(PropertySubdivisionPhase, self).create(vals)
        group = self.env['account.analytic.group'].create({
            'name': res.name,
            'parent_id': res.account_analytic_group_id.id
        })
        res.write({'account_analytic_group_set_id': group.id})
        res.account_analytic_id.write({'group_id': group.id})
        return res

    def unlink(self):
        property = self.env['property.detail'].search([('property_subdivision_phase_unit_id', '=', self.id)], limit=1)
        if property[:1]:
            raise ValidationError(_('Delete first the property associated to this Subdivision Phase'))
        else:
            return super(PropertySubdivisionPhase, self).unlink()


class PropertySubdivision(models.Model):
    _name = "property.subdivision"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", help="Project / Subdivision", required=True)
    account_analytic_group_id = fields.Many2one('account.analytic.group', string="Business Entity/Analytic Group", required="1")
    project_desciption = fields.Text(string="BE Description", store=True, related="account_analytic_group_id.description")
    subdivision_code = fields.Char(string="Subdivision Code")
    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    company_code = fields.Char(string="Company Code", related="company_id.code", store=True)
    branch_id = fields.Many2one('res.branch', string="Branch", domain="[('company_id', '=', company_id)]")
    branch_code = fields.Char(string="Branch Code", related="branch_id.code", store=True)
    marketing_head_id = fields.Many2one('hr.employee', string="Marketing Head")
    property_type = fields.Selection([
                        ('horizontal', 'Horizontal'),
                        ('vertical', 'Vertical'),
                        ('both', 'Horizontal and Vertical')], string="Project Type")
    subdivision_phase_ids = fields.One2many('property.subdivision.phase', 'subdivision_id', string="Phases")
    continent_id = fields.Many2one('res.continent', string="Continent")
    continent_region_id = fields.Many2one('res.continent.region')
    country_id = fields.Many2one('res.country', string="Country")
    island_group_id = fields.Many2one('res.island.group', string="Island Group")
    province_id = fields.Many2one('res.country.province', string="Province")
    city_id = fields.Many2one('res.country.city', string="City")
    barangay_id = fields.Many2one('res.barangay', string="Barangay")
    state_id = fields.Many2one('res.country.state', string="Region/States")
    zip = fields.Char(string="Zip Code")
    cluster_id = fields.Many2one('res.region.cluster', string="Regional Cluster I")
    cluster2_id = fields.Many2one('res.region.cluster', string="Regional Cluster II")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")

    def unlink(self):
        property = self.env['property.detail'].search([('subdivision_id', '=', self.id)], limit=1)
        if property[:1]:
            raise ValidationError(_('Delete first the property associated to this Subdivision'))
        else:
            return super(PropertySubdivision, self).unlink()

    @api.onchange('barangay_id')
    def onchange_barangay(self):
        if self.barangay_id:
            data = self.barangay_id
            self.zip = data.zip_code
            self.city_id = data.city_id and data.city_id.id

    @api.onchange('city_id')
    def onchange_city(self):
        if self.city_id:
            data = self.city_id
            self.province_id = data.province_id and data.province_id.id

    @api.onchange('province_id')
    def onchange_province(self):
        if self.province_id:
            data = self.province_id
            self.state_id = data.state_id and data.state_id.id

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            data = self.state_id
            self.island_group_id = data.island_group_id and data.island_group_id.id

    @api.onchange('island_group_id')
    def onchange_island_group(self):
        if self.island_group_id:
            data = self.island_group_id
            self.country_id = data.country_id.id

    @api.onchange('country_id')
    def onchange_country(self):
        if self.country_id:
            data = self.country_id
            self.continent_region_id = data.continent_region_id and data.continent_region_id.id

    @api.onchange('continent_region_id')
    def onchange_continent_region_i(self):
        if self.continent_region_id:
            data = self.continent_region_id
            self.continent_id = data.continent_id and data.continent_id.id
