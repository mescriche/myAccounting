__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk
from .transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
from .transaction import TransactionViewer, TransactionEditor
from dbase import Type
from datetime import datetime
import json, os

class TextEditor(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)
        self.text = Text(self, **kwargs)
        self.text.pack(expand=True, fill='both')
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')
        
    def load(self, filename):
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        self._data = list()
        self.filename = filename
        if os.stat(filename).st_size > 0:
            with open(filename, 'r') as _file:
                try: data = json.loads(_file.read())
                except:
                    print(f'Wrong file format: {filename}, expected json')
                    print('file not loaded')
                else:
                    for item in data:
                        try: trans = DMTransaction.from_json(item)
                        except Exception as e:
                            print(f'Wrong format when reading item= {item}')
                            print(e)
                            self.text['state'] = 'normal'
                            self.text.insert(1.0, json.dumps(data, indent=4))
                            self.text['state'] = 'disabled'
                            break
                        else: self._data.append(trans)
                    else: self.render()
        self.text['state'] = 'disabled'
        
    def save_to_file(self, filename=None):
        _filename = self.filename if not filename else filename
        with open(_filename, 'w') as _file:
            json.dump(self._data, _file, cls=DMTransactionEncoder, indent=4)
            
    def add_new_transaction(self, new_trans):
        if isinstance(new_trans, DMTransaction):
            try: last_trans = self._data[-1]
            except: new_trans.id = 1
            else: new_trans.id = last_trans.id + 1
            self._data.append(new_trans)
            self.render()
        elif isinstance(new_trans, list):
            for trans in new_trans:
                try: last_trans = self._data[-1]
                except: trans.id = 1
                else: trans.id = last_trans.id + 1
                self._data.append(trans)
            else:
                self.render()
        else: raise Exception('Unknown instance ')
        
    def remove_transaction(self, trans_id):
        for trans in self._data:
            if trans.id == trans_id:
                self._data.remove(trans)
                break
        self.render()

    def update_transaction(self, trans:DMTransaction):
        for n,item in enumerate(self._data):
            if item.id == trans.id:
                self._data[n] = trans
                break
        self.render()
        
    def data(self):
        yield from self._data
        
    def render(self, json=False):
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        if json:
            self.text.insert(1.0, json.dumps(self.data(), cls=DMTransactionEncoder, indent=4))
        else:
            for trans in self._data:
                wdgt = TransactionViewer(self.text, trans, borderwidth=2)
                for child in wdgt.winfo_children():
                    child.bindtags((trans.id,) + child.bindtags())
                else:
                    wdgt.bindtags((trans.id,) + self.bindtags())
                self.text.window_create('end', window=wdgt)
                self._create_popup_menu(wdgt, trans)
        self.text['state'] = 'disabled'
            
    def _create_popup_menu(self, widget, value):
        menu = Menu(widget)
        menu.add_command(label='Remove Transaction', command=lambda e=value.id: self.remove_transaction(e))
        menu.add_command(label='Edit Transaction', command=lambda e=value: self._get_updated_transaction(e))
        if self.text.tk.call('tk', 'windowingsystem') == 'aqua':
            widget.bind_class(value.id, '<2>',         lambda e: menu.post(e.x_root, e.y_root))
            widget.bind_class(value.id, '<Control-1>', lambda e: menu.post(e.x_root, e.y_root))
        else:
            widget.bind_class(value.id,'<3>', lambda e: menu.post(e.x_root, e.y_root))
        return 'break'

    def _get_updated_transaction(self, trans:DMTransaction):
        editor = TransactionEditor(self,trans)
        updated_trans = editor.trans
        if updated_trans != trans:
            self.update_transaction(updated_trans)
        
