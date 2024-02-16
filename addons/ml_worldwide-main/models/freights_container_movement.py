from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class FreightContainerMovements(models.Model):
    _name = 'freights.container.movement'
    _description = 'Container movement'

    freights_id = fields.One2many('mlworldwide.freights','freight_id')
    container_num = fields.Many2one(comodel_name='freights.containers', string="Container")
    container_type = fields.Many2one(related="container_num.container_type_id")

    orderDate = fields.Date(string='Order Date')
    return_border_date = fields.Date(string='On Border Date')
    return_coming_date = fields.Date(string='Order Coming Date')
    return_type = fields.Char(string='Return type')
    pages = fields.Char(string='Pages', default='1,4,6')
    cargoName = fields.Char(string='cargoName', default='Контейнеры большой грузоподъемности порожные 99310000')
    senderCertificateNumber = fields.Char(string='MLW Certificate', default='2685949')
    cargoType = fields.Char(string='cargoType',default='Контейнер')
    packageQty = fields.Char(string='packageQty', default='1')
    sender = fields.Char(string='sender',default='Монложистикс Ворлдвайд ООО Международная транспортно-экспедиторская компания Г-жа Эрдэнэбилэг Тел: 976-7011-5454, Факс: 976-7011-1616 Н.Сувд-Эрдэнэ')
    loader = fields.Char(string='loader', default='Отправитель')
    weightCalculation = fields.Char(string='weightCalculation', default='На стандартных весах')
    uplata = fields.Char(string='Uplata')
    document = fields.Char(string='Document')
    information = fields.Char(string='Information')
    receiver = fields.Char(string='Receiver')
    receiver_phone = fields.Char(string='Receiver Phone')
    polucha = fields.Char(string='Polucha')
    container_number = fields.Char(string='Container Number')
    sha_num = fields.Char(string='SHA Number')
    shipment = fields.Many2one('freights.shipments')
    stations= fields.Many2many(comodel_name='freight.stations')

    # container_type COC state 
    # 1. Confirmed Zahialga batalgaajsan
    # 2. On going Teeverlelt
    # 3. At Terminal Terminal deer huleej avsan
    # 4. In Consignee Hand Huleen avagch avch garsan
    # 5. Empty return Hooson butsaalt
    # 6. Empty loaded Butsalt achigdsan
    # 7. Empty At Border Butsaal hil deer irsen
    # 8. Empty Atd Border Butsaalt hilees garsan
    # 8. Empty return closed Butsaalt duussan
    # container_type SOC state
    # 1. Confirmed Zahialga batalgaajsan
    # 2. On going Teeverlelt
    # 3. At Terminal Terminal deer huleej avsan
    # 4. In Consignee Hand Huleen avagch avch garsan
    # 4. In terminal Talbaid
    # 5. In rent Tureeslesen
    # 6. Sold zarsan
    # container_type Transfer state
    # 1. Confirmed Zahialga batalgaajsan
    # 2. On going Teeverlelt
    # 3. At Terminal Terminal deer huleej avsan
    # 4. In Consignee Hand Huleen avagch avch garsan
    # 5. On tarnsfer 
    # 6. Transferred shiljuulsen
    #container yard char field name many2one
    state_id = fields.Selection(selection=[
            ('confirmed','Confirmed'),
            ('ongoing', 'Ongoing'),
            ('terminal', 'At Terminal'),
            ('in-consignee', 'In consignee'),
            ('at-cy', 'At CY'),
            ('in-terminal', 'In Terminal'),
            ('empty-return', 'Empty return'),
            ('empty-loaded', 'Empty loaded'),
            ('empty-at-border', 'Empty at border'),
            ('empty-atd', 'Empty atd border'),
            ('empty-returnc', 'Empty return closed'),
            ('in-rent', 'In rent'),
            ('sold', 'Sold'),
            ('on-transfer', 'On transfer'),
            ('transferred', 'Transferred'),
        ],
        domain=lambda self: [('state_type.name', 'in', self.compute_state_types())],
        default='confirmed')
    state_id1 = fields.Selection(selection=[
            ('confirmed','Confirmed'),
            ('ongoing', 'Ongoing'),
            ('terminal', 'At Terminal'),
            ('in-consignee', 'In consignee'),
            ('empty-return', 'Empty return'),
            ('empty-loaded', 'Empty loaded'),
            ('empty-at-border', 'Empty at border'),
            ('empty-atd', 'Empty atd border'),
            ('empty-returnc', 'Empty return closed'),
            
        ],
        domain=lambda self: [('state_type.name', 'in', self.compute_state_types())],
        default='ongoing')
    
    state_id2 = fields.Selection(selection=[
            ('confirmed','Confirmed'),
            ('ongoing', 'Ongoing'),
            ('terminal', 'At Terminal'),
            ('in-consignee', 'In consignee'),
            ('at-cy', 'At CY'),
            ('in-rent', 'In rent'),
            ('sold', 'Sold'),
        ],
        domain=lambda self: [('state_type.name', 'in', self.compute_state_types())],
        default='ongoing')

    state_id3 = fields.Selection(selection=[
            ('confirmed','Confirmed'),
            ('ongoing', 'Ongoing'),
            ('terminal', 'At Terminal'),
        
            ('in-terminal', 'In Terminal'),
            ('on-transfer', 'On transfer'),
            ('transferred', 'Transferred'),
        ],
        domain=lambda self: [('state_type.name', 'in', self.compute_state_types())],
        default='confirmed')
    
    # container_rail2rail = fields.Many2one(comodel_name='freight.container.details', string="Rail to rail")
    naklad_created = fields.Datetime(string="PDF created date")
    naklad_created_user = fields.Many2one(comodel_name='hr.employee', string="")
    
    taras_id = fields.Many2one(comodel_name='freights.taras', string="Tara", domain=[('active', '=', True)])
    
    from_data=fields.Many2one(comodel_name='freights.points' ,string="From")
    to_data=fields.Many2one(comodel_name='freights.points' ,string="To")
    terminal_date =fields.Datetime(string="Received date ", help="")
    free_days=fields.Integer(string="Free days")

    terminal_data=fields.Many2one(comodel_name='freights.terminal' ,string="Terminal")
    terminal=fields.Many2one(comodel_name='freights.terminal' ,string="Terminal")
    employee = fields.Many2one('hr.employee', string="Employee")    
    out_employee=fields.Many2one('hr.employee', string="Employee")    
    exit_date=fields.Datetime(string="Exit Date")

    terminal_date_consig =fields.Datetime(string="Received date ", help="")
    terminal_consig=fields.Many2one(comodel_name='freights.terminal' ,string="Terminal")

    empty_ret=fields.Datetime(string="Empty return date")
    ret_employee = fields.Many2one('hr.employee', string="Employee")    
    arrive_border_date=fields.Datetime(string="Arrive border date ")
    out_border_date=fields.Datetime(string="Out border date")

    demmurage_end_point_date=fields.Datetime(string="Demmurage end point date")
    transfer_date=fields.Datetime(string="Transfer date")
    transfer_agent=fields.Many2one(comodel_name="res.partner", string="Transfer agent", help="Захиалга өгсөн менежерийн нэр")
    transfer_employee=fields.Many2one('hr.employee', string="Employee")    

    rent_date=fields.Datetime(string="Rent date")
    renter=fields.Many2one(comodel_name="res.partner", string="Renter", help="Захиалга өгсөн менежерийн нэр")
    to_rent=fields.Char(string="To rent")
    rent_cost=fields.Float(string="Rent cost")

    container_yard = fields.Many2one('container.yard', string= 'Container yard')

    sold_date=fields.Datetime(string="Sold date")
    sold_cost=fields.Float(string="Sold cost")
    buyer=fields.Many2one(comodel_name="res.partner", string="Buyer", help="Захиалга өгсөн менежерийн нэр")

    place=fields.Char(string='place')
    is_show_details = fields.Boolean()
    state1=fields.Boolean()
    state2=fields.Boolean()
    state3=fields.Boolean()
    state4=fields.Boolean()
    show_field=fields.Boolean()
    show_field2=fields.Boolean()
    in_terminal=fields.Boolean()
    out_terminal=fields.Boolean()
    in_consignee_terminal=fields.Boolean()
    in_consig=fields.Boolean()
    rent_bool=fields.Boolean()
    sold_bool=fields.Boolean()
    sold_boolean=fields.Boolean()
    rent_boolean=fields.Boolean()
    move_bool=fields.Boolean()
    move_boolean=fields.Boolean()
    transfer_bool=fields.Boolean()
    transfer_boolean=fields.Boolean()
    show_field3=fields.Boolean()
    empty_boolean=fields.Boolean()

    @api.onchange('container_num')
    def _onchange_container_num(self):
       
        if self.container_type.name == 'COC':
            self.state1= True
            self.state2= False
            self.state3 = True
            self.transfer_bool = True
            self.state4 = False
        if self.container_type.name == 'Transfer':
            self.state4 = True
            self.state1= False
            self.state2= False
            self.state3 = True 
            self.show_field2 =True 
        if self.container_type.name == 'SOC':
            self.state2= True
            self.state1= False
            self.state3 = True
            self.state4 = False
            self.show_field2 = True
            self.transfer_bool = True
            self.out_terminal = True
    
    def action_out_terminal(self):
        self.ensure_one()
        self.out_terminal= True
        self.show_field3 = True
        
    # pdf gargana
    def make_pdf(self):
        arr = [{ 'data' :self.sender, 'text' : 'sender'}, 
        {'data': self.senderCertificateNumber,'text' : 'senderCertificateNumber'}, 
        {'data':self.polucha, 'text' : 'polucha'}, 
        {'data':self.return_type, 'text': 'return type'},
        {'data' : self.document , 'text' : 'document'}, 
        {'data':self.cargoName, 'text' : 'cargo Name'}, 
        {'data':self.cargoType, 'text': 'Cargo Type'}, 
        {'data':self.loader, 'text' : 'loader'}, 
        {'data':self.information, 'text': 'information'}, 
        {'data':self.receiver, 'text': 'receiver'}, 
        {'data': self.receiver_phone, 'text': 'receiver Phone'}, 
        {'data' :self.sha_num, 'text': 'Sha Number'}, 
        {'data':self.uplata, 'text': 'uplata'}, 
        {'data' : self.weightCalculation, 'text': 'weightCalculation'}, 
        {'data' :self.pages, 'text': 'Pages'}, 
        {'data':self.return_border_date, 'text': 'Return Border Rate'},
        {'data':self.return_coming_date, 'text': 'Return Coming Date'}]
        for rec in range(len(arr)):
            if not arr[rec]['data']:
                raise ValidationError("You must fill {} field".format(arr[rec]['text']))
        if len(self.stations) == 0:
            raise ValidationError('You must fill stations field')

        report = self.env['ir.actions.report']._get_report_from_name('ml_worldwide-main.mlworldwide_generate_pdf_using_img')
        report.report_type = 'qweb-pdf'
        pdf = report.report_action(self, config = False)
        return pdf 

    def action_in_terminal(self):
        self.ensure_one()
        self.show_field = True
        self.in_terminal = True
        # self.show_field2 = True
    
    def actoin_in_consignee(self):
        self.ensure_one()
        self.in_consig = True
        self.in_consignee_terminal = True

    def empty_return_container(self):
        self.ensure_one()
        self.empty_boolean = True
        self.show_field2 = True
        self.state_id1 = 'empty-return'

    def action_move(self):
        self.ensure_one()
        self.move_boolean = True
    
    def action_rent(self):
        self.ensure_one()
        self.rent_bool = True
        self.rent_boolean = True
    
    def action_transfer(self):
        self.ensure_one()
        self.transfer_boolean = True

    def show_container_details(self):
        self.is_show_details = not self.is_show_details
        
    def action_sold(self):
        self.ensure_one()
        self.sold_bool =True
        self.sold_boolean=True

    @api.onchange('container_yard')   
    def onchange_container_yard(self):
        if self.container_yard != False:
            self.state_id2 = 'at-cy'

    @api.onchange('transfer_date','transfer_agent','transfer_employee') 
    def onchange_transfer_dae(self):
        if self.transfer_date != False and self.transfer_agent != False and self.transfer_employee != False :
            self.state_id3 = 'on-transfer'

    @api.onchange('rent_date','renter','rent_cost')   
    def onchange_rent(self):
        if self.rent_date != False and self.renter != False and self.rent_cost != False:
            self.state_id2 = 'in-rent'

    @api.onchange('sold_date','buyer','sold_cost')
    def onchange_sold(self):
        if self.sold_date != False and self.buyer != False and self.sold_cost != False:
            self.state_id2 = 'sold'


    @api.onchange('empty_ret','ret_employee')
    def onchange_empty_ret(self):
        if self.empty_ret != False and self.ret_employee != False:
            self.state_id1 = 'empty-loaded'

    @api.onchange('arrive_border_date')
    def onchange_arrive_border(self):
        if self.arrive_border_date != False :
            self.state_id1 = 'empty-at-border'

    @api.onchange('out_border_date')
    def onchange_out_border(self):
        if self.out_border_date != False :
            self.state_id1 = 'empty-atd'

    @api.onchange('terminal_date','terminal')
    def onchange_terminal_date(self):
        # if self.state_id ==  self.state_id1
        if self.terminal.id:
            if self.terminal.id != False and self.terminal_date !=False:
                if self.container_type.name == 'COC':
                    self.state_id1 = 'terminal' 
                if self.container_type.name == 'SOC':
                    self.state_id2 = 'terminal' 
                if self.container_type.name == 'Transfer':
                    self.state_id3 = 'ongoing' 

    @api.onchange('employee','exit_date')
    def onchange_exit_date(self):
        if self.exit_date != False and self.employee != False:
            if self.container_type.name == 'COC':
                self.state_id1 = 'in-consignee'
            if self.container_type.name == 'Transfer':
                self.state_id3 = 'terminal'
    
    @api.onchange('terminal_date_consig','terminal_consig')   
    def onchange_terminal_consig(self):
        if self.terminal_consig.id:
            if self.terminal_consig.id != False and self.terminal_date_consig != False:
                if self.container_type.name == 'COC':
                    self.state_id1 = 'terminal'  
                if self.container_type.name == 'SOC':
                    self.state_id2 ='in-consignee'
                if self.container_type.name == 'Transfer':
                    self.state_id3 = 'in-terminal' 
            

    @api.onchange('state_id2')
    def onchange_state_id2(self):
        a = self.state_id2
        self.state_id = a
        if self.state_id2 == 'confirmed':
            self.out_terminal = True
            self.show_field2 = True
            self.in_consignee_terminal = True
            self.rent_bool = True
            self.sold_bool = True
            self.move_bool = True
            self.in_terminal = False
        if self.state_id2 == 'ongoing':       
            self.out_terminal = True
            self.in_consignee_terminal = True
            self.show_field2 = True
            self.rent_bool = True
            self.sold_bool = True
            self.move_bool = True
            self.in_terminal = False
        if self.state_id2 == 'terminal':    
            self.out_terminal = True
            self.in_consignee_terminal = False
            self.rent_bool = False
            self.sold_bool = False
            self.move_bool = False
            self.in_terminal = True
        if self.state_id2 == 'in-consignee':    
            self.out_terminal = True
            self.show_field2 = True
            self.in_consignee_terminal = True
            self.rent_bool = True
            self.sold_bool = True
            self.move_bool = True
            self.in_terminal = True
        if self.state_id2 == 'in_rent':    
            self.out_terminal = True
            self.show_field2 = True
            self.in_consignee_terminal = True
            self.rent_bool = True
            self.sold_bool = True
            self.move_bool = True
            self.in_terminal = True
        if self.state_id2 == 'sold':    
            self.out_terminal = True
            self.show_field2 = True
            self.in_consignee_terminal = True
            self.rent_bool = True
            self.sold_bool = True
            self.move_bool = True
            self.in_terminal = True

    

    @api.onchange('state_id1')   
    def onchange_state_id1(self): 
        a = self.state_id1
        self.state_id = a
        if self.state_id1 == 'confirmed':
            self.out_terminal = True            
            self.in_consignee_terminal = True          
            self.in_terminal = False
            self.show_field2 = False
        if self.state_id1 == 'ongoing':
            self.in_consignee_terminal = True    
            self.in_terminal = False
            self.show_field2 = False
            self.out_terminal = True
        if self.state_id1 == 'terminal':             
            self.in_terminal = True
            self.in_consignee_terminal = True
            self.out_terminal = False
            self.show_field2 = False
        if self.state_id1 == 'in-consignee':    
            self.out_terminal = True       
            self.in_consignee_terminal = False
            self.in_terminal = True
            self.show_field2 = False
        if self.state_id1 == 'empty-return':    
            self.out_terminal = True         
            self.in_consignee_terminal = True
            self.in_terminal =True
        if self.state_id1 == 'empty-loaded':    
            self.out_terminal = True           
            self.in_consignee_terminal = True
            self.in_terminal =True
        if self.state_id1 == 'empty-at-border':    
            self.out_terminal = True        
            self.in_consignee_terminal = True
            self.in_terminal =True
        if self.state_id1 == 'empty-atd':    
            self.out_terminal = True
            self.in_consignee_terminal = True
            self.in_terminal =True
        if self.state_id1 == 'empty-returnc': 
            self.in_terminal =True
            self.show_field2=True
        
        
    
    @api.onchange('state_id3')  
    def onchange_state_id3(self):   
        a = self.state_id3
        self.state_id = a
        if self.state_id3 == 'confirmed':
            # self.out_terminal = False          
            self.in_consignee_terminal = True          
            self.transfer_bool = False
        if self.state_id3 == 'ongoing':
            self.out_terminal = False
            self.in_consignee_terminal = True 
            self.transfer_bool = False
            self.in_terminal = True
        if self.state_id3 == 'terminal':             
            self.in_consignee_terminal = True
            self.in_consignee_terminal = False
            self.out_terminal = True
            self.transfer_bool = False
        if self.state_id3 == 'in-consignee':    
            self.in_terminal = False
            self.in_consignee_terminal = True
            self.out_terminal = False
            self.transfer_bool = True
       

        # if self.state_id1 == 'on-transfer':    
        #     self.out_terminal = True
        #     self.in_consignee_terminal = True
        #     self.in_terminal =True
        # if self.state_id1 == 'transferred': 
        #     self.in_terminal =True
        #     self.show_field2=True
    
    # terminal huleej avsan udur, terminal, huleej avsan hun
    # Huleen avagch avch garsan udur, Huleen avagch, gargasn hun
    # hooson achigdsan ognoo , achuulsan hun
    # Hil deer ochson ognoo
    # hilees garsan ognoo
    # demmurage end point-d ochson ognoo
    # shiljuulsen ognoo, shiljuulj avsan baiguullaga, shiljuulsen hun
    # Tureeslesen ognoo, Hend tureeslesen, Hen tureeslesen, Tureeslesen une
    # Zarsan ognoo, Hend zarsan, Hedeer zarsan, Hen zarsan
    # Bairlal (Teevert yavaa bol point, Talbai deer baigaa bol terminal esvel consignee)