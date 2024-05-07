# -*- coding: utf-8 -*-
{
    'name': "Article Manager",

    'summary': """
        Create, Manage and Read Articles""",

    'description': """
        Create, Manage and Read Articles
    """,

    'author': "Onuh Victor",
    'website': "https://github.com/onuh/article_manager",
    'email': "onuhvictor1@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contacts',
    'version': '16.0.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['contacts', 'portal'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'report/article_manager_report.xml',
        'views/report_template.xml',
        'views/mail_template.xml',
        # 'demo/demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'article_manager/static/src/views/**/*',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
