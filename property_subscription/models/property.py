from odoo import fields, models, api


class PropertyDetail(models.Model):
    _inherit = 'property.detail'

    tenant_partner_id = fields.Many2one('res.partner', string="Current Tenant", compute='_get_tenant_details', store=True)
    subscription_id = fields.Many2one('sale.subscription', string="Subscription Details", compute='_get_tenant_details', store=True)
    subscription_line_id = fields.One2many('sale.subscription.line', 'hoa_property_id', string="Tenant Subscriptions")
    subscription_count = fields.Integer(compute='_compute_subscription_count')

    def action_open_subscriptions(self):
        """Display the linked subscription and adapt the view to the number of records to display."""
        self.ensure_one()
        subscriptions = self.env['sale.subscription.line'].search(
            [('hoa_subscription', '=', True),
             ('hoa_property_id', '=', self.id)])
        action = self.env.ref('sale_subscription.sale_subscription_action').read()[0]
        if len(subscriptions) > 1:
            action['domain'] = [('id', 'in', subscriptions.ids)]
        elif len(subscriptions) == 1:
            form_view = [(self.env.ref('sale_subscription.sale_subscription_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = subscriptions.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = dict(self._context, create=False)
        return action

    def _compute_subscription_count(self):
        for i in self:
            subscription = self.env['sale.subscription.line'].search(
                [('hoa_subscription', '=', True),
                 ('hoa_property_id', '=', i.id)])
            i.subscription_count = subscription[:1] and len(subscription.ids) or 0

    @api.depends('subscription_line_id', 'subscription_line_id.analytic_account_id.stage_id', 'subscription_line_id.analytic_account_id.stage_id.in_progress')
    def _get_tenant_details(self):
        for i in self:
            i.tenant_partner_id = False
            i.subscription_id = False
            subscription = self.env['sale.subscription.line'].search(
                [('hoa_subscription', '=', True),
                 ('hoa_property_id', '=', i.id),
                 ('analytic_account_id.stage_id.in_progress', '=', True)])
            if subscription[:1]:
                i.tenant_partner_id = subscription[:1].analytic_account_id.partner_id.id
                i.subscription_id = subscription[:1].analytic_account_id.id



