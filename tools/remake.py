__author__ = 'Manuel Escriche'
import argparse, os, re, sys, json, textwrap

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)
from datamodel import UserData
from controller.app_seats import create_income_closing_seat, create_balance_closing_seat
from controller.app_seats import db_record_file
from dbase import db_init, db_setup, db_session


parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    It creates a new data base, and the closing and opening seats files over the years.
    
    It takes as data source:
    -> balance opening: <YEAR>_<user/tag>_opening_seat.json
    -> seats files: <YEAR>_<tag>_seats.json
    
    From that, it creates new consistent:
    -> year income closing seat: <YEAR>_<tag>_income_closing_seat.json
    -> year balance closing seat: <YEAR>_<tag>_balance_closing_seat.json
    -> next year balance opening seat: <YEAR+1>_<tag>_opening_seat.json
    which, are loaded into the data base, and ... repeats the process over the years.
    
    The final outcome are new consistent data base and seat files.
    '''),
    epilog=textwrap.dedent('''\
    This tool is meant to be used when having to modify or update the first opening seat
    or when having to modify the user profile <user>_profile.json; 
    Consequently the database and the mandatory seat files have to be rebuilt over the years.
    Use this tool carefully!!
    Good bye! Good luck!
    ''')
)
parser.add_argument('user', help='username; used to find data ')
parser.add_argument('-t','--tag', nargs='?', default='app', const='user',
                    help=' take data files with pattern YEAR_<tag>_seats.json:\
                    missing -t => tag = app;\
                    -t => tag = <user>;\
                    -t tag => tag = tag')
args = parser.parse_args()
print(args)

if args.tag == 'user': args.tag = args.user

user = UserData(root_dir, args.user)

files_list = sorted(os.listdir(user.datafiles_dir))

pattern = re.compile(r'\d{4}_' + args.user + '_opening_seat.json')
for filename in files_list:
    if pattern.match(filename):
        break
else:
    print(f'Not starting file with pattern YEAR_{args.user}_opening_seat.json available' )    
    sys.exit()

print(f'>>> starting opening data file:\n0 : {filename}')
starting_year = int(filename[:4])


pattern = re.compile(r'\d{4}_'+ args.tag + '_seats.json')
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
if os.path.isfile(user.dbase_file):
    backup_file = user.dbase_file + '.bk'
    os.rename(user.dbase_file , backup_file)
    print(f'... backing up database into file: {os.path.basename(backup_file)}')

print(f'... creating data base into {os.path.relpath(user.dbase_file, start=user.root_dir)}')

print('... init data base ...')
db_init(user.db_config)

print(f'... setup data base from user accounts file: {os.path.relpath(user.accounts_file, start=user.root_dir)}')
db_setup(user.accounts_file)

for year in years:
    print(f'>>> year : {year}')
    filename = f'{year}_{args.user}_opening_seat.json' \
        if year == starting_year else f'{year}_{args.tag}_opening_seat.json'
    print(f'...recording {filename:<35}', end='')
    filename = os.path.join(user.datafiles_dir, filename)
    try: n = db_record_file(filename)
    except Exception as e:
        print(e)
        break
    else:
        print(f": {n:>4} seats recorded")

    filename = f'{year}_{args.tag}_seats.json'
    print(f'...recording {filename:<35}', end='')
    filename = os.path.join(user.datafiles_dir, filename)
    try: n = db_record_file(filename)
    except Exception as e:
        print(e)
        break
    else:
        print(f": {n:>4} seats recorded")

    if year == years[-1]: break
    
    filename = create_income_closing_seat(year, user.user_dir, args.tag)
    print(f"...recording {filename:<35}", end='')
    filename = os.path.join(user.datafiles_dir, filename)
    try: n = db_record_file(filename)
    except Exception as e:
        print(e)
        break
    else:
        print(f": {n:>4} seats recorded")
    
    outcome = create_balance_closing_seat(year, user.user_dir, args.tag)
    print(f"...recording {outcome['closing']:<35}", end='')
    filename = os.path.join(user.datafiles_dir, outcome['closing'])
    try: n = db_record_file(filename)
    except Exception as e:
        print(e)
        break
    else:
        print(f": {n:>4} seats recorded")  
    

    

                


