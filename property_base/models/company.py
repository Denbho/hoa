# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char(string="Code")


class ResBranch(models.Model):
    _inherit = 'res.branch'

    code = fields.Char(string="Code")


class AnalyticAccountGroup(models.Model):
    _inherit = 'account.analytic.group'

    code = fields.Char(string="Code/Reference")


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    code = fields.Char(string="Code/Reference")
