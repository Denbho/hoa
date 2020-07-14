# -*- coding: utf-8 -*-
import logging

from odoo import models, api, fields

_logger = logging.getLogger("_name_")


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    lead_name = fields.Boolean(string="Lead/Opportunity", default=True)
    contact_name = fields.Boolean(string="Contact Name", default=True)
    salesteam = fields.Boolean(string="Salesteam", default=True)
    salesperson = fields.Boolean(string="Salesperson", default=True)
    subdivision = fields.Boolean(string="Subdivision", default=True)
    subdivision_project = fields.Boolean(string="Project", default=True)
    unit_model = fields.Boolean(string="Unit Model", default=True)

    @api.model
    def default_get(self, fields):
        """ Default get for name, opportunity_ids.
            If there is an exisitng partner link to the lead, find all existing
            opportunities links with this partner to merge all information together
        """
        result = super(Lead2OpportunityPartner, self).default_get(fields)
        if self._context.get('active_id'):
            tomerge = {int(self._context['active_id'])}

            partner_id = result.get('partner_id')
            lead = self.env['crm.lead'].browse(self._context['active_id'])
            email = lead.partner_id.email if lead.partner_id else lead.email_from

            tomerge.update(self.with_context({
                'lead_name': lead.name,
                'team_id': lead.team_id.id,
                'user_id': lead.user_id.id,
                'contact_name': lead.contact_name,
                'subdivision_id': lead.subdivision_id and lead.subdivision_id.id or False,
                'subdivision_phase_id': lead.subdivision_phase_id and lead.subdivision_phase_id.id or False,
                'house_model_id': lead.house_model_id and lead.house_model_id.id or False
            })._get_duplicated_leads(partner_id, email, include_lost=True).ids)

            if 'action' in fields and not result.get('action'):
                result['action'] = 'exist' if partner_id else 'create'
            if 'partner_id' in fields:
                result['partner_id'] = partner_id
            if 'name' in fields:
                result['name'] = 'merge' if len(tomerge) >= 2 else 'convert'
            if 'opportunity_ids' in fields and len(tomerge) >= 2:
                result['opportunity_ids'] = list(tomerge)
            if lead.user_id:
                result['user_id'] = lead.user_id.id
            if lead.team_id:
                result['team_id'] = lead.team_id.id
            if not partner_id and not lead.contact_name:
                result['action'] = 'nothing'
        return result


class Lead2OpportunityMassConvert(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner.mass'

    @api.onchange('deduplicate', 'lead_name', 'salesteam', 'salesperson', 'contact_name', 'contact_name', 'subdivision',
                  'subdivision_project', 'unit_model')
    def _onchange_deduplicate(self):
        active_leads = self.env['crm.lead'].browse(self._context.get('active_ids'))
        partner_ids = [(lead.partner_id.id, lead.partner_id and lead.partner_id.email or lead.email_from, lead) for lead
                       in
                       active_leads]
        partners_duplicated_leads = {}
        for partner_id, email, lead in partner_ids:
            duplicated_leads = self.with_context({
                'lead_name': self.lead_name and lead.name or False,
                'team_id': self.salesteam and lead.team_id and lead.team_id.id or False,
                'user_id': self.salesperson and lead.user_id and lead.user_id.id or False,
                'contact_name': self.contact_name and lead.contact_name or False,
                'subdivision_id': self.subdivision and lead.subdivision_id and lead.subdivision_id.id or False,
                'subdivision_phase_id': self.subdivision_project and lead.subdivision_phase_id and lead.subdivision_phase_id.id or False,
                'house_model_id': self.unit_model and lead.house_model_id and lead.house_model_id.id or False
            })._get_duplicated_leads(partner_id, email)
            if len(duplicated_leads) > 1:
                partners_duplicated_leads.setdefault((partner_id, email), []).extend(duplicated_leads)
        leads_with_duplicates = []
        for lead in active_leads:
            lead_tuple = (lead.partner_id.id, lead.partner_id.email if lead.partner_id else lead.email_from)
            if len(partners_duplicated_leads.get(lead_tuple, [])) > 1:
                leads_with_duplicates.append(lead.id)

        self.opportunity_ids = self.env['crm.lead'].browse(leads_with_duplicates)

    def mass_convert(self):
        self.ensure_one()
        if self.name == 'convert' and self.deduplicate:
            merged_lead_ids = set()
            remaining_lead_ids = set()
            lead_selected = self._context.get('active_ids', [])
            for lead_id in lead_selected:
                if lead_id not in merged_lead_ids:
                    lead = self.env['crm.lead'].browse(lead_id)
                    duplicated_leads = self.with_context({
                        'lead_name': self.lead_name and lead.name or False,
                        'team_id': self.salesteam and lead.team_id and lead.team_id.id or False,
                        'user_id': self.salesperson and lead.user_id and lead.user_id.id or False,
                        'contact_name': self.contact_name and lead.contact_name or False,
                        'subdivision_id': self.subdivision and lead.subdivision_id and lead.subdivision_id.id or False,
                        'subdivision_phase_id': self.subdivision_project and lead.subdivision_phase_id and lead.subdivision_phase_id.id or False,
                        'house_model_id': self.unit_model and lead.house_model_id and lead.house_model_id.id or False
                    })._get_duplicated_leads(lead.partner_id.id,
                                             lead.partner_id.email if lead.partner_id else lead.email_from)
                    if len(duplicated_leads) > 1:
                        lead = duplicated_leads.merge_opportunity()
                        merged_lead_ids.update(duplicated_leads.ids)
                        remaining_lead_ids.add(lead.id)
            active_ids = set(self._context.get('active_ids', {}))
            active_ids = (active_ids - merged_lead_ids) | remaining_lead_ids

            self = self.with_context(active_ids=list(active_ids))  # only update active_ids when there are set
        no_force_assignation = self._context.get('no_force_assignation', not self.force_assignation)
        return self.with_context(no_force_assignation=no_force_assignation).action_apply()
