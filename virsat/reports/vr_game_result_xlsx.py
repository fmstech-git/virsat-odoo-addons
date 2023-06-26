# -*- coding: utf-8 -*-
from odoo import models


class VrGameResultXlsx(models.AbstractModel):
    _name = 'report.virsat.vr_game_result_xlsx'
    _description = 'VR Game Result XLSX'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, game_result):
        row = 0
        sheet = workbook.add_worksheet("Training Result")

        # formats
        bold = workbook.add_format({'bold': True})\

        # column width
        sheet.set_column('A:A', 5)
        sheet.set_column('B:G', 20)

        # headers
        sheet.write(row, 0, "PIN", bold)
        sheet.write(row, 1, "Training Module", bold)
        sheet.write(row, 2, "Session Start", bold)
        sheet.write(row, 3, "Session End", bold)
        sheet.write(row, 4, "Challenge", bold)
        sheet.write(row, 5, "Selection", bold)
        sheet.write(row, 6, "Score", bold)
        sheet.write(row, 7, "Status", bold)

        row += 1

        for game in game_result:
            sheet.write(row, 0, game.pin)
            sheet.write(row, 1, game.game_id.name)
            sheet.write(row, 2, game.session_start.strftime("%d/%m/%Y %H:%M:%S"))
            sheet.write(row, 3, game.session_end.strftime("%d/%m/%Y %H:%M:%S"))
            sheet.write(row, 4, game.challenge_id.name)
            sheet.write(row, 5, game.selection)
            sheet.write(row, 6, game.score)
            sheet.write(row, 7, game.remark)
            row += 1

        if game_result:
            game = game_result[0]
            challenge_ids = game_result.mapped('challenge_id.id')
            challenges = self.env['vr.game.challenges'].search([('game_id', '=', game.game_id.id), ('id', 'not in', challenge_ids)])
            for c in challenges:
                sheet.write(row, 0, game.pin)
                sheet.write(row, 1, game.game_id.name)
                sheet.write(row, 2, game.session_start.strftime("%d/%m/%Y %H:%M:%S"))
                sheet.write(row, 3, game.session_end.strftime("%d/%m/%Y %H:%M:%S"))
                sheet.write(row, 4, c.name)
                sheet.write(row, 5, "")
                sheet.write(row, 6, "")
                sheet.write(row, 7, "Incomplete")
                row += 1
