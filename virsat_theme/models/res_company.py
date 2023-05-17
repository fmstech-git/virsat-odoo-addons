from odoo import fields, models, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    theme_color = fields.Char()
    theme_color_lighter = fields.Char()

    # def write(self, vals):
    #     res = super(ResCompanyInherit, self).write(vals)
    #
    #     if vals.get('theme_color'):
    #         web_editor_obj = self.env['web_editor.assets']
    #         content = """
    #         $o-brand-odoo: %s;
    #         $o-brand-primary: %s;
    #         """ % (self.theme_color, self.theme_color)
    #         web_editor_obj.save_asset('/theme_virsat/static/src/scss/colors.scss', 'web._assets_primary_variables', content, 'scss')
    #
    #     return res
