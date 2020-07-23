# -*- coding: utf-8 -*-
{
    'name': "Additional CRM custom parameters",

    'summary': """
    Additional CRM custom parameters and Validations
        """,

    'description': """
        The following are added:
            *   Lead and CRM:
                - Sales Team make required.
                _ Users Can only select team where they are member of.
    """,

    'author': "Dennis Boy Silva",
    'category': 'CRM',
    'version': '13.0.1',
    'depends': [
        'crm',
        'website_crm_score',
        ],
    'data': [
        'views/crm.xml',
    ],
    'installable': True,
    'auto_install': False,
}
