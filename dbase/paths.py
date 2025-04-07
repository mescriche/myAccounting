__author__ = 'Manuel Escriche'

import re

def find_path(code:str) -> str:
    rules = {
        #'balance': r'[1-5]',
        'claims' : r'1',  'debt': r'12',
        'assets': r'[2,5]', 'fixed': r'2[0-9]', 'current': r'5[0-9]',
        ###
        #'income': r'[6-7]',
        'output': r'6', 'expense': r'6[0-5]','tax':r'66', 'insurance': r'67',
        'input': r'7', 'revenue':r'7'
    }
    if match := re.fullmatch(r'\d{2,4}', code):
        path = list()    
        for key in rules:
            if match := re.match(rules[key], code):
                path.append(key)
        else:
            path = '/'.join(path)
            return path
    else:
        raise Exception(f'No valid code: {code}')
