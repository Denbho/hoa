# -*- coding: utf-8 -*-
{
    'name': "CRM Track Stagnant Leads",

    'summary': """
        This module track the number of days when it was last updated and able to send report via Email""",
    'author': "Dennis Boy Silva",
    'category': 'CRM',
    'version': '13.0.1',
    'depends': [
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stagnant_list_template.xml',
        'views/crm.xml'
    ],
    'installable': True,
    'auto_install': False,
}
