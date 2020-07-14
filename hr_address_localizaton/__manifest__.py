# -*- coding: utf-8 -*-
{
    'name': "PH Localized Address in Employee Profile",

    'summary': """
        PH Standard Localized Address""",

    'description': """
        The following are added:
            * Continents
            * Continent Regions
            * Countries
            * Island Groups
            * Regional Clusters
            * States/Regions
            * Provinces
            * Cities
            * Barangay
    """,
    'author': "Dennis Boy Silva",
    'category': 'HR',
    'version': '0.1',
    'depends': [
        'hr',
        'localize_address',
    ],
    'data': [
        'views/employee.xml'
    ],
    'installable': True,
    'auto_install': False,
}
