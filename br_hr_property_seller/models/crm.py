from odoo import fields, models, api

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    agent_hr_employee_id = fields.Many2one('hr.employee', domain="[('seller', '=', True)]", string="Agent (Seller)")
    sales_manager_hr_employee_id = fields.Many2one('hr.employee', domain="[('seller', '=', True)]", string="Sales Manager (Seller)")

    @api.onchange('agent_hr_employee_id', 'sales_manager_hr_employee_id')
    def _onchange_agent(self):
        if self.agent_hr_employee_id:
            self.broker_partner_id = self.agent_hr_employee_id and self.agent_hr_employee_id.broker_partner_id.id or False
        if not self.broker_partner_id and self.sales_manager_hr_employee_id:
            self.broker_partner_id = self.sales_manager_hr_employee_id.broker_partner_id and self.sales_manager_hr_employee_id.broker_partner_id.id or False





