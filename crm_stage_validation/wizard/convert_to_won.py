from odoo import fields, models, api


class LeadConvertWon(models.TransientModel):
    _name = 'lead.convert.won'
    _description = 'Converting Lead to Won Stage'

    closing_date = fields.Datetime('Closing Date')
    closing_note = fields.Text(string="Notes")

    def close_opportunity(self):
        lead = self.env['crm.lead'].browse(self._context.get('active_id'))
        return lead.with_context({
            'closing_date': self.closing_date,
            'closing_note': self.closing_note
        }).action_set_won_rainbowman()

    


