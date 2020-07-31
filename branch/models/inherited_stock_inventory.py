# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class stock_inventory(models.Model):
    _inherit = 'stock.inventory'


    @api.model
    def default_get(self,fields):
        res = super(stock_inventory, self).default_get(fields)
        if res.get('location_id'):
            location_branch = self.env['stock.location'].browse(res.get('location_id')).branch_id.id
            if location_branch:
                res['branch_id'] = location_branch
        else:
            if self.env.user.branch_id and self.env.user.branch_id.company_id.id == self.env.company.id:
                res['branch_id'] = self.env.user.branch_id.id
            elif self.env.user.branch_ids.ids:
                for i in self.env.user.branch_ids:
                    if self.env.company.id == i.company_id.id:
                        res['branch_id'] = i.id
                        break
        return res

    branch_id = fields.Many2one('res.branch', string='Branch', domain="[('company_id', '=', company_id)]")


    def post_inventory(self):
        # The inventory is posted as a single step which means quants cannot be moved from an internal location to another using an inventory
        # as they will be moved to inventory loss, and other quants will be created to the encoded quant location. This is a normal behavior
        # as quants cannot be reuse from inventory location (users can still manually move the products before/after the inventory if they want).
        self.mapped('move_ids').filtered(lambda move: move.state != 'done')._action_done()
        for move_id in self.move_ids:
            account_move =self.env['account.move'].search([('stock_move_id','=',move_id.id)])
            print ("account_move",account_move)
            account_move.write({'branch_id':self.branch_id.id})
            for line in account_move.line_ids:
                    line.write({'branch_id':self.branch_id.id})
