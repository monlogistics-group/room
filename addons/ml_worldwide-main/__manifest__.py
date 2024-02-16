# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02
{
    "name": "Worldwide Freights",
    "version": "15.0.0.1.0",
    "category": "Tools",
    "author": "Mon Logistics Group",
    "website": "https://mlholding.mn/",
    "depends": [
        "base", 
        "sale",
        "fleet",
        "account",
        "crm",
        "hr",
        "website",
        "web",
        "website_payment",
        "web_responsive",
        "base_geolocalize",
        "web_google_maps",
        "web_domain_field",
        "report_xlsx",
        "google_marker_icon_picker"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "wizard/insurance_appendix_views.xml",
        "wizard/freights_route_shipment.xml",
        "views/menu.xml",
        "views/freight_search_wizard.xml",
        "views/freight_stations.xml",
        "views/worldwide_freights.xml",
        "views/freights_shipments.xml",
        "views/freights_service.xml",
        "views/freights_payment_service.xml",
        "views/freights_service_template.xml",
        "views/freights_type.xml",
        "views/freights_terms.xml",
        "views/freights_packages.xml",
        "views/freights_quotations.xml",
        # "views/freight_container_details.xml",
        "views/quotation_confirm_wizard.xml",
        "views/freights_container_movement.xml",
        "views/worldwide_pdf_photo.xml",
        "views/freights_points.xml",
        "views/preview_pdf_wizard.xml",
        "views/freights_terminal.xml",
        "views/worldwide_confirm_quotation_email.xml",
        "views/freights_hscode_category.xml",
        "views/quotation_agents_mails.xml",
        "views/freights_tara.xml",
        "views/insurance_cost.xml",
        "views/freights_route_category.xml",
        "views/freights_wagon_type.xml",
        "views/freights_truck_type.xml",
        "views/confirm_quot_header.xml",
        "views/freights_shipping_line.xml",
        "data/worldwide_default_data.xml",
        "data/service_cron.xml",
        "data/quotation_mail_data.xml",
        "data/product_product_data.xml",
        "views/worldwide_cron_jobs.xml",
        "views/service_types.xml",
        "views/worldwide_user_groups.xml",
        "views/confirm_agent_quotation.xml",
        "views/worldwide_confirm_agent_quotation.xml",
        "views/hr_employee.xml",
        "views/freights_agent_inquiry.xml",
        "views/res_partner.xml",
        "views/container_yard.xml",
        "views/worldwide_quotation_data.xml",
        "views/worldwide_quotation_mail_data.xml",
        "views/employee_role.xml",
        "report/shipment_confirmation.xml",
        "report/shipment_order.xml",
        "report/confirm_quotation_agent_mail.xml",
        "report/confirm_quotation_email.xml",
        "report/empty_blank_template.xml",
        "report/mlworldwide_confirm_quotation_pdf.xml",
        "report/mlworldwide_quotation_template.xml",
        "report/mlworldwide_quotation_email_template.xml",
        "report/cargo_receipt.xml",
        "report/feedback_email.xml",
        "report/arrival_notice.xml",
        "report/send_truck_email.xml",
        "report/invoice_data.xml",
        "views/invoice_data.xml",
        "views/package_wizard.xml",
        "wizard/agent_inquiry_send_views.xml",
        "wizard/freights_type_assign.xml",
        "wizard/freights_invoice_create.xml",
        "wizard/add_records_to_payments.xml",
        "views/freights_container_type.xml",
        "views/freights_containers.xml",
        "views/freights_order_routes.xml",
        "views/cargo_receipt_data.xml",
        "views/freights_employee_role.xml",
        "views/freights_route.xml",
        "views/arrival_notice_data.xml",
        "views/freights_abilities.xml",
        "views/freights_release_status.xml",
        "views/freights_route_shipment.xml",
        "views/freights_shipment_type.xml",
        "views/freights_shipments_delay.xml",
        "views/freights_agent_review.xml",
        "views/freights_client_feedback.xml",
        "views/freight_incexc_service.xml",
        "views/freights_service_type.xml",
        "views/base_condition.xml",
        "views/inquiry_data.xml",
        "views/worldwide_reason_remark.xml",
        "views/worldwide_reason.xml",
        "views/freights_cost_type.xml",
        "views/crm_lead.xml",
        "views/delivery_rate.xml",
        "views/sale_order.xml",
        "views/res_company.xml",
        "data/incoterms_data.xml",
        "data/freight_type.xml",
        "data/wgn_type.xml",
        "data/truck_type.xml",
        "data/freight_taras.xml",
        "data/fcl_route.xml",
        "data/abilities.xml",
        "data/hscode_category.xml",
        "data/shipping_line.xml",
        "data/container_type.xml",
        "data/shipment_type.xml",
        "data/release status.xml",
        # "data/service_types_data.xml",
        "data/transport_type.xml",
        "data/delivery_rate.xml",
        "data/monthly_report.xml",
        "data/shpment_delay_reason.xml",
        "report/send_all.xml",
        'restApiViews/container_information.xml',
        "data/quotation.xml",
        "views/package_request.xml",
        "views/route_data.xml",
        "views/monthly_report.xml",
        "views/monthly_report_data.xml",
        "views/freights_insurance_view.xml",
        "views/delivery_rates.xml",
        "views/fob_rates.xml",
        "views/demurrages_rates.xml",
        "views/thc_rate.xml",
        "views/customer_rates.xml",
        "views/socprice_rate.xml",
        "views/shipment_order_tdmdata.xml",
        "views/account_incoterms.xml",
        "data/route_data.xml",
        "data/shipment_data.xml",
        "data/invoice_data.xml",
        "data/record_rule.xml",
        "report/route_template.xml",
        "restApiViews/dangerous_goods.xml",
        "restApiViews/wagon_types.xml",
        'restApiViews/worldwide_news.xml',
        "report/confirm_quotation_email.xml",
        "report/mlworldwide_generate_pdf_using_img.xml",
        "report/monthly_report_email.xml",
        "report/report_email_month.xml",
        "report/mlworldwide_invoice_template.xml",
        "report/confirm_quotation_agent_mail.xml",
        "report/empty_blank_template.xml",
        "report/mlworldwide_confirm_quotation_pdf.xml",
        "report/mlworldwide_quotation_template.xml",
        "report/mlworldwide_quotation_email_template.xml",
        "report/invoice_data.xml",
    ],
    'assets': {
        'web.assets_qweb': [
            'ml_worldwide-main/static/src/xml/mlw_dashboard.xml',
            'ml_worldwide-main/static/src/xml/groupby_templates.xml',
            'ml_worldwide-main/static/src/xml/ml_worldwide_export_button.xml',
        ],
        'web.assets_backend': [
            'ml_worldwide-main/static/src/js/format_number.js',
            'ml_worldwide-main/static/src/js/mlw_dashboard.js',
            'ml_worldwide-main/static/src/js/ml_worldwide.js',
            # 'ml_worldwide-main/static/src/js/merge_row.js',
            'ml_worldwide-main/static/src/js/ml_worldwide_export.js',
            'ml_worldwide-main/static/src/css/tree_view.scss',
            'ml_worldwide-main/static/src/css/dashboard.scss',
            'ml_worldwide-main/static/src/css/section_and_note_backend.scss',
            'ml_worldwide-main/static/src/js/section_and_note_fields_backend.js',
        ],
    },
    "installable": True,
}