# -*- coding: utf-8 -*-
from odoo.http import request, route, Controller, redirect_with_hash
from datetime import date, timedelta
import base64


class Admission(Controller):
    @route('/admission', auth='public', website=True)
    def index(self, **kw):
        return request.render('uni_admission.index')

    @route('/personal/info', auth='user', website=True, methods=['GET'])
    def form_pers_info(self, **kw):
        student = request.env['uni.student'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        if not student:
            return request.render('website.403')

       
        return request.render('uni_admission.personal_info', {
            'student': student,
            'has_errors': kw.get('has_errors', False)
        })

    @route('/personal/info', auth='user', website=True, methods=['POST'])
    def personal_info_post(self, **kw):
        try:
            request.session['admission_step'] = 2
            return redirect_with_hash('/registration/form')
        except Exception as e:
            return redirect_with_hash('/registration/form?has_errors=True')
    

    # GET|POST /admission/form
    @route('/admission/form', auth='user', website=True, methods=['GET'])
    def form(self, **kw):
        student = request.env['uni.student'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        if not student:
            return request.render('website.403')

        admission = request.env['uni.admission'].sudo().search([
            ('student_id', '=', student.id),
            ('state', '=', 'form')
        ])

        admission_reg = request.env['uni.admission'].sudo().search([
            ('student_id', '=', student.id),
            ('state', '=', 'reg_form')
        ])

        try:
            admission.ensure_one()
        except Exception:
            return request.render('uni_admission.form_done',{'admission_reg':admission_reg})


        country_id = request.env['res.country']

        country_ids = country_id.sudo().search([])

        sudan_id = country_id.sudo().search([('code','=','SD')]).id

        state_ids = request.env['res.country.state'].sudo().search(
            [('country_id', '=', sudan_id)]
        )

        # A hack to retrieve translated terms
        gender_list = request.env['uni.student']._fields['gender']._description_selection(
            request.env
        )
        martial_status = request.env['uni.student']._fields['martial_status']._description_selection(
            request.env
        )
        religion = request.env['uni.student']._fields['religion']._description_selection(
            request.env
        )

        return request.render('uni_admission.form', {
            'countries': country_ids,
            'states': state_ids,
            'student': student,
            'max_date': date.today() - timedelta(days=15*365),
            'gender_list': gender_list,
            'martial_status': martial_status,
            'religion': religion,
            'has_errors': kw.get('has_errors', False)
        })

    @route('/admission/form', auth='user', website=True, methods=['POST'])
    def form_post(self, **kw):
        try:
            student = request.env['uni.student'].sudo().search(
                [('user_id', '=', request.env.user.id)],
                limit=1
            )
            image = kw['student_id_img']

            # Check allowed extensions
            if image.content_type not in ['image/jpeg', 'image/png']:
                raise Exception('We only accept JPG/JPEG/PNG formats')
            image_data = image.read()
            if len(image_data) / (1024.0 * 1024.0) > 8.0:
                raise Exception('Maximum image size exceeded')

            student.sudo().write({
                'student_national_id_img': base64.encodestring(image_data)
            })
            # TODO: Validate data first, This is risky!

            student.write({
                'first_name_en': kw['first_name_en'].strip().title(),
                'middle_name_en': kw['middle_name_en'].strip().title(),
                'last_name_en': kw['last_name_en'].strip().title(),
                'fourth_name_en': kw['fourth_name_en'].strip().title(),
                'birth_date': kw['birth_date'].strip(),
                'place_of_birth': kw['place_of_birth'].strip(),
                'nationality_id': kw['nationality_id'].strip(),
                'gender': kw['gender'].strip(),
                'address': kw['address'].strip(),
                'email': kw['email'].strip(),
                'city': kw['city'].strip(),
                'state_id': kw['state_id'].strip(),
                'phone': kw['phone'].strip(),
                'mobile': kw['mobile'].strip(),
                'religion': kw['religion'].strip(),
                'national_id': kw['national_id'].strip(),
                'martial_status': kw['martial_status'].strip(),
            })

            # Advance to next step
            request.session['admission_step'] = 1
            return redirect_with_hash('/school/certificate')
        except Exception:
            return redirect_with_hash('/admission/form?has_errors=True')


    #GET|POST /school/certificate

    @route('/school/certificate', auth='user', website=True, methods=['GET'])
    def school_form(self, **kw):

        step = request.session.get('admission_step', 0)

        if step < 1:
             return redirect_with_hash('/admission/form')

        student = request.env['uni.student'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        if not student:
            return request.render('website.403')

        return request.render('uni_admission.school_certificate', {
            'student': student,
            'has_errors': kw.get('has_errors', False)
        })

    @route('/school/certificate', auth='user', website=True, methods=['POST'])
    def school_form_post(self, **kw):
        try:
            student = request.env['uni.student'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
            )
            admission_id = request.env['uni.admission'].sudo().search(
                [('student_id', '=',student.id)],
                limit=1
            )
            admission_id.student_id.write({
                'secondary_school': kw['secondary_school'].strip(),
                'examination_date': kw['examination_date'].strip(),
                'certificate_date': kw['certificate_date'].strip(),
            })

            print('----------- admission_id',admission_id.sec_subject)

            admission_id.sec_subject.create({
                'admission_id': admission_id.id,
                'name': kw['first_sub'].strip(),
                'degree': kw['first_deg'].strip(),
                })
            admission_id.sec_subject.create({
                'admission_id': admission_id.id,
                'name': kw['sec_sub'].strip(),
                'degree': kw['sec_deg'].strip(),
                })
            admission_id.sec_subject.create({
                'admission_id': admission_id.id,
                'name': kw['third_sub'].strip(),
                'degree': kw['third_deg'].strip(),
                })
            admission_id.sec_subject.create({
                'admission_id': admission_id.id,
                'name': kw['for_sub'].strip(),
                'degree': kw['for_deg'].strip(),
                })
            admission_id.sec_subject.create({
                'admission_id': admission_id.id,
                'name': kw['fif_sub'].strip(),
                'degree': kw['fif_deg'].strip(),
                })
            admission_id.sec_subject.create({
                'admission_id': admission_id.id,
                'name': kw['six_sub'].strip(),
                'degree': kw['six_deg'].strip(),
                })
            admission_id.sec_subject.create({
                'admission_id': admission_id.id,
                'name': kw['sev_sub'].strip(),
                'degree': kw['sev_deg'].strip(),
                })        

            # Advance to next step
            request.session['admission_step'] = 2
            return redirect_with_hash('/admission/form/family')
        except Exception:
            return redirect_with_hash('/school/certificate?has_errors=True')

    @route('/admission/form/family', auth='user', website=True, methods=['GET'])
    def family(self, **kw):
        step = request.session.get('admission_step', 0)

        if step < 2:
            return redirect_with_hash('/admission/form')

        student = request.env['uni.student'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        guardian_education_level = request.env['uni.student']._fields['guardian_education_level']._description_selection(
            request.env
        )

        mother_education_level = request.env['uni.student']._fields['mother_education_level']._description_selection(
            request.env
        )
        if not student:
            return request.render('website.403')

        admission = request.env['uni.admission'].sudo().search([
            ('student_id', '=', student.id),
            ('state', '=', 'form')
        ])

        try:
            admission.ensure_one()
        except Exception:
            return request.render('uni_admission.form_done')

        return request.render('uni_admission.form_family', {
            'student': student,
            'guardian_education_level': guardian_education_level,
            'mother_education_level': mother_education_level,
            'has_errors': kw.get('has_errors', False)
        })

    @route('/admission/form/family', auth='user', website=True, methods=['POST'])
    def family_post(self, **kw):
        try:
            student = request.env['uni.student'].sudo().search(
                [('user_id', '=', request.env.user.id)],
                limit=1
            )
            image = kw['nationality_id_photo']

            if image:
                if image.content_type not in ['image/jpeg', 'image/png']:
                    raise Exception('We only accept JPG/JPEG/PNG formats')

                image_data = image.read()

                if len(image_data) / (1024.0 * 1024.0) > 8.0:
                    raise Exception('Maximum image size exceeded')

                student.sudo().write({
                    'guardian_national_id_img': base64.encodestring(image_data)
                })
            # TODO: Validate data first, This is risky!
            student.sudo().write({
                'guardian_name': kw['guardian_name'].strip(),
                'guardian_relation': kw['guardian_relation'].strip(),
                'guardian_job': kw['guardian_job'].strip(),
                'guardian_nationality_id': kw['guardian_nationality_id'].strip(),
                'guardian_phone': kw['guardian_phone'].strip(),
                'guardian_address': kw['guardian_address'].strip(),
                'guardian_email': kw['guardian_email'].strip(),
                # 'relative_name': kw['relative_name'].strip(),
                # 'relative_phone': kw['relative_phone'].strip(),
                # 'relative_address': kw['relative_address'].strip(),
                'guardian_education_level': kw['guardian_education_level'].strip(),
                'kin_emergency': kw['kin_emergency'].strip(),
                'kin_ph_emergency': kw['kin_ph_emergency'].strip(),
                'mother_name': kw['mother_name'].strip(),
                'mother_education_level': kw['mother_education_level'].strip(),
                'mother_job': kw['mother_job'].strip(),
            })

            ##############
            # Advance to next step
            request.session['admission_step'] = 3
            return redirect_with_hash('/admission/form/photo')
        except Exception as e:
            return redirect_with_hash('/admission/form/family?has_errors=True')

    @route('/admission/form/photo', auth='user', website=True, methods=['GET'])
    def photo(self, **kw):
        student = request.env['uni.student'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        if not student:
            return request.render('website.403')

        admission = request.env['uni.admission'].sudo().search([
            ('student_id', '=', student.id),
            ('state', '=', 'form')
        ])

        try:
            admission.ensure_one()
        except Exception:
            return request.render('uni_admission.form_done')

        step = request.session.get('admission_step', 0)

        if step < 3:
            return redirect_with_hash('/admission/form')

        return request.render('uni_admission.form_photo', {
            'student':  student,
            'has_errors': kw.get('has_errors', False)
        })

    @route('/admission/form/photo', auth='user', website=True, methods=['POST'])
    def photo_post(self, **kw):
        try:
            image = kw['image']

            # Check allowed extensions
            if image.content_type not in ['image/jpeg', 'image/png']:
                raise Exception('We only accept JPG/JPEG/PNG formats')

            # Check size limit
            image_data = image.read()
            if len(image_data) / (1024.0 * 1024.0) > 8.0:
                raise Exception('Maximum image size exceeded')

            request.env.user.sudo().write({
                'image': base64.encodestring(image_data)
            })
            # TODO: Make image appear in student view
            request.env['uni.student'].sudo().search(
                [('user_id', '=', request.env.user.id)],
                limit=1).write({
                'std_img': base64.encodestring(image_data)
            }) 

            # Advance to next step
            student = request.env['uni.student'].sudo().search(
                [('user_id', '=', request.env.user.id)],
                limit=1
            )

            request.env['uni.admission'].sudo().search([
                ('student_id', '=', student.id),
                ('state', '=', 'form'),
            ], limit=1).write({
                'state': 'committee',
            })

            request.session['admission_step'] = 4
            return redirect_with_hash('/admission/form/success')
        except Exception:

            return redirect_with_hash('/admission/form/photo?has_errors=True')

    @route('/admission/form/success', auth='user', website=True )
    def submit(self, **kw):

        step = request.session.get('admission_step', 0)

        if step < 4:
            return redirect_with_hash('/admission/form')

        return request.render('uni_admission.form_success')



    @route('/registration/form' , auth='user', website=True ,methods=['GET'])
    def submit_(self, **kw):
        student = request.env['uni.student'].sudo().search(
            [('user_id', '=', request.env.user.id)],
            limit=1
        )

        admission_list = request.env['uni.student']._fields['type_admission']._description_selection(
            request.env
        )

        is_previouse_admitt = request.env['uni.student']._fields['is_previouse_admitt']._description_selection(
            request.env
        )

        reasons = request.env['uni.student']._fields['reasons']._description_selection(
            request.env
        )

        blood_group = request.env['uni.student']._fields['blood_group']._description_selection(
            request.env
        )

        return request.render('uni_admission.registration_form', {
            'student': student,
            'admission_list':admission_list,
            'is_previouse_admitt':is_previouse_admitt,
            'reasons':reasons,
            'blood_group':blood_group,
            'has_errors': kw.get('has_errors', False)
        })

    @route('/registration/form', auth='user', website=True, methods=['POST'])
    def form_(self, **kw):

        try:
            student = request.env['uni.student'].sudo().search(
                [('user_id', '=', request.env.user.id)],
                limit=1
            )

            image = kw['blood_image']

            if image:
                if image.content_type not in ['image/jpeg', 'image/png']:
                    raise Exception('We only accept JPG/JPEG/PNG formats')

                image_data = image.read()

                if len(image_data) / (1024.0 * 1024.0) > 8.0:
                    raise Exception('Maximum image size exceeded')

                student.sudo().write({
                    'blood_image': base64.encodestring(image_data)
                })

            # TODO: Validate data first, This is risky!
            student.sudo().write({
                'relative_name': kw['relative_name'].strip(),
                'relative_phone': kw['relative_phone'].strip(),
                'relative_address': kw['relative_address'].strip(),
                'blood_group': kw['blood_group'].strip(),
                'allergies_disea': kw['allergies_disea'].strip(),
                'chronic_dsease': kw['chronic_dsease'].strip(),
                'other_dsease': kw['other_dsease'].strip(),
                'secondary_school': kw['secondary_school'].strip(),
                'certificate_date': kw['certificate_date'].strip(),
                'examination_date': kw['examination_date'].strip(),
                'type_admission': kw['type_admission'].strip(),
                'is_previouse_admitt': kw['is_previouse_admitt'].strip(),
                'reasons': kw['reasons'].strip(),
                'other': kw['other'].strip(),
                #'sibling_in_nile': kw['sibling_in_nile'].strip(),
                
            })

            request.env['uni.admission'].sudo().search([
                ('student_id', '=', student.id),
                ('state', '=', 'reg_form'),
            ], limit=1).write({
                'state': 'clinic',
            })

            request.session['registration_step'] = 1
            return request.render('uni_admission.reg_form_success')
        except Exception:
            return redirect_with_hash('/registration/form?has_errors=True')

