import locale
locale.setlocale(locale.LC_ALL, '')

from tkinter import *
from tkinter import ttk
from view import View 
from control import Controller

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title('Personal Accounting')
        window_size = 800,600
        screen_size = self.winfo_screenwidth(), self.winfo_screenheight()
        center =  int((screen_size[0] - window_size[0]) / 2) , int((screen_size[1] - window_size[1]) / 2)
        self.geometry(f'{window_size[0]}x{window_size[1]}+{center[0]}+{center[1]}')
        self.resizable(True, True)
        self.style = ttk.Style()
        #print(self.style.theme_names())
        self.style.theme_use('default')
        #self.config(bg='skyblue')
        
        self.option_add('*tearOff', False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.createcommand('tk::mac::Quit', self.destroy)
        
        view = View(self)
        
        #sg = ttk.Sizegrip(self)
        #sg.grid(row=1, sticky=SE)
        #view.grid(row=0, column=0, padx=10, pady=10)
        #self.bind("<Return>", view.calculate)
        #model = Model()
        #controller = Controller(model,view)
        controller = Controller(view)
        view.set_controller(controller)
        #print(self.tk.call('tk', 'windowingsystem'))
        
        
if __name__ == '__main__':
    app = App()
    app.mainloop()


    
