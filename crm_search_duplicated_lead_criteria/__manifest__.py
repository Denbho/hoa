# -*- coding: utf-8 -*-
{
    'name': 'Search Criteria for Duplicate Leads',
    'version': '13.0.1',
    'summary': 'Added new search criteria for duplicate leads and opportunities',
    'description': """
    From just Partner/Contact's email added here the following criteria
        * Lead/Opportunities Title
        * Sales Team
        * Salesperson
        * Contact Person
        * Subdivision
        * Project
        * House Model
    Note: 
        * Search will only trigger if the selected lead has email address
    Merge opportunities together.
        If we're talking about opportunities, it's just because it makes more sense
        to merge opps than leads, because the leads are more ephemeral objects.
        But since opportunities are leads, it's also possible to merge leads
        together (resulting in a new lead), or leads and opps together (resulting
        in a new opp).
    """,
    'category': 'crm',
    'author': "Dennis Boy Silva",
    'depends': [
        'crm',
    ],
    'data': [
        'wizard/convert_to_opportunity.xml'
    ],
    'installable': True,
    'auto_install': False
}