__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog, dialog
import tkinter.font as tkfont 
from datetime import datetime
from json import load, loads, dumps
from dbase import db_session, Account, Transaction, BookEntry
from controller.utility import db_get_account_code
from enum import Enum
import os, re
from datamodel.transaction import DMTransaction
from view.transaction import TransactionEditor, askTransactionRecordDialog
from .text_editor import TextEditor

class InputView(ttk.Frame):
    def __init__(self, parent, user_dir, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)
        
        self.dirname = os.path.join(user_dir, 'datafiles')
        self.filename = StringVar()
        
        tools_bar = ttk.Frame(self, height=15)
        tools_bar.pack(expand=False, fill='x', padx=1, pady=1)
        
        file_bar = ttk.Labelframe(tools_bar, text='File')
        file_bar.pack(expand=False, side='left', ipady=4, ipadx=3)
        new_edit_icon = PhotoImage(file='./view/icons/new_file.gif')
        new_edit_btn = ttk.Button(file_bar, image=new_edit_icon, command=self.new_blackboard)
        new_edit_btn.image = new_edit_icon
        new_edit_btn.pack(side='left')
        
        open_file_icon = PhotoImage(file='./view/icons/open_file.gif')
        open_file_btn = ttk.Button(file_bar, image=open_file_icon, command=self.open_file)
        open_file_btn.image = open_file_icon
        open_file_btn.pack(side='left')

        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        save_file_btn = ttk.Button(file_bar, image=save_file_icon, command=self.save_file)
        save_file_btn.image = save_file_icon
        save_file_btn.pack(side='left')

        self.file_name_entry = ttk.Combobox(file_bar, textvariable=self.filename, width= 40, postcommand= self._get_filenames)
        self.file_name_entry.pack(side='left')
        self.file_name_entry.bind('<<ComboboxSelected>>', self._open_file)

        new_bar = ttk.LabelFrame(tools_bar, text='New Transaction')
        new_bar.pack(expand=False, side='left')
        new_trans_icon = PhotoImage(file='./view/icons/add.gif')        
        new_trans_btn = ttk.Button(new_bar, image=new_trans_icon, command=self.get_new_transaction)
        new_trans_btn.image = new_trans_icon
        new_trans_btn.pack(padx=10)

        import_bar = ttk.Labelframe(tools_bar, text='Import', labelanchor='n')
        import_bar.pack(expand=False, side='left', ipadx=10)
        play_icon = PhotoImage(file='./view/icons/next.gif')
        play_btn = ttk.Button(import_bar, image=play_icon, command=self.execute_step_by_step)
        play_btn.image = play_icon
        play_btn.pack(side='left', padx=10)
        
        long_play_icon = PhotoImage(file='./view/icons/end.gif')
        long_play_btn = ttk.Button(import_bar, image=long_play_icon, command=self.execute)
        long_play_btn.image = long_play_icon
        long_play_btn.pack(padx=0)                                   
        
        self.editor = TextEditor(self)
        basename = 'blackboard'
        self.ext = '.json'
        self.filename.set(basename)
        filename = os.path.join(self.dirname, basename + self.ext )
        if not os.path.exists(filename):
            with open(filename, 'w') as _file: pass
        self.editor.load(filename)
        
        
    def _get_filenames(self):
        files = (file for file in os.listdir(self.dirname) if os.path.isfile(os.path.join(self.dirname, file)))
        _files = filter(lambda x: x.endswith('.json'), files)
        self.file_name_entry['values'] = sorted(list(map(lambda x: x.removesuffix('.json'), _files)), reverse=True)
                   
    def new_blackboard(self, *args):
        basename = 'blackboard'
        filename = os.path.join(self.dirname, basename+self.ext )
        self.filename.set(basename)
        open(filename, 'w').close()
        self.editor.load(filename)

    def _open_file(self, event=None):
        filename = os.path.join(self.dirname, self.filename.get()+self.ext)
        self.editor.load(filename)
        
    def open_file(self, *args):
        filename = filedialog.askopenfilename(defaultextension="*.json", initialdir = self.dirname,
                                               filetypes=[("All Files", "*.*"),
                                                          ("Json Documents","*.json")])
        if filename:
            basename = os.path.basename(filename).removesuffix('.json')
            self.filename.set(basename)
            self.dirname = os.path.dirname(filename)
            self.file_name_entry['values'] = self._get_files()
            self.editor.load(filename)


    def save_file(self, *args):
        if not self.filename.get():
            file_name = filedialog.asksaveasfilename(defaultextension='*.json',
                                                     initialdir = self.dirname,
                                                     filetypes=[("All Files", "*.*"),
                                                                ("Json Documents","*.json")])
            self.dirname = os.path.dirname(file_name)
            self.filename.set(os.path.basename(file_name).removesuffix('.json'))
            self.editor.save_to_file(file_name)
        else:
            filename = os.path.join(self.dirname, self.filename.get()+self.ext)
            self.editor.save_to_file(filename)
        messagebox.showinfo( message = f"File {self.filename.get()} saved", parent = self )
           
    def execute_step_by_step(self, *args):
        answer = messagebox.askokcancel(title='Recording Confirmation',
                                        message=f"Transactions are ready, proceed?")
        if not answer: return
        for trans in self.editor.data():
            if not trans.validate():
                print('transaction is not valid for record:')
                print('transaction=', trans)
                break
            answer = askTransactionRecordDialog(self, trans)
            if answer:
                with db_session() as db:
                    try: self.record_transaction(db, trans)
                    except Exception as e:
                        print(f'Problem when recording transaction:{trans}')
                        print(e)
                        break
                self.master.event_generate("<<DataBaseContentChanged>>")
                    
    def execute(self, *args):
        data = list(self.editor.data())
        answer = messagebox.askokcancel(title='Record Confirmation',
                                        message=f"{len(data)} transactions are ready, proceed?")
        if answer:
            with db_session() as db:
                for trans in self.editor.data():
                    if trans.validate():
                        self.record_transaction(db, trans)
                    else:
                        print('transaction is not valid for record:')
                        print('transaction=', trans)
                        break
                    
            title = "Transactions Record"
            msg = f"{len(data)} transactions has/have been created"
            messagebox.showinfo(title=title, message=msg) 
            self.master.event_generate("<<DataBaseContentChanged>>")

    def record_transaction(self, db, trans:DMTransaction):
        transaction = Transaction(date=trans.date, description=trans.description)
        db.add(transaction)
        for entry in trans.entries:
            code = db_get_account_code(entry.account)
            try: account = db.query(Account).filter_by(code=code).one()
            except: raise Exception(f'Unknown account code={code}')
            else: db.add(BookEntry(account=account, transaction=transaction, type=entry.type, amount=entry.amount))

    def get_new_transaction(self):
        editor = TransactionEditor(self)
        new_trans = editor.trans
        if new_trans:
            self.editor.add_new_transaction(new_trans)

#    def get_transactions_from_excel(self):
#        filename = filedialog.askopenfilename(defaultextension="*.xlsx", initialdir=self.dirname,
#                                              filetypes=[("All files", "*.*"),("Excel Documents","*.xlsx")])
#        if filename:
#            editor = ExcelEditor(None, filename)
#            trans_list = editor.trans_list
#            if trans_list:
#                self.editor.add_new_transaction(trans_list)
