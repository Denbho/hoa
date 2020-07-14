# -*- coding: utf-8 -*-
{
    'name': "Property Sale: Tenant Subscription",

    'summary': """
        Management of Tenant's Property Dues""",
    'description': """
    """,
    'author': "Dennis Boy Silva",
    'category': 'Sales',
    'version': '0.1',
    'depends': [
        'sale',
        'sale_subscription',
        'property_base',
        'property_sale'
        ],
    'data': [
        'view/subscription.xml',
        'view/property.xml',
        'view/subscription_template.xml'
    ],
    'installable': True,
    'auto_install': False,
}
