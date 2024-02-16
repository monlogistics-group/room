# -*- coding: utf-8 -*-
{
    'name': "Odoo REST API",
    'summary': """
        Odoo REST API
        """,

    'description': """
        This module provide you accessibility to connect your odoo application with third party application,
        Rest,
        Rest API,
        APIs,
        odoo Rest API,
        tortecs,
        tortecs India,
        woocommerce,
        shopify,
        back market,
        pestashop,
    """,
    'author': "Tortecs India",
    'website': "https://www.tortecs.com/",
    'category': 'Developers',
    'version': '1.0.0',
    'application': True,
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 29.0,
    'maintainer': 'Tortecs India',
    'support': 'sales@tortecs.com',
    'images': ['static/description/banner.gif'],

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/tt_token_cron.xml',
        'views/tt_rest_api_view.xml',
        'views/tt_res_config_view.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'rest_api/static/src/xml/tt_table_template.xml',
        ],
        'web.assets_backend': [
            'rest_api/static/src/js/tt_route_widget.js',
        ],
    },

    "application": True,
    "installable": True,
    "auto_install": False,

    'external_dependencies': {
    }
}
