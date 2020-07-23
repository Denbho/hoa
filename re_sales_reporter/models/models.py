# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class re_sales_reporter(models.Model):
    _name = 're_sales_reporter.re_sales_reporter'
    _description = 're_sales_reporter.re_sales_reporter'

    name = fields.Char(string="Sales Order Number", required=True)
    rs_year = fields.Char(string="RS Year")
    rs_month = fields.Char(string="RS Month")
    rs_summary_date = fields.Date(string="RS Summary Date", required=False)
    so_order_type = fields.Char(string="SO Order Type")
    customer_name = fields.Char(string="Customer Name")
    type_of_sale = fields.Char(string="Type of Sale")
    rs_date = fields.Date(string="RS Date")
    cts_date = fields.Date(string="CTS Date")
    creation_date = fields.Date(string="Creation Date")
    cancel_date = fields.Date(string="Cancel Date")
    dp_percentage = fields.Float(string="DP %", widget="percentage")
    dp_terms = fields.Integer(string="DP Terms")
    full_dp_sched = fields.Date(string="Full DP Sched")
    tcp = fields.Float(string="TCP")
    ntcp = fields.Float(string="NTCP")
    vat = fields.Float(string="VAT")
    mcc = fields.Float(string="MCC")
    ntcp_in_m = fields.Float(string="NTCP in M")
    dp_amt = fields.Float(string="DP Amt")
    la_amt = fields.Float(string="LA Amt")
    dp_paid = fields.Float(string="DP Paid")
    dp_paid_percentage = fields.Float(string="DP Paid %", widget="percentage")
    cr_balance = fields.Float(string="CR Balance")
    project = fields.Char(string="Project")
    project_name = fields.Char(string="Project Name")
    block_lot = fields.Char(string="Block/Lot")
    unit_type = fields.Char(string="Unit Type")
    houseunit_status = fields.Char(string="House/Unit Status")
    house_model = fields.Char(string="House Model")
    bldg_status = fields.Char(string="Bldg Status")
    sales_status = fields.Char(string="Sales Status")
    rs_fee_or = fields.Char(string="RS Fee OR")
    res_fee = fields.Float(string="Res Fee")
    reference_so_no = fields.Char(string="Reference SO No")
    reference_so_date = fields.Date(string="Reference SO Date")
    reference_so_cancel_date = fields.Date(string="Reference SO Cancel Date")
    employment_type = fields.Char(string="Employment Type")
    broker_group = fields.Char(string="Broker Group")
    broker = fields.Char(string="Broker")
    managing_director = fields.Char(string="Managing Director")
    realty_name = fields.Char(string="Realty Name")
    sales_manager = fields.Char(string="Sales Manager")
    property_consultant = fields.Char(string="Property Consultant")
    industry = fields.Char(string="Industry")
    employment_country = fields.Char(string="Employment Country")
    country = fields.Char(string="Country")
    media = fields.Char(string="Media")
    financing_type = fields.Char(string="Financing Type")
    age_bracket = fields.Char(string="Age Bracket")
    marital_status = fields.Char(string="Marital Status")
    gender = fields.Char(string="Gender")
    monthly_income_range = fields.Char(string="Monthly Income Range")
    profession = fields.Char(string="Profession")
    brand = fields.Char(string="Brand")
    brand_group = fields.Char(string="Brand Group")
    division_group = fields.Char(string="Division Group")
    sub_division = fields.Char(string="Sub-Division")
    count = fields.Integer(string="Count")
    month_name = fields.Char(string="Month Name")
    island_group = fields.Char(string="Island Group")
    regional_cluster = fields.Char(string="Regional Cluster")
    region_cluster2 = fields.Char(string="Region Cluster 2")
    region = fields.Char(string="Region")
    province = fields.Char(string="Province")
    area = fields.Char(string="Area")
    project_name = fields.Char(string="Project Name")
    type_of_development = fields.Char(string="Type Of Development")
    rs_by_class = fields.Char(string="RS by Class")
    rs_by_house_model_class = fields.Char(string="RS by House Model Class")
    rs_per_vendor_group = fields.Char(string="RS Per Vendor Group")
    rs_by_employment_countryregion = fields.Char(string="RS by Employment Country/Region")
    lot_area = fields.Float(string="Lot Area")
    floor_area = fields.Float(string="Floor Area")
    lot_price = fields.Float(string="Lot Price")
    house_price = fields.Float(string="House Price")
    legal_entity = fields.Char(string="Legal Entity")
    company_code = fields.Char(string="Company Code")
    company_name = fields.Char(string="Company Name")
    profiling_class = fields.Char(string="Profiling Class")
    tcp_in_m = fields.Float(string="TCP in M")
    marketing_tl = fields.Char(string="Marketing TL")
    cluster_head = fields.Char(string="Cluster Head")
    qtr = fields.Char(string="QTR")
    zip_code = fields.Char(string="Zip Code")
    zip_area = fields.Char(string="Zip Area")
    continental_area = fields.Char(string="Continental Area Per Employment")

    ntcp_average = fields.Float(string="NTCP AVG", group_operator='avg', compute='get_ntcp_average', store=True)
    ntcp_in_m_average = fields.Float(string="NTCP in M AVG", group_operator='avg', compute='get_ntcp_in_m_average', store=True)
    tcp_average = fields.Float(string="TCP AVG", group_operator='avg', compute='get_tcp_average', store=True)
    lot_price_average = fields.Float(string="Lot Price AVG", group_operator='avg', compute='get_lot_price_average', store=True)
    house_price_average = fields.Float(string="House Price AVG", group_operator='avg', compute='get_house_price_average', store=True)
    effective_rs_date = fields.Date(string="Effective RS Date", compute='get_effective_rs_date', store=True)

    # Copy NTCP Value and Make the Group Value as Average Instead of the Default Sum
    @api.depends('ntcp')
    @api.onchange('ntcp')
    def get_ntcp_average(self):
        for record in self:
            record['ntcp_average'] = record['ntcp']

    # Copy NTCP in M Value and Make the Group Value as Average Instead of the Default Sum
    @api.depends('ntcp_in_m')
    @api.onchange('ntcp_in_m')
    def get_ntcp_in_m_average(self):
        for record in self:
            record['ntcp_in_m_average'] = record['ntcp_in_m']

    # Copy TCP Value and Make the Group Value as Average Instead of the Default Sum
    @api.depends('tcp')
    @api.onchange('tcp')
    def get_tcp_average(self):
        for record in self:
            record['tcp_average'] = record['tcp']

    # Copy Lot Price Value and Make the Group Value as Average Instead of the Default Sum
    @api.depends('lot_price')
    @api.onchange('lot_price')
    def get_lot_price_average(self):
        for record in self:
            record['lot_price_average'] = record['lot_price']

    # Copy House Value and Make the Group Value as Average Instead of the Default Sum
    @api.depends('house_price')
    @api.onchange('house_price')
    def get_house_price_average(self):
        for record in self:
            record['house_price_average'] = record['house_price']

    # Get The Effective RS Date From rs_summary_date or rs_month + 28 + rs_year
    @api.depends('rs_summary_date')
    @api.onchange('rs_summary_date')
    def get_effective_rs_date(self):
        for record in self:

            if record['rs_summary_date']:
                temp_effective_rs_date = datetime.datetime.strptime(str(record['rs_summary_date']), "%Y-%m-%d")
                if (str(temp_effective_rs_date.year) == str(record['rs_year']) and str(
                        temp_effective_rs_date.month) == str(record['rs_month'])):
                    record['effective_rs_date'] = record['rs_summary_date']
                else:
                    record['effective_rs_date'] = str(record['rs_year']) + '-' + str(record['rs_month']) + '-28'
            else:
                record['effective_rs_date'] = str(record['rs_year']) + '-' + str(record['rs_month']) + '-28'
