# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VrGameResultReport(models.Model):
    _name = "vr.game.result.report"
    _description = "VR Game Result Report"
    _auto = False
    _rec_name = 'trainee_id'
    _order = 'session_start desc'

    trainee_id = fields.Many2one('vr.trainee', readonly=True, string="PIN")
    trainee_name = fields.Char(readonly=True, groups="virsat.group_view_vr_trainee_name")
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    game_id = fields.Many2one('vr.games', string="Game", readonly=True)
    game_level_id = fields.Many2one('vr.game.levels', string="Level", readonly=True)
    session_start = fields.Datetime()
    session_end = fields.Datetime()
    # score = fields.Integer()
    # passing_score = fields.Integer()
    status = fields.Selection([("pass", "Passed"), ('fail', 'Failed')], readonly=True)

    _depends = {
        'vr.game.result': ['name'],
        'vr.trainee': ['name'],
    }

    @property
    def _table_query(self):
        return '%s %s %s' % (self._select(), self._from(), self._where())

    @api.model
    def _select(self):
        return '''
            SELECT
                line.id,
                trainee.name as trainee_name,
                line.vr_trainee_id as trainee_id,
                line.company_id,
                line.vr_game_id as game_id,
                level.id as game_level_id,
                line.session_start,
                line.session_end,
                line.status as status
        '''

    @api.model
    def _from(self):
        return '''
            FROM vr_game_result line
            LEFT JOIN vr_trainee trainee ON trainee.id = line.vr_trainee_id
            LEFT JOIN vr_game_levels level ON level.code = line.level_code
        '''

    @api.model
    def _where(self):
        return '''
            WHERE line.name IS NOT NULL
        '''
