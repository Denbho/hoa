# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger("_name_")

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    social_media_ids = fields.One2many('res.partner.social.media', 'lead_id', string="Social Media")
    continent_id = fields.Many2one('res.continent', string="Continent")
    continent_region_id = fields.Many2one('res.continent.region')
    island_group_id = fields.Many2one('res.island.group', string="Island Group")
    province_id = fields.Many2one('res.country.province', string="Province")
    city_id = fields.Many2one('res.country.city', string="City")
    barangay_id = fields.Many2one('res.barangay', string="Barangay")


    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        """ extract data from lead to create a partner
            :param name : furtur name of the partner
            :param is_company : True if the partner is a company
            :param parent_id : id of the parent partner (False if no parent)
            :returns res.partner record
        """
        res = super(CRMLead, self)._create_lead_partner_data(name, is_company, parent_id)
        social_media = [[0, 0, {
            # 'lead_id': self.id,
            'name': i.name,
            'description': i.description,
            'media_type_id': i.media_type_id.id
        }] for i in self.social_media_ids]
        res.update({
            'continent_id': self.continent_id.id,
            'continent_region_id': self.continent_region_id.id,
            'city_id': self.city_id.id,
            'island_group_id': self.island_group_id.id,
            'province_id': self.province_id.id,
            'barangay_id': self.barangay_id.id,
            'social_media_ids': social_media
        })
        return res


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
            self.city = f"{data.name}"
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
