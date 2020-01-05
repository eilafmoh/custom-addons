

from odoo import models, fields, api , _
from odoo.exceptions import  ValidationError


class HrContractCustom(models.Model):
    _inherit="hr.contract"

    degree_id = fields.Many2one("hr.degree", string="Degree", domain="[('job_id','=',job_id)]")
    state = fields.Selection([
		('draft', 'New'),
		('open', 'Open'),
		('ended', 'Ended'),
		('terminated', 'Terminated'),
		('resigned', 'Resigned'),
        ('promoted', 'Promoted'),
	], string="State", default='draft')

    @api.onchange('employee_id','struct_id','degree_id','date_start')
    def change_struc(self):
        self.employee_id.write({
            'structure_id': self.struct_id.id,
            'degree_id': self.degree_id.id,
            'employment_date': self.date_start,
            })
        if self.degree_id:
            self.wage = self.degree_id.amount


