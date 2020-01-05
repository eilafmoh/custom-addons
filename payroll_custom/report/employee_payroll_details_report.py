from odoo import api, fields, models, _


class emp_reports_payroll(models.AbstractModel):
      _name = 'report.payroll_custom.report_payroll_details'

      def _get_emplayee_payroll_data(self,employee_ids,category_ids,salary_structure_ids):
            emps = self.env['report.payroll_custom.report_employees_view_p']._get_emplayee_payroll_data(employee_ids,category_ids,salary_structure_ids)
            #emp = [ name,category,job,employment_date,net_salary,id,qual,gross ]
            
            query = ''' select emp.id , p_l.code , p_l.amount
                from hr_employee emp 
                join hr_payslip p on p.employee_id = emp.id 
                join hr_payslip_line p_l on p_l.slip_id = p.id
                where emp.state = 'in_service' and p.id = (SELECT MAX(id) FROM hr_payslip WHERE employee_id = emp.id)'''

            return []
