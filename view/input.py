from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
import tkinter.font as tkfont 
from datetime import datetime
from json import load, loads, dumps
from dbase import db_session, Account, Transaction, BookEntry
from enum import Enum
import os, re
from .transaction import TransactionView, ValidationError

class JSON_TransactionView(TransactionView):
    def __init__(self, parent):
        super().__init__(parent)
        
    def save(self):
        try: self.verify_input()
        except ValidationError as error:
            title = "Verifiying transaction"
            messagebox.showerror(title=title, message=error.message)
        else:
            trans = dict()
            trans['date'] = self.date_entry.get()
            trans['description'] = self.text.get(1.0, 'end-1c')
            trans['entries'] = list()
            for child_id in self.data.get_children():
                child = self.data.item(child_id)
                acc_name, debit, credit = tuple(child['values'])
                try: debit = abs(float(debit))
                except ValueError: debit = 0.0
                try: credit = abs(float(credit))
                except ValueError: credit = 0.0
                trans['entries'].append({'account': acc_name, 'debit': debit, 'credit': credit })
            self.parent.write_transaction(trans)
            self.dismiss()

class InputView(ttk.Frame):
    op_brace = dict([("{","}"),("}","{"),("[","]"),("]","[")])
    def __init__(self, parent):
        super().__init__(parent)
        self.dirname = StringVar()
        self.filename = StringVar()
        self.trns_index = 0
        self.pack(fill='both', expand=True)
        
        shortcut_bar = Frame(self, height=15, background='light sea green')
        shortcut_bar.pack(expand=False, fill='x', padx=1, pady=1)
        
        self.edit_control_bar = Frame(shortcut_bar)
        self.edit_control_bar.pack(side='left', expand=False, fill='x', padx=10)

                                    
        new_edit_icon = PhotoImage(file='./view/icons/new_file.gif')
        self.new_edit_btn = ttk.Button(self.edit_control_bar, image=new_edit_icon, command=self.new_edit)
        self.new_edit_btn.image = new_edit_icon
        self.new_edit_btn.pack(side='left')

        new_trans_icon = PhotoImage(file='./view/icons/add.gif')
        self.new_trans_btn = ttk.Button(self.edit_control_bar, image=new_trans_icon, command=lambda:JSON_TransactionView(self))
        self.new_trans_btn.image = new_trans_icon
        self.new_trans_btn.pack(side='left')

        play_icon = PhotoImage(file='./view/icons/play.gif')
        self.play_btn = ttk.Button(self.edit_control_bar, image=play_icon, command=self.execute)
        self.play_btn.image = play_icon
        self.play_btn.pack(side='left')
                                   
        self.file_control_bar = Frame(shortcut_bar)
        self.file_control_bar.pack(side='left', expand=False, fill='x', padx=10)
        
        open_file_icon = PhotoImage(file='./view/icons/open_file.gif')
        self.open_file_btn = ttk.Button(self.file_control_bar, image=open_file_icon, command=self.open_file)
        self.open_file_btn.image = open_file_icon
        self.open_file_btn.pack(side='left')

        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        self.save_file_btn = ttk.Button(self.file_control_bar, image=save_file_icon, command=self.save_file)
        self.save_file_btn.image = save_file_icon
        self.save_file_btn.pack(side='left')

        file_name_entry = Entry(shortcut_bar, textvariable=self.filename, width=25)
        #file_name_entry.configure(insertcolor='blue')
        file_name_entry.pack(side='left')
        
