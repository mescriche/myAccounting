__author__ = 'Manuel Escriche'
import argparse, os, re, sys, json, textwrap

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)

from controller.closing_seats import record_file, create_app_income_closing_seat, create_app_balance_closing_seat
from dbase import db_init, db_setup, db_session


parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    Process data over the years to work out four app files:  
    -> year income closing seat, 
    -> year balance closing seat, 
    -> year seats, 
    -> and next year opening seat. 
    The user data base is built according to files content '''),
    epilog=textwrap.dedent('''\
    This tool is meant to be used to amend the first opening seat, remake all database
    and subsequent yearly closing and opening seats. 
    Use this tool carefully!!
    Good bye! Good luck!
    ''')
)
parser.add_argument('user', help='username used to find data')
#parser.add_argument("--db", action='store_true', help="regenerate data base. Previous db is backed up as .bk file")
args = parser.parse_args()
#print(args)

#exit()

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

print('... creating data  ...')
db_file = os.path.join(dbase_dir, f"{args.user}_accounting.db")
db_config = {'sqlalchemy.url':f"sqlite+pysqlite:///{db_file}", 'sqlalchemy.echo':False}

if os.path.isfile(db_file):
    backup_file = db_file + '.bk'
    os.rename(db_file , backup_file)
    print(f'... renamed database file as {os.path.basename(backup_file)}')

print(db_config)
print('... init data base ...')
db_init(db_config)

accounts_file = os.path.join(config_dir, 'accounts.json')
print(f'... setup data base from user accounts file: {accounts_file}')
db_setup(accounts_file)

print(f'starting opening data file: {filename}')
starting_year = int(filename[:4])

pattern = re.compile(r'\d{4}_'+ args.user + '_seats.json')
files = sorted(filter(lambda x: pattern.match(x), files_list))
years = [int(filename[:4]) for filename in files]

if starting_year != years[0]:
    print(f"starting opening year {starting_year} doesn't match first year' seats {years[0]} ")
    sys.exit()

for year in years[:-1]:
    print(year)
    filename = f'{year}_{args.user}_opening_seat.json' if year == starting_year else f'{year}_app_opening_seat.json'
    filename = os.path.join(datafiles_dir, filename)
    try: record_file(filename)
    except Exception as e:
        print(e)
        break

    filename = f'{year}_{args.user}_seats.json'
    filename = os.path.join(datafiles_dir, filename)
    try: record_file(filename)
    except Exception as e:
        print(e)
        break
    
    filename = create_app_income_closing_seat(year, config_dir, datafiles_dir)
    filename = os.path.join(datafiles_dir, filename)
    try: record_file(filename)
    except Exception as e:
        print(e)
        break

    filename = create_app_balance_closing_seat(year, config_dir, datafiles_dir)
    filename = os.path.join(datafiles_dir, filename)
    try: record_file(filename)
    except Exception as e:
        print(e)
        break

    

    

                


