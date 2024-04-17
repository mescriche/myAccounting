__author__ = 'Manuel Escriche'
import argparse, os, re, sys, json, textwrap

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)

from controller.closing_seats import record_file, create_app_income_closing_seat, create_app_balance_closing_seat
from dbase import db_init, db_setup, db_session


parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    Process data over the years to work out three app files:  
    -> year income closing seat, 
    -> year balance closing seat, 
    -> and next year opening seat. 
    The user data base is built according to files content '''),
    epilog=textwrap.dedent('''\
    This tool is meant to be used to amend the first opening seat, remake the database
    and subsequent yearly closing and opening seats. 
    Use this tool carefully!!
    Good bye! Good luck!
    ''')
)
parser.add_argument('user', help='username used to find data')
parser.add_argument('-o','--owner', action='store_true', help='take owner files as source, normally takes app files')
args = parser.parse_args()
print(args)

user_dir = os.path.join(root_dir, 'users', args.user)
datafiles_dir = os.path.join(user_dir, 'datafiles')
config_dir = os.path.join(user_dir, 'configfiles')
dbase_dir = os.path.join(user_dir, 'dbase')

files_list = sorted(os.listdir(datafiles_dir))

pattern = re.compile(r'\d{4}_' + args.user + '_opening_seat' + r'\.json')
for filename in files_list:
    if pattern.match(filename):
        break
else:
    print(f'Not starting file available' )    
    sys.exit()

print(f'>>> starting opening data file:\n0 : {filename}')
starting_year = int(filename[:4])

file_tag = args.user if args.owner else 'app'
pattern = re.compile(r'\d{4}_'+ file_tag + '_seats.json')
files = sorted(filter(lambda x: pattern.match(x), files_list))

if not len(files):
    print(">>> there aren't files to operate on")

print('>>> file set selected to remake the data base:')
for n,_file in enumerate(files, start=1): print(n, ':', _file)

answer = input("Rebuild data base from these files? (Y/n) ")
if  answer and answer.upper() != 'Y': exit()
print(">>> Let's do it!!")

years = [int(filename[:4]) for filename in files]
if starting_year != years[0]:
    print(f"starting opening year {starting_year} doesn't match first year' seats {years[0]} ")
    sys.exit()

print('years:', years)
print('last year:', years[-1], 'is left open')
#exit()
    
print('... data base  ...')
db_file = os.path.join(dbase_dir, f"{args.user}_accounting.db")
db_config = {'sqlalchemy.url':f"sqlite+pysqlite:///{db_file}", 'sqlalchemy.echo':False}

if os.path.isfile(db_file):
    backup_file = db_file + '.bk'
    os.rename(db_file , backup_file)
    print(f'... backing up database into file: {os.path.basename(backup_file)}')

print(f'... creating data base into {os.path.relpath(db_file, start=user_dir)}')

print('... init data base ...')
db_init(db_config)

accounts_file = os.path.join(config_dir, 'accounts.json')
print(f'... setup data base from user accounts file: {os.path.relpath(accounts_file, start=user_dir)}')
db_setup(accounts_file)

for year in years:
    print(year)
    filename = f'{year}_{args.user}_opening_seat.json' if year == starting_year else f'{year}_app_opening_seat.json'
    print(f'...recording {filename}')
    filename = os.path.join(datafiles_dir, filename)
    try: record_file(filename)
    except Exception as e:
        print(e)
        break

    filename = f'{year}_{file_tag}_seats.json'
    print(f'...recording {filename}')
    filename = os.path.join(datafiles_dir, filename)
    try: record_file(filename)
    except Exception as e:
        print(e)
        break

    if year == years[-1]: break
    
    filename = create_app_income_closing_seat(year, config_dir, datafiles_dir)
    print(f'...recording {filename}')
    filename = os.path.join(datafiles_dir, filename)
    try: record_file(filename)
    except Exception as e:
        print(e)
        break

    filename = create_app_balance_closing_seat(year, config_dir, datafiles_dir)
    print(f'...recording {filename}')
    filename = os.path.join(datafiles_dir, filename)
    try: record_file(filename)
    except Exception as e:
        print(e)
        break
    
    

    

                


