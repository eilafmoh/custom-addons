
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError


class account_move(models.Model):
    _inherit = 'account.move'
    _rec_name = 'amount'

    check_line_id = fields.Many2one(
        string="Check Line",
        comodel_name="customer.check.line",
        readonly=True,
    )

    payment_id = fields.Many2one(
        string="Payment",
        comodel_name="payment.report.action",
        readonly=True,
    )

    on_creadit_check_line = fields.Many2one(
        string="Check Line",
        comodel_name="oncreadit.check.line",
        readonly=True,
    )


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    onc_check_id = fields.Many2one('oncreadit.check')
