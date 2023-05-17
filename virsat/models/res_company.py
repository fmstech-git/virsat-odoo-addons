from odoo import fields, models, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    vr_trainee_pin_size = fields.Integer(default=3, string="VR Trainee PIN Size")
    vr_trainee_pin_max_size = fields.Integer(compute='get_vr_trainee_pin_max_size', store=True, string="VR Trainee PIN Max Size")
    company_code = fields.Char(required=True)
    theme_color = fields.Char()

    _sql_constraints = [
        ('res_company_code_uniq', 'unique(company_code)', 'Company Code must be unique.'),
    ]

    @api.depends('vr_trainee_pin_size')
    def get_vr_trainee_pin_max_size(self):
        for company in self:
            if company.vr_trainee_pin_size:
                max_size = 1
                for r in range(company.vr_trainee_pin_size):
                    max_size *= 10

                company.vr_trainee_pin_max_size = max_size
