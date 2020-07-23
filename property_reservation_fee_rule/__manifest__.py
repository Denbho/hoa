# -*- coding: utf-8 -*-
{
    'name': "Property Reservation Fee Rule",
    'summary': """
        Template for rule of reservation fees""",
    'description': """
    This enable the user to create rule to be applied on the to total amount of reservation fee.
    """,
    'author': "Dennis Boy Silva",
    'category': 'Accounting',
    'version': '0.1',
    'depends': [
        'product',
        'account',
        'stock',
        'sale_stock',
        'property_base',
        'property_sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/property.xml',
    ],
    'installable': True,
    'auto_install': False,
}
