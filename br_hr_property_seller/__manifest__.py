# -*- coding: utf-8 -*-
{
    'name': "Property Sellers Information",

    'summary': """
        Property Sellers Information via HR Employee Profile""",

    'description': """
    """,
    'author': "Dennis Boy Silva",
    'category': 'HR',
    'version': '0.1',
    'depends': [
        'hr',
        'hr_social_media_links',
        'hr_address_localizaton',
        'hr_employee_firstname',
        'hr_employee_recruitement_source',
        'property_crm',
        'partner_defualt_account_entries_and_restriction',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/employee.xml',
        'views/crm.xml',
    ],
    'installable': True,
    'auto_install': False,
}
