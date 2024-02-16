# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "LMS Trucking",
    "description": "Logistics Managment System ML Trucking LLC",
    "version": "15.0.0.1.0",
    "category": "Tools",
    "author": "Mon Logistics Group",
    "website": "https://mlholding.mn/",
    "depends": [
        "base", 
        "fleet", 
        "sale",
        "base_geolocalize",
        "web_google_maps",
        "google_marker_icon_picker"
    ],
    "data": [
        "views/menu.xml",
        "views/res_company.xml",
        'views/res_company.xml',
        "report/mltrucking_each_document_data.xml",
        "views/inherited_field.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/inherited_field.xml",
        "views/trucking_base.xml",
        "views/trucking_shipment.xml",
        "views/trucking_type.xml",
        "views/trucking_address.xml",
        "views/trucking_transport_mail.xml",
        "views/trucking_incoterms.xml",
        "views/trucking_package_data.xml",
        "views/trucking_mail_data.xml",
        "views/trucking_freight_photo.xml",
        "views/trucking_port.xml",
        "views/trucking_points.xml",
        "views/trucking_route.xml",
        "views/trucking_order.xml",
        "views/trucking_service_wizard.xml",
        "views/trucking_package.xml",
        "data/trucking_data.xml",
        "views/trucking_services.xml",
        "views/trucking_currency.xml",
        "views/trucking_quotation_data.xml",
        "views/invoice_data.xml",
        "views/trucking_budget_data.xml",
        "views/trucking_document_data.xml",
        "views/trucking_expenditure_data.xml",
        "views/trucking_transport_mail_data.xml",
        "views/fleet_vehicle.xml",
        "report/mltrucking_document_template.xml",
        "report/empty_blank_template.xml",
        "report/mltrucking_quotation_template.xml",
        "report/invoice_data.xml", 
        "views/trucking_core.xml",
        "report/sale_order_quotation.xml",
        "report/mltrucking_budget.xml",
        "views/trucking_quotation_mail.xml",
        "views/sale_order_quotation.xml"
        
    ],
    'assets': {
        'web.assets_qweb': [
            'ml_trucking-main/static/src/xml/mltruck_dashboard.xml',
        ],
        'web.assets_backend': [
            
            'ml_trucking-main/static/src/css/dashboard.scss',
            'ml_trucking-main/static/src/js/chart.min.js',
            'ml_trucking-main/static/src/js/mltruck_dashboard.js',
        ],
    },
    "installable": True,
}
