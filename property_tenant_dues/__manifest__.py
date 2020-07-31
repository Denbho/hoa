# -*- coding: utf-8 -*-
{
    'name': "Tenant Subscription Report",

    'summary': """
        Tenant Subscription Report List""",
    'description': """
    """,
    'author': "Dennis Boy Silva",
    'category': 'Sales',
    'version': '0.1',
    'depends': [
        'account',
        'sale_subscription',
        'property_base',
        'property_subscription',
        'property_user_access_restriction',
        ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/tenant_due_list.xml'
    ],
    'installable': True,
    'auto_install': False,
}
