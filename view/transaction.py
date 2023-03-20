from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, date
from dbase import db_session, Account, Transaction, BookEntry
import re

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
        self.geometry('+{}+{}'.format(self._root().winfo_x()+44, self._root().winfo_y()+88))
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
        columns = ('account', 'debit', 'credit')
        self.data = ttk.Treeview(accounts_frame, height=5,
                                       selectmode='browse', columns = columns, show='headings')
        self.data.heading('debit', text='Debit(€)')
        self.data.column('debit', width=100, stretch=False, anchor='e')        
        self.data.heading('account' , text='Account')
        self.data.column('account', width=200, stretch=True, anchor='w')
        self.data.heading('credit', text='Credit(€)')
        self.data.column('credit', width=100, stretch=False, anchor='e')
        self.data.pack(fill='both',expand=True)
        self.data.tag_configure('to', background='lightblue')
        

        accounts_frame.pack(fill='both', expand=True)
        

        plus_icon = PhotoImage(file='./view/icons/add.gif')  
        minus_icon = PhotoImage(file='./view/icons/remove.gif')

        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill='x', expand=True)

        leftside_buttons_frame = ttk.Frame(controls_frame)
        Button(leftside_buttons_frame, image=minus_icon, command=self.remove_selected,
               padx=0, pady=0, bd=0).pack(side='left', padx=2)
        Button(leftside_buttons_frame, text='To', command=self.upload_to,
               padx=0, pady=3, bd=0).pack(side='left', padx=2)
        
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
            account_field['values'] = [account.gname for account in db.query(Account).all()]
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

        rightside_buttons_frame = ttk.Frame(controls_frame)
        Button(rightside_buttons_frame, text='Debit', command=self.upload_debit,
               padx=0, pady=3, bd=0).pack(side='left', padx=2)
        Button(rightside_buttons_frame, text='Credit', command=self.upload_credit,
               padx=0, pady=3, bd=0).pack(side='left', padx=2)

        leftside_buttons_frame.pack(side='left', anchor='s')
        input_frame.pack(side='left', expand=True)
        rightside_buttons_frame.pack(side='left', anchor='s')

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

        self.date_entry.set('23-03-2022')
        self.data.insert('','end', values=('[DR-51] Bank Account', '100', '0'))
        self.data.insert('','end', values=('[CN-70] Income-Parents', '0', '100'))
        self.text.insert(1.0, 'apoyo mensual')
            
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
        
    def upload_debit(self):
        if not self.amount_entry.get(): return
        try: amount = float(self.amount_entry.get())
        except ValueError: pass
        else:
            self.data.insert('','end', values=(self.account_entry.get(), amount, '-'))
        finally:
            self.amount_entry.set(' ')

    def upload_credit(self):
        if not self.amount_entry.get(): return
        try: amount = float(self.amount_entry.get())
        except: ValueError
        else:
            self.data.insert('','end', values=(self.account_entry.get(), '-', amount))
        finally:
            self.amount_entry.set(' ')
    def upload_to(self):
        self.data.insert('', 'end', values=('{:-^70}'.format(' To '), '', ''), tags=('to'))
            
    def remove_selected(self):
        try: item = self.data.selection()[0]
        except IndexError: pass
        else: self.data.delete(item)
            
    def dismiss(self):
        self.grab_release()
        self.destroy()

    def save(self):
        try: self.verify_input()
        except ValidationError as error:
            title = "Verifiying transaction"
            messagebox.showerror(title=title, message=error.message)
        else:
            ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\s\w]+')
            with db_session() as db:
                description =  self.text.get('1.0', 'end-1c')
                try: date = datetime.strptime(self.date_entry.get(), '%d-%m-%Y').date()
                except: raise Exception(f'Wrong date format:"{self.date_entry.get()}"')
                transaction = Transaction(date=date, description=description)
                db.add(transaction)
                for child_id in self.data.get_children():
                    child = self.data.item(child_id)
                    acc_name, debit, credit = tuple(child['values'])
                    if match := ptrn.fullmatch(acc_name):
                        code = match.group('code')
                        try: account = db.query(Account).filter_by(code=code).one()
                        except: raise Exception(f'Unknown code:"{code}"')
                        try: debit = abs(float(debit))
                        except ValueError: debit = 0.0
                        try: credit = abs(float(credit))
                        except ValueError: credit = 0.0
                        db.add(BookEntry(account=account, transaction=transaction, debit=debit, credit=credit))
                    else :
                        raise Exception(f'Wrong account pattern:"{acc_name}"')
            self.master.event_generate("<<DataBaseContentChanged>>")
            self.dismiss()
    
    def verify_input(self):
        debit_total, credit_total = 0,0
        for idd in self.data.get_children():
            #print(self.data.item(idd))
            debit = self.data.item(idd)['values'][1]
            credit = self.data.item(idd)['values'][2]
            try: debit = float(debit)
            except ValueError: pass    
            else: debit_total += debit
            try: credit = float(credit)
            except ValueError: pass
            else:  credit_total += credit                
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
