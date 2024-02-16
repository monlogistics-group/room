# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-25

import types
from odoo import api, fields, models

class TruckingDocumentData(models.Model):
    _name="mltrucking.document.data"    

    document=fields.Char()
       
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    version=fields.Char(string='Version')
    ref=fields.Char(string='Ref')
    date=fields.Char(string='Date')
    def company_phone(self):
        return self.env.company.phone
    phone=fields.Char(string='Phone Number', default=company_phone)
    address=fields.Char(string='Address')
    statement=fields.Char(string='Statement')
    company=fields.Char(string='Company')
    warning1=fields.Char(string='warning1')
    warning2=fields.Char(string='warning2')
    warning3=fields.Char(string='warning3')
    warning4=fields.Char(string='warning4')
    warning5=fields.Char(string='warning5')
    kmClause=fields.Char(string='kmClause')
    def company_name(self):
        return self.env.company.street
    companyAddress=fields.Char(string='companyAddress',default=company_name)
    sender=fields.Char(string='Sender Name')
    senderaddress=fields.Char(string='senderaddress')
    receiver=fields.Char(string='Receiver')
    receiveaddress=fields.Char(string='Receive address')
    freight=fields.Char(string='freight')
    size=fields.Char(string='Size')
    payment=fields.Char(string='Payment')
    quantity=fields.Char(string='Quantity')
    weight=fields.Char(string='Weight')
    chassisnumber=fields.Char(string='Chassis Number/Container')
    begintime=fields.Char(string='begintime')
    endtime=fields.Char(string='endtime')
    yes=fields.Char(string='Yes')
    end=fields.Char(string='End')
    begun=fields.Char(string='Begun')
    no=fields.Char(string='No')
    ready=fields.Char(string='Ready')
    invoice=fields.Char(string='invoice')
    sendercompany=fields.Char(string='sendercompany')
    employeename=fields.Char(string='Employee Name')
    employeephone=fields.Char(string='Phone')
    employeesignature=fields.Char(string='Autograph')
    carriercompany=fields.Char(string='carriercompany')
    drivername=fields.Char(string='Driver Name')
    driverphone=fields.Char(string='Phone')
    driversignature=fields.Char(string='Autograph')
    receivercompany=fields.Char(string='receivercompany')
    receivername=fields.Char(string='Name')
    receiverphone=fields.Char(string='Phone')
    receiversignature=fields.Char(string='Autograph')
    note=fields.Char(string='Note')
    warning=fields.Char(string='Warning')
    
    