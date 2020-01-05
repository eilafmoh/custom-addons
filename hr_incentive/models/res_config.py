# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################

from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'


    incentive_double_validation = fields.Selection([
        ('one_step', 'Confirm Incentive in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm Incentive')
        ], string="Levels of Approvals", default='one_step',
        help="Provide a double validation mechanism for purchases")

    incentive_double_validation_amount = fields.Monetary(string='Incentive Double validation amount', default=5000,
        help="Minimum amount for which a double validation is required")




class HrConfigSettings(models.TransientModel):
    _inherit  = 'res.config.settings'

    company_id = fields.Many2one ('res.company', string='Company', required=True , default=lambda self: self.env.user.company_id)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
        help='Utility field to express amount currency')
    incentive_double_validation = fields.Selection(related='company_id.incentive_double_validation', string="Incentive Levels of Approvals *")
    incentive_double_validation_amount = fields.Monetary(related='company_id.incentive_double_validation_amount', string="Incentive Double validation amount *", currency_field='company_currency_id')


