# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _


class Year(models.Model):
    _name = 'uni.year'
    _rec_name = 'code'
    _description = 'Academic Year'
    _inherit = ['mail.thread']

    code = fields.Char("Code", required=True)
    order = fields.Char('Order', required=True)
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        (
            'code_unique',
            'UNIQUE(code)',
            _('The code must be unique')
        ),
    ]
