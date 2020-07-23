# -*- coding: utf-8 -*-
import logging

from odoo import models, api
from odoo.tools import email_split

_logger = logging.getLogger("_name_")


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _get_duplicated_leads_by_emails(self, partner_id, email, include_lost=False):
        _logger.info(f"\n\n\nContext Value: {self._context}\n\n\n")
        """ Search for opportunities that have the same partner and that arent done or cancelled """
        if not email:
            return self.env['crm.lead']
        partner_match_domain = []
        for email in set(email_split(email) + [email]):
            partner_match_domain.append(('email_from', '=ilike', email))
        if partner_id:
            partner_match_domain.append(('partner_id', '=', partner_id))
        partner_match_domain = ['|'] * (len(partner_match_domain) - 1) + partner_match_domain
        if not partner_match_domain:
            return self.env['crm.lead']
        domain = partner_match_domain

        if 'lead' in self._context and self._context.get('lead'):
            domain += [('name', '=', self._context.get('lead_name'))]
        if 'team_id' in self._context and self._context.get('team_id'):
            domain += [('team_id', '=', self._context.get('team_id'))]
        if 'user_id' in self._context and self._context.get('user_id'):
            domain += [('user_id', '=', self._context.get('user_id'))]
        if 'contact_name' in self._context and self._context.get('contact_name'):
            domain += [('contact_name', '=', self._context.get('contact_name'))]
        if 'subdivision_id' in self._context and self._context.get('subdivision_id'):
            domain += [('subdivision_id', '=', self._context.get('subdivision_id'))]
        if 'subdivision_phase_id' in self._context and self._context.get('subdivision_phase_id'):
            domain += [('subdivision_phase_id', '=', self._context.get('subdivision_phase_id'))]
        if 'subdivision_project' in self._context and self._context.get('subdivision_project'):
            domain += [('house_model_id', '=', self._context.get('house_model_id'))]
        if not include_lost:
            domain += ['&', ('active', '=', True), ('probability', '<', 100)]
        else:
            domain += ['|', '&', ('type', '=', 'lead'), ('active', '=', True), ('type', '=', 'opportunity')]

        return self.search(domain)
