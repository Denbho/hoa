# -*- coding: utf-8 -*-
{
    'name': "Property Sale",

    'summary': """
        Base Module for Property Sales Management""",
    'description': """
    """,
    'author': "Dennis Boy Silva",
    'category': 'Sales',
    'version': '0.1',
    'depends': [
        'localize_address',
        'product',
        'contact_additional_info',
        'product_brand_sale',
        'website_sale',
        'stock',
        'property_base',
        'property_crm',
        'sale_coupon',
        'branch',
        'sale_enterprise',
        'partner_defualt_account_entries_and_restriction',
        ],
    'data': [
        'reports/sales_report_template.xml',
        'views/product_template.xml',
        'views/property.xml',
        'views/product.xml',
        'views/sale.xml'
    ],
    'installable': True,
    'auto_install': False,
}
