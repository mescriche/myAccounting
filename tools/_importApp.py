__author__ = 'Manuel Escriche'
import argparse, os, json, sys
root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)
from dbase import db_session, Account, Type, db_get_accounts_gname, db_get_account_code
from view.transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
from datetime import datetime


_ledger_map=dict()
_ledger_map['4176410318201804'] = '12' #credit card- claim
_ledger_map['ES6500730100500528440547'] = '511' # Open Bank current account
_ledger_map['ES8000730100580154738558'] = '512' # Open Bank savings account
_ledger_map['ES3214650100912041170260'] = '513' # Ing invest account
#_ledger__map['HND-IRPF-00'] = '00'

_type_cat_map=dict()
_type_cat_map['credit'] = dict()
_type_cat_map['expense'] = dict()
_type_cat_map['insurance'] = dict()
_type_cat_map['investment'] = dict()
_type_cat_map['revenue'] = dict()
_type_cat_map['saving'] = dict()
_type_cat_map['tax'] = dict()

_type_cat_map['credit']['creditCard']='12'
_type_cat_map['expense']['car-fuel']='631'
_type_cat_map['expense']['car-maintenance']='633'
_type_cat_map['expense']['car-others']='63'
_type_cat_map['expense']['car-parking']='632'
_type_cat_map['expense']['car-toll']='634'
_type_cat_map['expense']['family-accomodation']='615'
_type_cat_map['expense']['family-clothes']='611'
_type_cat_map['expense']['family-connectivity']='614'
_type_cat_map['expense']['family-devices']='25'
_type_cat_map['expense']['family-entertainment']='618'
_type_cat_map['expense']['family-fitness']='612'
_type_cat_map['expense']['family-food']='610'
_type_cat_map['expense']['family-gifts']='61'
_type_cat_map['expense']['family-others']='61'
_type_cat_map['expense']['family-pet']='61'
_type_cat_map['expense']['family-restaurants']='616'
_type_cat_map['expense']['family-transport']='617'
_type_cat_map['expense']['house-connectivity']='625'
_type_cat_map['expense']['house-electricity']='623'
_type_cat_map['expense']['house-furniture']='24'
_type_cat_map['expense']['house-gasoleo']='624'
_type_cat_map['expense']['house-maintenance']='626'
_type_cat_map['expense']['house-others']='62'
_type_cat_map['expense']['house-waste']='622'
_type_cat_map['expense']['house-water']='621'
_type_cat_map['expense']['land-maintenance']='67'
_type_cat_map['expense']['land-water']='67'
_type_cat_map['expense']['me-accomodation']='615'
_type_cat_map['expense']['me-clothes']='611'
_type_cat_map['expense']['me-devices']='25'
_type_cat_map['expense']['me-fitness']='612'
_type_cat_map['expense']['me-food']='610'
_type_cat_map['expense']['me-gifts']='61'
_type_cat_map['expense']['me-health']='612'
_type_cat_map['expense']['me-loteria']='619'
_type_cat_map['expense']['me-others']='61'
_type_cat_map['expense']['me-restaurants']='616'
_type_cat_map['expense']['me-transport']='617'
_type_cat_map['expense']['others-bankCommissions']='646'
_type_cat_map['expense']['others-creditCard']='60'
_type_cat_map['expense']['others-wallet']='60'
_type_cat_map['insurance']['car']='671'
_type_cat_map['insurance']['me']='670'
_type_cat_map['insurance']['others']='67'
_type_cat_map['investment']['family-formación-Manuel']='6132'
_type_cat_map['investment']['family-formación-Miguel']='6131'
_type_cat_map['investment']['funds']='53'
_type_cat_map['investment']['house-elHorno']='20'
_type_cat_map['investment']['house-mora-piso3D']='20'
_type_cat_map['investment']['land-elCoso']='21'
_type_cat_map['investment']['me-formación']='613'
_type_cat_map['investment']['shares']='54'
_type_cat_map['revenue']['discount']='74'
_type_cat_map['revenue']['dividend']='72'
_type_cat_map['revenue']['interest']='73'
_type_cat_map['revenue']['others']='70'
_type_cat_map['revenue']['payroll']='71'
_type_cat_map['revenue']['social insurance']='711'
_type_cat_map['revenue']['regularizacion'] = '75'
_type_cat_map['saving']['account']='512'
_type_cat_map['saving']['pension plan']='26'
_type_cat_map['tax']['car']='662'
_type_cat_map['tax']['house']='66'
_type_cat_map['tax']['irpf']='661'
_type_cat_map['tax']['land']='66'

