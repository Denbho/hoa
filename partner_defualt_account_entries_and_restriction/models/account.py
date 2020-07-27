# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger("_name_")


class ResPartnerAccountTypeGL(models.Model):
    _name = 'partner.account.gl.type'
    _description = 'Partner Default GL Account'
    # check_company_auto = True


    # company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company, check_company=True)
    name = fields.Char(string="Title", required=True)
    sequence_id = fields.Many2one("ir.sequence", string="ID Sequence Paramater")
    ar_ap_type = fields.Selection([('Receivable', 'AR GL'), ('Payable', 'AP GL')], string="General Ledger Account Type",
                                  help="AR GL - Account Receivable General Ledger; AP GL - Account Payable General Ledger")
    account_id = fields.Many2one('account.account', string="Default Account", required=True)
    other_account_ids = fields.Many2many('account.account', 'partner_gltype_rel', 'gltype_id', 'account_id',
                                         string="Other Related GL Account Allowed")
    account_ids = fields.Many2many('account.account', 'partner_accountgltype_rel', 'gltype_id', 'account_id',
                                   string="Valid Account", compute="_get_account")

    @api.depends('ar_ap_type')
    def _get_account(self):
        for i in self:
            if i.ar_ap_type:
                i.account_ids = self.env['account.account'].search([('user_type_id.name', '=', i.ar_ap_type)]).ids

    def write(self, vals):
        if vals.get('account_id'):
            if self.ar_ap_type == 'Payable':
                partner = self.env['res.partner'].search([('vendor_account_gltype_id', '=', self.id)])
                for i in partner:
                    i.write({
                        'property_account_payable_id': vals.get('account_id')
                    })
            else:
                partner = self.env['res.partner'].search([('customer_account_gltype_id', '=', self.id)])
                for i in partner:
                    i.write({
                        'property_account_receivable_id': vals.get('account_id')
                    })
        return super(ResPartnerAccountTypeGL, self).write(vals)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    processing_date = fields.Date(string='Processing Date', default=fields.Date.context_today, required=True, readonly=True,
                               states={'draft': [('readonly', False)]}, copy=False, tracking=True)
    payment_date = fields.Date(string='Accounting Date')


