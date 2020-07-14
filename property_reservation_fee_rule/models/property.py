# -*- coding: utf-8 -*-
import logging
from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger("_name_")


class HousingModel(models.Model):
    _inherit = 'housing.model'

    rfo_reservation_amount = fields.Monetary(string="RFO Reservation")
    nrfo_reservation_amount = fields.Monetary(string="NRFO Reservation")


class PropertySubdivisionPhaseUnitModel(models.Model):
    _inherit = "property.subdivision.phase.unit.model"

    rfo_reservation_amount = fields.Monetary(string="RFO Reservation")
    nrfo_reservation_amount = fields.Monetary(string="NRFO Reservation")


class PropertyDetail(models.Model):
    _inherit = 'property.detail'

    rfo_reservation_amount = fields.Monetary(string="RFO Reservation")
    nrfo_reservation_amount = fields.Monetary(string="NRFO Reservation")
    reservation_fee = fields.Monetary(string="Reservation Fee", compute="_get_reservation_amount", store=True)

    def write(self, vals):
        res = super(PropertyDetail, self).write(vals)
        if self.product_id and (vals.get('rfo_reservation_amount') or vals.get('nrfo_reservation_amount')):
            unit_status = vals.get('unit_state') or self.unit_state
            price = vals.get('nrfo_reservation_amount') or self.nrfo_reservation_amount
            if unit_status == 'completed':
                price = vals.get('rfo_reservation_amount') or self.rfo_reservation_amount
            self.product_id.write({'list_price': price})
        if (self.unit_state or vals.get('unit_state')) and (self.product_id or vals.get('product_id')):
            rules = self.env['property.rsfee.rule'].search([
                ('subdivision_id', '=', vals.get('subdivision_id') or self.subdivision_id.id),
                ('subdivision_phase_id', '=', vals.get('subdivision_phase_id') or self.subdivision_phase_id.id),
                ('house_model_id', '=', vals.get('house_model_id') or self.house_model_id.id)
            ])
            if rules[:1]:
                rules.manual_force_update()
        return res

    @api.model
    def create(self, vals):
        res = super(PropertyDetail,self).create(vals)
        if self.unit_state or vals.get('unit_state') and vals.get('product_id'):
            rules = self.env['property.rsfee.rule'].search([
                ('subdivision_id', '=', vals.get('subdivision_id') or self.subdivision_id.id),
                ('subdivision_phase_id', '=', vals.get('subdivision_phase_id') or self.subdivision_phase_id.id),
                ('house_model_id', '=', vals.get('house_model_id') or self.house_model_id.id)
            ])
            if rules[:1]:
                rules.manual_force_update()
        return res


    'subdivision_id', 'subdivision_phase_id', 'house_model_id'
    @api.depends('rfo_reservation_amount', 'nrfo_reservation_amount', 'unit_state')
    def _get_reservation_amount(self):
        for i in self:
            i.reservation_fee = i.nrfo_reservation_amount
            if i.unit_state == 'completed':
                i.reservation_fee = i.rfo_reservation_amount


