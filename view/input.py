from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as tkfont 
from datetime import datetime
from json import load
from dbase import db_session, Account, Transaction, BookEntry
from enum import Enum
import os, re

#class Mode(Enum):
#    EDIT = 1
#    INPUT = 2
    
Mode = Enum('Mode', ['EDIT', 'EXECUTE'])

class InputView(ttk.Frame):
    op_brace = dict([("{","}"),("}","{"),("[","]"),("]","[")])
    def __init__(self, parent):
        super().__init__(parent)
        self.mode = Mode.EDIT
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

        file_name_entry = Entry(shortcut_bar, textvariable=self.filename, width=25)
        #file_name_entry.configure(insertcolor='blue')
        file_name_entry.pack(side='left')
        
        self.play_control_bar = Frame(shortcut_bar, background='sea green')
        self.play_control_bar.pack(side='left', expand=False, fill='x', padx=10)
        
        #begin_icon = PhotoImage(file='./view/icons/begin.gif')
        #self.begin_btn = ttk.Button(self.play_control_bar, image=begin_icon, command=self.prev_transaction)
        #self.begin_btn.image = begin_icon
        #self.begin_btn.pack(side='left')

        
        self.play_icon = PhotoImage(file='./view/icons/play.gif')
        self.stop_icon = PhotoImage(file='./view/icons/stop.gif')
        self.play_stop_btn = ttk.Button(self.play_control_bar, image=self.play_icon, command=self.execute)
        self.play_stop_btn.image = self.play_icon
        self.play_stop_btn.pack(side='left', padx=10)

                
        prev_icon = PhotoImage(file='./view/icons/previous.gif')
        self.prev_btn = ttk.Button(self.play_control_bar, image=prev_icon, command=self.prev_transaction)
        self.prev_btn.image = prev_icon
        self.prev_btn.pack(side='left')
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
                                    background='khaki', foreground='dark blue', state='disabled', wrap=None)
        self.line_number_bar.pack(side='left', fill='y')
        
        self.text = Text(self, wrap='word', undo=1)
        self.text.pack(fill='both', expand=True)
        menu = Menu(self.text)
        menu.add_command(label='Insert transaction pattern', command=self.insert_transaction_pattern)
        menu.add_command(label='Highlight active line')
        menu.add_command(label='Verify syntax')
        
        if self.text.tk.call('tk', 'windowingsystem') == 'aqua':
            self.text.bind('<2>', lambda e: menu.post(e.x_root, e.y_root))
            self.text.bind('<Control-l>', lambda e: menu.post(e.x_root, e.y_root))
        else:
            self.text.bind('<3>', lambda e: menu.post(e.x_root, e.y_root))
        
        font = tkfont.Font(font=self.text['font'])
        self.text.config(tabs=font.measure(' '*4))
        self.text.bind('<Key>', self.key_press)

        self.cursor_info = Label(self.text, text='Line: 1 | Column: 1')
        self.cursor_info.pack(expand=False, fill=None, side='right', anchor='se')
        self.text.tag_configure('active_line', background='ivory2')
        self.text.tag_configure('brace', background='light gray')
        self.text.mark_set('prev_insert', 'insert-1c')
        self.text.focus_set()
        #print(self.text.mark_names())

    def insert_transaction_pattern(self):
        pos = self.text.index('insert')
        text = '\t{"date":"",\n\t "description":"",\n\t "entries":[\n\t\t{"account":"", "debit": 0, "credit": 0 },\n\t\t{"account":"", "debit": 0, "credit": 0 },\n\t\t{"account":"", "debit": 0, "credit": 0 }\n\t\t]\t\n\t}'
        self.text.insert(pos, text)

    def key_press(self, event):
        #print(event)
        pos = self.text.index('insert')
        #print('\n', 'insert at ', pos)
        if event.keysym == 'Down':
            pos = f"{pos}+1l lineend" if self.text.compare(pos, '==', f"{pos} lineend") else f"{pos}+1l"
        elif event.keysym == 'Up':
            pos = f"{pos}-1l lineend" if self.text.compare(pos, '==', f"{pos} lineend") else f"{pos}-1l"
        elif event.keysym == 'Right':
            pos = f"{pos}+1c" if self.text.compare(pos, '<', f"{pos} lineend") else pos
        elif event.keysym == 'Left':
            pos = f"{pos}-1c" if self.text.compare(pos, '>', f"{pos} linestart") else pos 
        else: pass #return 'break'
        pos = self.text.index(pos)
        #self.text.mark_set('insert', pos)

        if self.text.compare(pos, '==', '1.0'): return
        self.text.tag_remove('brace', '1.0', 'end')
        pos = self.text.index(pos)
        if (brace:= self.text.get(f"{pos}-1c", pos)) in '{[]}':
            self.text.tag_add('brace', f"{pos}-1c", pos)
            n_braces = 1
            pattern = r'({|})' if brace in '{}' else  r'(\[|\])'
            backwards = False if brace in '{[' else True
            pos = f"{pos}-1c" if backwards else f"{pos}+1c" 
            while fpos := self.text.search(pattern, pos, backwards=backwards, regexp=True):
                new_char = self.text.get(fpos, f"{fpos}+1c")
                if new_char == brace: n_braces += 1
                elif new_char == self.op_brace[brace]: n_braces -=1
                else: pass
                if n_braces == 0 or n_braces >= 25: break
                pos = f"{fpos}-1c" if backwards else f"{fpos}+1c"
            if n_braces == 0:
                self.text.tag_add('brace', fpos, f"{fpos}+1c")
        #return 'break'
    
    def update_shortcut_bar(self):
        if self.mode == Mode.EDIT:
            self.new_file_btn.config(state='normal')
            self.open_file_btn.config(state='normal')
            self.save_file_btn.config(state='normal')
            self.play_stop_btn.config(state='normal', image = self.play_icon)
            self.play_control_bar.config(background='sea green')
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
        elif self.mode == Mode.EXECUTE:
            self.play_stop_btn.config(state='normal', image = self.stop_icon)
            self.play_control_bar.config(background='red')
            #self.begin_btn.config(state='normal')
            self.prev_btn.config(state='normal')
            self.next_btn.config(state='normal')
            #self.end_btn.config(state='normal')
            self.new_file_btn.config(state='disabled')
            self.open_file_btn.config(state='disabled')
            self.save_file_btn.config(state='disabled')
        else: pass
        
    def new_file(self, *args):
        self.filename.set('')
        self.text.delete(1.0, 'end')
        self.render()
        #return 'break'
    
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

    def file_verification(self, filename):
        #print(filename)
        if not os.path.isfile(filename):
            raise Exception('File not found')
        if os.path.splitext(filename)[1] != '.json':
            raise Exception('Wrong file extension')

        with open(filename) as input_file:
            data = load(input_file)
            if 'content' not in data: raise Exception('Wrong data file format')
            elif data['content'] != 'transactions': raise Exception('Wrong content for transactions definition')
            else: pass
            if 'transactions' not in data: raise Exception('Missing transactions field')
            else:
                for trans in data['transactions']:
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
                    else:
                        for entry in trans['entries']:
                            if 'account' not in entry:
                                raise Exception('Transaction entry misses account')
                            if 'debit' not in entry and 'credit' not in entry:
                                raise  Exception('debit or credit amount miss in entry')
                                                 
    def execute(self, *args):
        e_file = os.path.join(self.dirname.get(), self.filename.get())
        try: self.file_verification(e_file)
        except Exception as e:
            print(e)
            self.text.focus_set()
        else:
            self.mode = Mode.EDIT if self.mode == Mode.EXECUTE else Mode.EXECUTE
            state = 'normal' if self.mode == Mode.EDIT else 'disabled'
            self.text.config(state = state)
            self.update_shortcut_bar()
            if self.mode == Mode.EXECUTE:
                with open(e_file) as _file:
                    self.data_file = load(_file)
                    self.trns_index = 0
            else: self.text.focus_set()
            
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
            self.master.master.event_generate("<<DataBaseContentChanged>>")
        self.render()
    
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
        
    def update_cursor_info(self):
        row, col = self.text.index(INSERT).split('.')
        line_num, col_num = str(int(row)), str(int(col) + 1)
        infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
        self.cursor_info.config(text=infotext)
        
    def render(self, *args):
        self.update_line_numbers()
        self.update_cursor_info()
        self.update_shortcut_bar()

        