class AccountMove(models.Model):
    _inherit = "account.move"

    journal_group_ids = fields.Many2many('account.journal.group', 'move_journal_groups_rel', string="Journal Groups",
                                         compute='_get_journal_groups')
    journal_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
    ], related="journal_id.type", string="Journal Type",
        help="Select 'Sale' for customer invoices journals.\n" \
             "Select 'Purchase' for vendor bills journals.\n" \
             "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n" \
             "Select 'General' for miscellaneous operations journals.")

    @api.depends('journal_id')
    def _get_journal_groups(self):
        for move in self:
            move.journal_group_ids = []
            if move.journal_id and move.journal_id:
                move.journal_group_ids = move.journal_id.journal_group_ids.ids or []

    @api.constrains('ref', 'type', 'company_id')
    def _validate_unique_reference(self):
        for move in self:
            if move.ref:
                rec = move.sudo().search([('id', 'not in', [move.id]), ('company_id', '=', move.company_id.id), ('type', '=', move.type), ('ref', '=', move.ref)])
                if rec[:1]:
                    raise ValidationError(_('The Reference of the Invoice document must be unique per company and type!'))
    # _sql_constraints = [
    #     ('reference_numbers_invoice_uniq', 'unique(ref, type, company_id)', 'The Reference of the Invoice document must be unique per company and type!')
    # ]


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    partner_allowed_account_ids = fields.Many2many('account.account', 'moveline_partner_account', 'aml_id',
                                                   'account_id', string="Allowed Account",
                                                   compute="_get_allowed_account")

    def _validate_partner_account(self):
        domain = list()
        accounts = list()
        if self.partner_id.vendor_account_gltype_id:
            accounts.append(self.partner_id.vendor_account_gltype_id.account_id.id)
            accounts += self.partner_id.vendor_account_gltype_id.other_account_ids.ids
        if self.partner_id.customer_account_gltype_id:
            accounts.append(self.partner_id.customer_account_gltype_id.account_id.id)
            accounts += self.partner_id.customer_account_gltype_id.other_account_ids.ids
        domain = [('user_type_id.name', 'in', ['Payable', 'Receivable']), ('id', 'not in', accounts)]
        return self.env['account.account'].search(domain)

    @api.depends('journal_id', 'partner_id')
    def _get_allowed_account(self):
        for i in self:
            excluded_accounts = list()
            if (i.partner_id and (
                    i.partner_id.vendor_account_gltype_id or i.partner_id.customer_account_gltype_id)) and (
                    i.journal_id and i.journal_id.type in ['sale', 'purchase']):
                excluded_accounts = self._validate_partner_account()
            allowed_accounts = self.env['account.account'].search([('id', 'not in', excluded_accounts[:1] and excluded_accounts.ids or [])])
            i.partner_allowed_account_ids = allowed_accounts[:1] and allowed_accounts.ids or []

    @api.constrains('journal_id', 'partner_id', 'account_id')
    def _validate_ar_and_ap_account(self):
        for line in self:
            if (line.partner_id and (
                    line.partner_id.vendor_account_gltype_id or line.partner_id.customer_account_gltype_id)) and (
                    line.journal_id and line.journal_id.type in ['sale', 'purchase']):
                excluded_accounts = line._validate_partner_account()
                if excluded_accounts[:1] and line.account_id.id in excluded_accounts.ids:
                    raise ValidationError(_(f'The Partner selected has no access to {line.account_id.name}.'))


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_account_gltype_id = fields.Many2one('partner.account.gl.type', string="AP Group",
                                               domain="[('ar_ap_type', '=', 'Payable')]",
                                               context="{'default_ar_ap_type': 'Payable'}")
    vendor_number = fields.Char(string="Vendor Number")
    customer_account_gltype_id = fields.Many2one('partner.account.gl.type', string="AR Group",
                                                 domain="[('ar_ap_type', '=', 'Receivable')]",
                                                 context="{'default_ar_ap_type': 'Receivable'}")
    customer_number = fields.Char(string="Customer Number")

    @api.onchange('vendor_account_gltype_id')
    def _onchange_vendor_account_gltyp(self):
        if self.vendor_account_gltype_id and self.vendor_account_gltype_id.account_id:
            self.property_account_payable_id = self.vendor_account_gltype_id.account_id.id

    @api.onchange('customer_account_gltype_id')
    def _onchange_customer_account_gltype_id(self):
        if self.customer_account_gltype_id and self.customer_account_gltype_id.account_id:
            self.property_account_receivable_id = self.customer_account_gltype_id.account_id.id

    @api.model
    def create(self, vals):
        if vals.get('vendor_account_gltype_id') and not vals.get('vendor_number'):
            vendor = self.env['partner.account.gl.type'].browse(vals.get('vendor_account_gltype_id'))
            vals['vendor_number'] = self.env['ir.sequence'].get(vendor.sequence_id.code)
        if vals.get('customer_account_gltype_id') and not vals.get('customer_number'):
            customer = self.env['partner.account.gl.type'].browse(vals.get('vendor_account_gltype_id'))
            vals['customer_number'] = self.env['ir.sequence'].get(customer.sequence_id.code)
        return super(ResPartner, self).create(vals)

    def generate_partner_number(self):
        for partner in self:
            # if self._context.get('gltype'):
            if self._context.get('gltype') == 'vendor':
                partner.write({'vendor_number': self.env['ir.sequence'].get(
                    partner.vendor_account_gltype_id.sequence_id.code)})
            else:
                partner.write({'customer_number': self.env['ir.sequence'].get(
                    partner.customer_account_gltype_id.sequence_id.code)})
