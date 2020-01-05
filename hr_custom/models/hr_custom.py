# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################
from odoo import models, fields, api


class HrConfigSettings(models.TransientModel):
   
    _inherit = 'res.config.settings'

    company_id = fields.Many2one ('res.company', string='Company', required=True , default=lambda self: self.env.user.company_id)
    hr_journal_id = fields.Many2one('account.journal' , 'HR Journal' , related='company_id.hr_journal_id')
    analytic_id = fields.Many2one('account.analytic.account' , 'HR Analytic account ' , related='company_id.analytic_id')
    payable_acc = fields.Many2one('account.account' , 'Employees Payable Account')
    end_serv_acc = fields.Many2one('account.account' , 'End Of Service Account' ,related='company_id.end_service_acc')

class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_journal_id = fields.Many2one ('account.journal', 'HR Journal')
    analytic_id = fields.Many2one ('account.analytic.account', 'HR Analytic account ')
    payable_acc = fields.Many2one('account.account' , 'Employees Payable Account')
    end_service_acc = fields.Many2one('account.account' , 'End Of Service Account')
