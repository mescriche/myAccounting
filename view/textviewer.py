__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk
from .transaction import TransactionViewer, DTransactionEditor, DBookEntry, DTransaction, DBookEntry_dict
from dbase import Type
from dataclasses import asdict
import json

class TextEditor(ttk.Frame):
    def __init__(self, parent, filename, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)

        new_trans_icon = PhotoImage(file='./view/icons/add.gif')
        self.tools_bar = ttk.LabelFrame(parent.tools_bar, text='Add Transaction')
        self.tools_bar.pack(expand=False, side='left')
        
        new_trans_btn = ttk.Button(self.tools_bar, image=new_trans_icon,
                                   command=lambda:DTransactionEditor(self))
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
        with open(filename, 'r') as _file:
            try: content = json.loads(_file.read())
            except:
                print(f'Wrong file format: {filename}')
                print('file not loaded')
            else:
                for n,item in enumerate(content):
                    try:
                        entries = [DBookEntry(e['account'], Type[e['type']], e['amount']) for e in item['entries']]
                        trans = DTransaction(n+1, item['date'], item['description'], entries)
                    except Exception as e:
                        print(f'Wrong format when reading item= {item}')
                        print(e)
                        self.text['state'] = 'normal'
                        self.text.insert(1.0, json.dumps(content, indent=4))
                        self.text['state'] = 'disabled'
                        break
                    else:
                        self._data.append(trans)
                else:
                    self.render()
        
    def save_to_file(self, filename=None):
        _filename = self.filename if not filename else filename
        with open(_filename, 'w') as _file:
            data = list(map(lambda x:asdict(x, dict_factory=DBookEntry_dict), self.data()))
            json.dump(data, _file, indent=4)        
                
    def add_transaction(self, trans):
        trans.id = len(self._data)+1
        self._data.append(trans)
        self.render()

    def data(self):
        yield from self._data
        
    def render_json(self):
        pass

    def render(self):
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        for trans in self._data:
            wdgt = TransactionViewer(self.text, trans)
            self.text.window_create('end', window=wdgt)
        self.text['state'] = 'disabled'

    def clean_up(self):
        self.tools_bar.destroy()
        for child in self.winfo_children():
            child.destroy()
        else: self.destroy()
