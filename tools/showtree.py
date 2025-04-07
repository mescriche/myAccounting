import argparse, os, sys

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)

from datamodel import UserData, AccountsTree
from dbase import db_open

parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description='Hola')
parser.add_argument('user', help='username')
parser.add_argument('-s', '--source', choices=['file', 'db', 'both'], default='file', help='print tree from database or file')
args = parser.parse_args()
print(args)

user = UserData(root_dir, args.user)

if args.source == 'file':
    tree = AccountsTree.from_file(user.accounts_file)
    tree.print()
elif args.source == 'db':
    db_open(user.db_config)
    tree = AccountsTree.from_db()
    tree.print()
else:
    db_open(user.db_config)
    file_tree =  AccountsTree.from_file(user.accounts_file)
    db_tree =  AccountsTree.from_db()

    file_acc = [(acc.code,str(acc)) for acc in file_tree.get_accounts()]
    db_acc = [(acc.code,str(acc)) for acc in db_tree.get_accounts()]

    equal_elements = list(set(file_acc) & set(db_acc))
    diff_elements = list(set(file_acc) ^ set(db_acc))
            
    if not diff_elements:
        print("There are NOT different accounts")
    else:
        print('DIFFERENT ACCOUNTS')
        for n,item in enumerate(sorted(diff_elements, key=lambda x:x[0])):
            print(n,item[1])
                    
    if not equal_elements:
        print("There are NOT equal accounts")
    else:
        print('ACCOUNTS ON BOTH: DATABASE AND FILE')
        for n,item in enumerate(sorted(equal_elements, key=lambda x:x[0])):
            print(n,item[1])
