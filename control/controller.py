from datetime import datetime
from dbase import db_session, Transaction, BookEntry
class YearRange:
    def __init__(self):
        today = datetime.today()
        self._min = today.year
        self._run = today.year
        self._max = today.year
    @property
    def min(self): return self._min

    @min.setter
    def min(self, value): self._min = value
    
    @property
    def max(self): return self._max

    @max.setter
    def max(self, value): self._max = value
    
    @property
    def run(self): return self._run

    @run.setter
    def run(self, value): self._run = value

    def __repr__(self):
        return "Year Range ({0.min}, {0.run}, {0.max})".format(self)
        
class Controller:
    def __init__(self, view):
        self.view = view
        self.year_range = YearRange()
        
        with db_session() as db:
            try:
                first = db.query(Transaction).order_by(Transaction.date.asc()).first()
                last = db.query(Transaction).order_by(Transaction.date.desc()).first()
                self.year_range.min = first.date.year
                self.year_range.max = last.date.year
                self.year_range.run = last.date.year
            except: pass

        print(self.year_range)
        #self.view.show_today(today)
        
        #self.view.show_year()
