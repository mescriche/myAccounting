__author__ = 'Manuel Escriche'
import argparse, os, json

parser = argparse.ArgumentParser(prog='configApp.py')
parser.add_argument('profile', choices=['student', 'senior'], help="profile to configure the application")
parser.add_argument("-c","--dbclean", help="delete db content", action="store_true")
args = parser.parse_args()
print("... procesing {} profile ...".format(args.profile))

config_dir = 'config'
view_dir = 'view'
dbase_dir = 'dbase'
tools_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(tools_dir)
config_dir = os.path.join(root_dir, config_dir)
source = os.path.join(config_dir, f"{args.profile}.json")

balancefile = 'balance.json'
incomefile = 'income.json'
accountsfile = 'accounts.json'

if args.dbclean:
    filename = 'accounting.db'
    target = os.path.join(root_dir, dbase_dir, filename)
    if os.path.isfile(target):
        with open(target, 'w', encoding='utf-8') as _file:
            pass
        print(f"... cleaned up db file: {os.path.basename(target)} .....")

if not os.path.isfile(source):
    print("{} profile is not available".format(args.profile))
else:
    with open(source) as _file:
        try: 
            data = json.load(_file)
        except json.decoder.JSONDecodeError as error:
            filename = os.path.basename(source)
            print(f"{filename}:", error)
        else:
            target = os.path.join(root_dir, dbase_dir, accountsfile)
            data['accounts']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['accounts'], _file, ensure_ascii=False, indent=4)
            print("... generated {} file ...".format(os.path.basename(target)))
                  
            target = os.path.join(root_dir,view_dir,balancefile)
            data['balance']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['balance'], _file, ensure_ascii=False, indent=4)
            print("... generated {} file ...".format(os.path.basename(target)))

            target = os.path.join(root_dir,view_dir, incomefile)
            data['income']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['income'], _file, ensure_ascii=False, indent=4)
            print("... generated {} file ...".format(os.path.basename(target)))
            
