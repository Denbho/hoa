# -*- coding: utf-8 -*-
{
    'name': "Property User Access Restriction",
    'summary': """
        Limit user access to Subdivision Property""",
    'description': """
    """,
    'author': "Dennis Boy Silva",
    'category': 'Accounting',
    'version': '0.1',
    'depends': [
        'property_base',
        ],
    'data': [
        'security/security.xml',
        'views/users.xml'
    ],
    'installable': True,
    'auto_install': False,
}
