from odoo import http
from odoo.http import request
from odoo.tools import SQL


def queries(cr, table, ids):
    # ruleid: odoo-sql-injection
    cr.execute(f"SELECT id FROM {table}")
    # ruleid: odoo-sql-injection
    cr.execute("SELECT id FROM %s" % table)
    # ruleid: odoo-sql-injection
    cr.execute("SELECT id FROM " + table)
    # ruleid: odoo-sql-injection
    cr.execute("SELECT id FROM {}".format(table))
    query = f"DELETE FROM {table}"
    # ruleid: odoo-sql-injection
    cr.execute(query)
    # ok: odoo-sql-injection
    cr.execute("SELECT id FROM res_partner WHERE id IN %s", (tuple(ids),))
    # ok: odoo-sql-injection
    cr.execute(SQL("SELECT id FROM %s", SQL.identifier(table)))


class Shop(http.Controller):
    @http.route("/shop/public", auth="public")
    def public(self):
        # ruleid: odoo-sudo-in-public-route
        return request.env["product.template"].sudo().search([])

    @http.route("/shop/user", auth="user")
    def user(self):
        # ok: odoo-sudo-in-public-route
        return request.env["product.template"].sudo().search([])
