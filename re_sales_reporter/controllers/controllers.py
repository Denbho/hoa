# -*- coding: utf-8 -*-
# from odoo import http


# class /home/sysadmin/odoo13/odoo-extra-addons/reSalesReporter(http.Controller):
#     @http.route('//home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter//home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter//home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('/home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter.listing', {
#             'root': '//home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter//home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter',
#             'objects': http.request.env['/home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter./home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter'].search([]),
#         })

#     @http.route('//home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter//home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter/objects/<model("/home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter./home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/home/sysadmin/odoo13/odoo-extra-addons/re_sales_reporter.object', {
#             'object': obj
#         })
