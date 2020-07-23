# -*- coding: utf-8 -*-
import locale
import logging
from datetime import datetime

import pandas as pd
from odoo import fields, models, api, _

_logger = logging.getLogger("_name_")


class CRMLeadStagnantReport(models.Model):
    _name = 'crm.lead.stagnant.report'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    name = fields.Char(string="Title", required=True)
    domain = fields.Char(string='Filter', default='[]', required=True, track_visibility="always")
    team_id = fields.Many2one('crm.team', string="Sales Team", track_visibility="always")
    salesperson_user_id = fields.Many2one('res.users', string="Salesperson", track_visibility="always")
    type = fields.Selection([
        ('lead', 'Leads Only'),
        ('opportunity', 'Opportunities Only'),
        ('all', 'All')
    ], string="Type", track_visibility="always")
    exclude_document_stage_ids = fields.Many2many('crm.stage', 'stagnant_stage_rel', 'stagnant_id', 'stage_id',
                                                  string="Exclude Opportunity Stages", track_visibility="always")
    minimum_stagnant_days = fields.Integer(string="Minimum Days", default=5, track_visibility="always")
    time_unit = fields.Selection([
        ('day', 'Day/s'),
        ('week', 'Week/s'),
        ('month', 'Month/s')
    ], string="Time Unit", required=True, track_visibility="always")
    advance_filter = fields.Boolean(string="Advance Filter", track_visibility="always")
    email_recipient_id = fields.Many2one('res.users', string="Email Recipient", domain="[('share','=',False)]", required=True, track_visibility="always")
    email_cc_recipient_ids = fields.Many2many('res.users', 'stagnant_recipient_rel', 'stagnant_temp_id', 'partner_id',
                                              string="Email CC Recipient/s",
                                              help="Make that all recipients has a valid email address.", domain="[('share','=',False)]", track_visibility="always")
    email_cc = fields.Char(string="Email CC")

    @api.onchange('email_cc_recipient_ids')
    def _onchange_email_cc(self):
        count = len(self.email_cc_recipient_ids.ids)
        if count > 0:
            email = list()
            for i in self.email_cc_recipient_ids:
                if i.email_normalized:
                    email.append(i.email_normalized)
            email_cc = False
            for r in email:
                email_cc = email_cc and f"{email_cc}, {r}" or f"{r}"
            self.email_cc = email_cc.replace(" ", "")

    def generate_stagnant_report(self):
        rec = self.browse([])
        for i in rec:
            i.send_email_report()

    def send_email_report(self):
        template_id = self.env.ref('crm_track_days_last_update.email_crm_lead_stagnant_report').id
        if template_id:
            self.message_post_with_template(template_id)
        return True

    def get_domain_filter(self, stagnant_record):
        domain = stagnant_record.domain
        if not stagnant_record.advance_filter:
            domain = [('team_id', '=', stagnant_record.team_id.id)]
            if stagnant_record.salesperson_user_id:
                domain += [('user_id', '=', stagnant_record.salesperson_user_id.id)]
            if stagnant_record.type == 'lead':
                domain += [('type', '=', 'lead')]
            if stagnant_record.type == 'opportunity':
                domain += [('type', '=', 'opportunity'),
                           ('stage_id', 'not in', stagnant_record.exclude_document_stage_ids.ids)]
        return domain

    def get_stagnant_lead(self):
        crm = self.env['crm.lead']
        for i in self:
            data = []
            domain = i.get_domain_filter(i)
            records = crm.search(domain)
            for lead in records:
                stagnant_days = (datetime.now() - lead.write_date).days
                if stagnant_days >= i.minimum_stagnant_days:
                    days = f"{stagnant_days} Day/s"
                    if i.time_unit == 'week':
                        days = f"{locale.format('%0.2f', stagnant_days / 7.0, grouping=True)} Week/s"
                    if i.time_unit == 'month':
                        days = f"{locale.format('%0.2f', stagnant_days / 30.0, grouping=True)} Month/s"
                    data.append(
                        {
                            'lead': lead,
                            'team': lead.team_id.name,
                            'user_id': lead.user_id.name,
                            'stagnant_days': days
                        }
                    )
            if data:
                df = pd.DataFrame(data).sort_values(by=['team', 'user_id', 'stagnant_days'],
                                                    ascending=[True, True, False])
                data_list = df.values.tolist()
                return data_list
            return data

#
#
#
#
#
#
#
# class CRMLead(models.Model):
#     _inherit = 'crm.lead'
#
#     days_last_update = fields.Integer(string="No. of Days Last Updated", compute="compute_last_date_updated")
#     display_paydays_last_update = fields.Char(string="Display No. of Days Last Updated")
#
#     def compute_last_date_updated(self):
#         for lead in self:
#             lead.days_last_update = (datetime.now() - lead.write_date).days
#             lead.write({'display_paydays_last_update': f"{(datetime.now() - lead.write_date).days}Day/s"})
#
#
#
#
