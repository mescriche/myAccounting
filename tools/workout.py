__author__ = 'Manuel Escriche'
import argparse, os, re, sys, json

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)

from datamodel.seat import record_file, create_app_income_closing_seat, create_app_balance_closing_seat
from dbase import db_init, db_setup, db_session


parser = argparse.ArgumentParser(description="Process data over the years to work out four app files:  \
                                 income closing seat, \
                                 balance closing seat, \
                                 running year seats, \
                                 and next year opening seat. \
                                 Data base can be created with files' content",
                                 epilog='Use this tool carefully. ')
parser.add_argument('user', help='username used to find data')
parser.add_argument("--db", action='store_true', help="regenerate data base. Previous db is backed up as .bk file")
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
db_store = os.path.join(dbase_dir, f"{args.user}_accounting.db") if args.db else ":memory:" 
db_config = {'sqlalchemy.url':f"sqlite+pysqlite:///{db_store}", 'sqlalchemy.echo':False}

if args.db and os.path.isfile(db_store):
    os.rename(db_store , f'{db_store}.bk')

print(db_config)
db_init(db_config)

accounts_file = os.path.join(config_dir, 'accounts.json')
#print(accounts_file)
db_setup(accounts_file)

print(f'starting file: {filename}')
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

    

    

                


