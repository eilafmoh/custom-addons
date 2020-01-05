
from odoo import api, fields, models
from datetime import datetime

# class MigrationWizard3(models.TransientModel):
# 	_name = 'bank.wizard'

# 	def process_migrate(self,data):
# 		ids = data.get('active_ids', [])
# 		mig_data = self.env['res.bank.migration'].browse(ids)
		
# 		for rec in mig_data:
# 			self.env['res.bank'].create({
# 				'name': rec.name,
# 			})

# 		mig_data.unlink()


class MigrationWizard4(models.TransientModel):
	_name = 'acc.bank.wizard'

	def process_migrate(self,data):
		ids = data.get('active_ids', [])
		mig_data = self.env['bank.migration'].browse(ids)
		
		for rec in mig_data:
			employee = self.env['hr.employee'].search([('name','=',rec.name)])
			for rmp in employee:
				print('-------- rmp ',rmp.name)
			if employee.bank_account_id:
				employee.bank_account_id.write({
					'company_id':1
				})
				rec.unlink()
				# pass
				# partner_id = self.env['res.partner'].search([('name','=',rec.name)])
				# if partner_id:
				# 	print('------------- partner ',partner_id)
				# 	em.write({
				# 		'partner_id': partner_id.id
				# 	})
				# else:
				# 	emp_partner_id = self.env['res.partner'].create({
				# 		'name': rec.name,
				# 		'supplier': True,	
				# 		'customer': False,						
				# 	})
				# 	em.write({
				# 		'partner_id': emp_partner_id.id
				# 	})

				# con_id = self.env['hr.contract'].search([
				# 	('employee_id','=', em.id),
				# 	('state','=', 'open')
				# ])
				# em.write({
				# 	'structure_id': con_id.struct_id.id if con_id else ''
				# })
			# else:
			# 	if rec.account_bank:
			# 		if employee:
			# 			print('---------------- employee ',employee.name)
			# 			account_bank = self.env['res.bank'].search([('name','=',rec.account_bank)])
					
			# 			bank_account_id = self.env['res.partner.bank'].create({
			# 				'acc_number': rec.ipan,
			# 				'bank_id': account_bank.id,
			# 				'partner_id': employee.partner_id.id
			# 			})
			# 			employee.write({
			# 				'bank_account_id':bank_account_id.id
			# 			})
						
			# 	rec.unlink()


class MigrationWizard0(models.TransientModel):
	_name = 'contype.wizard'

	def process_migrate(self,data):
		ids = data.get('active_ids', [])
		mig_data = self.env['contype.migration'].browse(ids)
		
		for rec in mig_data:
			employee = self.env['hr.employee'].search([('name','=',rec.name)])
			con_id = self.env['hr.contract'].search([
				('employee_id','=', employee.id),
			])
			con_id.write({
				'type_id':self.env['hr.contract.type'].search([('name','=',rec._type)]).id,
				# 'date_start':rec.date
			})

		mig_data.unlink()	
# # class MigrationWizard2(models.TransientModel):
# #     _name = 'migration.migration.wizard'
# #     _description = 'Migration Wizard'

# #     def process_migrate(self,data):
# #         ids = data.get('active_ids', [])
# #         mig_data = self.env['migration.migration'].browse(ids)
		
# #         for emp in mig_data:
# #             employee = self.env['hr.employee'].search([('identification_id','!=',False),('identification_id','=',emp.emp_identity)])
# #             if employee:
# #                 relation = ''
# #                 if emp.relation == 'Wife':
# #                     relation = 'wife'
# #                 elif emp.relation == 'Son':
# #                     relation = 'son'
# #                 elif emp.relation == 'Daughter':
# #                     relation = 'daughter'
# #                 elif emp.relation == 'Wife Without Maternity':
# #                     relation = 'wife_without_maternity'
# #                 emp_f = self.env['hr.employee.family'].create({
# #                     'name': emp.name,
# #                     'employee_id': employee.id,
# #                     'relation': relation,
# #                     'birthday': emp.birthday,
# #                     'company_id': employee.department_id.company_id.id,
# #                     'relation_identity':emp.relation_identity
# #                 })
# #                 if emp_f:
# #                     emp.unlink()
# #             else:
# #                 pass


# class MigrationWizard5(models.TransientModel):
#     _name = 'ins.wizard'

#     def process_migrate(self,data):
#         ids = data.get('active_ids', [])
#         mig_data = self.env['insurance.migration'].browse(ids)
		
#         for rec in mig_data:
#             document = self.env['hr.insurance.document'].search([('code','=',rec.doc_num)])
#             category = self.env['hr.insurance.category'].search([('code','=',rec.categ_code)])
#             relation = ''
#             if rec.emp_insur == 'Wife' or rec.emp_insur == 'wife':
#                 relation = 'wife'
#             elif rec.emp_insur == 'Employee' or rec.emp_insur == 'employee':
#                 relation = 'employee'
#             elif rec.emp_insur == 'Mother' or rec.emp_insur == 'mother':
#                 relation = 'mother'
#             elif rec.emp_insur == 'Son' or rec.emp_insur == 'son':
#                 relation = 'son'
#             elif rec.emp_insur == 'Daughter' or rec.emp_insur == 'daughter':
#                 relation = 'daughter'
#             elif rec.emp_insur == 'Wife Without Maternity' or rec.emp_insur == 'wife_without_maternity':
#                 relation = 'wife_without_maternity'

#             rel = self.env['hr.relation.category'].search([('relation','=',relation)])
#             bank_account_id = self.env['hr.insurance.price'].create({
#                 'insurance_document_id': document.id,
#                 'insurance_category_id': category.id,
#                 'price': rec.price,
#                 'relation':rel.id,
#             })
		   
#         mig_data.unlink()

# class MigrationWizard6(models.TransientModel):
#     _name = 'employee.insurance.wizard'

#     def process_migrate(self,data):
#         ids = data.get('active_ids', [])
#         mig_data = self.env['insurance.migration'].browse(ids)
		
#         for rec in mig_data:
#             employee = self.env['hr.employee'].search([('emp_code','=',rec.emp_code)])
#             rel = self.env['hr.relation.category'].search([('relation','=',relation)])
#             bank_account_id = self.env['hr.insurance.price'].create({
#                 'insurance_document_id': document.id,
#                 'insurance_category_id': category.id,
#                 'price': rec.price,
#                 'relation':rel.id,
#             })
		   
#         mig_data.unlink()