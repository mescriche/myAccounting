import os, json
from datamodel.transaction import DMTransaction, DMBookEntry, DMTransactionEncoder
from dbase import db_session
from dbase import Transaction, Account, BookEntry, Type, Content
from datetime import datetime
from .utility import db_get_account_code

def record_file(filename):
    def record_transaction(db, trans:DMTransaction):
        transaction = Transaction(date=trans.date, description=trans.description)
        db.add(transaction)
        for entry in trans.entries:
            code = db_get_account_code(entry.account)
            try: account = db.query(Account).filter_by(code=code).one()
            except: raise Exception(f'Unknown account code={code}')
            else: db.add(BookEntry(account=account, transaction=transaction,
                                   type=entry.type, amount=entry.amount))
        return
    
    with open(filename, 'r') as _file, db_session() as db:
        try:
            _data = json.loads(_file.read())
            #print(_data)
        except Exception as e:
            print(e)
            print(f'Wrong file format: {filename}, expected json')
            print('file not loaded')
        else:
            for item in _data:
                #print(item)
                try:
                    trans = DMTransaction.from_json(item)
                except Exception as e:
                    print(f'Wrong format when reading item = {item}')
                    print(e)
                    break
                else:
                    record_transaction(db, trans)
    #print(f'recorded {filename} in database with #records: {len(_data)}')
    return

def create_app_income_closing_seat(year, config_dir, datafiles_dir) -> str:
    def collect_codes(data:dict) -> list:
        codes = list()
        for k in data:
            if isinstance(data[k], dict):
                codes.extend(collect_codes(data[k]))
            elif isinstance(data[k], list):
                codes.extend(data[k])
        else: return codes
        
    report_file = 'income.json'
    with open(os.path.join(config_dir, report_file)) as _file:
        income_repo = json.load(_file)
    income_repo.pop('purpose')
    income_repo.pop('profile')

    entries = list()
    in_accounts = collect_codes(income_repo['inflows'])
    with db_session() as db:
        total = 0
        for code in in_accounts:
            account = db.query(Account).filter_by(code=code).one()
            amount = account.credit(year)
            if amount > 0:
                total += amount
                entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                entries.append(entry)
        else:
            ### Outcome (code=11)
            outcome_code = 11
            account = db.query(Account).filter_by(code=outcome_code).one()
            entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=total)
            entries.append(entry)
                    
    out_accounts = collect_codes(income_repo['outflows'])
    with db_session() as db:
        total = 0
        for code in out_accounts:
            account = db.query(Account).filter_by(code=code).one()
            amount = account.debit(year)
            if amount > 0:
                total += amount
                entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                entries.append(entry)
        else:
            outcome_code = 11
            account = db.query(Account).filter_by(code=outcome_code).one()
            entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=total)
            entries.append(entry)
                    
    date = datetime.strptime(f'31-12-{year}', '%d-%m-%Y').date()
    description = f"Income closing seat for year {year}"
    _data = [DMTransaction(id=0, date=date, description=description, entries=entries),]
    filename = f'{year}_app_income_closing_seat.json'
    _filename = os.path.join(datafiles_dir, filename)
    with open(_filename, 'w') as _file:
        json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)
    print(f'...created {filename} with #records: {len(_data)}')
    return filename

def create_app_balance_closing_seat(year, config_dir, datafiles_dir) -> str:
    def collect_codes(data:dict) -> list:
        codes = list()
        for k in data:
            if isinstance(data[k], dict):
                codes.extend(collect_codes(data[k]))
            elif isinstance(data[k], list):
                codes.extend(data[k])
        else: return codes
    report_file = 'balance.json'
    with open(os.path.join(config_dir, report_file)) as _file:
        balance_repo = json.load(_file)
    balance_repo.pop('purpose')
    balance_repo.pop('profile')
    
    closing_entries = list()
    opening_entries = list()
    assets_accounts = collect_codes(balance_repo['assets'])
    with db_session() as db:
        for code in assets_accounts:
            account = db.query(Account).filter_by(code=code).one()
            amount = account.balance(year)
            if amount > 0:
                closing_entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                closing_entries.append(closing_entry)
                opening_entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                opening_entries.append(opening_entry)
                    
    claims_accounts = collect_codes(balance_repo['claims'])
    with db_session() as db:
        for code in claims_accounts:
            account = db.query(Account).filter_by(code=code).one()
            amount = account.balance(year)
            if amount > 0:
                closing_entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                closing_entries.append(closing_entry)
                opening_entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                opening_entries.append(opening_entry)

    ### create closing seat for running year
    date = datetime.strptime(f'31-12-{year}', '%d-%m-%Y').date()
    description = f"Balance closing seat for year {year}"
    _data = [DMTransaction(id=0, date=date, description=description, entries=closing_entries),]
    filename =  f'{year}_app_balance_closing_seat.json'
    _filename = os.path.join(datafiles_dir, filename)
    with open(_filename, 'w') as _file:
        json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)
    print(f'...created {filename} with #records: {len(_data)}')
    closing_filename = filename
        
    with db_session() as db:
        wealth_acc = db.query(Account).filter_by(code=10).one() # Wealth account
        outcome_acc = db.query(Account).filter_by(code=11).one() # Outcome account
        earnings = outcome_acc.balance(year)
        outcome_type = Type.DEBIT if earnings > 0 else Type.CREDIT
        wealth_type = Type.CREDIT if outcome_type == Type.DEBIT else Type.CREDIT
        opening_entries.append(DMBookEntry(account=outcome_acc.gname, type=outcome_type, amount=abs(earnings)))
        opening_entries.append(DMBookEntry(account=wealth_acc.gname,  type=wealth_type,  amount=abs(earnings)))
    year = year + 1
    date = datetime.strptime(f'1-1-{year}', '%d-%m-%Y').date()
    description = f"Balance opening seat for year {year}"
    _data = [DMTransaction(id=0, date=date, description=description, entries=opening_entries),]
    filename = f'{year}_app_opening_seat.json'
    _filename = os.path.join(datafiles_dir, filename )
    with open(_filename, 'w') as _file:
        json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)        
    print(f'...created {filename} with #records: {len(_data)}')
    return closing_filename
