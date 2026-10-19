from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    # ruleid: odoo-sql-constraints-deprecated
    _sql_constraints = [("ref_unique", "unique(ref)", "Reference must be unique.")]

    # ruleid: odoo-group-operator-renamed
    score = fields.Integer(group_operator="avg")
    # ok: odoo-group-operator-renamed
    rank = fields.Integer(aggregator="avg")

    # ruleid: odoo-api-multi-one-removed
    @api.multi
    def action_multi(self):
        return True

    # ruleid: odoo-api-multi-one-removed
    @api.one
    def action_one(self):
        return True

    # ok: odoo-api-multi-one-removed
    @api.model
    def action_model(self):
        return True

    # ruleid: odoo-fields-view-get-removed
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        return super().fields_view_get(view_id, view_type, toolbar, submenu)

    # ruleid: odoo-name-get-deprecated
    def name_get(self):
        return [(partner.id, partner.ref) for partner in self]

    def action_env(self):
        # ruleid: odoo-record-env-shortcuts-deprecated
        self._cr.execute("SELECT 1")
        # ok: odoo-record-env-shortcuts-deprecated
        self.env.cr.execute("SELECT 1")

        # ruleid: odoo-record-env-shortcuts-deprecated
        return self._context.get("lang")


# ok: odoo-name-get-deprecated
def name_get():
    return []
