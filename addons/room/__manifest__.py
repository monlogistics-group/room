# -*- coding: utf-8 -*-
{
    'name': "Room Order",
    'summary': """
        Odoo Room Order
        """,

    'description': """
        Room Order
    """,
    'author': "Churug",
    'website': "https://lms.monlogistics.mn",
    'category': 'Developers',
    'version': '1.0.0',
    'application': True,
    'license': 'OPL-1',
    'currency': 'MNT',
    'price': 0.0,
    'maintainer': 'MonLogistics',
    'support': 'khuderchuluun@mlholding.mn',

    # any module necessary for this one to work correctly
    'depends': ['calendar'],

    # always loaded
    'data': [
        'views/room_order_views.xml'
    ],

    "application": True,
    "installable": True,
    "auto_install": False,
}
