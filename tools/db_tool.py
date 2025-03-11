__author__ = 'Manuel Escriche'

import argparse, os, re, sys, json, textwrap, shutil
root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)
import dbase
from datamodel.user import UserData
from controller.app_seats import create_year_seats
from controller.utility import  db_get_yearRange
from sqlalchemy.orm.exc import NoResultFound

class DBaseTool:
    def __init__(self, root_dir):
        parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = textwrap.dedent('''\
            Tool to manage the user database file.
            -> It uses the dbase model to init the user database file
            -> It uses the config file for accounts located at the user folder to setup the user database.
            '''),
            epilog = textwrap.dedent('''\
            After having created, inited and setup the user data base, it's ready for use with:
            - myAccounting.py
            - excel_tool.py ''')
        )

        parser.add_argument('user', help='username whose database file is targeted for operation')
        subparsers = parser.add_subparsers(required=True, help='commands available for database user file', dest='command')

        parser_create = subparsers.add_parser('create', help='creates the database file')
        parser_create.set_defaults(func=self.db_create)

        parser_init = subparsers.add_parser('init',
                                            help='init database file based on its definition: create engine, table, etc, and a session ')
        parser_init.set_defaults(func=self.db_init)

        parser_setup = subparsers.add_parser('setup', help='setup database. It adds records for new accounts.')
        parser_setup.add_argument('-c', "--check",
                                  help='check consistency between Accounts table in data base, and accounts.json file',
                                  action='store_true')
        parser_setup.set_defaults(func=self.db_setup)

        parser_query = subparsers.add_parser('query',
                                             help='simple database query for accounts created with setup')
        parser_query.set_defaults(func=self.db_query)

        parser_save = subparsers.add_parser('save', help='saves database content into seats files')
        parser_save.add_argument('-t','--tag', nargs='?', default='app', const='user', help='tag to be used in filenames:<year>_<tag>_seats.json; default tag=app, -t =<user>')
        parser_save.set_defaults(func=self.db_save_to_file)

        parser_backup = subparsers.add_parser('backup',
                                              help='creates a database file backup')
        parser_backup.set_defaults(func=self.db_backup)
        
        parser_remove = subparsers.add_parser('remove', help='remove database file')
        parser_remove.set_defaults(func=self.db_remove)

        args = parser.parse_args()
        #print(args)

        self.user = UserData(root_dir, args.user)
        
        # call method
        args.func(args)        

    def db_create(self, args):
        print('create', args.user)
        try:
            os.makedirs(self.user.dbase_dir)
        except FileExistsError:
            pass
        
        if not os.path.isfile(self.user.dbase_file):
            open(self.user.dbase_file, 'w', encoding='utf-8').close()
            print(f'... created database file: {os.path.relpath(self.user.dbase_file, start=self.user.root_dir)} ...')
        else:
            print(f'... it already exists database file: {os.path.relpath(self.user.dbase_file, start=self.user.root_dir)}  ...')
            print(f'... please, remove it before executing this command again ....')

    def db_init(self, args):
        print('init', args.user)
        dbase.db_init(self.user.db_config)
        
    def db_setup(self, args):
        print('setup', args)
        dbase.db_open(self.user.db_config)
        if not args.check:
            dbase.db_setup(self.user.accounts_file, self.user.rules_file, verbose=True)
        else:
            with open(self.user.accounts_file) as acc_file, dbase.db_session() as db:
                data = json.load(acc_file)
                for record in data:
                    try: account = db.query(dbase.Account).filter_by(name=record['name']).one()
                    except NoResultFound:
                        print(f'-> missing in data base account:\n\t{record}')
                    else:
                        print(f'ok {account}')

    def db_query(self, args):
        print('query', args.user)
        dbase.db_open(self.user.db_config)
        with dbase.db_session() as db:
            for account in db.query(dbase.Account):
                print(account)
                
    def db_remove(self, args):
        print('remove', args.user)
        backup_file = self.user.dbase_file + '.bk'
        if os.path.isfile(self.user.dbase_file):
            os.rename(self.user.dbase_file, backup_file)
            print(f'... renamed database file as {os.path.relpath(backup_file, start=self.user.root_dir)} ...')
        else:
            print(f"... it doesn't exist database file: {os.path.relpath(self.user.dbase_file, start=self.user.root_dir)}")

    def db_backup(self, args):
        print('backup', args.user)
        backup_file = self.user.dbase_file + '.bk'
        if os.path.isfile(self.user.dbase_file):
            shutil.copyfile(self.user.dbase_file, backup_file)
            print(f"... file {os.path.relpath(backup_file, start=self.user.root_dir)} created ")
        else:
            print(f"... it doesn't exist database file: {os.path.relpath(self.user.dbase_file, start=self.user.root_dir)}")            
    def db_save_to_file(self, args):
        print('save_to_file', args)
        dbase.db_open(self.user.db_config)

        if args.tag == 'user': args.tag = args.user
        min_year, max_year = db_get_yearRange()
        years =  [*range(min_year, max_year+1)]
        print(years)

        for year in years:
            print(year)
            outcome = create_year_seats(year, self.user.user_dir, args.tag)
            _msg = f"{outcome['filename']} saved, {outcome['n_records']} records"
            print(_msg)
        
if __name__ == '__main__':
    app = DBaseTool(root_dir)
