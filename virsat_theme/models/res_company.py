from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    theme_color = fields.Char()
    theme_color_lighter = fields.Char()
    set_login_logo = fields.Boolean(default=False, string="Use Logo in Login Screen")
    logo_login_height = fields.Integer(default=60)

    def write(self, vals):
        if vals.get('set_login_logo'):
            if self.search([('set_login_logo', '=', True), ('id', '!=', self.id)]):
                raise ValidationError("You can only set 1 default logo in login screen.")

        return super(ResCompanyInherit, self).write(vals)
