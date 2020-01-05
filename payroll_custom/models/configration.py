from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    loan_acc = fields.Many2one('account.account' , 'Employees Loan Account')
    end_serv_acc = fields.Many2one('account.account' , 'End Of Service Account')
    over_time_acc = fields.Many2one('account.account' , 'Overtime Account')


class HrConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one ('res.company', string='Company', required=True 
        , default=lambda self: self.env.user.company_id)
    loan_acc = fields.Many2one('account.account' , 'Employees Loan Account'
        ,related='company_id.loan_acc', readonly=False)
    end_serv_acc = fields.Many2one('account.account' , 'End Of Service Account' 
        ,related='company_id.end_serv_acc', readonly=False)
    over_time_acc = fields.Many2one('account.account' , 'Overtime Account' 
        ,related='company_id.over_time_acc', readonly=False)

