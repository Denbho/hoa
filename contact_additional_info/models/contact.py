# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
import locale
import logging


_logger = logging.getLogger("_name_")

class UTMSource(models.Model):
    _inherit = 'utm.source'

    active = fields.Boolean('Active', default=True)

    
class ResPartnerEducationAttainment(models.Model):
    _name = "res.partner.educational.attainment"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")


class ResPartnerReligion(models.Model):
    _name = "res.partner.religion"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")


class ResPartnerHouseType(models.Model):
    _name = "res.partner.house.type"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")


class ResPartnerBuyerRelationship(models.Model):
    _name = 'res.partner.buyer.relationship'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")


class ResPartnerEmploymentStatus(models.Model):
    _name = 'res.partner.employment.status'

    name = fields.Char(string="Name", required=True)
    parent_id = fields.Many2one('res.partner.employment.status', string="Parent")
    description = fields.Text(string="Description")

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(ResPartnerEmploymentStatus, self).name_get()

class SocialMediaType(models.Model):
    _name = 'social.media.type'

    name = fields.Char(string="Contact Info")
    description = fields.Text(string="Description")


class ResPartnerSocialMedia(models.Model):
    _name = 'res.partner.social.media'

    name = fields.Char(string="Contact Info")
    description = fields.Text(string="Description")
    media_type_id = fields.Many2one('social.media.type', string="Type")
    partner_id = fields.Many2one('res.partner', string="Contact Name")
    lead_id = fields.Many2one('crm.lead', string="Lead")


