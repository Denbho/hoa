from odoo import fields, models, api
from datetime import datetime, date


class HREmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'utm.mixin']

    application_id = fields.Many2one('hr.applicant', string="Application/Recruitement Source")
    application_remark = fields.Text(string="Remarks")
    application_date = fields.Date(string="Application Date")
    recruitment_date = fields.Date(string="Recruitment Date")
    onboarding_date = fields.Date(string="Onboarding Date")

class Applicant(models.Model):
    _inherit = "hr.applicant"

    def create_employee_from_applicant(self):
        res = super(Applicant, self).create_employee_from_applicant()
        employee = self.env['hr.employee'].browse(res.get('res_id'))
        employee.write({
            'application_id': self.id,
            'application_remark': self.description,
            'application_date': datetime.strftime(self.create_date, "%Y-%m-%d"),
            'recruitment_date': date.today(),
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
        })
        return











    


