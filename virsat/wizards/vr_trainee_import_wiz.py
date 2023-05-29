# -*- coding: utf-8 -*-
from odoo import fields, models, api
from xlrd import open_workbook
import base64
from odoo.exceptions import ValidationError
import xlrd


class VrTraineeImportWizard(models.TransientModel):
    _name = "vr.trainee.import.wiz"
    _description = "VR Trainee Import Wizard"
    _rec_name = 'file'

    file = fields.Binary(required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    def import_trainee(self):
        """
        Import trainees using excel.
        """
        file_data = base64.b64decode(self.file)
        wb = open_workbook(file_contents=file_data)
        sheet = wb.sheet_by_index(0)
        fields = []
        trainee_list = []

        for row in range(sheet.nrows):
            if row <= 0:
                fields = list(map(lambda x: str(x.value.lower().replace(" ", "_")), sheet.row(row)))
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
            try:
                # prepare the data
                dob = False
                if r.get('dob'):
                    datetime_date = xlrd.xldate.xldate_as_datetime(float(r['dob']), 0)
                    dob = datetime_date.date()

                trainee_data = {
                    'name': r['name'].strip() if r.get('name') else False,
                    'unit': r.get('unit', False),
                    'designation': r.get('designation', False),
                    'driver_for': r.get('driver_for', False),
                    'location': r.get('location', False),
                    'nationality': r.get('nationality', False),
                    'language': r['language'].lower() if r.get('language') else False,
                    'gender': r['gender'].lower() if r.get('gender') else False,
                    'dob': dob,
                    'company_id': self.company_id.id,
                }

                # create new trainee
                new = vr_trainee_obj.create(trainee_data)
                new_trainees.append(new.id)

            except Exception as e:
                raise ValidationError("Something went wrong. %s" % e)

        # show all newly created trainees
        return {
            "name": "New Trainees",
            "type": "ir.actions.act_window",
            "res_model": "vr.trainee",
            "view_mode": "tree,form",
            "domain": [('id', 'in', new_trainees)],
        }
