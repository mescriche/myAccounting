__author__ = 'Manuel Escriche'

import re, json

class Paths:
    rules = {
        'balance': r'[1-5]',
        'claims' : r'1',  'debt': r'12',
        'assets': r'[2,5]', 'fixed': r'2[0-9]', 'current': r'5[0-9]',
        ###
        'income': r'[6-7]',
        'output': r'6', 'expense': r'6[0-5]','tax':r'66', 'insurance': r'67',
        'input': r'7', 'revenue':r'7'
    }
    
    def __init__(self, user):
        self.user = user
        #with open(self.user.rules_file) as _file:
        #    self.rules = json.load(_file)
            
    def find_root(self, label):
        if label not in Paths.rules.keys():
            raise Exception(f'No valid label:{label}')
        codes = list()
        for code in range(10,100):
            match=re.match(Paths.rules[label], str(code))
            if match: codes.append(str(code))
        else:
            paths = [self.find_path(code) for code in codes]
            heads = [path.split('/')[0] for path in paths]
            u_paths = list(dict.fromkeys(heads))
            return u_paths[0]

    def find_path(self, code:str) -> str:
        match = re.fullmatch(r'\d{2,4}', code)
        if not match:
            raise Exception(f'No valid code: {code}')
        path = list()    
        for key in Paths.rules:
            match = re.match(Paths.rules[key], code)
            if match: path.append(key)
        else:
            path = '/'.join(path)
            return path

    def find_paths_for_codes(self, label, codes:list):
        print('codes:', codes)
        data = {code:self.find_path(code) for code in codes}
        for k,v in data.items():
            chunks = v.split('/')
            ndx = chunks.index(label)+2
            data[k] = '/'.join(chunks[:ndx])
        paths = list(dict.fromkeys(data.values()))
        out = dict()
        for path in paths:
            out[path] = [k for k,v in data.items() if v==path]
        print('output:', out)
        return out

    def find_codes(self, label):
        if label not in Paths.rules.keys():
            raise Exception(f'No valid label:{label}')
        codes = list()
        for code in range(10,100):
            match = re.match(Paths.rules[label], str(code))
            if match: codes.append(str(code))
        else:
            return codes
        


def find_path_by_code(code, rules:dict) -> list:
    match = re.fullmatch(r'\d{2,4}', code)
    if not match:
        raise Exception(f'No valid code: {code}')
    path = list()    
    for key in rules:
        match = re.match(Paths.rules[key], code)
        if match: path.append(key)
    else:
        path = '/'.join(path)
        #print('find_path_by_code', path)
        return path

def find_paths_by_label(label, rules:dict) -> list:
    if label not in Paths.rules.keys():
        raise Exception(f'No valid label:{label}')
    paths = list(dict.fromkeys([find_path_by_code(str(code)) for code in range(10,100)]))
    paths = [path for path in paths if label in path]
    #print(paths)
    #paths = [path for path in paths if path.partition(label)[2].count('/') <=1 ]
    paths.sort()    
    print(f'find_paths_by_label: {label} = ', paths)
    return paths

def find_paths_for_codes(codes:list, rules:dict):
    data = {code:find_path_by_code(code) for code in codes}
    paths = list(dict.fromkeys(data.values()))
    out = dict()
    for path in paths:
        out[path] = [k for k,v in data.items() if v==path]
    return out

def find_root(paths:list) -> str:
    parents = [path.split('/')[0] for path in paths]
    parents = list(dict.fromkeys(parents))
    return parents[0]

def find_codes_by_label(key, rules:dict) -> list:
    if key not in rules.keys():
        raise Exception(f'No valid label:{label}')
    codes = list()
    for code in range(10,100):
        match = re.match(rules[key], str(code))
        if match: codes.append(str(code))
    else:
        return codes
            
        
