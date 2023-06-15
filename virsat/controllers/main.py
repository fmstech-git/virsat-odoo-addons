# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class Virsat(http.Controller):
    @http.route('/virsat/selected-companies', type='json', auth='user')
    def get_selected_companies(self):
        cids = request.httprequest.cookies.get('cids', str(request.env.user.company_id.id))
        allowed_company_ids = [int(cid) for cid in cids.split(',')]

        return allowed_company_ids

    @http.route('/virsat/statistics', type='json', auth='user')
    def get_statistics(self):
        allowed_company_ids = self.get_selected_companies()
        print(allowed_company_ids)

        games = request.env['vr.games'].search([('company_id', 'in', allowed_company_ids)])
        trainees = request.env['vr.trainee'].search([('company_id', 'in', allowed_company_ids)])
        game_sessions = request.env['vr.game.sessions'].search([('company_id', 'in', allowed_company_ids)])
        game_sessions_stats = {'Passed': 0, 'Failed': 0}
        for g in game_sessions:
            game_sessions_stats['Passed'] += 1 if g.status == 'passed' else 0
            game_sessions_stats['Failed'] += 1 if g.status == 'failed' else 0

        return {
            "games": len(games),
            "trainees": len(trainees),
            "sessions": len(game_sessions),
            "sessions_stats": game_sessions_stats,
        }
