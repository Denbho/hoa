# -*- coding: utf-8 -*-
{
    'name': "CRM Stage Validations",

    'summary': """
        Additional validation layer upon moving to the next stage.
    """,

    'description': """
        The following are added on the CRM stage form:
            *   Minimum Expected Revenue
            *   Minimum Probability Rate
        Wizard pop-up when Opportunity converting to won stage
    """,
    'author': "Dennis Boy Silva",
    'category': 'CRM',
    'version': '13.0.1',
    'depends': [
        'crm',
        'website_crm_score',
    ],
    'data': [
        'wizard/convert_to_won.xml',
        'views/crm.xml',
    ],
    'installable': True,
    'auto_install': False,
}
