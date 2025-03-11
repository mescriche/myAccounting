__author__ = 'Manuel Escriche'

import re

rules = {
    'balance': r'[1-5]',
    'claim' : r'1',  'debt': r'12',
    'asset': r'[2,5]', 'fixed': r'2[0-9]', 'current': r'5[0-9]',
    ###
    'income': r'[6-7]',
    'output': r'6',
    'expense': r'6[0-5]','persons': r'61','house': r'62','vehicle':r'63','services':r'64','land':r'65',
    'tax':r'66',
    'insurance': r'67',
    'input': r'7', 'revenue':r'7'
}

def find_groups(code, rules:dict=rules) -> tuple:
    match = re.fullmatch(r'\d{2,4}', code)
    if not match:
        raise Exception(f'No valid code: {code}')
    groups = list()    
    for key in rules:
        match = re.match(rules[key], code)
        if match: groups.append(key)
    else:
        return groups
