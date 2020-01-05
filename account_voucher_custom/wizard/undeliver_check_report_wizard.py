
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class checkUnDeliverWizard(models.TransientModel):
    _name = 'check.undeliver.wizard'
    _description = "un deliverd checks"

    #date_start = fields.Datetime('Start Date')
    #date_end = fields.Datetime('End Date')

    @api.multi
    def report_undeliver_detail(self, data=None):
        # data = {
        #     'ids': self.ids,
        #     'model': 'customer.check.line',
        # }

        return self.env.ref('account_voucher_custom.report_check_wizar').with_context(landscape=True).report_action(self, data=data)
        # return self.env.ref('account_voucher_custom.report_undeliver_qweb').report_action(self, data=data)

        # return self.env['report'].get_action(
        # self,'account_voucher_custom.report_undeliver_qweb',data=data)

    # def get_checkout(self, date_start):
    #     check_line = self.env['customer.check.line']
    #     check_ids = check_line.search([('check_status', '=', 'revise')])
    #     res = check_line.browse(check_ids)
    #     return res
