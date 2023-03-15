import argparse, os, json

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="profile to configure the application")
args = parser.parse_args()
print("... procesing {} profile ...".format(args.profile))

config_dir = 'config'
view_dir = 'view'
dbase_dir = 'dbase'
current_dir = os.path.dirname(os.path.realpath(__file__))
config_dir = os.path.join(current_dir, config_dir)
source = os.path.join(config_dir, f"{args.profile}.json")

balancefile = 'balance.json'
incomefile = 'income.json'
accountsfile = 'accounts.json'


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
            target = os.path.join(current_dir, dbase_dir, accountsfile)
            data['accounts']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['accounts'], _file, ensure_ascii=False, indent=4)
            print("... generated {} file ...".format(os.path.basename(target)))
                  
            target = os.path.join(current_dir,view_dir,balancefile)
            data['balance']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['balance'], _file, ensure_ascii=False, indent=4)
            print("... generated {} file ...".format(os.path.basename(target)))

            target = os.path.join(current_dir,view_dir, incomefile)
            data['income']['profile'] = data['profile']
            with open(target, 'w', encoding='utf-8') as _file:
                json.dump(data['income'], _file, ensure_ascii=False, indent=4)
            print("... generated {} file ...".format(os.path.basename(target)))
            
    



#def config():
#if __name__ == '__main__':
#    config()
