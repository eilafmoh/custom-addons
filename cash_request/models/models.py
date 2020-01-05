# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class exchange_item(models.Model):
    _name = 'exchange.item'
    _description = 'Exchange Items'

    name = fields.Char(string="Name" , required=True)
    department_ids = fields.Many2many(
        string="Departments",
        comodel_name="hr.department",
        relation="exchange_dep_rel",
        column1="exchange_id",
        column2="dep_id",
    )


class payment_schedule(models.Model):
    _name = 'payment.schedule'
    _description = 'Payment Schedule'

    date = fields.Date(string="Date", required=True,)
    amount = fields.Float(string="Amount", required=True,)
    payment_type = fields.Selection(
        string="Payment Type",
        selection=[
                ('cash', 'Cash'),
                ('check', 'Check'),
        ],default='cash',required=True,
    )
    order_id = fields.Many2one(
        string="Order",
        comodel_name="cash.order",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        domain="[('type', 'in', ['cash' , 'bank'])]",
    )
    check_number = fields.Char(string="Check number", )

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string="Analytic Account")

    company_id = fields.Many2one('res.company' , default=lambda self: self.env.user.company_id)

    account_id = fields.Many2one("account.account", string="Account" , domain="[('company_id' , '=' ,company_id)]")
    description = fields.Text(string="Description",)
    # move_id = fields.Many2one(
    #     string="Journal Entry",
    #     comodel_name="account.move",
    #     readonly=True,
    # )

    state = fields.Selection(
        string="State",
        selection=[('draft', 'Draft'), ('confirm', 'wating for Department Manager'), ('department', 'Waiting For General Manger'),
                              ('general', 'Waiting for Finacial Manager'),
                              ('financial', 'waiting for Auditor'),
                              ('auditor', 'Wating for Payment'),
                              ('paid', 'Paid'), ('refuse', 'Refused')],related="order_id.state"
    )