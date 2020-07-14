# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger("_name_")


class AccountFollowupReport(models.AbstractModel):
    _inherit = 'account.followup.report'

    def _get_lines(self, options, line_id=None):
        res = super(AccountFollowupReport, self)._get_lines(options, line_id)
        for i in res:
            if i.get('columns')[3].get('name') and not i.get('columns')[3].get('name') in ['Total Due',
                                                                                           'Total Overdue']:
                if i.get('account_move'):
                    property = i.get('account_move').property_subscription()
                    if property:
                        i.get('columns')[3]['name'] = f"{i.get('columns')[3].get('name')}" \
                                                      f": {property}"
        return res


class SaleSubscriptionTemplate(models.Model):
    _inherit = 'sale.subscription.template'

    subdivision_id = fields.Many2one('property.subdivision', string="Subdivision", track_visibility="always")
    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase/Project",
                                           track_visibility="always")

    def check_and_create_analytic(self, data):
        for res in data:
            analytic_group = self.env['account.analytic.group']
            analytic_account = self.env['account.analytic.account']
            sub_analytic_group = analytic_group.search(
                [('name', '=', res.subdivision_id.name), ('company_id', 'in', [self.env.company.id])])

            if not sub_analytic_group[:1]:
                sub_analytic_group = analytic_group.create({
                    'name': res.subdivision_id.name,
                    'description': f"HOA: {res.subdivision_id.name}",
                    'company_id': self.env.company.id,
                })
                sub_phase_analytic_group = analytic_group.create({
                    'name': res.subdivision_phase_id.name,
                    'description': f"HOA: {res.subdivision_phase_id.name}",
                    'parent_id': sub_analytic_group.id,
                    'company_id': self.env.company.id,
                })
                sub_div_analytic = analytic_account.create({
                    'name': res.subdivision_id.name,
                    'group_id': sub_analytic_group.id,
                    'company_id': self.env.company.id,
                })
                sub_phase_div_analytic = analytic_account.create({
                    'name': res.subdivision_phase_id.name,
                    'group_id': sub_phase_analytic_group.id,
                    'company_id': self.env.company.id,
                })
            elif sub_analytic_group[:1]:
                sub_div_analytic = analytic_account.search(
                    [('name', '=', res.subdivision_id.name),
                     ('group_id', '=', sub_analytic_group[:1].id),
                     ('company_id', 'in', [self.env.company.id, False])])
                if not sub_div_analytic[:1]:
                    sub_div_analytic = analytic_account.create({
                        'name': res.subdivision_id.name,
                        'group_id': sub_analytic_group[:1].id,
                        'company_id': self.env.company.id,
                    })
                sub_phase_analytic_group = analytic_group.search(
                    [('name', '=', res.subdivision_phase_id.name),
                     ('parent_id', '=', sub_analytic_group[:1].id),
                     ('company_id', 'in', [self.env.company.id, False])])
                if not sub_phase_analytic_group[:1]:
                    sub_phase_analytic_group = analytic_group.create({
                        'name': res.subdivision_phase_id.name,
                        'description': f"HOA: {res.subdivision_phase_id.name}",
                        'parent_id': sub_analytic_group[:1].id,
                        'company_id': self.env.company.id,
                    })
                    sub_phase_div_analytic = analytic_account.create({
                        'name': res.subdivision_phase_id.name,
                        'group_id': sub_phase_analytic_group.id,
                        'company_id': self.env.company.id,
                    })
                else:
                    sub_phase_div_analytic = analytic_account.search(
                        [('name', '=', res.subdivision_phase_id.name),
                         ('group_id', '=', sub_phase_analytic_group.id),
                         ('company_id', 'in', [self.env.company.id, False])])
                    if not sub_phase_div_analytic[:1]:
                        sub_phase_div_analytic = analytic_account.create({
                            'name': res.subdivision_phase_id.name,
                            'group_id': sub_phase_analytic_group.id,
                            'company_id': self.env.company.id,
                        })
        return {
            'sub_analytic_group': sub_analytic_group[:1].id,
            'sub_phase_analytic_group': sub_phase_analytic_group.id,
            'sub_div_analytic': sub_div_analytic.id,
            'sub_phase_div_analytic': sub_phase_div_analytic.id
        }

    @api.model
    def create(self, vals):
        res = super(SaleSubscriptionTemplate, self).create(vals)
        self.check_and_create_analytic(res)
        return res


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    def is_property_subscription(self):
        with_property = False
        for line in self.recurring_invoice_line_ids:
            if line.hoa_subscription:
                with_property = True
                break
        return with_property

    def _prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        res = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position, date_start, date_stop)
        if line.hoa_subscription:
            res['hoa_subscription'] = line.hoa_subscription
            res['hoa_property_id'] = line.hoa_property_id.id
        return res


