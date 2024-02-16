from odoo import api, fields, models, _

class FreightEmployeesRole(models.Model):
    _name = 'freights.employee.role'
    _description = 'Freight Employee Role'
    _rec_name = 'employee'

    role_name = fields.Char(help="Contributor role")
    
    employee = fields.Many2one('hr.employee', string="Contributor", required=True)

    def name_get(self):
        result = []
        for rec in self:
            if rec.role_name:
                result.append((rec.id, '%s - %s' % (str(rec.role_name), str(rec.employee.name))))
            else:
                result.append((rec.id, '%s' % (str(rec.employee.name))))
        return result