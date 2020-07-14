# -*- coding: utf-8 -*-
{
    'name': "Additional Information of Contact Profile",

    'summary': """
        Additional Information of Contact Profile""",

    'description': """
        The following are added:
            * Spause Information
            * Co-borrower's Information
            * Attorney-In-Fact Information
            * Work and Occupation
                *  Business Information
                * Emplyment and OFW Information
            * Financial References
            * Personal References
        Data are sync with CRM
    """,

    'author': "Dennis Boy Silva",
    'category': 'Accounting',
    'version': '0.1',
    'depends': [
        'base',
        'crm',
        'portal',
        'contacts',
        #OCA Modules: https://github.com/OCA/partner-contact.git
        'partner_firstname',
        'partner_vat_unique',
        # 'partner_identification',
        #Sustom Module
        'localize_address',
        ],
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        # 'wizard/share_contact.xml',
        'views/contact.xml',
        'views/crm.xml',
        'views/contact_template.xml'
    ],
    'installable': True,
    'auto_install': False,
}
