
from odoo import api, fields, models, _
import re


class gross_net(models.AbstractModel):
    _name = 'report.payroll_custom.report_employees_view_p'

    def _get_emplayee_payroll_data(self,employee_ids,category_ids,salary_structure_ids):
        if employee_ids:
            employees = self.env['hr.employee'].browse(employee_ids)
        else:
            employees = self.env['hr.employee'].search([('state','=','in_service')])

        if category_ids:
            employees = employees.search([('category_ids','in',category_ids)])
        if salary_structure_ids:
            employees = employees.search([('structure_id','in',salary_structure_ids)])

        quals = self.env['hr.employee.qualification'].search([])
        qual_list = [ [rec.employee_id.id , rec.qualification_id.name] for rec in quals ]
        new_list = dict()
        for line in qual_list:
            if line[0] in new_list:
                new_list[line[0]].append(line[1])
            else:
                new_list[line[0]] = [line[1]]

        emps = [[emp.name ,[cat.name for cat in emp.category_ids] , emp.job_id.name , emp.employment_date ,emp.contract_id.net_salary ,emp.id] for emp in employees]
        
        for qual in new_list:
            for e in emps:
                if qual == e[5]:
                    e.append(new_list[qual])
        
        for e in emps:
            if len(e) < 7:
                e.append(' ')

        up_emps = self._get_gross(employee_ids,emps)
        return up_emps


    def _get_gross(self,employee_ids,emps):
        query = ''' select emp.id , p_l.amount
                from hr_employee emp 
                join hr_payslip p on p.employee_id = emp.id 
                join hr_payslip_line p_l on p_l.slip_id = p.id
                where emp.state = 'in_service' and p_l.code = 'GROSS' and p.id = (SELECT MAX(id) FROM hr_payslip WHERE employee_id = emp.id)'''

        self.env.cr.execute(query)
        emp_gross_data = self.env.cr.dictfetchall()
        for rec in emp_gross_data:
            for emp in emps:
                if rec['id'] == emp[5]:
                    emp.append(rec['amount'])

        for e in emps:
            if len(e) < 8:
                e.append('0')
        return emps
        

    # def _get_employee_data(self,employee_ids,category_ids,salary_structure_ids,qualifications,status,date_appointment,birthday,emp_phone,email):
    # 	emp_conditions = qual_select = qual_join = ""
        
    # 	employees =  ",".join(str(i) for i in employee_ids)
    # 	categories =  ",".join(str(i) for i in category_ids)
    # 	struct =  ",".join(str(i) for i in salary_structure_ids)

    # 	if employee_ids:
    # 		emp_conditions+= '''
    # 			where emp.id in ''' +('''(''' + employees +''')''' )+''' ''' 
                
    # 	if salary_structure_ids:
    # 		if employee_ids:
    # 			emp_conditions+= '''
    #     		AND emp.structure_id in ''' +('''(''' + struct +''')''' )+''' '''  
    # 		else:
    #     		emp_conditions+= '''
    #     		where emp.structure_id in ''' +('''(''' + struct +''')''' )+''' '''

    # 	# if category_ids:
    #  #    	if employee_ids:
    #  #    		emp_conditions += ''' AND emp.category_id in ''' +('''(''' + categories +''')''' )+''' '''
    #  #    	else:
    #  #    		emp_conditions += ''' where emp.category_id in ''' +('''(''' + categories +''')''' )+''' '''
            
    #     	# qual_select += ", emp_cat.name as category"
    #     	# qual_join += ''' join hr_employee_category emp_cat on emp.job_id = emp.id '''

    # 	if qualifications:
    #     	qual_select += ", qual.name as qual"
    #     	qual_join += ''' join hr_employee_qualification em_qual on em_qual.employee_id = emp.id
    #         join hr_qualification qual on em_qual.qualification_id = qual.id '''
            
    # 	if status:
    #         qual_select += ", hj.name as job"
    #         qual_join += ''' join hr_job hj on emp.job_id = hj.id '''
            
    # 	if date_appointment:
    #         qual_select += ", emp.employment_date as employment_date"

    # 	if birthday:
    #         qual_select += ", emp.birthday as birthday"

    # 	if emp_phone:
    #         qual_select += ", emp.mobile_phone as phone"

    # 	if email:
    #         qual_select += ", emp.work_email as email"
        
    # 	query = '''
    #         select emp.id , emp.name as name '''+qual_select+'''  
    #         from hr_employee emp
    #         '''+qual_join+'''
    #         '''+emp_conditions+'''
    #     '''

    # 	self.env.cr.execute(query)
    # 	employees_data = self.env.cr.dictfetchall()
    # 	#employees_data = self.env.cr.fetchall()
    # 	print('---------------------- employees_data ',employees_data)
    # 	da = self._get_emplayee_payroll_data(employees_data)
    # 	return da


    # # @api.model
    # # def _get_report_values(self, docids,data=None):
    # #     self.model = self.env.context.get('active_model')
    # #     docs = self.env[self.model].browse(self.env.context.get('active_id',[]))

    # #     year = data['form'].get('year')
    # #     month = data['form'].get('month')
    # #     employee_ids = data['form'].get('employee_ids')
    # #     category_ids = data['form'].get('category_ids')
    # #     salary_structure_ids = data['form'].get('salary_structure_ids')

    # #     qualifications = data['form'].get('qualifications')
    # #     status = data['form'].get('status')
    # #     date_appointment = data['form'].get('date_appointment')
    # #     birthday = data['form'].get('birthday')
    # #     emp_phone = data['form'].get('emp_phone')
    # #     email = data['form'].get('email')


    # #     emp_ids = re.findall('\d+', employee_ids)
    # #     cat_ids = re.findall('\d+', category_ids)
    # #     struc_ids = re.findall('\d+', salary_structure_ids)

    # #     employees_data = self._get_employee_data(emp_ids,cat_ids,struc_ids,qualifications,status,date_appointment,birthday,emp_phone,email)
    # #     self._get_emplayee_payroll_data(emp_ids,cat_ids,struc_ids)
    # #     return {
    # #         'doc_ids': data['ids'],
    # #         'doc_model': data['model'],
    # #         'employees_data': employees_data,
    # #         'docs': docs,
    # #         'qualifications':qualifications,
    # #         'status':status,
    # #         'date_appointment':date_appointment,
    # #         'birthday':birthday,
    # #         'emp_phone':emp_phone,
    # #         'email':email,
    # #     }
