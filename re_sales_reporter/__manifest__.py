# -*- coding: utf-8 -*-
{
    'name': "RE Sales Reporter",

    'summary': """
        Module For RE Sales Analytics""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bria Homes Inc.",
    'website': "http://www.bria.com.ph",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/security.xml',
        'security/ir.model.access.csv',
        'views/re_sales_reporter.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
