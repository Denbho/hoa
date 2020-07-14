# -*- coding: utf-8 -*-
{
    'name': "Website Product Quotation",

    'summary': """
        Creates Leads and Quotation from website shop with product details.
        """,

    'description': """
        Allowes the user to send quotion for a product from website which creates lead in backend.
        Allowes sales person to generate lead with product lines.
    """,
    'price': 49.00,
    'currency': 'EUR',
    'author': "Techspawn Solutions and Enhanced & Corrected by Dennis Boy Silva",
    'website': "http://www.techspawn.com",
    'license':'OPL-1',
    'category': 'Sale/Crm',
    'version': '1.1',

    'depends': ['base','crm', 'sale', 'sale_management', 'sale_crm', 'website_sale'],


    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/quote_view.xml',
            
    ],
    "images": ['static/description/WebsiteProductQuotation.jpg'],
    "installable": True,
}