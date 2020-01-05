##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_

class Department(models.Model):
    _inherit = "hr.department"

    category_id = fields.Selection(
        string='Department Type',
        selection=[('academic', 'Academic department'), ('admin', 'Admin department')]
    )
  
class DepartmentCategory(models.Model):
    _name = "hr.department.category"
    
    name = fields.Char(string='Name', translate=True)
    active = fields.Boolean('Active', default=True)
