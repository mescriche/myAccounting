__author__ = 'Manuel Escriche'
import argparse, os, sys, json, textwrap, shutil
root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)

from datamodel import UserData

class ConfigTool:
    def __init__(self, root_dir):    
        parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''\
            Tool to create the user room with the stated profile. 
            -> Find available profiles at the configfiles folder by executing 'ls -l configfiles'
            -> Explore the profile files inside to assess what accounts fit your needs better
            -> Execute create command to create the user folder and subfolders, and place the profile file.
               --> The create command copies the profile file into the user config folder
                   users/{user}/configfiles/
               --> Besides it splits the chosen profile into three files:
                   - accounts.json with all accounts to create the data base {user}_accounting.db
                   - income.json with nominal/flow accounts used for reporting
                   - balance.json with real/state accounts used for reporting
            -> Execute the refresh command when you have edited your own profile file, and have to regenerate
               the three files: accounts, income and balance
            '''),
            epilog=textwrap.dedent('''\
            You have to create the user folder before using any other tools or the main application.
            After using this tool, you have to create the user database by using db_tool.py
            Good bye! Good luck!
            ''')
        )

        parser.add_argument('user', help="username is used to place configurations files properly")
        subparsers = parser.add_subparsers(required=True, help='commands available for user config files')

        parser_create = subparsers.add_parser('create',
                                              help='create user config files from a generic profile')
        parser_create.add_argument('profile',
                                   help="generic profile used to configure the application for the user")
        parser_create.set_defaults(func=self.cnf_create)

        parser_refresh = subparsers.add_parser('refresh',
                                               help='refresh user config files from user profile')
        parser_refresh.set_defaults(func=self.cnf_refresh)

        args = parser.parse_args()
        self.user = UserData(root_dir, args.user)
        
        args.func(args)

    def cnf_create(self, args):
        source = os.path.join(self.user.configfiles_dir, f"{args.profile}.json")
        print(f'... searching file {os.path.relpath(source, start=root_dir)}')

        if not os.path.isfile(source):
            print(f"configuration {source} file is not available")
            sys.exit()        
    
        if not os.path.isdir(self.user.configfiles_dir):
            print(f"... creating {self.user.configfiles_dir}")
            os.makedirs(config_dir)

        if not os.path.isdir(self.user.datafiles_dir):
            print(f"... creating {self.user.datafiles_dir}")
            os.makedirs(self.user.datafiles_dir)

        if not os.path.isdir(self.user.excelfiles_dir):
            print(f"... creating {self.user.excelfiles_dir}")
            os.makedirs(self.user.excelfiles_dir)

        # copy profile file
        target = self.user.profile_file
        print(f"... copying {os.path.relpath(source, start=root_dir)} into {os.path.relpath(target, start=root_dir)}")
        try:
            shutil.copyfile(source, target)
        except Exception as err:
            print(err)
            print(f"... failed when creating target file: {os.path.basename(target)}")
        else:
            self._generate_files(target)
            
             
    def cnf_refresh(self, args):
        source = self.user.profile_file
        self._generate_files(source)
                             

    def _generate_files(self, source):
        print(f'... generate files from {os.path.relpath(source,start=root_dir)}' )
        def collect_codes(data:dict) -> list:
            codes = list()
            for k in data:
                if isinstance(data[k], dict):
                    codes.extend(collect_codes(data[k]))
                elif isinstance(data[k], list):
                    codes.extend(data[k])
            else: return codes
            
        with open(source) as _file:
            try: 
                data = json.load(_file)
            except json.decoder.JSONDecodeError as error:
                filename = os.path.basename(source)
                print(f"{filename}:", error)
            else:
                accounts = data['accounts']
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
            
                revenue_codes = sorted(collect_codes(data['income']['revenue']))
                if revenue_codes != acc_nom_credit_codes:
                    print("Account codes in income inflows don't correspond with NOMINAL CREDIT account codes")
                    print(f'Income inflows codes = {revenue_codes}')
                    print(f'Nominal credit account codes = {acc_nom_credit_codes}')
                    exit()
            
                outgoing_codes = sorted(collect_codes(data['income']['outgoing']))
                if outgoing_codes != acc_nom_debit_codes:
                    print("Account codes in income outflows don't correspond with NOMINAL DEBIT account codes")
                    print(f'Income outflows codes = {outgoing_codes}')
                    print(f'Nominal debit account codes = {acc_nom_debit_codes}')
                    exit()
                    
                target = self.user.accounts_file
                with open(target, 'w', encoding='utf-8') as _file:
                    json.dump(data['accounts'], _file, ensure_ascii=False, indent=4)
                    print(f"... generated accounts file {os.path.basename(target)} ")

                target = self.user.income_file
                with open(target, 'w', encoding='utf-8') as _file:
                    json.dump(data['income'], _file, ensure_ascii=False, indent=4)
                print(f"... generated income file {os.path.basename(target)}")
        
                target = self.user.balance_file
                with open(target, 'w', encoding='utf-8') as _file:
                    json.dump(data['balance'], _file, ensure_ascii=False, indent=4)
                print(f"... generated balance file {os.path.basename(target)}")


if __name__ == '__main__':
    app = ConfigTool(root_dir)
