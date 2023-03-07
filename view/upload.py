from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime
from json import load
from dbase import db_session, Account, Transaction, BookEntry
from enum import Enum
import os

#class Mode(Enum):
#    EDIT = 1
#    INPUT = 2
    
Mode = Enum('Mode', ['START','EDIT', 'EXECUTE'])

class InputView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.mode = Mode.START
        self.dirname = StringVar()
        self.filename = StringVar()
        self.trns_index = 0
        self.pack(fill='both', expand=True)
        shortcut_bar = Frame(self, height=15, background='light sea green')
        shortcut_bar.pack(expand=False, fill='x', padx=1, pady=1)
        
        self.file_control_bar = Frame(shortcut_bar)
        self.file_control_bar.pack(side='left', expand=False, fill='x', padx=10)
 
        new_file_icon = PhotoImage(file='./view/icons/new_file.gif')
        self.new_file_btn = ttk.Button(self.file_control_bar, image=new_file_icon, command=self.new_file)
        self.new_file_btn.image = new_file_icon
        self.new_file_btn.pack(side='left')
        
        open_file_icon = PhotoImage(file='./view/icons/open_file.gif')
        self.open_file_btn = ttk.Button(self.file_control_bar, image=open_file_icon, command=self.open_file)
        self.open_file_btn.image = open_file_icon
        self.open_file_btn.pack(side='left')

        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        self.save_file_btn = ttk.Button(self.file_control_bar, image=save_file_icon, command=self.save_file)
        self.save_file_btn.image = save_file_icon
        self.save_file_btn.pack(side='left')

        file_name_label = ttk.Entry(shortcut_bar, textvariable=self.filename, width=25)
        file_name_label.pack(side='left')
        
        self.play_control_bar = Frame(shortcut_bar)
        self.play_control_bar.pack(side='left', expand=False, fill='x', padx=10)
        
        #begin_icon = PhotoImage(file='./view/icons/begin.gif')
        #self.begin_btn = ttk.Button(self.play_control_bar, image=begin_icon, command=self.prev_transaction)
        #self.begin_btn.image = begin_icon
        #self.begin_btn.pack(side='left')
        
        prev_icon = PhotoImage(file='./view/icons/previous.gif')
        self.prev_btn = ttk.Button(self.play_control_bar, image=prev_icon, command=self.prev_transaction)
        self.prev_btn.image = prev_icon
        self.prev_btn.pack(side='left')
        
        self.play_icon = PhotoImage(file='./view/icons/play.gif')
        self.stop_icon = PhotoImage(file='./view/icons/stop.gif')
        self.play_stop_btn = ttk.Button(self.play_control_bar, image=self.play_icon, command=self.execute)
        self.play_stop_btn.image = self.play_icon
        self.play_stop_btn.pack(side='left')
        
        next_icon = PhotoImage(file='./view/icons/next.gif')
        self.next_btn = ttk.Button(self.play_control_bar, image=next_icon, command=self.next_transaction)
        self.next_btn.image = next_icon
        self.next_btn.pack(side='left')

        #end_icon = PhotoImage(file='./view/icons/end.gif')
        #self.end_btn = ttk.Button(self.play_control_bar, image=end_icon, command=self.next_transaction)
        #self.end_btn.image = end_icon
        #self.end_btn.pack(side='left')        
        
        self.update_shortcut_bar()
        
        self.line_number_bar = Text(self, width=4, padx=3, takefocus=0, border=0,
                                    background='khaki', state='disabled', wrap=None)
        self.line_number_bar.pack(side='left', fill='y')
        
        self.text = Text(self, wrap='word', undo=1)
        self.text.pack(fill='both', expand=True)

        self.cursor_info = Label(self.text, text='Line: 1 | Column: 1')
        self.cursor_info.pack(expand=False, fill=None, side='right', anchor='se')
        self.text.tag_configure('active_line', background='ivory2')

    def update_shortcut_bar(self):
        for button in self.file_control_bar.winfo_children():
            button.config(state='disabled')
        for button in self.play_control_bar.winfo_children():
            button.config(state='disabled')
            
        if self.mode == Mode.START:
            self.new_file_btn.config(state='normal')
            self.open_file_btn.config(state='normal')
            
        elif self.mode == Mode.EDIT:
            self.new_file_btn.config(state='normal')
            self.open_file_btn.config(state='normal')
            self.save_file_btn.config(state='normal')
            self.play_stop_btn.config(state='normal', image = self.play_icon)

        elif self.mode == Mode.EXECUTE:
            self.play_stop_btn.config(state='normal', image = self.stop_icon)
            #self.begin_btn.config(state='normal')
            self.prev_btn.config(state='normal')
            self.next_btn.config(state='normal')
            #self.end_btn.config(state='normal')
            
        else: pass
    def new_file(self, *args):
        pass
    
    def open_file(self, *args):
        file_name = filedialog.askopenfilename(defaultextension="*.json",
                                               filetypes=[("All Files", "*.*"),("Json Documents","*.json")])
        if file_name:
            self.dirname.set(os.path.dirname(file_name))
            self.filename.set(os.path.basename(file_name))            
            self.text.delete(1.0, END)
            with open(file_name) as _file:
                self.text.insert(1.0, _file.read())
            self.mode = Mode.EDIT
            self.render()

    def save_file(self, *args):
        pass
            
    def execute(self, *args):
        self.mode = Mode.EDIT if self.mode == Mode.EXECUTE else Mode.EXECUTE
        self.update_shortcut_bar()
        if self.mode == Mode.EXECUTE:
            with open(os.path.join(self.dirname.get(), self.filename.get())) as _file:
                self.data_file = load(_file)
                self.trns_index = 0

    def next_transaction(self, *args):
        try:
            trans = self.data_file['transactions'][self.trns_index]
        except IndexError:
            self.next_btn.config(state='disabled')
        else:
            with db_session() as db:
                description = trans['description']
                date = datetime.strptime(trans['date'], '%d-%m-%Y').date()
                transaction = Transaction(date=date, description=description)
                db.add(transaction)
                for entry in trans['entries']:
                    try: account = db.query(Account).filter_by(name=entry['account']).one()
                    except: raise
                    else:
                        debit = float(entry['debit']) if 'debit' in entry else 0.0
                        credit = float(entry['credit']) if 'credit' in entry else 0.0
                        db.add(BookEntry(account=account, transaction=transaction, debit=debit, credit=credit))
                else: self.trns_index +=1
            self.master.master.event_generate("<<NewTransaction>>")
            
    
    def prev_transaction(self, *args):
        if self.trns_index == 0:
            self.prev_btn.config(state='disabled')
            return
        with db_session() as db:
            trans = db.query(Transaction).order_by(Transaction.id.desc()).first()
            for entry in trans.entries:
                db.delete(entry)
            else:
                db.delete(trans)
                self.trns_index -= 1
        self.master.master.event_generate("<<DeletedTransaction>>")
    
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
        
    def update_cursor_info(self):
        row, col = self.text.index(INSERT).split('.')
        line_num, col_num = str(int(row)), str(int(col) + 1)
        infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
        self.cursor_info.config(text=infotext)
        
    def render(self, *args):
        self.update_line_numbers()
        self.update_cursor_info()
        self.update_shortcut_bar()

        
