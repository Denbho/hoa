# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition
import base64
import os, os.path
import csv
from os import listdir
import sys



class Download_xls(http.Controller):
    
    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self,model,id, **kw):

        Model = request.env[model]
        res = Model.browse(int(id))

        if res.sample_option == 'xls' and res.account_opt == 'default':

            invoice_xls = request.env['ir.attachment'].search([('name','=','invoice.xls')])
            filecontent = invoice_xls.datas
            filename = 'Invoice Without Account.xls'
            filecontent = base64.b64decode(filecontent)

        elif res.sample_option == 'xls' and res.account_opt == 'custom':

            invoice_xls = request.env['ir.attachment'].search([('name','=','invoice_with_account.xls')])
            filecontent = invoice_xls.datas
            filename = 'Invoice With Account.xls'
            filecontent = base64.b64decode(filecontent)

        elif res.sample_option == 'csv' and res.account_opt == 'default':

            invoice_xls = request.env['ir.attachment'].search([('name','=','invoice.csv')])
            filecontent = invoice_xls.datas
            filename = 'Invoice Without Account.csv'
            filecontent = base64.b64decode(filecontent)

        elif res.sample_option == 'csv' and res.account_opt == 'custom':

            invoice_xls = request.env['ir.attachment'].search([('name','=','invoice_with_account.csv')])
            filecontent = invoice_xls.datas
            filename = 'Invoice With Account.csv'
            filecontent = base64.b64decode(filecontent)
            

        return request.make_response(filecontent,
            [('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', content_disposition(filename))])