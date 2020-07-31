# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo import tools


class TenantSubscriptionsReport(models.Model):
    _name = 'tenant.subscription.report'
    _description = 'Tenant Subscription Due Reports'
    _auto = False

    company_id = fields.Many2one('res.company', string='Company', index=True)
    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")
    partner_id = fields.Many2one('res.partner', string="Tenant")
    subscription_id = fields.Many2one('sale.subscription', string="Subscription")
    move_id = fields.Many2one('account.move', string="Invoice")
    invoice_payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid')],
        string='Payment')
    invoice_date = fields.Date(string='Invoice/Bill Date')
    invoice_date_due = fields.Date(string='Due Date')
    move_line_id = fields.Many2one('account.move.line', string="Invoice Line")
    price_subtotal = fields.Monetary(string='Subtotal', store=True, related="move_line_id.price_subtotal")
    price_total = fields.Monetary(string='Total', store=True, related="move_line_id.price_total")
    property_id = fields.Many2one('property.detail', string="Property")
    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision")
    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase")
    house_model_id = fields.Many2one('housing.model', string="Unit/House Model")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """
                CREATE or REPLACE view tenant_subscription_report as (
                    SELECT
                        aml.id as id,
                        aml.company_id as company_id,
                        am.partner_id as partner_id,
                        aml.subscription_id as subscription_id,
                        am.id as move_id,
                        aml.id as move_line_id,
                        aml.hoa_property_id as property_id,
                        am.invoice_payment_state as invoice_payment_state,
                        am.invoice_date as invoice_date,
                        am.invoice_date_due as invoice_date_due,
                        aml.price_subtotal as price_subtotal,
                        aml.price_total as price_total,
                        pd.subdivision_id as subdivision_id,
                        pd.subdivision_phase_id as subdivision_phase_id,
                        pd.house_model_id as house_model_id
                    FROM account_move_line as aml
                    LEFT JOIN account_move am
                        ON aml.move_id = am.id
                    LEFT JOIN property_detail pd
                        ON aml.hoa_property_id = pd.id
                    WHERE 
                        aml.hoa_property_id IS NOT NULL and am.state='posted'
                );
            """
        )

    def action_open_tenant_profile(self):
        self.ensure_one()
        action = self.env.ref('property_tenant_dues.res_partner_action_form').read()[0]
        form_view = [(self.env.ref('base.view_partner_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = self.partner_id.id
        action['context'] = dict(self._context, create=False, delete=False)
        return action

    def action_open_tenant_subscription(self):
        self.ensure_one()
        action = self.env.ref('sale_subscription.sale_subscription_action').read()[0]
        form_view = [(self.env.ref('sale_subscription.sale_subscription_view_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = self.subscription_id.id
        action['context'] = dict(self._context, create=False, delete=False, edit=False)
        return action

    def action_open_property_detail(self):
        self.ensure_one()
        action = self.env.ref('property_base.property_detail_action_form').read()[0]
        form_view = [(self.env.ref('property_base.property_detail_view_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = self.property_id.id
        action['context'] = dict(self._context, create=False, delete=False, edit=False)
        return action

    def action_open_invoice_detail(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = self.move_id.id
        action['context'] = dict(self._context, create=False, delete=False, edit=False)
        return action


