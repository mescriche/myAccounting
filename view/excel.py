__author__ = 'Manuel Escriche'

from tkinter import *
from tkinter import ttk
from .excel_editor import ExcelEditor
import os

class ExcelView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)
        view_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = os.path.dirname(view_dir)
        self.dirname = os.path.join(root_dir, 'excelfiles')
        self.filename = StringVar()
        
        file_bar = ttk.Labelframe(self, text='File')
        file_bar.pack(expand=True, fill='x', ipady=4, ipadx=3)

        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        save_file_btn = ttk.Button(file_bar, image=save_file_icon, command=self.save_file)
        save_file_btn.image = save_file_icon
        save_file_btn.pack(side='left',padx=10)

        self.file_name_entry = ttk.Combobox(file_bar, textvariable=self.filename, width=40, postcommand= self._get_filenames)
        self.file_name_entry.pack(side='left')
        self.file_name_entry.bind('<<ComboboxSelected>>', self._open_file)

        verify_btn = ttk.Button(file_bar, text='Verify', command = self.verify_table)
        verify_btn.pack(side='left', padx=10)
        
        export_btn = ttk.Button(file_bar, text='Blackboard', command = self.export)
        export_btn.pack(side='left', padx=10)
        
        self.editor = ExcelEditor(self)
        
    def _get_filenames(self):
        files = (file for file in os.listdir(self.dirname) if os.path.isfile(os.path.join(self.dirname, file)))
        _files = filter(lambda x: x.endswith('.xls') or x.endswith('.xlsx'), files)
        self.file_name_entry['values'] = sorted(list(_files), reverse=True)

    def _open_file(self, event=None):
        filename = os.path.join(self.dirname, self.filename.get())
        self.editor.load(filename)

    def execute_step_by_step(self):
        pass

    def execute(self):
        pass

    def save_file(self):
        pass

    def verify_table(self):
        pass

    def export(self):
        pass
