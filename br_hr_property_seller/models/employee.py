from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    application_date = fields.Date(string="Application Date")
    recruitment_date = fields.Date(string="Recruitment Date")
    onboarding_date = fields.Date(string="Onboarding Date")
    broker_remark = fields.Text(string="Remark")
    source_id = fields.Many2one('utm.source', string="Source")
    seller_division = fields.Selection([('luzon', 'Luzon'), ('vismin', 'VisMin')], string="Division")
    seller_type = fields.Selection([('Sales Manager', 'Sales Manager'), ('Agent', 'Agent')], string="Seller Type")

class HREmplyee(models.Model):
    _inherit = 'hr.employee'

    seller = fields.Boolean(string="Seller")
    seller_type = fields.Selection([('Sales Manager', 'Sales Manager'), ('Agent', 'Agent')], string="Seller Type")
    seller_division = fields.Selection([('luzon', 'Luzon'), ('vismin', 'VisMin')], string="Division")
    broker_partner_id = fields.Many2one('res.partner', string="Realty/Broker Name", domain="[('broker', '=', True)]")
    vendor_group_id = fields.Many2one('property.vendor.group', string="Vendor Group")
    vendor_number = fields.Char(string="Vendor No.", store=True, compute="_get_partner_number",
                                 inverse="_inverse_partner_number")
    tin = fields.Char(string="TIN", store=True, compute="_get_partner_number", inverse="_inverse_partner_number")

    @api.depends('address_home_id', 'address_home_id.vat', 'address_home_id.vendor_number')
    def _get_partner_number(self):
        for i in self:
            if i.address_home_id:
                if i.address_home_id.vat:
                    i.tin = i.address_home_id.vat
                if i.address_home_id.vendor_number:
                    i.vendor_number = i.address_home_id.vendor_number

    def _inverse_partner_number(self):
        for i in self:
            if not i.address_home_id:
                continue
            if i.address_home_id and not i.address_home_id.vendor_number:
                continue
            if i.address_home_id and not i.address_home_id.vat:
                continue

    @api.model
    def create(self, vals):
        res = super(HREmplyee, self).create(vals)
        if not res.address_home_id:
            new_partner_id = self.env['res.partner'].create({
                'is_company': False,
                'name': res.name,
                'firstname': res.firstname,
                'lastname': res.lastname,
                'middle_name': res.middle_name,
                'nick_name': res.nick_name,
                'suffix_name': res.suffix_name,
                'email': res.work_email,
                'phone': res.work_phone,
                'mobile': res.mobile_phone,
                'recruitment_date': res.recruitment_date,
                'application_date': res.application_date,
                'onboarding_date': res.onboarding_date,
                'seller_division': res.seller_division,
                'seller_type': res.seller_type,
                'vendor_group_id': res.vendor_group_id and res.vendor_group_id.id or False,
                'source_id': res.source_id and res.source_id.id or False,
                'broker_remark': res.application_remark,
                'vendor_number': res.vendor_number,
                'vat': res.tin
            })
            address_id = new_partner_id.address_get(['contact'])['contact']
            res.write({'address_home_id': address_id})
        return res


