import argparse, os, json
from dbase import db_session, Account
from datetime import datetime


#with db_session() as db:
#    for account in db.query(Account).all():
#        print(account)

_journal_map=dict()
_journal_map['4176410318201804'] = '12'
_journal_map['ES6500730100500528440547'] = '511'
_journal_map['ES8000730100580154738558'] = '512'
_journal_map['ES3214650100912041170260'] = '513'
#_journal_map['HND-IRPF-00'] = '00'

_map=dict()
_map['credit'] = dict()
_map['expense'] = dict()
_map['insurance'] = dict()
_map['investment'] = dict()
_map['revenue'] = dict()
_map['saving'] = dict()
_map['tax'] = dict()

_map['credit']['creditCard']='12'
_map['expense']['car-fuel']='631'
_map['expense']['car-maintenance']='633'
_map['expense']['car-others']='63'
_map['expense']['car-parking']='632'
_map['expense']['family-accomodation']='615'
_map['expense']['family-clothes']='611'
_map['expense']['family-connectivity']='614'
_map['expense']['family-devices']='25'
_map['expense']['family-entertainment']='618'
_map['expense']['family-fitness']='612'
_map['expense']['family-food']='610'
_map['expense']['family-gifts']='61'
_map['expense']['family-others']='61'
_map['expense']['family-pet']='61'
_map['expense']['family-restaurants']='616'
_map['expense']['family-transport']='617'
_map['expense']['house-connectivity']='625'
_map['expense']['house-electricity']='623'
_map['expense']['house-furniture']='24'
_map['expense']['house-gasoleo']='624'
_map['expense']['house-maintenance']='626'
_map['expense']['house-others']='62'
_map['expense']['house-waste']='622'
_map['expense']['house-water']='621'
_map['expense']['land-maintenance']='67'
_map['expense']['land-water']='67'
_map['expense']['me-accomodation']='615'
_map['expense']['me-clothes']='611'
_map['expense']['me-devices']='25'
_map['expense']['me-fitness']='612'
_map['expense']['me-food']='610'
_map['expense']['me-gifts']='61'
_map['expense']['me-health']='612'
_map['expense']['me-loteria']='619'
_map['expense']['me-others']='61'
_map['expense']['me-restaurants']='616'
_map['expense']['me-transport']='617'
_map['expense']['others-bankCommissions']='646'
_map['expense']['others-creditCard']='60'
_map['expense']['others-wallet']='60'
_map['insurance']['car']='671'
_map['insurance']['me']='670'
_map['insurance']['others']='67'
_map['investment']['family-formación-Manuel']='6132'
_map['investment']['family-formación-Miguel']='6131'
_map['investment']['funds']='53'
_map['investment']['house-elHorno']='20'
_map['investment']['house-mora-piso3D']='20'
_map['investment']['land-elCoso']='21'
_map['investment']['me-formación']='613'
_map['investment']['shares']='54'
_map['revenue']['discount']='74'
_map['revenue']['dividend']='72'
_map['revenue']['interest']='73'
_map['revenue']['others']='70'
_map['revenue']['payroll']='71'
_map['revenue']['social insurance']='711'
_map['saving']['account']='512'
_map['saving']['pension plan']='26'
_map['tax']['car']='662'
_map['tax']['house']='66'
_map['tax']['irpf']='661'
_map['tax']['land']='66'

def print_map():
    for key in _map:
        for subkey in _map[key]:
            print(key, subkey, _map[key][subkey])

def label_trans(debit_acc, nom_acc, entry): #between one debit real account and  nominal accounts
    trans = dict()
    trans['description'] = 'label:' + entry['comment']
    trans['date'] = entry['date']
    entries = list()
    if entry['amount'] > 0:
        entries.append({"account":debit_acc.gname,  "debit": entry['amount'],  "credit": 0.0})  
        entries.append({"account":nom_acc.gname ,   "debit":0.0,               "credit": entry['amount']})
    elif entry['amount'] < 0: 
        entries.append({"account":debit_acc.gname,  "debit": 0.0,                   "credit":abs(entry['amount'])})   
        entries.append({"account":nom_acc.gname ,   "debit": abs(entry['amount']),  "credit":0.0}) 
    else: pass
    trans['entries'] = entries
    #return json.dumps(trans, indent=4)
    return trans

def assets_trans(debit1_acc, debit2_acc, entry): #between two real debit accounts
    trans = dict()
    trans['description'] = 'assets_trans :' + entry['comment']
    trans['date'] = entry['date']
    entries = list()
    if entry['amount'] > 0:
        entries.append({"account":debit1_acc.gname,  "debit": entry['amount'],  "credit": 0.0})  
        entries.append({"account":debit2_acc.gname , "debit": 0.0,              "credit": entry['amount']})
    elif entry['amount'] < 0: 
        entries.append({"account":debit1_acc.gname,  "debit": 0.0,                  "credit":abs(entry['amount'])})   
        entries.append({"account":debit2_acc.gname , "debit": abs(entry['amount']), "credit":0.0}) 
    else: pass
    trans['entries'] = entries
    #return json.dumps(trans, indent=4)
    return trans
    
