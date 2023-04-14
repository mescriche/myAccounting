__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk
from .transaction import DMBookEntry, DMTransaction, DMBookEntry_dict
from .transaction import TransactionViewer, TransactionEditor
from dbase import Type
from dataclasses import asdict
import json, os

class TextEditor(ttk.Frame):
    def __init__(self, parent, filename, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)

        new_trans_icon = PhotoImage(file='./view/icons/add.gif')
        self.tools_bar = ttk.LabelFrame(parent.tools_bar, text='Add Transaction')
        self.tools_bar.pack(expand=False, side='left')
        
        new_trans_btn = ttk.Button(self.tools_bar, image=new_trans_icon, command=self.get_new_transaction)
        new_trans_btn.image = new_trans_icon
        new_trans_btn.pack()
        
        self.text = Text(self, **kwargs)
        self.text.pack(expand=True, fill='both')
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')
              
        self.filename = filename
        self._data = list()
        self._data_counter = 0
        if os.stat(filename).st_size > 0:
            with open(filename, 'r') as _file:
                try: content = json.loads(_file.read())
                except:
                    print(f'Wrong file format: {filename}')
                    print('file not loaded')
                else:
                    for n,item in enumerate(content):
                        try:
                            entries = [DMBookEntry(e['account'], Type[e['type']], e['amount']) for e in item['entries']]
                            trans = DMTransaction(n+1, item['date'], item['description'], entries)
                        except Exception as e:
                            print(f'Wrong format when reading item= {item}')
                            print(e)
                            self.text['state'] = 'normal'
                            self.text.insert(1.0, json.dumps(content, indent=4))
                            self.text['state'] = 'disabled'
                            break
                        else:
                            self._data.append(trans)
                            self._data_counter +=1
                    else:
                        self.render()
        
    def save_to_file(self, filename=None):
        _filename = self.filename if not filename else filename
        with open(_filename, 'w') as _file:
            data = list(map(lambda x:asdict(x, dict_factory=DMBookEntry_dict), self.data()))
            json.dump(data, _file, indent=4)        

    def get_new_transaction(self):
        editor = TransactionEditor(self)
        new_trans = editor.trans
        if new_trans:
            self._data_counter += 1
            new_trans.id = self._data_counter
            self._data.append(new_trans)
            self.render()

    def remove_transaction(self, trans_id):
        for trans in self._data:
            if trans.id == trans_id:
                self._data.remove(trans)
                break
        self.render()

    def update_transaction(self, trans):
        for n,item in enumerate(self._data):
            if item.id == trans.id:
                self._data[n] = trans
                break
        self.render()
        
    def data(self):
        yield from self._data
        
    def render_json(self):
        pass

    def render(self):
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        for trans in self._data:
            wdgt = TransactionViewer(self.text, trans, borderwidth=2)
            for child in wdgt.winfo_children():
                child.bindtags((trans.id,) + child.bindtags())
            else:
                wdgt.bindtags((trans.id,) + self.bindtags())
            self.text.window_create('end', window=wdgt)
            self._create_popup_menu(wdgt, trans)
        self.text['state'] = 'disabled'
        #print(self.bindtags())
        
    def clean_up(self):
        self.tools_bar.destroy()
        for child in self.winfo_children():
            child.destroy()
        else: self.destroy()

    def _create_popup_menu(self, widget, value):
        menu = Menu(widget)
        menu.add_command(label='Remove Transaction', command=lambda e=value.id: self.remove_transaction(e))
        menu.add_command(label='Edit Transaction', command=lambda e=value: NewTransactionEditor(self, e))
        if self.text.tk.call('tk', 'windowingsystem') == 'aqua':
            widget.bind_class(value.id, '<2>',         lambda e: menu.post(e.x_root, e.y_root))
            widget.bind_class(value.id, '<Control-1>', lambda e: menu.post(e.x_root, e.y_root))
        else:
            widget.bind_class(value,'<3>', lambda e: menu.post(e.x_root, e.y_root))
            
