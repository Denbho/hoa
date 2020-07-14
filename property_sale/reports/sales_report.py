# -*- coding: utf-8 -*-

from odoo import fields, models
import logging

_logger = logging.getLogger("_name_")


class SaleReport(models.Model):
    _inherit = "sale.report"

    property_sale = fields.Boolean(string="Sale of Property")
    managing_director_employee_id = fields.Many2one('hr.employee', string="Managing Director")
    marketing_lead_employee_id = fields.Many2one('hr.employee', string="Marketing Team Lead")
    broker_partner_id = fields.Many2one('res.partner', string="Broker/Realty")
    vendor_group_id = fields.Many2one('property.vendor.group', string="Vendor Group")
    downpayment_term_id = fields.Many2one('property.downpayment.term', string="Downpayment Term")
    downpayment_percent = fields.Float(string="Downpayment", help="Downpayment Term (%)")
    financing_type_id = fields.Many2one('property.financing.type', string="Financing Type")
    financing_type_term_id = fields.Many2one('property.financing.type.term', string="Financing Term")
    downpayment_amount = fields.Float(string="DP Amount")
    dp_discount_amount = fields.Float(string="DP Discount")
    ntcp_discount_amount = fields.Float(string="Buyers Discount")
    net_of_ntcp_discount_amount = fields.Float(string="Net of Discount Discount")
    spot_amount = fields.Float(string="Spot Cash Payment")
    dp_amount_due = fields.Float(string="Amount Due")
    dp_interest = fields.Float(string="DP Interest")
    dp_monthly_due = fields.Float(string="Monthly Due")
    turned_over_balance_amount = fields.Float(string="Turnover Balance Amount")
    turned_over_balance_percent = fields.Float(string="Turnover Balance Percent")
    turned_over_balance_mdue = fields.Float(string="After Turnover Monthly Due")
    property_id = fields.Many2one('property.detail')
    house_price = fields.Float(string="House Price")
    lot_price = fields.Float(string="Lot Price")
    miscellaneous_amount = fields.Float(string="Miscellaneous Amount")
    reservation_fee = fields.Float(string="Reservation Fee")
    ntcp = fields.Float(string="NTCP")
    tcp = fields.Float(string="TPC")
    tcp_vat = fields.Float(string="TPC + Vat")
    property_vat = fields.Float(string="VAT")
    spot_dp_invoice_id = fields.Many2one('account.move', string="Spot Cash DP Invoice")
    dp_invoice_id = fields.Many2one('account.move', string="Downpayment Invoice")
    turnover_balance_invoice_id = fields.Many2one('account.move', string="Turnover Balance Invoice")
    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision")
    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase")
    house_model_id = fields.Many2one('housing.model', string="Unit/House Model")
    brand_id = fields.Many2one('product.brand', string='Property Brand')
    model_type_id = fields.Many2one("property.model.type", string="Model Type")
    floor_area = fields.Float(string="Floor Area")
    lot_area = fields.Float(string="Lot Area")
    property_type = fields.Selection([('House', 'House and Lot'), ('Condo', 'Condo Unit')], string="Property Type")
    property_continent_id = fields.Many2one('res.continent', string="Property Continent")
    property_continent_region_id = fields.Many2one('res.continent.region', string="Property Continent Region")
    property_country_id = fields.Many2one('res.country', string="Property Country")
    property_island_group_id = fields.Many2one('res.island.group', string="Property Island Group")
    property_province_id = fields.Many2one('res.country.province', string="Property Province")
    property_city_id = fields.Many2one('res.country.city', string="Property City")
    property_barangay_id = fields.Many2one('res.barangay', string="Property Barangay")
    property_state_id = fields.Many2one('res.country.state', string="Property Region/States")
    property_zip = fields.Char(string="Property Zip Code", store=True)
    property_cluster_id = fields.Many2one('res.region.cluster', string="Regional Cluster I")
    property_cluster2_id = fields.Many2one('res.region.cluster', string="Regional Cluster II")
    property_street = fields.Char(string="Street")
    property_street2 = fields.Char(string="Street2")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields.update({
            'is_property': ", t.is_property as property_sale",
            'managing_director_employee_id': ",  s.managing_director_employee_id as managing_director_employee_id",
            'marketing_lead_employee_id': ", s.marketing_lead_employee_id as marketing_lead_employee_id",
            'broker_partner_id': ", s.broker_partner_id as broker_partner_id",
            'vendor_group_id': ", s.vendor_group_id as vendor_group_id",
            'downpayment_term_id': ", s.downpayment_term_id as downpayment_term_id",
            'downpayment_percent': ", s.downpayment_percent as downpayment_percent",
            'financing_type_id': ", s.financing_type_id as financing_type_id",
            'financing_type_term_id': ", s.financing_type_term_id as financing_type_term_id",
            'downpayment_amount': ", s.downpayment_amount as downpayment_amount",
            'dp_discount_amount': ", s.dp_discount_amount as dp_discount_amount",
            'ntcp_discount_amount': ", s.ntcp_discount_amount as ntcp_discount_amount",
            'net_of_ntcp_discount_amount': ", s.net_of_ntcp_discount_amount as net_of_ntcp_discount_amount",
            'spot_amount': ", s.spot_amount as spot_amount",
            'dp_amount_due': ", s.dp_amount_due as dp_amount_due",
            'dp_interest': ", s.dp_interest as dp_interest",
            'dp_monthly_due': ", s.dp_monthly_due as dp_monthly_due",
            'turned_over_balance_amount': ", s.turned_over_balance_amount as turned_over_balance_amount",
            'turned_over_balance_percent': ", s.turned_over_balance_percent as turned_over_balance_percent",
            'turned_over_balance_mdue': ", s.turned_over_balance_mdue as turned_over_balance_mdue",
            'property_id': ", s.property_id as property_id",
            'house_price': ", s.house_price as house_price",
            'lot_price': ", s.lot_price as lot_price",
            'miscellaneous_amount': ", s.miscellaneous_amount as miscellaneous_amount",
            'reservation_fee': ", s.reservation_fee as reservation_fee",
            'ntcp': ", s.ntcp as ntcp",
            'tcp': ", s.tcp as tcp",
            'tcp_vat': ", s.tcp_vat as tcp_vat",
            'property_vat': ", s.property_vat as property_vat",
            'spot_dp_invoice_id': ", s.spot_dp_invoice_id as spot_dp_invoice_id",
            'dp_invoice_id': ", s.dp_invoice_id as dp_invoice_id",
            'turnover_balance_invoice_id': ", s.turnover_balance_invoice_id as turnover_balance_invoice_id",
            'subdivision_id': ", s.subdivision_id as subdivision_id",
            'subdivision_phase_id': ", s.subdivision_phase_id as subdivision_phase_id",
            'house_model_id': ", s.house_model_id as house_model_id",
            'model_type_id': ", s.model_type_id as model_type_id",
            'floor_area': ", s.floor_area as floor_area",
            'lot_area': ", s.lot_area as lot_area",
            'property_type': ", s.property_type as property_type",
            'brand_id': ", s.brand_id as brand_id",
            'model_type_id': ", s.model_type_id as model_type_id",
            'floor_area': ", s.floor_area as floor_area",
            'lot_area': ", s.lot_area as lot_area",
            'property_type': ", s.property_type as property_type",
            'property_continent_id': ", s.property_continent_id as property_continent_id",
            'property_continent_region_id': ", s.property_continent_region_id as property_continent_region_id",
            'property_country_id': ", s.property_country_id as property_country_id",
            'property_island_group_id': ", s.property_island_group_id as property_island_group_id",
            'property_province_id': ", s.property_province_id as property_province_id",
            'property_city_id': ", s.property_city_id as property_city_id",
            'property_barangay_id': ", s.property_barangay_id as property_barangay_id",
            'property_state_id': ", s.property_state_id as property_state_id",
            'property_zip': ", s.property_zip as property_zip",
            'property_cluster_id': ", s.property_cluster_id as property_cluster_id",
            'property_cluster2_id': ", s.property_cluster2_id as property_cluster2_id",
            'property_street': ", s.property_street as property_street",
            'property_street2': ", s.property_street2 as property_street2",
        })

        groupby += ', t.is_property, s.managing_director_employee_id, s.marketing_lead_employee_id, s.broker_partner_id, \
                    s.vendor_group_id, s.downpayment_term_id, s.downpayment_percent, s.financing_type_id, s.financing_type_term_id, \
                    s.downpayment_amount, s.dp_discount_amount, s.ntcp_discount_amount, s.net_of_ntcp_discount_amount, s.spot_amount, \
                    s.dp_interest, s.dp_monthly_due, s.turned_over_balance_amount, s.turned_over_balance_percent, s.turned_over_balance_mdue, \
                    s.property_id, s.house_price, s.lot_price, s.miscellaneous_amount, s.reservation_fee, s.ntcp, s.tcp, s.tcp_vat, \
                    s.property_vat, s.spot_dp_invoice_id, s.dp_invoice_id, s.turnover_balance_invoice_id, s.subdivision_id, s.subdivision_phase_id, \
                    s.house_model_id, s.model_type_id, s.floor_area, s.lot_area, s.property_type, s.brand_id, s.model_type_id, s.floor_area, \
                    s.lot_area, s.property_type, s.property_continent_id, s.property_continent_region_id, s.property_country_id, s.property_island_group_id, \
                    s.property_province_id, s.property_city_id, s.property_barangay_id, s.property_state_id, s.property_zip, \
                    s.property_cluster_id, s.property_cluster2_id, s.property_street, s.property_street2'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
