# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _name = "admission.report.analysis"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'


    date = fields.Datetime('Date', readonly=True)
    student_id = fields.Many2one('uni.student', 'student', readonly=True)
    faculty_id = fields.Many2one('res.company', 'Faculty', readonly=True)
    department_id = fields.Many2one('uni.faculty.department', 'Department', readonly=True)
    specialization_id = fields.Many2one('uni.faculty.department.specialization', 'Specialization', readonly=True)
    admission_type = fields.Selection([('private','Private'),('public','Public')],readonly=True)
    certificate_type_id = fields.Many2one('uni.certificate.type',string="Certificate type",readonly=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('form', 'Waiting for filling out the form'),
            ('clinic', 'Waiting for medical examination'),
            ('committee', 'Waiting for the faculty committee'),
            ('payment', 'Waiting for payment'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ],readonly=True)
    # batch_id = fields.Many2one('uni.faculty.department.batch',string="Batch",readonly=True)
    medical_condition = fields.Selection([
            ('fit', 'Medically fit'),
            ('unfit', 'Medically unfit'),
        ],readonly=True)
    
    year_id = fields.Many2one('uni.year', 'year', readonly=True)
    def _select(self):
        select_str = """
            
             SELECT min(a.id) as id,
              
                    
                    a.date,
                    a.student_id,
                    a.state,
                    a.faculty_id,
                    a.department_id,
                    s.year_id,
                    a.specialization_id,
                    s.admission_type,
                    a.certificate_type_id,
                    -- a.batch_id,
                    a.medical_condition
        """ 
        return select_str

    def _from(self):
        from_str = """
                uni_admission a
                      join uni_student s on (a.student_id=s.id)
                      join res_company f on (a.faculty_id = f.id)
                      left join uni_year y on (s.year_id=y.id)
                      left join uni_faculty_department d on (a.department_id=d.id)
                      left join uni_faculty_department_specialization sp on (a.specialization_id=sp.id)
                      left join uni_certificate_type cer on (a.certificate_type_id=cer.id)
                      
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY a.date,
                    a.student_id,
                    a.state,
                    a.faculty_id,
                    s.year_id,
                    a.department_id,
                    a.specialization_id,
                    a.medical_condition,
                    s.admission_type,
                    a.certificate_type_id,
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
