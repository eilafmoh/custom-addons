# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date , datetime
from odoo.exceptions import ValidationError, UserError
from odoo import _

class RecRequest(models.Model):
    _name='recruitment.request'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name",related="job_id.name",)
    job_id = fields.Many2one("hr.job",string="Job" ,required=True)
    request_number = fields.Integer('Requested Number',required=True )
    job_description = fields.Html('Notes')
    request_date=fields.Datetime("Order Date", default= fields.datetime.now())
    department_id = fields.Many2one('hr.department', string="Department" , required=True)
    state = fields.Selection([("draft", "Draft"),
                              ("approve", "Confirmed"),
                              ("cancel", "Cancel"),
                              ("done", "approved")], default='draft', string="Status")

    employment_date = fields.Date("Employment Date")
    base_salary = fields.Float("Base Salary",required=True)
    training_salary = fields.Float("Probation Salary",required=True)
    active = fields.Boolean('active',default=True)

    @api.one
    def bt_approve(self):
        self.state = "approve"
    @api.one
    def bt_reject(self):
        self.state = "cancel"
        self.active = False

    @api.one
    def bt_done(self):
        self.state = "done"

class HrJob(models.Model):
    _inherit='hr.job'

    request_number = fields.Integer('Requested Number',required=True )
    job_description = fields.Text('Job Description')
    department_id = fields.Many2one('hr.department', string="Department ID")

class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
           
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
                                               'job_id': applicant.job_id.id,
                                               'address_home_id': address_id,
                                               'employee_type':'trainee',
                                               'department_id': applicant.department_id.id or False,
                                               'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                               'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                               'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window


class covenant_covenant(models.Model):
    _name = "covenant.covenant"

    name = fields.Char(string="Name", required=True)

class employee_covenant(models.Model):
    _name = "employee.covenant"
    _description = "Employee covenant from company"

    name = fields.Many2one("covenant.covenant",string="Name", required=True)
    number=fields.Integer(string="Number",required=True)
    amount=fields.Float(string="Amount",required=True)
    contract_id=fields.Many2one('hr.contract', 'Employee Contract', required=True)
    state = fields.Selection([('draft', "Draft"),
                   ('with_employee', "With employee"),
                   ('received', "Received")],
                  string="State", required=True, copy=False,default="with_employee")


    @api.multi
    def action_receive_covenant(self):
        self.write({'state':'received'})

    @api.multi
    def action_with_employee(self):
        self.write({'state':'with_employee'})

class hrContract(models.Model):
    _inherit = "hr.contract"

    covenant_id=fields.One2many('employee.covenant', 'contract_id', string="Employee Exit", index=True)