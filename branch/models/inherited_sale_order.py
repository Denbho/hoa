# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self,fields):
        res = super(SaleOrder, self).default_get(fields)
        if self.env.user.branch_id and self.env.user.branch_id.company_id.id == self.env.company.id:
            res['branch_id'] = self.env.user.branch_id.id
        elif self.env.user.branch_ids.ids:
            for i in self.env.user.branch_ids:
                if self.env.company.id == i.company_id.id:
                    res['branch_id'] = i.id
                    break
        if res.get('branch_id'):
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id','=',res.get('branch_id'))])
            if branched_warehouse:
                res['warehouse_id'] = branched_warehouse.ids[0]
        return res

    branch_id = fields.Many2one('res.branch', string='Branch', domain="[('company_id', '=', company_id)]")


    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['branch_id'] = self.branch_id.id
        return res
