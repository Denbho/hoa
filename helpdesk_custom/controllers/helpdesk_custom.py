from odoo import fields, models, api


class TicketSourceTicketSouce(models.Model):
    _name = 'ticketsource.ticketsource'

    name = fields.Char('Name')
    description = fields.Text('Description')
    ticketsource_ids = fields.One2many('helpdesk.ticket', 'ticketsource_id', 'Ticket Source')


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    ticketsource_id = fields.Many2one('ticketsource.ticketsource', 'Ticket Source')