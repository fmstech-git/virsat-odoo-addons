{
    "name": "Virsat",
    "summary": "VIRSAT Games",
    "version": "16.0.1.0.0",
    "category": "Virtual Reality",
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
        # wizard
        'wizards/vr_trainee_import_wiz.xml',
        'wizards/vr_mails_fetch_wiz.xml',
        # Menu
        'views/menus.xml',
    ],
    "assets": {
        'web.assets_backend': [
            'virsat/static/src/components/**/*.js',
            'virsat/static/src/components/**/*.xml',
            'virsat/static/src/components/**/*.scss',
        ],
    },
    "sequence": 1,
}
