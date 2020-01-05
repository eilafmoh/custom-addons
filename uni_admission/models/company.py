# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class res_company(models.Model):
    _inherit = "res.company"

    general_account_id = fields.Many2one(
        'account.account',
        domain=lambda self: [('user_type_id.id', '=', self.env.ref(
        'account.data_account_type_revenue').id)],
        help="Income account for general admission registration"
    )

    special_account_id = fields.Many2one('account.account',
                                         domain=lambda self: [('user_type_id.id', '=', self.env.ref(
                                             'account.data_account_type_revenue').id)],
                                         help="Income account for general admission registration",)
    income_journal_id = fields.Many2one(
        string="Income Journal",
        comodel_name="account.journal",
        domain="[('type', '=', 'sale')]",
    )

    bank_account_id = fields.Many2one(
        'account.account',
        domain=lambda self: [('user_type_id.id', '=', self.env.ref(
        'account.data_account_type_liquidity').id)],
        help="Income account for general admission registration",
        required=True
    )
