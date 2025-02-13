__author__ = 'Manuel Escriche'
import os,json
from datetime import datetime
from dbase import db_session
from dbase import Account, Transaction, BookEntry, Type, Content
from datamodel.transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
from controller.utility import db_get_account_code


def db_record_file(filename) -> int:
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
            return
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
            else:
                return len(_data)

def create_income_closing_seat(year, user_dir, tag='app') -> str:
    datafiles_dir = os.path.join(user_dir, 'datafiles')
    entries = list()
    with db_session() as db:
        in_total = 0
        in_accounts = db.query(Account).filter_by(type=Type.CREDIT, content=Content.NOMINAL)
        for account in in_accounts:
            amount = account.credit(year)
            if round(amount,2)!= 0:
                in_total += amount
                entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                entries.append(entry)
        out_total = 0
        out_accounts = db.query(Account).filter_by(type=Type.DEBIT, content=Content.NOMINAL)
        for account in out_accounts:
            amount = account.debit(year)
            if round(amount,2) != 0:
                out_total += amount
                entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                entries.append(entry)
        
        ### Earnings (code=11)
        earnings_code = 11
        account = db.query(Account).filter_by(code=earnings_code).one()
        earnings = in_total - out_total
        earnings_type = Type.CREDIT if earnings >= 0 else Type.DEBIT
        entry = DMBookEntry(account=account.gname, type=earnings_type, amount=abs(earnings))
        entries.append(entry)
                    
    date = datetime.strptime(f'31-12-{year}', '%d-%m-%Y').date()
    description = f"Income closing seat for year {year}"
    _data = [DMTransaction(id=0, date=date, description=description, entries=entries),]
    filename = f'{year}_{tag}_income_closing_seat.json'
    _filename = os.path.join(datafiles_dir, filename)
    with open(_filename, 'w') as _file:
        json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)        
    return filename

def create_balance_closing_seat(year, user_dir, tag='app') -> dict:
    datafiles_dir = os.path.join(user_dir, 'datafiles')
    closing_entries = list()
    opening_entries = list()
    wealth_code = 10
    earning_code = 11
        
    with db_session() as db:
        earning_acc = db.query(Account).filter_by(code=earning_code).one()
        wealth_acc = db.query(Account).filter_by(code=wealth_code).one()
        assests_accounts = db.query(Account).filter_by(type=Type.DEBIT, content=Content.REAL)
        for account in assests_accounts:
            amount = account.balance(year)
            if round(amount,2) != 0:
                closing_entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                closing_entries.append(closing_entry)
                opening_entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                opening_entries.append(opening_entry)
        claim_accounts = db.query(Account).filter_by(type=Type.CREDIT, content=Content.REAL)
        for account in claim_accounts:
            amount = account.balance(year)
            if round(amount,2) != 0:
                closing_entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                closing_entries.append(closing_entry)
                if int(account.code) not in ( wealth_code, earning_code):           
                    opening_entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                    opening_entries.append(opening_entry)

        wealth = wealth_acc.balance(year) + earning_acc.balance(year)
        wealth_type = Type.CREDIT if wealth > 0 else Type.DEBIT
        opening_wealth_entry= DMBookEntry(account=wealth_acc.gname, type=wealth_type, amount=wealth)
        opening_entries.append(opening_wealth_entry)
        
        
    ### create closing seat for running year
    date = datetime.strptime(f'31-12-{year}', '%d-%m-%Y').date()
    description = f"Balance closing seat for year {year}"
    _data = [DMTransaction(id=0, date=date, description=description, entries=closing_entries),]
    closing_filename =  f'{year}_{tag}_balance_closing_seat.json'
    _filename = os.path.join(datafiles_dir, closing_filename)
    with open(_filename, 'w') as _file:
        json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)

    ### create opening seat for next year
    year = year + 1
    date = datetime.strptime(f'1-1-{year}', '%d-%m-%Y').date()
    description = f"Balance opening seat for year {year}"
    _data = [DMTransaction(id=0, date=date, description=description, entries=opening_entries),]
    opening_filename = f'{year}_{tag}_opening_seat.json'
    _filename = os.path.join(datafiles_dir, opening_filename )
    with open(_filename, 'w') as _file:
        json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)
    return  {'closing': closing_filename, 'opening': opening_filename}

def create_year_seats(year, user_dir, tag='app') -> dict:
    datafiles_dir = os.path.join(user_dir, 'datafiles')
    _opening_statement = "Balance Opening Statement"
    _balance_opening_seat = f"Balance opening seat for year {year}"
    _income_closing_seat =  f"Income closing seat for year {year}"
    _balance_closing_seat = f"Balance closing seat for year {year}"
    _exclude_seats = (_opening_statement, _balance_opening_seat, _income_closing_seat, _balance_closing_seat)
    with db_session() as db:
         min_date = datetime.strptime(f'01-01-{year}', "%d-%m-%Y").date()
         max_date = datetime.strptime(f'31-12-{year}', "%d-%m-%Y").date()
         query = db.query(Transaction).filter(Transaction.date >= min_date).filter(Transaction.date <= max_date)
         if items := [item for item in query]:
            _data = map(lambda x: DMTransaction.from_DBTransaction(x), items)
            _data = list(filter(lambda x:x.description.splitlines()[0].strip() not in _exclude_seats, _data))
            _data = sorted(_data, key=lambda x:x.date)
            for n,item in enumerate(_data, start=1): item.id = n
                 #print(n, item.date, item.description)       
            filename = f'{year}_{tag}_seats.json'
            _filename = os.path.join(datafiles_dir, filename )
            with open(_filename, 'w') as _file:
                json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)
    return {'n_records': len(_data), 'filename': filename}
