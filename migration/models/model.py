# -*- encoding: utf-8 -*-

from odoo import api, fields, models
    
class Migration(models.Model):
    _name = 'hr.migration'
    _description = 'HR Migration'

    first_name = fields.Char('First Name')
    second_name = fields.Char('Second Name')
    third_name = fields.Char('Third Name')
    last_name = fields.Char('Last Name')
    work_email = fields.Char()
    state = fields.Char()
    marital = fields.Char()
    religion = fields.Char()
    company_id = fields.Char()
    department_code = fields.Char('Department Code')
    start_date = fields.Date()
    sinid_date = fields.Date()
    birthday = fields.Date()
    visa_expire = fields.Date()
    sinid = fields.Char()
    emp_code = fields.Char('Employee Code')
    identification_id = fields.Char()
    passport_id = fields.Char()
    mobile_phone = fields.Char()
    country = fields.Char()
    work_location = fields.Char()
    work_phone = fields.Char()


class Migration_dept(models.Model):
    _name = 'hr.dept.migration'
    _description = 'HR DEPT Migration'

    name = fields.Char('Name')
    code = fields.Char('Code')
    parent = fields.Char( 'Parent')
    category_code = fields.Char( 'category code')


    
class Migration_tasks(models.Model):
    _name = 'hr.task.migration'
    _description = 'HR Task Migration'
    _rec_name = 'code'

    name = fields.Text('Name')
    sequence = fields.Integer('Job sequence')
    code = fields.Integer('Job code')
    category_code = fields.Integer( 'category code')
    department_code = fields.Char('Department Code')
    next_job_code = fields.Char('Next Job id')
    next_job_name = fields.Char('Next Job Name')
    degree_code = fields.Float('Degree Code')
    company_id = fields.Integer('Company')


class Migration_goals(models.Model):
    _name = 'hr.goal.migration'
    _description = 'HR Goal Migration'
    _rec_name = 'code'

    name = fields.Text('Name')
    sequence = fields.Integer('Job sequence')
    code = fields.Integer('Job code')
    company_id = fields.Integer('Company')



