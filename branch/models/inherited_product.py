# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductTemplateIn(models.Model):
    _inherit = 'product.template'


    @api.model
    def default_get(self, default_fields):
        res = super(ProductTemplateIn, self).default_get(default_fields)
        if self._context.get('branch_id'):
            res['branch_id'] = self._context.get('branch_id')
        elif self.env.user.branch_id and self.env.user.branch_id.company_id.id == self.env.company.id:
            res['branch_id'] = self.env.user.branch_id.id
        elif self.env.user.branch_ids.ids:
            for i in self.env.user.branch_ids:
                if self.env.company.id == i.company_id.id:
                    res['branch_id'] = i.id
        return res

    branch_id = fields.Many2one('res.branch', string='Branch', domain="[('company_id', '=', company_id)]")