class PropertyRSFeeRule(models.Model):
    _name = 'property.rsfee.rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Property Reservation Fee Rule'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")
    domain = fields.Char(string='Filter', default='[]', required=True, track_visibility="always")
    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision", required=True,
                                     track_visibility="always",
                                     domain="[('company_id', '=', company_id)]")
    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase", required=True,
                                           domain="[('subdivision_id', '=', subdivision_id)]")

    property_subdivision_phase_unit_ids = fields.Many2many('housing.model', 'property_house_unit_rule_rel', 'rule_id',
                                                           'unit_id', compute="_get_subdivision_phase_unit")
    house_model_id = fields.Many2one('housing.model', string="Unit/House Model", required=True,
                                     track_visibility="always")
    property_detail_exception_ids = fields.Many2many('property.detail', 'property_rsrule_rels', 'rule_id',
                                                     'property_id', string="Exceptions")
    rfo_reservation_fee_amount = fields.Monetary(string="Set RFO Reservation Fee", required=True, track_visibility="always")
    nrfo_reservation_fee_amount = fields.Monetary(string="Set NRFO Reservation Fee", required=True, track_visibility="always")
    rule_based = fields.Selection([('tcp', 'TCP Value'), ('ntcp', 'NTCP Value')], default='tcp', required=True,
                                  track_visibility="always", string="Price Based On")
    range_start = fields.Monetary(string="Range Start", required=True, track_visibility="always")
    range_end = fields.Monetary(string="Range End", required=True, track_visibility="always")
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")

    # CRON Job definition
    def update_reservation_fee_rule(self):
        current_date = date.today()
        rules = self.search([('date_start', '<=', current_date), ('date_end', '>=', current_date)])
        if rules[:1]:
            rules.update_price()
            rules.revert_price()

    def manual_force_update(self):
        for rec in self:
            if self.date_start <= date.today() >= self.date_end:
                rec.update_price()
                rec.revert_price()

    @api.depends('subdivision_phase_id')
    def _get_subdivision_phase_unit(self):
        for i in self:
            i.property_subdivision_phase_unit_ids = []
            if i.subdivision_phase_id:
                i.property_subdivision_phase_unit_ids = [rec.house_model_id.id for rec in
                                                         i.subdivision_phase_id.unit_model_ids]

    @api.onchange('subdivision_id', 'subdivision_phase_id', 'house_model_id', 'rule_based', 'date_start',
                  'date_end', 'range_end', 'range_start', 'property_detail_exception_ids')
    def _onchange_domain_context(self):
        domain = [('id', 'not in', self.property_detail_exception_ids.ids),
                  ('subdivision_id', '=', self.subdivision_id and self.subdivision_id.id or False),
                  ('subdivision_phase_id', '=', self.subdivision_phase_id and self.subdivision_phase_id.id or False),
                  ('house_model_id', '=', self.house_model_id and self.house_model_id.id or False)]
        if self.rule_based == 'tcp':
            domain += [('tcp', '>=', self.range_start), ('tcp', '<=', self.range_end)]
        else:
            domain += [('ntcp', '>=', self.range_start), ('ntcp', '<=', self.range_end)]
        self.domain = f"{domain}"

    @api.constrains('company_id', 'subdivision_id', 'subdivision_phase_id', 'house_model_id', 'domain', 'date_start',
                    'date_end', 'range_end', 'range_start')
    def _check_overlapping_parameter(self):
        domain = [
            "&", "&", "&", "&", "&",
            ('id', 'not in', [self.id]),
            ('subdivision_id', '=', self.subdivision_id.id),
            ('subdivision_phase_id', '=', self.subdivision_phase_id.id),
            ('house_model_id', '=', self.house_model_id.id),
            "|",
            ("date_start", ">=", self.date_start), ("date_end", ">=", self.date_end),
            "|",
            ("range_start", ">=", self.range_start), ("range_end", "<=", self.range_end)
        ]
        dup = self.search(domain, limit=1)
        if dup[:1]:
            raise ValidationError(_(f'Your rules could either a duplicate or has a data overlapping with {dup.name}.'))

    def update_price(self):
        for rec in self:
            if rec.domain and rec.domain != '[]':
                property = self.env['property.detail'].search(safe_eval(rec.domain))
                if property[:1]:
                    for p in property:
                        if p.product_id:
                            rs_amount = rec.nrfo_reservation_fee_amount
                            if p.unit_state == 'completed':
                                rs_amount = rec.rfo_reservation_fee_amount
                            p.product_id.write({'list_price': rs_amount})

    def revert_price(self):
        for rec in self:
            if rec.domain and rec.domain != '[]':
                property = self.env['property.detail'].search(safe_eval(rec.domain))
                if property[:1]:
                    for p in property:
                        if p.product_id:
                            p.product_id.write({'list_price': p.reservation_fee})

    _sql_constraints = [
        ('price_range_validation',
         "CHECK(range_start <= range_end)",
         "Price Range End should be >= to Price Start."),
        ('date_range_validation',
         "CHECK(date_start <>>= date_end)",
         "Date Range End should be >= to Date Start."),
        ('unique_rule_parameters',
         'unique(company_id, subdivision_id, subdivision_phase_id, house_model_id, date_start, date_end)',
         'The same rules parameter already exist')
    ]
