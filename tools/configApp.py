__author__ = 'Manuel Escriche'
import argparse, os, json

def collect_codes(data:dict) -> list:
    codes = list()
    for k in data:
        if isinstance(data[k], dict):
            codes.extend(collect_codes(data[k]))
        elif isinstance(data[k], list):
            codes.extend(data[k])
    else: return codes

parser = argparse.ArgumentParser(prog='configApp.py')
parser.add_argument('profile', choices=['student', 'senior'], help="profile to configure the application")
parser.add_argument("-u", '--user', nargs=1, help="username used to find out configuration <profile>_<username>.json file")  
parser.add_argument("-c","--dbclean", help="delete db content", action="store_true")
args = parser.parse_args()
#print(args)

if args.user:
    basename = f'{args.profile}_{args.user[0]}'
    print(f'... procesing {args.profile} profile for user {args.user[0]} ...')
else:
    basename = f'{args.profile}'
    print("... procesing {} profile ...".format(args.profile))
    

config_dir = 'configfiles'
view_dir = 'view'
dbase_dir = 'dbase'
tools_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(tools_dir)
config_dir = os.path.join(root_dir, config_dir)

source = os.path.join(config_dir, f"{basename}.json")
print(f'... searching file {source}')

balancefile = 'balance.json'
incomefile = 'income.json'
accountsfile = 'accounts.json'

if not os.path.isfile(source):
    print(f"{source} file is not available")
else:
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
                        
            target = os.path.join(root_dir, dbase_dir, accountsfile)
            data['accounts']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['accounts'], _file, ensure_ascii=False, indent=4)
            print(f"... generated file {os.path.basename(target)} ")
                  
            target = os.path.join(root_dir,view_dir,balancefile)
            data['balance']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['balance'], _file, ensure_ascii=False, indent=4)
            print(f"... generated file {os.path.basename(target)}")

            target = os.path.join(root_dir,view_dir, incomefile)
            data['income']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['income'], _file, ensure_ascii=False, indent=4)
            print(f"... generated file {os.path.basename(target)}")
            

if args.dbclean:
    filename = 'accounting.db'
    target = os.path.join(root_dir, dbase_dir, filename)
    if os.path.isfile(target):
        with open(target, 'w', encoding='utf-8') as _file:
            pass
        print(f"... cleaned up db file: {os.path.basename(target)} .....")
