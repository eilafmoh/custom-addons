
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class check_wizard(models.Model):
    _name = "check.wizard"
    _description = "Check wizard"

    date_from = fields.Date("Start Date", requierd='True')
    date_to = fields.Date("End Date", requierd='True')
    state = fields.Selection(
        [('in', 'In'), ('out', 'Out')], 'Check State', requierd='True')

    _defaults = {
        'state': 'out',
    }

    @api.multi
    def retrive_checks(self):
        context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'state'])[0]
        #data['formm'] = self.read(['date_from','date_to','state'])

        ir_model_data = self.env['ir.model.data']

        # Those lines hashed because form view of check line enable users to edit on it
        #form_res = ir_model_data.get_object_reference(cr, uid, 'account_voucher_custom', 'customer_check_line_form')
        #form_id = form_res and form_res[1] or False

        form_res_check = ir_model_data.get_object_reference(
            'account_voucher_custom', 'on_credit_check_line_form')
        form_check_id = form_res_check and form_res_check[1] or False

        tree_res = ir_model_data.get_object_reference(
            'account_voucher_custom', 'customer_check_line_tree')
        tree_id = tree_res and tree_res[1] or False

        form_res = ir_model_data.get_object_reference(
            'account_voucher_custom', 'customer_check_line_form')
        form_id = form_res and form_res[1] or False

        ree_res = ir_model_data.get_object_reference(
            'account_voucher_custom', 'on_credit_check_line_tree')
        ree_id = ree_res and ree_res[1] or False

        #onc_check = self.env['oncreadit.check.line']
        customer_check = self.env['customer.check.line']

        # if data['form']['state']=='in':
        customer_check_ids = customer_check.search([('due_date', '>=', data['form']['date_from']),
                                                    ('due_date', '<=', data['form']['date_to']), ('move_check', '=', False), ('check_status', '=', 'schedule')])

        check_array = []
        for x in customer_check_ids:
            check_array.append(x.id)

        if customer_check_ids:
            return {
                'name': _('Customers Checks'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'customer.check.line',
                'views': [(tree_id, 'tree'), (form_id, 'form')],
                'domain': [('id', 'in', check_array)],
                'type': 'ir.actions.act_window',
            }
        else:
            raise UserError(
                _('It seems that there is no in checks in this period'))


class check_edit_wizard(models.TransientModel):
    _name = "check.edit"
    _description = "check edition"

    new_date = fields.Date("New Date", requierd='True')
    check_lines = fields.Many2one('customer.check.line', 'Check Lines')
    partner_id = fields.Many2one('customer.check', 'Customer checks')
    selection = fields.Selection([
        ('date', 'Date'),
        ('status', 'Status')], default='date')

    new_status = fields.Selection(
        [('revise', 'Revise'),
         ('schedule', 'Schedule'),

         ], 'New check status')
    revise_reson = fields.Char('The reson of revise')
    check_lines2 = fields.Many2one('customer.check.line', 'Check Lines')
    move_line = fields.Many2one('account.move' , string='Move Lines')

    def edit_checks(self):
        data = {}
        data['ids'] = self._context.get('active_ids', [])
        data['model'] = self._context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['new_date', 'state', 'partner_id', 'check_lines',
                                  'selection', 'new_status', 'check_lines2', 'revise_reson'])[0]

        customer_check = self.env['customer.check.line']
        if data['form']['selection'] == 'date':
            check_lines = customer_check.browse(data['form']['check_lines'][0])
            check_lines[0].write({'due_date': data['form']['new_date']})
        else:
            check_lines = customer_check.browse(
                data['form']['check_lines2'][0])
            # update status from schedule to open
            if data['form']['new_status'] == 'schedule' and check_lines.check_status == 'revise':
                check_lines[0].write({
                    'check_status': 'schedule',
                })
            elif data['form']['new_status'] == 'revise' and check_lines.check_status == 'paid':
                description = check_lines.description
                partner_id = check_lines.partner_id.id

                partner_account = check_lines.partner_id.property_account_receivable_id.id
                amount = check_lines.amount
                ref = check_lines.check_number

                print('--------------- check_lines',check_lines.move_ids)

                for line in check_lines.move_ids.line_ids:
                    credit_account = line.move_ids.journal_id.default_credit_account_id.id
                    journal_id = line.move_id.journal_id.id
                    # TO Review
                    analytic_account_id = line.analytic_account_id
                    debit_account = line.partner_id.property_account_receivable_id.id

                post_action_obj = self.env['post.check.action']
                debit = 0.0
                credit = amount
                move_id = post_action_obj.create_move(ref, journal_id)
                # delete analytic_account_id from sendig param
                post_action_obj.create_move_line(
                    partner_id, ref, move_id.id, credit_account, debit, credit)

                debit = amount
                credit = 0.0
                # delete analytic_account_id from sendig param
                post_action_obj.create_move_line(
                    partner_id, ref, move_id.id, debit_account, debit, credit)
                status = data['form']['new_status']
                revise_reson = data['form']['revise_reson']
                check_lines[0].write({
                    'check_status': 'revise',
                    'revise_reson': revise_reson
                })
                if check_lines.related_lines:
                    for line in check_lines.related_lines:
                        line.write({
                            'check_status': 'revise',
                            'revise_reson': revise_reson
                        })
        return True
