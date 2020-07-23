# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Mashood K.U (Contact : odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class FilterRecurringEntries(models.Model):
    _inherit = 'account.move'

    is_active = fields.Boolean()
    recurring_internal_ref = fields.Char()


class RecurringPayments(models.Model):
    _name = 'account.recurring.payments'


    def _get_next_schedule(self):

        if self.date:

            recurr_dates = []
            today = datetime.today()
            start_date = datetime.strptime(str(self.date), '%Y-%m-%d')
            while start_date <= today:
                recurr_dates.append(str(start_date.date()))
                if self.recurring_period == 'days':
                    start_date += relativedelta(days=int(self.recurring_interval))
                elif self.recurring_period == 'weeks':
                    start_date += relativedelta(weeks=int(self.recurring_interval))
                elif self.recurring_period == 'months':
                    start_date += relativedelta(months=int(self.recurring_interval))
                else:
                    start_date += relativedelta(years=int(self.recurring_interval))
            self.next_date = start_date.date()



    def get_company_id(self):
        return self.env.user.company_id.id

    name = fields.Char('Name')
    debit_account = fields.Many2one('account.account', 'Debit Account', required=True)
    credit_account = fields.Many2one('account.account', 'Credit Account', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    date = fields.Date('Starting Date', required=True, default=date.today())
    recurring_period = fields.Selection(selection=[('days', 'Days'),
                                                   ('weeks', 'Weeks'),
                                                   ('months', 'Months'),
                                                   ('years', 'Years')], store=True, required=True)
    next_date = fields.Date('Next Schedule', compute=_get_next_schedule, readonly=True)
    amount = fields.Float('Amount')
    description = fields.Text('Description')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('running', 'Running')], default='draft', string='Status')
    journal_state = fields.Selection(selection=[('draft', 'Unposted'),
                                                ('posted', 'Posted')],
                                     required=True, default='posted', string='Generate Journal As')
    recurring_interval = fields.Float('Recurring Interval', default=1)
    partner_id = fields.Many2one('res.partner', 'Partner')
    pay_time = fields.Selection(selection=[('pay_now', 'Pay Directly'),
                                           ('pay_later', 'Pay Later')], store=True, required=True)
    company_id = fields.Integer(default=get_company_id)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.property_account_receivable_id:
            self.credit_account = self.partner_id.property_account_payable_id
