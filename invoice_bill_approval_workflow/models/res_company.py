# -*- coding: utf-8 -*-
from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    invoice_bill_approval = fields.Boolean("Invoice/Bill Approval")
    invoice_ammount = fields.Monetary(string='Invoice Double validation amount')
    bill_ammount = fields.Monetary(string='Bill Double validation amount')
    customer_vendor_credit_approval = fields.Boolean("Customer/Vendor Credit Note Approval")
    customer_credit_note_ammount_ammount = fields.Monetary(string='Customer credit note alidation amount')
    vendor_credit_note_ammount = fields.Monetary(string='Vendor credit note validation amount')
