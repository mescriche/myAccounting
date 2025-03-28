import os
from os.path import relpath
class UserData:
    def __init__(self, root_dir, username):
        self.name = username
        self.root_dir = root_dir
        self.users_dir = os.path.join(root_dir, 'users')
        self.user_dir = os.path.join(self.users_dir, username)
        self.datafiles_dir = os.path.join(self.user_dir, 'datafiles')
        self.excelfiles_dir = os.path.join(self.user_dir, 'excelfiles')
        self.configfiles_dir = os.path.join(self.user_dir, 'configfiles')
        self.profile_file = os.path.join(self.configfiles_dir, f'{username}_profile.json')
        self.accounts_file = os.path.join(self.configfiles_dir, 'accounts.json')
        #self.income_file = os.path.join(self.configfiles_dir, 'income.json')
        #self.balance_file = os.path.join(self.configfiles_dir, 'balance.json')
        #self.rules_file = os.path.join(self.configfiles_dir, 'groups_rules.json')
        
        self.dbase_dir = os.path.join(self.user_dir, 'dbase')
        self.dbase_file = os.path.join(self.dbase_dir,  f'{username}_accounting.db')

        self.db_config = {'sqlalchemy.url':f'sqlite+pysqlite:///{self.dbase_file}',
                     'sqlalchemy.echo' : False}
    def __repr__(self):
        return f"name:{self.name}\ndbase_file:{relpath(self.dbase_file, self.root_dir)}\ndb_config:{self.db_config} "
