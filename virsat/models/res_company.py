from odoo import fields, models, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    vr_trainee_seq_size = fields.Integer(default=3, string="VR Trainee Sequence Size")
    vr_trainee_seq_max_size = fields.Integer(compute='get_vr_trainee_seq_max_size', store=True, string="VR Trainee Sequence Max Size")
    company_code = fields.Char(required=True)

    _sql_constraints = [
        ('res_company_code_uniq', 'unique(company_code)', 'Company Code must be unique.'),
    ]

    @api.depends('vr_trainee_seq_size')
    def get_vr_trainee_seq_max_size(self):
        self.ensure_one()
        if self.vr_trainee_seq_size:
            max_size = 1
            for r in range(self.vr_trainee_seq_size):
                max_size *= 10

            self.vr_trainee_seq_max_size = max_size
