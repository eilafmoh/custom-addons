# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime
import re
#from hijri_converter import convert


class MigrationWizard(models.TransientModel):
    _name = 'migration.wizard'
    _description = 'Migration Wizard'

    def process_migrate(self,data):
        ids = data.get('active_ids', [])
        mig_data = self.env['hr.migration'].browse(ids)

        for emp in mig_data:

            company = self.env['res.company'].search([('name','=',emp.company_id)])
            emp_dept = self.env['hr.department'].search([('code','=',int(emp.department_code))])
            country = self.env['res.country'].search([('name','=',emp.country)])


            new_employee = self.env['hr.employee'].create({
                'name': str(emp.first_name if emp.first_name else '')  + ' ' + str(emp.second_name if emp.second_name else '') + ' ' + str(emp.third_name if emp.third_name else '') + ' ' + str(emp.last_name if emp.last_name else '') ,
                'first_name': emp.first_name,
                'second_name': emp.second_name,
                'third_name': emp.third_name,
                'last_name': emp.last_name,
                'work_email': emp.work_email,
                'department_id': emp_dept.id,
                'state': emp.state,
                'marital': emp.marital,
                'religion': emp.religion,
                'company_id': company.id,
                # 'start_date': datetime.strptime(str(emp.start_date), "%Y-%m-%d").strftime('%d/%m/%Y'),
                # 'sinid_date': datetime.strptime(str(emp.sinid_date), "%Y-%m-%d").strftime('%d/%m/%Y'),
                # 'birthday': datetime.strptime(str(emp.birthday), "%Y-%m-%d").strftime('%d/%m/%Y'),
                'visa_expire': emp.visa_expire,
                'sinid': emp.sinid,
                'emp_code': emp.emp_code,
                'identification_id': emp.identification_id,
                'passport_id': emp.passport_id,
                'mobile_phone': emp.mobile_phone,
                'country_id': country.id,
                'work_location': emp.work_location,
                'work_phone': emp.work_phone
                })

            new_employee.user_id.login = emp.emp_code
            new_employee.user_id.password = emp.emp_code

        mig_data.unlink()


            
class DeptMigrationWizard(models.TransientModel):
    _name = 'dept.migration.wizard'
    _description = 'Dept Migration Wizard'

    @api.multi
    def process_migrate(self,data):
        ids = data.get('active_ids', [])
        mig_data = self.env['hr.dept.migration'].browse(ids)

        for rec in mig_data:
            sub_dept = self.env['hr.department'].search([('code','=',rec.code)])
            parent_dept = self.env['hr.department'].search([('code','=',rec.parent)])

            category = self.env['hr.department.category'].search([('code','=',rec.category_code)])

            sub_dept.write({
                'parent_id': parent_dept.id,
                'category_id': category.id
                })

        mig_data.unlink()


class GoalMigrationWizard(models.TransientModel):
    _name = 'goal.migration.wizard'
    _description = 'Goal Migration Wizard'

    @api.multi
    def process_migrate(self,data):
        ids = data.get('active_ids', [])
        mig_data = self.env['hr.goal.migration'].browse(ids)

        for record in mig_data:
            job = self.env['hr.job'].search([('sequence','=',record.sequence),('code','=',record.code),('company_id','=',record.company_id)])
            
            if record.name:
                text = record.name.splitlines()
                for line in text:
                    self.env['hr.job.goal'].create({
                        'name': line,
                        'job_id': job.id
                        })

        mig_data.unlink()


class TaskMigrationWizard(models.TransientModel):
    _name = 'task.migration.wizard'
    _description = 'Task Migration Wizard'

    @api.multi
    def task_process_migrate(self,data):
        ids = data.get('active_ids', [])
        mig_data = self.env['hr.task.migration'].browse(ids)

        for record in mig_data:
            job = self.env['hr.job'].search([('sequence','=',record.sequence),('code','=',record.code),('company_id','=',record.company_id)])
            dept = self.env['hr.department'].search([('code','=',int(record.department_code))])
            category = self.env['hr.job.category'].search([('code','=',int(record.category_code))])

            next_job = self.env['hr.job'].search([('code','=',record.next_job_code),('company_id','=',record.company_id),('name','=',record.next_job_name),])
            low_degree = self.env['hr.recruitment.degree'].search([('weight','=',record.degree_code)])

            if record.name:
                text = record.name.splitlines()
                for line in text:
                    self.env['hr.job.task'].create({
                        'name': line,
                        'job_id': job.id
                        })

            job.write({
                'department_id': dept.id,
                'categ_id': category.id,
                'next_job_id': next_job.id,
                'degree_id': low_degree.id
            })

        mig_data.unlink()
        


