
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class check_action(models.TransientModel):
    _name = "check.action"
    _description = "check posting"

    journal_id = fields.Many2one('account.journal', 'Journal')

    def create_move(self, ref, journal_id):
        move = self.env['account.move']
        vals = {
            'ref': ref,
            'journal_id': journal_id,
        }
        return move.create(vals)

    def create_move_line(self, partner_id, name, move_id, account_id, debit, credit):
        move_line = self.env['account.move.line']
        vals = {
            'partner_id': partner_id,
            'name': name,
            'move_id': move_id,
            'account_id': account_id,
            'debit': debit,
            'credit': credit,
        }
        print ('vals is : ', vals)

        return move_line.with_context(check_move_validity=False).create(vals)

    def update_state(self, check_line_obj):
        print ('check line object is : ', check_line_obj)
        check_line_obj.write({'check_status': 'paid'})
        flag = True

        for line in check_line_obj.check_lines:
            print('----------- line',line.move_ids)
            if not line.move_ids:
                print ('$$$$$$$$$$$$$$$$4', check_line_obj.check_lines)
                flag = False

        if flag:
            print ("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            check_line_obj.write({'check_status': 'paid'})
            '''
			if check_line_obj.voucher_id:
				#TODO it came from voucher 'voucher must closed '
				print 'on voucher '
			elif check_line_obj.invoice_id :
				check_line_obj.invoice_id.write({'state':'paid'})
			'''

    def paid(self):

        #wf_service = netsvc.LocalService("workflow")

        check_line = self.env['customer.check.line']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']

        check_action = self

        if 'active_ids' in self.env.context and self.env.context['active_ids']:
            for rec in check_line.browse(self.env.context['active_ids']):
                print('%%%%%%%%', rec.description)
                if rec.check_status == "paid":
                    raise UserError(_('Sorry this check is already paid ! '))
                else:
                    if rec.related_lines:
                        for line in rec.related_lines:
                            partner_id = line.line_id.partner_id.id

                            ref = line.check_number
                            journal_id = check_action.journal_id.id
                            move_id = self.create_move(ref, journal_id)
                            print ('created move id is : ', move_id)

                            if line.description:
                                name = line.description
                            else:
                                name = '/'
                            account_id = check_action.journal_id.default_debit_account_id.id
                            debit = line.amount
                            credit = 0.0
                            self.create_move_line(
                                partner_id, name, move_id.id, account_id, debit, credit)

                            account_id = line.line_id.partner_id.property_account_receivable_id.id
                            debit = 0.0
                            credit = line.amount
                            self.create_move_line(
                                partner_id, name, move_id.id, account_id, debit, credit)

                            line.write({
                                'move_id': move_id.id,
                            })

                            account_move = move_obj.browse(move_id.id)
                            print ('*********************************',
                                   account_move)

                            account_move.write({
                                'state': 'posted',
                            })

                        rec.write({
                            'move_id': move_id.id,
                        })

                        self.update_state(rec.line_id)
                        rec.write({'check_status': 'paid'})

                    else:

                        partner_id = rec.line_id.partner_id.id

                        ref = rec.check_number
                        journal_id = check_action.journal_id.id
                        move_id = self.create_move(ref, journal_id)
                        print ('created move id is : ', move_id)
                        if rec.description:
                            name = rec.description
                        else:
                            name = '/'
                        account_id = check_action.journal_id.default_debit_account_id.id
                        debit = rec.amount
                        credit = 0.0
                        self.create_move_line(
                            partner_id, name, move_id.id, account_id, debit, credit)

                        account_id = rec.line_id.partner_id.property_account_receivable_id.id
                        debit = 0.0
                        credit = rec.amount
                        self.create_move_line(
                            partner_id, name, move_id.id, account_id, debit, credit)

                        print('rec is : ', rec)
                        rec.write({
                            'move_id': move_id.id,
                        })

                        account_move = move_obj.browse(move_id.id)
                        print ('*********************************', account_move)
                        account_move.write({
                            'state': 'posted',
                        })

                        self.update_state(rec.line_id)
                        rec.write({'check_status': 'paid'})
