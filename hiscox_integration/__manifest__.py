{
    'name': 'Hiscox Insurance Integration',
    'version': '1.0',
    'summary': 'Integrate customer applications with Hiscox API',
    'description': 'This module provides API integration for insurance processing with Hiscox.',
    'author': 'Disa',
    'category': 'Insurance',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hiscox_case_views.xml',
        'views/actions.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}