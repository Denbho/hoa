# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import locale


locale.setlocale(locale.LC_ALL, '')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_property = fields.Boolean(string="Is a Property", track_visibility="always")
    # property_unit = fields.Boolean(string="Inventory Unit")
    # reservation_use = fields.Boolean(string="Reservation Use Only")
    property_id = fields.Many2one('property.detail', string="Property", track_visibility="always", domain="[('product_id', 'in', [False])]", ondelete="cascade")
    name = fields.Char(compute="_compute_name", inverse="_inverse_compute_name", store=True, track_visibility="always", required=True)

    reservation_price = fields.Monetary(string="Reservation Price")


    @api.model
    def create(self, vals):
        if not vals.get('description_sale') and vals.get('property_id'):
            property_data = self.env['property.detail'].browse(vals.get('property_id'))
            vals['description_sale'] = f"Property Reservation \
                    \nLot Area: {property_data.lot_area}m² \
                    \nFloor Area: {property_data.floor_area}m² \
                    \nTCP: Php {locale.format('%0.2f', property_data.tcp, grouping=True)} VAT Exclusive"
        return super(ProductTemplate, self).create(vals)


    @api.onchange('is_property')
    def _onchange_is_property(self):
        if not self.is_property:
            self.property_id = False

    @api.depends('is_property', 'property_id')
    def _compute_name(self):
        for i in self:
            i.name = (i.is_property and i.property_id) and  i.property_id.name or False

    def _inverse_compute_name(self):
        for i in self:
            if not i.is_property and not i.property_id:
                continue
