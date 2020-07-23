import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger("_name_")


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.model
    def _default_user_id(self):
        custodian = self.env['account.petty.cash'].sudo().search(
            [('user_id', '=', self.env.user.id), ('company_id', '=', self.env.company.id)])
        if custodian[:1]:
            return self._uid
        return False

    @api.model
    def default_get(self, fields):
        result = super(HrExpenseSheet, self).default_get(fields)
        custodian = self.env['account.petty.cash'].sudo().search([('company_id', '=', self.env.company.id)])
        result['valid_user_ids'] = custodian[:1] and [r.user_id.id for r in custodian] or []
        return result

    valid_user_ids = fields.Many2many('res.users', 'valid_petty_cash_user_rel', string="Valid Users")
    user_id = fields.Many2one('res.users', 'Manager', readonly=True, copy=False,
                              states={'draft': [('readonly', False)]}, tracking=True, default=_default_user_id)
    petty_cash_account_id = fields.Many2one('account.petty.cash', string="Petty Cash Account", check_company=True,
                                            tracking=True, readonly=True, copy=False,
                                            states={'draft': [('readonly', False)]})
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal', store=True,
                                      related="petty_cash_account_id.journal_id",
                                      check_company=True, tracking=True,
                                      help="The payment method used when the expense is paid by the company.")

    def action_submit_sheet(self):
        if not self.user_id or not self.petty_cash_account_id:
            raise ValidationError(_("You must select a valid custodian and petty cash account."))
        return super(HrExpenseSheet, self).action_submit_sheet()

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.address_id = self.employee_id.sudo().address_home_id
        self.department_id = self.employee_id.department_id

    def action_sheet_move_create(self):
        if self.petty_cash_account_id and self.petty_cash_account_id.balance_amount < self.total_amount:
            for user in self.petty_cash_account_id.threshold_notify_user_ids:
                user.notify_warning(
                    f'Custodian of {self.petty_cash_account_id.name} account is trying to post a liquidation '
                    f'Enteries. However, the Total Liquidation Expense he is trying to post is greater than the '
                    f'remaining Petty Cash Fund balance. You may consider replenishing it.', False, True)
            return True
            # raise UserError(_(
            #     "The Total Liquidation Expense you are trying to post is greater than the remaining Petty Cash Fund balance. Please replenish it first in order to proceed"))
        return super(HrExpenseSheet, self).action_sheet_move_create()

    def action_sheet_move_create(self):
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        if self.petty_cash_account_id:
            if self.petty_cash_account_id.balance_threshold_amount >= self.petty_cash_account_id.balance_amount:
                for user in self.petty_cash_account_id.threshold_notify_user_ids:
                    user.notify_danger(
                        f'{self.petty_cash_account_id.name} account has already reached its Threshold Balance. Please Replenish it.',
                        f'{self.petty_cash_account_id.name} account need Replenishment!', True)
                return True
        return res
