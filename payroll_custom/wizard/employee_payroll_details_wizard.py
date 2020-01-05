
from odoo import api, fields, models, _
from datetime import datetime

import xlwt
from xlsxwriter.workbook import Workbook
from io import StringIO , BytesIO
import base64

months = [('1' , 'January') , ('2' , 'February'),('3','March'),
	('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),
	('9','September'),('10','October'),('11','November'),('12','December')]


class hr_employee_reports_wizard_payroll(models.TransientModel):
	_name = 'hr.employee.reports.wizard.payroll'
	_description = "Employees Payroll Reports "

	date = fields.Date(string='Date',default=lambda self: str(datetime.now()) ,required=True)
	employee_ids =fields.Many2many("hr.employee",string="Employee name")
	category_ids = fields.Many2many('hr.employee.category' , string ='Category')
	salary_structure_ids =fields.Many2many('hr.payroll.structure',string=" Salary Structure")

	def print_report(self ,data):
		data['form'] = self.read(['date','employee_ids','category_ids','salary_structure_ids'])[0]
		date = data['form'].get('year')
		employee_ids = data['form'].get('employee_ids')
		category_ids = data['form'].get('category_ids')
		salary_structure_ids = data['form'].get('salary_structure_ids')

		workbook= xlwt.Workbook(encoding="UTF-8")
		worksheet= workbook.add_sheet('Payroll Report')
		header_style_base = xlwt.easyxf(
			'font: bold True;align: horizontal center , vertical center')
		header_style = xlwt.easyxf(
			'font: bold True;align: horizontal center , vertical center')
		style = xlwt.easyxf('align: horizontal center , vertical center;')
		style2 = xlwt.easyxf('align: horizontal left , vertical center;')
		date_format = xlwt.XFStyle()
		date_format.num_format_str = 'DD - MM - YYYY' 

		worksheet.row(1).height = 256*3
		worksheet.row(2).height = 256*2
		worksheet.row(3).height = 256*4

		worksheet.col(1).width = 256*8
		worksheet.col(2).width = 256*8
		worksheet.col(3).width = 256*30
		worksheet.col(4).width = 256*30
		worksheet.col(5).width = 256*20
		worksheet.col(6).width = 256*20
		worksheet.col(9).width = 256*20
		worksheet.col(11).width = 256*20
		worksheet.col(12).width = 256*20
		worksheet.col(13).width = 256*20
		worksheet.col(14).width = 256*20
		worksheet.col(15).width = 256*20
		worksheet.col(16).width = 256*30
		worksheet.col(17).width = 256*20
		worksheet.col(18).width = 256*30
		worksheet.col(19).width = 256*20
		worksheet.col(20).width = 256*20
		worksheet.col(21).width = 256*30
		worksheet.col(22).width = 256*30
		worksheet.col(23).width = 256*20
		worksheet.col(24).width = 256*30

		data = self.env['report.payroll_custom.report_payroll_details']._get_emplayee_payroll_data(employee_ids,category_ids,salary_structure_ids)
		
		worksheet.write_merge(1, 1 , 3 ,7 ,'Academic  Staff' , header_style_base)
		worksheet.write_merge(2, 2 , 3 ,7 , 'As at : ' + str(self.date.month) + '  , ' + str(self.date.year) , header_style_base)

		worksheet.write(3, 1 , 'N⁰  PT' , header_style)
		worksheet.write(3, 2 , 'N⁰  FT ' , header_style)
		worksheet.write(3, 3 , 'Employee' , header_style)
		worksheet.write(3, 4 , 'Qualifications' , header_style)
		worksheet.write(3, 5 , 'Status' , header_style)
		worksheet.write(3, 6 , 'Date of Appointment' , header_style)
		worksheet.write(3, 7 , 'Gross' , header_style)
		worksheet.write(3, 8 , 'Basic' , header_style)
		worksheet.write(3, 9 , 'Cost Of Living' , header_style)
		worksheet.write(3, 10 , 'Housing' , header_style)
		worksheet.write(3, 11 , 'Transportation' , header_style)
		worksheet.write(3, 12 , 'Research and Books' , header_style)
		worksheet.write(3, 13 , 'Outsourcing' , header_style)
		worksheet.write(3, 14 , 'Office Hours' , header_style)
		worksheet.write(3, 15 , 'Rare Specialties' , header_style)
		worksheet.write(3, 16 , 'Cordination of Program' , header_style)
		worksheet.write(3, 17 , 'Head of Division' , header_style)
		worksheet.write(3, 18 , 'Additional Responsibilities' , header_style)
		worksheet.write(3, 19 , 'Exceptional Allowance' , header_style)
		worksheet.write(3, 20 , 'Medical Allowance' , header_style)
		worksheet.write(3, 21 , 'Social Security Insurance' , header_style)
		worksheet.write(3, 22 , 'Health Insurance' + '\n' + '(Company Contribution)' , header_style)
		worksheet.write(3, 23 , 'Stamp Duty' , header_style)
		worksheet.write(3, 24 , 'Personal Income Tax' , header_style)		
		worksheet.write(3, 25 , 'Net Salary' , header_style)

		# row = 4
		# col = 3
		# full_count = 0
		# part_count = 0
		# total_net = 0.0
		# for rec in data:
		# 	#rec = [name,category,job,employment_date,net_salary,id,qual,gross]
		# 	worksheet.write (row, col    , rec[0] ,style2)
		# 	worksheet.write (row, col + 1, rec[6] ,style)
		# 	worksheet.write (row, col + 2, rec[2] ,style2)
		# 	worksheet.write (row, col + 3, rec[3] ,date_format)
		# 	worksheet.write (row, col + 4, rec[7] ,style)
		# 	worksheet.write (row, col + 5, rec[4] ,style)
		# 	if rec[1] == ['Part Time']:
		# 		part_count += 1
		# 		worksheet.write (row, col - 2 , '1',style )
				
		# 	elif rec[1] == ['Full Time']:
		# 		full_count += 1
		# 		worksheet.write (row, col - 1 , '1' ,style)	

		# 	total_net += rec[4]
		# 	row += 1

		# worksheet.write (row , col - 2, part_count ,header_style)
		# worksheet.write (row , col - 1, full_count ,header_style)
		# worksheet.write (row , col + 5, total_net ,header_style)

		_file = StringIO()
		_file = BytesIO()

		workbook.save(_file)

		export_id = self.env['excel.extended.report'].create({
			'excel_file': base64.encodestring(_file.getvalue()),
			'file_name': 'payroll_details_report.xls'
			})

		_file.close()

		return{
			'view_mode': 'form',
			'res_id': export_id.id,
			'res_model': 'excel.extended.report',
			'view_type': 'form',
			'type': 'ir.actions.act_window',
			'target': 'new',
			}

