# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class VrTraineeImportWizard(models.TransientModel):
    _name = "vr.mails.fetch.wiz"
    _description = "Fetch VR Mails Wizard"

    def get_incoming_mail_account(self):
        mail = self.env['fetchmail.server'].sudo().search([('name', '=', 'vrgameresults')], limit=1)
        return mail.user if mail else False

    name = fields.Char(default=get_incoming_mail_account, readonly=True)

    def fetch_mail(self):
        mail = self.env['fetchmail.server'].sudo().search([('name', '=', 'vrgameresults')], limit=1)

        if not mail or not self.name:
            raise ValidationError("Please make sure to setup Incoming Mail Server.")

        mail.fetch_mail()
        action = self.env.ref('virsat.action_virsat_vr_mails').read()[0]

        return action
