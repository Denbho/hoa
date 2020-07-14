from datetime import date, datetime

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class CRMStage(models.Model):
    _inherit = 'crm.stage'

    minimum_expected_revenue = fields.Float(string="Minimum Expected Revenue")
    minimum_probability_rate = fields.Float(string="Minimum Probability Rate")

    _sql_constraints = [
        ('check_minimumprobability', 'check(minimum_probability_rate >= 0 and minimum_probability_rate <= 100)',
         'The Minimum Probability Rate the deal should be between 0% and 100%!'),
        ('check_minimumrevenue', 'check(minimum_expected_revenue >= 0)',
         'The Minimum Expected Revenue must be greater than or equal!'),
    ]


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    inquiry_date = fields.Date(string="Inquiry Date", default=fields.Date.context_today, track_visibility="always")
    closing_note = fields.Text(string="Closing Note", track_visibility="always")

    def write(self, vals):
        context_data = {
            'date_closed': self._context.get('closing_date'),
            'closing_note': self._context.get('closing_note')
        }
        res = super(CRMLead, self).write(vals)
        if self._context.get('closing_date') and self._context.get('closing_note'):
            self.with_context({
                'date_closed': False,
                'closing_note': False
            }).write(context_data)
        return res

    @api.constrains('stage_id', 'probability', 'planned_revenue')
    def _validate_revenue_and_probability(self):
        if self.stage_id:
            stage = self.stage_id
            if self.probability < stage.minimum_probability_rate:
                raise ValidationError(_(f"Probability must be greater than or equal {stage.minimum_probability_rate}"))
            if self.planned_revenue < stage.minimum_expected_revenue:
                raise ValidationError(_(
                    f"Minimum Planned/Expected Revenue must be greater than or equal {stage.minimum_expected_revenue}"))

    @api.constrains('inquiry_date', 'date_closed')
    def _validate_inquiry_date_and_date_closed(self):
        if self.inquiry_date and self.inquiry_date > date.today():
            raise ValidationError(_('Inquiry Date must be not greater today!'))
        if self.date_closed and self.date_closed > datetime.now():
            raise ValidationError(_('Inquiry Date must be not greater today!'))
