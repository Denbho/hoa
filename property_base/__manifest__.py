# -*- coding: utf-8 -*-
{
    'name': "Property",
    'summary': """
        Base Module for Property Management""",
    'description': """
    """,
    'author': "Dennis Boy Silva",
    'category': 'Accounting',
    'version': '0.1',
    'depends': [
        'base',
        'account',
        'hr',
        'contacts',
        'analytic',
        'localize_address',
        'product',
        'contact_additional_info',
        'branch',
        'product_brand_sale',
        'website_sale'
        ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/property.xml',
        'views/company.xml',
    ],
    'installable': True,
    'auto_install': False,
}
