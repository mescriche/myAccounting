from dataclasses import dataclass
from datetime import datetime, date
from dbase.model import Type
import json

@dataclass
class DMBookEntry:
    account : str
    type  : Type
    amount : float
    
@dataclass
class DMTransaction:
    id: int
    date: datetime.date
    description: str
    entries: list[DMBookEntry]

    @classmethod
    def from_json(cls, data):
        entries = [DMBookEntry(entry['account'], Type[entry['type']], entry['amount']) for entry in data['entries']]
        return cls(data['id'], datetime.strptime(data['date'], '%d-%m-%Y').date(), data['description'], entries)
    @classmethod
    def from_DBTransaction(cls, trans):
        entries = [DMBookEntry(entry.account.gname, entry.type, entry.amount) for entry in trans.entries]
        return cls(trans.id, trans.date, trans.description, entries)
    def validate(self) ->bool:
        if not self.date or not isinstance(self.date, datetime.date): return False
        if not self.description or not isinstance(self.description, str): return False
        if len(self.entries) < 2: return False
        for entry in self.entries:
            if not entry.account or not isinstance(entry.account, str) or entry.account not in db_get_accounts_gname(): return False
            if not entry.type or not isinstance(entry.type, Type): return False
            if not entry.amount or not isinstance(entry.amount, float) or entry.amount < 0: return False
        return True

class DMTransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DMTransaction):
            item = dict()
            item['id'] = obj.id
            item['date'] = obj.date.strftime('%d-%m-%Y')
            item['description'] = obj.description
            item['entries'] = [{'account':entry.account, 'type':entry.type.name, 'amount':entry.amount } for entry in obj.entries]
            return item
        return super().default(obj)    
    
