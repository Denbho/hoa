# -*- coding: utf-8 -*-
{
    'name': "Property CRM",
    'summary': """
        Base Module for CRM Management and Property related""",
    'description': """
    """,
    'author': "Dennis Boy Silva",
    'category': 'Accounting',
    'version': '0.1',
    'depends': [
        'localize_address',
        'contact_additional_info',
        'property_base',
        'sale_crm',
        'request_quote',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm.xml',
    ],
    'installable': True,
    'auto_install': False,
}
