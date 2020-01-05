
from odoo import api, fields, models, _
from datetime import datetime

months = [('1' , 'January') , ('2' , 'February'),('3','March'),
    ('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),
    ('9','September'),('10','October'),('11','November'),('12','December')]

class hr_employee_reports_wizard(models.TransientModel):
    _name = 'hr.employee.reports.wizard'
    _description = "Employees Reports "

    year = fields.Char('Year', default=lambda self: str(datetime.now().year),required=True)
    month = fields.Selection(months , default=lambda self: str(datetime.now().month) , required=True)
    employee_ids =fields.Many2many("hr.employee",string="Employee name")

    category_ids = fields.Many2many('hr.employee.category' , string ='Category')
    salary_structure_ids =fields.Many2many('hr.payroll.structure',string=" Salary Structure")
    #status_ids = fields.Many2many('hr.job','Status')

    qualifications = fields.Boolean('Qualifications')
    status = fields.Boolean('status')
    date_appointment = fields.Boolean('Date of Appointment')
    birthday = fields.Boolean('Date of Birth')
    emp_phone = fields.Boolean('Telephone N⁰')
    email = fields.Boolean('Email')



    @api.multi
    def print_report(self):
        data = {
            'ids': self.env.context.get('active_ids', []),
            'model': self.env.context.get('active_model', 'ir.ui.menu'),
            'form': {
                'year': self.year,
                'month':self.month,
                'employee_ids': self.employee_ids,
                'category_ids': self.category_ids,
                'salary_structure_ids': self.salary_structure_ids,
                'qualifications': self.qualifications,
                'status': self.status,
                'date_appointment': self.date_appointment,
                'birthday': self.birthday,
                'emp_phone': self.emp_phone,
                'email': self.email,
            },
        }

        return self.env.ref('payroll_custom.report_employees_report').report_action(self, data=data)
        

