# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-08-18

from odoo import api, fields, models

class TruckingBaseModel(models.Model):
    _inherit = "mltrucking.base"

    is_blocked = fields.Boolean(string="Hide the file", readonly=False,)

    customer_id = fields.Many2many(
        comodel_name="res.partner",
        relation="dms_access_file_hidden",
        column1="gid",
        column2="uid",
        string="Customer Users",
    )

    # ----------------------------------------------------------
    # Reading
    # ----------------------------------------------------------

    def read(self, fields=None, load=""):
        tmp_files = self.sudo()
        #print("Files ", tmp_files, )
        files = self[0]
        files = files - self[0]
        if tmp_files:
            for rec in tmp_files:
                # print("available_user_ids ", rec.available_user_ids, )
                if rec.is_blocked:
                    is_unhide = False
                    for uid in rec.available_user_ids:
                        if uid.id == self.env.uid:
                            is_unhide = True
                    if is_unhide:
                        files = files + rec
                else:
                    files = files + rec
                    #files.append(rec.id)

        #print("Filtered Files ", files, )
        #print("User id = ", self.env.user.id)
        return super(DMSFileRole, files).read(fields, load)   

    # ----------------------------------------------------------
    # Hidding Events
    # ----------------------------------------------------------

    @api.onchange("is_blocked")
    def _change_file_state(self):
        if self.is_blocked:
            self.hide()
        else:
            self.unhide()

    @api.onchange("available_user_ids")
    def _change_file_available_user_list(self):
        if not self.available_user_ids:
            self.write({"is_blocked": False})

    @api.onchange("directory_id")
    def _change_directory_id(self):
        if self.directory_id.name:
            # print("onchange ", self.directory_id)
            # print("onchange name", self.directory_id.name)
            dirName = self.directory_id.name.lower()
            if dirName.find('tuz') != -1:
                self.write({"is_blocked": True})

    def hide(self):
        self.update({'available_user_ids': [(self.env.uid)]})

    def unhide(self):
        self.write({"available_user_ids": None})




    # @api.depends("hidden_by")
    # def _compute_locked(self):
    #     for record in self:
    #         if record.available_user_ids.exists():
    #             record.update(
    #                 {
    #                     "is_blocked": True,
    #                 }
    #             )
    #         else:
    #             record.update({"is_blocked": False,})

    # @api.model
    # def _default_role_lines(self):
    #     default_user = self.env.ref("base.default_user", raise_if_not_found=False)
    #     default_values = []
    #     if default_user:
    #         for role_line in default_user.with_context(active_test=False).role_line_ids:
    #             default_values.append(
    #                 {
    #                     "role_id": role_line.role_id.id,
    #                     "date_from": role_line.date_from,
    #                     "date_to": role_line.date_to,
    #                     "is_enabled": role_line.is_enabled,
    #                 }
    #             )
    #     return default_values

    # @api.depends("role_line_ids.role_id")
    # def _compute_role_ids(self):
    #     for user in self:
    #         user.role_ids = user.role_line_ids.mapped("role_id")

    # @api.model
    # def create(self, vals):
    #     new_record = super(ResUsers, self).create(vals)
    #     new_record.set_groups_from_roles()
    #     return new_record

    # def write(self, vals):
    #     res = super(ResUsers, self).write(vals)
    #     self.sudo().set_groups_from_roles()
    #     return res

    # def _get_enabled_roles(self):
    #     return self.role_line_ids.filtered(lambda rec: rec.is_enabled)

    # def set_groups_from_roles(self, force=False):
    #     """Set (replace) the groups following the roles defined on users.
    #     If no role is defined on the user, its groups are let untouched unless
    #     the `force` parameter is `True`.
    #     """
    #     role_groups = {}
    #     # We obtain all the groups associated to each role first, so that
    #     # it is faster to compare later with each user's groups.
    #     for role in self.mapped("role_line_ids.role_id"):
    #         role_groups[role] = list(
    #             set(
    #                 role.group_id.ids
    #                 + role.implied_ids.ids
    #                 + role.trans_implied_ids.ids
    #             )
    #         )
    #     for user in self:
    #         if not user.role_line_ids and not force:
    #             continue
    #         group_ids = []
    #         for role_line in user._get_enabled_roles():
    #             role = role_line.role_id
    #             group_ids += role_groups[role]
    #         group_ids = list(set(group_ids))  # Remove duplicates IDs
    #         groups_to_add = list(set(group_ids) - set(user.groups_id.ids))
    #         groups_to_remove = list(set(user.groups_id.ids) - set(group_ids))
    #         to_add = [(4, gr) for gr in groups_to_add]
    #         to_remove = [(3, gr) for gr in groups_to_remove]
    #         groups = to_remove + to_add
    #         if groups:
    #             vals = {"groups_id": groups}
    #             super(ResUsers, user).write(vals)
    #     return True
