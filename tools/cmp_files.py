__author__ = 'Manuel Escriche'
import argparse, os, sys, json, textwrap
root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)
from datamodel.transaction import DMTransaction

parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    Tool useful to compare json transactions files; especifically, year_<tag>_seats.json file against year_app_seats.json file.
    '''))
parser.add_argument('user', help="user")
parser.add_argument('year', help="files' year")
parser.add_argument('-t', "--tag" , nargs='?', help="file's tag - format: year_<tag>_seats.json; <user> works as default tag  ")
parser.add_argument('-m', "--map", action='store_true', help='print comparation map')
parser.add_argument('-p', "--print" , metavar='Tid', type=int, nargs='+', action='store',
                    help='print transactions from tag file first, and app file second. examples: -p 1; -p 2 3; -p 0 23')
args=parser.parse_args()
print(args)
                    
user_dir = os.path.join(root_dir, 'users', args.user)
datafiles_dir = os.path.join(user_dir, 'datafiles')

if not args.tag: args.tag = args.user 

tag_file = os.path.join(datafiles_dir, f'{args.year}_{args.tag}_seats.json')
app_file = os.path.join(datafiles_dir, f'{args.year}_app_seats.json')

tag_data = list()
if os.path.exists(tag_file):
    with open(tag_file, 'r') as _file:
        try: data = json.loads(_file.read())
        except Exception as e:
            print(e)
            exit()
        else:
            data.sort(key=lambda x:(x['date'], x['description']))
            for n,item in enumerate(data,start=1):
                try: trans = DMTransaction.from_json(item)
                except Exception as e:
                    print(e)
                    break
                else:
                    trans.id = 0
                    tag_data.append(trans)
            else:
                print(f"{os.path.basename(tag_file)}: {len(tag_data)} transactions")
                
app_data = list()
if os.path.exists(app_file):
    with open(app_file, 'r') as _file:
        try: data = json.loads(_file.read())
        except Exception as e:
            print(e)
            exit()
        else:
            data.sort(key=lambda x:(x['date'], x['description']))
            for n,item in enumerate(data, start=1):
                try: trans = DMTransaction.from_json(item)
                except Exception as e:
                    print(e)
                    break
                else:
                    trans.id = 0
                    app_data.append(trans)
            else:
                print(f"{os.path.basename(app_file)}: {len(app_data)} transactions")
                
_match = list()
_removed = list()
for m,x in enumerate(tag_data, start=1):
    for n,y in enumerate(app_data, start=1):
        if y.id: continue
        if x == y:
            y.id = 1
            _match.append((m,n,'OK'))
            break
    else:
        _removed.append(m)
_added = list()
for n,y in enumerate(app_data, start=1):
    y.id = n
    for m,x in enumerate(tag_data, start=1):
        x.id = y.id
        _test = x == y
        x.id = m
        if _test: break
    else: _added.append(n)
print('------------')    
print(f'>>> {len(_match)} transactions are equal to both files')
print(f'>>> {len(_removed)} transactions removed from file: {os.path.basename(tag_file)}')
print(f'>>> {len(_added)} transactions added to file: {os.path.basename(app_file)}')
print('------------')
if (len(tag_data) == len(_match)):
    print(f'>>> {os.path.basename(tag_file)} IS INCLUDED IN {os.path.basename(app_file)}')

###
if args.map:
    if len(_match):
        print(f'>>> matching map')
        for item in sorted(_match, key=lambda x:x[0]): print(item)
    if len(_removed):
        print(f'>>> removed from {os.path.basename(tag_file)}')
        for item in sorted(_removed): print(item)
    if len(_added):
        print(f'>>> added to {os.path.basename(app_file)}')
        for item in sorted(_added):print(item)
                                  
###
if args.print:
    print('--------------')
    print(f'>>> printing transactions #{args.print}')
    if len(args.print) == 1:
        trns = tag_data[args.print[0]-1]
        print('[id]:',  f'[{trns.id}] from {os.path.basename(tag_file)}')
        print('[date] => ', trns.date )
        print('[description] => ', trns.description )
        print('[entries] => ' )
        for entry in trns.entries: print('\t:', entry)

    elif len(args.print) == 2 and args.print[0] == 0:
        if args.print[1] != 0:
            trns = app_data[args.print[1]-1]
            print('[id]:',  f'[{trns.id}] from {os.path.basename(app_file)}' )
            print('[date] => ', trns.date )
            print('[description] => ', trns.description )
            print('[entries] => ' )
            for entry in trns.entries: print('\t:', entry)
        else:
            print('>>> empty statement: try -p 0 1')
                
    else:
        tu, ta = tag_data[args.print[0]-1],app_data[args.print[1]-1]
        _ta_id = ta.id
        ta.id = tu.id
        assessment = 'OK' if tu == ta else 'FAILED'
        ta.id = _ta_id
        print(f"Test {assessment}")
        print('[id]: ')
        print('\t:', f'[{tu.id}] from {os.path.basename(tag_file)}')
        print('\t:', f'[{ta.id}] from {os.path.basename(app_file)}')
        print('[date] => ', 'OK' if tu.date == ta.date else 'FAILED')
        print('\t:', tu.date)
        print('\t:', ta.date)
        print('[description] => ', 'OK' if tu.description == ta.description else 'FAILED' )
        print('\t:', tu.description)
        print('\t:', ta.description)
        print('[entries] => ', 'OK' if tu.entries == ta.entries else 'FAILED' )
        for entry in tu.entries: print('\t:', entry)
        print('---')
        for entry in ta.entries: print('\t:', entry)



    


 
