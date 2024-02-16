# -*- coding: utf-8 -*-
{
    'name': "ml_currency_rate_update",
    'description': """
        ML Cyrrency rate updater
    """,
    'author': "Mon Logistics Holding",
    'website': "http://www.mlholding.mn",
    'category': 'Tools',
    'version': '15.0.0.1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/mlcurrency_views.xml',
        'views/ml_currency_update.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
