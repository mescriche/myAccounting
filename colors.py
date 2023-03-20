import os, codecs
from tkinter import *
from tkinter import ttk
from html.parser import HTMLParser
from json import load

class MyHTMLParser(HTMLParser):
    
    def set_output(self, filename):
        self._file_ = open(filename, 'w', encoding='utf-8')
        
    def handle_starttag(self, tag, attrs):
        #print( tag)
        pass
    
    def handle_endtag(self, tag):
        #print(tag)
        pass
    
    def handle_data(self, data):
        try: int(data)
        except ValueError as e:
            msg = f',"{data}"'
            self._file_.write(msg)
            print('data:', msg)
        else: pass
        
    def close(self):
        self._file_.close()

class ColorView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        colors_source = 'colors.html'
        colors_target = 'colors.json'
        config_dir = 'config'
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config_dir = os.path.join(current_dir, config_dir)
        source = os.path.join(config_dir, colors_source)
        target = os.path.join(config_dir, colors_target)
        
        #parser = MyHTMLParser()
        #parser.set_output(target)
        #with codecs.open(source, 'r', encoding='utf-8', errors='ignore') as _file:
        #    while line := _file.readline():
        #        parser.feed(line)
        with open(target) as _file:
            self.colors = load(_file)
            
    def render(self):
        self.text['state'] = 'normal'
        self.text.insert('end', 'Colors\n')
        for color in self.colors:
            try: 
                label1 = Label(self.text, width=20, text=color, foreground='white', background=color)
                label2 = Label(self.text, width=20, text=color, foreground='black', background=color)
            except TclError as e:
                print(e)
            else:
                #self.text.insert('end', f"{color:<20}: ")
                self.text.window_create('end', window=label1)
                self.text.window_create('end', window=label2)
                self.text.insert('end', '\n')
        self.text['state'] = 'disabled'
        self.text.focus_set()
        
class App(Tk):
    def __init__(self):
        super().__init__()
        self.title('Colors')
        window_size = 500,600
        screen_size = self.winfo_screenwidth(), self.winfo_screenheight()
        center =  int((screen_size[0] - window_size[0]) / 2) , int((screen_size[1] - window_size[1]) / 2)
        self.geometry(f'{window_size[0]}x{window_size[1]}+{center[0]}+{center[1]}')
        self.resizable(True, True)
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.createcommand('tk::mac::Quit', self.destroy)
        self.view = ColorView(self)
        self.view.render()

if __name__ == '__main__':
    app = App()
    app.mainloop()
