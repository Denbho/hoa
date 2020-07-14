# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare




class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def default_get(self, default_fields):
        res = super(AccountMove, self).default_get(default_fields)
        branch_id = False
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({
            'branch_id' : branch_id
        })
        return res


    branch_id = fields.Many2one('res.branch', string='Branch', domain="[('company_id', '=', company_id)]")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def default_get(self, default_fields):
        res = super(AccountMoveLine, self).default_get(default_fields)
        branch_id = False
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({'branch_id' : branch_id})
        return res

    branch_id = fields.Many2one('res.branch', string='Branch', domain="[('company_id', '=', company_id)]")

    # @api.model
    # def create(self, vals):
    #     if not vals.get('branch_id'):
    #         vals['branch_id'] = self.env['account.move'].browse(vals.get('move_id'))
