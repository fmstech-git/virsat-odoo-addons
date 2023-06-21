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
            try:
                game_result_obj = self.env['vr.game.result']
                result_raw = base64.b64decode(res.datas).decode("utf-8", "ignore")
                results = []

                if res.mimetype in ('application/vnd.ms-excel', 'text/csv'):
                    results = csv.DictReader(result_raw.split('\n'))

                if res.mimetype == 'application/json':
                    results.append(json.loads(result_raw))

                # game session needed variables
                game_session_obj = self.env['vr.game.sessions']
                game_obj = self.env['vr.games']
                challenge_obj = self.env['vr.game.challenges']
                company_code = ''
                game = {}
                existing_game = {}
                new_session = {}
                new_game_result_ids = []

                for line in results:
                    try:
                        # add new session but make sure only single entry will be created
                        challenge_code = line.get('Violation', 'False')
                        if not challenge_code or challenge_code.strip() in ('N/A', 'False', False, ''):
                            challenge_code = line.get('LevelCode', False)
                        game_code = line.get('GameCode', False)
                        challenge = challenge_obj.search([('code', '=', challenge_code)])

                        # if challenge not exist, add a log note
                        if not challenge:
                            vr_mail.message_post(body="Challenge code (%s) doesn't exist." % challenge_code)

                        game_ids = challenge.mapped('game_id.id')
                        # game = game_obj.search([('id', 'in', game_ids)], limit=1)
                        if game_code and game_code.strip() not in ('N/A', 'False', False, ''):
                            game = game_obj.search([('id', 'in', game_ids), ('code', '=', game_code)], limit=1)

                        # add log not if challenge code doesn't belong to any games
                        if not game:
                            vr_mail.message_post(body="No game matching with the challenge code (%s)." % challenge_code)

                        if game_code and game:
                            company_code = game.company_id.company_code if game else False

                            if not existing_game:
                                existing_game = game

                        if not new_session:
                            new_session = game_session_obj.create({
                                'name': line.get('UserID', False),
                                'session_start_str': line.get('SessionStart', False),
                                'session_end_str': line.get('SessionEnd', False),
                                'vr_mail_id': vr_mail.id,
                            })

                        game_data = {
                            'name': line.get('UserID', False),
                            'device_id': line.get('DeviceID', False),
                            'app_version': line.get('AppVersion', False),
                            'experience': line.get('Experience', False),
                            'game_code': game_code,
                            'vr_game_id': game.id if game else False,
                            'session_id': line.get('SessionID', False),
                            'game_session_id': new_session and new_session.id or False,
                            'session_start_str': line.get('SessionStart', False),
                            'session_end_str': line.get('SessionEnd', False),
                            'domain': line.get('Domain', False),
                            'replay': line.get('Replay', False),
                            'challenge_code': challenge_code,
                            'selection': line.get('Selection').strip() if line.get('Selection', False) else False,
                            'sub_selection': line.get('SubSelection', False),
                            'score_str': line.get('Score', False),
                            'remark': line.get('Status', False),
                            'gaze_point': line.get('GazePoint', False),
                            'view_count': line.get('ViewCount', False),
                            'reaction_time_str': line.get('ReactionTime', False),
                            'view_time_str': line.get('ViewTime', False),
                            'vr_mail_id': vr_mail.id,
                            'attachment_id': res.id,
                        }

                        new_game_result = game_result_obj.create(game_data)

                        # create a new record in game result even if no matching pin
                        if new_game_result:
                            new_game_result_ids.append(new_game_result.id)

                            # immediately save even if next have issues
                            self.env.cr.commit()

                    except Exception as e:
                        vr_mail.message_post(body="Game result not saved. Something went wrong. %s" % e)
                        _logger.error("Game result not saved. Something went wrong. %s", e)
                        pass

                # update game result
                if new_game_result_ids and existing_game and company_code:
                    # update company code
                    game_result_obj.browse(new_game_result_ids).write({'company_code': company_code})

                    # update result which doesn't have game
                    no_game_id = game_result_obj.browse(new_game_result_ids).filtered(lambda g: not g.vr_game_id)
                    no_game_id.write({'vr_game_id': existing_game.id})

                # update game session
                if new_session and existing_game:
                    new_session.write({'company_code': company_code,
                                       'game_id': existing_game.id,
                                       'status_compute_type': existing_game.status_compute_type,
                                       'status_compute_qty': existing_game.status_compute_qty,
                                       })
                    # compute the status
                    new_session.compute_status()

                vr_mail.update({'company_code': company_code})

                if new_game_result_ids:
                    vr_mail.message_post(body="Game result created successfully %s." % new_game_result_ids)
                    _logger.info("======= Game result created successfully %s =======", new_game_result_ids)

            except Exception as e:
                vr_mail.message_post(body="Game result not saved. Something went wrong. %s" % e)
                _logger.error("Game result not saved. Something went wrong. %s", e)
                pass

        return res
