from odoo import fields, models, api

class ResPartnerSocialMedia(models.Model):
    _inherit = 'res.partner.social.media'

    employee_id = fields.Many2many('hr.employee', string="Employee")

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    social_media_ids = fields.One2many('res.partner.social.media', 'partner_id', string="Social Media")
    


