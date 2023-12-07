__author__ = 'Manuel Escriche'
import locale
locale.setlocale(locale.LC_ALL, '')

import sys, os
tools_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(tools_dir)
sys.path.append(root_dir)

from view.ledger import LedgerView
from view.excelreader import create_excel_reader
from view.excel_editor import ExcelEditor
#import pandas, argparse


#parser = argparse.ArgumentParser(prog='xlsReader')
#parser.add_argument('filename', help="xls file to be transformed into xlsx")
#args = parser.parse_args()
#print(args.filename)


excelfiles_dir = os.path.join(root_dir, 'excelfiles')

#filename_dir = os.path.join(root_dir, datafile_dir)
#filename = args.filename
#basename, ext = os.path.splitext(filename)

#dirname = os.path.dirname(args.filename)
#basename = os.path.basename(args.filename).removesuffix('.xls')

#if not os.path.exists(filename):
#    print(f"{filename} does not exists")
#    exit()

#if ext == '.xls':
#    new_filename = os.path.join(dirname, basename+'.xlsx')    
#    if os.path.exists(new_filename):
#        os.remove(new_filename)
#        print(f"existing {new_filename} has been removed")

    
#    df = pandas.read_html(f'{filename}', thousands='.', decimal=',')
#    df_sh = df[0]
#    df_sh.to_excel(new_filename, index=False, header=False, engine='openpyxl', float_format="%.2f")

#    try: reader = create_excel_reader(new_filename)
#    except Exception as e:
#        print (e)
#        raise
#    else:
#        for item in reader.data[:10]:
#            print(item)
#        target = os.path.join(dirname, reader.filename)
#        os.replace(new_filename, target)
#        print(f'file {reader.filename} has been created')
#    
#        source = target.removesuffix('.xlsx') + '.xls'
#        if filename != source:
#            os.rename(filename, source)
#            print(f'file {filename} has been rename to {source}')

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class ExcelView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)
        
        DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.dirname = os.path.join(DIR, 'excelfiles')
        self.filename = StringVar()
        
        tools_bar = ttk.Frame(self, height=15)
        tools_bar.pack(expand=False, fill='x', padx=1, pady=1)
        
        file_bar = ttk.Labelframe(tools_bar, text='File')
        file_bar.pack(expand=False, side='left', ipady=4, ipadx=3)

        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        save_file_btn = ttk.Button(file_bar, image=save_file_icon, command=self.save_file)
        save_file_btn.image = save_file_icon
        save_file_btn.pack(side='left',padx=10)

        self.file_name_entry = ttk.Combobox(file_bar, textvariable=self.filename, width=45, postcommand= self._get_filenames)
        self.file_name_entry.pack(side='left')
        self.file_name_entry.bind('<<ComboboxSelected>>', self._open_file)

        import_bar = ttk.Labelframe(tools_bar, text='Import', labelanchor='n')
        import_bar.pack(expand=False, side='left', ipadx=10)

        
        long_play_icon = PhotoImage(file='./view/icons/end.gif')
        long_play_btn = ttk.Button(import_bar, image=long_play_icon, command=self.execute)
        long_play_btn.image = long_play_icon
        long_play_btn.pack(padx=0)

        self.editor = ExcelEditor(self)
        
    def _get_filenames(self):
        files = (file for file in os.listdir(self.dirname) if os.path.isfile(os.path.join(self.dirname, file)))
        _files = filter(lambda x: x.endswith('.xls') or x.endswith('.xlsx'), files)
        #self.file_name_entry['values'] = sorted(list(map(lambda x: x.removesuffix('.xls'), _files)), reverse=True)
        self.file_name_entry['values'] = sorted(list(_files), reverse=True)

    def _open_file(self, event=None):
        
        filename = os.path.join(self.dirname, self.filename.get())
        print(filename)
        self.editor.load(filename)

    def execute_step_by_step(self):
        pass

    def execute(self):
        pass

    def save_file(self):
        pass

class XlsReader(Tk):
    def __init__(self):
        super().__init__()
        self.title('Excel Reader')
        window_size = 1100, 600
        screen_size = self.winfo_screenwidth(), self.winfo_screenheight()
        center =  int((screen_size[0] - window_size[0]) / 2) , int((screen_size[1] - window_size[1]) / 2)
        self.geometry(f'{window_size[0]}x{window_size[1]}+{center[0]}+{center[1]}')
        self.resizable(True, True)
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.option_add('*tearOff', False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.createcommand('tk::mac::Quit', self.destroy)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.input = ExcelView(self.notebook)
        self.notebook.add(self.input, text='Excel')

        self.ledger = LedgerView(self.notebook)
        self.notebook.add(self.ledger, text='Ledger')
        
        #filename = filedialog.askopenfilename(defaultextension="*.xls",
        #                                      initialdir = excelfiles_dir,
        #                                      filetypes = [("All files", "*.*"),
        #                                                   ("Excel Documents", "*.xls")])
        #
        #editor = ExcelEditor(self, filename)
        #trans_list = editor.trans_list
        
if __name__ == '__main__':
    app = XlsReader()
    app.mainloop()
