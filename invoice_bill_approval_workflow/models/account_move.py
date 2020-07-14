# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    approve_by = fields.Many2one(
        'res.users', string='Approve By', readonly=True, attachment=True)
    state = fields.Selection(selection_add=[('approve', 'To Approve')])

    def action_post_ip(self):
        ammount = self.filtered(lambda inv: inv.state != 'open')
        if self.company_id.invoice_bill_approval or self.company_id.customer_vendor_credit_approval:
            ctx = {}
            action = self.env.ref('account.view_invoice_tree').id
            if self.type == 'out_invoice':
                ammount = self.company_id.invoice_ammount
                ctx['type'] = 'Invoice'
            elif self.type == 'in_invoice':
                ammount = self.company_id.bill_ammount
                ctx['type'] = 'Bill'
                action = self.env.ref('account.action_move_in_invoice_type').id
            elif self.type == 'out_refund':
                ammount = self.company_id.customer_credit_note_ammount_ammount
                ctx['type'] = 'Customer Credit Note'
                action = self.env.ref('account.action_move_out_refund_type').id
            elif self.type == 'in_refund':
                ammount = self.company_id.vendor_credit_note_ammount
                ctx['type'] = 'Vendor Credit Note'
                action = self.env.ref('account.action_move_in_refund_type').id

            if self.amount_total < float(ammount):
                self.action_post()
            else:
                email_list = [user.email for user in self.env['res.users'].sudo().search(
                    [('company_ids', 'in', self.company_id.ids)]) if user.has_group('account.group_account_manager')]
                if email_list:
                    ctx['partner_manager_email'] = ','.join([email for email in email_list if email])
                    ctx['email_from'] = self.env.user.email
                    ctx['partner_name'] = self.env.user.name
                    ctx['customer_name'] = self.partner_id.name
                    ctx['amount_total'] = self.amount_total
                    ctx['lang'] = self.env.user.lang
                    template = self.env.ref(
                        'invoice_bill_approval_workflow.invoice_bill_validate_email_template_ip')
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    ctx['action_url'] = "{}/web?db={}#id={}&action={}&view_type=form&model=account.invoice".format(
                        base_url, self.env.cr.dbname, self.id, action)
                    template.with_context(ctx).sudo().send_mail(
                        self.id, force_send=True, raise_exception=False)
                self.write({'state': 'approve'})
        else:
            self.action_post()

    def action_invoice_approve(self):
        self.write({'state': 'draft'})
        self.approve_by = self.env.user.id
        self.action_post()
