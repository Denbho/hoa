# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.osv import expression


class AccountAnalyticGroup(models.Model):
    _inherit = 'account.analytic.group'

    def name_get(self):
        res = super(AccountAnalyticGroup, self).name_get()
        data = []
        for i in self:
            display_value = f"{i.name}"
            if i.parent_id:
                display_value = f"{i.parent_id.name}/{i.name}"
            data.append((i.id, display_value))
        return data

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100):
    #     args = args or []
    #     domain = ['|', ('name', operator, name), ('parent_id', operator, name)]
    #     return super(AccountAnalyticGroup, self).search(expression.AND([args, domain]), limit=limit).name_get()


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.name
            if analytic.code:
                name = '[' + analytic.code + '] ' + name
            if analytic.partner_id.commercial_partner_id.name:
                name = name + ' - ' + analytic.partner_id.commercial_partner_id.name
            if analytic.group_id:
                name = f"{analytic.group_id.complete_name}/{name}"
            res.append((analytic.id, name))
        return res
    

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if operator not in ('ilike', 'like', '=', '=like', '=ilike'):
            return super(AccountAnalyticAccount, self)._name_search(name, args, operator, limit,
                                                                    name_get_uid=name_get_uid)
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            # `partner_id` is in auto_join and the searches using ORs with auto_join fields doesn't work
            # we have to cut the search in two searches ... https://github.com/odoo/odoo/issues/25175
            partner_ids = self.env['res.partner']._search([('name', operator, name)], limit=limit,
                                                          access_rights_uid=name_get_uid)
            domain = ['|', '|', '|', ('code', operator, name), ('name', operator, name), ('partner_id', 'in', partner_ids), ('group_id', operator, name)]
        analytic_account_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(analytic_account_ids).with_user(name_get_uid))


    


