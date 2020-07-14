# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.backend import WebsiteBackend


class kitepages(http.Controller):

    @http.route(['/quotation'], type='http', auth="public", methods=['POST','GET'], website=True, csrf=False)
    def quote_send(self, product_id, **values):
        product = request.env['product.template'].sudo().browse(int(product_id))
        values = {
            'product_id': int(product_id),
            'product_description_name': product[:1] and f'Request for Quotation: {product.display_name}',
            'product_description_sale': product[:1] and f'Property: {product.display_name}\n {product.description_sale}'
        }
        template = 'request_quote.quotation'
        return request.render(template, values)

    def _filter_attributes(self, **kw):
        return {k: v for k, v in kw.items() if "attribute" in k}
