# -*- coding: utf-8 -*-
{
    'name': "Petty Cash Management",

    'summary': """
        Petty cash management where Expense module is used as the base liquidation app in the accounting""",
    'author': "Dennis Boy Silva",
    'category': 'Accounting',
    'version': '13.0.1',
    'depends': [
        'account',
        'hr_expense',
        'account_reports',
        'web_notify'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/petty_cash.xml',
        'views/expense.xml',
    ],
    'installable': True,
    'auto_install': False,
}
