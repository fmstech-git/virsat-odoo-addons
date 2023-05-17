from odoo import fields, models, api
import base64
import csv
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class VirsatVrMails(models.Model):
    """
    Inherit IR Attachment so that we can automate the CSV/JSON file attached to an email
    Only process it if the res_model is virsat.vr.mails
    """
    _inherit = "ir.attachment"

    def vr_dev(self):
        if self.res_model == 'virsat.vr.mails' and self.mimetype == 'application/json':
            f = base64.b64decode(self.datas).decode("utf-8", "ignore")
            result_json = json.loads(f)
            print("Yes it's JSON", result_json, result_json['DeviceID'])

        if self.res_model == 'virsat.vr.mails' and self.mimetype in ('application/vnd.ms-excel', 'text/csv'):
            # file_extension = self.name.split('.')
            # if file_extension and file_extension[-1] != 'csv':
            #     print("not a csv file.")
            # else:
            #     print("Yes a csv file.")
            # results = csv.DictReader(result_raw.split('\n'))
            # print(results)
            results = [
                {'SessionStart': '2023/04/25 2:30aa'},
                {'SessionStart': '2023/04/25 2:30'},
            ]

            for line in results:
                try:
                    session_start = datetime.strptime(line['SessionStart'], '%Y/%m/%d %H:%M') if line.get('SessionStart') else False
                    print(line, session_start)
                    self.env.cr.commit()
                except Exception as e:
                    _logger.error("Error %s", e)
                    pass

    @api.model
    def create(self, vals):
        res = super(VirsatVrMails, self).create(vals)

        if res.res_model == 'virsat.vr.mails' and res.mimetype in ('application/vnd.ms-excel', 'application/json', 'text/csv'):
            vr_mail = self.env[res.res_model].search([('id', '=', res.res_id)], limit=1)
            game_result_obj = self.env['vr.game.result']
            result_raw = base64.b64decode(res.datas).decode("utf-8", "ignore")
            results = []

            if res.mimetype in ('application/vnd.ms-excel', 'text/csv'):
                results = csv.DictReader(result_raw.split('\n'))

            if res.mimetype == 'application/json':
                results.append(json.loads(result_raw))

            for line in results:
                try:
                    # convert dates
                    session_start = datetime.strptime(line['SessionStart'], '%Y/%m/%d %H:%M') if line.get('SessionStart') else False
                    session_end = datetime.strptime(line['SessionEnd'], '%Y/%m/%d %H:%M') if line.get('SessionEnd') else False
                    reaction_time = session_start + relativedelta(minutes=5) if session_end else False

                    new_game_result = game_result_obj.create({
                        'name': line['UserID'] if line.get('UserID') else False,
                        'device_id': line['DeviceID'] if line.get('DeviceID') else False,
                        'app_version': line['AppVersion'] if line.get('AppVersion') else False,
                        'experience': line['Experience'] if line.get('Experience') else False,
                        'session_start': session_start,
                        'session_end': session_end,
                        'domain': line['Domain'] if line.get('Domain') else False,
                        'replay': line['Replay'] if line.get('Replay') else False,
                        'violation': line['Violation'] if line.get('Violation') else False,
                        'reaction_time': reaction_time,
                        'selection': line['Selection'] if line.get('Selection') else False,
                        'sub_selection': line['SubSelection'] if line.get('SubSelection') else False,
                        'result': line['Result'] if line.get('Result') else False,
                        'gaze_point': line['GazePoint'] if line.get('GazePoint') else False,
                        'view_count': line['ViewCount'] if line.get('ViewCount') else False,
                        'view_time': line['ViewTime'] if line.get('ViewTime') else False,
                        'game_code': line['GameCode'] if line.get('GameCode') else False,
                        'company_code': line['CompanyCode'] if line.get('CompanyCode') else False,
                        'score': line['Score'] if line.get('CompanyCode') else False,
                        'vr_mail_id': vr_mail.id,
                        'attachment_id': res.id,
                    })

                    # create a new record in game result even if no matching pin
                    if new_game_result:
                        vr_mail.message_post(body="Game result created successfully.")
                        _logger.info("New game result added %s", new_game_result.name)

                        # immediately save even if next have issues
                        self.env.cr.commit()

                except Exception as e:
                    vr_mail.message_post(body="Game result not saved. Something went wrong. %s" % e)
                    _logger.error("Game result not saved. Something went wrong. %s", e)
                    pass

        return res
