from odoo import models, fields, api

class FiniceDudction(models.Model):
    _name = "finice.deduction"

    date = fields.Date(string='Date',default=fields.Date.today(), readonly=True)
    month = fields.Date(string='Month')
    
    user_id = fields.Many2one('res.users',string="Made By",default=lambda self: self.env.user,readonly=True)
    salary_advance = fields.Float(string='Salary Advance')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    
    other_advance = fields.Float(string='Other Advance')
    vehicle_exp_share = fields.Float(string='Vechile Expense share')
    mobile_bill = fields.Float(string='Mobile Bill')
    other_deduction = fields.Float(string='Other Deduction')
   
    
    state = fields.Selection(string='state', selection=[('draft', 'Draft'), ('Aprroved', 'Aprroved'),], default="draft")



    @api.multi
    def approve_deduction(self):
       employee_id=self.employee_id
       
       contract_obj=self.env['hr.contract'].search([('employee_id','=',employee_id.id)])

       for line in contract_obj:
           line.write({
               'others':self.other_advance,
               'vehicle_exp_share':self.vehicle_exp_share,
               'mobile_bill':self.mobile_bill,
               'salary_advance':self.salary_advance,
           })
    
    
    
    
    
    

    