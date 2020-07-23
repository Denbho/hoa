import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger("_name_")

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def action_open_journal_reconciliation(self):
        self.ensure_one()
        _logger.info('\n\n\nI am Called\n\n\n')
        action = self.env.ref('account_reports.action_account_report_bank_reconciliation_with_journal').read()[0]
        return action

# class AccountCommonReport(models.TransientModel):
#     _inherit = "account.common.report"
#     _check_company_auto = True
#
#     journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
#                                    default=list(), check_company=True)
#
#     # def check_report(self):
#     #     res = super(AccountCommonReport, self).check_report()
#     #     _logger.info(f"\n\nReport Data:\n{res}\n\n")
#     #     return res


class AccountPettyCash(models.Model):
    _name = 'account.petty.cash'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Petty Cash Management'
    _check_company_auto = True

    name = fields.Char(string="Name", required=True, track_visibility="always")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company, track_visibility="always")
    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")
    journal_id = fields.Many2one('account.journal', string="Journal", required=True, track_visibility="always", check_company=True)
    user_id = fields.Many2one('res.users', string="Custodian", required=True, track_visibility="always")

    total_fund_transfer = fields.Monetary(string="Accumulative Funds", compute="_get_total_journal_transaction")
    total_transaction = fields.Monetary(string="Accumulative Transactions", compute="_get_total_journal_transaction")
    balance_amount = fields.Monetary(string="Balance", help="Remaining Funds", compute="_get_total_journal_transaction")
    balance_threshold_amount = fields.Monetary(string="Threshold Balance")
    threshold_limit = fields.Boolean(compute="_get_total_journal_transaction")
    threshold_notify_user_ids = fields.Many2many('res.users', 'petty_users_notif_rel', string="Notify Users",
                                                 help="The selected users will get a notification when the balance is lower or equal to Thershold Balance.")

    def _get_total_journal_transaction(self):
        for i in self:
            payment = self.env['account.payment']
            i.threshold_limit = False
            if i.journal_id:
                fund_transfers = sum(payment.sudo().search(
                    [('destination_journal_id', '=', i.journal_id.id), ('state', 'in', ['posted', 'reconciled'])]).mapped('amount'))
                transactions = sum(payment.sudo().search(
                    [('journal_id', '=', i.journal_id.id), ('state', 'in', ['posted', 'reconciled'])]).mapped('amount'))
                balance = fund_transfers - transactions
                i.total_fund_transfer = fund_transfers
                i.total_transaction = transactions
                i.balance_amount = balance
                if balance <= i.balance_threshold_amount:
                    i.threshold_limit = True

    def open_journal_reconciliation(self):
        self.ensure_one()
        action = self.env.ref('account_petty_cash.action_account_report_petty_cash_reconciliation_with_journal').read()[0]
        action['context'] = {
            'active_ids': self.journal_id.ids,
            'active_id': self.journal_id.id,
            'model': 'account.bank.reconciliation.report'
        }
        return action

    # def open_journal_audit(self):
    #     return {
    #         'name': _('Petty Cash Journal Audit'),
    #         'res_model': 'account.common.report',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('account_petty_cash.petty_cash_journal_audit_view_form').id,
    #         'context': {
    #             'journal_ids': self.journal_id.ids
    #         },
    #         'target': 'new',
    #         'type': 'ir.actions.act_window',
    #     }

    def action_open_fund_transfers(self):
        self.ensure_one()
        transfers = self.env['account.payment'].search(
            [('destination_journal_id', '=', self.journal_id.id), ('state', 'in', ['posted', 'reconciled'])])
        action = self.env.ref('account_petty_cash.account_payment_transaction_action').read()[0]
        if len(transfers) > 1:
            action['domain'] = [('id', 'in', transfers.ids)]
        elif len(transfers) == 1:
            form_view = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = transfers.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = dict(self._context, create=False)
        return action

    def action_open_transactions(self):
        self.ensure_one()
        transactions = self.env['account.payment'].search(
            [('journal_id', '=', self.journal_id.id), ('state', 'in', ['posted', 'reconciled'])])
        action = self.env.ref('account_petty_cash.account_payment_transaction_action').read()[0]
        if len(transactions) > 1:
            action['domain'] = [('id', 'in', transactions.ids)]
        elif len(transactions) == 1:
            form_view = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = transactions[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = dict(self._context, create=False)
        return action