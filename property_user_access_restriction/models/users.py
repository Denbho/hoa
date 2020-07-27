from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    subdivision_ids = fields.Many2many('property.subdivision', string="Subdivision")
    


