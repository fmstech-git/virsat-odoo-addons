# Copyright 2016-2017 LasLabs Inc.
# Copyright 2017-2018 Tecnativa - Jairo Llopis
# Copyright 2018-2019 Tecnativa - Alexandre Díaz
# Copyright 2021 ITerra - Sergey Shebanin
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Virsat",
    "summary": "VIRSAT Games",
    "version": "15.0.1.0.0",
    "category": "Website",
    "website": "https://virsat.com",
    "author": "VIRSAT",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "mail", "web", "report_xlsx"],
    "development_status": "Production/Stable",
    "maintainers": [],
    "excludes": [],
    "data": [
        # security
        'security/vr_groups.xml',
        'security/vr_security.xml',
        'security/ir.model.access.csv',
        # reports
        'reports/excel_reports.xml',
        # views
        'views/vr_mails.xml',
        'views/vr_game_result.xml',
        'views/vr_trainee.xml',
        'views/vr_games.xml',
        'views/res_company.xml',
        'views/webclient_templates.xml',
        'views/themes.xml',
        # wizard
        'wizards/vr_trainee_import_wiz.xml',
        'wizards/vr_mails_fetch_wiz.xml',
        # Menu
        'views/menus.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            'virsat/static/src/scss/*.scss',
        ],
        "web.assets_backend": [],
        "web.assets_qweb": [],
    },
    "sequence": 1,
}
