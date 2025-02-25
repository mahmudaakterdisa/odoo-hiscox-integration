{
    'name': 'Hiscox Insurance Integration',
    'version': '1.0',
    'summary': 'Integrate customer applications with Hiscox API',
    'author': 'Disa',
    'category': 'Insurance',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hiscox_case_views.xml',
    ],
    'installable': True,
    'application': True,
}