{
    "name": "Virsat Theme",
    "summary": "VIRSAT Theme",
    "version": "16.0.1.0.0",
    "category": "Virtual Reality",
    "website": "https://virsat.com",
    "author": "VIRSAT",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "depends": ["base", "web"],
    "maintainers": [],
    "excludes": [],
    "data": [
        "views/res_company.xml",
        "views/web_layout.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            'virsat_theme/static/src/scss/styles.scss',
        ],
        'web._assets_primary_variables': [
            ('after', 'web/static/src/scss/primary_variables.scss', 'virsat_theme/static/src/scss/primary_variables.scss'),
        ],
    },
    "sequence": 1,
}