def main():
    print('Hola')
    root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    datafiles_dir = os.path.join(root_dir, 'datafiles')
    filename = os.path.join(datafiles_dir, 'accounts_db_mev.json')
    with open(filename, 'r') as _file:
        data = json.load(_file)
    #for item in data:
    #    if 'RETENCION HACIENDA' in item['comment']: print(item)
    #exit()
    
    types = frozenset(item['type'] for item in data)
    print('total=', len(data))
    for _type in types:
        n_entries = sum(map(lambda x:x['type'] == _type, data))
        print(f"{_type} = {n_entries}")
        
    remaining = list(filter(lambda x: x['type'] not in types, data))
    for item in remaining: print(item['type'])
    print('remaining =', len(remaining))
    
    ledgers = sorted(frozenset(item['journal'] for item in data))
    years = sorted(frozenset(item['date'][0:4] for item in data))
    with db_session() as db:
        outcome = list()
        for n, entry in enumerate(sorted(data, key=lambda x:datetime.strptime(x['date'], "%Y-%m-%d").date())):
            if entry['journal'] == 'HND-IRPF-00':
                entry['journal'] = 'ES6500730100500528440547'
            ledger_code = _ledger_map[entry['journal']]
            if not ledger_code:
                raise Exception(f'Not ledger code for: {entry}')            
            entry_cat_code = _type_cat_map[entry['type']][entry['category']]
            if not entry_cat_code:
                raise Exception(f'Not category code for: {entry}')
            if entry['type'] == 'expense' and entry['amount'] > 0 : entry_cat_code = '75'
            if 'REGULARIZACION' in entry['comment']: entry_cat_code = '75'
            if 'DEVOLUCIONES TRIBUTARIAS' in entry['comment']: entry_cat_code = '75'
            
            try:
                master_acc = db.query(Account).filter_by(code=ledger_code).one()
                entry_acc = db.query(Account).filter_by(code=entry_cat_code).one()
            except Exception as e:
                print('==> Failed: ',ledger_code, entry_cat_code, entry)
                print(e)
            else:
                date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
                amount = float(entry['amount'])
                description = entry['comment']
                macc_type = master_acc.gname[1]
                if macc_type == 'D': entry1_type = Type.DEBIT if amount > 0 else Type.CREDIT
                elif macc_type == 'C': entry1_type = Type.CREDIT if amount < 0 else Type.DEBIT
                else: raise Exception('Unknown entry type')
                entry2_type = Type.CREDIT if entry1_type == Type.DEBIT else Type.DEBIT
                amount = abs(amount)
                trans = DMTransaction(id=n+1, date=date, description=description,
                                      entries = [DMBookEntry(master_acc.gname, entry1_type, amount),
                                                 DMBookEntry(entry_acc.gname, entry2_type, amount)])
                #print(trans)
                outcome.append(trans)

    #for trans in outcome: print(trans.date.year)
    for year in years:
        year_outcome = list(filter(lambda x: x.date.year == int(year), outcome))
        filename = os.path.join(datafiles_dir, f'accounts_db_new_mev_{year}.json')
        with open(filename ,'w') as _file:
            json.dump(year_outcome, _file, cls=DMTransactionEncoder, indent=4)
            print(f'==> stored {len(year_outcome)} transactions in file {os.path.basename(filename)}')

if __name__ == '__main__':
    main()

