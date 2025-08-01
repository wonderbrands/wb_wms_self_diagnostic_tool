# -*- coding: utf-8 -*-
{
    'name': "WB WMS Self Diagnostic Tool",

    'summary': """
        A tool that checks EP portals API and synnchronizes the info available into odoo
    """,

    'description': """
        A tool that checks EP portals API and synnchronizes the info available into odoo,
        such as the list od Sale Orders.
    """,

    'author': "Wonderbrands - Demian Avila",
    'website': "https://wonderbrands.co/",


    'category': 'Technical',
    'version': '15.0',

    'depends': [
        'base', 
        'sale_management',
        'wb_sale',
        'wms_integrator_module',
        'madkting'
    ],

    'data': [
        'data/rules.xml',
        'cron/cron_oms.xml',
    ],

    'external_dependencies': {
        'python': [
            'PyPDF2',
            'polars'
        ],
    },
    
}
