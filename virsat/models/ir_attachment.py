from odoo import fields, models, api
import base64
import csv
import json
from datetime import datetime
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
                    print(line.get('asdfasdf', False))
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

            # game session needed variables
            game_session_obj = self.env['vr.game.sessions']
            ctr = 0
            new_session = False

            for line in results:
                print(line)
                try:
                    # add new session but make sure only single entry will be created
                    ctr += 1
                    if ctr == 1:
                        new_session = game_session_obj.create({
                            'name': line.get('UserID', False),
                            'company_code': line.get('CompanyCode', False),
                            'session_start_str': line.get('SessionStart', False),
                            'session_end_str': line.get('SessionEnd', False),
                            'vr_mail_id': vr_mail.id,
                        })

                    game_data = {
                        'name': line.get('UserID', False),
                        'company_code': line.get('CompanyCode', False),
                        'device_id': line.get('DeviceID', False),
                        'app_version': line.get('AppVersion', False),
                        'experience': line.get('Experience', False),
                        'game_code': line.get('GameCode', False),
                        'level_code': line.get('LevelCode', False),
                        'session_id': line.get('SessionID', False),
                        'game_session_id': new_session and new_session.id or False,
                        'session_start_str': line.get('SessionStart', False),
                        'session_end_str': line.get('SessionEnd', False),
                        'domain': line.get('Domain', False),
                        'replay': line.get('Replay', False),
                        'violation': line.get('Violation', False),
                        'selection': line.get('Selection', False),
                        'sub_selection': line.get('SubSelection', False),
                        'score': line.get('Score', False),
                        # 'status': line['Status'].lower() if line.get('Status') else False,
                        'remark': line.get('Status', False),
                        'gaze_point': line.get('GazePoint', False),
                        'view_count': line.get('ViewCount', False),
                        'reaction_time_str': line.get('ReactionTime', False),
                        'view_time_str': line.get('ViewTime', False),
                        'vr_mail_id': vr_mail.id,
                        'attachment_id': res.id,
                    }

                    new_game_result = game_result_obj.create(game_data)
                    vr_mail.update({'company_code': line.get('CompanyCode', False)})

                    # create a new record in game result even if no matching pin
                    if new_game_result:
                        vr_mail.message_post(body="Game result created successfully (ID: %s)." % new_game_result.id)
                        _logger.info("New game result added %s", new_game_result.name)

                        # immediately save even if next have issues
                        self.env.cr.commit()

                except Exception as e:
                    vr_mail.message_post(body="Game result not saved. Something went wrong. %s" % e)
                    _logger.error("Game result not saved. Something went wrong. %s", e)
                    pass

        return res
