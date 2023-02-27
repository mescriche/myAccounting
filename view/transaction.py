from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, date
from dbase import db_session, Account, Transaction, BookEntry

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
    
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
        debit_frame=ttk.Labelframe(accounts_frame, text='Debit:', labelanchor='n')
        self.debit_tree = ttk.Treeview(debit_frame, height=5,
                                      selectmode='browse', columns=('amount', 'account'), show='headings')
        self.debit_tree.heading('account' , text='Account')
        self.debit_tree.column('account', width=200, stretch=False, anchor='c')
        self.debit_tree.heading('amount', text='Amount(€)')
        self.debit_tree.column('amount', width=100, stretch=False, anchor='e')
        self.debit_tree.pack(fill='both',expand=True)

        credit_frame=ttk.Labelframe(accounts_frame, text='Credit:', labelanchor='n')
        self.credit_tree = ttk.Treeview(credit_frame, height=5, columns=('account','amount'), show='headings')
        self.credit_tree.heading('amount', text='Amount(€)')
        self.credit_tree.column('amount', width=100, stretch=False, anchor='e')
        self.credit_tree.heading('account', text='Account')
        self.credit_tree.column('account', width=200, stretch=False, anchor='c')
        self.credit_tree.pack(fill='both', expand=True)
        
        debit_frame.pack(side='left', fill='both', expand=True)
        credit_frame.pack(side='right', fill='both', expand=True)
        accounts_frame.pack(fill='both', expand=True)
        

        plus_icon = PhotoImage(file='./view/icons/add.gif')  
        minus_icon = PhotoImage(file='./view/icons/remove.gif')

        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill='x', expand=True)

        debit_buttons_frame = ttk.Frame(controls_frame)
        ttk.Button(debit_buttons_frame, image=plus_icon, command=self.add_debit_side).pack(side='left')
        ttk.Button(debit_buttons_frame, image=minus_icon, command=self.remove_debit_selected).pack(side='left')
        
        input_frame = ttk.Frame(controls_frame)
        #
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
        #
        input_amnt_frame=ttk.Frame(input_frame)
        ttk.Label(input_amnt_frame, text="Amount(€):").pack()
        vamount_wrapper = (self.register(self.validate_amount), '%P')
        ttk.Entry(input_amnt_frame, width=12, justify='right',
                  textvariable=self.amount_entry,
                  validate='key', validatecommand=vamount_wrapper).pack()
        input_amnt_frame.pack(side='left', fill='x', expand=True)

        credit_buttons_frame = ttk.Frame(controls_frame)
        ttk.Button(credit_buttons_frame, image=plus_icon, command=self.add_credit_side).pack(side='right')
        ttk.Button(credit_buttons_frame, image=minus_icon, command=self.remove_credit_selected).pack(side='left')

        debit_buttons_frame.pack(side='left')
        input_frame.pack(side='left', expand=True)
        credit_buttons_frame.pack(side='left')

        ttk.Separator(frame, orient='horizontal').pack(fill='x', expand=True)
        
        text_frame = ttk.Labelframe(frame, text='Description:')
        self.text = Text(text_frame, height=5)
        self.text.config(bg='white', fg='black')
        self.text.pack(fill='x', expand=True)
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
        self.debit_tree.insert('','end', values=['50.0','Cash'])
        self.credit_tree.insert('', 'end',values=['Equity','50.0'])
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
        
    def add_debit_side(self):
        if not self.amount_entry.get(): return
        try: amount = float(self.amount_entry.get())
        except ValueError: pass
        else:
            self.debit_tree.insert('','end', values=(amount, self.account_entry.get()))
        finally:
            self.amount_entry.set(' ')

    def add_credit_side(self):
        if not self.amount_entry.get(): return
        try: amount = float(self.amount_entry.get())
        except: ValueError
        else:
            self.credit_tree.insert('','end', values=(self.account_entry.get(), amount))
        finally:
            self.amount_entry.set(' ')

    def remove_debit_selected(self):
        try: item = self.debit_tree.selection()[0]
        except IndexError: pass
        else: self.debit_tree.delete(item)
            
    def remove_credit_selected(self):
        try: item = self.credit_tree.selection()[0]
        except IndexError: pass
        else: self.credit_tree.delete(item)
        
    def dismiss(self):
        self.grab_release()
        self.destroy()

    def save(self):
        try: self.verify_input()
        except ValidationError as error:
            title = "Verifiying transaction"
            messagebox.showerror(title=title, message=error.message)
        else:
            with db_session() as db:
                description =  self.text.get('1.0', 'end-1c')
                date = datetime.strptime(self.date_entry.get(), '%d-%m-%Y').date()
                transaction = Transaction(date=date, description=description)
                db.add(transaction)
                # asset vs claim
                # assets are debit accounts, claims are credit accounts 
                # credit is positive for claims but negative for assets
                # debit is positive for assets but negative for claims
                for child_id in self.debit_tree.get_children():
                    child = self.debit_tree.item(child_id)
                    amount, name = tuple(child['values'])
                    amount = abs(float(amount))
                    account = db.query(Account).filter_by(name=name).one()
                    db.add(BookEntry(account=account, transaction=transaction, debit=amount))
                        
                for child_id in self.credit_tree.get_children():
                    child = self.credit_tree.item(child_id)
                    name, amount = tuple(child['values'])
                    amount = abs(float(amount))
                    account = db.query(Account).filter_by(name=name).one()
                    db.add(BookEntry(account=account, transaction=transaction, credit=amount))
            
            #messagebox.showinfo(title='Creating Transaction', message='OK')
            self.parent.event_generate("<<NewTransaction>>")
            self.dismiss()
    
    def verify_input(self):
        debit_total = sum([float(self.debit_tree.item(idd)['values'][0])
                           for idd in self.debit_tree.get_children()])
        credit_total = sum([float(self.credit_tree.item(idd)['values'][1])
                        for idd in self.credit_tree.get_children()])        
        if not debit_total or not credit_total:
            raise ValidationError('Missing input for accounts')
        if debit_total != credit_total:
            raise ValidationError('Totals mismatch')
        if not self.date_entry.get():
            raise ValidationError('No Date')
        comment = self.text.get('1.0', 'end-1c')
        if not comment:
            raise ValidationError('No Comment')
        
    def verify(self):
        try: self.verify_input()
        except ValidationError as error:
            title = "Verifiying transaction"
            messagebox.showerror(title=title, message=error.message)
        else:
            self.verify_button.config(text='OK')
            self.after(2000, lambda: self.verify_button.config(text='Verify'))
