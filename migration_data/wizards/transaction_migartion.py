# -*- encoding: utf-8 -*-

from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import Warning



class MigrationtranWizard(models.TransientModel):
    _name = 'tran.migration.wizard'

    account_id = fields.Many2one('account.account',string="Payable Account")
    account_receivable_id = fields.Many2one('account.account',string="Receivable Account")

    account_equity = fields.Many2one('account.account',string="Equity Account")
    journal_id = fields.Many2one('account.journal' , string="Journal")
    @api.multi
    def cretae_data(self, data):

        student_data = self.env['uni.migration'].search([('balance','!=',0)])
        invoice_id = self.env['account.invoice']
        invoice_line_id = self.env['account.invoice.line']
    
        for std in student_data :
            if std.std_course_id == 'ACC':
            	company_id = self.env['res.company'].search([('code','=','BUS')])
            else:
                company_id = self.env['res.company'].search([('code','=',std.std_course_id)])
            account_receivable = company_id.receivable_fees_account
            partner_id = self.env['res.partner'].search([
            	('ref','=',std.std_reg_no),('company_id','=',self.env.user.company_id.id)])
            

            if partner_id:
                
                line = []
                vals ={
                    'invoice_id': invoice_id.id,
                    'account_id': 249,
                    'name':  'Fees 2019',
                    'price_unit': float(std.balance),
                }

                line.append((0,0,vals))

                invoice_id.create({
                    'journal_id':29,
                    'partner_id': partner_id.id,
                    'state': 'draft',
                    'account_id': self.account_receivable_id.id,
                    'type': 'out_invoice',
                    'date_invoice' : '2020-01-01',
                    'invoice_line_ids' : line
                    })


            else:
                
                self.env['uni.notfound'].create({
                'std_reg_no' : std.std_reg_no,
                'std_course_id' : std.std_course_id,
                'debit':std.debit,
                'credit' : std.credit,
                'balance' : std.balance,
                })

    def cretae_payable_data(self, data):
        print('-------------- in payable')

        partner_data = self.env['uni.migration.payable'].search([('balance','!=',0)])
        
        if self.account_id and not self.account_receivable_id:
            total_credit_payable = 0.0
            total_debit_payable = 0.0

            move_id = self.env['account.move'].create({
                    'journal_id':self.journal_id.id,
                    'date': fields.Date.today(),
                    #'ref': 'Liabilities',
                    #'currency_id' : std.currency_id,
                    })

            for partner in partner_data:
                partner_id = self.env['res.partner'].search([('ref','=',partner.partner_id)])

                if partner_id:
                    if float(partner.balance) < 0:
                        total_credit_payable = total_credit_payable + float(partner.balance)
                    else : 
                        total_debit_payable = total_debit_payable + float(partner.balance)

                    move_line_id = self.env['account.move.line'].with_context({'check_move_validity': False})
                    
                    move_line_id.create({
                        'move_id': move_id.id,
                        'account_id': self.account_id.id,
                        'name': '/',
                        'debit': 0 if float(partner.balance) < 0 else float(partner.balance),
                        'credit': abs(float(partner.balance)) if float(partner.balance) < 0 else 0,
                        'date': '2020-01-01',
                        'partner_id' :partner_id.id,
                    })

                    move_line_id.create({
                    'move_id': move_id.id,
                    'account_id': self.account_equity.id,
                    'name': '/',
                    'debit': 0 if float(partner.balance) > 0 else abs(float(partner.balance)),
                    'credit': abs(float(partner.balance)) if float(partner.balance) > 0 else 0,
                    'date': '2020-01-01',
                    })
                    
                else:
                    self.env['uni.notfound.payable'].create({
                        'partner_name' : partner.partner_name,
                        'partner_id' : partner.partner_id,
                        'std_reg_no' : partner.std_reg_no,
                        'std_course_id' : partner.std_course_id,
                        'debit' : partner.debit,
                        'credit' : partner.credit,
                        'balance' : partner.balance ,
                        'discription' : partner.discription,

                        })
            # total_payable = total_debit_payable + total_credit_payable
            # move_line_id.create({
            #     'move_id': move_id.id,
            #     'account_id': self.account_equity.id,
            #     'name': '/',
            #     'debit': 0 if total_payable > 0 else abs(total_payable),
            #     'credit': abs(total_payable) if total_payable > 0 else 0,
            #     'date': '2020-01-01',
            # })

        elif self.account_receivable_id and not self.account_id:
            total_receivable = 0.0
            move_id = self.env['account.move'].create({
                    'journal_id':27,
                    'date': fields.Date.today(),
                    'ref': 'Receivables',
                    #'currency_id' : std.currency_id,
                    })

            for partner in partner_data:
                

                partner_id = self.env['res.partner'].search([('ref','=',partner.partner_id)])

                if partner_id:
                    total_receivable = total_receivable + float(partner.balance)

                    move_line_id = self.env['account.move.line'].with_context({'check_move_validity': False})
                    
                    move_line_id.create({
                        'move_id': move_id.id,
                        'account_id': self.account_receivable_id.id,
                        'name': '/////',
                        'debit': abs(float(partner.balance)) if float(partner.balance) > 0 else 0,
                        'credit': 0 if float(partner.balance) > 0 else float(partner.balance),
                        'date': '2020-01-01',
                        'partner_id' :partner_id.id,
                    })
                else:
                    msg = ('Partner Does not exist',partner.partner_id)

                    raise Warning(
                        _(msg)
                    )


            move_line_id.create({
                'move_id': move_id.id,
                'account_id': 236,
                'name': '/////',
                'debit': 0 if total_receivable > 0 else total_receivable,
                'credit': abs(total_receivable) if total_receivable > 0 else 0,
                'date': '2020-01-01',
            })



    		


        
