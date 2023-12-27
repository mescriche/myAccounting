__author__ = 'Manuel Escriche'
import argparse, os, sys, json

def collect_codes(data:dict) -> list:
    codes = list()
    for k in data:
        if isinstance(data[k], dict):
            codes.extend(collect_codes(data[k]))
        elif isinstance(data[k], list):
            codes.extend(data[k])
    else: return codes

parser = argparse.ArgumentParser(prog='configApp.py')
parser.add_argument('profile', help="profile to configure the application for the user")
parser.add_argument('user', help="username is used to place configurations files properly")  
parser.add_argument("-c","--dbclean", help="delete database content", action="store_true")
args = parser.parse_args()
#print(args)

print(f"... procesing {args.profile[0]} profile ...")
    


users_dir = 'users'


root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
user_dir = os.path.join(root_dir, users_dir, args.user[0])

source = os.path.join(root_dir, config_dir, f"{args.profile[0]}.json")
print(f'... searching file {source}')

if not os.path.isfile(source):
    print(f"configuration {source} file is not available")
    sys.exit()
    
config_dir = 'configfiles'
config_dir = os.path.join(user_dir, config_dir)
if not os.path.isdir(config_dir):
    print(f"... creating {config_dir}")
    os.makedirs(config_dir)
    
balancefile = 'balance.json'
incomefile = 'income.json'
accountsfile = 'accounts.json'
dbase_file = f'{args.user[0]}_accounting.db'

datafiles_dir = 'datafiles'
datafiles_dir = os.path.join(user_dir, datafiles_dir)
if not os.path.isdir(datafiles_dir):
    print(f"... creating {datafiles_dir}")
    os.makedirs(datafiles_dir)

excelfiles_dir = 'excelfiles'
excelfiles_dir = os.path.join(user_dir, excelfiles_dir)
if not os.path.isdir(excelfiles_dir):
    print(f"... creating {excelfiles_dir}")
    os.makedirs(excelfiles_dir)

dbase_dir = 'dbase'
dbase_dir = os.path.join(user_dir, dbase_dir)
if not os.path.isdir(dbase_dir):
    print(f"... creating {dbase_dir}")
    os.makedirs(dbase_dir)
        
    
with open(source) as _file:
    try: 
        data = json.load(_file)
    except json.decoder.JSONDecodeError as error:
        filename = os.path.basename(source)
        print(f"{filename}:", error)
    else:
        accounts = data['accounts']['accounts']
        acc_real_debit_codes = sorted([acc['code'] for acc in accounts
                                       if acc['content'] == 'REAL' and acc['type'] == 'DEBIT'])
        acc_real_credit_codes = sorted([acc['code'] for acc in accounts
                                        if acc['content'] == 'REAL' and acc['type'] == 'CREDIT'])
        acc_nom_debit_codes = sorted([acc['code'] for acc in accounts
                                      if acc['content'] == 'NOMINAL' and acc['type'] == 'DEBIT'])
        acc_nom_credit_codes = sorted([acc['code'] for acc in accounts
                                       if acc['content'] == 'NOMINAL' and acc['type'] == 'CREDIT'])

        assets_codes = sorted(collect_codes(data['balance']['assets']))
        if assets_codes != acc_real_debit_codes:
            print("Account codes in balance assets  don't correspond with REAL DEBIT account codes ")
            print(f'Balance asset codes = {assets_codes}')
            print(f'Real debit account codes = {acc_real_debit_codes}')
            exit()
            
        claims_codes = sorted(collect_codes(data['balance']['claims']))
        if claims_codes != acc_real_credit_codes:
            print("Account codes in balance claims don't correspond with REAL CREDIT account codes")
            print(f'Balance claim codes = {claims_codes}')
            print(f'Real credit account codes = {acc_real_credit_codes}')
            exit()
            
        inflows_codes = sorted(collect_codes(data['income']['inflows']))
        if inflows_codes != acc_nom_credit_codes:
            print("Account codes in income inflows don't correspond with NOMINAL CREDIT account codes")
            print(f'Income inflows codes = {inflows_codes}')
            print(f'Nominal credit account codes = {acc_nom_credit_codes}')
            exit()
            
        outflows_codes = sorted(collect_codes(data['income']['outflows']))
        if outflows_codes != acc_nom_debit_codes:
            print("Account codes in income outflows don't correspond with NOMINAL DEBIT account codes")
            print(f'Income outflows codes = {outflows_codes}')
            print(f'Nominal debit account codes = {acc_nom_debit_codes}')
            exit()
                        
        target = os.path.join(user_dir, config_dir, accountsfile)
        data['accounts']['profile'] = data['profile']
        with open(target, 'w', encoding='utf-8') as _file:
            json.dump(data['accounts'], _file, ensure_ascii=False, indent=4)
        print(f"... generated accounts file {os.path.basename(target)} ")

        target = os.path.join(user_dir, config_dir, incomefile)
        data['income']['profile'] = data['profile']
        with open(target, 'w', encoding='utf-8') as _file:
            json.dump(data['income'], _file, ensure_ascii=False, indent=4)
        print(f"... generated income file {os.path.basename(target)}")
        
        target = os.path.join(user_dir, config_dir,balancefile)
        data['balance']['profile'] = data['profile']
        with open(target, 'w', encoding='utf-8') as _file:
            json.dump(data['balance'], _file, ensure_ascii=False, indent=4)
        print(f"... generated balance file {os.path.basename(target)}")

            

target =  os.path.join(dbase_dir, dbase_file)
if not os.path.isfile(target):
    with open(target, 'w', encoding='utf-8') as _file:
        pass
    print(f"... created database file: {dbase_file}")
elif args.dbclean:
    with open(target, 'w', encoding='utf-8') as _file:
        pass
    print(f"... cleaned up db file: {dbase_file} .....")
else: pass
