# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class RoomOrder(models.Model):
    _inherit = 'calendar.event'
    
    rooms = fields.Selection([('meeting_room', 'Meeting Room'),
                               ('conference_room', 'Conference Room')], string='Select Room', required=True)
    
    @api.constrains('rooms', 'start', 'stop')
    def _check_room_availability(self):
        for record in self:
            conflicting_records = self.search([
                ('id', '!=', record.id),
                ('rooms', '=', record.rooms),
                ('start', '<', record.stop),
                ('stop', '>', record.start),
            ])
            if conflicting_records:
                raise exceptions.UserError(_("This room has a meeting scheduled during this time. Please select another time."))

    def unlink(self):
        for record in self:
            if record.start < fields.Datetime.now():
                raise exceptions.UserError(_("Cannot delete past room bookings."))
        return super(RoomOrder, self).unlink()

    