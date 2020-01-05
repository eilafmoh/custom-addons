from odoo import api, fields, models, _
import logging
logger= logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    select_linked = fields.Selection([
        ('fix','Fixed'),
        ('job','Linked To Job'),
    ], string='Type', index=True, required=True, default='fix')
    default_amount=fields.Float(string='Default Amount/Percentage', required=True , default=0.0)

    salary_amount_ids = fields.One2many('hr.salary.amount','salary_rule_id',required=False)

    @api.multi
    def compute_allowed_deduct_amount(self, contract_id):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = self.category_id.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0
        
        blacklist = []
        result_dict = {}
        rules_dict = {}
        categories = BrowsableObject(contract_id.employee_id.id, {}, self.env)
        rules = BrowsableObject(contract_id.employee_id.id, rules_dict, self.env)
        baselocaldict = {'categories': categories, 'rules': rules, }
        structure_ids = contract_id.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        # if self.deduct_absence == 'day' or self.deduct_absence == 'hour':
        rule_ids_list =  []
        # for exeption in contract_id.expectation_ids:
        #     if exeption.salary_rule_id.id in self.amount_percentage_base.ids:
        #         rule_ids_list.append((exeption.salary_rule_id.id, exeption.salary_rule_id.sequence))
        # for slip_lin in contract_id.payslip_line_ids:
        #     if slip_lin.salary_rule_id.id in self.amount_percentage_base.ids:
        #         rule_ids_list.append((slip_lin.salary_rule_id.id, slip_lin.salary_rule_id.sequence))
        # rule_ids = rule_ids_list

        falg = False
        for x in rule_ids:
            if x[0] == self.id:
                falg =True
        if not falg:
            rule_ids.append((self.id,self.sequence))
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        # logger.info("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ %s", sorted_rule_ids)
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)
        contract =contract_id
        employee = contract.employee_id
        localdict = dict(baselocaldict, employee=contract_id.employee_id, contract=contract_id)\
        
        for rule in sorted_rules:
            # print('------------------- contraact ',rule.code ,contract.id)
            key = rule.code + '-' + str(contract.id)
            localdict['result'] = None
            localdict['result_qty'] = 1.0
            localdict['result_rate'] = 100
            localdict['contract'] = contract_id
            localdict['employee'] = contract_id.employee_id
            # if rule._satisfy_condition(localdict) and rule.id not in blacklist:
            amount, qty, rate = rule._compute_rule(localdict)
            # logger.info("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ rule _id%s", rule.id)
            # logger.info("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ amount%s", amount)
            previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
            tot_rule = amount * qty * rate / 100.0
            localdict[rule.code] = tot_rule
            rules_dict[rule.code] = rule
            result_dict[rule.code] = {
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'name': rule.name,
                    'code': rule.code,
                    'category_id': rule.category_id.id,
                    'sequence': rule.sequence,
                    'condition_select': rule.condition_select,
                    'condition_python': rule.condition_python,
                    'condition_range': rule.condition_range,
                    'condition_range_min': rule.condition_range_min,
                    'condition_range_max': rule.condition_range_max,
                    'amount_select': rule.amount_select,
                    'amount_fix': rule.amount_fix,
                    'amount_python_compute': rule.amount_python_compute,
                    'amount_percentage': rule.amount_percentage,
                    'amount_percentage_base': rule.amount_percentage_base,
                    'register_id': rule.register_id.id,
                    'amount': amount,
                    'employee_id': contract.employee_id.id,
                    'quantity': qty,
                    'rate': rate,
                }
            if rule.id == self.id:
                return result_dict[self.code]['amount']
            else:
                blacklist += [id for id, seq in rule._recursive_search_of_rules()]
        # logger.info("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ %s", result_dict[self.code]['amount'])
        return result_dict[self.code]['amount']


    @api.multi
    def _rule_amount_percentage(self, contract):

        amount = self.default_amount
        domain = [('salary_rule_id','=',self.id)]
        hr_salary = self.env['hr.salary.amount']
        if self.select_linked == 'job':
           if contract.job_id:
                if self.salary_amount_ids :
                    print('------------------- inside if',self.salary_amount_ids)
                    record = hr_salary.search(domain + [('job_id','=',contract.job_id.id)])
                    print('------------------ record ',record)
                    if record:
                       amount = record.amount or 0.0
                       print('--------------- amount ',amount)
        elif self.select_linked == 'fix':

            amount = self.amount_fix
            
        return amount

    @api.multi
    def _compute_rule(self, localdict):
  
        """
        :param localdict: dictionary containing the environement in which to compute the rule
        :return: returns a tuple build as the base/amount computed, the quantity and the rate
        :rtype: (float, float, float)
        """
        self.ensure_one()
        print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn',self.amount_select)
        if self.amount_select == 'fix':
            print('hhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
            amount_fix = self._rule_amount_percentage(localdict['contract'])
            try:
                amount_fix = self._rule_amount_percentage(localdict['contract'])
                print('ggggggggggggggggggggg',amount_fix,localdict,self.quantity)
                return amount_fix, float(safe_eval(self.quantity, localdict)), 100.0
            except:
                print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnhghfydtst',amount_fix)
                raise UserError(_('Wrong quantity defined for salary rule %s (%s).') % (self.name, self.code))

        elif self.amount_select == 'percentage':
            try:
                return (float(safe_eval(self.amount_percentage_base, localdict)),
                        float(safe_eval(self.quantity, localdict)),
                        self.amount_percentage)
            except:
                raise UserError(_('Wrong percentage base or quantity defined for salary rule %s (%s).') % (self.name, self.code))
        else:
            try:
                safe_eval(self.amount_python_compute, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise UserError(_('Wrong python code defined for salary rule %s (%s).') % (self.name, self.code))



class SalaryAmount(models.Model):
    _name='hr.salary.amount'

    
    amount=fields.Float(string='Amount', required=True)
    salary_rule_id=fields.Many2one('hr.salary.rule')
    job_id = fields.Many2one('hr.job', 'Job Position')
