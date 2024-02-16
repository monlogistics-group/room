from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval, datetime


class WorldwideBaseCondition(models.Model):
    _name = "mlworldwide.base.condition"
    _description = "Model conditions for MLW"
    _order = 'model_id, name, id desc'
    
    name = fields.Char(string='Condidtion Name', translate=True, required=True)
    domain = fields.Text(default='[]', required=True)
    context = fields.Text(default='{}', required=True)
    sort = fields.Text(default='[]', required=True)
    model_id = fields.Selection(selection='_list_all_models', string='Model', required=True)
    active = fields.Boolean(default=True)
    
    action_id = fields.Many2one('ir.actions.actions', string='Action', ondelete='cascade',help="The menu action this filter applies to. ""When left empty the filter applies to all menus ""for this model.")
    user_id = fields.Many2one('res.users', string='User', ondelete='cascade', help="The user this filter is private to. When left empty the filter is public ""and available to all users.")
    
    @api.model
    def _list_all_models(self):
        self._cr.execute("SELECT model, name FROM ir_model ORDER BY name")
        return self._cr.fetchall()

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s (copy)', self.name))
        return super(WorldwideBaseCondition, self).copy(default)

    def _get_eval_domain(self):
        self.ensure_one()
        return safe_eval(self.domain, {
            'datetime': datetime,
            'context_today': datetime.datetime.now,
        })

    @api.model
    def _get_action_domain(self, action_id=None):
        
        if action_id:
            return [('action_id', 'in', [action_id, False])]
        return [('action_id', '=', False)]

    @api.model
    @api.returns('self', lambda value: value.id)
    def create_or_replace(self, vals):
        action_id = vals.get('action_id')
        return self.create(vals)

    _sql_constraints = [
        ('name_model_uid_unique', 'unique (name, model_id, user_id, action_id)', 'Filter names must be unique'),
    ]
    def _auto_init(self):
        result = super(WorldwideBaseCondition, self)._auto_init()
        tools.create_unique_index(self._cr, 'mlworldwide_base_condition_name_model_uid_unique_action_index',
            self._table, ['lower(name)', 'model_id', 'COALESCE(user_id,-1)', 'COALESCE(action_id,-1)'])
        return result