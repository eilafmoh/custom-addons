
from odoo import api,models, _

class ReportLunchorder(models.AbstractModel):
    _name = 'report.account_voucher_custom.customer_check_report'
    #_inherit = 'report.abstract_report'
    _template = 'account_voucher_custom.customer_check_report'
    #_wrapped_report_class = FolioReport