class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"

    hoa_property_id = fields.Many2one('property.detail', string="Property/Unit", track_visibility="always")
    hoa_subscription = fields.Boolean(string="HOA Subscription")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account',
        copy=False, check_company=True,  # Unrequired company
        states={'done': [('readonly', True)]}, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="The analytic account related to a sales order.")

    @api.constrains('order_line', 'order_line.hoa_subscription', 'order_line.hoa_property_id')
    def _check_hoa_subscription(self):
        for line in self.order_line:
            if line.hoa_subscription and not line.hoa_property_id:
                raise ValidationError(_('Please the property name on the order line.'))

    def check_exist_running_subscription(self, orderline):
        subscription = self.env['sale.subscription.line']
        for line in orderline:
            data = subscription.search(
                [('product_id', '=', line.product_id.id),
                 ('hoa_subscription', '=', True),
                 ('hoa_property_id', '=', line.hoa_property_id.id),
                 ('analytic_account_id.stage_id.in_progress', '=', True)]
            )
            if data[:1]:
                raise ValidationError(_(f"{line.name} of {line.hoa_property_id.name} property,"
                                        f" has an Existing Active Subscription/Tenant, Please close those first in order to proceed."))

    def _action_confirm(self):
        for line in self.order_line:
            if (line.hoa_subscription or line.require_proprty_tag) and line.hoa_property_id:
                self.check_exist_running_subscription(line)
                analytic = line.product_id.subscription_template_id.check_and_create_analytic(
                    line.product_id.subscription_template_id)
                property_analytic = self.env['account.analytic.account'].search(
                    [('name', '=', line.hoa_property_id.name),
                     ('group_id', '=', analytic.get('sub_phase_analytic_group')),
                     ('company_id', 'in', [self.env.company.id, False])])
                if not property_analytic[:1]:
                    property_analytic = self.env['account.analytic.account'].create({
                        'name': line.hoa_property_id.name,
                        'group_id': analytic.get('sub_phase_analytic_group'),
                        'company_id': self.env.company.id,
                    })
                self.write({
                    'analytic_account_id': property_analytic.id
                })
        res = super(SaleOrder, self)._action_confirm()
        return res

    def is_property_subscription(self):
        with_property = False
        for line in self.order_line:
            if line.hoa_subscription:
                with_property = True
                break
        return with_property


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    require_proprty_tag = fields.Boolean(string="Require Tagging of Property",
                                         help="Upon entering the Orderline details requires to tag the Property related to sales.")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def _is_hoa_subscription(self):
        for i in self:
            if i.product_id and i.product_id.subscription_template_id and i.product_id.subscription_template_id.subdivision_id:
                i.hoa_subscription = True
                i.subdivision_phase_id = i.product_id.subscription_template_id.subdivision_phase_id.id

    hoa_subscription = fields.Boolean(string="HOA Subscription", store=True, compute="_is_hoa_subscription", inverse="_inverse_is_hoa_subscription")
    require_proprty_tag = fields.Boolean(string="Require Tagging of Property",
                                         help="Upon entering the Orderline details requires to tag the Property related to sales.",
                                         related="product_id.require_proprty_tag", store=True)

    subdivision_phase_id = fields.Many2one('property.subdivision.phase', string="Phase/Project", store=True,
                                           compute="_is_hoa_subscription", inverse="_inverse_is_hoa_subscription")
    hoa_property_id = fields.Many2one('property.detail', string="Property/Unit (HOA)", track_visibility="always",
                                      domain="[('subdivision_phase_id', '=', subdivision_phase_id)]", copy=False)

    def _inverse_is_hoa_subscription(self):
        for i in self:
            if i.product_id and not i.product_id.subscription_template_id or i.product_id and not i.product_id.subscription_template_id.subdivision_id:
                continue

    def _prepare_subscription_line_data(self):
        res = super(SaleOrderLine, self)._prepare_subscription_line_data()
        for line in self:
            if line.hoa_property_id:
                res[0][2]['hoa_property_id'] = line.hoa_property_id.id
                res[0][2]['hoa_subscription'] = True
                res[0][2]['price_unit'] = line.product_id.lst_price

        return res

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.subscription_id and self.hoa_subscription:
            res['hoa_property_id'] = self.hoa_property_id.id
            res['hoa_subscription'] = True
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    hoa_property_id = fields.Many2one('property.detail', string="Property/Unit", track_visibility="always")
    hoa_subscription = fields.Boolean(string="HOA Subscription")


class AccountMove(models.Model):
    _inherit = 'account.move'

    def property_subscription(self):
        property = False
        for line in self.invoice_line_ids:
            if line.hoa_subscription:
                property = line.hoa_property_id.name
        return property
