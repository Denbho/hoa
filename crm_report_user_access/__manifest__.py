# -*- coding: utf-8 -*-
{
    'name': "CRM - User for Reports only",

    'summary': """
    CRM - User for Reports only
        """,

    'description': """
    """,

    'author': "Dennis Boy Silva",
    'category': 'CRM',
    'version': '13.0.1',
    'depends': [
        'crm',
        'sales_team'
        ],
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/crm.xml',
    ],
    'installable': True,
    'auto_install': False,
}
