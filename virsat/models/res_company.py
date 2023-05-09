from odoo import fields, models, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    vr_trainee_seq_size = fields.Integer(default=4)
    vr_trainee_seq_max_size = fields.Integer()
    company_code = fields.Char()
