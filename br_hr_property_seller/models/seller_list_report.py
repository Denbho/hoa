# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo import tools


class PropertySellerList(models.Model):
    _name = 'property.seller.list'
    _description = 'List of Sellers'
    _auto = False

    name = fields.Char(string="Full Name")
    lastname = fields.Char(string="Last Name")
    firstname = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    suffix_name = fields.Char(string="Suffix Name")
    seller_id = fields.Char(string="Seller ID")
    type = fields.Selection([('Broker', 'Broker'),('Sales Manager', 'Sales Manager'), ('Agent', 'Agent')], string="Seller Type")
    active = fields.Boolean()
    company_id = fields.Many2one('res.company', string="Company")
    seller_social_media_ids = fields.Many2many('res.partner.social.media', 'seller_social_media_rel',string="Social Media", compute="_get_social_media")
    vendor_number = fields.Char(string="Vendor Number")
    seller_division = fields.Selection([('luzon', 'Luzon'), ('vismin', 'VisMin')], string="Division")
    broker_partner = fields.Char(string="Realty/Broker Name")
    source_id = fields.Many2one('utm.source', string="Source")
    vendor_group_id = fields.Many2one('property.vendor.group', string="Vendor Group")
    application_date = fields.Date(string="Application Date")
    recruitment_date = fields.Date(string="Recruitment Date")
    onboarding_date = fields.Date(string="Onboarding Date")
    dob = fields.Date(string="Date of Birth")
    remark = fields.Text(string="Remark")
    mobile = fields.Char(string="Mobile")
    phone = fields.Char(string="phone")
    email = fields.Char(string="Email")
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

    def init(self):
        # tools.drop_view_if_exists(self._cr, 'property_seller_list')
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """
                CREATE or REPLACE view property_seller_list as (
                    SELECT
                        row_number() over(ORDER BY seller.seller_id) as id,
                        seller.name as name,
                        seller.firstname as firstname,
                        seller.lastname as lastname,
                        seller.middle_name as middle_name,
                        seller.suffix_name as suffix_name,
                        seller.seller_id as seller_id,
                        seller.company_id as company_id,
                        seller.type as type,
                        seller.vendor_number as vendor_number,
                        seller.seller_division as seller_division,
                        seller.broker_partner as broker_partner,
                        seller.source_id as source_id,
                        seller.vendor_group_id as vendor_group_id,
                        seller.application_date as application_date,
                        seller.recruitment_date as recruitment_date,
                        seller.onboarding_date as onboarding_date,
                        seller.dob as dob,
                        seller.remark as remark,
                        seller.mobile as mobile,
                        seller.phone as phone,
                        seller.email as email,
                        seller.street as street,
                        seller.street2 as street2,
                        seller.zip as zip,
                        seller.barangay_id as barangay_id,
                        seller.city_id as city_id,
                        seller.province_id as province_id,
                        seller.state_id as state_id,
                        seller.island_group_id as island_group_id,
                        seller.country_id as country_id,
                        seller.continent_id as continent_id,
                        seller.continent_region_id as continent_region_id,
                        seller.active as active
                    FROM (
                        SELECT
                            partner.name as name,
                            partner.firstname as firstname,
                            partner.lastname as lastname,
                            partner.middle_name as middle_name,
                            partner.suffix_name as suffix_name,
                            partner.id as seller_id,
                            partner.company_id as company_id,
                            'Broker' as type,
                            partner.vendor_number as vendor_number,
                            partner.seller_division as seller_division,
                            '' as broker_partner,
                            partner.source_id as source_id,
                            partner.vendor_group_id as vendor_group_id,
                            partner.application_date as application_date,
                            partner.recruitment_date as recruitment_date,
                            partner.onboarding_date as onboarding_date,
                            date_of_birth as dob,
                            partner.broker_remark as remark,
                            partner.mobile as mobile,
                            partner.phone as phone,
                            partner.email as email,
                            partner.street as street,
                            partner.street2 as street2,
                            partner.zip as zip,
                            partner.barangay_id as barangay_id,
                            partner.city_id as city_id,
                            partner.province_id as province_id,
                            partner.state_id as state_id,
                            partner.island_group_id as island_group_id,
                            partner.country_id as country_id,
                            partner.continent_id as continent_id,
                            partner.continent_region_id as continent_region_id,
                            partner.active as active
                        FROM res_partner as partner
                        WHERE partner.broker IS true
                        UNION ALL SELECT
                            employee.name as name,
                            employee.firstname as firstname,
                            employee.lastname as lastname,
                            employee.middle_name as middle_name,
                            employee.suffix_name as suffix_name,
                            employee.id as seller_id,
                            employee.company_id as company_id,
                            employee.seller_type as type,
                            empartner.vendor_number as vendor_number,
                            employee.seller_division as seller_division,
                            empbroker.name as broker_partner,
                            employee.source_id as source_id,
                            employee.vendor_group_id as vendor_group_id,
                            employee.application_date as application_date,
                            employee.recruitment_date as recruitment_date,
                            employee.onboarding_date as onboarding_date,
                            employee.birthday as dob,
                            employee.application_remark as remark,
                            employee.mobile_phone as mobile,
                            employee.work_phone as phone,
                            employee.work_email as email,
                            employee.street as street,
                            employee.street2 as street2,
                            employee.zip as zip,
                            employee.barangay_id as barangay_id,
                            employee.city_id as city_id,
                            employee.province_id as province_id,
                            employee.state_id as state_id,
                            employee.island_group_id as island_group_id,
                            employee.country_id as country_id,
                            employee.continent_id as continent_id,
                            employee.continent_region_id as continent_region_id,
                            employee.active as active
                        FROM hr_employee as employee
                        LEFT JOIN res_partner empartner
                        ON employee.address_home_id = empartner.id
                        LEFT JOIN res_partner empbroker
                        ON employee.broker_partner_id = empbroker.id

                        WHERE employee.seller IS true
                    ) seller
                );
            """
        )

    def get_model_name(self, type):
        if type == 'Broker':
            model = 'res.partner'
        else:
            model = 'hr.employee'
        return self.env[model]

    # @api.depends('type', 'seller_id')
    # def _get_seller_mass_data(self):
    #     for seller in self:
    #         model = seller.get_model_name(seller.type)
    #         record = model.browse(seller.seller_id)
    # #         seller.street = record.street
    # #         seller.street2 = record.street2
    # #         seller.zip = record.zip
    # #         seller.barangay_id = record.barangay_id and record.barangay_id.id or False
    # #         seller.city_id = record.city_id and record.city_id.id or False
    # #         seller.province_id = record.province_id and record.province_id.id or False
    # #         seller.state_id = record.state_id and record.state_id.id or False
    # #         seller.island_group_id = record.island_group_id and record.island_group_id.id or False
    # #         seller.country_id = record.country_id and record.country_id.id or False
    # #         seller.continent_region_id = record.continent_id and record.continent_id.id and False
    # #         seller.continent_id = record.continent_id and record.continent_id.id
    # #         seller.seller_division = record.seller_division
    # #         seller.vendor_group_id = record.vendor_group_id and record.vendor_group_id.id or False
    # #         seller.application_date = record.application_date
    # #         seller.recruitment_date = record.recruitment_date
    # #         seller.onboarding_date = record.onboarding_date
    # #         seller.source_id = record.source_id and record.source_id.id or False
    # #         seller.broker_partner_id = False
    # #         seller.dob = False
    #         if not seller.type in ['Broker']:
    # #             seller.broker_partner_id = record.broker_partner_id and record.broker_partner_id.id or False
    # #             seller.remark = record.application_remark
    # #             seller.email = record.work_email
    # #             seller.mobile = record.mobile_phone
    # #             seller.phone = record.work_phone
    # #             seller.dob = record.birthday
    #             seller.vendor_number = record.address_home_id and record.address_home_id.vendor_number or False
    #         else:
    # #             seller.remark = record.broker_remark
    # #             seller.email = record.email
    # #             seller.phone = record.phone
    # #             seller.mobile = record.mobile
    #             seller.vendor_number = record.vendor_number

    @api.depends('type', 'seller_id')
    def _get_social_media(self):
        for i in self:
            model = i.get_model_name(i.type)
            record = model.browse(i.seller_id)
            i.seller_social_media_ids = record.social_media_ids.ids

    def action_open_seller_profile(self):
        """Display the linked sellers View."""
        self.ensure_one()
        if self.type == 'Broker':
            action = self.env.ref('property_crm.res_partner_action_form').read()[0]
            form_view = [(self.env.ref('base.view_partner_form').id, 'form')]
        else:
            action = self.env.ref('hr.open_view_employee_list_my').read()[0]
            form_view = [(self.env.ref('hr.view_employee_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.seller_id
        action['context'] = dict(self._context, create=False)
        return action








