# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PropertyDetail(models.Model):
    _inherit = "property.detail"

    product_id = fields.Many2one('product.template', string="Inventory Name", ondelete="cascade", copy=False, track_visibility="always",
                                 context="{'default_property_id': active_id, 'default_is_property': 1, 'default_list_price': reservation_fee, 'default_company_id': company_id, 'default_type': 'product', 'default_purchase_ok': 0}")
    tcp_marketing_markup = fields.Monetary(string="Markup", track_visibility="always")


class PropertySubdivisionPhase(models.Model):
    _inherit = "property.subdivision.phase"

    downpayment_term_ids = fields.Many2many('property.downpayment.term', 'phase_dp_term_rel', 'phase_id', 'term_id', string="Downpayment Terms")
    financing_type_ids = fields.Many2many('property.financing.type', 'phase_financingtype_rel', 'phase_id', 'term_id', string="Financing Types")
