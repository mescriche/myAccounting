from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, date
from dbase import db_session, Account, Transaction, BookEntry

class TransactionView(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title('Transaction')
        #self.config(bg='skyblue')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.geometry('+{}+{}'.format(self._root().winfo_x()+20, self._root().winfo_y()+20))
        #self.geometry('700x300+300+200')
        
        self.date_entry = StringVar()
        self.account_entry = StringVar()
        self.amount_entry = StringVar()

        frame = ttk.Frame(self)
        date_frame = ttk.Frame(frame)
        ttk.Label(date_frame, text='Date:').pack(side='left')
        vdate_wrapper = (self.register(self.validate_date), '%P')
        date_entry = ttk.Entry(date_frame, width=10, textvariable=self.date_entry,
                  validate='focusout', validatecommand=vdate_wrapper)
        date_entry.pack(side='right')
        date_frame.pack(padx=10, pady=10, ipadx=5, ipady=5)
        
        ttk.Separator(frame, orient='horizontal').pack(fill='x', expand=True)
        
        accounts_frame=ttk.Frame(frame)
        from_frame=ttk.Labelframe(accounts_frame, text='From:')
        self.from_tree = ttk.Treeview(from_frame, height=5,
                                      selectmode='browse', columns=('amount', 'account'), show='headings')
        self.from_tree.heading('account' , text='Account')
        self.from_tree.column('account', width=200, stretch=False, anchor='c')
        self.from_tree.heading('amount', text='Amount(€)')
        self.from_tree.column('amount', width=100, stretch=False, anchor='e')
        self.from_tree.pack(fill='both',expand=True)
        
        minus_icon = PhotoImage(file='./view/icons/remove.gif')
        remove_button = ttk.Button(accounts_frame, image=minus_icon, command=self.remove_tree_selected)

        to_frame=ttk.Labelframe(accounts_frame, text='To:')
        self.to_tree = ttk.Treeview(to_frame, height=5, columns=('account','amount'), show='headings')
        self.to_tree.heading('amount', text='Amount(€)')
        self.to_tree.column('amount', width=100, stretch=False, anchor='e')
        self.to_tree.heading('account', text='Account')
        self.to_tree.column('account', width=200, stretch=False, anchor='c')
        self.to_tree.pack(fill='both', expand=True)
        
        from_frame.pack(side='left', fill='both', expand=True)
        remove_button.pack(side='left', anchor='s')
        to_frame.pack(side='right', fill='both', expand=True)
        accounts_frame.pack(fill='both', expand=True)
        
        
        acc_buttons_frame = ttk.Frame(frame)
        plus_icon = PhotoImage(file='./view/icons/add.gif')
        ttk.Button(acc_buttons_frame, image=plus_icon, command=self.add_from_side).pack(side='left')
        
        input_frame = ttk.Frame(acc_buttons_frame)
        input_frame.pack(side='left', expand=True)
        
        input_acc_frame = ttk.Frame(input_frame)
        ttk.Label(input_acc_frame, text="Account:").pack()
        account_field = ttk.Combobox(input_acc_frame, state='readonly',
                                     justify='center',
                                     textvariable=self.account_entry)
        account_field.bind('<<ComboboxSelected>>', lambda x:self.amount_entry.set(' '))
        account_field.pack(anchor='center')
        with db_session() as db:
            account_field['values'] = [account.name for account in db.query(Account).all()]
        account_field.current(0)
        input_acc_frame.pack( side='left', fill='x', expand=True)

        input_amnt_frame=ttk.Frame(input_frame)
        ttk.Label(input_amnt_frame, text="Amount(€):").pack()
        vamount_wrapper = (self.register(self.validate_amount), '%P')
        ttk.Entry(input_amnt_frame, width=12, justify='right',
                  textvariable=self.amount_entry,
                  validate='key', validatecommand=vamount_wrapper).pack()
        input_amnt_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Button(acc_buttons_frame, image=plus_icon, command=self.add_to_side).pack(side='right')
                
        acc_buttons_frame.pack(side='top', fill='x', expand=True)
       
        text_frame = ttk.Labelframe(frame, text='Description:')
        self.text = Text(text_frame, height=5)
        self.text.config(bg='white', fg='black')
        self.text.pack()
        text_frame.pack(fill='x', expand=True)
        
        ttk.Separator(frame, orient='horizontal').pack(fill='x', expand=True)
        
        buttons_frame=ttk.Frame(frame)
        ttk.Button(buttons_frame, text='Dismiss', command=self.dismiss).pack(side='left', padx=10, pady=10)
        self.verify_button = ttk.Button(buttons_frame, text="Verify", command=self.verify)
        self.verify_button.pack(side='left', padx=10, pady=10)
        ttk.Button(buttons_frame, text="Save", command=self.save).pack(side='right', padx=10, pady=10)
        buttons_frame.pack(side='bottom')
        
        frame.pack(side='top', anchor='n', fill='x', expand=True)
        date_entry.focus()
        # 
        date_entry.insert(0,'26-10-1964')
        self.from_tree.insert('','end', values=['50.0','Cash'])
        self.to_tree.insert('', 'end',values=['Equity','50.0'])
        self.text.insert('1.0','Hola')
            
        self.protocol("WM_DELETE_WINDOW", self.dismiss) # intercept close button
        self.wait_visibility() # can't grab until window appears, so we wait
        self.grab_set()        # ensure all input goes to our window
        self.wait_window()     # block until window is destroyed

    def validate_date(self, in_date) -> bool:
        if not in_date: return True
        else:
            try:
                datetime.strptime(in_date, "%d-%m-%Y")
            except ValueError:
                return False
            else:
                return True
                
    def validate_amount(self, amnt) -> bool:
        if not amnt: return True
        else:
            try: float(amnt)
            except ValueError:
                return False
            return True
        
    def add_from_side(self):
        if not self.amount_entry.get(): return
        try: amount = float(self.amount_entry.get())
        except ValueError: pass
        else:
            self.from_tree.insert('','end', values=(amount, self.account_entry.get()))
        finally:
            self.amount_entry.set(' ')

    def add_to_side(self):
        if not self.amount_entry.get(): return
        try: amount = float(self.amount_entry.get())
        except: ValueError
        else:
            self.to_tree.insert('','end', values=(self.account_entry.get(), amount))
        finally:
            self.amount_entry.set(' ')

    def remove_tree_selected(self):
        try: item = self.to_tree.selection()[0]
        except IndexError: pass
        else: self.to_tree.delete(item)
        try: item = self.from_tree.selection()[0]
        except IndexError: pass
        else: self.from_tree.delete(item)
    
    def dismiss(self):
        self.grab_release()
        self.destroy()

    def save(self):
        #print("save transaction")
        if self.verify():
            with db_session() as db:
                description =  self.text.get('1.0', 'end-1c')
                date = datetime.strptime(self.date_entry.get(), '%d-%m-%Y').date()
                transaction = Transaction(date=date, description=description)
                db.add(transaction)
                #asset vs claim
                ## assets are debit accounts, claims are credit accounts
                for child_id in self.from_tree.get_children():
                    child = self.from_tree.item(child_id)
                    amount, name = tuple(child['values'])
                    amount = float(amount)
                    account = db.query(Account).filter_by(name=name).one()    
                    if (account.type == 'asset'): amount = - amount
                    db.add(BookEntry(account, transaction, amount, account.balance))
                        
                for child_id in self.to_tree.get_children():
                    child = self.to_tree.item(child_id)
                    name, amount = tuple(child['values'])
                    amount = float(amount)
                    account = db.query(Account).filter_by(name=name).one()
                    if (account.type == 'claim'): amount = - amount 
                    db.add(BookEntry(account, transaction, amount, account.balance))
                
            messagebox.showinfo(title='Creating Transaction', message='OK')
            #self._root().event_generate("<<NewTransaction>>")
            self.dismiss()

    def verify(self) -> bool:
        title = "Verifiying transaction"
        from_total = sum([float(self.from_tree.item(idd)['values'][0])
                           for idd in self.from_tree.get_children()])
        to_total = sum([float(self.to_tree.item(idd)['values'][1])
                        for idd in self.to_tree.get_children()])
        if( not from_total or  not to_total):
            messagebox.showerror(title=title, message='Missing input for accounts')
            return False
        if(from_total != to_total):
            messagebox.showerror(title=title, message='Totals differ')
            return False
        if not self.date_entry.get():
            messagebox.showerror(title=title, message='Missing date')
            return False
        comment = self.text.get('1.0', 'end-1c')
        if not comment:
            messagebox.showwarning(title=title, message='Missing comment')
            return False
        return True
            
            