#        self.play_control_bar = Frame(shortcut_bar, background='sea green')
#        self.play_control_bar.pack(side='left', expand=False, fill='x', padx=10)


        self.line_number_bar = Text(self, width=4, padx=3, takefocus=0, border=0,
                                    background='khaki', foreground='dark blue', state='disabled', wrap=None)
        self.line_number_bar.pack(side='left', fill='y')
        
        self.text = Text(self, wrap='word', undo=1)
        self.text.pack(fill='both', expand=True)
        
        
    def insert_transaction(self, event):
        print(event)
        pos = self.text.index('insert')
        text = '\t{"date":"",\n\t "description":"",\n\t "entries":[\n\t\t{"account":"", "debit": 0, "credit": 0 },\n\t\t{"account":"", "debit": 0, "credit": 0 },\n\t\t{"account":"", "debit": 0, "credit": 0 }\n\t\t]\t\n\t}'
        self.text.insert(pos, text)

    def new_edit(self, *args):
        self.text.delete(1.0, 'end')
        #text = '{"content":"transactions",\n "transactions":[\n  ]\n}'
        #self.text.insert(1.0, text)                 
        #self.render()
        #return 'break'
        
    def write_transaction(self, data):
        if content := self.text.get(1.0, 'end-1c'):
            content = loads(content)
            self.text.delete(1.0, 'end')            
        else: content = list()
        content.append(data)
        self.text.insert('end', dumps(content, indent=4))
        
    def open_file(self, *args):
        file_name = filedialog.askopenfilename(defaultextension="*.json",
                                               filetypes=[("All Files", "*.*"),("Json Documents","*.json")])
        if file_name:
            self.dirname.set(os.path.dirname(file_name))
            self.filename.set(os.path.basename(file_name))            
            self.text.delete(1.0, 'end')
            with open(file_name) as _file:
                self.text.insert(1.0, _file.read())
            self.render()
            self.text.focus_set()
        #return 'break'

    def save_file(self, *args):
        if not self.filename.get():
            file_name = filedialog.asksaveasfilename(defaultextension='*.json',
                                                     filetypes=[("All Files", "*.*"),("Json Documents","*.json")])
            self.dirname.set(os.path.dirname(file_name))
            self.filename.set(os.path.basename(file_name))
            with open(file_name, 'w') as _file:
                _file.write(self.text.get(1.0, 'end'))
        else:
            file_name  = os.path.join(self.dirname.get(), self.filename.get())
            with open(file_name, 'w') as _file:
                _file.write(self.text.get(1.0, 'end'))
        #return 'break'

    def content_verification(self):
        content = self.text.get(1.0, 'end-1c')
        data = loads(content)
        for trans in data:
            if 'date' not in trans:
                raise Exception('Transaction miss date')
            else:
                try: datetime.strptime(trans['date'], '%d-%m-%Y').date()
                except: raise Exception('Wrong date format')
                
            if 'description' not in trans:
                raise Exception('Transaction miss description')
            elif not re.fullmatch(r'[\w\s]+', trans['description']):
                raise Exception('Transaction description with wrong string format')
            else: pass
                        
            if 'entries' not in trans:
                raise Exception('Transaction miss entries')
            elif len(trans['entries']) < 2:
                raise Exception('At least two entries are required in a transaction')
            else:
                for entry in trans['entries']:
                    if 'account' not in entry:
                        raise Exception('Transaction entry misses account')
                    if 'debit' not in entry and 'credit' not in entry:
                        raise  Exception('debit or credit amount miss in entry')
                                                 
    def execute(self, *args):
        try:
            self.content_verification()
        except Exception as e:
            print(e)
            #self.text.focus_set()
        else:
            content = self.text.get(1.0, 'end-1c')
            data = loads(content)
            for trans in data:
                self.new_transaction(trans)
            else:
                title = "Transaction Input"
                msg = f"{len(data)} transactions has/have been created"
                messagebox.showinfo(title=title, message=msg)

    def new_transaction(self, trans):
        ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\s\w]+')
        with db_session() as db:
            description = trans['description']
            date = datetime.strptime(trans['date'], '%d-%m-%Y').date()
            transaction = Transaction(date=date, description=description)
            db.add(transaction)
            for entry in trans['entries']:
                _account = entry['account']
                if match := ptrn.fullmatch(_account):
                    code = match.group('code')
                    try: account = db.query(Account).filter_by(code=code).one()
                    except: raise Exception(f'Unknown account code:"{code}"')
                    else:
                        debit = float(entry['debit']) if 'debit' in entry else 0.0
                        credit = float(entry['credit']) if 'credit' in entry else 0.0
                        db.add(BookEntry(account=account, transaction=transaction, debit=debit, credit=credit))
                else:
                    raise Exception(f'Wrong account pattern:"{_account}"')
        self.master.master.event_generate("<<DataBaseContentChanged>>")
    
    def get_line_numbers(self):
        output = ''
        row, col = self.text.index('end').split('.')
        for i in range(1, int(row)):
            output += str(i) + '\n'
        return output
    
    def update_line_numbers(self):
        line_numbers = self.get_line_numbers()
        self.line_number_bar.config(state='normal')
        self.line_number_bar.delete('1.0', 'end')
        self.line_number_bar.insert('1.0', line_numbers)
        self.line_number_bar.config(state='disabled')
        
    #def update_cursor_info(self):
    #    row, col = self.text.index(INSERT).split('.')
    #    line_num, col_num = str(int(row)), str(int(col) + 1)
    #    infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
    #    self.cursor_info.config(text=infotext)
        
    def render(self, *args):
        self.update_line_numbers()
        #self.update_cursor_info()
        #self.update_shortcut_bar()

        
