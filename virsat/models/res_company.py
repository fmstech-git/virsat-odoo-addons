from odoo import fields, models, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    vr_trainee_pin_size = fields.Integer(default=3, string="VR Trainee PIN Length")
    vr_trainee_pin_max_size = fields.Integer(compute='get_vr_trainee_pin_max_size', store=True, string="PIN Max Size", help="Maximum PIN the system can generate.")
    vr_trainee_limit = fields.Integer(help='Limit the number of trainee per company.', string="Max Trainees Allowed")
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
