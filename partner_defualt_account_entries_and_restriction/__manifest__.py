# -*- coding: utf-8 -*-
{
    'name': "Customers and Vendors Account Restriction and Validation",
    'summary': """
        Set default Chart of Account on AP, AR and account Restriction""",
    'description': """
    Through this module you can do the following:
        * Able to Set Contact type;
        * Able to Set Default Partner's Chart of Account (Receivable/Payable type);
        * Restrict and Validate the use of Chart of Account in the Journal Entries related to partner;
        * Group your Vendor/Customer and set an ID number related to their Contact type;
        * Display the Journal type ang Journal group in the Journal Entries document;
        * Able to add payment processing date on the Payment form.
        
    Please note, Account validation on applies to Sale and Purchase type journal related.
    """,
    'author': "Dennis Boy Silva",
    'category': 'Accounting',
    'version': '13.0.1',
    'price': 20.00,
    'currency': 'EUR',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'auto_install': False,
}
