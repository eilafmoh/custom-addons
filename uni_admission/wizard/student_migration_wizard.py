# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime


class MigrationWizard(models.TransientModel):
    _name = 'student.migration.wizard'
    _description = 'Student Migration Wizard'

    certificate_type_id = fields.Many2one(
        string="Certificate Type",
        comodel_name="uni.certificate.type",
        ondelete="restrict",
        required=True
    )

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        ondelete="restrict",
        required=True
    )

    @api.multi
    def process_migrate(self, data):
        # TODO: rewrite this function to use sql quries inested of ORM
        ids = data.get('active_ids', [])
        query = '''
        with migration as (
            select  
                first_name,middle_name,last_name,fourth_name,
                CONCAT (first_name, ' ',middle_name,' ',last_name,' ',fourth_name)  as name,
                faculty_id,secondary_school,department_id,
                university_id 
            from 
                student_migration  
            where 
                id in %s 
        ),
            partner as (
                insert into 
                    res_partner (
                        name , display_name ,ref, email,company_id,active,invoice_warn,customer
                    ) 
                select 
                    name,name ,university_id, null,faculty_id,True,'no-message',True
                from 
                    migration m
                RETURNING 
                    id,company_id,email,ref
                ),
            users as (
                insert into 
                    res_users (
                        login,password,partner_id,company_id,notification_type,odoobot_state
                    )  
                select  
                    ref,ref,id ,company_id,'inbox','onboarding_emoji'
                from 
                    partner
                RETURNING 
                id as u_id ,login,company_id
            ),
            group_record as (
                insert into 
                    res_groups_users_rel (
                        gid, uid
                    ) 
                select 
                    t1.id,t2.u_id 
                from 
                    res_groups as t1,users as t2 
                where 
                    t1.name = 'Contact Creation'
            ),
            company_record as (
                insert into 
                    res_company_users_rel (
                        cid , user_id
                    ) 
                select  
                    company_id ,u_id from users
            ),
            student as (
                insert into 
                    uni_student(
                        first_name,middle_name,last_name,
                        fourth_name,name,secondary_school,faculty_id,
                        department_id,university_id,user_id,
                        certificate_type_id,year_id,currency_id,state
                    )  
                select  
                    first_name,middle_name,last_name,
                    fourth_name,CONCAT (first_name, ' ',middle_name,' ',last_name,' ',fourth_name),
                    secondary_school,faculty_id,department_id,m.university_id,u_id,%s,%s,%s,'draft'
                from 
                    migration m  
                    left join  
                        users u on  u.login = m.university_id
                RETURNING 
                    id,department_id,faculty_id,university_id,certificate_type_id,year_id
            ),

            medical_data as (
                insert into 
                    uni_health_service_medical_data(student_id) 
                select 
                    id 
                from 
                    student
                RETURNING 
                    id ,student_id
            )
            insert into 
                uni_admission (
                    medical_data,student_id,department_id,faculty_id,university_id,certificate_type_id,state
                ) 
                select 
                    m.id,student_id,department_id,faculty_id,
                    university_id,certificate_type_id,'form'
                from 
                    medical_data m 
                    left join 
                    student s 
                    on s.id = m.student_id
            
        '''
        self.env.cr.execute(query, (tuple(ids),self.certificate_type_id.id,self.year_id.id ,self.certificate_type_id.currency_id.id),)
        ids = self.env['student.migration'].browse(ids)
        ids.unlink()