def expense(journal_acc, cat_acc, entry):
    return label_trans(journal_acc, cat_acc, entry)

def income(journal_acc, cat_acc, entry):
    return label_trans(journal_acc, cat_acc, entry)
                       
def claim(credit_acc, debit_acc, entry):
    trans = dict()
    trans['description'] = 'claim: '+ entry['comment']
    trans['date'] = entry['date']
    entries = list()        
    if entry['amount'] > 0:
        entries.append({"account":credit_acc.gname,   "debit":entry['amount'],  "credit":0.0})   
        entries.append({"account":debit_acc.gname,    "debit":0.0,  "credit":entry['amount']})  
    elif entry['amount'] < 0:
        entries.append({"account":credit_acc.gname,   "debit":0.0,  "credit": abs(entry['amount'])}) 
        entries.append({"account":debit_acc.gname ,   "debit":abs(entry['amount']) ,  "credit": 0.0})
    else: pass
    trans['entries'] = entries
    #return json.dumps(trans, indent=4)
    return trans
    

def main():
    print('Hola')
    DIR = os.path.dirname(os.path.realpath(__file__))
    DIR = os.path.join(DIR, 'datafiles')
    filename = os.path.join(DIR, 'accounts_db_mev.json')
    with open(filename, 'r') as _file:
        data = json.load(_file)
    #types = ('expense', 'tax', 'revenue', 'investment', 'saving', 'insurance', 'credit')
    types = frozenset(item['type'] for item in data)
    print('total=', len(data))
    for _type in types:
        n_entries = sum(map(lambda x:x['type'] == _type, data))
        print(f"{_type} = {n_entries}")
        
    remaining = list(filter(lambda x: x['type'] not in types, data))
    for item in remaining: print(item['type'])
    print('remaining =', len(remaining))
    
    #for _type in types:
    #    _data = list(filter(lambda x:x['type'] == _type, data))
    #    categories = sorted(frozenset(item['category'] for item in _data))
    #    print(f"{_type:_^60}")
    #    for _cat in categories:
    #        value = _map[_type][_cat]
    #        print(f"_map['{_type}']['{_cat}']='{value}'")
    #    print('n_cat=', len(categories), ' n_items=', len(_data))
    #    eval(f'transform_{_type}(_data)')
    journals = sorted(frozenset(item['journal'] for item in data))
    #for journal in journals: print('journal=', journal)
    years = sorted(frozenset(item['date'][0:4] for item in data))
    with db_session() as db:
        outcome = list()
        for entry in sorted(data, key=lambda x:datetime.strptime(x['date'], "%Y-%m-%d")):
            entry['date'] = datetime.strptime(entry['date'], '%Y-%m-%d').date()
            entry['date'] = datetime.strftime(entry['date'], '%d-%m-%Y')
            if entry['journal'] == 'HND-IRPF-00':
                entry['journal'] = 'ES6500730100500528440547'
            journal_code = _journal_map[entry['journal']]
            if not journal_code: raise Exception(f'Not journal code for: {entry}')
            cat_code = _map[entry['type']][entry['category']]
            if not cat_code: raise Exception(f'Not category code for: {entry}')
            try:
                journal_acc = db.query(Account).filter_by(code=journal_code).one()
                cat_acc = db.query(Account).filter_by(code=cat_code).one()
            except Exception as e:
                print('==> Failed: ',journal_code, cat_code, entry)
                print(e)
            else:
                #print(journal_acc.gname, cat_acc.gname)
                #print(f"{entry['date']}, amount={entry['amount']}, {entry['comment']}")
                if   cat_code[0] == '1':
                    #print('==> Claims')
                    outcome.append(claim(journal_acc, cat_acc, entry))
                elif cat_code[0] == '2':
                    #print('==> Fixed Assets')
                    outcome.append(assets_trans(journal_acc, cat_acc, entry))
                elif cat_code[0] == '5':
                    #print('==> Bank Assets')
                    outcome.append(assets_trans(journal_acc, cat_acc, entry))
                elif cat_code[0] == '6':
                    #print('==> Expense')
                    outcome.append(expense(journal_acc, cat_acc, entry))
                elif cat_code[0] == '7':
                    #print('==> Income')
                    outcome.append(income(journal_acc, cat_acc, entry))
                else: print('==> Unknown')

    for year in years:
        year_outcome = list(filter(lambda x: x['date'][6:10] == year, outcome))
        
        filename = os.path.join(DIR, f'accounts_db_new_mev_{year}.json')
        with open(filename ,'w') as _file:
            _file.write(json.dumps(year_outcome, indent=4))
            print(f'==> generated file {os.path.basename(filename)}')
    else:
        filename = os.path.join(DIR, f'accounts_db_new_mev.json')
        with open(filename ,'w') as _file:
            _file.write(json.dumps(outcome, indent=4))
            print(f'==> generated file {os.path.basename(filename)}')        
            

if __name__ == '__main__':
    main()

