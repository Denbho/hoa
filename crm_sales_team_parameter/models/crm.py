# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError

class Lead(models.Model):
    _inherit = "crm.lead"

    @api.depends('user_id')
    def _get_team_options(self):
        for i in self:
            domain = [('team_id.use_leads', '=', True)] if i._context.get('default_type') == "lead" or i.type == 'lead' else [('team_id.use_opportunities', '=', True)]
            user_id = i.user_id.id
            if not i.user_id:
                user_id = i.env.user.id
            i.team_select_ids = [rec.team_id.id for rec in i.env['team.user'].sudo().search([('user_id', '=', user_id)] + domain)]

    team_select_ids = fields.Many2many('crm.team', 'crm_lead_team_rel', 'lead_id', 'team_id', string="Team Options",
                                       compute='_get_team_options')
    team_id = fields.Many2one('crm.team', string='Sales Team', default=lambda self: self._default_team_id(self.env.uid),
                              index=True, tracking=True,
                              help='When sending mails, the default email address is taken from the Sales Team.')
    date_conversion = fields.Datetime('Conversion Date', default=fields.Datetime.now, readonly=False,copy=False)
    stage_name = fields.Char(string="Stage Name", related='stage_id.name', store=True)
    date_closed = fields.Datetime('Closed Date', readonly=False, copy=False)

    @api.constrains('team_id', 'user_id')
    def _validate_team(self):
        if self.user_id and self.team_id:
            domain = [('team_id.use_leads', '=', True)] if self._context.get(
                'default_type') == "lead" or self.type == 'lead' else [('team_id.use_opportunities', '=', True)]
            user_id = self.user_id.id
            if not self.team_id.id in [rec.team_id.id for rec in self.env['team.user'].sudo().search([('user_id', '=', user_id)] + domain)]:
                raise UserError(_(f'Salesperson "{self.user_id.name}" does not belong to "{self.team_id.name}" team.'))