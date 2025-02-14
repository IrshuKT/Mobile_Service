# -*- coding: utf-8 -*-
{
    'name': "Mobile Service",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Irshad K T",
    'website': "https://www.ktshubmpm.org",
    'application': True,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Mobile Service',
    'sequence': -101,
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail', 'report_pdf_options', 'account', 'stock', 'product', 'board'],

    # always loaded
    'data': [
        'security/mobile_security.xml',
        'security/ir.model.access.csv',
        'sequence/complaint_sequence.xml',
        'report/qr_payment_template.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/brand.xml',
        'views/model.xml',
        'views/term.xml',
        'views/complaint_type.xml',
        'views/complaint_template.xml',
        # 'views/products.xml',
        'views/technician.xml',
        'views/unit.xml',
        'report/service_report_template.xml',
        'report/service_report.xml',
        'report/service_invoice_template.xml',
        'report/service_invoice.xml',
        # 'views/map_view.xml',
        # 'data/mobile_product_data.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'mobileservice/static/src/css/styles.css',
        ]
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
