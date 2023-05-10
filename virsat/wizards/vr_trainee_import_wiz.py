# -*- coding: utf-8 -*-
from odoo import fields, models, api
from xlrd import open_workbook
import base64
from odoo.exceptions import ValidationError

class VrTraineeImportWizard(models.TransientModel):
    _name = "vr.trainee.import.wiz"
    _description = "VR Trainee Import Wizard"
    _rec_name = 'file'

    file = fields.Binary(required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def import_trainee(self):
        file_data = base64.b64decode(self.file)
        wb = open_workbook(file_contents=file_data)
        sheet = wb.sheet_by_index(0)
        fields = []
        trainee_list = []

        for row in range(sheet.nrows):
            if row <= 0:
                fields = list(map(lambda x: str(x.value.lower()), sheet.row(row)))
            else:
                lines = list(map(lambda x: isinstance(x.value, bytes) and x.value.encode('utf-8') or str(x.value), sheet.row(row)))

                if fields and lines:
                    list_dict = dict(zip(fields, lines))
                    trainee_list.append(list_dict)

        vr_trainee_obj = self.env['vr.trainee']

        if any(not r['name'].strip() for r in trainee_list):
            raise ValidationError("Please make sure not to add empty name on the list.")

        new_trainees = []
        for r in trainee_list:
            new = vr_trainee_obj.create({'name': r['name'].strip(), 'company_id': self.company_id.id})
            new_trainees.append(new.id)

        return {
            "name": "New Trainees",
            "type": "ir.actions.act_window",
            "res_model": "vr.trainee",
            "view_mode": "tree,form",
            "domain": [('id', 'in', new_trainees)],
        }
