# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
import werkzeug.urls
import werkzeug.wrappers
import base64
import io
from io import StringIO
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime, date
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal


class OdooWebsiteAllInOne(http.Controller):

    @http.route('/shop/payment/attachment/add', type='http', auth="public", website=True)
    def payment_attachment_add(self, url=None, upload=None, **post):
    
        cr, uid, context = request.cr, request.uid, request.context 

        order = request.website.sale_get_order()
                    
        Attachments = request.env['ir.attachment']  # registry for the attachment table
        
        upload_file = request.httprequest.files.getlist('upload')
        
        if upload_file:
            for i in range(len(upload_file)):
                attachment_id = Attachments.sudo().create({
                    'name': upload_file[i].filename,
                    'type': 'binary',
                    'datas': base64.b64encode(upload_file[i].read()),
                    'store_fname': upload_file[i].filename,
                    'public': True,
                    'res_model': 'ir.ui.view',
                    'sale_order_id' : order.id,
                })   
            
            return request.redirect('/shop/payment')
        
    @http.route(['/search/suggestion'], type='http', auth="public", website=True)
    def search_suggestion(self, **post):
        #print "/search/suggestion calleddddddddddddddddddddddddddddddddddddddddddddddddd",post, post.get('query').split(" ")
        suggestion_list = []
        product=[]
        product_list_name={}        


        if post:
            for suggestion in post.get('query').split(" "):
                product_list = request.env['product.template'].search(([('website_published', '=', True), ('name', "ilike", suggestion)]))
                #print "====================product_list",product_list
                read_prod = product_list.read(['name','public_categ_ids'])
                #print "****************************product_obj",product_list
                suggestion_list = suggestion_list + read_prod
                #print "2222222222222222222222222212product_obj",suggestion_list
                

        for line in suggestion_list:
            if len(line['public_categ_ids'])==0:
                #print "\n \n =========================line",line
                prod_str=line['name']+ "No category"
                #print "\n \n =========================id",id
                if not prod_str in product_list_name :
                    product.append({'product':line['name'],'category':'No category'})

            for pub_cat_ids in line['public_categ_ids']:
                categ_srch= request.env['product.public.category'].search(([('id','=',pub_cat_ids)]))
                categ_read = categ_srch.read(['name'])
                #print "\n \n ====================categ",categ_read
                prod_str=line['name']+categ_read[0]['name']
                #print "\n \n =========================line",prod_str                
                if not prod_str in product_list_name :
                    product.append({'product':line['name'],'category':categ_read[0]['name']})
        #print "=================product_list_name",product_list_name


        data={}
        #print "================="
        data['status']=True,
        #print "================="
        data['error']=None,
        #print "================="
        data['data']={'product':product}
        #print "================="
        return json.dumps(data)
        
    @http.route(['/page/sitemap'], type='http', auth="public", website=True)
    def odoo_sitemap(self, page=0, category=None, search='', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        return request.render("website_all_in_one.website_sitemap")
        
                
class WebsiteSaleAttachment(WebsiteSale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):

        res = super(WebsiteSaleAttachment,self).product(product,category,search,**kwargs)
        
        attachment_obj = request.env['product.attachment']
        attachments = attachment_obj.sudo().search([('product_tmpl_id', '=', product.id)])

        res.qcontext.update({
            'attachments': attachments
        })
        return res
        

    @http.route(['/download/attachment'], type='http', auth="public", website=True)
    def download_attachment(self, attachment_id):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        attachment = request.env['product.attachment'].sudo().search_read([('id', '=', int(attachment_id))], ["attachment","name"])

        if attachment:
            attachment = attachment[0]
        else:
            return redirect('/shop')

        data = io.BytesIO(base64.standard_b64decode(attachment["attachment"]))
        return http.send_file(data, filename=attachment['name'], as_attachment=True)


    @http.route(['/shop/product/comment/<int:product_template_id>'], type='http', auth="public", methods=['POST'], website=True)
    def website_product_review(self, product_template_id, **post):
        cr, uid, context = request.cr, request.uid, request.context
        description=post.get('short_description')
        review_rate = post.get('review')
        comment = post.get('comment')
        #customer_id = request.uid
        
        reviews_ratings = request.env['reviews.ratings']
        reviews_ratings.create({'message_rate':review_rate, 'short_desc':description, 'review':comment, 'website_message':True, 'rating_product_id':product_template_id, 'customer_id':uid})

        return werkzeug.utils.redirect( request.httprequest.referrer + "#reviews" )
                
                
class website_account_payment(CustomerPortal):

    @http.route(['/my/invoices/multiple/payment'], type='http', auth="public", website=True)
    def multiple_payment(self,**post):
        if post:
            user_id = request.uid
            user = request.env['res.users'].browse(user_id)
            invoice_obj = request.env['account.move']

            invoices = []
            id_list = post['invoice']
            new_list = id_list.split(',')
            invoice_num = ''
            total_amount = 0.00
            if id_list != '':
                for invoice in new_list:
                    invoice_search = invoice_obj.search([('id','=',int(invoice))])
                    invoices.append(invoice_search)
                    invoice_num = invoice_num + invoice_search.name + ','
                    total_amount = total_amount + invoice_search.amount_residual

                currency_id = user.company_id.currency_id.id
                currency = request.env['res.currency'].browse(currency_id)
                
                acquirer_id = request.env['payment.acquirer'].sudo().search([('company_id', '=', user.company_id.id)])
                acquirer = request.env['payment.acquirer'].browse(acquirer_id)
                values = {
                    'acquire_id' : acquirer_id,
                    'invoices' : invoices,
                    'invoice_num' : invoice_num,
                    'total_amount' : float(total_amount),
                }
                return request.render("website_all_in_one.pay_multiple_payment",values)
            else:
                return request.render("website_all_in_one.pay_multiple_payment")
                
    @http.route(['/my/invoices/multiple/payment/confirm'], type='http', auth="public", website=True)
    def multiple_payment_confirm(self, **post):
        if post:
            print("Multiple Payment Confirm$$$$$$$$$$$$$$",post)
            user_id = request.uid
            user = request.env['res.users'].browse(user_id)

            currency_id = user.company_id.currency_id.id
            currency = request.env['res.currency'].browse(currency_id)
            
            acquirer = post['pm_id']
            invoices = post['invoice_ids']
            num_list = post['invoice_num']
            
            invoices = num_list.split(',')
            
            amount = post['amount']
            new_amount = 0

            for invoice in invoices:
                
                acquirer_obj = request.env['payment.acquirer']
                invoice_obj = request.env['account.move']
                reference_obj = request.env['payment.transaction']
                acquirer_id = acquirer_obj.sudo().search([('id','=',int(acquirer))])

                invoice_id = invoice_obj.sudo().search([('name','=',str(invoice))])
                
                reference = reference_obj.sudo()._compute_reference()
                if float(amount) != 0.0:
                    if invoice_id.amount_residual < float(amount):  
                        new_amount = invoice_id.amount_residual
                        amount = abs(invoice_id.amount_residual - float(amount))
                    else:
                        new_amount = float(amount)
                        amount = 0.0
                else:
                    return request.render("website_all_in_one.payment_thankyou")

                tx_values = {
                    'acquirer_id': acquirer_id.id,
                    'reference': reference,
                    'amount': new_amount,
                    'currency_id': int(currency_id),
                    'partner_id': invoice_id.partner_id.id,
                }
                
                tx = request.env['payment.transaction'].sudo().create(tx_values)
                request.session['website_payment_tx_id'] = tx.id

                payment = request.env['account.payment']
                payment_method = request.env['account.payment.method'].sudo().search([],limit=1)
                
                res = payment.sudo().create({
                            'partner_id':invoice_id.partner_id.id,
                            'amount': new_amount,
                            'payment_type':'inbound',
                            'partner_type':'customer',
                            'payment_method_id' : payment_method.id,
                            'journal_id':acquirer_id.journal_id.id,
                            'payment_date':date.today(),
                            'communication':invoice_id.name,
                            'invoice_ids':[(6,0,[invoice_id.id])]
                            })

                sequence_code = 'account.payment.customer.invoice'
                res.sudo().write({
                    
                    'name': request.env['ir.sequence'].sudo().with_context(ir_sequence_date=res.payment_date).next_by_code(sequence_code),

                    })
                
                invoice_id.reconciled = True
                invoice_id.sudo().action_invoice_paid()

                pay_confirm = request.env['account.payment'].sudo().search([("communication","=",invoice_id.name)])
                for payment in pay_confirm:
                    if not payment.state == 'posted':
                        payment.sudo().post()

        return request.render("website_all_in_one.payment_thankyou")
        

    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AccountInvoice = request.env['account.move']

        domain = [
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft', 'posted', 'cancel'])
        ]
        archive_groups = self._get_archive_groups('account.move', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(domain, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/invoices',
        })
        return request.render("website_all_in_one.bi_portal_my_invoices", values)
        
    @http.route(['/my/invoices/partial/<model("account.move"):id>'], type='http', auth="public", website=True)
    def pay_partial(self, **post):
        
        env = request.env
        user = env.user.sudo()
        acquire_id = request.env['payment.acquirer'].search([('company_id', '=', user.company_id.id)])
        acquire_obj = request.env['payment.acquirer'].browse(acquire_id)
        values = {
                'id' : post['id'],
                'invoice' : post['invoice'],
                'acquire_id' : acquire_id,
        }
        return request.render("website_all_in_one.pay_portal_payment",values)

    
    @http.route(['/my/invoices/partial/confirm'], type='http', auth="public", website=True)
    def quote_confirm(self, **post):
         
        if post:
            user_id = request.uid
            user = request.env['res.users'].browse(user_id)

            currency_id = user.company_id.currency_id.id
            currency = request.env['res.currency'].browse(currency_id)
            
            acquirer = post['pm_id']
            invoice = int(post['invoice'])
            amount = post['amount1']

            acquirer_obj = request.env['payment.acquirer']
            invoice_obj = request.env['account.move']
            reference_obj = request.env['payment.transaction']
            acquirer_id = acquirer_obj.sudo().search([('id','=',int(acquirer))])

            invoice_id = invoice_obj.sudo().browse(invoice)
            reference = reference_obj.sudo()._compute_reference()  

            tx_values = {
                'acquirer_id': acquirer_id.id,
                'reference': reference,
                'amount': float(amount),
                'currency_id': int(currency_id),
                'partner_id': invoice_id.partner_id.id,
            }
            
            tx = request.env['payment.transaction'].sudo().create(tx_values)
            request.session['website_payment_tx_id'] = tx.id

            payment = request.env['account.payment']
            payment_method = request.env['account.payment.method'].sudo().search([],limit=1)

            res = payment.sudo().create({
                        'partner_id':invoice_id.partner_id.id,
                        'amount': amount,
                        'payment_type':'inbound',
                        'partner_type':'customer',
                        'payment_method_id' : payment_method.id,
                        'journal_id':acquirer_id.journal_id.id,
                        'payment_date':date.today(),
                        'communication':invoice_id.name,
                        'invoice_ids':[(6,0,[invoice_id.id])]
                        })

            sequence_code = 'account.payment.customer.invoice'
            res.sudo().write({
                
                'name': request.env['ir.sequence'].sudo().with_context(ir_sequence_date=res.payment_date).next_by_code(sequence_code),

                })
            
            invoice_id.reconciled = True
            invoice_id.sudo().action_invoice_paid()

            pay_confirm = request.env['account.payment'].sudo().search([("communication","=",invoice_id.name)])
            for payment in pay_confirm:
                if not payment.state == 'posted':
                    payment.sudo().post()

            return request.render("website_all_in_one.payment_thankyou")