class ResPartnerBusiness(models.Model):
    _name = 'res.partner.business'

    name = fields.Char(string="Name", required=True, help="Business Name")
    street = fields.Char(string="No. Inc, Bldg Name, Street")
    street2 = fields.Char(string="Subdivision")
    name = fields.Char(string="Name", required=True, help="Business Name")
    city = fields.Char(string="City")
    region = fields.Char(string="Region")
    zip = fields.Char(string="Zip Code")
    continent_id = fields.Many2one('res.continent', string="Continent")
    continent_region_id = fields.Many2one('res.continent.region')
    country_id = fields.Many2one('res.country', string="Country")
    island_group_id = fields.Many2one('res.island.group', string="Island Group")
    state_id = fields.Many2one('res.country.state', string="Region/States")
    province_id = fields.Many2one('res.country.province', string="Province")
    city_id = fields.Many2one('res.country.city', string="City")
    barangay_id = fields.Many2one('res.barangay', string="Barangay")
    industry_id = fields.Many2one('res.partner.industry', string="Industry", required=True)
    business_type = fields.Selection([
                    ('proprietor', 'Single Proprietorship'),
                    ('partnership', 'Partnership'),
                    ('corporation', 'Corporation'),
                    ('cooperative', 'Cooperative')
                ], string="Business/Company Type", required=True)
    establishment_date = fields.Date(string="Date of Business Establishment", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")

    @api.onchange('barangay_id')
    def onchange_barangay(self):
        if self.barangay_id:
            data = self.barangay_id
            self.city_id = data.city_id and data.city_id.id
            self.zip = data.zip_code
            self.city = f"{data.name}, {data.city_id.name}"
            self.region =  f"{data.province_id.name}, {data.state_id.name}"

    @api.onchange('city_id')
    def onchange_city(self):
        if self.city_id:
            data = self.city_id
            self.province_id = data.province_id and data.province_id.id
            # self.city = f"{data.name}"

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


class ResPartnerLoan(models.Model):
    _name = 'res.partner.loan'

    name = fields.Char(string="Name of Institution", required=True)
    type_of_loan = fields.Char(string="Type of Loan", required=True)
    date_paid = fields.Date(string="Date Granted/Paid", required=True)
    maturity_date = fields.Date(string="Maturity Date")
    monthly_amortization = fields.Float(string="Monthly Amortization")
    partner_id = fields.Many2one('res.partner', string="Partner")


class ResPartnerCreditCardIssuer(models.Model):
    _name = 'res.partner.credit.card.issuer'

    name = fields.Char(string="Card Issuer", required=True)
    card_holder_name = fields.Char(string="Name of Card")
    partner_id = fields.Many2one('res.partner', string="Partner")


class ResPartnerPersonalReferences(models.Model):
    _name = 'res.partner.personal.references'

    reference_partner_id = fields.Char(string="reference Name")
    name = fields.Char(string="Name", required=True)
    buyer_relationship_id = fields.Many2one("res.partner.buyer.relationship", string="Relationship with Buyer")
    buyer_relationship = fields.Char(string="Relationship with Buyer")
    contact_number = fields.Char(string="Contact Number")
    address = fields.Text(string="Residence Address")
    other = fields.Char(string="Other Info")
    partner_id = fields.Many2one('res.partner', string="Partner")


# class ResPartnerRegion(models.Model):
#     _name = 'res.partner.region'
#
#     name = fields.Char(string="Name", required=True)
#     description = fields.Text(string="Description")


class ResPartnerPropertyPurpose(models.Model):
    _name = 'res.partner.property.purpose'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")


class ResPartnerMonthlyIncomeRange(models.Model):
    _name = 'res.partner.monthly.income.range'

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


class ResPartnerAgeRange(models.Model):
    _name = 'res.partner.age.range'

    range_from = fields.Float(string="From", required=True)
    range_to = fields.Float(string="To", required=True)
    name = fields.Char(string="Display Range", store=True, compute="_get_range_name")

    @api.depends('range_from', 'range_to')
    def _get_range_name(self):
        for i in self:
            if i.range_from and i.range_to:
                i.name = f"{int(i.range_from)} - {int(i.range_to)}"
    @api.constrains('range_from', 'range_to')
    def _check_range(self):
        if self.range_from >= self.range_to:
            raise ValidationError(_('"Range To" must greate than "Range From" value.'))


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.onchange("firstname", "lastname")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for rec in self:
            rec.name = rec.partner_id._get_computed_name(rec.lastname, rec.firstname, middle_name=False, suffix_name=False)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    # _inherit = ['portal.mixin', 'res.partner']
    _sql_constraints = [('partner_assign_number', 'unique(partner_assign_number)', 'The "Contact Number" field  must have unique value!')]

    @api.depends('salary_income', 'other_income')
    def get_total_income(self):
        for i in self:
            total_income = sum([i.salary_income, i.other_income])
            i.total_income = total_income
            income_range = self.env['res.partner.monthly.income.range'].search([('range_from', '<=', total_income), ('range_to', '>=', total_income)], limit=1)
            i.monthly_income_range_id = income_range[:1] and income_range.id or False

    middle_name = fields.Char(string="Middle Name", tracking=True)
    mother_maiden_name = fields.Char(string="Mother's Maiden Name", tracking=True)
    nick_name = fields.Char(string="Nick Name (AKA)", tracking=True)
    suffix_name = fields.Char(string="Suffix Name", tracking=True)
    partner_assign_number = fields.Char(string="Contact Number", tracking=True, help="A Unique Identifier number")
    gender = fields.Selection([
                ('male', 'Male'),
                ('female', 'Female'),
                ('other', 'Other')
            ], string="Gender", default="male", tracking=True)
    marital = fields.Selection([
            ('single', 'Single'),
            ('married', 'Married'),
            ('cohabitant', 'Legal Cohabitant'),
            ('widower', 'Widower'),
            ('divorced', 'Divorced'),
            ('separated', 'Separated'),
            ('annulled', 'Annulled')
        ], string='Marital Status',  default='single', tracking=True)
    years_on_address = fields.Integer(string="Years at Present Address")
    home_number = fields.Char(string="Home Phone Number")
    educational_attaiment_id = fields.Many2one('res.partner.educational.attainment', string="Highest Educational Attainment")
    religion_id = fields.Many2one('res.partner.religion', string="Religion")
    nationality_country_id = fields.Many2one('res.country', string="Nationality")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age")
    age_range_id = fields.Many2one('res.partner.age.range', string="Age Range")
    house_type_id = fields.Many2one('res.partner.house.type', string="Type of House")
    number_of_dependencies = fields.Integer(string="No. of Dependents")
    buyer_relationship_id = fields.Many2one("res.partner.buyer.relationship", string="Relationship with Buyer")
    employment_status_id = fields.Many2one('res.partner.employment.status', string="Employment Status")
    business_ids = fields.One2many('res.partner.business', 'partner_id', string="Business Information")
    salary_income = fields.Float(string="Salary/Income from Business(for SE)", help="Monthly")
    other_income = fields.Float(string="Allowances, Commissions and Other Income", help="Monthly")
    total_income = fields.Float(string="Total Monthly Income", compute="get_total_income", store=True)
    monthly_income_range_id = fields.Many2one('res.partner.monthly.income.range', string="Monthly Income Range", compute="get_total_income", store=True)
    spouse_partner_id = fields.Many2one('res.partner', string="Spause's Name")
    co_borrower_partner_id = fields.Many2one('res.partner', string="Co-borrower's Name")
    co_borrower_relationship_id = fields.Many2one("res.partner.buyer.relationship", help="Relationship with Buyer")
    attorney_partner_id = fields.Many2one('res.partner', string="Attorney-In-Fact Name")
    attorney_borrower_relationship_id = fields.Many2one("res.partner.buyer.relationship", help="Relationship with Buyer")
    total_spause_income = fields.Float(string="Total Spause's Income")
    total_coborrower_income = fields.Float(string="Total Co-borrower's Income")
    loan_history_ids = fields.One2many('res.partner.loan', 'partner_id', string="History of Loan")
    credit_card_ids = fields.One2many('res.partner.credit.card.issuer', 'partner_id', string="Credit Cards")
    personal_reference_ids = fields.One2many('res.partner.personal.references', 'partner_id', string="Personal References")
    property_purpose_id = fields.Many2one("res.partner.property.purpose", string="This property is for...")
    ad_source_ids = fields.Many2many('utm.source', 'partner_utm_source_rel', 'partner_id', 'utm_source_id', string="Where did you get to know about the property?",
                                     help="Where did you get to know about the property? Check all possible answers.")
    social_media_ids = fields.One2many('res.partner.social.media', 'partner_id', string="Social Media")

    emp_company_name = fields.Char(string="Employer Company Name", help="Company Name")
    emp_continent_id = fields.Many2one('res.continent', string="Employer Continent")
    emp_continent_region_id = fields.Many2one('res.continent.region', string="Employer Continent Region")
    emp_country_id = fields.Many2one('res.country', string="Employer Country")
    emp_island_group_id = fields.Many2one('res.island.group', string="Employer Island Group")
    emp_province_id = fields.Many2one('res.country.province', string="Employer Province")
    emp_city_id = fields.Many2one('res.country.city', string="Employer City")
    emp_state_id = fields.Many2one('res.country.state', string="Employer Region/States")
    emp_industry_id = fields.Many2one('res.partner.industry', string="Employer Industry")
    employment_date = fields.Date(string="Date Employed")
    emp_city = fields.Char(string="Employer City")
    emp_region = fields.Char(string="Employer Region")
    emp_zip = fields.Char(string="Employer Zip")
    emp_street = fields.Char(string="Employer Street")
    emp_street2 = fields.Char(string="Employer Street2")
    emp_contract_status = fields.Selection([
                            ('regular', 'Regular'),
                            ('contractual', 'Constractual'),
                            ('project_based', 'Project Based')
                        ], string="Contract Status")
    emp_position_level = fields.Selection([
                        ('rank_file', 'Rank and File/Staff/Clerk'),
                        ('supervisor', 'Supervisor/Team Lead'),
                        ('manager', 'Manager/Director'),
                        ('executive', 'Executive Officer'),
                        ('professional', 'Professional (Doctor/Lawyer/Engineer/Architect)')
                    ], string="Position/Level")

    @api.onchange('emp_city_id')
    def onchange_emp_city(self):
        if self.emp_city_id:
            data = self.emp_city_id
            self.emp_city = data.name
            self.emp_region = f"{data.province_id.name}, {data.state_id.name}"
            self.emp_province_id = data.province_id and data.province_id.id

    @api.onchange('emp_province_id')
    def onchange_emp_province(self):
        if self.emp_province_id:
            data = self.emp_province_id
            self.emp_state_id = data.state_id and data.state_id.id

    @api.onchange('emp_state_id')
    def onchange_emp_state(self):
        if self.emp_state_id:
            data = self.emp_state_id
            self.emp_island_group_id = data.island_group_id and data.island_group_id.id

    @api.onchange('emp_island_group_id')
    def onchange_emp_island_group(self):
        if self.emp_island_group_id:
            data = self.emp_island_group_id
            self.emp_country_id = data.country_id.id

    @api.onchange('emp_country_id')
    def onchange_emp_country(self):
        if self.emp_country_id:
            data = self.emp_country_id
            self.emp_continent_region_id = data.continent_region_id and data.continent_region_id.id

    @api.onchange('emp_continent_region_id')
    def onchange_emp_ontinent_region_id(self):
        if self.emp_continent_region_id:
            data = self.emp_continent_region_id
            self.emp_continent_id = data.continent_id and data.continent_id.id

    @api.onchange('date_of_birth')
    def onchange_dob(self):
        if self.date_of_birth:
            age = date.today().year - self.date_of_birth.year
            self.age = age
            age_range = self.env['res.partner.age.range'].search([('range_from', '<=', age), ('range_to', '>=', age)], limit=1)
            # _logger.info(f'\n\nAge: {age}\tRange: {age_range.id}\n\n\n')
            self.age_range_id = age_range[:1] and age_range.id or False

    @api.model
    def _get_computed_name(self, lastname, firstname, middle_name, suffix_name):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        order = self._get_names_order()
        if order == "last_first_comma":
            if middle_name:
                firstname = " ".join(p for p in (firstname, middle_name) if p)
            if suffix_name:
                 firstname = " ".join(p for p in (firstname, suffix_name) if p)
            return ", ".join(p for p in (lastname, firstname) if p)
        else:# order == "first_last":
            return " ".join(p for p in (firstname, middle_name, lastname, suffix_name) if p)
        # else:
        #     return " ".join(p for p in (lastname, firstname) if p)

    @api.depends("firstname", "lastname", "middle_name", "suffix_name")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            record.name = record._get_computed_name(record.lastname, record.firstname, record.middle_name, record.suffix_name)

    # def _compute_access_url(self):
    #     super(ResPartner, self)._compute_access_url()
    #     for Partner in self:
    #         Partner.access_url = '/my/account%s' % (Partner.id)
    #
    # def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
    #     self.ensure_one()
    #     auth_param = url_encode(self.signup_get_auth_param()[self.id])
    #     return self.get_portal_url(query_string='&%s' % auth_param)
    #     return super(ResPartner, self)._get_share_url(redirect, signup_partner, pid)
    #
    # def preview_contact(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'target': 'self',
    #         'url': self.get_portal_url(),
    #     }
