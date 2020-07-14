# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    continent_id = fields.Many2one('res.continent', string="Continent")
    continent_region_id = fields.Many2one('res.continent.region')
    country_id = fields.Many2one('res.country', string="Country")
    island_group_id = fields.Many2one('res.island.group', string="Island Group")
    province_id = fields.Many2one('res.country.province', string="Province")
    city_id = fields.Many2one('res.country.city', string="City Name")
    barangay_id = fields.Many2one('res.barangay', string="Barangay")
    zip = fields.Char(string="Zip Code")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    state_id = fields.Many2one('res.country.state', string="Region")

    @api.onchange('address_home_id')
    def _onchange_address_home(self):
        if self.address_home_id:
            data = self.address_home_id
            self.street = data.street
            self.street2 = data.street2
            self.zip = data.zip
            self.barangay_id = data.barangay_id and data.barangay_id.id or False
            self.city_id = data.city_id and data.city_id.id or False

    @api.onchange('barangay_id')
    def onchange_barangay(self):
        if self.barangay_id:
            data = self.barangay_id
            self.zip = data.zip_code or False
            self.city_id = data.city_id and data.city_id.id or False

    @api.onchange('city_id')
    def onchange_city(self):
        if self.city_id:
            data = self.city_id
            self.province_id = data.province_id and data.province_id.id or False

    @api.onchange('province_id')
    def onchange_province(self):
        if self.province_id:
            data = self.province_id
            self.state_id = data.state_id and data.state_id.id

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            data = self.state_id
            self.island_group_id = data.island_group_id and data.island_group_id.id or False
            self.country_id = data.country_id.id

    @api.onchange('island_group_id')
    def onchange_island_group(self):
        if self.island_group_id:
            data = self.island_group_id
            self.country_id = data.country_id.id or False

    @api.onchange('country_id')
    def onchange_country(self):
        if self.country_id:
            data = self.country_id
            self.continent_region_id = data.continent_region_id and data.continent_region_id.id or False

    @api.onchange('continent_region_id')
    def onchange_continent_region_i(self):
        if self.continent_region_id:
            data = self.continent_region_id
            self.continent_id = data.continent_id and data.continent_id.id or False

