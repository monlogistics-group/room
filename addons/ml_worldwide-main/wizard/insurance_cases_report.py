# -*- coding: utf-8 -*-
# Created by Umbaa. 2023-06-07

import base64
from odoo import fields, models
from datetime import datetime, timedelta
from collections import defaultdict
import io

class InsuranceCasesReport(models.AbstractModel):
    _name = 'report.ml_worldwide.insurance_cases_report'
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
        index = 1

        date_from = fields.Datetime.from_string(data.get("from_date"))
        date_to = fields.Datetime.from_string(data.get("to_date"))

        date_from = date_from - timedelta(days=1)
        date_from = date_from.replace(hour=16, minute=0, second=0)
        date_to = date_to.replace(hour=15, minute=59, second=59)

        report_data = self.env["mlworldwide.freights"].search(
            [
                ("freights_routes_shipment.ata_date", ">=", date_from),
                ("freights_routes_shipment.ata_date", "<=", date_to),
                ("state_id", "=", "arrived"),
                ("has_insurance", "=", True),
                ("freights_shipment.insurance_ids", "!=", [])
            ]
        )

        # --------------------------------------------------------------------------------------------------------
        sheet = workbook.add_worksheet("Insurance cases")

        sheet.merge_range("A6:M6", self.env.user.company_id.name , formatTitle)
        
        if self.env.user.company_id.logo:
            buf_image=io.BytesIO(base64.b64decode(self.env.user.company_id.logo))
            sheet.insert_image('B1', "logo.png", {'image_data': buf_image})
            
        sheet.merge_range(
            "A8:M8",
            "%s-р сарын " % str(datetime.now().month)+ "Даатгал тохиолдол",
            formatTitle,
        )
        
        sheet.merge_range(
            "A10:D10",
            "Даатгал тохиолдол хугацаа: " + date_from.strftime("%Y/%m/%d") + " - " + date_to.strftime("%Y/%m/%d"),
            formatDesc,
        )

        sheet.merge_range(rw-2, 0, rw-1, 12, u"Даатгал тохиолдол", formatColHeader)
        sheet.merge_range(rw, 0, rw+1, 0, u"Д/д", headunpaidLeave)
        sheet.merge_range(rw, 1, rw+1, 1, u"Дугаар", headunpaidLeave)
        sheet.merge_range(rw, 2, rw+1, 2, u"Харилцагчийн нэр", headunpaidLeave)
        sheet.merge_range(rw, 3, rw+1, 3, u"Ref дугаар", headunpaidLeave)
        sheet.merge_range(rw, 4, rw+1, 4, u"Чингэлэг дугаар", headunpaidLeave)
        sheet.merge_range(rw, 5, rw+1, 5, u"Огноо", headunpaidLeave)
        sheet.merge_range(rw, 6, rw+1, 6, u"Барааны нэр", headunpaidLeave)
        sheet.merge_range(rw, 7, rw+1, 7, u"Үл тохирол", headunpaidLeave)
        sheet.merge_range(rw, 8, rw+1, 8, u"Тайлбар /хохирлын талаар бичих/", headunpaidLeave)
        sheet.merge_range(rw, 9, rw+1, 9, u"ТМ-н нэр", headunpaidLeave)
        sheet.merge_range(rw, 10, rw+1, 10, u"И-мэйл", headunpaidLeave)
        sheet.merge_range(rw, 11, rw+1, 11, u"Утас", headunpaidLeave)
        sheet.merge_range(rw, 12, rw+1, 12, u" Даатгал үзлэг хийсэн огноо", headunpaidLeave)

        sheet.merge_range(rw-2, 13, rw-1, 13, u"Ажлын урсал", formatColHeader)
        sheet.merge_range(rw, 13, rw+1, 13, u"Төлөв/сонгох/", headunpaidLeave)
        
        sheet.merge_range(rw-2, 14, rw-1, 16, u"Даатгагч руу шилжүүлсэн эсэх", formatColHeader)
        sheet.merge_range(rw, 14, rw+1, 14, u"Огноо", headunpaidLeave)
        sheet.merge_range(rw, 15, rw+1, 15, u"Үгүй бол шалтгаан бичих", headunpaidLeave)
        sheet.merge_range(rw, 16, rw+1, 16, u"Хүлээлтын хугацаа", headunpaidLeave)

        sheet.merge_range(rw-2, 17, rw-1, 25, u"Санхүүгийн мэдээлэл", formatColHeader)
        sheet.merge_range(rw, 17, rw+1, 17, u"Нэхэмжлэлийн дүн", headunpaidLeave)
        sheet.merge_range(rw, 18, rw+1, 18, u"НТ-н дүн", headunpaidLeave)
        sheet.merge_range(rw, 19, rw+1, 19, u"Зөрүү дүн", headunpaidLeave)
        sheet.merge_range(rw, 20, rw+1, 20, u"НТ товьч тайлбар", headunpaidLeave)
        sheet.merge_range(rw, 21, rw+1, 21, u"НТ-с татгалзсан гэрээний заалт", headunpaidLeave)
        sheet.merge_range(rw, 22, rw+1, 22, u"Олгосон огноо", headunpaidLeave)
        sheet.merge_range(rw, 23, rw+1, 23, u"Хүлээлтын хугацаа", headunpaidLeave)
        sheet.merge_range(rw, 24, rw+1, 24, u"Статус /сонгох/", headunpaidLeave)
        sheet.merge_range(rw, 25, rw+1, 25, u"Хаагдсан огноо", headunpaidLeave)

        rw += 2

        for tmp_data in report_data:
            for shippment in tmp_data.freights_shipment:
                for insurance in shippment.insurance_ids:
                    sheet.write(rw, 0, rw-12, formatDep)
                    sheet.write(rw, 1, tmp_data.ref_num, formatDep)
                    sheet.write(rw, 2, tmp_data.customer_id.name, formatDep)
                    sheet.write(rw, 3, tmp_data.ref_num, formatDep)
                    sheet.write(rw, 4, shippment.track_number, formatDep)
                    sheet.write(rw, 5, tmp_data.freights_routes_shipment[len(tmp_data.freights_routes_shipment)-1].ata_date.strftime("%Y/%m/%d"), formatDep)
                    sheet.write(rw, 6, insurance.reimbursement_packages.name, formatDep)
                    sheet.write(rw, 7, insurance.short_desc, formatDep)
                    sheet.write(rw, 8, insurance.description, formatDep)
                    sheet.write(rw, 9, insurance.reimbursement_employee.name, formatDep)
                    sheet.write(rw, 10, insurance.reimbursement_employee.work_email, formatDep)
                    sheet.write(rw, 11, insurance.reimbursement_employee.mobile_phone, formatDep)
                    sheet.write(rw, 12, insurance.insurance_date, formatDep)
                    
                    sheet.write(rw, 13, insurance.state_id, formatDep)
                    sheet.write(rw, 14, insurance.transfer_date, formatDep)
                    sheet.write(rw, 15, insurance.transfer_note, formatDep)
                    sheet.write(rw, 16, insurance.waiting_day, formatDep)
                    sheet.write(rw, 17, insurance.claim_amount, formatDep)
                    sheet.write(rw, 18, insurance.reimbursement_amount, formatDep)
                    sheet.write(rw, 19, insurance.diff_amount, formatDep)
                    sheet.write(rw, 20, insurance.reimbursement_note, formatDep)
                    sheet.write(rw, 21, insurance.contract_note, formatDep)
                    sheet.write(rw, 22, insurance.reimbursement_date, formatDep)
                    sheet.write(rw, 23, insurance.waiting_day, formatDep)
                    sheet.write(rw, 24, insurance.status_id, formatDep)
                    sheet.write(rw, 25, insurance.closed_date, formatDep)
                    rw += 1

        rw += 4

        sheet.merge_range(9, 6, 9, 10, "Даатгал тохиолдол татсан өдөр" + " " + str(datetime.now().strftime("%Y-%m-%d")) , formatDesc)

        sheet.merge_range(2+rw, 3, 2+rw, 14, "Даатгал тохиолдол гаргасан:" + "  . . . . . . . . . . . . . . . . . . / " + self.env.user.name + " /", formatDesc)
        sheet.merge_range(3+rw, 3, 3+rw, 14, "Хянасан:" + "  . . . . . . . . . . . . . . . . . . /  /", formatDesc)