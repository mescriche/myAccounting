__author__ = 'Manuel Escriche'
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
from .excelviewer import ExcelViewer
from .textviewer import TextEditor

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
                if debit > 0:
                    trans['entries'].append({'account': acc_name, 'debit': debit })
                elif credit > 0:
                    trans['entries'].append({'account': acc_name, 'credit': credit })
                else: raise Exception(f'Wrong BookEntry Format')
            self.parent.write_transaction(trans)
            self.dismiss()

class InputView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.pack(fill='both', expand=True)
        
        shortcut_bar = Frame(self, height=15, background='light sea green')
        shortcut_bar.pack(expand=False, fill='x', padx=1, pady=1)
        
        self.edit_control_bar = Frame(shortcut_bar)
        self.edit_control_bar.pack(side='left', expand=False, fill='x', padx=10) 

        new_trans_icon = PhotoImage(file='./view/icons/add.gif')
        self.new_trans_btn = ttk.Button(self.edit_control_bar, image=new_trans_icon, command=lambda:JSON_TransactionView(self))
        self.new_trans_btn.image = new_trans_icon
        self.new_trans_btn.pack(side='left')

        play_icon = PhotoImage(file='./view/icons/next.gif')
        self.play_btn = ttk.Button(self.edit_control_bar, image=play_icon, command=self.execute_step)
        self.play_btn.image = play_icon
        self.play_btn.pack(side='left')
        
        long_play_icon = PhotoImage(file='./view/icons/end.gif')
        self.long_play_btn = ttk.Button(self.edit_control_bar, image=long_play_icon, command=self.execute)
        self.long_play_btn.image = long_play_icon
        self.long_play_btn.pack(side='left')                                   
        self.file_control_bar = Frame(shortcut_bar)
        self.file_control_bar.pack(side='left', expand=False, fill='x', padx=10)

                
        DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.dirname = os.path.join(DIR, 'datafiles')
        self.filename = StringVar()

        
        new_edit_icon = PhotoImage(file='./view/icons/new_file.gif')
        self.new_edit_btn = ttk.Button(self.file_control_bar, image=new_edit_icon, command=self.new_edit)
        self.new_edit_btn.image = new_edit_icon
        self.new_edit_btn.pack(side='left')
        
        open_file_icon = PhotoImage(file='./view/icons/open_file.gif')
        self.open_file_btn = ttk.Button(self.file_control_bar, image=open_file_icon, command=self.open_file)
        self.open_file_btn.image = open_file_icon
        self.open_file_btn.pack(side='left')

        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        self.save_file_btn = ttk.Button(self.file_control_bar, image=save_file_icon, command=self.save_file)
        self.save_file_btn.image = save_file_icon
        self.save_file_btn.pack(side='left')

        file_name_entry = Entry(shortcut_bar, textvariable=self.filename, width=25)
        file_name_entry.pack(side='left')
                
        self.editor = TextEditor(self)
        
    def new_edit(self, *args):
        self.editor.destroy()
        self.editor = TextEditor(self)

    def open_file(self, *args):
        print(self.dirname)
        filename = filedialog.askopenfilename(defaultextension="*.json", initialdir = self.dirname,
                                               filetypes=[("All Files", "*.*"),
                                                          ("Json Documents","*.json"),
                                                          ("Excel Documents","*.xlsx")])
        if filename:
            self.filename.set(os.path.basename(filename))
            self.dirname = os.path.dirname(filename)
            self.editor.destroy()
            if filename.endswith(".xlsx"):
                self.editor = ExcelViewer(self, filename)
            elif filename.endswith("*.json"):
                self.editor = TexEditor(self, filename)
            else: raise Exception('Unknown file extension')

    def save_file(self, *args):
        if not self.filename.get():
            file_name = filedialog.asksaveasfilename(defaultextension='*.json', initialdire = self.dirname,
                                                     filetypes=[("All Files", "*.*"),
                                                                ("Json Documents","*.json")])
            self.dirname = os.path.dirname(file_name)
            self.filename.set(os.path.basename(file_name))
            with open(file_name, 'w') as _file:
                _file.write(self.text.get(1.0, 'end'))
        else:
            #file_name  = os.path.join(self.dirname, self.filename.get())
            #with open(file_name, 'w') as _file:
            #    _file.write(self.text.get(1.0, 'end'))
            self.editor.save_to_file()

                        
    def write_transaction(self, data):
        if content := self.text.get(1.0, 'end-1c'):
            content = loads(content)
            self.text.delete(1.0, 'end')            
        else: content = list()
        content.append(data)
        self.text.insert('end', dumps(content, indent=4))
        
    def content_verification(self):
        ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\/\s\w]+')
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
            if 'entries' not in trans:
                raise Exception('Transaction miss entries')
            elif len(trans['entries']) < 2:
                raise Exception('At least two entries are required in a transaction')
            else:
                with db_session() as db:
                    for entry in trans['entries']:
                        if 'account' not in entry:
                            raise Exception('Transaction entry misses account')
                        else:
                            _account = entry['account']
                            if match := ptrn.fullmatch(_account):
                                code = match.group('code')
                                try: account = db.query(Account).filter_by(code=code).one()
                                except: raise Exception(f'Unknown account code:"{code}"')
                            if 'debit' not in entry and 'credit' not in entry:
                                raise  Exception('debit or credit amount miss in entry')
    def execute_step(self, *args):
        try: self.content_verification()
        except Exception as e:
            print(e)
            raise Exception('Verification failed')
        else:
            content = self.text.get(1.0, 'end-1c')
            data = loads(content)
            answer = messagebox.askokcancel(title='Confirmation',
                                            message=f"{len(data)} transactiosn are ready",
                                            icon=WARNING)
            if answer:
                with db_session() as db:
                    for n,trans in enumerate(data):
                        answer = messagebox.askokcancel(title='Step by step',
                                                     message="Next transaction?",
                                                     icon=WARNING)
                        if not answer: break
                        self.new_transaction(db, trans)
                    else:
                        title = "Transaction Input"
                        msg = f"{len(data)} transactions has/have been created"
                        messagebox.showinfo(title=title, message=msg)
                #self.master.master.event_generate("<<DataBaseContentChanged>>")
    
    def execute(self, *args):
        try: self.content_verification()
        except Exception as e:
            print(e)
            raise Exception('Verification failed')
        else:
            content = self.text.get(1.0, 'end-1c')
            data = loads(content)
            answer = messagebox.askokcancel(title='Confirmation',
                                            message=f"{len(data)} transactiosn are ready",
                                            icon=WARNING)
            if answer:
                with db_session() as db:
                    for n,trans in enumerate(data):
                        self.new_transaction(db, trans)
                    else:
                        title = "Transaction Input"
                        msg = f"{len(data)} transactions has/have been created"
                        messagebox.showinfo(title=title, message=msg)
                #self.master.master.event_generate("<<DataBaseContentChanged>>")

    def new_transaction(self, db, trans):
        ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\/\s\w]+')
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
                    if 'debit' in entry and 'credit' in entry:
                        print(trans)
                        raise Exception('Wrong BookEntry Format')
                    elif 'debit' in entry and entry['debit'] > 0:
                        db.add(BookEntry(account=account, transaction=transaction, type='DEBIT', amount=float(entry['debit'])))
                    elif 'credit' in entry and entry['credit'] > 0:
                        db.add(BookEntry(account=account, transaction=transaction, type='CREDIT', amount=float(entry['credit'])))
                    else: raise Exception(f'Wrong BookEntry format')
            else:
                raise Exception(f'Wrong account pattern:"{_account}"')

    

        
