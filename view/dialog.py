from tkinter import *

def _setup_dialog(w):
    if w._windowingsystem == "aqua":
        w.tk.call("::tk::unsupported::MacWindowStyle", "style",
                  w, "moveableModal", "")
    elif w._windowingsystem == "x11":
        w.wm_attributes("-type", "dialog")
        
def _place_window(w, parent=None):
    w.wm_withdraw() # Remain invisible while we figure out the geometry
    w.update_idletasks() # Actualize geometry information

    minwidth = w.winfo_reqwidth()
    minheight = w.winfo_reqheight()
    maxwidth = w.winfo_vrootwidth()
    maxheight = w.winfo_vrootheight()
    if parent is not None and parent.winfo_ismapped():
        x = parent.winfo_rootx() + (parent.winfo_width() - minwidth) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - minheight) // 2
        vrootx = w.winfo_vrootx()
        vrooty = w.winfo_vrooty()
        x = min(x, vrootx + maxwidth - minwidth)
        x = max(x, vrootx)
        y = min(y, vrooty + maxheight - minheight)
        y = max(y, vrooty)
        if w._windowingsystem == 'aqua':
            # Avoid the native menu bar which sits on top of everything.
            y = max(y, 22)
    else:
        x = (w.winfo_screenwidth() - minwidth) // 2
        y = (w.winfo_screenheight() - minheight) // 2

    w.wm_maxsize(maxwidth, maxheight)
    w.wm_geometry('+%d+%d' % (x, y))
    w.wm_deiconify() # Become visible at the desired location


    
class Dialog(Toplevel):
    def __init__(self, parent, title=None):
        master = parent
        super().__init__(master)
        self.withdraw()
        if parent is not None and parent.winfo_viewable():
            self.transient(parent)

        if title:
            self.title(title)
        _setup_dialog(self)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        if self.initial_focus is None:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        _place_window(self, parent)

        self.wait_visibility()
        #self.grab_set()
        self.wait_window(self)

    def destroy(self):
        self.initial_focus = None
        Toplevel.destroy(self)
        #_destroy_temp_root(self.master)


    def body(self, master):
        pass

    def buttonbox(self):
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()
            
    def cancel(self, event=None):
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    def validate(self):
        return 1

    def apply(self):
        pass
    
