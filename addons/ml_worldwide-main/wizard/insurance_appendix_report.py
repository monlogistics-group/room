# -*- coding: utf-8 -*-
# Created by Umbaa. 2023-06-05

import base64
from odoo import fields, models
from datetime import datetime, timedelta
from collections import defaultdict
import io

class InsuranceAppindexReport(models.AbstractModel):
    _name = 'report.ml_worldwide.insurance_appendix_report'
    _inherit = "report.report_xlsx.abstract"
    _translate = False

    def generate_xlsx_report(self, workbook, data, products):
        self = self.with_context(lang=self.env.user.lang)
        formatTitle = workbook.add_format({"font_size": 16, "bold": True})
        formatTitle.set_text_wrap()
        formatTitle.set_align("center")
        formatTitle.set_align("vcenter")
        
        formatDep = workbook.add_format(
            {
                "fg_color": "#ffffff",
                "font_size": 8,
                "border": 1,
                "align": "left",
                "valign": "vcenter",
                "text_wrap": True,
                "bold": False,
                "font": "Arial",
            }
        )
        formatDesc = workbook.add_format(
            {
                "font_size": 10,
                "border": 0,
                "align": "left",
                "valign": "vcenter",
                "text_wrap": True,
                "bold": True,
                "font": "Arial",
            }
        )
        
        headunpaidLeave = workbook.add_format(
            {
                "fg_color": "#8cd6d6",
                "font_size": 8,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "bold": True,
                "font": "Arial",
            }
        )
        
        formatColHeader = workbook.add_format(
            {"font_size": 13, "align": "center", "fg_color": "#f79646", "bold": True}
        )
        formatColHeader.set_border(style=1)
        formatColHeader.set_text_wrap()
        formatColHeader.set_align("center")
        formatColHeader.set_align("vcenter")
        formatRowText = workbook.add_format(
            {"font_size": 12, "align": "justify", "text_wrap": True}
        )
        formatRowText.set_border(style=1)
        formatNumb = workbook.add_format({"font_size": 12, "align": "right"})
        formatNumb.set_border(style=1)
        formatNumb.set_num_format("#,##0.00")
        formatSubCatTitle = workbook.add_format(
            {"font_size": 12, "align": "left", "fg_color": "#fcd5b4"}
        )
        formatSubCatTitle.set_border(style=1)
        formatSubCatNum = workbook.add_format(
            {"font_size": 12, "align": "right", "fg_color": "#fcd5b4"}
        )
        formatSubCatNum.set_border(style=1)
        formatSubCatNum.set_num_format("#,##0.00")

        formatCatTitle = workbook.add_format(
            {"font_size": 13, "align": "left", "bold": True, "fg_color": "#fabf8f"}
        )
        formatCatTitle.set_border(style=1)
        formatCatNum = workbook.add_format(
            {"font_size": 13, "align": "right", "bold": True, "fg_color": "#fabf8f"}
        )
        formatCatNum.set_border(style=1)
        formatCatNum.set_num_format("#,##0.00")

        # --------------------------------------------------------------------------------------------------------
        rw = 11
        index = 1

        date_from = fields.Datetime.from_string(data.get("from_date"))
        date_to = fields.Datetime.from_string(data.get("to_date"))

        date_from = date_from - timedelta(days=1)
        date_from = date_from.replace(hour=16, minute=0, second=0)
        date_to = date_to.replace(hour=15, minute=59, second=59)

        report_data = self.env["mlworldwide.freights"].search(
            [
                ("freights_routes_shipment.atd_date", ">=", date_from),
                ("freights_routes_shipment.atd_date", "<=", date_to),
                ("state_id", "=", "on-going")
            ]
        )

        # --------------------------------------------------------------------------------------------------------
        sheet = workbook.add_worksheet("Insurance appendix")

        sheet.merge_range("A6:M6", self.env.user.company_id.name , formatTitle)
        
        if self.env.user.company_id.logo:
            buf_image=io.BytesIO(base64.b64decode(self.env.user.company_id.logo))
            sheet.insert_image('B1', "logo.png", {'image_data': buf_image})
            
        sheet.merge_range(
            "A8:M8",
            "%s-р сарын " % str(datetime.now().month)+ "хавсралт-1",
            formatTitle,
        )
        
        sheet.merge_range(
            "A10:D10",
            "Хавсралт-1 хугацаа: " + date_from.strftime("%Y/%m/%d") + " - " + date_to.strftime("%Y/%m/%d"),
            formatDesc,
        )

        sheet.merge_range(rw, 0, rw+1, 0, u"Д/д", headunpaidLeave)
        sheet.merge_range(rw, 1, rw+1, 1, u"Ачааны REF дугаар", headunpaidLeave)
        sheet.merge_range(rw, 2, rw+1, 2, u"Ачаа, бараа бүтээгдэхүүний нэршил", headunpaidLeave)
        sheet.merge_range(rw, 3, rw+1, 3, u"Ачаа хөдөлсөн огноо ", headunpaidLeave)
        sheet.merge_range(rw, 4, rw+1, 4, u"Ачааны үнэ (үндсэн валют)", headunpaidLeave)
        sheet.merge_range(rw, 5, rw+1, 5, u"Ачаа тээвэрлэлт эхлэх цэг", headunpaidLeave)
        sheet.merge_range(rw, 6, rw+1, 6, u"Ачаа хүрэх эцсийн цэг", headunpaidLeave)

        rw += 2
        for tmp_data in report_data:
            atd = False
            for track in tmp_data.freights_routes_shipment:
                if atd == False:
                    atd = track.atd_date
            for shippment in tmp_data.freights_shipment:
                for package in shippment.shipment_packages:
                    sheet.write(rw, 0, rw-12, formatDep)
                    sheet.write(rw, 1, tmp_data.ref_num, formatDep)
                    sheet.write(rw, 2, package.name, formatDep)
                    sheet.write(rw, 3, atd.strftime("%Y/%m/%d"), formatDep)
                    sheet.write(rw, 4, str(shippment.cargo_price) + "(" + shippment.cargo_currency_id.name + ")", formatDep)
                    sheet.write(rw, 5, tmp_data.origin_point_id.name, formatDep)
                    sheet.write(rw, 6, tmp_data.destination_point_id.name, formatDep)
                    rw += 1

                
        rw += 4

        sheet.merge_range(9, 6, 9, 10, "Хавсралт-1 татсан өдөр" + " " + str(datetime.now().strftime("%Y-%m-%d")) , formatDesc)

        sheet.merge_range(2+rw, 3, 2+rw, 14, "Хавсралт-1 гаргасан:" + "  . . . . . . . . . . . . . . . . . . / " + self.env.user.name + " /", formatDesc)
        sheet.merge_range(3+rw, 3, 3+rw, 14, "Хянасан:" + "  . . . . . . . . . . . . . . . . . . /  /", formatDesc)