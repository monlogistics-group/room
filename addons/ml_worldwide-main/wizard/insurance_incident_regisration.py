# -*- coding: utf-8 -*-
# Created by Umbaa. 2023-06-07

import base64
from odoo import fields, models
from datetime import datetime, timedelta
from collections import defaultdict
import io

class InsuranceIncidentRegisration(models.AbstractModel):
    _name = 'report.ml_worldwide.insurance_incident_regisration'
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
                "italic": True,
                "font": "Arial italic",
            }
        )
        
        formatColHeader = workbook.add_format(
            {"font_size": 8, "align": "center", "fg_color": "#f79646", "bold": True,"italic": True,}
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

        report_data = self.env["mlworldwide.freights"].search(
            [
                ("state_id", "=", "arrived"),
                ("has_insurance", "=", True),
                ("freights_shipment", "!=", [data.get("shipment_id")])
            ]
        )

        # --------------------------------------------------------------------------------------------------------
        sheet = workbook.add_worksheet("Insurance register")

        sheet.merge_range("A6:M6", self.env.user.company_id.name , formatTitle)
        
        if self.env.user.company_id.logo:
            buf_image=io.BytesIO(base64.b64decode(self.env.user.company_id.logo))
            sheet.insert_image('B1', "logo.png", {'image_data': buf_image})
            
        sheet.merge_range(
            "A8:M8",
            "\"Монложистикс ворлдвайд\" даатгалын тохиолдын дуудлага өгөхөд бөглөх хүснэгт:",
            formatTitle,
        )

        sheet.merge_range(rw, 0, rw+1, 0, u"Д/д", headunpaidLeave)
        sheet.merge_range(rw, 1, rw+1, 1, u"Харилцагчийн нэр", headunpaidLeave)
        sheet.merge_range(rw, 2, rw+1, 2, u"Ref дугаар", headunpaidLeave)
        sheet.merge_range(rw, 3, rw+1, 3, u"Чингэлэг/ вагон дугаар", headunpaidLeave)
        sheet.merge_range(rw, 4, rw+1, 4, u"Гааль хийгдсэн терминалийн нэр", headunpaidLeave)

        sheet.merge_range(rw, 5, rw, 7, u"Даатгалын тохиолдол", headunpaidLeave)
        sheet.write(rw+1, 5, u"Огноо", headunpaidLeave)
        sheet.write(rw+1, 6, u"Барааны нэр", headunpaidLeave)
        sheet.write(rw+1, 7, u"Тайлбар /хохирлын талаар бичих/", headunpaidLeave)

        sheet.merge_range(rw, 8, rw, 9, u"Тээврийн мэргэжилтэн", headunpaidLeave)
        sheet.write(rw+1, 8, u"ТМ-н нэр", headunpaidLeave)
        sheet.write(rw+1, 9, u"Утас", headunpaidLeave)

        sheet.merge_range(rw, 10, rw+1, 10, u"Үзлэг хийгдэх газар", headunpaidLeave)
        
        sheet.merge_range(rw, 11, rw, 13, u"Мандал даатгал үзлэг хийх ажилтны мэдээлэл", headunpaidLeave)
        sheet.write(rw+1, 11, u"Огноо", headunpaidLeave)
        sheet.write(rw+1, 12, u"Ажилтны нэр ", headunpaidLeave)
        sheet.write(rw+1, 13, u"Хүлээлтын хугацаа", headunpaidLeave)

        sheet.merge_range(rw, 14, rw, 16, u"Тээврийн мэдээлэл", headunpaidLeave)
        sheet.write(rw+1, 14, u"Тээврийн хэрэгслийн төрөл/FCL,FTL,WGN,AIR гм/", headunpaidLeave)
        sheet.write(rw+1, 15, u"Аль улсаас", headunpaidLeave)
        sheet.write(rw+1, 16, u"Ирсэн огноо", headunpaidLeave)

        rw += 2
        
        for tmp_data in report_data:
            for shippment in tmp_data.freights_shipment:
                for insurance in shippment.insurance_ids:
                    sheet.write(rw, 0, rw-12, formatDep)
                    sheet.write(rw, 1, tmp_data.customer_id.name, formatDep)
                    sheet.write(rw, 2, tmp_data.ref_num, formatDep)
                    sheet.write(rw, 3, shippment.track_number, formatDep)
                    sheet.write(rw, 4, insurance.reimbursement_packages.terminal, formatDep)
                    sheet.write(rw, 5, tmp_data.freights_routes_shipment[len(tmp_data.freights_routes_shipment)-1].ata_date.strftime("%Y/%m/%d"), formatDep)
                    sheet.write(rw, 6, insurance.reimbursement_packages.name, formatDep)
                    sheet.write(rw, 7, insurance.description, formatDep)
                    sheet.write(rw, 8, insurance.reimbursement_employee.name, formatDep)
                    sheet.write(rw, 9, insurance.reimbursement_employee.mobile_phone, formatDep)
                    sheet.write(rw, 10, insurance.reimbursement_packages.terminal, formatDep)
                    ##### Insurance agentiin bugluh 3 nud uldeene  
                    sheet.write(rw, 14, tmp_data.freigths_type, formatDep)
                    sheet.write(rw, 15, tmp_data.origin_point_id.country.name, formatDep)
                    sheet.write(rw, 16, tmp_data.freights_routes_shipment[len(tmp_data.freights_routes_shipment)-1].ata_date.strftime("%Y/%m/%d"), formatDep)
                    rw += 1

        rw += 4

        sheet.merge_range(9, 6, 9, 10, "даатгалын тохиолдын дуудлага өдөр" + " " + str(datetime.now().strftime("%Y-%m-%d")) , formatDesc)

        sheet.merge_range(2+rw, 3, 2+rw, 14, "даатгалын тохиолдын дуудлага гаргасан:" + "  . . . . . . . . . . . . . . . . . . / " + self.env.user.name + " /", formatDesc)
        sheet.merge_range(3+rw, 3, 3+rw, 14, "Хянасан:" + "  . . . . . . . . . . . . . . . . . . /  /", formatDesc)