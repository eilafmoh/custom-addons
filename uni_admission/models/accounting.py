from odoo import api, fields, models, _


class account_config_settings(models.TransientModel):
    _inherit = 'account.config.settings'

    general_account_id = fields.Many2one(
        'account.account',
        related='company_id.general_account_id',
        domain=lambda self: [('user_type_id.id', '=', self.env.ref(
            'account.data_account_type_revenue').id)],
        help="Income account for general admission registration",
        # required=True
    )

    special_account_id = fields.Many2one(
        'account.account',
        related='company_id.special_account_id',
        domain=lambda self: [('user_type_id.id', '=', self.env.ref(
            'account.data_account_type_revenue').id)],
        help="Income account for general admission registration",
        # required=True
    )

    bank_account_id = fields.Many2one(
        'account.account',
        related='company_id.bank_account_id',
        domain=lambda self: [('user_type_id.id', '=', self.env.ref(
            'account.data_account_type_liquidity').id)],
        help="Income account for general admission registration",
        # required=True
    )

    income_journal_id = fields.Many2one(
        related='company_id.income_journal_id',
        string="Income Journal",
        comodel_name="account.journal",
        domain="[('type', '=', 'sale')]",
        # required=True
    )


class account_move(models.Model):
    _inherit = 'account.move'

    payment_id = fields.Many2one(
        string="Related Pyament",
        comodel_name="uofk.payment",
        readonly=True,
    )
