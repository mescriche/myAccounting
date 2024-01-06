__author__ = 'Manuel Escriche'
import argparse, os, sys, json, textwrap, shutil
root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)


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
            You have to create the user room before using any other tools or the main application.
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
        self.user_dir = os.path.join(root_dir, 'users', args.user)
        args.func(args)

    def cnf_create(self, args):
        config_dir = 'configfiles'
        source = os.path.join(root_dir, config_dir, f"{args.profile}.json")
        print(f'... searching file {os.path.relpath(source, start=root_dir)}')

        if not os.path.isfile(source):
            print(f"configuration {source} file is not available")
            sys.exit()        
    
        config_dir = 'configfiles'
        config_dir = os.path.join(self.user_dir, config_dir)
        if not os.path.isdir(config_dir):
            print(f"... creating {config_dir}")
            os.makedirs(config_dir)

        datafiles_dir = 'datafiles'
        datafiles_dir = os.path.join(self.user_dir, datafiles_dir)
        if not os.path.isdir(datafiles_dir):
            print(f"... creating {datafiles_dir}")
            os.makedirs(datafiles_dir)

        excelfiles_dir = 'excelfiles'
        excelfiles_dir = os.path.join(self.user_dir, excelfiles_dir)
        if not os.path.isdir(excelfiles_dir):
            print(f"... creating {excelfiles_dir}")
            os.makedirs(excelfiles_dir)

        # copy profile file
        user_profile_filename =  f"{args.user}_profile.json"
        target = os.path.join(self.user_dir, config_dir, user_profile_filename)
        print(f"... copying {os.path.relpath(source, start=root_dir)} into {os.path.relpath(target, start=root_dir)}")
        try:
            shutil.copyfile(source, target)
        except Exception as err:
            print(err)
            print(f"... failed when creating target file: {os.path.basename(target)}")
        else:
            self._generate_files(target)
            
             
    def cnf_refresh(self, args):
        config_dir = 'configfiles'
        user_profile_filename =  f"{args.user}_profile.json"
        source = os.path.join(self.user_dir, config_dir, user_profile_filename)
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
            
        config_dir = 'configfiles'
        balance_file = 'balance.json'
        balance_file = os.path.join(self.user_dir, config_dir, balance_file)
        income_file = 'income.json'
        income_file = os.path.join(self.user_dir, config_dir, income_file) 
        accounts_file = 'accounts.json'
        accounts_file = os.path.join(self.user_dir, config_dir, accounts_file)
        
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
                    
                target = os.path.join(self.user_dir, config_dir, accounts_file)
                data['accounts']['profile'] = data['profile']
                with open(target, 'w', encoding='utf-8') as _file:
                    json.dump(data['accounts'], _file, ensure_ascii=False, indent=4)
                    print(f"... generated accounts file {os.path.basename(target)} ")

                target = os.path.join(self.user_dir, config_dir, income_file)
                data['income']['profile'] = data['profile']
                with open(target, 'w', encoding='utf-8') as _file:
                    json.dump(data['income'], _file, ensure_ascii=False, indent=4)
                print(f"... generated income file {os.path.basename(target)}")
        
                target = os.path.join(self.user_dir, config_dir, balance_file)
                data['balance']['profile'] = data['profile']
                with open(target, 'w', encoding='utf-8') as _file:
                    json.dump(data['balance'], _file, ensure_ascii=False, indent=4)
                print(f"... generated balance file {os.path.basename(target)}")


if __name__ == '__main__':
    app = ConfigTool(root_dir)
