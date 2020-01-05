from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class Revise_report(models.AbstractModel):
    _name = 'report.account_voucher_custom.report_undeliver_qweb'
    _description = 'Undeliverd Checks/installment'

    def get_checkout(self):
        checks_obj = self.env['customer.check.line']
        checks = checks_obj.search([('check_status', '=', 'revise')])
        #res = checks_obj.browse(checks)
        return checks

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))

        #rm_act = self.with_context(data['form'].get('used_context', {}))
        data_res = self.get_checkout()
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            #'data': data['form'],
            'docs': docs,
            #'time': time,
            'get_checkout': data_res,
        }

        render_model = 'account_voucher_custom.report_undeliver_qweb'
        return self.env['report'].render(render_model, docargs)
