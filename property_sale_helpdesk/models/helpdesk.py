# -*- coding: utf-8 -*-
from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    property_id = fields.Many2one('property.detail', string="Property", domain="[('partner_id', '=', partner_id)]")


class PropertyDetail(models.Model):
    _inherit = "property.detail"

    ticket_count = fields.Integer("Tickets", compute='_compute_ticket_count')

    def _compute_ticket_count(self):
        for i in self:
            i.ticket_count = len([r.id for r in i.env['helpdesk.ticket'].search([('property_id', '=', i.id)])])

    def action_open_helpdesk_ticket(self):
        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree').read()[0]
        action['context'] = {}
        action['domain'] = [('property_id', '=', self.id)]
        return action
