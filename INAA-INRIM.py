#imports
import os
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
import numpy as np
import pandas as pd
from scipy.optimize import minimize

import classes.recovery as recovery_script
#try:
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import classes.GUI_things as gui_things
#import classes.naaoutputs as naaoutput
import classes.naanalysis as naaobject


class MainWindow:
    # only one subwindow open at a time
    def __init__(self, M, settings, home):
        __version__ = 3.1
        self.main_window = tk.Frame(M)
        self.main_window.pack(anchor=tk.NW, padx=5, pady=5)
        M.resizable(False, False)
        M.home = home
        M.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(M))
        M._version = f'INAA-INRIM version {__version__}'

        M.settings = settings
        M.unclosablewindows = ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation')
        M.InformationWindow = None
        M.trigger_emission_assignment = False

        M.INAAnalysis = None

        M.progressbar = ttk.Progressbar(M, orient='horizontal')
        M.progressbar.pack(fill=tk.X)
        M.progressbar['value'] = 1
        M.progressbar['maximum'] = 1
        M.progressbar.update()

        M.hintlabel = tk.Label(M, text=M._version, width=70, anchor=tk.W)
        M.hintlabel.pack(anchor=tk.W)
        clear_window(self.main_window)
        WelcomeWindow(self.main_window, M)

    def on_closing(self, M, title='Quit INAA-INRIM', message='Unsaved data will be lost.\n\nDo you want to quit?'):
        if messagebox.askokcancel(title, message):
            M.destroy()


def clear_window(window):
    #clears all children in window
    cdn = window.winfo_children()
    for i in cdn:
        i.destroy()


class UsefulUnusefulInformationWindow:
    def __init__(self, parent):
        parent.title('INAA-INRIM information')
        parent.resizable(False, False)

        welcome_info = 'INAA-INRIM version 3.1\n\nThis software is developed as an aid for analysts to perform INAA measurement (with application of either relative and k0 method) and a support to compile uncertainty budgets.\nIt was built from the merging of two separate projects (k0-INRIM and Rel-INRIM) concerning the application of k0 and relative methods but sharing various features and modelizations.\nThe produced uncertainty budgets are standalone and exportable in Microsoft Excel format; it could take into account measurement performed on different emissions, samples and irradiation'

        contact_info = 'Inquiries can be sent to the following email addresses\n\nm.diluzio@inrim.it\ng.dagostino@inrim.it'

        license_info = 'INAA-INRIM © 2024 by Marco Di Luzio is licensed under Creative Commons Attribution 4.0 International.\n\nTo view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/'

        reference_info = '\n\n'.join(['References to the various publications related to the INAA-INRIM software',

        """MEASUREMENT MODEL AND UNCERTAINTY EVALUATION\n\n# D'Agostino et al; "Development and application of a comprehensive measurement equation for the direct comaprator standardization method of Instrumental Neutron Activation Analysis"\nSubmitted to: Spectrochimica Acta Part B (2024)\nDOI: XX.XXXX/XXXXXX-XXX-XXXXX-X\n\n# Di Luzio et al; "Developments of the k0-NAA measurement model implemented in k0-INRIM software"\nJournal of Radioanalytical and Nuclear Chemistry (2022)\nDOI: 10.1007/s10967-022-08476-x\n\n# Di Luzio et al; "A method to deal with correlations affecting γ counting efficiencies in analytical chemistry measurements performed by k0-NAA"\nMeasurement Science and Technology (2020)\nDOI: 10.1088/1361-6501/ab7ca8\n\n# D'Agostino et al; "An uncertainty spreadsheet for the k0-standardisation method in Neutron Activation Analysis"\nJournal of Radioanalytical and Nuclear Chemistry (2018)\nDOI: 10.1007/s10967-018-6094-8""",

        'SOFTWARE VALIDATION:\n\n# Di Luzio et al; "Validation of detection efficiency-based corrections implemented in the k0-INRIM software"\nJournal of Radioanalytical and Nuclear Chemistry (2024)\nDOI: 10.1007/s10967-023-09223-6\n\n# Blaauw et al; "The 2021 IAEA software intercomparison for k0-INAA"\nJournal of Radioanalytical and Nuclear Chemistry (2023)\nDOI: 10.1007/s10967-022-08626-1',

        """REFERENCE TO PREVIOUS VERSIONS\n\n# Di Luzio et al; "The k0-INRIM software version 2.0: presentation and an analysis vademecum"\nJournal of Radioanalytical and Nuclear Chemistry (2023)\nDOI: 10.1007/s10967-022-08622-5\n\nD'Agostino et al; "Erratum: The k0-INRIM software: A tool to compile uncertainty budgets in neutron activation analysis based on k0-standardisation"\nMeasurement Science and Technology (2020)\nDOI: 10.1088/1361-6501/ab57c8"""
        ])

        version_info = '\n\n'.join(['# version 3.1 (2024)\n-> bugfix to model (efficiency ratio)', '# version 3.0 (2024)\n-> elaboration with relative method (from rel-INRIM)\n-> elaboration with k0 method (from k0-INRIM)\n-> adoption of updated model with macro-parameters\n-> iterative composition evaluation\n-> combination of measurements from various analysis\n-> result given as sample-per-sample averaged budgets\n-> standalone and protected spreadsheet output files'])

        self._infodict = {'welcome' : welcome_info, 'references' : reference_info, 'license' : license_info, 'versions' : version_info, 'contacts' : contact_info}
        self.labelwidget = tk.Label(parent, text='')

        itemlist_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text='index'), relief='solid', bd=2, padx=4, pady=4)
        itemlist_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NW)

        text_frame = tk.LabelFrame(parent, labelwidget=self.labelwidget, relief='solid', bd=2, padx=4, pady=4)
        text_frame.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky=tk.NSEW)

        logo_k0main = tk.PhotoImage(data=gui_things.PL_logoinrim_white)
        k0logo = tk.Label(parent, image=logo_k0main)
        k0logo.grid(row=1, column=1, pady=5, padx=5, sticky=tk.S)
        k0logo.image = logo_k0main

        self.items_LB = gui_things.ScrollableListbox(itemlist_frame, width=20, height=len(self._infodict), data=('welcome', 'license', 'references', 'versions', 'contacts'), relief='solid')
        self.items_LB.pack(anchor=tk.NW)
        self.space_TX = gui_things.ScrollableText(text_frame, width=60, height=15)
        self.space_TX.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)

        text = self._infodict.get('welcome', '')        
        self.labelwidget.configure(text='welcome')
        self.space_TX._update(text)

        self.items_LB.listbox.bind('<Double-Button-1>', lambda e='<Double-Button-1>': self.dclick())

    def dclick(self):
        idx = self.items_LB.get_selection()

        if idx not in self._infodict.keys():
            idx = 'welcome'
        text = self._infodict.get(idx, '')        
        
        self.labelwidget.configure(text=idx)        
        self.space_TX._update(text)


class WelcomeWindow:
    def __init__(self, parent, M):
        mframe = tk.Frame(parent)
        M.title('The INRIM toolbox')
        first_line = tk.Frame(mframe)

        logo_infos = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_infos = gui_things.Button(first_line, image=logo_infos, hint='useful and unuseful info', hint_destination=M.hintlabel, command=lambda : self.go_to_unusefulinformation(parent, M))
        B_infos.pack(side=tk.LEFT, anchor=tk.NW)
        B_infos.image = logo_infos
        tk.Label(first_line, text='welcome to the INAA-INRIM experience!\nversion 3.1, 2024', justify=tk.LEFT, anchor=tk.W).pack(side=tk.LEFT, anchor=tk.W, padx=5)
        button_header = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='settings & data'), relief='solid', bd=2, padx=4, pady=4)
        first_line.pack(anchor=tk.NW, fill=tk.X, expand=True)

        col = 0
        logo_settings = tk.PhotoImage(data=gui_things.PL_ggear)
        B_settings = gui_things.Button(button_header, image=logo_settings, hint='settings', hint_destination=M.hintlabel, command=lambda : self.go_to_settings(parent, M))
        B_settings.grid(row=0, column=0, sticky=tk.W)
        B_settings.image = logo_settings

        ttk.Separator(button_header, orient="vertical").grid(
            row=0, column=1, sticky=tk.NS, padx=3)

        logo_libraries = tk.PhotoImage(data=gui_things.PL_bookmark)
        B_libraries = gui_things.Button(button_header, image=logo_libraries, hint='databases', hint_destination=M.hintlabel, command=lambda : self.go_to_databasesettings(parent, M))
        B_libraries.grid(row=0, column=2, sticky=tk.W)
        B_libraries.image = logo_libraries

        ttk.Separator(button_header, orient="vertical").grid(
            row=0, column=3, sticky=tk.NS, padx=3)

        logo_loadNAA = tk.PhotoImage(data=gui_things.PL_florish)
        B_loadNAA = gui_things.Button(button_header, image=logo_loadNAA, hint='load analysis', hint_destination=M.hintlabel)
        B_loadNAA.grid(row=0, column=4, sticky=tk.W)
        B_loadNAA.image = logo_loadNAA

        button_header.pack(anchor=tk.NW, padx=5, pady=5)

        analysis_space = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='analysis'), relief='solid', bd=2, padx=4, pady=4)

        M.variable_new_analysis = tk.IntVar(M)
        M.variable_new_analysis.set(0)
        CHB_new_analysis = tk.Checkbutton(analysis_space, onvalue=1, offvalue=0, variable=M.variable_new_analysis, text='new analysis')
        CHB_new_analysis.grid(row=3, column=0, sticky=tk.W)

        logo_relmain = tk.PhotoImage(data=gui_things.PL_logoinaa)
        B_k0 = gui_things.Button(analysis_space, image=logo_relmain, hint='INAA-INRIM analysis', hint_destination=M.hintlabel, command=lambda : self.go_to_analysis(parent, M))
        B_k0.grid(row=2, column=0, sticky=tk.W, pady=5)
        B_k0.image = logo_relmain

        analysis_space.pack(anchor=tk.NW, padx=5, pady=5)

        manageresults_space = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='manage results'), relief='solid', bd=2, padx=4, pady=4)

        ttk.Separator(manageresults_space, orient="vertical").grid(
            row=2, column=4, sticky=tk.NS, padx=3)

        logo_showres_3 = tk.PhotoImage(data=gui_things.PL_output_sam)
        B_showresults_3 = gui_things.Button(manageresults_space, image=logo_showres_3, hint='show merged results (grouped by sample)', hint_destination=M.hintlabel, command=lambda : self.go_to_showmergedresults(parent, M, 'sample'))
        B_showresults_3.grid(row=2, column=3, sticky=tk.W)
        B_showresults_3.image = logo_showres_3

        logo_showres_4 = tk.PhotoImage(data=gui_things.PL_output_mat)
        B_showresults_4 = gui_things.Button(manageresults_space, image=logo_showres_4, hint='show merged results (grouped by material)', hint_destination=M.hintlabel, command=lambda : self.go_to_showmergedresults(parent, M, 'material'))
        B_showresults_4.grid(row=2, column=5, sticky=tk.W)
        B_showresults_4.image = logo_showres_4

        manageresults_space.pack(anchor=tk.NW, padx=5, pady=5)

        mframe.pack(anchor=tk.NW)

        B_loadNAA.configure(command=lambda : self._call_previously_saved_analysis_(parent, M))

    def _call_previously_saved_analysis_(self, parent, M):
        filetypes = (('INAAnalysis save file','*.naas'),)
        filename = askopenfilename(parent=parent, title=f'Recall analysis file',filetypes=filetypes)
        if filename != '':
            recalled_results = naaobject._call_results(filename)
            if isinstance(recalled_results, naaobject.RelAnalysis):
                M.INAAnalysis = recalled_results
                M.variable_new_analysis.set(0)
                M.hintlabel.configure(text='analysis loaded')
            else:
                M.hintlabel.configure(text='impossible to load, incorrect file format')

    def go_to_analysis(self, parent, M):
        clear_window(parent)
        #initialize k0_NAA
        if M.INAAnalysis is None or M.variable_new_analysis.get() == 1:
            M.INAAnalysis = naaobject.RelAnalysis(M.settings)
        RelINRIM_MainWindow(parent, M)

    def go_to_showmergedresults(self, parent, M, vtype='sample'):
        filetypes = (('Budget Object','*.boj'),)
        filenames = askopenfilenames(parent=parent, title=f'Recall analysis results',filetypes=filetypes)
        if filenames != () and len(filenames) < 27:
            recalled_results = []
            for nnn, savedfile in enumerate(filenames):
                recalled_results += naaobject._call_results_and_indicize(savedfile, nnn)

            lb_filenames = [f'{letter}) {filename}' for letter, filename in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', filenames)]

            RW = tk.Toplevel(parent)
            RW.resizable(False, False)
            RW.title(f'Merged results from {len(filenames)} savefiles')
            all_colors = (M.settings.get('color04'), M.settings.get('color05'), M.settings.get('color06'), M.settings.get('color07'), M.settings.get('color08'), M.settings.get('color09'), M.settings.get('color10'), M.settings.get('color11'), M.settings.get('color12'), M.settings.get('color01'), M.settings.get('color02'), M.settings.get('color03'))
            PTR = gui_things.PeriodicTable(RW, recalled_results, default_palette=M.settings.get('color palette'), colors=(M.settings.get('color01'), M.settings.get('color02'), M.settings.get('color03')), allcolors=all_colors, visualization_type=vtype, display_type='show', lock_cells=M.settings.get('excel worksheet lock'), set_autolinks=M.settings.get('excel internal links'), origin_files=lb_filenames, visible_models=M.settings.get('visible models'), hide_grid=M.settings.get('hide grid'))
            PTR.pack(anchor=tk.NW, padx=5, pady=5)
        elif len(filenames) >= 27:
            M.hintlabel.configure(text='too many files')

    def go_to_showresults(self, parent, M, vtype='sample'):
        filetypes = (('Budget Object','*.boj'),)
        filename = askopenfilename(parent=parent, title=f'Recall analysis results',filetypes=filetypes)
        if filename != '':
            recalled_results = naaobject._call_results(filename)

            RW = tk.Toplevel(parent)
            RW.resizable(False, False)
            RW.title(os.path.basename(filename).split('.', 1)[0])
            all_colors = (M.settings.get('color04'), M.settings.get('color05'), M.settings.get('color06'), M.settings.get('color07'), M.settings.get('color08'), M.settings.get('color09'), M.settings.get('color10'), M.settings.get('color11'), M.settings.get('color12'), M.settings.get('color01'), M.settings.get('color02'), M.settings.get('color03'))
            PTR = gui_things.PeriodicTable(RW, recalled_results.results, default_palette=M.settings.get('color palette'), colors=(M.settings.get('color01'), M.settings.get('color02'), M.settings.get('color03')), allcolors=all_colors, visualization_type=vtype, display_type='show', lock_cells=M.settings.get('excel worksheet lock'), set_autolinks=M.settings.get('excel internal links'), visible_models=M.settings.get('visible models'), hide_grid=M.settings.get('hide grid'))
            PTR.pack(anchor=tk.NW, padx=5, pady=5)

    def go_to_settings(self, parent, M):
        clear_window(parent)
        SettingsWindow(parent, M)

    def go_to_databasesettings(self, parent, M):
        clear_window(parent)
        DatabaseWindow(parent, M)
    
    def go_to_unusefulinformation(self, parent, M):
        try:
            M.InformationWindow.destroy()
        except:
            pass
        M.InformationWindow = tk.Toplevel(parent)
        UsefulUnusefulInformationWindow(M.InformationWindow)


class SettingsWindow:
    def __init__(self, parent, M):
        mframe = tk.Frame(parent)
        M.title('Settings')
        labelspace = 25

        header = tk.Frame(mframe)

        logo_back_to_welcome = tk.PhotoImage(data=gui_things.PL_aback)
        B_back = gui_things.Button(header, image=logo_back_to_welcome, hint='back to main menu', hint_destination=M.hintlabel, command=lambda : self.go_back(parent, M))
        B_back.pack(side=tk.LEFT)
        B_back.image = logo_back_to_welcome

        ttk.Separator(header, orient="vertical").pack(fill=tk.Y, side=tk.LEFT, padx=3)

        logo_confirm_changes = tk.PhotoImage(data=gui_things.PL_save)
        B_confirm = gui_things.Button(header, image=logo_confirm_changes, hint='confirm changes', hint_destination=M.hintlabel, command=lambda : self.confirm_options(M))
        B_confirm.pack(side=tk.LEFT)
        B_confirm.image = logo_confirm_changes

        header.grid(row=0, column=0, sticky=tk.W)

        notebook = ttk.Notebook(mframe, height=250)
        gframe = tk.Frame(notebook)
        nrow = 0
        
        nrow += 1
        gui_things.Label(gframe, text='line 2', hint='', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        
        nrow += 1
        gui_things.Label(gframe, text='line 3', hint='', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        gframe.pack(anchor=tk.NW, padx=5, pady=5)

        peak_identification = tk.Frame(notebook)
        nrow = 0
        gui_things.Label(peak_identification, text='energy tolerance / keV', hint='for peak identification algorithm', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_energy_tolerance = gui_things.FSlider(peak_identification, decimals=2, label_width=4, resolution=0.05, from_=0.1, to=2.0, default=M.settings.get('energy tolerance'))
        variable_energy_tolerance.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        gui_things.Label(peak_identification, text='elaborate selection only', hint='elaborate only emission selected in sample peaklist', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_elaborate_only_selected = gui_things.OnOffButton(peak_identification, default=M.settings.get('elaborate only selected emissions'))
        variable_elaborate_only_selected.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        gui_things.Label(peak_identification, text='overwrite manual identification', hint='for peak identification algorithm', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_overwrite_emission_selection = gui_things.OnOffButton(peak_identification, default=M.settings.get('overwrite manual emission selection'))
        variable_overwrite_emission_selection.grid(row=nrow, column=1, sticky=tk.E)
        nrow += 1
        gui_things.Label(peak_identification, text='max peak uncertainty (characterization)', hint='exclude peaks with higher statistical uncertainty (characterization spectra)', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_statistics_characterization = gui_things.Slider(peak_identification, percent=True, label_width=4, resolution=1, from_=1, to=10, default=M.settings.get('calibs statistical uncertainty limit'))
        variable_statistics_characterization.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        gui_things.Label(peak_identification, text='max peak uncertainty (standards)', hint='exclude peaks with higher statistical uncertainty (standard spectra)', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_statistics_standard = gui_things.Slider(peak_identification, percent=True, label_width=4, resolution=1, from_=1, to=15, default=M.settings.get('standard statistical uncertainty limit'))
        variable_statistics_standard.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        gui_things.Label(peak_identification, text='max peak uncertainty (samples)', hint='exclude peaks with higher statistical uncertainty (sample spectra)', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_statistics_sample = gui_things.Slider(peak_identification, percent=True, label_width=4, resolution=1, from_=5, to=40, default=M.settings.get('sample statistical uncertainty limit'))
        variable_statistics_sample.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        gui_things.Label(peak_identification, text='count rate alert (threshold) / s⁻¹', hint='raise an alert if peak count rate exceeds the threshold in counts per second', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        count_rate_alert = gui_things.Slider(peak_identification, percent=False, label_width=4, resolution=10, from_=10, to=1000, default=M.settings.get('count rate threshold'))
        count_rate_alert.grid(row=nrow, column=1, sticky=tk.E)
        peak_identification.pack(anchor=tk.NW, padx=5, pady=5)

        nrow += 1
        gui_things.Label(peak_identification, text='check peak consistency', hint='calculate z value for emissions from same target', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        check_internal_peak_consistency = gui_things.OnOffButton(peak_identification, default=M.settings.get('check internal consistency'))
        check_internal_peak_consistency.grid(row=nrow, column=1, sticky=tk.E)
        peak_identification.pack(anchor=tk.NW, padx=5, pady=5)

        nrow += 1
        gui_things.Label(peak_identification, text='z value limit for consistency', hint='threshold for peak consistency', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        z_limit_variable = gui_things.FSlider(peak_identification, decimals=2, label_width=4, resolution=0.50, from_=2.0, to=5.0, default=M.settings.get('z limit'))
        z_limit_variable.grid(row=nrow, column=1, sticky=tk.E)

        elaboration = tk.Frame(notebook)
        nrow = 0
        gui_things.Label(elaboration, text='number of iterations', hint='max limit for iterative processes', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_iterations = gui_things.Slider(elaboration, percent=False, label_width=4, resolution=5, from_=0, to=15, default=M.settings.get('max iterations'))
        variable_iterations.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        gui_things.Label(elaboration, text='default f-α correlation', hint='set a correlation value adopted as default for f and α', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_fluxcorrelation = gui_things.FSlider(elaboration, decimals=3, label_width=6, resolution=0.001, from_=-1.0, to=1.0, default=M.settings.get('f&a correlation'))
        variable_fluxcorrelation.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        #gui_things.Label(elaboration, text='composition update', hint='merging prior and posterior information', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_priormerge = gui_things.Combobox(elaboration, width=15, state='readonly')
        #variable_priormerge.grid(row=nrow, column=1, sticky=tk.E)
        variable_priormerge['values'] = ('Bayes', 'average', 'neglect')
        variable_priormerge.set(M.settings.get('merge with prior'))

        nrow += 1
        #gui_things.Label(elaboration, text='average formula', hint='formula to adopt for averaging', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_averagetype = gui_things.Combobox(elaboration, width=15, state='readonly')
        #variable_averagetype.grid(row=nrow, column=1, sticky=tk.E)
        variable_averagetype['values'] = ('weighted', 'aritmetic')
        variable_averagetype.set(M.settings.get('average method'))
        
        elaboration.pack(anchor=tk.NW, padx=5, pady=5)


        relframe = tk.Frame(notebook)
        relframe.pack(anchor=tk.NW, padx=5, pady=5)

        visualframe = tk.Frame(notebook)
        nrow = 0
        gui_things.Label(visualframe, text='color of markers', hint='the sequence of colors in graphs', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)

        palette_of_colors = tk.Frame(visualframe)
        color01 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color01'), size='small', hint_destination=M.hintlabel)
        color01.grid(row=0, column=0)
        color02 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color02'), size='small', hint_destination=M.hintlabel)
        color02.grid(row=0, column=1)
        color03 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color03'), size='small', hint_destination=M.hintlabel)
        color03.grid(row=0, column=2)
        color04 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color04'), size='small', hint_destination=M.hintlabel)
        color04.grid(row=0, column=3)
        color05 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color05'), size='small', hint_destination=M.hintlabel)
        color05.grid(row=0, column=4)
        color06 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color06'), size='small', hint_destination=M.hintlabel)
        color06.grid(row=0, column=5)
        color07 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color07'), size='small', hint_destination=M.hintlabel)
        color07.grid(row=1, column=0)
        color08 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color08'), size='small', hint_destination=M.hintlabel)
        color08.grid(row=1, column=1)
        color09 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color09'), size='small', hint_destination=M.hintlabel)
        color09.grid(row=1, column=2)
        color10 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color10'), size='small', hint_destination=M.hintlabel)
        color10.grid(row=1, column=3)
        color11 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color11'), size='small', hint_destination=M.hintlabel)
        color11.grid(row=1, column=4)
        color12 = gui_things.ColorButton(palette_of_colors, default_color=M.settings.get('color12'), size='small', hint_destination=M.hintlabel)
        color12.grid(row=1, column=5)

        palette_of_colors.grid(row=nrow, column=1, sticky=tk.E)
        nrow += 1
        gui_things.Label(visualframe, text='color palette', hint='define the color palette for PeriodicTable views', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_color_palette = gui_things.Combobox(visualframe, width=15, state='readonly')
        variable_color_palette.grid(row=nrow, column=1, sticky=tk.E)
        variable_color_palette['values'] = ('Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'viridis', 'plasma', 'cividis', 'tab20b')
        variable_color_palette.set(M.settings.get('color palette'))
        nrow += 1
        gui_things.Label(visualframe, text='lines in peaklist window', hint='manage height of peaklist window', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_window_lines = gui_things.Slider(visualframe, label_width=4, from_=15, to=40, resolution=1, default=M.settings.get('page height'))
        variable_window_lines.grid(row=nrow, column=1, sticky=tk.E)
        nrow += 1
        gui_things.Label(visualframe, text='show graph in flux database', hint='display trend graph in flux database section', hint_destination=M.hintlabel, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_showgraph_database = gui_things.OnOffButton(visualframe, default=M.settings.get('display graph in flux database'))
        variable_showgraph_database.grid(row=nrow, column=1, sticky=tk.E)

        visualframe.pack(anchor=tk.NW, padx=5, pady=5)

        outputframe = tk.Frame(notebook)
        nrow = 0
        
        nrow += 1
        gui_things.Label(outputframe, text='link budgets', hint='set internal links among budgets in the excel output file', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_excel_internal_links = gui_things.OnOffButton(outputframe, default=M.settings.get('excel internal links'))
        variable_excel_internal_links.grid(row=nrow, column=1, sticky=tk.E)
        
        nrow += 1
        gui_things.Label(outputframe, text='lock Excel worksheet', hint='prevent modifications to the input values (password: unlock)', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_excel_ws_locks = gui_things.OnOffButton(outputframe, default=M.settings.get('excel worksheet lock'))
        variable_excel_ws_locks.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        gui_things.Label(outputframe, text='show equation models', hint='display adopted measurement models in the excel output file', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_excel_show_models = gui_things.OnOffButton(outputframe, default=M.settings.get('visible models'))
        variable_excel_show_models.grid(row=nrow, column=1, sticky=tk.E)

        nrow += 1
        gui_things.Label(outputframe, text='hide excel grid', hint='hide the worksheet grid in the excel output file', hint_destination=M.hintlabel, width=labelspace, anchor=tk.W).grid(row=nrow, column=0, sticky=tk.W)
        variable_excel_hide_grid = gui_things.OnOffButton(outputframe, default=M.settings.get('hide grid'))
        variable_excel_hide_grid.grid(row=nrow, column=1, sticky=tk.E)

        outputframe.pack(anchor=tk.NW, padx=5, pady=5)

        notebook.add(gframe, text='general  ')
        notebook.add(peak_identification, text='peak identification  ')
        notebook.add(relframe, text='Rel-INRIM  ')
        notebook.add(elaboration, text='elaboration  ')
        notebook.add(visualframe, text='visualization  ')
        notebook.add(outputframe, text='output  ')

        notebook.hide(gframe)
        notebook.hide(relframe)

        notebook.grid(row=1, column=0, columnspan=5, pady=10, sticky=tk.NSEW)

        mframe.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)

        self.settings_pairings = {'energy tolerance' : variable_energy_tolerance, 'color01' : color01, 'color02' : color02, 'color03' : color03, 'color04' : color04, 'color05' : color05, 'color06' : color06, 'color07' : color07, 'color08' : color08, 'color09' : color09, 'color10' : color10, 'color11' : color11, 'color12' : color12, 'display graph in flux database' : variable_showgraph_database, 'overwrite manual emission selection' : variable_overwrite_emission_selection, 'page height' : variable_window_lines, 'color palette' : variable_color_palette, 'calibs statistical uncertainty limit' : variable_statistics_characterization, 'standard statistical uncertainty limit' : variable_statistics_standard, 'sample statistical uncertainty limit' : variable_statistics_sample, 'count rate threshold' : count_rate_alert, 'elaborate only selected emissions' : variable_elaborate_only_selected, 'max iterations' : variable_iterations, 'excel internal links' : variable_excel_internal_links, 'excel worksheet lock' : variable_excel_ws_locks, 'merge with prior' : variable_priormerge, 'average method' : variable_averagetype, 'visible models' : variable_excel_show_models, 'hide grid' : variable_excel_hide_grid, 'check internal consistency' : check_internal_peak_consistency, 'z limit' : z_limit_variable, 'f&a correlation' : variable_fluxcorrelation}

    def check_options(self, M):
        for key, value in self.settings_pairings.items():
            M.settings.set(key, value)

    def confirm_options(self, M):
        self.check_options(M)
        M.hintlabel.configure(text='changes saved')
        M.trigger_emission_assignment = True

    def go_back(self, parent, M):
        clear_window(parent)
        M.settings.dump()
        WelcomeWindow(parent, M)


class DatabaseWindow:
    def __init__(self, parent, M):
        mframe = tk.Frame(parent)
        M.title('Databases')

        header = tk.Frame(mframe)

        logo_back_to_welcome = tk.PhotoImage(data=gui_things.PL_aback)
        B_back = gui_things.Button(header, image=logo_back_to_welcome, hint='back to main menu', hint_destination=M.hintlabel, command=lambda : self.go_back(parent, M))
        B_back.pack(side=tk.LEFT)
        B_back.image = logo_back_to_welcome

        header.grid(row=0, column=0, sticky=tk.W)

        ttk.Separator(mframe, orient="horizontal").grid(row=1, column=0, sticky=tk.EW, pady=10)

        buttons_frame = tk.Frame(mframe)

        work_frame = tk.Frame(mframe)

        clm = 0
        label_title = 'emission database'
        logo_k0data = tk.PhotoImage(data=gui_things.PL_list)
        B_k0data = gui_things.Button(buttons_frame, image=logo_k0data, hint=label_title, hint_destination=M.hintlabel, command=lambda l_title=label_title: self.go_to_k0database(work_frame, M, l_title))
        B_k0data.grid(row=0, column=clm)
        B_k0data.image = logo_k0data
        #default page
        self.go_to_k0database(work_frame, M, label_title)

        clm += 1
        ttk.Separator(buttons_frame, orient="vertical").grid(row=0, column=clm, padx=3, pady=3, sticky=tk.NS)

        clm += 1
        label_title = 'self-shielding database'
        logo_sshielding = tk.PhotoImage(data=gui_things.PL_element_red)
        B_sshielding = gui_things.Button(buttons_frame, image=logo_sshielding, hint=label_title, hint_destination=M.hintlabel, command=lambda l_title=label_title: self.go_to_selfshieldingdatabase(work_frame, M, l_title))
        B_sshielding.grid(row=0, column=clm)
        B_sshielding.image = logo_sshielding

        clm += 1
        ttk.Separator(buttons_frame, orient="vertical").grid(row=0, column=clm, padx=3, pady=3, sticky=tk.NS)

        clm += 1
        label_title = 'COI database'
        logo_coi = tk.PhotoImage(data=gui_things.PL_letter_n)
        B_coi = gui_things.Button(buttons_frame, image=logo_coi, hint=label_title, hint_destination=M.hintlabel, command=lambda l_title=label_title: self.go_to_coidatabase(work_frame, M, l_title))
        B_coi.grid(row=0, column=clm)
        B_coi.image = logo_coi

        clm += 1
        ttk.Separator(buttons_frame, orient="vertical").grid(row=0, column=clm, padx=3, pady=3, sticky=tk.NS)

        clm += 1
        label_title = 'material database'
        logo_material = tk.PhotoImage(data=gui_things.PL_flasks)
        B_material = gui_things.Button(buttons_frame, image=logo_material, hint=label_title, hint_destination=M.hintlabel, command=lambda l_title=label_title: self.go_to_materialdatabase(work_frame, M, l_title))
        B_material.grid(row=0, column=clm)
        B_material.image = logo_material

        clm += 1
        ttk.Separator(buttons_frame, orient="vertical").grid(row=0, column=clm, padx=3, pady=3, sticky=tk.NS)

        clm += 1
        label_title = 'gamma source database'
        logo_source = tk.PhotoImage(data=gui_things.PL_letter_gamma)
        B_source = gui_things.Button(buttons_frame, image=logo_source, hint=label_title, hint_destination=M.hintlabel, command=lambda l_title=label_title: self.go_to_sourcesdatabase(work_frame, M, l_title))
        B_source.grid(row=0, column=clm)
        B_source.image = logo_source

        clm += 1
        ttk.Separator(buttons_frame, orient="vertical").grid(row=0, column=clm, padx=3, pady=3, sticky=tk.NS)

        clm += 1
        label_title = 'detector database'
        logo_detector = tk.PhotoImage(data=gui_things.PL_parabole)
        B_detector = gui_things.Button(buttons_frame, image=logo_detector, hint=label_title, hint_destination=M.hintlabel, command=lambda l_title=label_title: self.go_to_detectordatabase(work_frame, M, l_title))
        B_detector.grid(row=0, column=clm)
        B_detector.image = logo_detector

        clm += 1
        ttk.Separator(buttons_frame, orient="vertical").grid(row=0, column=clm, padx=3, pady=3, sticky=tk.NS)

        clm += 1
        label_title = 'detector characterization database'
        logo_detector_characterization = tk.PhotoImage(data=gui_things.PL_curve)
        B_detector = gui_things.Button(buttons_frame, image=logo_detector_characterization, hint=label_title, hint_destination=M.hintlabel, command=lambda l_title=label_title: self.go_to_detectorcharacterizationdatabase(work_frame, M, l_title))
        B_detector.grid(row=0, column=clm)
        B_detector.image = logo_detector_characterization

        clm += 1
        ttk.Separator(buttons_frame, orient="vertical").grid(row=0, column=clm, padx=3, pady=3, sticky=tk.NS)

        clm += 1
        label_title = 'flux measurement database'
        logo_flux = tk.PhotoImage(data=gui_things.PL_letter_phi)
        B_flux = gui_things.Button(buttons_frame, image=logo_flux, hint=label_title, hint_destination=M.hintlabel, command=lambda l_title=label_title: self.go_to_fluxesdatabase(work_frame, M, l_title))
        B_flux.grid(row=0, column=clm)
        B_flux.image = logo_flux

        buttons_frame.grid(row=2, column=0, sticky=tk.W)
        work_frame.grid(row=3, column=0, columnspan=10, sticky=tk.EW, pady=5)

        mframe.pack(anchor=tk.NW)

    def go_to_materialdatabase(self, parent, M, title):
        clear_window(parent)
        MaterialdatabaseWindow(parent, M, title)

    def go_to_sourcesdatabase(self, parent, M, title):
        clear_window(parent)
        SourcedatabaseWindow(parent, M, title)

    def go_to_detectordatabase(self, parent, M, title):
        clear_window(parent)
        DetectordatabaseWindow(parent, M, title)

    def go_to_detectorcharacterizationdatabase(self, parent, M, title):
        clear_window(parent)
        DetectorCharacterizationdatabaseWindow(parent, M, title)

    def go_to_fluxesdatabase(self, parent, M, title):
        clear_window(parent)
        NeutronFluxdatabaseWindow(parent, M, title)

    def go_to_k0database(self, parent, M, title):
        clear_window(parent)
        k0databaseWindow(parent, M, title)

    def go_to_selfshieldingdatabase(self, parent, M, title):
        clear_window(parent)
        SelfShieldingdatabaseWindow(parent, M, title)

    def go_to_coidatabase(self, parent, M, title):
        clear_window(parent)
        COIdatabaseWindow(parent, M, title)

    def go_back(self, parent, M):
        clear_window(parent)
        WelcomeWindow(parent, M)


class SelfShieldingdatabaseWindow:
    def __init__(self, parent, M, title):
        self.shieldshow_window = None
        m_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=title), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='currently available shielding databases', anchor=tk.W).pack(anchor=tk.W)

        ssdatabase_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'chemical_data')) if filename.lower().endswith('.mmd')]

        self.SS_LB = gui_things.ScrollableListbox(m_frame, width=45, height=15, data=ssdatabase_list)
        self.SS_LB.pack(expand=True, fill=tk.X)

        f_buttons = tk.Frame(m_frame)

        logo_showss = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_showss = gui_things.Button(f_buttons, image=logo_showss, hint='display data for the selected shielding database', hint_destination=M.hintlabel, command=lambda : self.see_ss(m_frame, M))
        B_showss.pack(side=tk.LEFT)
        B_showss.image = logo_showss

        f_buttons.pack(anchor=tk.W)

        m_frame.pack(padx=5, pady=5)

    def see_ss(self, parent, M):
        if self.SS_LB.get_selection() is not None:
            if self.shieldshow_window is not None:
                try:
                    self.shieldshow_window.destroy()
                except:
                    pass
            self.shieldshow_window = tk.Toplevel(parent)
            self.shieldshow_window.resizable(False, False)
            self.shieldshow_window.title(f'Show: {self.SS_LB.get_selection()}')
            SS_database = naaobject._call_database(self.SS_LB.get_selection(), 'chemical_data', 'mmd')
            general_frame = tk.Frame(self.shieldshow_window)
            tk.Label(general_frame, text=f'name: {self.SS_LB.get_selection()}', width=70, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(general_frame, text=f'entries: {len(SS_database)}', anchor=tk.W).pack(anchor=tk.W)

            general_frame.pack(anchor=tk.NW, pady=6)
            data_frame = tk.Frame(self.shieldshow_window)

            ssprint = SS_database.to_string(columns=['element', 'A', 'abundance', 'scatt', 'absorption', 'resonance', 'Gamma_ratio'], index=False, header=['element', 'A', 'abu. / 1', 'scatt / cm²', 'abs / cm²', 'res / cm²', 'y ratio / 1'], formatters={'A':"{:.0f}".format, 'abundance':"{:.4f}".format, 'scatt':"{:.2e}".format, 'absorption':"{:.2e}".format, 'resonance':"{:.2e}".format, 'Gamma_ratio':"{:.4f}".format}, col_space={'element':5, 'A':5, 'abundance':9, 'scatt':12, 'absorption':12, 'resonance':12, 'Gamma_ratio':12}, justify='right', na_rep='')

            limit_cut = ssprint.find('\n')
            if limit_cut > -1:
                ssprint_header = ssprint[:limit_cut]
                ssprint = ssprint[limit_cut+1:]

            tk.Label(data_frame, text=ssprint_header, anchor=tk.W, font=('Courier', 10)).pack(anchor=tk.W)

            stext = gui_things.ScrollableText(data_frame, width=78, data=ssprint, height=32, font=('Courier', 10))
            stext.pack(anchor=tk.W)

            data_frame.pack(anchor=tk.NW)

        else:
            M.hintlabel.configure(text='no database selected')

    
class COIdatabaseWindow:
    def __init__(self, parent, M, title):
        self.coishow_window = None
        m_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=title), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='currently available coincidence databases', anchor=tk.W).pack(anchor=tk.W)

        coidatabase_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'coincidences')) if filename.lower().endswith('.coi')]

        self.coi_LB = gui_things.ScrollableListbox(m_frame, width=45, height=15, data=coidatabase_list)
        self.coi_LB.pack(expand=True, fill=tk.X)

        f_buttons = tk.Frame(m_frame)

        logo_showcoi = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_showcoi = gui_things.Button(f_buttons, image=logo_showcoi, hint='display data for the selected shielding database', hint_destination=M.hintlabel, command=lambda : self.see_coi(m_frame, M))
        B_showcoi.pack(side=tk.LEFT)
        B_showcoi.image = logo_showcoi

        f_buttons.pack(anchor=tk.W)

        m_frame.pack(padx=5, pady=5)

    def see_coi(self, parent, M):

        def condensed_type(type_line):
            splits = type_line.split(' : ')
            if len(splits) == 1 and splits[0] == '':
                return 'no coincidences'
            splits = [split for split in splits if '*' not in split]
            _sums = [split for split in splits if 'X=' in split]
            if len(_sums) > 0:
                sums = f'sum : {len(_sums)}'
            else:
                sums = ''
            _lenloss = len(splits) - len(_sums)
            if _lenloss > 0:
                loss = f'loss : {_lenloss}'
            else:
                loss = ''
            if loss != '' and sums != '':
                conj = ' & '
            else:
                conj = ''
            condensed_line = f'{loss}{conj}{sums}'
            return condensed_line

        if self.coi_LB.get_selection() is not None:
            if self.coishow_window is not None:
                try:
                    self.coishow_window.destroy()
                except:
                    pass
            self.coishow_window = tk.Toplevel(parent)
            self.coishow_window.resizable(False, False)
            self.coishow_window.title(f'Show: {self.coi_LB.get_selection()}')
            COI_database = naaobject._call_database(self.coi_LB.get_selection(), 'coincidences', 'coi')
            general_frame = tk.Frame(self.coishow_window)
            tk.Label(general_frame, text=f'name: {self.coi_LB.get_selection()}', width=70, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(general_frame, text=f'entries: {len(COI_database)}', anchor=tk.W).pack(anchor=tk.W)

            general_frame.pack(anchor=tk.NW, pady=6)
            data_frame = tk.Frame(self.coishow_window)

            COI_database['r_type'] = [condensed_type(line) for line in COI_database['type']]

            coiprint = COI_database.to_string(columns=['target', 'emitter', 'E', 'line', 'a', 'c', 'g', 'r_type'], index=False, header=['target', 'emitter', 'E / keV', 'line', 'a / 1', 'c / 1', 'g / 1', 'coincidence type'], formatters={'E':"{:.1f}".format, 'a':"{:.3f}".format, 'c':"{:.3f}".format, 'g':"{:.4f}".format}, col_space={'target':5, 'emitter':9, 'E':9, 'line':5, 'a':8, 'c':8, 'g':8, 'r_type':25}, justify='right')

            limit_cut = coiprint.find('\n')
            if limit_cut > -1:
                coiprint_header = coiprint[:limit_cut]
                coiprint = coiprint[limit_cut+1:]

            tk.Label(data_frame, text=coiprint_header, anchor=tk.W, font=('Courier', 10)).pack(anchor=tk.W)

            stext = gui_things.ScrollableText(data_frame, width=85, data=coiprint, height=32, font=('Courier', 10))
            stext.pack(anchor=tk.W)

            data_frame.pack(anchor=tk.NW)

        else:
            M.hintlabel.configure(text='no database selected')


class NeutronFluxdatabaseWindow:
    def __init__(self, parent, M, title):
        self.facilitydisplay_window = None
        m_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=title), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='currently available facilities', anchor=tk.W).pack(anchor=tk.W)

        self.ch_data = naaobject._call_database('channels', 'facilities', 'chs')
        self.ch_list = sorted(set(self.ch_data['channel_name']))

        self.facility_LB = gui_things.ScrollableListbox(m_frame, width=45, height=15, data=self.ch_list)
        self.facility_LB.pack(expand=True, fill=tk.X)

        f_buttons = tk.Frame(m_frame)
        logo_displayfacility = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_displayfacility = gui_things.Button(f_buttons, image=logo_displayfacility, hint='display facility information', hint_destination=M.hintlabel, command=lambda : self.display_facility(m_frame, M))
        B_displayfacility.pack(side=tk.LEFT)
        B_displayfacility.image = logo_displayfacility

        logo_deletefacility = tk.PhotoImage(data=gui_things.PL_none)
        B_deletefacility = gui_things.Button(f_buttons, image=logo_deletefacility, hint='delete selected facility', hint_destination=M.hintlabel, command=lambda : self.delete_facility_data(m_frame, M))
        B_deletefacility.pack(side=tk.LEFT)
        B_deletefacility.image = logo_deletefacility
        f_buttons.pack(anchor=tk.W)

        m_frame.pack(padx=5, pady=5)

    def delete_facility_data(self, parent, M):
        facilityname = self.facility_LB.get_selection()

        if self.facilitydisplay_window is not None:
            try:
                self.facilitydisplay_window.destroy()
            except:
                pass

        if facilityname is not None:
            if messagebox.askyesno(title='Delete facility data', message=f'\nAre you sure to delete all data\nrelated to {facilityname} facility?\n', parent=parent):
                to_delete = self.ch_data['channel_name'] == facilityname
                self.ch_data = self.ch_data.loc[~to_delete]
                naaobject._save_facility_database(self.ch_data)
                self.ch_list = sorted(set(list(self.ch_data['channel_name'])))
                self.facility_LB._update(self.ch_list)
        else:
            M.hintlabel.configure(text='no facility is selected')

    def _facility_as_text_display(self, data, spaces=[15,8,12,12,10,10,10,10]):

        def text_cut(text,limit):
            if len(text) > limit - 1:
                return (text[:limit-3]+'..').ljust(limit," ")
            else:
                return text.ljust(limit," ")

        return [f'{text_cut(idx,spaces[0])}{format(pos,".1f").ljust(spaces[1])}{mtime.strftime("%d/%m/%Y").rjust(spaces[2]," ")}{dtime.strftime("%d/%m/%Y").rjust(spaces[3]," ")}{format(ff,".2f").rjust(spaces[4]," ")}{format(aa,".5f").rjust(spaces[5]," ")}{format(thermal,".2e").rjust(spaces[6]," ")}{format(fast,".2e").rjust(spaces[7]," ")}' for idx, pos, mtime, dtime, ff, aa, thermal, fast in zip(data['channel_name'], data['pos'], data['m_datetime'], data['datetime'], data['f_value'], data['a_value'], data['thermal_flux'], data['fast_flux'])]

    def display_facility(self, parent, M):

        if self.facility_LB.get_selection() is not None:
            self.f_index = self.facility_LB.get_selection()

            if self.facilitydisplay_window is not None:
                try:
                    self.facilitydisplay_window.destroy()
                except:
                    pass

            self.facilitydisplay_window = tk.Toplevel(parent)
            title = f'Display facility information ({self.f_index})'
            self.facilitydisplay_window.title(title)
            self.facilitydisplay_window.resizable(False, False)

            self.hintlabel = tk.Label(self.facilitydisplay_window, text='', anchor=tk.W)

            data_frame = tk.Frame(self.facilitydisplay_window)

            spaces = [15,8,12,12,10,10,10,10]
            header=['channel','position','meas date','eval date','f / 1', 'α / 1','thermal', 'fast']
            tk.Label(data_frame, text=f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}{header[3].rjust(spaces[3]," ")}{header[4].rjust(spaces[4]," ")}{header[5].rjust(spaces[5]," ")}{header[6].rjust(spaces[6]," ")}{header[7].rjust(spaces[7]," ")}', anchor=tk.W, font=('Courier', 10)).pack(anchor=tk.W)

            if M.settings.get('display graph in flux database'):
                height = 15
            else:
                height = 25

            self.selected_facility_LB = gui_things.ScrollableListbox(data_frame, width=90, height=height, data=self._facility_as_text_display(self.ch_data[self.ch_data['channel_name'] == self.f_index]), font=('Courier', 10))
            self.selected_facility_LB.pack(anchor=tk.NW)

            data_frame.pack(anchor=tk.NW, padx=5, pady=5)
            
            button_frame = tk.Frame(self.facilitydisplay_window)

            logo_deletemeasuremententry = tk.PhotoImage(data=gui_things.PL_none)
            B_deletemeasuremententry = gui_things.Button(button_frame, image=logo_deletemeasuremententry, hint='delete selected entry', hint_destination=self.hintlabel, command=lambda : self.delete_selected_entry_data(self.facilitydisplay_window, M))
            B_deletemeasuremententry.pack(side=tk.LEFT)
            B_deletemeasuremententry.image = logo_deletemeasuremententry

            if M.settings.get('display graph in flux database'):
                ttk.Separator(button_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=3)
                tk.Label(button_frame, text='plot', width=5).pack(side=tk.LEFT)
                self.selector = gui_things.Combobox(button_frame, width=10, state='readonly')
                self.selector.pack(side=tk.LEFT)
                self.selector['values'] = ['f', 'α', 'thermal', 'epithermal', 'fast', 'f & α', 'th & epi']
                self.selector.set(self.selector['values'][0])

            button_frame.pack(anchor=tk.NW, padx=5)

            if M.settings.get('display graph in flux database'):

                graph_frame = tk.Frame(self.facilitydisplay_window)
                self.fig = Figure(figsize=(7, 2.5), dpi=100)

                Figur = tk.Frame(graph_frame)
                Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
                self.canvas = FigureCanvasTkAgg(self.fig, master=Figur)
                self.fig.patch.set_alpha(0.0)
                #self.canvas.draw()
                self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                self.fig.patch.set_alpha(0.0)
                self.canvas.get_tk_widget().configure(background=self.facilitydisplay_window.cget('bg'))
                self.canvas.draw()
                self.plot_facility_data(M)
                graph_frame.pack(anchor=tk.NW, padx=5, pady=5, fill=tk.X, expand=True)

                self.selector.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.plot_facility_data(M))

            self.hintlabel.pack(anchor=tk.NW)

    def delete_selected_entry_data(self, parent, M):
        facilityindex = self.selected_facility_LB.curselection()
        try:
            facilityindex = facilityindex[0]
        except IndexError:
            facilityindex = None

        if facilityindex is not None:
            if messagebox.askyesno(title='Delete facility data', message=f'\nAre you sure to delete the selected entry?\n', parent=parent):
                sub_section = self.ch_data[self.ch_data['channel_name'] == self.f_index]
                how_many_data = len(sub_section)
                to_delete = self.ch_data.iterrows == sub_section.iloc[facilityindex]
                to_delete = to_delete.name

                if how_many_data == 1:
                    self.ch_data.drop(to_delete, inplace=True)
                    naaobject._save_facility_database(self.ch_data)
                    parent.destroy()
                    self.ch_list = sorted(set(list(self.ch_data['channel_name'])))
                    self.facility_LB._update(self.ch_list)

                else:
                    self.ch_data.drop(to_delete, inplace=True)
                    naaobject._save_facility_database(self.ch_data)
                    self.selected_facility_LB._update(self._facility_as_text_display(self.ch_data[self.ch_data['channel_name'] == self.f_index]))
                    if M.settings.get('display graph in flux database'):
                        self.plot_facility_data(M)
        else:
            self.hintlabel.configure(text='no entry is selected')

    def plot_facility_data(self, M):
        data = self.ch_data[self.ch_data['channel_name'] == self.f_index]

        mainoptions = {'linestyle' : '', 'marker' : 'o', 'markersize' : 3, 'markerfacecolor' : M.settings.get('color01'), 'color' : 'k', 'elinewidth' : 0.75}
        secoptions = {'linestyle' : '', 'marker' : 's', 'markersize' : 3, 'markerfacecolor': M.settings.get('color02'), 'color' : 'k', 'elinewidth' : 0.75, 'capsize' : 5}
        gridoptions = {'axis' : 'y', 'linestyle' : '-.', 'linewidth' : '0.5'}
        gridoptions2 = {'axis' : 'y', 'linestyle' : '-', 'linewidth' : '0.4'}
        mlabel = 'irradiation date'

        self.fig.clear()
        if self.selector.get() == 'f':
            axes_LEFT = self.fig.add_subplot(111)
            axes_LEFT.ticklabel_format(useMathText=True)
            x = data['datetime']
            y = data['f_value']
            uy = data['unc_f_value']
            axes_LEFT.errorbar(x, y, yerr=[2*uy, 2*uy], **mainoptions)
            axes_LEFT.grid(**gridoptions)
            axes_LEFT.set_ylabel(r'$f$ / 1')
            axes_LEFT.set_xlabel(mlabel)

        elif self.selector.get() == 'α':
            axes_LEFT = self.fig.add_subplot(111)
            axes_LEFT.ticklabel_format(useMathText=True)
            x = data['datetime']
            y = data['a_value']
            uy = data['unc_a_value']
            axes_LEFT.errorbar(x, y, yerr=[2*uy, 2*uy], **mainoptions)
            axes_LEFT.grid(**gridoptions)
            axes_LEFT.set_ylabel(r'$\alpha$ / 1')
            axes_LEFT.set_xlabel(mlabel)

        elif self.selector.get() == 'thermal':
            axes_LEFT = self.fig.add_subplot(111)
            axes_LEFT.ticklabel_format(useMathText=True)
            x = data['datetime']
            y = data['thermal_flux']
            uy = data['unc_thermal_flux']
            y = np.array([yi if yi>0 else np.nan for yi in y])
            uy = np.array([uyi if uyi>0 else np.nan for uyi in uy])
            axes_LEFT.errorbar(x, y, yerr=[2*uy, 2*uy], **mainoptions)
            axes_LEFT.grid(**gridoptions)
            axes_LEFT.set_ylabel(r'$\Phi_{\mathrm{thermal}}$ / cm$^{-2}$ s$^{-1}$')
            axes_LEFT.set_xlabel(mlabel)

        elif self.selector.get() == 'epithermal':
            axes_LEFT = self.fig.add_subplot(111)
            axes_LEFT.ticklabel_format(useMathText=True)
            x = data['datetime']
            y = data['epithermal_flux']
            uy = data['unc_epithermal_flux']
            y = np.array([yi if yi>0 else np.nan for yi in y])
            uy = np.array([uyi if uyi>0 else np.nan for uyi in uy])
            axes_LEFT.errorbar(x, y, yerr=[2*uy, 2*uy], **mainoptions)
            axes_LEFT.grid(**gridoptions)
            axes_LEFT.set_ylabel(r'$\Phi_{\mathrm{epithermal}}$ / cm$^{-2}$ s$^{-1}$')
            axes_LEFT.set_xlabel(mlabel)

        elif self.selector.get() == 'fast':
            axes_LEFT = self.fig.add_subplot(111)
            axes_LEFT.ticklabel_format(useMathText=True)
            x = data['datetime']
            y = data['fast_flux']
            uy = data['unc_fast_flux']
            y = np.array([yi if yi>0 else np.nan for yi in y])
            uy = np.array([uyi if uyi>0 else np.nan for uyi in uy])
            axes_LEFT.errorbar(x, y, yerr=[2*uy, 2*uy], **mainoptions)
            axes_LEFT.grid(**gridoptions)
            axes_LEFT.set_ylabel(r'$\Phi_{\mathrm{fast}}$ / cm$^{-2}$ s$^{-1}$')
            axes_LEFT.set_xlabel(mlabel)

        elif self.selector.get() == 'f & α':
            axes_LEFT = self.fig.add_subplot(111)
            axes_LEFT.ticklabel_format(useMathText=True)
            axes_RIGHT = axes_LEFT.twinx()
            axes_RIGHT.ticklabel_format(useMathText=True)
            x = data['datetime']
            y = data['f_value']
            uy = data['unc_f_value']
            axes_LEFT.errorbar(x, y, yerr=[2*uy, 2*uy], **mainoptions, label=r'$f$')

            y = data['a_value']
            uy = data['unc_a_value']
            axes_RIGHT.errorbar(x, y, yerr=[2*uy, 2*uy], **secoptions, label=r'$\alpha$')
            axes_LEFT.grid(**gridoptions)
            axes_LEFT.set_ylabel(r'$f$ / 1')
            axes_LEFT.set_xlabel(mlabel)
            axes_RIGHT.grid(**gridoptions2)
            axes_RIGHT.set_ylabel(r'$\alpha$ / 1')
            self.fig.legend(loc='lower left')

        elif self.selector.get() == 'th & epi':
            axes_LEFT = self.fig.add_subplot(111)
            axes_LEFT.ticklabel_format(useMathText=True)
            axes_RIGHT = axes_LEFT.twinx()
            axes_RIGHT.ticklabel_format(useMathText=True)
            x = data['datetime']
            y = data['thermal_flux']
            uy = data['unc_thermal_flux']
            y = np.array([yi if yi>0 else np.nan for yi in y])
            uy = np.array([uyi if uyi>0 else np.nan for uyi in uy])
            axes_LEFT.errorbar(x, y, yerr=[2*uy, 2*uy], **mainoptions, label=r'$\Phi_{\mathrm{th}}$')

            y = data['epithermal_flux']
            uy = data['unc_epithermal_flux']
            y = np.array([yi if yi>0 else np.nan for yi in y])
            uy = np.array([uyi if uyi>0 else np.nan for uyi in uy])
            axes_RIGHT.errorbar(x, y, yerr=[2*uy, 2*uy], **secoptions, label=r'$\Phi_{\mathrm{epi}}$')
            axes_LEFT.grid(**gridoptions)
            axes_LEFT.set_ylabel(r'$\Phi_{\mathrm{thermal}}$ / cm$^{-2}$ s$^{-1}$')
            axes_LEFT.set_xlabel(mlabel)
            axes_RIGHT.grid(**gridoptions2)
            axes_RIGHT.set_ylabel(r'$\Phi_{\mathrm{epithermal}}$ / cm$^{-2}$ s$^{-1}$')
            self.fig.legend(loc='lower left')
            
        self.fig.tight_layout()
        self.canvas.draw()


class DetectorCharacterizationdatabaseWindow:
    def __init__(self, parent, M, title):
        self.detectorcharacterizationmodify_window = None
        self.peaklist_window = None
        m_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=title), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='currently available detector characterizations', anchor=tk.W).pack(anchor=tk.W)

        detector_characterization_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'characterizations')) if filename.lower().endswith('.dcr')]

        self.detector_chr_LB = gui_things.ScrollableListbox(m_frame, width=45, height=15, data=detector_characterization_list)
        self.detector_chr_LB.pack(expand=True, fill=tk.X)

        f_buttons = tk.Frame(m_frame)

        logo_adddetector_characterization = tk.PhotoImage(data=gui_things.PL_plussign)
        B_adddetector_characterization = gui_things.Button(f_buttons, image=logo_adddetector_characterization, hint='add a new detector characterization', hint_destination=M.hintlabel, command=lambda : self.add_detector_characterization(m_frame, M))
        B_adddetector_characterization.pack(side=tk.LEFT)
        B_adddetector_characterization.image = logo_adddetector_characterization

        logo_modifydetector_characterization = tk.PhotoImage(data=gui_things.PL_ggear)
        B_modifydetector_characterization = gui_things.Button(f_buttons, image=logo_modifydetector_characterization, hint='modify detector characterization', hint_destination=M.hintlabel, command=lambda : self.modify_detector_characterization(m_frame, M))
        B_modifydetector_characterization.pack(side=tk.LEFT)
        B_modifydetector_characterization.image = logo_modifydetector_characterization

        logo_deletedetector_characterization = tk.PhotoImage(data=gui_things.PL_none)
        B_deletedetector_characterization = gui_things.Button(f_buttons, image=logo_deletedetector_characterization, hint='delete detector characterization', hint_destination=M.hintlabel, command=lambda : self.delete_detector_characterization(m_frame, M))
        B_deletedetector_characterization.pack(side=tk.LEFT)
        B_deletedetector_characterization.image = logo_deletedetector_characterization
        
        f_buttons.pack(anchor=tk.W)

        m_frame.pack(padx=5, pady=5)

    def delete_detector_characterization(self, parent, M):
        detname = self.detector_chr_LB.get_selection()

        if self.detectorcharacterizationmodify_window is not None:
            try:
                self.detectorcharacterizationmodify_window.destroy()
            except:
                pass

        if detname is not None:
            if messagebox.askyesno(title='Delete detector characterization', message=f'\nAre you sure to delete characterization {detname}?\n', parent=parent):
                os.remove(os.path.join(os.path.join('data', 'characterizations'),f'{detname}.dcr'))

                detector_characterization_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'characterizations')) if filename.lower().endswith('.dcr')]
                self.detector_chr_LB._update(detector_characterization_list)
                M.hintlabel.configure(text=f'detector {detname} deleted')
        else:
            M.hintlabel.configure(text='no detector characterization is selected')

    def add_detector_characterization(self, parent, M):
        if self.detectorcharacterizationmodify_window is not None:
            try:
                self.detectorcharacterizationmodify_window.destroy()
            except:
                pass
        self.detectcharactmodification_form(parent, M)

    def modify_detector_characterization(self, parent, M):
        filename = self.detector_chr_LB.get_selection()
        if filename is not None:
            if self.detectorcharacterizationmodify_window is not None:
                try:
                    self.detectorcharacterizationmodify_window.destroy()
                except:
                    pass
            self.detectcharactmodification_form(parent, M, naaobject._call_database(filename, 'characterizations', 'dcr'))
        else:
            M.hintlabel.configure(text='no detector characterization is selected')

    def detectcharactmodification_form(self, parent, M, characterization=None):
        self.detectorcharacterizationmodify_window = tk.Toplevel(parent)
        if characterization is not None:
            title = f'Display existing characterization ({characterization.name})'
            filename = characterization.name
        else:
            title = f'New detector characterization'
            filename = title
        self.detectorcharacterizationmodify_window.title(title)
        self.detectorcharacterizationmodify_window.resizable(False, False)

        self.emissionselectionwindow = None

        if characterization is not None:
            self.temporary_detector = characterization.detector
            self.temporary_source = characterization.source
            self.temporary_positions = characterization.positions
            self.temporary_background = characterization.background
        else:
            self.temporary_detector = None
            self.temporary_source = None
            self.temporary_positions = {'reference' : NominalCountingPosition('reference')}
            self.temporary_background = None
        self.characterization_results = {}

        hintlabel = tk.Label(self.detectorcharacterizationmodify_window, text='', anchor=tk.W)

        info_frame = tk.LabelFrame(self.detectorcharacterizationmodify_window, labelwidget=tk.Label(self.detectorcharacterizationmodify_window, text='information'), relief='solid', bd=2, padx=4, pady=4)

        tk.Label(info_frame, text='name', anchor=tk.W, width=15).grid(row=0, column=0, sticky=tk.W)
        tk.Label(info_frame, text='detector', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
        tk.Frame(info_frame).grid(row=0, column=3, padx=10)
        tk.Label(info_frame, text='source', anchor=tk.W).grid(row=1, column=4, sticky=tk.W)

        self.char_name_E = gui_things.LockedEntry(info_frame, default_value=filename, width=30, hint='', hint_destination=hintlabel)
        self.char_name_E.grid(row=0, column=1, padx=5)
        logo_newcharacterization_name = tk.PhotoImage(data=gui_things.PL_name)
        B_new_characterization = gui_things.Button(info_frame, image=logo_newcharacterization_name, hint='modify characterization name', hint_destination=hintlabel)
        B_new_characterization.grid(row=0, column=2)
        B_new_characterization.image = logo_newcharacterization_name

        B_new_characterization.configure(command=lambda : self.char_name_E.change_value())

        self.detector_name_E = gui_things.Combobox(info_frame, width=25, state='readonly', hint_destination=hintlabel)
        self.detector_name_E.grid(row=1, column=1, padx=5)
        self.detector_name_E['values'] = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'detectors')) if filename.lower().endswith('.dec')]
        if self.temporary_detector is not None:
            self.detector_name_E.set(self.temporary_detector.name)
        else:
            self.detector_name_E.set('')
        logo_visualizedetector = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_visualizedetector = gui_things.Button(info_frame, image=logo_visualizedetector, hint='display detector features', hint_destination=hintlabel, command=lambda : self.visualize_dec(parent))
        B_visualizedetector.grid(row=1, column=2)
        B_visualizedetector.image = logo_visualizedetector

        self.gsource_name_E = gui_things.Combobox(info_frame, width=25, state='readonly', hint_destination=hintlabel)
        self.gsource_name_E.grid(row=1, column=5, padx=5)
        self.gsource_name_E['values'] = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'sources')) if filename.lower().endswith('.sce')]
        if self.temporary_source is not None:
            self.gsource_name_E.set(self.temporary_source.name)
        else:
            self.gsource_name_E.set('')

        logo_sourceselector = tk.PhotoImage(data=gui_things.PL_ggear)
        B_sourceselector = gui_things.Button(info_frame, image=logo_sourceselector, hint='select emissions from source', hint_destination=hintlabel, command=lambda : self.select_sourceemissions(self.detectorcharacterizationmodify_window))
        B_sourceselector.grid(row=1, column=6)
        B_sourceselector.image = logo_sourceselector

        BKG_F = tk.Frame(info_frame)

        logo_backgroundselector = tk.PhotoImage(data=gui_things.PL_pluspeak)
        B_backgroundselector = gui_things.Button(BKG_F, image=logo_backgroundselector, hint='select background spectrum', hint_destination=hintlabel)
        B_backgroundselector.pack(side=tk.LEFT, anchor=tk.W)
        B_backgroundselector.image = logo_backgroundselector

        self.label_background_name = tk.Label(BKG_F, text='', anchor=tk.W, width=40)
        self.label_background_name.pack(side=tk.LEFT, padx=3)
        if self.temporary_background is not None:
            self.label_background_name.configure(text=self.temporary_background.filename())

        B_backgroundselector.configure(command=lambda : self.select_background(self.detectorcharacterizationmodify_window))

        BKG_F.grid(row=2, column=0, columnspan=3, sticky=tk.W)

        info_frame.pack(anchor=tk.NW, padx=5, pady=5)

        positions_frame = tk.LabelFrame(self.detectorcharacterizationmodify_window, labelwidget=tk.Label(self.detectorcharacterizationmodify_window, text='nominal counting positions'), relief='solid', bd=2, padx=4, pady=4)

        tk.Label(positions_frame, text='counting position', anchor=tk.W, width=20).grid(row=0, column=0, sticky=tk.W)

        self.positions_CB = gui_things.Combobox(positions_frame, width=20, state='readonly')
        self.positions_CB.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5)
        self.positions_CB['values'] = list(self.temporary_positions.keys())

        tk.Frame(positions_frame).grid(row=0, column=3, padx=10)
        tk.Label(positions_frame, text='nominal distance / mm', anchor=tk.W, width=20).grid(row=1, column=0, sticky=tk.W)
        self.nominaldistance_E = gui_things.LockedNumEntry(positions_frame, width=13, hint='distance of the gamma source from detector end-cap', hint_destination=hintlabel)
        self.nominaldistance_E.grid(row=1, column=1, sticky=tk.W)

        logo_changedistance = tk.PhotoImage(data=gui_things.PL_meter)
        B_changedistance = gui_things.Button(positions_frame, image=logo_changedistance, hint='change nominal distance', hint_destination=hintlabel, command=lambda : self.nominaldistance_E.change_value())
        B_changedistance.grid(row=1, column=2, padx=2)
        B_changedistance.image = logo_changedistance

        tk.Label(positions_frame, text='spectra list', anchor=tk.W).grid(row=2, column=0, sticky=tk.NW)

        self.spectra_LB = gui_things.ScrollableListbox(positions_frame, width=45, height=10)
        self.spectra_LB.grid(row=3, column=0, columnspan=3, sticky=tk.NW)


        buttons_frame = tk.Frame(positions_frame)

        logo_addposition = tk.PhotoImage(data=gui_things.PL_plussign)
        B_addposition = gui_things.Button(buttons_frame, image=logo_addposition, hint='add a new nominal position', hint_destination=hintlabel, command=lambda : self.add_position())
        B_addposition.pack(side=tk.LEFT)
        B_addposition.image = logo_addposition

        logo_renameposition = tk.PhotoImage(data=gui_things.PL_name)
        B_renameposition = gui_things.Button(buttons_frame, image=logo_renameposition, hint='rename current nominal position', hint_destination=hintlabel, command=lambda : self.rename_position(hintlabel))
        B_renameposition.pack(side=tk.LEFT)
        B_renameposition.image = logo_renameposition

        logo_deleteposition = tk.PhotoImage(data=gui_things.PL_none)
        B_deleteposition = gui_things.Button(buttons_frame, image=logo_deleteposition, hint='delete current nominal position', hint_destination=hintlabel, command=lambda : self.delete_position(self.detectorcharacterizationmodify_window))
        B_deleteposition.pack(side=tk.LEFT)
        B_deleteposition.image = logo_deleteposition

        ttk.Separator(buttons_frame, orient="vertical").pack(side=tk.LEFT, padx=3, pady=3, fill=tk.Y, expand=True)

        logo_addspectra = tk.PhotoImage(data=gui_things.PL_pluspeak)
        B_addspectra = gui_things.Button(buttons_frame, image=logo_addspectra, hint='add spectra to current nominal position', hint_destination=hintlabel, command=lambda : self.go_to_opencharacterizationspectra(M))
        B_addspectra.pack(side=tk.LEFT)
        B_addspectra.image = logo_addspectra

        logo_openspectrum = tk.PhotoImage(data=gui_things.PL_peak_list)
        B_openspectrum = gui_things.Button(buttons_frame, image=logo_openspectrum, hint='display peaklist for selected spectrum', hint_destination=hintlabel, command=lambda : self.characterization_peaklist(M))
        B_openspectrum.pack(side=tk.LEFT)
        B_openspectrum.image = logo_openspectrum

        logo_deletespectrum = tk.PhotoImage(data=gui_things.PL_none)
        B_deletespectrum = gui_things.Button(buttons_frame, image=logo_deletespectrum, hint='delete selected spectrum', hint_destination=hintlabel, command=lambda : None)
        B_deletespectrum.pack(side=tk.LEFT)
        B_deletespectrum.image = logo_deletespectrum

        ttk.Separator(buttons_frame, orient="vertical").pack(side=tk.LEFT, padx=3, pady=3, fill=tk.Y, expand=True)

        self.plot_CB = gui_things.Combobox(buttons_frame, width=25, state='readonly')
        self.plot_CB.pack(side=tk.LEFT)

        logo_seeinfos = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_seeinfos = gui_things.Button(buttons_frame, image=logo_seeinfos, hint='display fit information', hint_destination=hintlabel, command=lambda : self._display_fit_information())
        B_seeinfos.pack(side=tk.LEFT, padx=3)
        B_seeinfos.image = logo_seeinfos

        buttons_frame.grid(row=0, column=4, sticky=tk.NW)

        tk.Label(positions_frame, text='uncertainty on nominal positions / mm', anchor=tk.W, width=35).grid(row=20, column=0, columnspan=2, sticky=tk.W)

        self.unc_nompos_SB = gui_things.Spinbox(positions_frame, from_=0.0, to=10.0, increment=0.01, width=6, hint='applies to all nominal positions', hint_destination=hintlabel)
        self.unc_nompos_SB.grid(row=20, column=2, sticky=tk.W)

        if characterization is not None:
            self.unc_nompos_SB.delete(0, tk.END)
            self.unc_nompos_SB.insert(0, f'{characterization.udistances:.2f}')

        plotdata = tk.Frame(positions_frame)

        self.SF_figure = Figure(figsize=(4.6, 2.5))
        self.SF_axes = self.SF_figure.subplots(1, 1)
        Figur = tk.Frame(plotdata)
        Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        self.SF_canvas = FigureCanvasTkAgg(self.SF_figure, master=Figur)
        self.SF_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
        self.SF_figure.patch.set_alpha(0.0)
        self.SF_canvas.get_tk_widget().configure(background=self.detectorcharacterizationmodify_window.cget('bg'))

        plotdata.grid(row=1, column=4, rowspan=4)

        other_button_frame = tk.Frame(positions_frame)

        logo_elaborate_characterization = tk.PhotoImage(data=gui_things.PL_check)
        B_elaborate_characterization = gui_things.Button(other_button_frame, image=logo_elaborate_characterization, hint='elaborate characterization data', hint_destination=hintlabel, command=lambda : self.elaborate_characterization(hintlabel))
        B_elaborate_characterization.pack(side=tk.LEFT)
        B_elaborate_characterization.image = logo_elaborate_characterization

        logo_save_characterization = tk.PhotoImage(data=gui_things.PL_save)
        B_save_characterization = gui_things.Button(other_button_frame, image=logo_save_characterization, hint='save characterization data', hint_destination=hintlabel, command=lambda : self.save_characterization(hintlabel))
        B_save_characterization.pack(side=tk.LEFT)
        B_save_characterization.image = logo_save_characterization

        other_button_frame.grid(row=21, column=0, sticky=tk.W)

        positions_frame.pack(anchor=tk.NW, padx=5, pady=5)

        hintlabel.pack(anchor=tk.NW)

        self.nominaldistance_E.variable.trace_add('write', lambda a,b,c : self.select_distance())
        self.detector_name_E.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_detector())
        self.gsource_name_E.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_source(M))
        self.positions_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_position())
        self.positions_CB.set('reference')
        self.select_position()
        self._update_plot_labels()
        self.plot_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._update_plot())

    def _display_fit_information(self):
        if self.plot_CB.get() != '':
            text = ''
            if self.plot_CB.get() == 'reference efficiency':
                title = 'reference efficiency'
                text = self.characterization_results['reference efficiency']._showoff()

                header = f'{"E / keV".ljust(10)}{"e / 1".rjust(10)}{"efit / 1".rjust(10)}{"res / 1".rjust(10)}\n'

                efit = [self.characterization_results["reference efficiency"].eval(eV) for eV in self.characterization_results['energy_data']]

                residuals = '\n'.join([f'{format(eV,".1f").ljust(10)}{format(ef_V,".2e").rjust(10)}{format(eft_V[0],".2e").rjust(10)}{(format((ef_V - eft_V[0]) / eft_V[0]*100,".1f") + " %").rjust(10)}' for eV, ef_V, eft_V in zip(self.characterization_results['energy_data'], self.characterization_results['eff_data'], efit)])

                text += '\n\n' + header + residuals

            elif self.plot_CB.get() == 'FWHM characterization':
                title = 'FWHM'
                space = 10
                FC = self.characterization_results['FWHM characterization']

                std_unc = np.sqrt(np.diag(FC[1]))
                head = f'{str("x^").ljust(5)}{str("p").rjust(space)}{str("ur(p)").rjust(space)}'
                head += str('').rjust(space) + ''.join([f'{str(esp).rjust(space)}' for esp in (1,0)])
                body = "\n".join([f'{str(esp).ljust(5)}{format(param, ".2e").rjust(space)}{(format(np.abs(s_unc / param) *100, ".1f") + " %").rjust(space)}{str(esp).rjust(space)}{format(cov_m[0], ".2e").rjust(space)}{format(cov_m[1], ".2e").rjust(space)}' for esp, param, cov_m, s_unc in zip((1,0), FC[0], FC[1], std_unc)])
                text = head + '\n' + body

            elif self.plot_CB.get() == 'energy characterization':
                title = 'Energy'
                space = 10
                EC = self.characterization_results['energy characterization']

                std_unc = np.sqrt(np.diag(EC[1]))
                head = f'{str("x^").ljust(5)}{str("p").rjust(space)}{str("ur(p)").rjust(space)}'
                head += str('').rjust(space) + ''.join([f'{str(esp).rjust(space)}' for esp in (1,0)])
                body = "\n".join([f'{str(esp).ljust(5)}{format(param, ".2e").rjust(space)}{(format(np.abs(s_unc / param) *100, ".1f") + " %").rjust(space)}{str(esp).rjust(space)}{format(cov_m[0], ".2e").rjust(space)}{format(cov_m[1], ".2e").rjust(space)}' for esp, param, cov_m, s_unc in zip((1,0), EC[0], EC[1], std_unc)])
                text = head + '\n' + body

            elif 'd0p:' in self.plot_CB.get():
                _dist = self.plot_CB.get().split()[-1]
                title = f"d'0 at {_dist} mm"
                text = self.characterization_results['d0p_fits'][_dist]._showoff()

            elif 'keDd:' in self.plot_CB.get():
                _dist = self.plot_CB.get().split()[-1]
                title = f'keDd at {_dist} mm'
                text = self.characterization_results['kdd_fits'][_dist]._showoff()
            
            elif 'PT:' in self.plot_CB.get():
                _dist = self.plot_CB.get().split()[-1]
                title = f'PT at {_dist} mm'
                text = self.characterization_results['PT_fits'][_dist]._showoff()

            ITL = tk.Toplevel(self.detectorcharacterizationmodify_window)
            ITL.title(title)
            ITL.resizable(True, False)
            STB = gui_things.ScrollableText(ITL, width=95, height=12, data=text)
            STB.pack(anchor=tk.NW, fill=tk.X, expand=True, padx=5, pady=5)
    
    def _update_plot_labels(self):
        labels = []
        for item in self.characterization_results.keys():
            if item == 'energy characterization':
                labels.append('energy characterization')
            if item == 'FWHM characterization':
                labels.append('FWHM characterization')
            if item == 'reference efficiency':
                labels.append('reference efficiency')
            if item == 'd0p_fits':
                multilabels = [f'd0p: {dictitem}' for dictitem in self.characterization_results['d0p_fits'].keys()]
                labels += multilabels
            if item == 'kdd_fits':
                multilabels = [f'keDd: {dictitem}' for dictitem in self.characterization_results['kdd_fits'].keys()]
                labels += multilabels
            if item == 'PT_fits':
                multilabels = [f'PT: {dictitem}' for dictitem in self.characterization_results['PT_fits'].keys()]
                labels += multilabels

        self.plot_CB['values'] = labels
        if 'reference efficiency' in self.plot_CB['values']:
            self.plot_CB.set('reference efficiency')
        else:
            self.plot_CB.set('')
        self._update_plot()

    def save_characterization(self, hintlabel):
        proceed = True

        if self.char_name_E.get().replace(' ','') == '':
            proceed = False

        if self.temporary_detector is None:
            proceed = False

        if self.temporary_source is None or len(self.temporary_source.selection) < 7:
            proceed = False

        if len(self.temporary_positions.values()) != len(set([item.distance for item in self.temporary_positions.values()])):
            proceed = False

        if self.temporary_positions['reference'].fdistance() < np.max([item.fdistance() for item in self.temporary_positions.values()]):
            proceed = False

        nnlen = len([item.npos() for item in self.temporary_positions.values()if item.npos() > 0])

        if nnlen == 0:
            proceed = False

        if self.characterization_results == {}:
            proceed = False

        try:
            unomdis = float(self.unc_nompos_SB.get())
        except (TypeError, ValueError):
            unomdis = 0.1

        if proceed:
            DC = naaobject.DetectorCharacterization(self.char_name_E.get(), self.temporary_detector, self.temporary_source, self.temporary_positions, self.temporary_background, self.characterization_results, unomdis)
            DC._save()
            detector_characterization_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'characterizations')) if filename.lower().endswith('.dcr')]
            self.detector_chr_LB._update(detector_characterization_list)
            hintlabel.configure(text='Characterization successfully saved!')
        else:
            hintlabel.configure(text='Error occurred, failed to save! Update elaboration and retry')

    def elaborate_characterization(self, hintlabel):
        proceed = True

        if self.char_name_E.get().replace(' ','') == '':
            proceed = False

        if self.temporary_detector is None:
            proceed = False

        if self.temporary_source is None or len(self.temporary_source.selection) < 7:
            proceed = False

        if len(self.temporary_positions.values()) != len(set([item.distance for item in self.temporary_positions.values()])):
            proceed = False

        if self.temporary_positions['reference'].fdistance() < np.max([item.fdistance() for item in self.temporary_positions.values()]):
            proceed = False

        nnlen = len([item.npos() for item in self.temporary_positions.values()if item.npos() > 0])

        if nnlen == 0:
            proceed = False

        fit_ch, fit_en, fit_fw, fit_efy, nn, ur_efy, warnings_note = self.get_data_to_fit()

        if len(fit_efy) <= 6:
            proceed = False

        #FILTERING OF ONLY FREE-COINCIDENCE EMISSIONS
        if self.temporary_source is not None:
            noCOI_filter = self.temporary_source.data[self.temporary_source.selection]['COIfree']
            coifree = self.temporary_source.data[self.temporary_source.selection][noCOI_filter]
        else:
            coifree = pd.DataFrame([])
            proceed = False
        
        C_values, uC_values = self.get_coifreedata_to_fit(coifree)
        elaboration_day = datetime.date.today()
        self.characterization_results.clear()

        if proceed:
            #ENERGY FIT
            energy_fit_parameters, energy_fit_covariance, _ = self._fit_linear(fit_ch, fit_en, (1, 0))

            #FWHM FIT
            fwhm_fit_parameters, fwhm_fit_covariance, _ = self._fit_linear(fit_ch, np.power(fit_fw, 2), (1, 0))

            #EFFICIENCY FIT AT REFERENCE
            efficiency_fit_parameters, efficiency_fit_covariance, _ = self._efficiency_fit(fit_en, fit_efy)

            self.characterization_results['channel_data'] = fit_ch
            self.characterization_results['energy_data'] = fit_en
            self.characterization_results['fwhm_data'] = fit_fw
            self.characterization_results['eff_data'] = fit_efy
            self.characterization_results['ueff_data'] = ur_efy
            self.characterization_results['energy characterization'] = (energy_fit_parameters, energy_fit_covariance)
            self.characterization_results['FWHM characterization'] = (fwhm_fit_parameters, fwhm_fit_covariance)
            self.characterization_results['reference efficiency'] = naaobject.SixParameterFix(efficiency_fit_parameters, efficiency_fit_covariance)
            self.characterization_results['elaboration_day'] = elaboration_day

            #SQRT_C TO DER
            #check norm_C size

            d0p_fits = {}
            kdd_fits = {}
            PT_fits = {}

            norm_C = C_values.iloc[0] / C_values
            norm_uC = uC_values / C_values
            sqrt_C = np.sqrt(norm_C)
            d0_C = norm_C.copy(deep=True)
            d0_C[:] = np.nan
            ud0_C = norm_C.copy(deep=True)
            ud0_C[:] = 0.0

            if C_values.shape[0] > 3 and C_values.shape[1] > 6:

                #populate d'0 matrix
                for energy_C in sqrt_C.columns:
                    local_copy = sqrt_C[energy_C].copy(deep=True)
                    local_copy.dropna(inplace=True)
                    XX = np.array(local_copy.index)
                    if len(XX) > 3:
                        parameters, mcov, _ = self._fit_linear(XX, local_copy, (2,1,0))

                        col_der = self.linear_d0(XX, parameters)
                        col_uder = self.ulinear_d0(XX, parameters, mcov)
                        d0_C.loc[local_copy.index, energy_C] = col_der
                        ud0_C.loc[local_copy.index, energy_C] = col_uder

                #perform d'0 fits
                for _dist in list(d0_C.index):
                    local_copy = d0_C.loc[_dist].copy(deep=True)
                    local_copy.dropna(inplace=True)
                    XX = np.array(local_copy.index)
                    if len(XX) > 5:
                        parameters, mcov, _ = self._d0p_fit(XX, local_copy)
                        d0p_fits[f'{_dist:.1f}'] = naaobject.d0SixParameterFix(parameters, mcov)

                #keDD evaluation

                rel_unc_C_values = norm_C * np.sqrt(np.power(norm_uC.iloc[0],2) + np.power(norm_uC,2))

                for _dist in list(norm_C.index)[1:]:
                    local_copy = norm_C.loc[_dist].copy(deep=True)
                    local_copy.dropna(inplace=True)
                    XX = np.array(local_copy.index)
                    if len(XX) > 6:
                        parameters, mcov, _ = self._efficiency_fit(XX, local_copy)
                        kdd_fits[f'{_dist:.1f}'] = naaobject.SixParameterFix(parameters, mcov)

            #PT evaluation
            PT_values, uPT_values = self.get_PTdata_to_fit(coifree)
            for _dist in list(PT_values.index)[1:]:
                local_copy = PT_values.loc[_dist].copy(deep=True)
                local_copy.dropna(inplace=True)
                XX = np.array(local_copy.index)
                if len(XX) > 4:
                    outcome = self._PT_fit(XX, local_copy)
                    PT_fits[f'{_dist:.1f}'] = naaobject.PTFit(*outcome)

            self.characterization_results['d0p_fits'] = d0p_fits
            self.characterization_results['kdd_fits'] = kdd_fits
            self.characterization_results['C_values'] = (C_values, uC_values)
            self.characterization_results['d0_values'] = (d0_C, ud0_C)
            self.characterization_results['PT_values'] = (PT_values, uPT_values)
            self.characterization_results['PT_fits'] = PT_fits

            self._update_plot_labels()
        else:
            hintlabel.configure(text='incomplete information provided')

    def linear_d0(self, X, p):
        #filter non-physical values
        ret = -(-p[0]*np.power(X,2) + p[2]) / (2*p[0]*X + p[1])
        ret[ret >= 0.0] = np.nan
        return ret

    def ulinear_d0(self, X, p, mcov):
        scp0 = (p[1]*np.power(X,2) + 2*p[2]*X) / np.power(2*p[0]*X + p[1], 2)
        scp1 = (-p[0]*np.power(X,2) + p[2]) / np.power(2*p[0]*X + p[1], 2)
        scp2 = -1 / (2*p[0]*X + p[1])

        sc_stack = np.stack([scp0, scp1, scp2])

        return np.array([np.sqrt((values.T@mcov)@values) for values in sc_stack.T])

    def _update_plot(self):
        self.SF_axes.clear()
        if self.plot_CB.get() != '':
            if self.plot_CB.get() == 'reference efficiency':
                lop, hip = np.min([np.min(self.characterization_results['energy_data']), 50]), np.max([np.max(self.characterization_results['energy_data']), 2000])
                xx, yy = self.fit_draw(self.characterization_results['reference efficiency'].parameters, lop, hip)
                self.SF_axes.plot(xx, np.exp(yy), 'r-')
                PYX = self.characterization_results['energy_data']
                PYY = self.characterization_results['eff_data']
                self.SF_axes.plot(PYX, PYY, 'ko')
                self.SF_axes.set_ylabel(r'$\varepsilon$ / 1')
                self.SF_axes.set_xlabel(r'$E$ / keV')

            elif self.plot_CB.get() == 'energy characterization':
                lop, hip = np.min([np.min(self.characterization_results['channel_data']), 50]), np.max([np.max(self.characterization_results['channel_data']), 2000])
                xx, yy = self.fit_draw(self.characterization_results['energy characterization'][0], lop, hip, MeV=False)
                self.SF_axes.plot(xx, yy, 'r-')
                PYX = self.characterization_results['channel_data']
                PYY = self.characterization_results['energy_data']
                self.SF_axes.plot(PYX, PYY, 'ko')
                self.SF_axes.set_ylabel(r'$E$ / keV')
                self.SF_axes.set_xlabel(r'$channel$ / 1')

            elif self.plot_CB.get() == 'FWHM characterization':
                lop, hip = np.min([np.min(self.characterization_results['channel_data']), 50]), np.max([np.max(self.characterization_results['channel_data']), 2000])
                xx, yy = self.fit_draw(self.characterization_results['FWHM characterization'][0], lop, hip, MeV=False)
                self.SF_axes.plot(xx, np.sqrt(yy), 'r-')
                PYX = self.characterization_results['channel_data']
                PYY = self.characterization_results['fwhm_data']
                self.SF_axes.plot(PYX, PYY, 'ko')
                self.SF_axes.set_ylabel(r'$FWHM$ / 1')
                self.SF_axes.set_xlabel(r'$channel$ / 1')

            elif 'keDd:' in self.plot_CB.get():
                plit = self.plot_CB.get().split()[1]
                CVs = self.characterization_results['C_values'][0]
                norm_C = CVs.iloc[0] / CVs
                norm_C = norm_C.loc[float(plit)]
                lop, hip = np.min([np.min(self.characterization_results['energy_data']), 50]), np.max([np.max(self.characterization_results['energy_data']), 2000])
                xx, yy = self.fit_draw(self.characterization_results['kdd_fits'][plit].parameters, lop, hip)
                self.SF_axes.plot(xx, np.exp(yy), 'r-')
                PYX = norm_C.index
                PYY = norm_C
                self.SF_axes.plot(PYX, PYY, 'ko')
                self.SF_axes.set_ylabel(r'$k\varepsilon\Delta d$ / 1')
                self.SF_axes.set_xlabel(r'$E$ / keV')

            elif 'd0p:' in self.plot_CB.get():
                plit = self.plot_CB.get().split()[1]
                CVs = self.characterization_results['d0_values'][0]
                CVs = CVs.loc[float(plit)]
                lop, hip = np.min([np.min(self.characterization_results['energy_data']), 50]), np.max([np.max(self.characterization_results['energy_data']), 2000])
                xx, yy = self.fit_draw(self.characterization_results['d0p_fits'][plit].parameters, lop, hip)
                self.SF_axes.plot(xx, -np.exp(yy), 'r-')
                PYX = CVs.index
                PYY = CVs
                self.SF_axes.plot(PYX, PYY, 'ko')
                self.SF_axes.set_ylabel(r'$d^{\prime}_0$ / mm')
                self.SF_axes.set_xlabel(r'$E$ / keV')

            elif 'PT:' in self.plot_CB.get():
                plit = self.plot_CB.get().split()[1]
                CVs = self.characterization_results['PT_values'][0]
                CVs = CVs.loc[float(plit)]
                lop, hip = np.min([np.min(self.characterization_results['energy_data']), 50]), np.max([np.max(self.characterization_results['energy_data']), 2000])
                xx = np.linspace(lop, hip, 500)
                xlimit = self.characterization_results['PT_fits'][plit].limit
                ylimit, _ = self.characterization_results['PT_fits'][plit].eval(xlimit)
                yy, _ = self.characterization_results['PT_fits'][plit].eval(xx)
                self.SF_axes.loglog(xx, yy, 'r-')
                PYX = CVs.index
                PYY = CVs
                self.SF_axes.loglog(PYX, PYY, 'ko')
                self.SF_axes.loglog(xlimit, ylimit, marker='x', color='k')
                self.SF_axes.set_ylabel(r'$PT$ / 1')
                self.SF_axes.set_xlabel(r'$E$ / keV')

        self.SF_figure.tight_layout()
        self.SF_canvas.draw()

    def fit_draw(self, parameters, low_point=100, high_point=3000, N=500, MeV=True):
        total_esp = [1, 0, -1, -2, -3, -4]
        if len(parameters) == 6:
            esp = total_esp
        elif len(parameters) == 2:
            esp = total_esp[:2]
        X = np.linspace(low_point, high_point, N)
        if MeV:
            X = X / 1000
        W = X[:, np.newaxis]**esp
        if MeV:
            X = X * 1000
        return X, parameters@W.T
    
    def _fit_linear(self, X, Y, esp, rel=False):
        W = X[:, np.newaxis]**esp
        I = np.identity(W.shape[0])
        parameters = np.linalg.inv(W.T@W)@(W.T@Y)
        residuals = Y - parameters@W.T
        n, k = Y.shape[0], W.shape[1]
        mcov = np.linalg.inv((W.T@np.linalg.inv(np.true_divide(1, n-k)*np.dot(residuals, residuals)*I))@W)
        if rel:
            #relative residuals
            residuals = residuals / (parameters@W.T)
        return parameters, mcov, residuals

    def _d0p_fit(self, X, Y, limit=100):
        X = X / 1000
        Y = np.log(np.abs(Y))
        esp = [1, 0, -1, -2, -3]
        solution = False
        fparameters, fmcov = np.array([0.0]*6), np.zeros((6,6))
        while solution == False:
            parameters, mcov, residuals = self._fit_linear(X, Y, esp)
            uncertainties = np.sqrt(np.diag(mcov))
            if np.max(np.abs(uncertainties / parameters)) > limit / 100 and len(parameters) > 4:
                idx = np.argmax(np.abs(uncertainties / parameters))
                try:
                    idx = idx[0]
                except (IndexError):
                    pass
                esp.pop(idx)
            else:
                solution = True
        guide = [1, 0, -1, -2, -3, -4]
        for exponent, par, covline in zip(esp, parameters, mcov):
            fparameters[guide.index(exponent)] = par
            for exponent2, cov in zip(esp, covline):
                fmcov[guide.index(exponent),guide.index(exponent2)] = cov
        return fparameters, fmcov, residuals
    
    def _efficiency_fit(self, X, Y, limit=100):
        X = X / 1000
        Y = np.log(Y)
        esp = [1, 0, -1, -2, -3, -4]
        solution = False
        fparameters, fmcov = np.array([0.0]*6), np.zeros((6,6))
        while solution == False:
            parameters, mcov, residuals = self._fit_linear(X, Y, esp)
            uncertainties = np.sqrt(np.diag(mcov))
            if np.max(np.abs(uncertainties / parameters)) > limit / 100 and len(parameters) > 4:
                idx = np.argmax(np.abs(uncertainties / parameters))
                try:
                    idx = idx[0]
                except:
                    pass
                esp.pop(idx)
            else:
                solution = True
        guide = [1, 0, -1, -2, -3, -4]
        for exponent, par, covline in zip(esp, parameters, mcov):
            fparameters[guide.index(exponent)] = par
            for exponent2, cov in zip(esp, covline):
                fmcov[guide.index(exponent),guide.index(exponent2)] = cov
        return fparameters, fmcov, residuals
    
    def _PT_fit(self, X, Y):
        optimized_E, optimized_param_L, optimized_cov_L, optimized_param_P, optimized_cov_P, _ = None, None, None, None, None, None
        limit, parameters_L, cov_L, parameters_P, cov_P = 0, np.array([0.0, 0.0]), np.array([[1.0, 0.0], [0.0, 1.0]]), np.array([0.0, 0.0, 0.0]), np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        try:
            start = X[2] + 1
            if start < 200:
                start = 200
            end = X[-1] - 1
            if end < 450:
                raise IndexError
        except IndexError:
            return limit, parameters_L, cov_L, parameters_P, cov_P
        range_limit = [start, 450]

        #3-way strategy
        while range_limit[1] - range_limit[0] > 2:
            point_A = range_limit[0]
            point_B = int(range_limit[0] + (range_limit[1] - range_limit[0]) / 2)
            point_C = range_limit[1]

            result_A = self.specifit_PT_fit(X, Y, point_A)
            result_B = self.specifit_PT_fit(X, Y, point_B)
            result_C = self.specifit_PT_fit(X, Y, point_C)

            if optimized_E is None:
                optimized_E, optimized_param_L, optimized_cov_L, optimized_param_P, optimized_cov_P, _ = result_B
            elif result_B[-1] < _:
                optimized_E, optimized_param_L, optimized_cov_L, optimized_param_P, optimized_cov_P, _ = result_B
            else:
                break
        
            #range_limit shrinking
            if result_A[-1] < result_C[-1]:
                range_limit = [result_A[0], result_B[0]]

        return optimized_E, optimized_param_L, optimized_cov_L, optimized_param_P, optimized_cov_P

    def residual_minimization_func(self, params, x, y):
        residuals = [y_data - self.PT_func_poly(x_data, *params) for x_data, y_data in zip(x,y)]
        return np.sum(np.power(residuals,2))

    def PT_func_poly(self, x, a1, a2, a3):
        return a1*np.power(x,2) + a2*x + a3

    def specifit_PT_fit(self, X, Y, E):
        x_data_selector = X > E
        x_data, y_data = X[x_data_selector], Y[x_data_selector]
        x_data, y_data = np.log10(x_data), np.log10(y_data)

        lparam, lcov, lres = self._fit_linear(x_data, y_data, (1, 0), True)

        logyE = lparam[0] * np.log10(E) + lparam[1]
        #yE = 10**logyE

        x_data, y_data = X[~x_data_selector], Y[~x_data_selector]
        x_data, y_data = np.log10(x_data), np.log10(y_data)
        root = minimize(self.residual_minimization_func, [0,1,1], args=(x_data, y_data), constraints=({'type': 'eq', 'fun': lambda x: 2*x[0]*np.log10(E)+x[1]-lparam[0]}, {'type': 'eq', 'fun': lambda x: x[0]*np.power(np.log10(E),2) + x[1]*np.log10(E) + x[2] - logyE}))
        pparam = root.x
        try:
            pcov = np.linalg.inv(2 * np.dot(root.jac.T, root.jac))
        except Exception:
            pcov = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        pres = (self.PT_func_poly(x_data, *pparam) - y_data) / y_data
        allres = np.sqrt(np.sum(np.power(lres,2)) + np.sum(np.power(pres,2)))

        return E, lparam, lcov, pparam, pcov, allres

    def get_data_to_fit(self):
        #do something under the hood
        fit_ch = []  # mean(axis=1) #maybe single
        fit_en = []  # single       #maybe single
        fit_fw = []  # mean(axis=1) #maybe single
        fit_efy = []  # mean(axis=1)#maybe single
        u_efy = [] # statistical (relative) uncertainty of peak 
        index = []
        warnings = []

        if self.temporary_source is None or self.temporary_detector is None:
            return np.array(fit_ch), np.array(fit_en), np.array(fit_fw), np.array(fit_efy), np.array(index), np.array(u_efy), warnings

        for idx in list(self.temporary_source.data[self.temporary_source.selection].index):
            local = self.temporary_source.data.loc[idx]
            localE = f'{local["emitter"]} {float(local["energy"]):.1f} keV'

            emission_found = []
            spectra_names = []
            for spectrum in self.temporary_positions['reference'].spectra:
                selectio = [(item[nn], peakline) for item, nn, peakline in zip(spectrum.suspected_peaks, spectrum.assigned_peaks, spectrum.peak_list) if nn != -1]
                for emiss in selectio:
                    if emiss[0].emission == localE:
                        emission_found.append(emiss)
                        spectra_names.append(spectrum)
            if len(emission_found) > 0:
                chosen_info = self._get_best_result(emission_found, spectra_names, 'A')
                fit_ch.append(chosen_info[1])
                fit_en.append(chosen_info[0])
                fit_fw.append(chosen_info[2])
                fit_efy.append(chosen_info[3])
                u_efy.append(chosen_info[4])
                warnings.append(chosen_info[5])
                index.append(idx)

        return np.array(fit_ch), np.array(fit_en), np.array(fit_fw), np.array(fit_efy), np.array(index), np.array(u_efy), warnings
    
    def get_PTdata_to_fit(self, coifree):
        keys = sorted([(key, value.fdistance()) for key, value in self.temporary_positions.items()], key=lambda x:x[1], reverse=True)

        fit_C = []
        fit_uC = []

        for key in keys:
            next_line = []
            unext_line = []

            for idx in list(coifree.index):
                local = coifree.loc[idx]
                localE = f'{local["emitter"]} {float(local["energy"]):.1f} keV'

                emission_found = []
                spectra_names = []
                next_pos = self.temporary_positions.get(key[0])
                for spectrum in next_pos.spectra:
                    selectio = [(item[nn], peakline) for item, nn, peakline in zip(spectrum.suspected_peaks, spectrum.assigned_peaks, spectrum.peak_list) if nn != -1]
                    for emiss in selectio:
                        if emiss[0].emission == localE:
                            emission_found.append(emiss)
                            spectra_names.append(spectrum)
                chosen_info = self._get_PT_result(emission_found, spectra_names)
                next_line.append(chosen_info[0])
                unext_line.append(chosen_info[1])

            fit_C.append(next_line)
            fit_uC.append(unext_line)

        fit_C = pd.DataFrame(data=fit_C, index=[key[1] for key in keys], columns=[float(coifree.loc[idx]["energy"]) for idx in coifree.index])
        fit_uC = pd.DataFrame(data=fit_uC, index=[key[1] for key in keys], columns=[float(coifree.loc[idx]["energy"]) for idx in coifree.index])

        return fit_C, fit_uC
    
    def get_coifreedata_to_fit(self, coifree):
        keys = sorted([(key, value.fdistance()) for key, value in self.temporary_positions.items() if key != 'reference'], key=lambda x:x[1], reverse=True)

        ref_pos = self.temporary_positions.get('reference')
        fit_C = []
        fit_uC = []

        first_line = []
        ufirst_line = []
        n_index = []

        for idx in list(coifree.index):
            local = coifree.loc[idx]
            localE = f'{local["emitter"]} {float(local["energy"]):.1f} keV'

            emission_found = []
            spectra_names = []
            for spectrum in ref_pos.spectra:
                selectio = [(item[nn], peakline) for item, nn, peakline in zip(spectrum.suspected_peaks, spectrum.assigned_peaks, spectrum.peak_list) if nn != -1]
                for emiss in selectio:
                    if emiss[0].emission == localE:
                        emission_found.append(emiss)
                        spectra_names.append(spectrum)
            if len(emission_found) > 0:
                chosen_info = self._get_best_result(emission_found, spectra_names, 'CR')
                first_line.append(chosen_info[3])
                ufirst_line.append(chosen_info[4])
                n_index.append(idx)

        fit_C.append(first_line)
        fit_uC.append(ufirst_line)

        for key in keys:
            next_line = []
            unext_line = []

            for idx in n_index:
                local = coifree.loc[idx]
                localE = f'{local["emitter"]} {float(local["energy"]):.1f} keV'

                emission_found = []
                spectra_names = []
                next_pos = self.temporary_positions.get(key[0])
                for spectrum in next_pos.spectra:
                    selectio = [(item[nn], peakline) for item, nn, peakline in zip(spectrum.suspected_peaks, spectrum.assigned_peaks, spectrum.peak_list) if nn != -1]
                    for emiss in selectio:
                        if emiss[0].emission == localE:
                            emission_found.append(emiss)
                            spectra_names.append(spectrum)
                chosen_info = self._get_best_result(emission_found, spectra_names, 'CR')
                next_line.append(chosen_info[3])
                unext_line.append(chosen_info[4])

            fit_C.append(next_line)
            fit_uC.append(unext_line)

        fit_C = pd.DataFrame(data=fit_C, index=[ref_pos.fdistance()] + [key[1] for key in keys], columns=[float(coifree.loc[idx]["energy"]) for idx in n_index])
        fit_uC = pd.DataFrame(data=fit_uC, index=[ref_pos.fdistance()] + [key[1] for key in keys], columns=[float(coifree.loc[idx]["energy"]) for idx in n_index])
        return fit_C, fit_uC

    def _get_PT_result(self, emission_found, local):
        if len(emission_found) == 1:
            bestchoice = emission_found[0]
            spct = local[0]
            #message = f' -> {spct.filename()}'
        elif len(emission_found) == 0:
            return np.nan, np.nan
            #message = f' -> {spct.filename()}'
        else:
            argm = np.argmin([item[1][5] / item[1][4] for item in emission_found])
            bestchoice = emission_found[argm]
            spct = local[argm]
            #message = f' -> {spct.filename()}'
        PT = bestchoice[1][4] / np.sum(spct.background_corrected_spectrum(self.temporary_background, lowchannelcompensation=True))
        uPT = 0.0
        return PT, uPT#PT, uPT
    
    def _get_best_result(self, emission_found, local, measurand='CR'):
        if len(emission_found) == 1:
            bestchoice = emission_found[0]
            spct = local[0]
            message = f' -> {spct.filename()}'
        else:
            argm = np.argmin([item[1][5] / item[1][4] for item in emission_found])
            bestchoice = emission_found[argm]
            spct = local[argm]
            message = f' -> {spct.filename()}'
        eff, ueff = self._activity_or_CR(bestchoice, spct, measurand)
        return bestchoice[0].energy, bestchoice[1][0], bestchoice[1][6], eff, ueff, message #energy, channel, FWHM, efficiency, uefficiency

    def _activity_or_CR(self, bestchoice, spct, measurand='CR'):
        mu = self.temporary_detector.mu
        NPA, uNPA = bestchoice[1][4], bestchoice[1][5]
        _lbd = bestchoice[0].line['lambda']
        ACT, YLD = bestchoice[0].line['activity'], bestchoice[0].line['yield']
        uACT, uYLD = bestchoice[0].line['u_activity'], bestchoice[0].line['u_yield']
        td = spct.datetime - self.temporary_source.datetime
        td = td.total_seconds()
        if measurand.lower() in ('a', 'activity', 'act'):
            EFF = (NPA*_lbd*spct.real_time*np.exp(mu*(1-spct.live_time/spct.real_time)))/(spct.live_time*np.exp(-_lbd*td)*(1-np.exp(-_lbd*spct.real_time))*YLD*ACT)
            uEFF = EFF * np.sqrt(np.power(uNPA / NPA, 2) + np.power(uACT / ACT, 2) + np.power(uYLD / YLD, 2))
            return EFF, uEFF
        EFF = (NPA*_lbd*spct.real_time*np.exp(mu*(1-spct.live_time/spct.real_time)))/(spct.live_time*np.exp(-_lbd*td)*(1-np.exp(-_lbd*spct.real_time)))
        uEFF = EFF * uNPA / NPA
        return EFF, uEFF
        
        
        



        
    def visualize_dec(self, parent):
        if self.temporary_detector is not None:
            TPDEC = tk.Toplevel(parent)
            TPDEC.title(f'Detector: {self.temporary_detector.name}')
            TPDEC.resizable(False, False)

            tk.Label(TPDEC, text='detector name', width=20, anchor=tk.W).grid(row=0, column=0, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text=self.temporary_detector.name, width=20, anchor=tk.W).grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text='relative efficiency / %', anchor=tk.W).grid(row=1, column=0, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text=self.temporary_detector.relative_efficiency, width=20, anchor=tk.W).grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text='resolution at 1332 / keV', anchor=tk.W).grid(row=2, column=0, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text=self.temporary_detector.resolution, width=20, anchor=tk.W).grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text='detector type', anchor=tk.W).grid(row=3, column=0, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text=self.temporary_detector.detector_type, width=20, anchor=tk.W).grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text='crystal diameter / mm', anchor=tk.W).grid(row=4, column=0, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text=self.temporary_detector.diameter, width=20, anchor=tk.W).grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5)
            tk.Frame(TPDEC).grid(row=5, column=1, pady=5)
            tk.Label(TPDEC, text='μ / 1', anchor=tk.W).grid(row=7, column=0, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text='x', anchor=tk.W).grid(row=6, column=1)
            tk.Label(TPDEC, text='u(x)', anchor=tk.W).grid(row=6, column=2)
            tk.Label(TPDEC, text=f'{self.temporary_detector.mu:.4f}', width=10, anchor=tk.W).grid(row=7, column=1, sticky=tk.W, padx=5)
            tk.Label(TPDEC, text=f'{self.temporary_detector.u_mu:.4f}', width=10, anchor=tk.W).grid(row=7, column=2, sticky=tk.W, padx=5)

    def go_to_opencharacterizationspectra(self, M):
        #close children if necessary
        if self.temporary_source is not None:
            database = self.temporary_source.data.copy()
            database.rename(columns={"energy": "E"}, inplace=True)
            database['E'] = database['E'].astype(float)
        else:
            database = None
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))
        limit_s = M.settings.get('calibs statistical uncertainty limit')
        try:
            output = tuple(askopenfilenames(parent=self.detectorcharacterizationmodify_window, title=f'Recall characterization spectra',filetypes=filetypes))
        except TypeError:
            output = ()
        for filename in output:
            if filename != '' and filename != ():
                peak_list, counts, start_acquisition, real_time, live_time, result, _, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=M.settings.get('look for spectrum file'))
                if result == True:
                    Spectrum = naaobject.SpectrumAnalysis(identity=f'characterization spectrum', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=filename, source=source, efficiency=None, energy_tolerance=M.settings.get('energy tolerance'), database=database,prompt_peak_identification=True)#SpectrumAnalysis
                    self.temporary_positions[self.positions_CB.get()].spectra.append(Spectrum)
        self._update_spectralist()

    def _update_spectralist(self):
        self.spectra_LB._update([item.filename() for item in self.temporary_positions[self.positions_CB.get()].spectra])

    def add_position(self):
        if self.peaklist_window is not None:
            try:
                self.peaklist_window.destroy()
            except:
                pass
        nn = 1
        names = tuple(self.temporary_positions.keys())
        while f'position {nn}' in names:
            nn += 1
        self.temporary_positions[f'position {nn}'] = NominalCountingPosition(f'position {nn}')
        self.positions_CB['values'] = list(self.temporary_positions.keys())
        self.positions_CB.set(f'position {nn}')
        self.select_position()

    def rename_position(self, hintlabel):

        def check_function(string):
            response = True
            chars = set("""*"?\/|[]{}""")
            if string.replace(' ','') == '' or any((c in chars) for c in string):
                response = False
            return response

        def command_return(hintlabel):
            messagetext='invalid string'
            new_string = self.subvariable.get()
            names = tuple(self.temporary_positions.keys())
            if check_function(new_string) and new_string not in names:

                nom_pos = self.temporary_positions.pop(self.positions_CB.get())
                self.temporary_positions[new_string] = nom_pos
                self.positions_CB['values'] = list(self.temporary_positions.keys())
                self.positions_CB.set(new_string)
                self.select_position()

                self.subvariable.set('')
                self.subwindow.destroy()
                self.subwindow = None
                messagetext='field updated'
            if hintlabel is not None:
                hintlabel.configure(text=messagetext)

        def command_esc():
            self.subwindow.destroy()

        def command_canc():
            self.subvariable.set('')

        if self.positions_CB.get() != 'reference':
            x, y, width, height = self.positions_CB.winfo_rootx(), self.positions_CB.winfo_rooty(), self.positions_CB.winfo_width(), self.positions_CB.winfo_height()
            self.subwindow = tk.Toplevel(self.positions_CB)
            self.subwindow.overrideredirect(True)
            self.subwindow.resizable(False, False)
            self.subwindow.geometry(f'{width}x{height}+{x}+{y+height}')
            self.subvariable = tk.StringVar(self.subwindow)
            self.subvariable.set(self.positions_CB.get())
            entry = tk.Entry(self.subwindow, textvariable=self.subvariable)
            entry.pack(anchor=tk.W, fill=tk.BOTH, expand=True)
            entry.icursor(len(self.subvariable.get()))
            entry.focus_set()

            entry.bind('<Return>', lambda event : command_return(hintlabel))
            entry.bind('<Escape>', lambda event: command_esc())
            entry.bind('<Delete>', lambda event: command_canc())
            entry.bind('<FocusOut>', lambda event: command_esc())

    def delete_position(self, parent):
        if self.peaklist_window is not None:
            try:
                self.peaklist_window.destroy()
            except:
                pass
        name = self.positions_CB.get()
        if name != 'reference':
            if messagebox.askyesno(title='Delete nominal position', message=f'\nAre you sure to delete all data\nrelated to {name} nominal position?\n', parent=parent):
                del self.temporary_positions[name]
                self.positions_CB['values'] = list(self.temporary_positions.keys())
                self.positions_CB.set(f'reference')
                self.select_position()

    def select_sourceemissions(self, parent):
        if self.temporary_source is not None:

            if self.emissionselectionwindow is not None:
                    try:
                        self.emissionselectionwindow.destroy()
                    except:
                        pass
            self.emissionselectionwindow = tk.Toplevel(parent)
            self.emissionselectionwindow.title('select emissions from source')
            self.emissionselectionwindow.resizable(False, False)
            self._true_color, self._false_color = '#FFFFFF', '#ff474c'

            self.sourcemiss = gui_things.ScrollableListbox(self.emissionselectionwindow, width=50, height=20, data=[f'{item}' for item in self.temporary_source.data['reference']])

            self.sourcemiss._colored_update(self.temporary_source.selection, self._true_color, self._false_color)

            self.sourcemiss.pack(anchor=tk.NW, padx=5, pady=5)

            self.sourcemiss.listbox.bind('<Double-Button-1>', lambda e='<Double-Button-1>' : self.double_click_event())

    def double_click_event(self):
        emission_index = self.sourcemiss.curselection()
        try:
            emission_index = emission_index[0]
        except IndexError:
            emission_index = None

        if emission_index is not None:
            self.temporary_source.selection[emission_index] = not self.temporary_source.selection[emission_index]
            self.sourcemiss._colored_update(self.temporary_source.selection, self._true_color, self._false_color)

            self.sourcemiss.listbox.selection_clear(emission_index)

    def select_background(self, parent):
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))
        limit_s = 40
        try:
            filename = askopenfilename(parent=parent, title=f'Recall background spectrum',filetypes=filetypes)
        except TypeError:
            filename = ''
        notes = []
        txt = self.label_background_name.cget('text')
        if filename != '' and filename is not None:
            peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=True)
            if result == True:
                self.temporary_background = naaobject.SpectrumAnalysis(identity=f'background spectrum', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=filename, source=source, efficiency=None, energy_tolerance=1, database=None)#SpectrumAnalysis
                txt = self.temporary_background.filename()
            else:
                notes.append(note)
        self.label_background_name.configure(text=txt)

    def select_distance(self):
        self.temporary_positions[self.positions_CB.get()].distance = self.nominaldistance_E.variable.get()

    def select_position(self):
        c_position = self.temporary_positions[self.positions_CB.get()]
        self.nominaldistance_E.variable.set(c_position.distance)
        self._update_spectralist()

    def select_source(self, M):
        if self.peaklist_window is not None:
            try:
                self.peaklist_window.destroy()
            except:
                pass

        if self.emissionselectionwindow is not None:
            try:
                self.emissionselectionwindow.destroy()
            except:
                pass

        self.temporary_source = naaobject.GammaSource(f'{self.gsource_name_E.get()}.sce')
        database = self.temporary_source.data.copy()
        database.rename(columns={"energy": "E"}, inplace=True)
        database['E'] = database['E'].astype(float)

        for posx in self.temporary_positions.keys():
            for nn, _ in enumerate(self.temporary_positions[posx].spectra):
                self.temporary_positions[posx].spectra[nn].discriminate_peaks(database, M.settings.get('energy tolerance'))

    def select_detector(self):
        self.temporary_detector = naaobject.Detector(f'{self.detector_name_E.get()}.dec')

    def characterization_peaklist(self, M):
        try:
            idx = self.spectra_LB.curselection()[0]
        except IndexError:
            if self.spectra_LB.listbox.index("end") > 0:
                idx = 0
            else:
                idx = None
        if idx is not None:
            if self.peaklist_window is not None:
                try:
                    self.peaklist_window.destroy()
                except:
                    pass

            self.peaklist_window = tk.Toplevel(self.detectorcharacterizationmodify_window)
            CharacterizationPeaklistWindow(self.peaklist_window, self.temporary_positions[self.positions_CB.get()], idx, cheight=M.settings.get('page height'), background=self.temporary_background)


class NominalCountingPosition:
    def __init__(self, name):
        self.name = name
        self.distance = '0.0'
        self.spectra = []

    def fdistance(self):
        return float(self.distance)

    def npos(self):
        return len(self.spectra)
    

class CharacterizationPeaklistWindow:
    def __init__(self, parent, spectralist, index, cheight=25, background=None):
        self.SpectrumPlotSubwindow = None
        self.SpectrumProfileSubwindow = None
        self.PeakInformationSubwindow = None

        self.options = {'attach_to' : 'parent', 'resizable' : False}

        self.index = index

        self.cheight = cheight
        if background is not None and spectralist.spectra[self.index].number_of_channels() == background.number_of_channels():
            self.background = background
        else:
            self.background = None
        self.clive_time = spectralist.spectra[self.index].live_time

        localhintlabel = tk.Label(parent, text='', anchor=tk.W)

        parent.title(f'{spectralist.spectra[self.index].filename()} (at {spectralist.distance} mm)')
        parent.resizable(False, False)
        title_action_frame = tk.Frame(parent)

        logo_sprofile = tk.PhotoImage(data=gui_things.PL_frame_peak)
        B_show_spectrum_profile = gui_things.Button(title_action_frame, image=logo_sprofile, hint='display spectrum profile', hint_destination=localhintlabel, command=lambda : self.show_spectrum_plot(parent, spectralist.spectra[self.index]))
        B_show_spectrum_profile.grid(row=0, column=0, sticky=tk.W, padx=5)
        B_show_spectrum_profile.image = logo_sprofile

        ttk.Separator(title_action_frame, orient="vertical").grid(row=0, column=1, sticky=tk.NS, padx=3)

        logo_sinfo = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_show_spectrum_info = gui_things.Button(title_action_frame, image=logo_sinfo, hint='general spectrum information', hint_destination=localhintlabel, command=lambda : self.show_spectrum_info(parent, spectralist.spectra[self.index]))
        B_show_spectrum_info.grid(row=0, column=2, sticky=tk.E, padx=5)
        B_show_spectrum_info.image = logo_sinfo

        ttk.Separator(title_action_frame, orient="vertical").grid(row=0, column=3, sticky=tk.NS, padx=3)
        logo_speakinfo = tk.PhotoImage(data=gui_things.PL_ggear)
        B_show_peak_info = gui_things.Button(title_action_frame, image=logo_speakinfo, hint='peak information', hint_destination=localhintlabel, command=lambda : self.select_item_from_tree(parent, spectralist.spectra[self.index]))
        B_show_peak_info.grid(row=0, column=4, sticky=tk.E, padx=5)
        B_show_peak_info.image = logo_speakinfo

        ttk.Separator(title_action_frame, orient="vertical").grid(row=0, column=5, sticky=tk.NS, padx=3)
        logo_options = tk.PhotoImage(data=gui_things.PL_none)
        B_show_options = gui_things.Button(title_action_frame, image=logo_options, hint='clear emissions assignment', hint_destination=localhintlabel)
        B_show_options.grid(row=0, column=6, sticky=tk.E, padx=5)
        B_show_options.image = logo_options

        title_action_frame.pack(anchor=tk.W, fill=tk.X, expand=True, pady=5)

        alldata = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text='peaklist'), relief='solid', bd=2, padx=4, pady=4)

        #Treeview!
        defwidth = 80
        columns = (('channel', defwidth, tk.W), ('E / keV', defwidth, tk.E), ('net area / 1', 90, tk.E), ('uncertainty', defwidth, tk.E), ('FWHM / 1', defwidth, tk.E), ('n', 40, tk.CENTER), ('emitter', 130, tk.CENTER))
        self.tree = ttk.Treeview(alldata, columns=[item[0] for item in columns], show='headings', selectmode='browse', height=self.cheight)
        for item in columns:
            self.tree.heading(item[0], text=item[0])
            self.tree.column(item[0], anchor=item[2], stretch=False, minwidth=item[1], width=item[1])
        self.tree.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.X, expand=True)
        scroll = ttk.Scrollbar(alldata, orient="vertical", command=self.tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)

        alldata.pack(anchor=tk.NW, fill=tk.X, expand=True, padx=5, pady=5)

        localhintlabel.pack(anchor=tk.W, fill=tk.X, expand=True)

        #populate treeview
        nnn = 0
        for line, ass, sus in zip(spectralist.spectra[self.index].peak_list, spectralist.spectra[self.index].suspected_peaks, spectralist.spectra[self.index].assigned_peaks):
            self.tree.insert('', 'end', iid=nnn, values=(f'{line[0]:.2f}',f'{line[2]:.2f}',f'{line[4]:.1f}',f'{line[5]/line[4]*100:.1f} %',f'{line[6]:.2f}',self.lenass(ass),self.stringass(ass,sus)))
            nnn += 1

        self.tree.bind('<Double-Button-1>', lambda e='<Double-Button-1>' : self.select_item_from_tree(parent, spectralist.spectra[self.index]))
        B_show_options.configure(command=lambda : self.clear_emission_assignment(parent, spectralist.spectra[self.index]))

    def stringass(self, ass, sus):
        if sus > -1:
            return ass[sus].emission
        return ''
    
    def lenass(self, ass):
        if len(ass) > 0:
            return f'({len(ass)})'
        return ''

    def show_spectrum_info(self, parent, spectrum):
        if self.SpectrumProfileSubwindow is not None:
            self.SpectrumProfileSubwindow.focus()
        else:
            self.SpectrumProfileSubwindow = tk.Toplevel(parent)
            self.SpectrumProfileSubwindow.title(f'Spectrum info ({spectrum.filename()})')
            self.SpectrumProfileSubwindow.resizable(False, False)
            self.SpectrumProfileSubwindow.geometry(f'+{parent.winfo_rootx()}+{parent.winfo_rooty()}')
            mframe = tk.Frame(self.SpectrumProfileSubwindow)

            localhintlabel = tk.Label(mframe, text='', anchor=tk.W)

            info_frame = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='info'), relief='solid', bd=2, padx=4, pady=4)

            tk.Label(info_frame, text='filename:', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
            tk.Label(info_frame, text='start acquisition:', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
            tk.Label(info_frame, text='real time:', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
            tk.Label(info_frame, text='live time:', anchor=tk.W).grid(row=3, column=0, sticky=tk.W)
            tk.Label(info_frame, text='dead time:', anchor=tk.W).grid(row=4, column=0, sticky=tk.W)
            tk.Label(info_frame, text='role:', anchor=tk.W).grid(row=7, column=0, sticky=tk.W)
            tk.Label(info_frame, text='path:', anchor=tk.W).grid(row=8, column=0, sticky=tk.W)
            tk.Label(info_frame, text='peaklist lines:', anchor=tk.W).grid(row=10, column=0, sticky=tk.W)
            tk.Label(info_frame, text='prominent peaks:', anchor=tk.W).grid(row=11, column=0, sticky=tk.W)

            self.filenameL = tk.Label(info_frame, text='', anchor=tk.W)
            self.filenameL.grid(row=0, column=1, sticky=tk.W, padx=8)
            self.startacquisitionL = tk.Label(info_frame, text='', anchor=tk.W)
            self.startacquisitionL.grid(row=1, column=1, sticky=tk.W, padx=8)
            self.realL = tk.Label(info_frame, text='', anchor=tk.W)
            self.realL.grid(row=2, column=1, sticky=tk.W, padx=8)
            self.liveL = tk.Label(info_frame, text='', anchor=tk.W)
            self.liveL.grid(row=3, column=1, sticky=tk.W, padx=8)
            self.deadL = tk.Label(info_frame, text='', anchor=tk.W)
            self.deadL.grid(row=4, column=1, sticky=tk.W, padx=8)

            self.roleCB = tk.Label(info_frame, text='')
            self.roleCB.grid(row=7, column=1, sticky=tk.W, padx=8)

            self.pathL = tk.Label(info_frame, text='', width=80, anchor=tk.W)
            self.pathL.grid(row=8, column=1, sticky=tk.W, padx=8)
            self.spfileL = tk.Label(info_frame, text='', anchor=tk.W)
            self.spfileL.grid(row=9, column=1, sticky=tk.W, padx=8)
            self.pllfileL = tk.Label(info_frame, text='', anchor=tk.W)
            self.pllfileL.grid(row=10, column=1, sticky=tk.W, padx=8)
            self.psfileL = tk.Label(info_frame, text='', anchor=tk.W)
            self.psfileL.grid(row=11, column=1, sticky=tk.W, padx=8)

            info_frame.pack(anchor=tk.NW)

            localhintlabel.pack(anchor=tk.NW)

            mframe.pack(anchor=tk.NW, padx=5, pady=5)
            self._update_spectrum_info(spectrum)
            self.SpectrumProfileSubwindow.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.SpectrumProfileSubwindow))

    def show_spectrum_plot(self, parent, spectrum, centroid=None):
        if self.SpectrumPlotSubwindow is not None:
            self.SpectrumPlotSubwindow.focus()
        else:
            if spectrum.counts is not None:
                self.SpectrumPlotSubwindow = tk.Toplevel(parent)
                self.SpectrumPlotSubwindow.title('Spectrum plot')
                if self.options['resizable']:
                    res = (True, True)
                else:
                    res = (False, False)
                self.SpectrumPlotSubwindow.resizable(*res)

                #as relative
                zoom_range = [spectrum.number_of_channels()//div for div in (1000, 500, 400, 300, 200, 100, 75, 50, 40, 20, 10, 5, 2, 1) if spectrum.number_of_channels()//div > 10]
                self.SpectrumPlotSubwindow.figure = Figure(figsize=(8, 4))
                self.SpectrumPlotSubwindow.figure.patch.set_alpha(0.0)
                self.SpectrumPlotSubwindow.ax = self.SpectrumPlotSubwindow.figure.add_subplot(111)
                Figur = tk.Frame(self.SpectrumPlotSubwindow)
                Figur.grid(row=0, column=0, sticky=tk.NSEW)
                self.SpectrumPlotSubwindow.canvas = FigureCanvasTkAgg(self.SpectrumPlotSubwindow.figure, master=Figur)
                self.SpectrumPlotSubwindow.canvas.draw()
                self.SpectrumPlotSubwindow.canvas.get_tk_widget().configure(background=self.SpectrumPlotSubwindow.cget('bg'))
                self.SpectrumPlotSubwindow.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

                xlimits = (0, spectrum.number_of_channels())
                ylimits = (1, np.max(spectrum.counts)*1.10+10)

                plot = self.SpectrumPlotSubwindow.ax.plot(np.linspace(0.5,xlimits[1]+0.5,num=xlimits[1]), spectrum.counts, marker='o', linestyle='-', color='k', linewidth=0.5, markersize=3, markerfacecolor='r', zorder=9)

                self.background_counts = self.SpectrumPlotSubwindow.ax.plot(np.linspace(0.5,xlimits[1]+0.5,num=xlimits[1]), np.array([np.nan] * xlimits[1]), marker='', linestyle='-', color='g', linewidth=0.5, zorder=3)

                #limits
                self.SpectrumPlotSubwindow.ax.set_xlim(*xlimits)
                self.SpectrumPlotSubwindow.ax.set_ylim(*ylimits)
                self.SpectrumPlotSubwindow.ax.set_yscale('log', nonposy='clip')

                self.SpectrumPlotSubwindow.ax.set_ylabel('counts')
                self.SpectrumPlotSubwindow.ax.set_xlabel('channel')

                self.SpectrumPlotSubwindow.figure.tight_layout()
                self.SpectrumPlotSubwindow.canvas.draw()

                self.SpectrumPlotSubwindow.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.SpectrumPlotSubwindow))

                cid = self.SpectrumPlotSubwindow.canvas.mpl_connect('scroll_event', lambda event='scroll_event' : self.on_scroll(event, spectrum))
                sid = self.SpectrumPlotSubwindow.canvas.mpl_connect('motion_notify_event', lambda event='motion_notify_event' : self.on_motion(event, spectrum))

                infoframe = tk.Frame(self.SpectrumPlotSubwindow)
                zoomf = tk.Frame(infoframe)
                tk.Label(zoomf, text='spectrum view width').pack(side=tk.LEFT, anchor=tk.W)
                self.zoomslider = gui_things.Combobox(zoomf, width=8, state='readonly')
                self.zoomslider['values'] = zoom_range
                self.zoomslider.set(zoom_range[-1])
                self.zoomslider.pack(side=tk.RIGHT, anchor=tk.W, padx=5)
                zoomf.pack(side=tk.LEFT, anchor=tk.W)
                self.coordinates = tk.Label(infoframe, text='')
                self.coordinates.pack(side=tk.RIGHT, anchor=tk.E)
                infoframe.grid(row=1, column=0, sticky=tk.EW)

                optionframe = tk.LabelFrame(self.SpectrumPlotSubwindow, labelwidget=tk.Label(self.SpectrumPlotSubwindow, text='options'), relief='solid', bd=2, padx=4, pady=4)#options
                self.autoadjustyV = tk.IntVar(self.SpectrumPlotSubwindow)
                autoadjustyCX = tk.Checkbutton(optionframe, onvalue=1, offvalue=0, variable=self.autoadjustyV, text='autoadjust y axis')
                autoadjustyCX.pack(anchor=tk.W)
                self.autoadjustyV.set(0)

                self.display_backgroundV = tk.IntVar(self.SpectrumPlotSubwindow)
                display_backgroundCX = tk.Checkbutton(optionframe, onvalue=1, offvalue=0, variable=self.display_backgroundV, text='display background', command=lambda : self.display_background())
                display_backgroundCX.pack(anchor=tk.W)
                self.display_backgroundV.set(0)

                optionframe.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW, padx=5, pady=5)

    def display_background(self):
        pass
        if self.display_backgroundV.get() == 0:
            self.background_counts[0].set_ydata(np.array([np.nan] * len(self.background_counts[0].get_xdata())))
            self.SpectrumPlotSubwindow.canvas.draw()
        else:
            if self.background is not None:
                self.background_counts[0].set_ydata(self.background.counts / self.background.live_time * self.clive_time)
                self.SpectrumPlotSubwindow.canvas.draw()
            else:
                self.background_counts[0].set_ydata(np.array([np.nan] * len(self.background_counts[0].get_xdata())))
                self.SpectrumPlotSubwindow.canvas.draw()

    def re_center_plot(self, peak_centroid, spectrum):
        if self.SpectrumPlotSubwindow is not None:

            centroid = peak_centroid

            screen_width = int(self.zoomslider.get())
            new_limits = (int(centroid - screen_width/2), int(centroid - screen_width/2 + screen_width))
            if new_limits[0] < 0:
                new_limits = (0, screen_width)
            elif new_limits[1] > spectrum.number_of_channels():
                new_limits = (spectrum.number_of_channels()- screen_width, spectrum.number_of_channels())
            self.SpectrumPlotSubwindow.ax.set_xlim(*new_limits)
            if self.autoadjustyV.get() == True:
                ylimits = (1, np.max(spectrum.counts[new_limits[0]:new_limits[1]])*1.10+10)
                self.SpectrumPlotSubwindow.ax.set_ylim(*ylimits)

            self.SpectrumPlotSubwindow.canvas.draw()

    def on_motion(self, event, spectrum):
        #mouse motion on spectrum profile
        text=''
        if event.xdata is not None and event.ydata is not None:
            x = int(event.xdata)
            if x >= 0 and x < spectrum.number_of_channels():
                y = int(spectrum.counts[x])
                text = f'channel={x}, counts={y}'
        self.coordinates.configure(text=text)

    def _update_spectrum_info(self, spectrum):
        self.filenameL.configure(text=spectrum.filename())
        self.startacquisitionL.configure(text=spectrum.readable_datetime())
        self.realL.configure(text=f'{spectrum.real_time:.2f} s ({spectrum.real_time/3600:.2f} h)')
        self.liveL.configure(text=f'{spectrum.live_time:.2f} s ({spectrum.live_time/3600:.2f} h)')
        self.deadL.configure(text=f'{(1-spectrum.live_time/spectrum.real_time)*100:.2f} %')
        self.roleCB.configure(text='characterization spectrum')
        self.pathL.configure(text=spectrum.spectrumpath)
        self.spfileL.configure(text='')
        self.pllfileL.configure(text=f'{spectrum.peak_summary()[0]}')
        self.psfileL.configure(text=spectrum.peak_summary(8)[1])

    def on_scroll(self, event, spectrum):
        #Scroll spectrum profile
        if event.xdata is not None and event.ydata is not None:
            current_limits = self.SpectrumPlotSubwindow.ax.get_xlim()

            centroid, diff = int((current_limits[0]+current_limits[1])/2), abs(int(event.xdata-(current_limits[0]+(current_limits[1]-current_limits[0])/2)))

            screen_width = int(self.zoomslider.get())
            new_limits = (int(centroid - screen_width/2 + event.step*diff), int(centroid - screen_width/2 + screen_width + event.step*diff))
            if new_limits[0] < 0:
                new_limits = (0, screen_width)
            elif new_limits[1] > spectrum.number_of_channels():
                new_limits = (spectrum.number_of_channels()- screen_width, spectrum.number_of_channels())
            self.SpectrumPlotSubwindow.ax.set_xlim(*new_limits)
            if self.autoadjustyV.get() == True:
                ylimits = (1, np.max(spectrum.counts[new_limits[0]:new_limits[1]])*1.10+10)
                self.SpectrumPlotSubwindow.ax.set_ylim(*ylimits)

            self.SpectrumPlotSubwindow.canvas.draw()
            self.on_motion(event, spectrum)
    
    def select_item_from_tree(self, parent, spectrum):
        curItem = self.tree.focus()
        item_index = self.tree.index(curItem)
        values = self.tree.item(curItem, 'values')
        if values != '':
            self.re_center_plot(int(spectrum.peak_list[item_index][0]), spectrum)
            self.show_peak_info(parent, spectrum, item_index)

    def clear_emission_assignment(self, parent, spectrum):
        if messagebox.askyesno(title='Clear assigned emissions', message=f'\nAre you sure to clear\nall currently assigned emissions?\n', parent=parent):

            try:
                self.PeakInformationSubwindow.destroy()
                self.PeakInformationSubwindow = None
            except Exception:
                pass
            
            for nn, _ in enumerate(spectrum.assigned_peaks):
                spectrum.assigned_peaks[nn] = -1
                self.tree.set(nn, column='emitter', value='')

    def show_peak_info(self, parent, spectrum, item_index):
        self.item_index = item_index
        if self.PeakInformationSubwindow is not None:
            self.PeakInformationSubwindow.focus()
            self._update_peakinfo(spectrum)
            self.emissionslist_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._select_CB_assigned(spectrum))
            self.B_accept_emission.configure(command=lambda : self.confirm_emission_assignment(spectrum))
            self.B_cancel_emission.configure(command=lambda : self.cancel_emission_assignment(spectrum))
        else:
            self.PeakInformationSubwindow = tk.Toplevel(parent)
            self.PeakInformationSubwindow.title('Peak info')
            self.PeakInformationSubwindow.resizable(False, False)
            self.PeakInformationSubwindow.geometry(f'+{parent.winfo_rootx()}+{parent.winfo_rooty()}')
            mframe = tk.Frame(self.PeakInformationSubwindow)

            localhintlabel = tk.Label(mframe, text='', anchor=tk.W)

            datapeak = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='peak info'), relief='solid', bd=2, padx=4, pady=4)

            tk.Label(datapeak, text='channel:', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
            tk.Label(datapeak, text='energy:', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
            tk.Label(datapeak, text='net area:', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
            tk.Label(datapeak, text='coincidence:', anchor=tk.W).grid(row=3, column=0, sticky=tk.W)
            tk.Label(datapeak, text='escape from:', anchor=tk.W).grid(row=4, column=0, sticky=tk.W)
            
            self.channel_F = tk.Label(datapeak, text='', anchor=tk.W)
            self.channel_F.grid(row=0, column=1, sticky=tk.W, padx=8)
            self.energy_F = tk.Label(datapeak, text='', anchor=tk.W)
            self.energy_F.grid(row=1, column=1, sticky=tk.W, padx=8)
            self.netarea_F = tk.Label(datapeak, text='', anchor=tk.W)
            self.netarea_F.grid(row=2, column=1, sticky=tk.W, padx=8)
            self.coincidence_F = tk.Label(datapeak, text='', anchor=tk.W, width=60)
            self.coincidence_F.grid(row=3, column=1, sticky=tk.W, padx=8)
            self.escape_F = tk.Label(datapeak, text='', anchor=tk.W, width=60)
            self.escape_F.grid(row=4, column=1, sticky=tk.W, padx=8)


            datapeak.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

            peakid = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='identity'), relief='solid', bd=2, padx=4, pady=4)
            tk.Label(peakid, text='emission', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
            self.emissionslist_CB = gui_things.Combobox(peakid, state='readonly', width=18)
            self.emissionslist_CB['values'] = []#
            self.emissionslist_CB.grid(row=0, column=1, columnspan=2, padx=5)
            self.how_many_suspects = tk.Label(peakid, text='(0)')
            self.how_many_suspects.grid(row=0, column=3, sticky=tk.W)

            nn = 2
            width=10

            tk.Label(peakid, text='EMITTER', width=width, anchor=tk.W).grid(row=nn, column=0, rowspan=2, sticky=tk.W)
            tk.Label(peakid, text='isotope', width=width).grid(row=nn, column=1, sticky=tk.W)
            tk.Label(peakid, text='Eγ / keV', width=width).grid(row=nn, column=2, sticky=tk.W)
            tk.Label(peakid, text='COIfree', width=width).grid(row=nn, column=3, sticky=tk.W)
            tk.Label(peakid, text='γ-yield / %', width=width).grid(row=nn, column=4, sticky=tk.W)

            nn += 1

            self.Eisotope_F = tk.Label(peakid, text='', width=width)
            self.Eisotope_F.grid(row=nn, column=1, sticky=tk.W)
            self.Eenergy_F = tk.Label(peakid, text='', width=width)
            self.Eenergy_F.grid(row=nn, column=2, sticky=tk.W)
            self.ECOI_F = tk.Label(peakid, text='', width=width)
            self.ECOI_F.grid(row=nn, column=3, sticky=tk.W)
            self.Eyield_F = tk.Label(peakid, text='', width=width)
            self.Eyield_F.grid(row=nn, column=4, sticky=tk.W)

            peakid.grid(row=1, column=0, sticky=tk.NW)

            self._true_color, self._false_color = '#FFFFFF', '#ff474c'

            buttonframe = tk.Frame(mframe)

            logo_confirm = tk.PhotoImage(data=gui_things.PL_check)
            self.B_accept_emission = gui_things.Button(buttonframe, image=logo_confirm, hint='Confirm emission assignment!', hint_destination=localhintlabel, command=lambda : self.confirm_emission_assignment(spectrum))
            self.B_accept_emission.grid(row=0, column=0)
            self.B_accept_emission.image = logo_confirm

            logo_cancel = tk.PhotoImage(data=gui_things.PL_none)
            self.B_cancel_emission = gui_things.Button(buttonframe, image=logo_cancel, hint='Cancel emission assignment!', hint_destination=localhintlabel, command=lambda : self.cancel_emission_assignment(spectrum))
            self.B_cancel_emission.grid(row=0, column=1)
            self.B_cancel_emission.image = logo_cancel

            buttonframe.grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)

            localhintlabel.grid(row=3, column=0, columnspan=2, sticky=tk.EW)

            mframe.pack(anchor=tk.NW, padx=5, pady=5)

            self._update_peakinfo(spectrum)

            self.emissionslist_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._select_CB_assigned(spectrum))

            self.PeakInformationSubwindow.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.PeakInformationSubwindow))

    def confirm_emission_assignment(self, spectrum):
        if self.emissionslist_CB.get() != '':
            idx = self.emissionslist_CB['values'].index(self.emissionslist_CB.get())
            spectrum.assigned_peaks[self.item_index] = idx
            self.tree.set(self.item_index, column='emitter', value=spectrum.suspected_peaks[self.item_index][idx].emission)

    def cancel_emission_assignment(self, spectrum):
        self.emissionslist_CB.set('')
        spectrum.assigned_peaks[self.item_index] = -1
        self.tree.set(self.item_index, column='emitter', value='')
        self._update_peakinfo(spectrum)

    def on_closing(self, window):
        if window == self.SpectrumProfileSubwindow:
            self.SpectrumProfileSubwindow.destroy()
            self.SpectrumProfileSubwindow = None
        elif window == self.SpectrumPlotSubwindow:
            self.SpectrumPlotSubwindow.destroy()
            self.SpectrumPlotSubwindow = None
        else:
            self.PeakInformationSubwindow.destroy()
            self.PeakInformationSubwindow = None

    def _select_CB_assigned(self, spectrum):
        index = self.emissionslist_CB['values'].index(self.emissionslist_CB.get())
        infos = spectrum.suspected_peaks[self.item_index][index]
        self._update_assignedinfo(infos)

    def _update_peakinfo(self, spectrum):
        line = spectrum.peak_list[self.item_index]
        self.channel_F.configure(text=f'{line[0]:.2f}')
        self.energy_F.configure(text=f'{line[2]:.2f} keV')
        self.netarea_F.configure(text=f'{line[4]:.1f} ({line[5]:.1f}) [{line[5]/line[4]*100:.2f} %], count rate: {line[4]/spectrum.live_time:.2f} s⁻¹')

        coincidence = spectrum.check_for_coincidence(line[2], comp_net_area=line[4])
        singleescape, doubleescape = spectrum.check_for_escapes(line[2], peakthreshold=line[4])

        self.coincidence_F.configure(text=', '.join([f"{con[0]:.1f} + {con[1]:.1f}" for con in coincidence]))
        self.escape_F.configure(text=', '.join([f"{en:.1f} (SE)" for en in singleescape] + [f"{en:.1f} (DE)" for en in doubleescape]))

        self.emissionslist_CB['values'] = [item.emission for item in spectrum.suspected_peaks[self.item_index]]
        if spectrum.assigned_peaks[self.item_index] > -1:
            set_text = self.emissionslist_CB['values'][spectrum.assigned_peaks[self.item_index]]
        else:
            set_text = ''    
        self.emissionslist_CB.set(set_text)
        self.how_many_suspects.configure(text=f'({len(spectrum.suspected_peaks[self.item_index])})')

        if spectrum.assigned_peaks[self.item_index] != -1:
            infos = spectrum.suspected_peaks[self.item_index][spectrum.assigned_peaks[self.item_index]]
        else:
            infos = None

        self._update_assignedinfo(infos)

    def _update_assignedinfo(self, infos):
        if infos is not None:
            self.Eisotope_F.configure(text=f'{infos.target}')
            self.Eenergy_F.configure(text=f'{infos.energy:.1f}')
            self.ECOI_F.configure(text=str(bool(infos.line["COIfree"])))
            self.Eyield_F.configure(text=self.recvalues(infos.line["yield"],'gy'))
        else:
            self.Eisotope_F.configure(text='')
            self.Eenergy_F.configure(text='')
            self.ECOI_F.configure(text='')
            self.Eyield_F.configure(text='')

    def recvalues(self, value, par):
        none = (lambda x : np.nan, '.2f')
        parameters = {'Q0':(lambda x : '20', '.2f'), 'Er':(lambda x : '50', '.2f'), 'k0':(lambda x : '5', '.2f'), 'gy':(lambda x : str(x), '.3f')}
        opt = parameters.get(par, none)
        try:
            value = float(value)
            return format(value,opt[1])
        except ValueError:
            value = opt[0](value)
            rec = ' (NR)'
            if par == 'gy':
                rec = ''
            return f'{value}{rec}'


class DetectordatabaseWindow:
    def __init__(self, parent, M, title):
        self.detectormodify_window = None
        m_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=title), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='currently available detectors', anchor=tk.W).pack(anchor=tk.W)

        detector_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'detectors')) if filename.lower().endswith('.dec')]

        self.detector_LB = gui_things.ScrollableListbox(m_frame, width=45, height=15, data=detector_list)
        self.detector_LB.pack(expand=True, fill=tk.X)

        f_buttons = tk.Frame(m_frame)

        logo_adddetector = tk.PhotoImage(data=gui_things.PL_plussign)
        B_adddetector = gui_things.Button(f_buttons, image=logo_adddetector, hint='add a new detector', hint_destination=M.hintlabel, command=lambda : self.add_detector(m_frame, M))
        B_adddetector.pack(side=tk.LEFT)
        B_adddetector.image = logo_adddetector

        logo_modifydetector = tk.PhotoImage(data=gui_things.PL_ggear)
        B_modifydetector = gui_things.Button(f_buttons, image=logo_modifydetector, hint='modify detector', hint_destination=M.hintlabel, command=lambda : self.modify_detector(m_frame, M))
        B_modifydetector.pack(side=tk.LEFT)
        B_modifydetector.image = logo_modifydetector

        logo_deletedetector = tk.PhotoImage(data=gui_things.PL_none)
        B_deletedetector = gui_things.Button(f_buttons, image=logo_deletedetector, hint='delete detector', hint_destination=M.hintlabel, command=lambda : self.delete_detector(m_frame, M))
        B_deletedetector.pack(side=tk.LEFT)
        B_deletedetector.image = logo_deletedetector

        f_buttons.pack(anchor=tk.W)

        m_frame.pack(padx=5, pady=5)

    def delete_detector(self, parent, M):
        detname = self.detector_LB.get_selection()

        if self.detectormodify_window is not None:
            try:
                self.detectormodify_window.destroy()
            except:
                pass

        if detname is not None:
            if messagebox.askyesno(title='Delete detector', message=f'\nAre you sure to delete {detname} detector?\n', parent=parent):
                os.remove(os.path.join(os.path.join('data', 'detectors'),f'{detname}.dec'))

                detector_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'detectors')) if filename.lower().endswith('.dec')]
                self.detector_LB._update(detector_list)
                M.hintlabel.configure(text=f'detector {detname} deleted')
        else:
            M.hintlabel.configure(text='no detector is selected')

    def add_detector(self, parent, M):
        if self.detectormodify_window is not None:
            try:
                self.detectormodify_window.destroy()
            except:
                pass
        self.detectmodification_form(parent, M)

    def modify_detector(self, parent, M):
        filename = self.detector_LB.get_selection()
        if filename is not None:
            if self.detectormodify_window is not None:
                try:
                    self.detectormodify_window.destroy()
                except:
                    pass
            self.detectmodification_form(parent, M, naaobject.Detector(f'{filename}.dec'))
        else:
            M.hintlabel.configure(text='no detector is selected')

    def detectmodification_form(self, parent, M, detector=None):
        self.detectormodify_window = tk.Toplevel(parent)
        try:
            title = f'Modify detector ({detector.name})'
        except AttributeError:
            title = 'New detector'
        self.detectormodify_window.title(title)
        self.detectormodify_window.resizable(False, False)
        self.detectormodify_window.hintlabel = tk.Label(self.detectormodify_window, text='', anchor=tk.W)
        tk.Label(self.detectormodify_window, text='detector name', width=20, anchor=tk.W).grid(row=0, column=0, sticky=tk.W, padx=5)
        tk.Label(self.detectormodify_window, text='relative efficiency / %', anchor=tk.W).grid(row=1, column=0, sticky=tk.W, padx=5)
        tk.Label(self.detectormodify_window, text='resolution at 1332 / keV', anchor=tk.W).grid(row=2, column=0, sticky=tk.W, padx=5)
        tk.Label(self.detectormodify_window, text='detector type', anchor=tk.W).grid(row=3, column=0, sticky=tk.W, padx=5)
        tk.Label(self.detectormodify_window, text='crystal diameter / mm', anchor=tk.W).grid(row=4, column=0, sticky=tk.W, padx=5)
        tk.Label(self.detectormodify_window, text='μ / 1', anchor=tk.W).grid(row=6, column=0, sticky=tk.W, padx=5)
        tk.Label(self.detectormodify_window, text='x', anchor=tk.W).grid(row=5, column=1)
        tk.Label(self.detectormodify_window, text='u(x)', anchor=tk.W).grid(row=5, column=2)
        
        self.detectorname_F = gui_things.Entry(self.detectormodify_window, width=25)
        self.detectorname_F.grid(row=0, column=1, columnspan=2, sticky=tk.EW)
        F_font = self.detectorname_F.cget('font')
        try:
            name_text = detector.name
        except AttributeError:
            name_text = 'new detector'
        self.detectorname_F.delete(0, tk.END)
        self.detectorname_F.insert(0, name_text)

        self.detectorefficiency_F = gui_things.Entry(self.detectormodify_window, width=25, font=F_font)
        self.detectorefficiency_F.grid(row=1, column=1, columnspan=2, sticky=tk.EW)
        try:
            relefficiency_text = detector.relative_efficiency
        except AttributeError:
            relefficiency_text = '0'
        self.detectorefficiency_F.delete(0, tk.END)
        self.detectorefficiency_F.insert(0, relefficiency_text)

        self.detectorresolution_F = gui_things.Entry(self.detectormodify_window, width=25, font=F_font)
        self.detectorresolution_F.grid(row=2, column=1, columnspan=2, sticky=tk.EW)
        try:
            resolution_text = detector.resolution
        except AttributeError:
            resolution_text = '0'
        self.detectorresolution_F.delete(0, tk.END)
        self.detectorresolution_F.insert(0, resolution_text)

        self.detectortype_F = gui_things.Entry(self.detectormodify_window, width=25, font=F_font)
        self.detectortype_F.grid(row=3, column=1, columnspan=2, sticky=tk.EW)
        try:
            type_text = detector.detector_type
        except AttributeError:
            type_text = 'unknown'
        self.detectortype_F.delete(0, tk.END)
        self.detectortype_F.insert(0, type_text)

        self.detectordiameter_F = gui_things.Entry(self.detectormodify_window, width=25, font=F_font)
        self.detectordiameter_F.grid(row=4, column=1, columnspan=2, sticky=tk.EW)
        try:
            diameter_text = detector.diameter
        except AttributeError:
            diameter_text = '0'
        self.detectordiameter_F.delete(0, tk.END)
        self.detectordiameter_F.insert(0, diameter_text)

        self.detectormu_F = gui_things.Spinbox(self.detectormodify_window, width=10, font=F_font)
        self.detectormu_F.grid(row=6, column=1)
        try:
            mu_text = detector.mu
        except AttributeError:
            mu_text = 0.0
        self.detectormu_F.delete(0, tk.END)
        self.detectormu_F.insert(0, mu_text)

        self.detector_unc_mu_F = gui_things.Spinbox(self.detectormodify_window, width=10, font=F_font)
        self.detector_unc_mu_F.grid(row=6, column=2)
        try:
            u_mu_text = detector.u_mu
        except AttributeError:
            u_mu_text = 0.0
        self.detector_unc_mu_F.delete(0, tk.END)
        self.detector_unc_mu_F.insert(0, u_mu_text)

        logo_confirmchanges = tk.PhotoImage(data=gui_things.PL_save)
        B_confirmchanges = gui_things.Button(self.detectormodify_window, image=logo_confirmchanges, hint='confirm changes to detector', hint_destination=self.detectormodify_window.hintlabel, command=lambda : self.save_detector(self.detectormodify_window.hintlabel))
        B_confirmchanges.grid(row=7, column=0, columnspan=4, pady=5)
        B_confirmchanges.image = logo_confirmchanges

        self.detectormodify_window.hintlabel.grid(row=8, column=0, columnspan=4, sticky=tk.W)

    def save_detector(self, Shintlabel):
        detector_name = self.detectorname_F.get()

        valid_numbers = True
        try:
            xx = float(self.detectormu_F.get())
        except:
            valid_numbers = False
        try:
            ux = float(self.detector_unc_mu_F.get())
        except:
            valid_numbers = False

        if detector_name.replace(' ', '') != '' and valid_numbers:

            #prepare file and save
            with open(os.path.join(os.path.join('data','detectors'),f'{detector_name}.dec'), 'w') as f:
                f.write(f'mu <#> {xx} {ux}\n')
                f.write(f'refficiency <#> {self.detectorefficiency_F.get()}\n')
                f.write(f'FWHM <#> {self.detectorresolution_F.get()}\n')
                f.write(f'type <#> {self.detectortype_F.get()}\n')
                f.write(f'diameter <#> {self.detectordiameter_F.get()}\n')

            #update list
            detector_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'detectors')) if filename.lower().endswith('.dec')]
            self.detector_LB._update(detector_list)
            self.detectormodify_window.title()
            title = f'Modify detector ({detector_name})'
            self.detectormodify_window.title(title)
            Shintlabel.configure(text=f'detector {detector_name} saved')
        else:
            Shintlabel.configure(text='invalid name or μ data')


class SourcedatabaseWindow:
    def __init__(self, parent, M, title):
        self.sourcemodify_window = None
        m_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=title), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='currently available sources', anchor=tk.W).pack(anchor=tk.W)
        source_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'sources')) if filename.lower().endswith('.sce')]

        self.source_LB = gui_things.ScrollableListbox(m_frame, width=45, height=15, data=source_list)
        self.source_LB.pack(expand=True, fill=tk.X)

        f_buttons = tk.Frame(m_frame)

        logo_addsource = tk.PhotoImage(data=gui_things.PL_plussign)
        B_addsource = gui_things.Button(f_buttons, image=logo_addsource, hint='add a new source', hint_destination=M.hintlabel, command=lambda : self.add_source(m_frame, M))
        B_addsource.pack(side=tk.LEFT)
        B_addsource.image = logo_addsource

        logo_modifysource = tk.PhotoImage(data=gui_things.PL_ggear)
        B_modifysource = gui_things.Button(f_buttons, image=logo_modifysource, hint='modify source', hint_destination=M.hintlabel, command=lambda : self.modify_source(m_frame, M))
        B_modifysource.pack(side=tk.LEFT)
        B_modifysource.image = logo_modifysource

        logo_deletesource = tk.PhotoImage(data=gui_things.PL_none)
        B_deletesource = gui_things.Button(f_buttons, image=logo_deletesource, hint='delete source', hint_destination=M.hintlabel, command=lambda : self.delete_source(m_frame, M))
        B_deletesource.pack(side=tk.LEFT)
        B_deletesource.image = logo_deletesource

        logo_mergesources = tk.PhotoImage(data=gui_things.PL_convergence)
        B_mergesources = gui_things.Button(f_buttons, image=logo_mergesources, hint='merge sources', hint_destination=M.hintlabel, command=lambda : self.merge_source(m_frame, M))
        B_mergesources.pack(side=tk.LEFT)
        B_mergesources.image = logo_mergesources

        f_buttons.pack(anchor=tk.W)

        m_frame.pack(padx=5, pady=5)

    def merge_source(self, parent, M):
        if self.sourcemodify_window is not None:
            try:
                self.sourcemodify_window.destroy()
            except:
                pass
        self.merge_source_form(parent, M)

    def delete_source(self, parent, M):
        sourcename = self.source_LB.get_selection()
        if self.source_LB.get_selection() is not None:
            if self.sourcemodify_window is not None:
                try:
                    self.sourcemodify_window.destroy()
                except:
                    pass
            if messagebox.askyesno(title='Delete source', message=f'\nAre you sure to delete {sourcename} source?\n', parent=parent):
                os.remove(os.path.join(os.path.join('data', 'sources'),f'{sourcename}.sce'))

                source_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'sources')) if filename.lower().endswith('.sce')]
                self.source_LB._update(source_list)
                M.hintlabel.configure(text='source deleted')
        else:
            M.hintlabel.configure(text='no source is selected')

    def add_source(self, parent, M):
        if self.sourcemodify_window is not None:
            try:
                self.sourcemodify_window.destroy()
            except:
                pass
        self.sourcemodification_form(parent, M)

    def modify_source(self, parent, M):
        filename = self.source_LB.get_selection()
        if filename is not None:
            if self.sourcemodify_window is not None:
                try:
                    self.sourcemodify_window.destroy()
                except:
                    pass
            self.sourcemodification_form(parent, M, naaobject.GammaSource(f'{filename}.sce'))
        else:
            M.hintlabel.configure(text='no source is selected')

    def display_dataframe(self):
        req_infos = ['energy', 'emitter','activity', 'yield','t_half','COIfree']

        if self.sourcedata.empty:
            return ''
        else:
            part_data = self.sourcedata[req_infos].copy(deep=True)
            part_data.loc[:,'t_half'] = part_data['t_half'] / 86400
            part_data.loc[:,'yield'] = part_data['yield'] * 100
            return '\n'.join([f'{self.formatter_function(float(energy)).ljust(9)}{emitter.ljust(9)}{self.formatter_function(activity).rjust(11)}{self.formatter_function(gyield).rjust(8)}{self.formatter_function(t_half).rjust(11)}{str(COI).rjust(7)}' for energy,emitter,activity,gyield,t_half,COI in zip(*[part_data[i] for i in part_data.columns])])

    def formatter_function(self, x, limit=1e6,fformat='.1f',eformat='.2e'):
        if x > -limit and x < limit:
            return format(x,fformat)
        else:
            return format(x,eformat)

    def sourcemodification_form(self, parent, M, source=None):
        self.sourcemodify_window = tk.Toplevel(parent)
        try:
            title = f'Modify source ({source.name})'
        except AttributeError:
            title = 'New source'
        self.sourcemodify_window.title(title)
        self.sourcemodify_window.resizable(False, False)
        self.sourcemodify_window.hintlabel = tk.Label(self.sourcemodify_window, text='', anchor=tk.W)

        tk.Label(self.sourcemodify_window, text='source name', width=15, anchor=tk.W).grid(row=0, column=0, sticky=tk.W, padx=5)
        tk.Label(self.sourcemodify_window, text='certificate date').grid(row=1, column=0, sticky=tk.W, padx=5)
        tk.Frame(self.sourcemodify_window).grid(row=2, column=0, pady=4)
        tk.Label(self.sourcemodify_window, text='emissions').grid(row=3, column=0, sticky=tk.W, padx=5)

        tk.Label(self.sourcemodify_window, text=f'{"E / keV".ljust(9)}{"emitter".ljust(9)}{"A / Bq".rjust(11)}{"γ / %".rjust(8)}{"t½ / d".rjust(11)}{"COI".rjust(7)}', font=('Courier', 10)).grid(row=4, column=0, columnspan=2, sticky=tk.W)

        self.source_name_F = ttk.Entry(self.sourcemodify_window, width=25)
        self.source_name_F.grid(row=0, column=1, sticky=tk.W)
        F_font = self.source_name_F.cget('font')
        try:
            name_text = source.name
        except AttributeError:
            name_text = 'new source'
        self.source_name_F.delete(0, tk.END)
        self.source_name_F.insert(0, name_text)

        try:
            date_text = source.datetime
        except AttributeError:
            date_text = None

        self.source_date_F = gui_things.DateLabel(self.sourcemodify_window, default_date=date_text, hint='certificate date', hint_destination=self.sourcemodify_window.hintlabel)
        self.source_date_F.grid(row=1, column=1, sticky=tk.W)

        try:
            self.sourcedata = source.data
        except AttributeError:
            self.sourcedata = pd.DataFrame(data={}, columns=['energy','emitter','activity','u_activity','yield','u_yield','t_half','COIfree', 'lambda', 't_half', 'reference'])

        emissions_list = self.display_dataframe()

        self.emissions_text = gui_things.ScrollableText(self.sourcemodify_window, width=56, height=25, data=emissions_list, font=('Courier', 10))
        self.emissions_text.grid(row=7, column=0, columnspan=2, sticky=tk.EW, padx=5)

        f_buttons = tk.Frame(self.sourcemodify_window)
        tk.Label(f_buttons, text='emitter', anchor=tk.W, width=10).grid(row=0, column=0, sticky=tk.W)
        tk.Label(f_buttons, text='activity / Bq').grid(row=0, column=1)
        tk.Label(f_buttons, text='u(activity) / Bq').grid(row=0, column=2)
        tk.Label(f_buttons, text='unit').grid(row=0, column=3)
        
        unit_list = ('s','h','d')
        self.unit_index = 0

        halflife_label = tk.Label(f_buttons, text=f't½ / {unit_list[self.unit_index]}')
        halflife_label.grid(row=0, column=4)

        tk.Frame(f_buttons).grid(row=2, column=0, pady=5)

        tk.Label(f_buttons, text='E / keV', anchor=tk.W, width=10).grid(row=3, column=0, sticky=tk.W)

        tk.Label(f_buttons, text='γ yield / 1').grid(row=3, column=1)
        tk.Label(f_buttons, text='u(γ yield) / 1').grid(row=3, column=2)
        tk.Label(f_buttons, text='COI free').grid(row=3, column=3)

        self.emitter_CB = gui_things.Combobox(f_buttons, width=8, font=F_font)
        self.emitter_CB.grid(row=1, column=0, sticky=tk.W)

        self.nuclear_data = naaobject.nuclear_data()
        self.emission_subdata = pd.DataFrame(data={}, columns=['energy', 'yield', 'COIfree'])
        self.emitter_CB['values'] = list(self.nuclear_data['ref'])
        self.emitter_CB.set('')

        self.activity_F = ttk.Entry(f_buttons, width=15, font=F_font)
        self.activity_F.grid(row=1, column=1)

        self.uactivity_F = ttk.Entry(f_buttons, width=12, font=F_font)
        self.uactivity_F.grid(row=1, column=2)

        B_unit = gui_things.Button(f_buttons, text=f'{unit_list[self.unit_index]}', width=8, command=lambda : self.change_unit(B_unit, unit_list, halflife_label))
        B_unit.grid(row=1, column=3, padx=5)

        self.halflife_F = ttk.Entry(f_buttons, width=15, font=F_font)
        self.halflife_F.grid(row=1, column=4)

        self.energy_CB = gui_things.Combobox(f_buttons, width=8, font=F_font)
        self.energy_CB.grid(row=4, column=0, sticky=tk.W)

        self.yield_F = ttk.Entry(f_buttons, width=11, font=F_font)
        self.yield_F.grid(row=4, column=1)

        self.uyield_F = ttk.Entry(f_buttons, width=9, font=F_font)
        self.uyield_F.grid(row=4, column=2)

        self.checkbox_variable = tk.IntVar(parent)
        COIfree_CBT = gui_things.Checkbutton(f_buttons, hint='', hint_destination=self.sourcemodify_window.hintlabel, variable=self.checkbox_variable)
        self.checkbox_variable.set(0)
        COIfree_CBT.grid(row=4, column=3)

        logo_addemitter = tk.PhotoImage(data=gui_things.PL_ggear)
        B_addemitter = gui_things.Button(f_buttons, image=logo_addemitter, hint='add/modify emitter to source', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.add_modify_emission(self.sourcemodify_window.hintlabel))
        B_addemitter.grid(row=3, column=5, rowspan=2, padx=10)
        B_addemitter.image = logo_addemitter

        logo_deleteemitter = tk.PhotoImage(data=gui_things.PL_none)
        B_deleteemitter = gui_things.Button(f_buttons, image=logo_deleteemitter, hint='delete current emitter from source', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.delete_from_source(self.sourcemodify_window, self.sourcemodify_window.hintlabel, 0))
        B_deleteemitter.grid(row=0, column=6, rowspan=2)
        B_deleteemitter.image = logo_deleteemitter

        logo_deleteemission = tk.PhotoImage(data=gui_things.PL_none)
        B_deleteemission = gui_things.Button(f_buttons, image=logo_deleteemission, hint='delete current emission from source', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.delete_from_source(self.sourcemodify_window, self.sourcemodify_window.hintlabel, 1))
        B_deleteemission.grid(row=3, column=6, rowspan=2)
        B_deleteemission.image = logo_deleteemission

        logo_savesource = tk.PhotoImage(data=gui_things.PL_save)
        B_savesource = gui_things.Button(f_buttons, image=logo_savesource, hint='save source data', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.save_source(self.sourcemodify_window.hintlabel))
        B_savesource.grid(row=5, column=0, columnspan=6, pady=10)
        B_savesource.image = logo_savesource

        f_buttons.grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.sourcemodify_window.hintlabel.grid(row=9, column=0, columnspan=2, sticky=tk.W)

        self.emitter_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_emitter(M))
        self.energy_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_emission(M))

    def save_source(self, Shintlabel):
        source_name = self.source_name_F.get()

        if source_name.replace(' ', '') != '' and not self.sourcedata.empty:

            #prepare file and save
            with open(os.path.join(os.path.join('data','sources'),f'{source_name}.sce'), 'w') as f:
                self.sourcedata['COIfree'] = self.sourcedata['COIfree'].astype(int)
                f.write(f'{self.source_date_F.get_string()}\n')
                f.write(self.sourcedata.to_string(columns=['energy','emitter','activity','u_activity','yield','u_yield','t_half','COIfree'], header=False, index=False, show_dimensions=False, decimal='.'))
            self.sourcedata['COIfree'] = self.sourcedata['COIfree'].astype(bool)

            #update list
            source_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'sources')) if filename.lower().endswith('.sce')]

            self.source_LB._update(source_list)
            Shintlabel.configure(text=f'source {source_name} saved')
        else:
            Shintlabel.configure(text='invalid name or emission data')

    def add_modify_emission(self, Shintlabel, unit_conversions=(1,3600,86400)):
        good_ending, message_text = True, 'successful'
        element_list = ('H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og')
        D_emitter = self.emitter_CB.get()
        try:
            if len(D_emitter.split('-')) == 2 and D_emitter.split('-')[0] in element_list and D_emitter.split('-')[1] != '':
                pass
        except IndexError:
            D_emitter = None
            good_ending, message_text = False, 'element not recognized'
        
        try:
            D_activity = float(self.activity_F.get())
            if D_activity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            D_activity = None
            good_ending, message_text = False, 'invalid activity'

        try:
            D_uactivity = float(self.uactivity_F.get())
            if D_uactivity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            D_uactivity = 0.0
            good_ending, message_text = True, 'activity uncertainty set to 0'
        
        try:
            D_halflife = float(self.halflife_F.get())
            if D_halflife <= 0:
                raise ValueError
            D_halflife = D_halflife * unit_conversions[self.unit_index]
        except (ValueError, TypeError):
            D_halflife = None
            good_ending, message_text = False, 'invalid half-life'
        
        try:
            D_energy = float(self.energy_CB.get())
            if D_energy <= 0:
                raise ValueError
            D_energy = format(D_energy,'.2f')
        except (ValueError, TypeError):
            D_energy = None
            good_ending, message_text = False, 'invalid energy value'
        
        try:
            D_yield = float(self.yield_F.get())
            if not 0 < D_yield <= 1:
                raise ValueError
        except (ValueError, TypeError):
            D_yield = None
            good_ending, message_text = False, 'invalid yield value'

        try:
            D_uyield = float(self.uyield_F.get())
            if not 0 < D_uyield <= 1:
                raise ValueError
        except (ValueError, TypeError):
            D_uyield = 0.0
        self.checkbox_variable.get()

        if good_ending:

            filtT = self.sourcedata['emitter'] == D_emitter

            if np.sum(filtT) == 0:
                self.add_data_to_source(D_energy, D_emitter, D_activity, D_uactivity, D_yield, D_uyield, D_halflife)
            else:
                self.sourcedata.loc[filtT, ['activity']] = D_activity
                self.sourcedata.loc[filtT, ['u_activity']] = D_uactivity
                self.sourcedata.loc[filtT, ['t_half']] = D_halflife

                filtE = self.sourcedata['energy'] == D_energy
                filtToT = filtT & filtE
                if np.sum(filtToT) > 0:
                    self.sourcedata.loc[filtToT, ['yield']] = D_yield
                    self.sourcedata.loc[filtToT, ['u_yield']] = D_uyield
                    self.sourcedata.loc[filtToT, ['COIfree']] = self.checkbox_variable.get()
                else:
                    self.add_data_to_source(D_energy, D_emitter, D_activity, D_uactivity, D_yield, D_uyield, D_halflife)

                self.sourcedata['COIfree'] = self.sourcedata['COIfree'].astype(int).astype(bool)
                self.sourcedata['lambda'] = np.log(2)/self.sourcedata['t_half']

            self.emissions_text._update(self.display_dataframe())

        Shintlabel.configure(text=message_text)

    def add_data_to_source(self, D_energy, D_emitter, D_activity, D_uactivity, D_yield, D_uyield, D_halflife):
        df_new = pd.DataFrame(data=[[D_energy, D_emitter, D_activity, D_uactivity, D_yield, D_uyield, D_halflife, self.checkbox_variable.get(), np.nan, '']], index=None, columns=['energy', 'emitter', 'activity', 'u_activity', 'yield', 'u_yield', 't_half', 'COIfree', 'lambda', 'reference'])
        df_new['COIfree'] = df_new['COIfree'].astype(int).astype(bool)
        df_new['lambda'] = np.log(2)/df_new['t_half']
        df_new['reference'] = [f'{energy} keV {emitter}' for energy, emitter in zip(df_new['energy'], df_new['emitter'])]
        
        if self.sourcedata.empty:
            self.sourcedata = df_new
        else:
            self.sourcedata = pd.concat([self.sourcedata, df_new],verify_integrity=True, sort=False, copy=False, ignore_index=True)
            self.sourcedata.sort_values(by='energy', key=lambda x : [float(i) for i in x], inplace=True, ignore_index=True)

    def select_emitter(self, M, unit_conversions=(1,1/3600,1/86400)):
        dataline = self.sourcedata.loc[self.sourcedata['emitter'] == self.emitter_CB.get(), self.sourcedata.columns]
        if dataline.empty:
            activity, uactivity, t_half = '', '', ''
            self.emission_subdata = dataline[['energy', 'yield', 'u_yield', 'COIfree']]
            t_half = self.nuclear_data.loc[self.nuclear_data['ref'] == self.emitter_CB.get(), ['halflife(Seconds)']]
            t_half = t_half.iloc[0, 0]
        else:
            activity, uactivity, t_half = dataline.iloc[0, 2], dataline.iloc[0, 3], dataline.iloc[0, 6]
            self.emission_subdata = dataline[['energy', 'yield', 'u_yield', 'COIfree']]

        self.activity_F.delete(0, tk.END)
        self.activity_F.insert(0, activity)
        self.uactivity_F.delete(0, tk.END)
        self.uactivity_F.insert(0, uactivity)
        t_half = float(t_half) * unit_conversions[self.unit_index]
        self.halflife_F.delete(0, tk.END)
        self.halflife_F.insert(0, t_half)

        self.energy_CB['values'] = list(self.emission_subdata['energy'])

        #for the moment
        if len(self.energy_CB['values']) > 0:
            self.energy_CB.set(self.energy_CB['values'][0])
            self.select_emission(M)
        else:
            self.energy_CB.set('')
            self.yield_F.delete(0, tk.END)
            self.checkbox_variable.set(0)

    def select_emission(self, M):
        linevalues = self.emission_subdata.loc[self.emission_subdata['energy'] == self.energy_CB.get()]
        yield_value, yield_unc, COIfree_value = linevalues.iloc[0, 1], linevalues.iloc[0, 2], linevalues.iloc[0, 3]
        self.yield_F.delete(0, tk.END)
        self.yield_F.insert(0, yield_value)
        self.uyield_F.delete(0, tk.END)
        self.uyield_F.insert(0, yield_unc)
        self.checkbox_variable.set(int(COIfree_value))

    def change_unit(self, B_unit, unit_list, halflife_label, unit_conversions=(1,1/3600,1/86400)):
        if self.unit_index < len(unit_list) - 1:
            self.unit_index += 1
        else:
            self.unit_index = 0

        B_unit.configure(text=f'{unit_list[self.unit_index]}')
        halflife_label.configure(text=f't½ / {unit_list[self.unit_index]}')

        try:
            newvalue = float(self.halflife_F.get())
            newvalue = newvalue * unit_conversions[self.unit_index] / unit_conversions[self.unit_index - 1]
            self.halflife_F.delete(0, tk.END)
            self.halflife_F.insert(0, newvalue)
        except ValueError:
            pass

    def delete_from_source(self, parent, Shintlabel, switch=0):
        D_emitter = self.emitter_CB.get()
        try:
            D_energy = float(self.energy_CB.get())
            if D_energy <= 0:
                raise ValueError
            D_energy = format(D_energy,'.2f')
        except ValueError:
            D_energy = ''

        if switch == 0:
            total_filter = self.sourcedata['emitter'] == D_emitter
            messagge_areyousure = f'\nAre you sure to delete\n{int(np.sum(total_filter))} data for {D_emitter}?'
        else:
            filtT = self.sourcedata['emitter'] == D_emitter
            filtE = self.sourcedata['energy'] == D_energy
            total_filter = filtT & filtE
            messagge_areyousure = f'\nAre you sure to delete\nemission {D_energy} kev of {D_emitter}?'

        if np.sum(total_filter) > 0:
            if messagebox.askyesno(title='Delete data from source', message=messagge_areyousure, parent=parent):
                self.sourcedata = self.sourcedata[~total_filter]
                self.sourcedata.sort_values(by='energy', key=lambda x : [float(i) for i in x], inplace=True, ignore_index=True)
                self.emissions_text._update(self.display_dataframe())
                message_text = f'{np.sum(total_filter)} data deleted'
        else:
            message_text = 'No data selected'
            
        Shintlabel.configure(text=message_text)

    def merge_source_form(self, parent, M):
        self.sources_list = []
        self.sourcedata = pd.DataFrame(data={}, columns=['energy','emitter','activity','yield','t_half','COIfree', 'lambda', 't_half', 'reference'])
        self.sourcemodify_window = tk.Toplevel(parent)
        self.sourcemodify_window.title('Merge sources')
        self.sourcemodify_window.resizable(False, False)
        self.sourcemodify_window.hintlabel = tk.Label(self.sourcemodify_window, text='', anchor=tk.W)
        tk.Label(self.sourcemodify_window, text='select source', width=15, anchor=tk.W).grid(row=0, column=0, sticky=tk.W, padx=5)
        tk.Frame(self.sourcemodify_window).grid(row=1, column=0, pady=4)
        tk.Label(self.sourcemodify_window, text='sources to merge').grid(row=2, column=0, sticky=tk.W, padx=5)
        self.merge_source_LB = gui_things.ScrollableListbox(self.sourcemodify_window, width=45, height=8, data=[si.name for si in self.sources_list])
        self.merge_source_LB.grid(row=3, column=0, columnspan=2, sticky=tk.EW)
        tk.Label(self.sourcemodify_window, text='reference date').grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)

        lat_but = tk.Frame(self.sourcemodify_window)
        logo_moveup_iteminlist = tk.PhotoImage(data=gui_things.PL_aup)
        B_moveup_iteminlist = gui_things.Button(lat_but, image=logo_moveup_iteminlist, hint='move source up in list', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.moveupanddown_inlist(self.sourcemodify_window.hintlabel, direction=0))
        B_moveup_iteminlist.pack()
        B_moveup_iteminlist.image = logo_moveup_iteminlist
        
        logo_movedown_iteminlist = tk.PhotoImage(data=gui_things.PL_adown)
        B_movedown_iteminlist = gui_things.Button(lat_but, image=logo_movedown_iteminlist, hint='move source down in list', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.moveupanddown_inlist(self.sourcemodify_window.hintlabel, direction=1))
        B_movedown_iteminlist.pack()
        B_movedown_iteminlist.image = logo_movedown_iteminlist

        logo_delete_iteminlist = tk.PhotoImage(data=gui_things.PL_none)
        B_delete_iteminlist = gui_things.Button(lat_but, image=logo_delete_iteminlist, hint='delete selected source', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.deleteitem_inlist(self.sourcemodify_window))
        B_delete_iteminlist.pack()
        B_delete_iteminlist.image = logo_delete_iteminlist

        lat_but.grid(row=3, column=2, sticky=tk.NS)
        
        tf = tk.Frame(self.sourcemodify_window)
        self.reference_date_variable = tk.IntVar(self.sourcemodify_window)
        RB1 = tk.Radiobutton(tf, text='from a source', variable=self.reference_date_variable, value=0)
        RB1.grid(row=0, column=0)
        self.source_name_CB = gui_things.Combobox(tf, width=35, state='readonly')
        self.source_name_CB.grid(row=1, column=0)
        self.source_name_CB['values'] = [si.name for si in self.sources_list]
        RB2 = tk.Radiobutton(tf, text='manual', variable=self.reference_date_variable, value=1)
        RB2.grid(row=0, column=1)
        F_font = self.source_name_CB.cget('font')

        self.source_reference_date_CB = gui_things.DateLabel(tf, hint_destination=self.sourcemodify_window.hintlabel)
        self.source_reference_date_CB.grid(row=1, column=1)
        self.reference_date_variable.set(0)

        tk.Label(tf, text='manage duplicates').grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.duplicates_variable = tk.IntVar(self.sourcemodify_window)

        RBOPZ1 = tk.Radiobutton(tf, text='based on source order', variable=self.duplicates_variable, value=0)
        RBOPZ1.grid(row=3, column=0)
        RBOPZ2 = tk.Radiobutton(tf, text='delete all', variable=self.duplicates_variable, value=1)
        RBOPZ2.grid(row=3, column=1)

        tf.grid(row=5, column=0, columnspan=3, sticky=tk.EW, padx=5)

        self.duplicates_variable.set(0)

        tk.Label(self.sourcemodify_window, text='merged source name', width=20, anchor=tk.W).grid(row=8, column=0, sticky=tk.W, padx=5)

        self.newnamesource_F = ttk.Entry(self.sourcemodify_window, width=35, font=F_font)
        self.newnamesource_F.grid(row=8, column=1, sticky=tk.EW, pady=10)
        self.newnamesource_F.delete(0, tk.END)
        self.newnamesource_F.insert(0, 'merged_source')

        self.selectionsource_CB = gui_things.Combobox(self.sourcemodify_window, width=35, state='readonly', font=F_font)
        self.selectionsource_CB.grid(row=0, column=1, sticky=tk.W)
        source_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'sources')) if filename.lower().endswith('.sce')]
        self.selectionsource_CB['values'] = source_list
        self.selectionsource_CB.set('')

        logo_addsource_for_merging = tk.PhotoImage(data=gui_things.PL_plussign)
        B_addsource_for_merging = gui_things.Button(self.sourcemodify_window, image=logo_addsource_for_merging, hint='add source to merge list', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.add_source_to_mergesourcelist(self.sourcemodify_window.hintlabel))
        B_addsource_for_merging.grid(row=0, column=2, padx=10)
        B_addsource_for_merging.image = logo_addsource_for_merging

        cff = tk.Frame(self.sourcemodify_window)

        logo_mergit = tk.PhotoImage(data=gui_things.PL_save)
        B_mergit = gui_things.Button(cff, image=logo_mergit, hint='merge sources', hint_destination=self.sourcemodify_window.hintlabel, command=lambda : self.merge_sources(self.sourcemodify_window.hintlabel))
        B_mergit.pack()
        B_mergit.image = logo_mergit

        cff.grid(row=9, column=0, columnspan=3, sticky=tk.EW, pady=5)

        self.sourcemodify_window.hintlabel.grid(row=10, column=0, columnspan=3, sticky=tk.W)

    def moveupanddown_inlist(self, Shintlabel, direction=0):
        try:
            move_index = self.merge_source_LB.curselection()[0]
        except IndexError:
            move_index = None
        if move_index is not None:
            if direction == 0:
                if move_index != 0:
                    self.sources_list.insert(move_index-1, self.sources_list.pop(move_index))
            else:
                self.sources_list.insert(move_index+1, self.sources_list.pop(move_index))
            self.merge_source_LB._update([si.name for si in self.sources_list])
        else:
            Shintlabel.configure(text='source is not selected')

    def deleteitem_inlist(self, parent):
        if self.merge_source_LB.get_selection() is not None:
            if messagebox.askyesno(title='Undo selection', message=f'\nAre you sure to unselect the gamma source: {self.merge_source_LB.get_selection()}?\n', parent=parent):
                self.sources_list.pop(self.merge_source_LB.curselection()[0])
                source_names = [si.name for si in self.sources_list]
                self.merge_source_LB._update(source_names)
                self.source_name_CB['values'] = source_names
                self.source_name_CB.set('')
        else:
            parent.hintlabel.configure(text='source is not selected')

    def move_reference_date(self, source, reference_date):
        decay = reference_date - source.datetime
        sdata = source.data.copy()
        sdata['activity'] = sdata['activity'] * np.exp(-sdata['lambda'] * decay.total_seconds())
        activity_filter = (0 < sdata['activity']) & (sdata['activity'] < np.inf)
        return sdata.loc[activity_filter]

    def merge_sources(self, Shintlabel):
        proceed = True
        if len(self.sources_list) < 2:
            Shintlabel.configure(text='few sources to merge')
            proceed = False
        elif self.reference_date_variable.get() == 0 and self.source_name_CB.get() == '':
            Shintlabel.configure(text='reference date not specified')
            proceed = False
        elif self.newnamesource_F.get().replace(' ','') == '':
            Shintlabel.configure(text='invalid name')
            proceed = False

        if proceed:
            if self.reference_date_variable.get() == 0:
                sourceslist = [si.name for si in self.sources_list]
                idx = sourceslist.index(self.source_name_CB.get())
                reference_date = self.sources_list[idx].datetime
            else:
                reference_date = self.source_reference_date_CB.get()
            sourceslist = [self.move_reference_date(si, reference_date) for si in self.sources_list]
            sourceslist = pd.concat(sourceslist, verify_integrity=True, sort=False, copy=False, ignore_index=True)
            if self.duplicates_variable.get() == 0:
                sourceslist.drop_duplicates(subset=['reference'], keep='first', inplace=True)
            else:
                sourceslist.drop_duplicates(subset=['reference'], keep=False, inplace=True)
            sourceslist.sort_values(by='energy', key=lambda x : [float(i) for i in x], inplace=True, ignore_index=True)

            if not sourceslist.empty:

                #prepare file and save
                with open(os.path.join(os.path.join('data','sources'),f'{self.newnamesource_F.get()}.sce'), 'w') as f:
                    sourceslist['COIfree'] = sourceslist['COIfree'].astype(int)
                    f.write(f'{reference_date.strftime("%d/%m/%Y %H:%M:%S")}\n')
                    f.write(sourceslist.to_string(columns=['energy','emitter','activity','u_activity','yield','u_yield','t_half','COIfree'], header=False, index=False, show_dimensions=False, decimal='.'))
                sourceslist['COIfree'] = sourceslist['COIfree'].astype(bool)

                #update list
                source_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'sources')) if filename.lower().endswith('.sce')]

                self.source_LB._update(source_list)
                Shintlabel.configure(text=f'source {self.newnamesource_F.get()} saved')
            else:
                Shintlabel.configure(text='no emission data')

    def add_source_to_mergesourcelist(self, Shintlabel):
        if self.selectionsource_CB.get() != '':
            source = naaobject.GammaSource(f'{self.selectionsource_CB.get()}.sce')
            if source.name not in [si.name for si in self.sources_list]:
                self.sources_list.append(source)
                self.merge_source_LB._update([si.name for si in self.sources_list])
                self.source_name_CB['values'] = [si.name for si in self.sources_list]
                self.source_name_CB.set('')
            else:
                Shintlabel.configure(text='source already in list')


class MaterialdatabaseWindow:
    # only one subwindow open at a time
    def __init__(self, parent, M, title):
        self.matmodify_window = None
        m_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=title), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='currently available materials', anchor=tk.W).pack(anchor=tk.W)
        material_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'samples')) if filename.lower().endswith('.csv')]

        self.material_LB = gui_things.ScrollableListbox(m_frame, width=45, height=15, data=material_list)
        self.material_LB.pack(expand=True, fill=tk.X)

        f_buttons = tk.Frame(m_frame)

        logo_addmaterial = tk.PhotoImage(data=gui_things.PL_plussign)
        B_addmaterial = gui_things.Button(f_buttons, image=logo_addmaterial, hint='add a new material', hint_destination=M.hintlabel, command=lambda : self.add_material(m_frame, M))
        B_addmaterial.pack(side=tk.LEFT)
        B_addmaterial.image = logo_addmaterial

        logo_modifymaterial = tk.PhotoImage(data=gui_things.PL_ggear)
        B_modifymaterial = gui_things.Button(f_buttons, image=logo_modifymaterial, hint='modify material', hint_destination=M.hintlabel, command=lambda : self.modify_material(m_frame, M))
        B_modifymaterial.pack(side=tk.LEFT)
        B_modifymaterial.image = logo_modifymaterial

        logo_deletematerial = tk.PhotoImage(data=gui_things.PL_none)
        B_deletematerial = gui_things.Button(f_buttons, image=logo_deletematerial, hint='delete material', hint_destination=M.hintlabel, command=lambda : self.delete_material(m_frame, M))
        B_deletematerial.pack(side=tk.LEFT)
        B_deletematerial.image = logo_deletematerial

        f_buttons.pack(anchor=tk.W)

        m_frame.pack(padx=5, pady=5)

    def _as_text_display(self, certificate,preamble='Elemental components of the sample listed in decreasing value of mass fraction, relative uncertainty (k=1) is reported while non certified values are indicated as "nan"\n\n', header=['El','x / g g⁻¹','urx / %'],unit=None,include_header=True):
            spaces = [4,11,11]
            if include_header:
                head = f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}\n'
            else:
                head = ''
            lines = sorted([(key,value[0],value[1]/value[0]) for key,value in certificate.items()], key=lambda x:x[1], reverse=True)
            if unit == 'ppm':
                astext = '\n'.join([f'{line[0].ljust(spaces[0]," ")}{format(line[1]*1000000,".3e").rjust(spaces[1]," ")}{format(line[2]*100,".1f").rjust(spaces[2]," ")}' for line in lines])
                if include_header:
                    header[1] = 'x / ppm'
            else:
                astext = '\n'.join([f'{line[0].ljust(spaces[0]," ")}{format(line[1],".3e").rjust(spaces[1]," ")}{format(line[2]*100,".1f").rjust(spaces[2]," ")}' for line in lines])
                if include_header:
                    header[1] = 'x / g g⁻¹'
            return preamble+head+astext

    def delete_material(self, parent, M):
        matname = self.material_LB.get_selection()
        if matname is not None:
            if messagebox.askyesno(title='Delete material', message=f'\nAre you sure to delete {matname} material?\n', parent=parent):
                os.remove(os.path.join(os.path.join('data', 'samples'),f'{matname}.csv'))

                material_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'samples')) if filename.lower().endswith('.csv')]
                self.material_LB._update(material_list)
                M.hintlabel.configure(text=f'material {matname} deleted')
        else:
            M.hintlabel.configure(text='no material is selected')

    def add_material(self, parent, M):
        if self.matmodify_window is not None:
            try:
                self.matmodify_window.destroy()
            except:
                pass
        self.matmodification_form(parent, M)

    def modify_material(self, parent, M):
        filename = self.material_LB.get_selection()
        if filename is not None:
            if self.matmodify_window is not None:
                try:
                    self.matmodify_window.destroy()
                except:
                    pass
            self.matmodification_form(parent, M, naaobject.Material(f'{filename}.csv'))
        else:
            M.hintlabel.configure(text='no material is selected')

    def matmodification_form(self, parent, M, sample=None):
        self.matmodify_window = tk.Toplevel(parent)
        try:
            title = f'Modify material ({sample.name})'
        except AttributeError:
            title = 'New material'
        self.matmodify_window.title(title)
        self.matmodify_window.resizable(False, False)
        self.matmodify_window.hintlabel = tk.Label(self.matmodify_window, text='', anchor=tk.W)
        tk.Label(self.matmodify_window, text='material name', width=15, anchor=tk.W).grid(row=0, column=0, sticky=tk.W, padx=5)
        tk.Label(self.matmodify_window, text='description').grid(row=1, column=0, sticky=tk.NW, padx=5)
        tk.Label(self.matmodify_window, text='material type').grid(row=2, column=0, sticky=tk.W, padx=5)
        tk.Label(self.matmodify_window, text='physical type').grid(row=3, column=0, sticky=tk.W, padx=5)
        tk.Label(self.matmodify_window, text='density / g cm⁻³').grid(row=4, column=0, sticky=tk.W, padx=5)
        tk.Frame(self.matmodify_window).grid(row=5, column=0, pady=4)
        tk.Label(self.matmodify_window, text='composition').grid(row=6, column=0, sticky=tk.W, padx=5)
        tk.Label(self.matmodify_window, text=f'{"".ljust(4)}{"x / g g⁻¹".rjust(11)}{"uᵣx / %".rjust(11)}', font=('Courier', 10)).grid(row=7, column=0, sticky=tk.W)

        self.material_name_F = ttk.Entry(self.matmodify_window, width=25)
        self.material_name_F.grid(row=0, column=1, sticky=tk.W)
        F_font = self.material_name_F.cget('font')
        try:
            name_text = sample.name
        except AttributeError:
            name_text = 'new material'
        self.material_name_F.delete(0, tk.END)
        self.material_name_F.insert(0, name_text)

        self.material_description_F = gui_things.ScrollableText(self.matmodify_window, width=35, height=3, font=F_font, state='normal')
        self.material_description_F.grid(row=1, column=1, sticky=tk.EW)
        try:
            description_text = sample.description
        except AttributeError:
            description_text = 'no description'
        self.material_description_F._update(description_text)

        self.material_type_F = gui_things.Combobox(self.matmodify_window, width=25, font=F_font)
        self.material_type_F.grid(row=2, column=1, sticky=tk.W)
        self.material_type_F['values'] = ['organic','soil', 'Reference Material']
        try:
            type_text = sample.sample_type
        except AttributeError:
            type_text = 'unknown'
        self.material_type_F.set(type_text)

        self.material_state_F = gui_things.Combobox(self.matmodify_window, width=25, font=F_font)
        self.material_state_F.grid(row=3, column=1, sticky=tk.W)
        self.material_state_F['values'] = ['solid','solution']
        try:
            state_text = sample.state
        except AttributeError:
            state_text = 'unknown'
        self.material_state_F.set(state_text)

        density_frame = tk.Frame(self.matmodify_window)

        self.density_w_F = gui_things.Spinbox(density_frame, width=9, from_=0.000, to=10.000, increment=0.001, font=F_font)
        self.density_w_F.pack(side=tk.LEFT, anchor=tk.W)
        try:
            density_text = sample.o_density
        except AttributeError:
            density_text = 1.000
        self.density_w_F.delete(0, tk.END)
        self.density_w_F.insert(0, density_text)

        self.u_density_w_F = gui_things.Spinbox(density_frame, width=9, from_=0.000, to=1.000, increment=0.001, font=F_font)
        self.u_density_w_F.pack(side=tk.LEFT, anchor=tk.W, padx=8)
        try:
            u_density_text = sample.o_udensity
        except AttributeError:
            u_density_text = 0.000
        self.u_density_w_F.delete(0, tk.END)
        self.u_density_w_F.insert(0, u_density_text)

        density_frame.grid(row=4, column=1, sticky=tk.EW)

        try:
            composition_list = self._as_text_display(sample.certificate, preamble='', include_header=False)
            self.composition = sample.certificate
        except AttributeError:
            composition_list = ''
            self.composition = {}

        self.composition_text = gui_things.ScrollableText(self.matmodify_window, width=45, height=25, data=composition_list, font=('Courier', 10))
        self.composition_text.grid(row=8, column=0, columnspan=2, sticky=tk.EW, padx=5)

        f_buttons = tk.Frame(self.matmodify_window)
        tk.Label(f_buttons, text='element', anchor=tk.W, width=10).grid(row=0, column=0, sticky=tk.W)
        self.element_CB = gui_things.Combobox(f_buttons, width=4, font=F_font)
        self.element_CB.grid(row=1, column=0, sticky=tk.W)
        element_list = ('H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og')
        self.element_CB['values'] = element_list
        self.element_CB.set('')

        unit_list = ('g g⁻¹','ppm','%')
        self.unit_index = 0

        tk.Label(f_buttons, text='unit').grid(row=0, column=1)
        value_label = tk.Label(f_buttons, text=f'w / {unit_list[self.unit_index]}')
        value_label.grid(row=0, column=2)
        uncertainty_label = tk.Label(f_buttons, text=f'uw / {unit_list[self.unit_index]}')
        uncertainty_label.grid(row=0, column=3)

        self.value_F = ttk.Entry(f_buttons, width=15, font=F_font)
        self.value_F.grid(row=1, column=2)
        self.uncertainty_F = ttk.Entry(f_buttons, width=15, font=F_font)
        self.uncertainty_F.grid(row=1, column=3, padx=5)

        B_unit = gui_things.Button(f_buttons, text=f'{unit_list[self.unit_index]}', width=8, command=lambda : self.change_unit(B_unit, unit_list, value_label, uncertainty_label))
        B_unit.grid(row=1, column=1, padx=5)

        logo_updateelement = tk.PhotoImage(data=gui_things.PL_check)
        B_updateelement = gui_things.Button(f_buttons, image=logo_updateelement, hint='update element information', hint_destination=self.matmodify_window.hintlabel, command=lambda : self.update_element(self.matmodify_window.hintlabel))
        B_updateelement.grid(row=0, column=4, rowspan=2)
        B_updateelement.image = logo_updateelement

        logo_deleteelement = tk.PhotoImage(data=gui_things.PL_none)
        B_deleteelement = gui_things.Button(f_buttons, image=logo_deleteelement, hint='delete element information', hint_destination=self.matmodify_window.hintlabel, command=lambda : self.delete_element(self.matmodify_window.hintlabel))
        B_deleteelement.grid(row=0, column=5, rowspan=2)
        B_deleteelement.image = logo_deleteelement

        f_buttons.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NW)

        logo_savematerial = tk.PhotoImage(data=gui_things.PL_save)
        B_savematerial = gui_things.Button(self.matmodify_window, image=logo_savematerial, hint='save material information', hint_destination=self.matmodify_window.hintlabel, command=lambda : self.save_material(self.matmodify_window.hintlabel))
        B_savematerial.grid(row=10, column=0, columnspan=2, pady=5)
        B_savematerial.image = logo_savematerial

        self.matmodify_window.hintlabel.grid(row=11, column=0, columnspan=2, sticky=tk.W)

        self.element_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': self.select_combo())

    def select_combo(self, unit_conversions=(1,1000000,100)):
        self.value_F.delete(0, tk.END)
        self.uncertainty_F.delete(0, tk.END)
        if self.element_CB.get() in self.composition.keys():
            value, uncertainty = self.composition[self.element_CB.get()]
            value = value * unit_conversions[self.unit_index]
            uncertainty = uncertainty * unit_conversions[self.unit_index]
            self.value_F.insert(0, value)
            self.uncertainty_F.insert(0, uncertainty)

    def change_unit(self, B_unit, unit_list, value_label, uncertainty_label, unit_conversions=(1,1000000,100)):
        if self.unit_index < len(unit_list) - 1:
            self.unit_index += 1
        else:
            self.unit_index = 0

        B_unit.configure(text=f'{unit_list[self.unit_index]}')
        value_label.configure(text=f'w / {unit_list[self.unit_index]}')
        uncertainty_label.configure(text=f'uw / {unit_list[self.unit_index]}')

        try:
            newvalue = float(self.value_F.get())
            newvalue = newvalue * unit_conversions[self.unit_index] / unit_conversions[self.unit_index - 1]
            self.value_F.delete(0, tk.END)
            self.value_F.insert(0, newvalue)
        except ValueError:
            pass
        try:
            newvalue = float(self.uncertainty_F.get())
            newvalue = newvalue * unit_conversions[self.unit_index] / unit_conversions[self.unit_index - 1]
            self.uncertainty_F.delete(0, tk.END)
            self.uncertainty_F.insert(0, newvalue)
        except ValueError:
            pass

    def update_element(self, Shintlabel, unit_conversions=(1,1000000,100)):
        if self.element_CB.get() in self.element_CB['values']:
            try:
                massfractionvalue = float(self.value_F.get()) / unit_conversions[self.unit_index]
                if not 0 <= massfractionvalue <= 1:
                    raise ValueError
            except (TypeError, ValueError):
                massfractionvalue = None
            try:
                uncertaintyvalue = float(self.uncertainty_F.get()) / unit_conversions[self.unit_index]
                if uncertaintyvalue < 0:
                    raise ValueError
            except (TypeError, ValueError):
                uncertaintyvalue = np.nan

            if massfractionvalue is not None:
                self.composition[self.element_CB.get()] = (massfractionvalue, uncertaintyvalue)
                self.composition_text._update(self._as_text_display(self.composition, preamble='', include_header=False))
            else:
                Shintlabel.configure(text='invalid mass fraction value')
        else:
            Shintlabel.configure(text='invalid element symbol')

    def delete_element(self, Shintlabel):
        if self.element_CB.get() in self.element_CB['values']:
            self.composition.pop(self.element_CB.get(),None)
            self.composition_text._update(self._as_text_display(self.composition, preamble='', include_header=False))
        else:
            Shintlabel.configure(text='invalid element symbol')

    def save_material(self, Shintlabel):

        def not_cert(value):
            if np.isnan(value):
                return ''
            return value

        def _to_csv(certificate):
            text = [f'{key},{item[0]},{not_cert(item[1])}' for key,item in certificate.items()]
            return '\n'.join(text)

        if self.material_name_F.get() != '':
            if self.material_description_F.get().replace('\n',' ').replace(' ','') != '':
                description = self.material_description_F.get().replace('\n',' ')
            else:
                description = 'no description'
            if self.material_type_F.get().replace(' ','') != '':
                stype = self.material_type_F.get()
            else:
                stype = 'unknown'
            if self.material_state_F.get().replace(' ','') != '':
                state = self.material_state_F.get()
            else:
                state = 'unknown'
            try:
                ddensity = float(self.density_w_F.get())
            except Exception:
                ddensity = 1.0
            try:
                uddensity = float(self.u_density_w_F.get())
            except Exception:
                uddensity = 0.0

            with open(os.path.join(os.path.join('data','samples'),f'{self.material_name_F.get()}.csv'),'w') as saved_sample:
                saved_sample.write(f'{description}\n')
                saved_sample.write(f'{stype}\n')
                saved_sample.write(f'{state}\n')
                saved_sample.write(f'{ddensity}\n')
                saved_sample.write(f'{uddensity}\n')
                saved_sample.write(f'{_to_csv(self.composition)}')

            material_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'samples')) if filename.lower().endswith('.csv')]
            self.material_LB._update(material_list)
            Shintlabel.configure(text='material saved')
        else:
            Shintlabel.configure(text='invalid name')


class k0databaseWindow:
    # only one subwindow open at a time
    def __init__(self, parent, M, title):
        self.k0modify_window = None
        m_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=title), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='currently available emission databases', anchor=tk.W).pack(anchor=tk.W)

        k0database_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'k0data')) if filename.lower().endswith('.k0d')]

        self.k0_LB = gui_things.ScrollableListbox(m_frame, width=45, height=15, data=k0database_list)
        self.k0_LB.pack(expand=True, fill=tk.X)

        f_buttons = tk.Frame(m_frame)

        logo_showk0 = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_showk0 = gui_things.Button(f_buttons, image=logo_showk0, hint='display data for the selected emission database', hint_destination=M.hintlabel, command=lambda : self.see_k0(m_frame, M))
        B_showk0.pack(side=tk.LEFT)
        B_showk0.image = logo_showk0

        f_buttons.pack(anchor=tk.W)

        m_frame.pack(padx=5, pady=5)

    def recall_k0(self, parent, M):
        outcome, message = naaobject._get_k0_database(parent)
        if outcome:
            k0database_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'k0data')) if filename.lower().endswith('.k0d')]
            self.k0_LB._update(k0database_list)
        M.hintlabel.configure(text=message)

    def see_k0(self, parent, M):
        if self.k0_LB.get_selection() is not None:
            if self.k0modify_window is not None:
                try:
                    self.k0modify_window.destroy()
                except:
                    pass
            self.k0modify_window = tk.Toplevel(parent)
            self.k0modify_window.resizable(False, False)
            self.k0modify_window.title(f'Show: {self.k0_LB.get_selection()}')
            NAA_database = naaobject._call_database(self.k0_LB.get_selection(), 'k0data', 'k0d')
            general_frame = tk.Frame(self.k0modify_window)
            tk.Label(general_frame, text=f'name: {self.k0_LB.get_selection()}', width=70, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(general_frame, text=f'entries: {len(NAA_database)}', anchor=tk.W).pack(anchor=tk.W)

            general_frame.pack(anchor=tk.NW, pady=6)
            data_frame = tk.Frame(self.k0modify_window)

            k0print = NAA_database.to_string(columns=['target', 'C3', 'E', 'k0', 'type', 'Q0', 'Er'], index=False, header=['target', 'emitter', 'E / keV', 'k0 / 1', 'type', 'Q0 / 1', 'Er / eV'], formatters={'E':"{:.1f}".format, 'k0':"{:.2e}".format, 'Q0':"{:.2f}".format, 'Er':"{:.1f}".format}, col_space={'target':5, 'C3':9, 'E':9, 'k0':10, 'type':7, 'Q0':9, 'Er':11}, justify='right')

            limit_cut = k0print.find('\n')
            if limit_cut > -1:
                k0print_header = k0print[:limit_cut]
                k0print = k0print[limit_cut+1:]

            tk.Label(data_frame, text=k0print_header, anchor=tk.W, font=('Courier', 10)).pack(anchor=tk.W)

            stext = gui_things.ScrollableText(data_frame, width=73, data=k0print, height=32, font=('Courier', 10))
            stext.pack(anchor=tk.W)

            data_frame.pack(anchor=tk.NW)

        else:
            M.hintlabel.configure(text='no database selected')


class RelINRIM_MainWindow:
    # only one subwindow open at a time
    def __init__(self, parent, M):
        M.title('INAA-INRIM Main')
        self.secondary_window = None
        self.positiondistance_window = None

        greeting = M._version
        borderwidthvalue = 2

        Logo_frame = tk.Frame(parent)
        logo_k0main = tk.PhotoImage(data=gui_things.PL_logoinaa)
        k0logo = gui_things.Label(Logo_frame, image=logo_k0main, hint=greeting, hint_destination=M.hintlabel)
        k0logo.pack(side=tk.RIGHT, anchor=tk.E)
        k0logo.image = logo_k0main

        logo_back_to_welcome = tk.PhotoImage(data=gui_things.PL_aback)
        B_back = gui_things.Button(Logo_frame, image=logo_back_to_welcome, hint='back to main menu', hint_destination=M.hintlabel, command=lambda : self.go_back(parent, M))
        B_back.pack(side=tk.LEFT, anchor=tk.W)
        B_back.image = logo_back_to_welcome

        Logo_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, expand=True, pady=3)

        LineFrame = tk.Frame(parent)
        
        #analysis name
        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Analysis name'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        nln = 0

        logo_newanalysis_name = tk.PhotoImage(data=gui_things.PL_name)
        B_new_analysis = gui_things.Button(Buttons_frame, image=logo_newanalysis_name, hint='Modify analysis name!', hint_destination=M.hintlabel)
        B_new_analysis.grid(row=nln, column=0)
        B_new_analysis.image = logo_newanalysis_name

        self.analysisname_combobox = gui_things.LockedEntry(Buttons_frame, width=40, hint='insert string here', hint_destination=M.hintlabel, relief='sunken', bd=3, default_value=M.INAAnalysis.analysis_name)
        self.analysisname_combobox.grid(row=nln, column=1, padx=3)
        B_new_analysis.configure(command=lambda : self.analysisname_combobox.change_value())
        self.analysisname_combobox.variable.trace_add('write', lambda a,b,c : self._update_analysis_name(M))

        Buttons_frame.grid(row=0, column=0, sticky=tk.NW, padx=5)

        #characterization
        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Characterization'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        nln = 0

        self.calibration_combobox = gui_things.Combobox(Buttons_frame, width=30, state='readonly', hint='select detector characterization', hint_destination=M.hintlabel)
        self.calibration_combobox.grid(row=nln, column=0, padx=3)
        characterizations = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'characterizations')) if filename.lower().endswith('.dcr')]
        self.calibration_combobox['values'] = characterizations
        if M.INAAnalysis.characterization is not None:
            self.calibration_combobox.set(M.INAAnalysis.characterization.name)

        logo_displaycalib = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_display_calibration = gui_things.Button(Buttons_frame, image=logo_displaycalib, hint='Display detector characterization!', hint_destination=M.hintlabel, command=lambda : self.show_selected_characterization_info(parent, M))
        B_display_calibration.grid(row=nln, column=1)
        B_display_calibration.image = logo_displaycalib

        Buttons_frame.grid(row=0, column=1, sticky=tk.NW, padx=5)

        LineFrame.pack(anchor=tk.NW, pady=5)

        LineFrame = tk.Frame(parent)

        #buoyancy
        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Buoyancy'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        nln = 0

        logo_environment = tk.PhotoImage(data=gui_things.PL_droplet)
        B_manage_environment = gui_things.Button(Buttons_frame, image=logo_environment, hint='Manage environmental conditions and balance features!', hint_destination=M.hintlabel, command=lambda : self.go_to_environmentalmanagement(M))
        B_manage_environment.grid(row=nln, column=0)
        B_manage_environment.image = logo_environment

        Buttons_frame.grid(row=0, column=0, sticky=tk.NW, padx=5)

        #sample management, declare measurement samples
        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Sample management'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        nln = 0

        self.measurementsamplescounter = tk.Label(Buttons_frame, text=f'{len(M.INAAnalysis.samples_id)} samples', width=12, anchor=tk.W)

        logo_dsample = tk.PhotoImage(data=gui_things.PL_florish)
        B_manage_samples = gui_things.Button(Buttons_frame, image=logo_dsample, hint='Manage measurement samples!', hint_destination=M.hintlabel)
        B_manage_samples.grid(row=nln, column=0)
        B_manage_samples.image = logo_dsample

        self.measurementsamplescounter.grid(row=nln, column=1, padx=5)

        Buttons_frame.grid(row=0, column=1, sticky=tk.NW, padx=5)

        #irradiation
        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Irradiation'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        nln = 0

        logo_neutrons = tk.PhotoImage(data=gui_things.PL_neutron)
        B_new_irradiation = gui_things.Button(Buttons_frame, image=logo_neutrons, hint='New irradiation!', hint_destination=M.hintlabel)
        B_new_irradiation.grid(row=nln, column=0)
        B_new_irradiation.image = logo_neutrons

        self.irradiation_combobox = ttk.Entry(Buttons_frame, width=30, state='readonly')
        self.irradiation_combobox.grid(row=nln, column=1, padx=3)
        if M.INAAnalysis.irradiation is not None:
            self.irradiation_combobox.configure(state='normal')
            self.irradiation_combobox.delete(0, tk.END)
            self.irradiation_combobox.insert(0, M.INAAnalysis.irradiation.code)
            self.irradiation_combobox.configure(state='readonly')

        Buttons_frame.grid(row=0, column=2, sticky=tk.NW, padx=5)

        LineFrame.pack(anchor=tk.NW, pady=5)

        logo_add_spectrum = tk.PhotoImage(data=gui_things.PL_pluspeak)
        logo_none = tk.PhotoImage(data=gui_things.PL_none)
        logo_gear = tk.PhotoImage(data=gui_things.PL_ggear)
        logo_peaklist = tk.PhotoImage(data=gui_things.PL_peak_list)

        LineFrame = tk.Frame(parent)

        #background
        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Background spectrum'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        B_background_open = gui_things.Button(Buttons_frame, image=logo_add_spectrum, hint='Recall background spectrum!', hint_destination=M.hintlabel)
        B_background_open.pack(side=tk.LEFT)
        B_background_open.image = logo_add_spectrum

        BKG_L = tk.Label(Buttons_frame, text='', width=30, anchor=tk.W)
        BKG_L.pack(side=tk.LEFT, padx=5)
        if M.INAAnalysis.background_spectrum is not None:
            BKG_L.configure(text=M.INAAnalysis.background_spectrum.filename())

        B_background_neglect = gui_things.Button(Buttons_frame, image=logo_none, hint='Neglect background correction!', hint_destination=M.hintlabel)
        B_background_neglect.pack(side=tk.LEFT)
        B_background_neglect.image = logo_none

        Buttons_frame.grid(row=0, column=0, sticky=tk.NW, padx=5)

        B_background_open.configure(command=lambda label=BKG_L: self.open_background(parent, M, label))
        B_background_neglect.configure(command=lambda label=BKG_L: self.close_background(M, label))

        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Blank'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        BNK_L = tk.Label(Buttons_frame, text='', width=25, anchor=tk.W)
        BNK_L.pack(side=tk.LEFT, padx=5)
        if M.INAAnalysis.blank_info is not None:
            BNK_L.configure(text=M.INAAnalysis.blank_info.data[0][4].name)

        B_blankselection_open = gui_things.Button(Buttons_frame, image=logo_gear, hint='Manage blank container!', hint_destination=M.hintlabel)
        B_blankselection_open.pack(side=tk.LEFT)
        B_blankselection_open.image = logo_gear

        B_blankselection_open.configure(command=lambda label=BNK_L: self.open_blankies(parent, M, label))

        Buttons_frame.grid(row=0, column=1, sticky=tk.NW, padx=5)

        LineFrame.pack(anchor=tk.NW, pady=5)

        LineFrame = tk.Frame(parent)

        #standard and sample together
        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Measurement spectra'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        nln = 0
        B_standard_open = gui_things.Button(Buttons_frame, image=logo_add_spectrum, hint='Recall spectra!', hint_destination=M.hintlabel)
        B_standard_open.grid(row=nln, column=0)
        B_standard_open.image = logo_add_spectrum

        spectrum_identity_frame = tk.Frame(Buttons_frame)

        #check emission assignment in spectra
        if M.trigger_emission_assignment:
            for nn, _ in enumerate(M.INAAnalysis.spectra):
                M.INAAnalysis.spectra[nn].discriminate_peaks(M.INAAnalysis.k0_database, M.settings.get('energy tolerance'))
                M.trigger_emission_assignment = False

        self.standard_spectra_combobox = gui_things.Combobox(spectrum_identity_frame, width=35, state='readonly', hint='select spectrum', hint_destination=M.hintlabel)
        self.standard_spectra_combobox.pack(anchor=tk.NW)

        self.standard_measurementsamplecode = tk.Label(spectrum_identity_frame, text='-', width=25, anchor=tk.E)
        self.standard_measurementsamplecode.pack(anchor=tk.SE, fill=tk.X, expand=True)

        self.standard_measurementsamplerole = tk.Label(spectrum_identity_frame, text='-', width=25, anchor=tk.E)
        self.standard_measurementsamplerole.pack(anchor=tk.SE, fill=tk.X, expand=True)

        spectrum_identity_frame.grid(row=nln, column=1, padx=3)

        self.standard_counter = tk.Label(Buttons_frame, text='#0 of 0', width=9)
        self.standard_counter.grid(row=nln, column=2, padx=3)

        delete_block = tk.Frame(Buttons_frame)

        B_standard_peaklist = gui_things.Button(delete_block, image=logo_peaklist, hint='Peaklist!', hint_destination=M.hintlabel, command=lambda : self.go_to_spectrummanagement(M))
        B_standard_peaklist.pack(side=tk.LEFT)
        B_standard_peaklist.image = logo_peaklist

        logo_spdelete = tk.PhotoImage(data=gui_things.PL_none)
        B_standard_delete = gui_things.Button(delete_block, image=logo_spdelete, hint='Delete spectrum!', hint_destination=M.hintlabel)
        B_standard_delete.pack(side=tk.LEFT)
        B_standard_delete.image = logo_spdelete

        F_delete_selector_standard = tk.Frame(delete_block)
        self.delete_selector_standard = tk.IntVar(parent)
        R1 = tk.Radiobutton(F_delete_selector_standard, text='selected', anchor=tk.W, value=0, variable=self.delete_selector_standard)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_delete_selector_standard, text='all', anchor=tk.W, value=1, variable=self.delete_selector_standard)
        R2.pack(anchor=tk.W)
        self.delete_selector_standard.set(0)
        F_delete_selector_standard.pack(side=tk.LEFT, padx=3)

        B_standard_delete.configure(command=lambda : self.delete_spectrum(parent, M))

        delete_block.grid(row=nln, column=4)

        nln += 1
        self.standard_position = gui_things.CountingDistanceLabel(Buttons_frame, width=35)
        self.standard_position.grid(row=nln, column=1, sticky=tk.EW)

        logo_modifydistance = tk.PhotoImage(data=gui_things.PL_meter)
        change_distance_B = gui_things.Button(Buttons_frame, image=logo_modifydistance, hint='Modify distances of counting position', hint_destination=M.hintlabel)
        change_distance_B.grid(row=nln, column=2)
        change_distance_B.image = logo_modifydistance
        
        Buttons_frame.grid(row=0, column=1, sticky=tk.NW, padx=5)

        #recall spectra
        self._update_spectra(M)

        LineFrame.pack(anchor=tk.NW, pady=5)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, expand=True, pady=3)

        LineFrame = tk.Frame(parent)

        Buttons_frame = tk.LabelFrame(LineFrame, labelwidget=tk.Label(parent, text='Result'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        logo_elaborate_results = tk.PhotoImage(data=gui_things.PL_check)
        B_elaborate_results = gui_things.Button(Buttons_frame, image=logo_elaborate_results, hint='Analysis overview!', hint_destination=M.hintlabel, command=lambda : self.elaboration_process(parent, M))
        B_elaborate_results.grid(row=0, column=0)
        B_elaborate_results.image = logo_elaborate_results

        ttk.Separator(Buttons_frame, orient=tk.VERTICAL).grid(row=0, column=1, sticky=tk.NS, padx=3)

        logo_save_progress = tk.PhotoImage(data=gui_things.PL_save)
        B_save_progress = gui_things.Button(Buttons_frame, image=logo_save_progress, hint='Save analysis progress!', hint_destination=M.hintlabel, command=lambda : self.save_analysis_progress(parent, M))
        B_save_progress.grid(row=0, column=2)
        B_save_progress.image = logo_save_progress

        Buttons_frame.grid(row=0, column=0, sticky=tk.NW, padx=5)

        LineFrame.pack(anchor=tk.NW, pady=5)

        #commands
        self.calibration_combobox.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_characterization(M))
        B_manage_samples.configure(command= lambda : self.go_to_measurementsamplemanagement(M, self.measurementsamplescounter, self.standard_measurementsamplecode, self.standard_measurementsamplerole))
        B_new_irradiation.configure(command= lambda : self.go_to_irradiationsamplemanagement(M, self.irradiation_combobox))
        B_standard_open.configure(command=lambda : self.go_to_openspectra(M))
        change_distance_B.configure(command=lambda : self.go_to_distance_modifier(M, self.standard_position))

        self.standard_spectra_combobox.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_spectrum(M))

    def save_analysis_progress(self, parent, M):
        filetypes = (('INAAnalysis save file','*.naas'),)
        namefile = asksaveasfilename(parent=parent, initialfile=f'{M.INAAnalysis.analysis_name}.naas', filetypes=filetypes)

        if namefile != '':
            naaobject._save_naalysis_file(M.INAAnalysis, namefile)
            M.hintlabel.configure(text='analysis succesfully saved!')

        else:
            M.hintlabel.configure(text='not saved!')

    def show_selected_characterization_info(self, parent, M):
        if M.INAAnalysis.characterization is not None:
            TOP = tk.Toplevel(parent)
            TOP.title('Characterization overview')
            TOP.resizable(False, False)
            gui_things.ScrollableText(TOP, width=70, height=15, data=M.INAAnalysis.characterization.short_report()).pack(anchor=tk.NW, padx=5, pady=5)

    def check_the_analysis(self, Analysis):

        def thehead(nn):
            if nn == 0:
                return True
            return False

        overview, errors = [], []

        #check analysis name
        overview.append(f"""########
ANALYSIS

analysis name: {Analysis.analysis_name}
""")

        if Analysis.characterization is not None:
            overview.append(f'{Analysis.characterization.short_report()}')
        else:
            errors.append('! - characterization is not selected')

        stypes = [item.sampletype for item in Analysis.samples_id]
        if len(stypes) == 0:
            errors.append('! - no samples or standards registered')
        elif stypes.count('standard') == 0:
            errors.append('! - no standards registered')
        elif stypes.count('sample') == 0:
            errors.append('! - no samples registered')
        else:
            sampleroles = '\n'.join([f'{item.name}  →  {item.sampletype}' for item in Analysis.samples_id])
            overview.append(f"""#######
SAMPLES

{sampleroles}
""")

        if Analysis.irradiation is not None:
            overview.append(f'{Analysis.irradiation.short_report()}')
        else:
            errors.append('! - irradiation is not selected')

        if Analysis.background_spectrum is not None:
            overview.append(f"""##########
BACKGROUND

spectrum name: {Analysis.background_spectrum.filename()}
real time / s: {Analysis.background_spectrum.real_time:.1f}
live time / s: {Analysis.background_spectrum.live_time:.1f}
""")
        else:
            overview.append("""##########
BACKGROUND

background spectrum not included
""")
        
        if Analysis.blank_info is not None:
            overview.append(f"""#####
BLANK

material name: {Analysis.blank_info.data[0][4].name}
mass / g: {Analysis.blank_info.mass}
""")
        else:
            overview.append("""#####
BLANK

blank information not included
""")
        ids = [item.name for item in Analysis.samples_id]
        spcts = [item.get_sample() for item in Analysis.spectra]
        diffs = set(ids).difference(set(spcts))
        if len(spcts) == 0:
            errors.append('! - no spectra are recalled')
        elif spcts.count('-') > 0:
            errors.append(f'! - {spcts.count("-")} unassigned spectra')
        elif diffs != set():
            errors.append(f'! - no spectra assigned to ({", ".join([item for item in diffs])}) samples')
        elif Analysis.characterization is None or Analysis.irradiation is None:
            pass
        else:
            spectrainfolist = '\n'.join([item.short_report(eof_date=Analysis.irradiation.datetime, header=thehead(nnn)) for nnn, item in enumerate(Analysis.spectra)])
            overview.append(f"""#######
SPECTRA

{spectrainfolist}
""")
        return '\n'.join(overview), '\n'.join(errors)

    def elaboration_process(self, parent, M):
        if self.secondary_window is not None:
            try:
                self.secondary_window.destroy()
            except:
                pass
        clear_window(parent)
        #check INAA
        message, errors = self.check_the_analysis(M.INAAnalysis)
        Results_MainWindow(parent, M, message, errors)

    def _update_analysis_name(self, M):
        M.INAAnalysis.analysis_name = self.analysisname_combobox.variable.get()

    def update_counting_position(self, M):
        s_index = self.standard_spectra_combobox.current()
        if s_index > -1:
            if self.standard_position.get() != M.INAAnalysis.spectra[s_index].counting_position:
                M.INAAnalysis.spectra[s_index].counting_position = self.standard_position.get()

    def open_blankies(self, parent, M, label):
        #open the window for blank management
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in M.unclosablewindows:
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()

        self.secondary_window = tk.Toplevel(M)
        BlankManagementWindow(self.secondary_window, M, label)

    def open_background(self, parent, M, label):
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))
        limit_s = M.settings.get('sample statistical uncertainty limit')
        try:
            filename = askopenfilename(parent=M, title=f'Recall background spectrum',filetypes=filetypes)
        except TypeError:
            filename = ''
        notes = []
        txt = label.cget('text')
        if filename != '' and filename is not None:
            peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=M.settings.get('look for spectrum file'))
            if result == True:
                Spectrum = naaobject.SpectrumAnalysis(identity=f'background spectrum', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=filename, source=source, efficiency=None, energy_tolerance=M.settings.get('energy tolerance'), database=M.INAAnalysis.k0_database)#SpectrumAnalysis
                M.INAAnalysis.background_spectrum = Spectrum
                txt = Spectrum.filename()
            else:
                notes.append(note)
        label.configure(text=txt)
        M.hintlabel.configure(text='background spectrum imported')

    def close_background(self, M, label):
        M.INAAnalysis.background_spectrum = None
        label.configure(text='')
        M.hintlabel.configure(text='background spectrum removed')

    def select_characterization(self, M):
        M.INAAnalysis.characterization = naaobject._call_database(self.calibration_combobox.get(), 'characterizations', 'dcr')

        for spectrum in M.INAAnalysis.spectra:
            spectrum.counting_position = M.INAAnalysis.characterization.reference_position

        self._update_spectra(M)
        try:
            self.secondary_window.destroy()
        except Exception:
            None
        self.calibration_combobox._showhint()

    def go_to_distance_modifier(self, M, llabel):
        s_index = self.standard_spectra_combobox.current()
        if 0 <= s_index < len(M.INAAnalysis.spectra) and M.INAAnalysis.characterization is not None:
            if self.secondary_window is not None:
                try:
                    if self.secondary_window.title() in M.unclosablewindows:
                        if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progress.\nDo you want to continue?\n', parent=self.secondary_window):
                            self.secondary_window.destroy()
                        else:
                            return
                    else:
                        self.secondary_window.destroy()
                except Exception:
                    self.secondary_window.destroy()
            self.secondary_window = tk.Toplevel(M)
            SetdistanceWindow(self.secondary_window, M, s_index, llabel)
        else:
            M.hintlabel.configure(text='no spectrum or characterization selected')

    def select_spectrum(self, M):
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in M.unclosablewindows:
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()

        s_index = self.standard_spectra_combobox.current()
        prov_spct = M.INAAnalysis.spectra[s_index]
        self.standard_position.set(prov_spct)
        sample_id = prov_spct.get_sample()
        role_string = M.INAAnalysis.get_sampletype(sample_id)
        self.standard_measurementsamplecode.configure(text=sample_id)
        self.standard_measurementsamplerole.configure(text=role_string)
        self.standard_counter.configure(text=f'#{s_index + 1} of {len(M.INAAnalysis.spectra)}')
        self.standard_spectra_combobox._showhint()

    def delete_spectrum(self, parent, M):
        s_index = self.standard_spectra_combobox.current()
        if 0 <= s_index < len(M.INAAnalysis.spectra):
            if self.delete_selector_standard.get() == 0:
                message = f'Are you sure to delete spectrum\n{M.INAAnalysis.spectra[s_index].filename()} (#{s_index+1})\nfrom the list?\n'
            else:
                message = 'Are you sure to delete all spectra from the list?\n'
            if messagebox.askyesno(title='Delete spectrum', message=message, parent=parent):
                if self.secondary_window is not None:
                    try:
                        self.secondary_window.destroy()
                    except:
                        pass
                if self.delete_selector_standard.get() == 0:
                    M.INAAnalysis.spectra.pop(s_index)
                else:
                    hh = len(M.INAAnalysis.spectra)
                    for i in range(hh):
                        M.INAAnalysis.spectra.pop()
                self._update_spectra(M)
        else:
            M.hintlabel.configure(text='no spectrum selected')

    def go_back(self, parent, M):
        if self.secondary_window is not None:
            try:
                self.secondary_window.destroy()
            except:
                pass
        clear_window(parent)
        WelcomeWindow(parent, M)

    def go_to_spectrummanagement(self, M):
        #open the window for peak inspection
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in M.unclosablewindows:
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()

        s_index = self.standard_spectra_combobox.current()
        if 0 <= s_index < len(M.INAAnalysis.spectra):
            #perform a peak discrimination
            if M.INAAnalysis.spectra[s_index].suspected_peaks is None:
                M.INAAnalysis.spectra[s_index].discriminate_peaks()
            self.secondary_window = tk.Toplevel(M)
            PeaklistWindow(self.secondary_window, M, s_index, self.standard_measurementsamplecode, self.standard_measurementsamplerole)
        else:
            M.hintlabel.configure(text='no spectrum selected')

    def go_to_environmentalmanagement(self, M):
        #open the window for environmental and balance parameters
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in M.unclosablewindows:
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        EnvironmentalManagementWindow(self.secondary_window, M)

    def go_to_measurementsamplemanagement(self, M, mslabel, idlabel, rolelabel):
        #open the window for measurement samples record
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in M.unclosablewindows:
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        MeasurementSampleManagementWindow(self.secondary_window, M, mslabel, idlabel, rolelabel)

    def go_to_irradiationsamplemanagement(self, M, irrlabel):
        #open the window for irradiation record
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in M.unclosablewindows:
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        IrradiationSampleManagementWindow(self.secondary_window, M, irrlabel)

    def go_to_openspectra(self, M):
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in M.unclosablewindows:
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))#,('HyperLab ASC file','*.asc'),('CHN spectrum file','*.chn'))
        limit_s = M.settings.get('sample statistical uncertainty limit')
        try:
            output = tuple(askopenfilenames(parent=M, title=f'Recall spectra',filetypes=filetypes))
        except TypeError:
            output = ()
        notes = []
        if len(output) > 0:
            M.hintlabel.configure(text=f'importing {len(output)} spectra')
            M.progressbar['value'] = 0
            M.progressbar['maximum'] = len(output)
            M.progressbar.update()
        for filename in output:
            if filename != '' and filename != ():
                peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=M.settings.get('look for spectrum file'))
                if result == True:
                    Spectrum = naaobject.SpectrumAnalysis(identity=f'analysis spectrum', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=filename, source=source, efficiency=M.INAAnalysis.characterization, energy_tolerance=M.settings.get('energy tolerance'), database=M.INAAnalysis.k0_database)#SpectrumAnalysis
                    M.INAAnalysis.spectra.append(Spectrum)
                else:
                    notes.append(note)
            M.progressbar['value'] += 1
            M.progressbar.update()
        M.hintlabel.configure(text='imported')

        self._update_spectra(M)

    def _update_spectra(self, M):
        self.standard_spectra_combobox['values'] = [item.filename() for item in M.INAAnalysis.spectra]
        if len(M.INAAnalysis.spectra) > 0:
            s_index = len(M.INAAnalysis.spectra) - 1
            self.standard_spectra_combobox.set(self.standard_spectra_combobox['values'][s_index])
            self.standard_position.set(M.INAAnalysis.spectra[s_index])#####
            sample_id = M.INAAnalysis.spectra[s_index].get_sample()
            self.standard_measurementsamplecode.configure(text=sample_id)
            role_string = M.INAAnalysis.get_sampletype(sample_id)
            self.standard_measurementsamplecode.configure(text=sample_id)
            self.standard_measurementsamplerole.configure(text=role_string)
            self.standard_counter.configure(text=f'#{s_index+1} of {len(M.INAAnalysis.spectra)}')
        else:
            self.standard_spectra_combobox.set('')
            self.standard_measurementsamplecode.configure(text='-')
            self.standard_measurementsamplerole.configure(text='-')
            self.standard_counter.configure(text='#0 of 0')
            self.standard_position.set(None)


class Results_MainWindow:
    def __init__(self, parent, M, message, errors):

        M.title('INAA-INRIM Result')
        self.secondary_window = None
        borderwidthvalue = 2

        Logo_frame = tk.Frame(parent)
        logo_k0main = tk.PhotoImage(data=gui_things.PL_logoinaa)
        k0logo = gui_things.Label(Logo_frame, image=logo_k0main, hint='greetings', hint_destination=M.hintlabel)
        k0logo.pack(side=tk.RIGHT, anchor=tk.E)
        k0logo.image = logo_k0main

        logo_back_to_welcome = tk.PhotoImage(data=gui_things.PL_aback)
        B_back = gui_things.Button(Logo_frame, image=logo_back_to_welcome, hint='back to main window', hint_destination=M.hintlabel, command=lambda : self.go_back(parent, M))
        B_back.pack(side=tk.LEFT, anchor=tk.W)
        B_back.image = logo_back_to_welcome

        Logo_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, expand=True, pady=3)

        if errors != '':
            header = 'List of errors'
        else:
            header = 'Experimental overview of analysis'

        Data_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text=header), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        overview = gui_things.ScrollableText(Data_frame, width=70, height=12)

        if errors != '':
            overview._update(errors)
        else:
            overview._update(message)

        overview.pack()

        codes = [item.name for item in M.INAAnalysis.samples_id]
        M.INAAnalysis.pairings = [pair for pair in M.INAAnalysis.pairings if pair[0] in codes and pair[1] in codes]

        Data_frame.pack(anchor=tk.NW, padx=5)

        Results_frame = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text='select analysis'), relief='solid', bd=borderwidthvalue, padx=4, pady=4)

        results_frame = tk.Frame(Results_frame)

        lline = tk.Frame(results_frame)
        tk.Label(lline, text='method', anchor=tk.W).pack(side=tk.LEFT)

        choiceline = tk.Frame(lline)
        self.methodofchoice = tk.IntVar(choiceline)

        tk.Frame(choiceline).pack(side=tk.LEFT, padx=8)
        MC1 = tk.Radiobutton(choiceline, text='relative', variable=self.methodofchoice, value=0)
        MC1.pack(side=tk.LEFT)
        tk.Frame(choiceline).pack(side=tk.LEFT, padx=8)
        MC2 = tk.Radiobutton(choiceline, text='k0', variable=self.methodofchoice, value=1)
        MC2.pack(side=tk.LEFT)
        tk.Frame(choiceline).pack(side=tk.LEFT, padx=8)
        MC3 = tk.Radiobutton(choiceline, text='relative + k0', variable=self.methodofchoice, value=2)
        MC3.pack(side=tk.LEFT)

        self.methodofchoice.set(0)

        choiceline.pack(side=tk.LEFT, padx=5)

        lline.pack(anchor=tk.W)

        tk.Frame(results_frame).pack(pady=3)

        lline = tk.Frame(results_frame)
        tk.Label(lline, text='sample', anchor=tk.W).pack(side=tk.LEFT)
        self.sampleCB = gui_things.Combobox(lline, width=15, state='readonly')
        self.sampleCB.pack(side=tk.LEFT, padx=5)
        self.sampleCB['values'] = [item.name for item in M.INAAnalysis.samples_id if item.sampletype == 'sample']
        if len(self.sampleCB['values']) > 0:
            self.sampleCB.set(self.sampleCB['values'][0])
        tk.Frame(lline).pack(side=tk.LEFT, padx=8)
        tk.Label(lline, text='standard', anchor=tk.W).pack(side=tk.LEFT)
        self.standardCB = gui_things.Combobox(lline, width=15, state='readonly')
        self.standardCB.pack(side=tk.LEFT, padx=5)
        self.standardCB['values'] = [item.name for item in M.INAAnalysis.samples_id if item.sampletype == 'standard']
        if len(self.standardCB['values']) > 0:
            couple = M.INAAnalysis.get_pair(self.sampleCB.get())
            if couple is not None:
                self.standardCB.set(couple)
            else:
                self.standardCB.set(self.standardCB['values'][0])
                M.INAAnalysis.pairings.append((self.sampleCB.get(), self.standardCB['values'][0]))

        logo_confirm_pairing = tk.PhotoImage(data=gui_things.PL_check)
        B_confirm_pairing = gui_things.Button(lline, image=logo_confirm_pairing, hint='confirm pairing', hint_destination=M.hintlabel, command=lambda : self.confirm_pairings(M))
        B_confirm_pairing.pack(side=tk.LEFT, padx=5)
        B_confirm_pairing.image = logo_confirm_pairing

        logo_view_pairings = tk.PhotoImage(data=gui_things.PL_list)
        B_view_pairings = gui_things.Button(lline, image=logo_view_pairings, hint='view all sample-standard pairings', hint_destination=M.hintlabel, command=lambda : self.view_all_pairings(parent, M))
        B_view_pairings.pack(side=tk.LEFT)
        B_view_pairings.image = logo_view_pairings

        lline.pack(anchor=tk.W, pady=3)

        lline = tk.Frame(results_frame)
        tk.Label(lline, text='k0 monitor', anchor=tk.W).pack(side=tk.LEFT)
        self.k0monitorCB = gui_things.Combobox(lline, width=25, state='readonly')
        self.k0monitorCB.pack(side=tk.LEFT, padx=5)
        self._update_k0emissions(M)

        lline.pack(anchor=tk.W, pady=3)

        results_frame.pack(anchor=tk.NW, fill=tk.X)

        self.standardCB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._update_k0emissions(M))
        self.sampleCB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._update_standard_accordingly(M))

        bline = tk.Frame(Results_frame)
        logo_elaborate_results = tk.PhotoImage(data=gui_things.PL_output_sam)
        B_elaborate_results = gui_things.Button(bline, image=logo_elaborate_results, hint='compute results (sample)', hint_destination=M.hintlabel, command=lambda : self.compute_results(parent, M, 'sample', overview.get()))
        B_elaborate_results.pack(side=tk.LEFT)
        B_elaborate_results.image = logo_elaborate_results

        logo_elaborate_results_2 = tk.PhotoImage(data=gui_things.PL_output_mat)
        B_elaborate_results_2 = gui_things.Button(bline, image=logo_elaborate_results_2, hint='compute results (material)', hint_destination=M.hintlabel, command=lambda : self.compute_results(parent, M, 'material', overview.get()))
        B_elaborate_results_2.pack(side=tk.LEFT)
        B_elaborate_results_2.image = logo_elaborate_results_2

        bline.pack(anchor=tk.W, padx=5, pady=5)

        self.methodofchoice.trace_add('write', lambda a,b,c : self._hideorseek())
        self._hideorseek()

        if errors == '':
            Results_frame.pack(anchor=tk.NW, padx=5, fill=tk.X)

    def confirm_pairings(self, M):
        new_pairing = (self.sampleCB.get(), self.standardCB.get())
        idx = -1
        for nn, pair in enumerate(M.INAAnalysis.pairings):
            if pair[0] == new_pairing[0]:
                idx = nn
                break
        if idx == -1:
            M.INAAnalysis.pairings.append(new_pairing)
        else:
            M.INAAnalysis.pairings[idx] = new_pairing

        M.hintlabel.configure(text='new pairing confirmed')

    def view_all_pairings(self, parent, M):
        VP = tk.Toplevel(parent)
        VP.title('Pairings')
        VP.resizable(False, False)
        m_frame = tk.LabelFrame(VP, labelwidget=tk.Label(VP, text='list'), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(m_frame, text='sample', width=15, anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        tk.Label(m_frame, text='standard', width=15, anchor=tk.W).grid(row=0, column=2, sticky=tk.W)
        for nl, items in enumerate(M.INAAnalysis.pairings):
            tk.Label(m_frame, text=items[0], width=15, anchor=tk.W).grid(row=1+nl, column=0, sticky=tk.W)
            tk.Label(m_frame, text='->', width=3).grid(row=1+nl, column=1, sticky=tk.W)
            tk.Label(m_frame, text=items[1], width=15, anchor=tk.W).grid(row=1+nl, column=2, sticky=tk.W)

        m_frame.pack(anchor=tk.NW, padx=5, pady=5)

    def _hideorseek(self):
        if self.methodofchoice.get() == 0:
            self.k0monitorCB.configure(state='disabled')
        else:
            self.k0monitorCB.configure(state='readonly')

    def _unpack_selected_emissions(self, spectrum, allowed):
        pre_check = [sus[ass] for ass, sus in zip(spectrum.assigned_peaks, spectrum.suspected_peaks) if ass != -1]
        return [item.emission for item in pre_check if item.line['type'] in allowed]

    def _update_standard_accordingly(self, M):
        self.sampleCB.get()
        for pair in M.INAAnalysis.pairings:
            if pair[0] == self.sampleCB.get() and pair[1] in self.standardCB['values']:
                self.standardCB.set(pair[1])
                break
        self._update_k0emissions(M)

    def _update_k0emissions(self, M, allowed=('I', 'IVB')):
        k0spectra = [self._unpack_selected_emissions(spectrum, allowed) for spectrum in M.INAAnalysis.spectra if spectrum.sample == self.standardCB.get()]
        values = sorted(set([item for sublist in k0spectra for item in sublist]))
        self.k0monitorCB['values'] = values
        if 'Au-198 411.8 keV' in self.k0monitorCB['values']:
            self.k0monitorCB.set('Au-198 411.8 keV')
        elif len(self.k0monitorCB['values']) > 0:
            self.k0monitorCB.set(self.k0monitorCB['values'][0])
        else:
            self.k0monitorCB.set('')

    def compute_results(self, parent, M, vtype, overview_setup):
        base_hint = M.hintlabel.cget('text')

        if self.methodofchoice.get() == 0:
            textline = f'relative-INAA method\nresult visualization: {vtype} mode'
        elif self.methodofchoice.get() == 1:
            textline = f'k0-INAA method ({self.k0monitorCB.get()} monitor)\nresult visualization: {vtype} mode'
        else:
            textline = f'relative-INAA + k0-INAA method ({self.k0monitorCB.get()} monitor)\nresults visualization: {vtype} mode'

        overview = [overview_setup,  f'###########\nELABORATION\n\n{textline}\n', '##########################\nSAMPLE -> STANDARD PAIRING\n\n' + '\n'.join([f'{pitem[0]}  ->  {pitem[1]}' for pitem in M.INAAnalysis.pairings]) + '\n']

        results = []
        if M.INAAnalysis.irradiation.irradiation_scheme is not None:
            M.INAAnalysis.irradiation.irradiation_scheme.beta_list.clear()

        for _smpl in M.INAAnalysis.samples_id:
            _smpl.composition._rezero()

        M.progressbar['value'] = 0
        M.progressbar['maximum'] = len(M.INAAnalysis.pairings) * 5 + 3
        M.progressbar.update()
        M.hintlabel.configure(text=f'{base_hint} ...analyzing standards')

        for s_pair in M.INAAnalysis.pairings:

            #measurement samples
            standard = M.INAAnalysis.get_sample(s_pair[1])
            sample = M.INAAnalysis.get_sample(s_pair[0])

            linearize_standards = {}
            linearize_auxiliary_standards = {}
            linearize_samples = {}

            for nn, inv_spectrum in enumerate(M.INAAnalysis.spectra):
                if inv_spectrum.sample == standard.name:
                    emissions_list = []
                    for nnn, (sus, ass) in enumerate(zip(inv_spectrum.suspected_peaks, inv_spectrum.assigned_peaks)):
                        emissions_list += self.manage_emissions(sus, ass, nnn, True)
                    linearize_standards[(inv_spectrum, nn)] = tuple(emissions_list)

            M.progressbar['value'] += 1
            M.progressbar.update()
            M.hintlabel.configure(text=f'{base_hint} ...evaluating β')

            #neutron gradient evaluation
            if M.INAAnalysis.irradiation.irradiation_scheme is not None:

                aux_code = M.INAAnalysis.irradiation.irradiation_scheme._get_adjacent_standards(standard.name, sample.name)
                for nn, inv_spectrum in enumerate(M.INAAnalysis.spectra):
                    if inv_spectrum.sample == aux_code:
                        emissions_list = []
                        for nnn, (sus, ass) in enumerate(zip(inv_spectrum.suspected_peaks, inv_spectrum.assigned_peaks)):
                            emissions_list += self.manage_emissions(sus, ass, nnn, True)
                        linearize_auxiliary_standards[(inv_spectrum, nn)] = tuple(emissions_list)

                for (sstand, emissions) in linearize_standards.items():
                    for emiss in emissions:
                        for (ssamp, smemissions) in linearize_auxiliary_standards.items():
                            if sstand[0].counting_position == ssamp[0].counting_position:
                                for semiss in smemissions:
                                    if emiss[1] == semiss[1]:
                                        beta, ubeta = self.calculate_beta(M, sstand[0], sstand[1], ssamp[0], ssamp[1], emiss[1], emiss[0], semiss[1], semiss[0])
                                        M.INAAnalysis.irradiation.irradiation_scheme.update_beta(beta, ubeta, ssamp[0].sample, sstand[0].sample, emiss[1].target, emiss[1].emission, sstand[0].counting_position)

            M.progressbar['value'] += 1
            M.progressbar.update()
            M.hintlabel.configure(text=f'{base_hint} ...analyzing samples')

            for nn, inv_spectrum in enumerate(M.INAAnalysis.spectra):
                if inv_spectrum.sample == sample.name:
                    emissions_list = []
                    for nnn, (sus, ass) in enumerate(zip(inv_spectrum.suspected_peaks, inv_spectrum.assigned_peaks)):
                        emissions_list += self.manage_emissions(sus, ass, nnn, M.settings.get('elaborate only selected emissions'))#option to select only user assigned standard emissions
                    linearize_samples[(inv_spectrum, nn)] = tuple(emissions_list)

            M.progressbar['value'] += 1
            M.progressbar.update()
            M.hintlabel.configure(text=f'{base_hint} ...application of relative method')

            #relative
            if self.methodofchoice.get() in (0, 2):
                for (sstand, emissions) in linearize_standards.items():
                    for emiss in emissions:
                        for (ssamp, smemissions) in linearize_samples.items():
                            for semiss in smemissions:
                                if emiss[1] == semiss[1]:
                                    results.append(naaobject.UncBudget(M, sstand[0], sstand[1], ssamp[0], ssamp[1], emiss[1], emiss[0], semiss[1], semiss[0]))
                                    break

            M.progressbar['value'] += 1
            M.progressbar.update()
            M.hintlabel.configure(text=f'{base_hint} ...application of k0 method')

            #k0
            if self.methodofchoice.get() in (1, 2):
                monitor_label = self.k0monitorCB.get()
                standard_item = None
                for (sstand, emissions) in linearize_standards.items():
                    for emiss in emissions:
                        if emiss[1].emission == monitor_label:
                            standard_item = self.confirm_emission(sstand, standard_item, emiss)

                if standard_item is not None:
                    kyy = list(linearize_samples.keys())[0]
                    already_present = [item.emission for item in results if item.sample_id==kyy[0].sample]
                    for (ssamp, smemissions) in linearize_samples.items():
                        for semiss in smemissions:
                            if semiss[1].emission not in already_present:
                                results.append(naaobject.UncBudget(M, standard_item[0][0], standard_item[0][1], ssamp[0], ssamp[1], standard_item[1][1], standard_item[1][0], semiss[1], semiss[0]))

            M.progressbar['value'] += 1
            M.progressbar.update()

        _beta_list = '###############\nBETA EVALUATION\n\n' + '\n'.join([f'{key[0]}  ->  {key[1]} ({key[3]}) {key[4]}; β / mm⁻¹: {value[0]:.2e} [{np.abs(value[1]/value[0])*100:.0f} %]' for key, value in M.INAAnalysis.irradiation.irradiation_scheme.beta_list.items()]) + '\n'
        overview.append(_beta_list)

        #DISCRIMINANTS relative results
        # first discriminant
        M.hintlabel.configure(text=f'{base_hint} ...discrimination of results')
        results, _part1 = naaobject._get_likelihood(results)

        M.progressbar['value'] += 1
        M.progressbar.update()

        #iterations for composition update, up to n=10 iterations
        #get composition from current results (weighted averages)

        #iterations
        max_it = M.settings.get('max iterations')
        for _ in range(max_it):
            M.hintlabel.configure(text=f'{base_hint} ...iterative update {_+1} of {max_it}')
            #updated_composition -> dict
            #sample update
            naaobject._get_composition_updated_improved(results, M)
 
            #update the results accordingly
            improvements = []
            for result in results:
                pre_value = result.y
                result._update(M.INAAnalysis)
                post_value = result.y
                improvements.append((pre_value - post_value) / post_value)
            #premature exit
            improvements = np.array(improvements)
            if all(np.abs(improvements) < 0.001):
                break

        M.progressbar['value'] += 1
        M.progressbar.update()
        M.hintlabel.configure(text=f'{base_hint} ...discrimination of results')

        #second discriminant
        results, _part2 = naaobject._get_likelihood(results, streamlined=True)

        _part1['budget tested']
        discs = sorted(_part1['discarded'].union(_part2['discarded']))
        if len(discs) > 0:
            disc_list = '\n'.join(discs)
        else:
            disc_list = 'None'
        grand_finale = f'#######\nRESULTS\n\nuncertainty budgets evaluated from all selected emissions: {_part1["budget tested"]}\nuncertainty budgets resulted: {len(results)}\n\n' + 'list of discarded budgets due to invalid results\n' + disc_list
        overview.append(grand_finale)

        M.progressbar['value'] += 1
        M.progressbar.update()
        M.hintlabel.configure(text=f'{base_hint} ...done!')

        RW = tk.Toplevel(parent)
        RW.resizable(False, False)
        all_colors = (M.settings.get('color04'), M.settings.get('color05'), M.settings.get('color06'), M.settings.get('color07'), M.settings.get('color08'), M.settings.get('color09'), M.settings.get('color10'), M.settings.get('color11'), M.settings.get('color12'), M.settings.get('color01'), M.settings.get('color02'), M.settings.get('color03'))
        PTR = gui_things.PeriodicTable(RW, results, default_palette=M.settings.get('color palette'), colors=(M.settings.get('color01'), M.settings.get('color02'), M.settings.get('color03')), allcolors=all_colors, visualization_type=vtype, lock_cells=M.settings.get('excel worksheet lock'), set_autolinks=M.settings.get('excel internal links'), visible_models=M.settings.get('visible models'), hide_grid=M.settings.get('hide grid'), summary='\n'.join(overview))
        PTR.pack(anchor=tk.NW, padx=5, pady=5)

    def calculate_beta(self, M, standard_spectrum, st_idx, sample_spectrum, sm_idx, st_emission_line, st_emiss_id, sm_emission_line, sm_emiss_id):
        _dd, _udd = M.INAAnalysis.irradiation.irradiation_scheme.standard_sample_distance(standard_spectrum.sample, sample_spectrum.sample)

        np1, unp1 = standard_spectrum.peak_list[st_emiss_id][4], standard_spectrum.peak_list[st_emiss_id][5]
        lbd, _ = st_emission_line.get_lambda(st_emission_line.line['C3_t1/2'], st_emission_line.line['C3_ut1/2'], st_emission_line.line['C3_unit'])
        np2, unp2 = sample_spectrum.peak_list[sm_emiss_id][4], sample_spectrum.peak_list[sm_emiss_id][5]
        td1 = standard_spectrum.datetime - M.INAAnalysis.irradiation.datetime
        td2 = sample_spectrum.datetime - M.INAAnalysis.irradiation.datetime
        td1, td2 = td1.total_seconds(), td2.total_seconds()

        TGT = st_emission_line.target        
        std_smp = M.INAAnalysis.get_sample(standard_spectrum.get_sample())
        std_mass, std_umass, std_moist, std_umoist = std_smp.composition.mass, std_smp.composition.umass, std_smp.composition.moisture, std_smp.composition.umoisture
        std_w, std_uw = std_smp.composition.certificate.get(TGT, (0.0, 0.0))

        smp_smp = M.INAAnalysis.get_sample(sample_spectrum.get_sample())
        smp_mass, smp_umass, smp_moist, smp_umoist = smp_smp.composition.mass, smp_smp.composition.umass, smp_smp.composition.moisture, smp_smp.composition.umoisture
        smp_w, smp_uw = smp_smp.composition.certificate.get(TGT, (0.0, 0.0))
        
        m1, m2 = std_mass * (1 - std_moist) * std_w, smp_mass * (1 - smp_moist) * smp_w
        um1, um2 = m1 * np.sqrt(np.power(std_umass / std_mass, 2) + np.power(std_umoist / (1 - std_moist), 2) + np.power(std_uw / std_w, 2)), m2 * np.sqrt(np.power(smp_umass / smp_mass, 2) + np.power(smp_umoist / (1 - smp_moist), 2) + np.power(smp_uw / smp_w, 2))

        Gspm1 = (np1 * standard_spectrum.real_time) / (standard_spectrum.live_time * (1 - np.exp(-lbd * standard_spectrum.real_time)) * np.exp(-lbd * td1) * m1)

        Gspm2 = (np2 * sample_spectrum.real_time) / (sample_spectrum.live_time * (1 - np.exp(-lbd * sample_spectrum.real_time)) * np.exp(-lbd * td2) * m2)

        beta = (Gspm2 / Gspm1 -1) / _dd

        urnum = Gspm2 / Gspm1 * np.sqrt(np.power(unp1/np1, 2) + np.power(unp2/np2, 2) + np.power(um1/m1, 2) + np.power(um2/m2, 2)) / (Gspm2 / Gspm1 -1)

        ubeta = np.abs(beta * np.sqrt(np.power(urnum, 2) + np.power(_udd/_dd, 2)))

        return beta, ubeta

    def confirm_emission(self, sstand, previous_standard_item, emiss, selection_criterium='statistics'):
        #criteriums('statistics', 'earlier', 'later', 'shorter', 'longer')
        if previous_standard_item is None:
            return (sstand, emiss)
        else:
            spectrum, emissionidx = previous_standard_item[0], previous_standard_item[1]
            old_stats = spectrum[0].peak_list[emissionidx[0]][5] / spectrum[0].peak_list[emissionidx[0]][4]
            new_stats = sstand[0].peak_list[emiss[0]][5] / sstand[0].peak_list[emiss[0]][4]
            if selection_criterium == 'statistics' and new_stats < old_stats:
                return (sstand, emiss)
            elif selection_criterium == 'earlier' and sstand[0].datetime < spectrum[0].datetime:
                return (sstand, emiss)
            elif selection_criterium == 'later' and sstand[0].datetime > spectrum[0].datetime:
                return (sstand, emiss)
            elif selection_criterium == 'shorter' and sstand[0].real_time < spectrum[0].real_time:
                return (sstand, emiss)
            elif selection_criterium == 'longer' and sstand[0].real_time > spectrum[0].real_time:
                return (sstand, emiss)
            return previous_standard_item

    def manage_emissions(self, sus, ass, nnn, user_defined=False):
        if len(sus) == 0:
            return []
        elif len(sus) == 1:
            if user_defined and ass < 0:
                return []
            elif ass == -2:
                return []
            return [(nnn, sus[0])]
        else:
            if ass > -1:
                return [(nnn, sus[ass])]
            else:
                if user_defined or ass == -2:
                    return []
                return [(nnn, ss) for ss in sus]

    def go_back(self, parent, M):
        if self.secondary_window is not None:
            try:
                self.secondary_window.destroy()
            except:
                pass
        clear_window(parent)
        RelINRIM_MainWindow(parent, M)


class SetdistanceWindow:
    def __init__(self, parent, M, index, labeldis=None):
        self.index = index

        parent.title(f'{M.INAAnalysis.spectra[self.index].filename()} ({M.INAAnalysis.spectra[self.index].identity}) counting position')
        parent.resizable(False, False)
        self.hintlabel = tk.Label(parent, text='', anchor=tk.W)
        title_action_frame = tk.Frame(parent)

        tk.Label(title_action_frame, text='nominal counting position / mm', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        tk.Label(title_action_frame, text='δd / mm', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
        tk.Label(title_action_frame, text='u(δd) / mm', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)

        self.nominal_position = gui_things.FDiscreteSlider(title_action_frame, length=300, label_width=10, values=M.INAAnalysis.characterization._get_positions(), default=M.INAAnalysis.spectra[self.index].counting_position, unit_format='')
        self.nominal_position.grid(row=0, column=1, sticky=tk.W)

        self.deltad = gui_things.MutableVFSlider(title_action_frame, default=M.INAAnalysis.spectra[self.index].positioning_variability, length=300, label_width=10)
        self.deltad.grid(row=1, column=1, sticky=tk.W)

        self.udeltad = gui_things.FSlider(title_action_frame, length=300, label_width=10, default=M.INAAnalysis.spectra[self.index].uncertainty_positioning_variability, from_=0.00, to=5.00, resolution=0.02)
        self.udeltad.grid(row=2, column=1, sticky=tk.W)

        logo_confirmall = tk.PhotoImage(data=gui_things.PL_check)
        confirmall_B = gui_things.Button(title_action_frame, image=logo_confirmall, hint='confirm distances', hint_destination=self.hintlabel, command=lambda : self.confirmall(M, labeldis))
        confirmall_B.grid(row=3, column=0, columnspan=2, pady=5)
        confirmall_B.image = logo_confirmall

        title_action_frame.pack(anchor=tk.W, fill=tk.X, expand=True, pady=5)
        self.hintlabel.pack(anchor=tk.NW, fill=tk.X, expand=True)

    def confirmall(self, M, labeldis):
        pos = self.nominal_position.get()
        dd = self.deltad.get()
        udd = self.udeltad.get()

        M.INAAnalysis.spectra[self.index].counting_position = pos
        M.INAAnalysis.spectra[self.index].positioning_variability = dd
        M.INAAnalysis.spectra[self.index].uncertainty_positioning_variability = udd
        labeldis.set(M.INAAnalysis.spectra[self.index])


class PeaklistWindow:
    def __init__(self, parent, M, index, labelid=None, labelrole=None):
        self.SpectrumPlotSubwindow = None
        self.SpectrumProfileSubwindow = None
        self.PeakInformationSubwindow = None

        self.options = {'attach_to' : 'parent', 'resizable' : False}

        self.index = index

        self.labelid = labelid
        self.labelrole = labelrole

        localhintlabel = tk.Label(parent, text='', anchor=tk.W)

        parent.title(f'{M.INAAnalysis.spectra[self.index].filename()} ({M.INAAnalysis.spectra[self.index].identity})')
        parent.resizable(False, False)
        title_action_frame = tk.Frame(parent)

        logo_sprofile = tk.PhotoImage(data=gui_things.PL_frame_peak)
        B_show_spectrum_profile = gui_things.Button(title_action_frame, image=logo_sprofile, hint='display spectrum profile', hint_destination=localhintlabel, command=lambda : self.show_spectrum_plot(parent, M))
        B_show_spectrum_profile.grid(row=0, column=0, sticky=tk.W, padx=5)
        B_show_spectrum_profile.image = logo_sprofile

        ttk.Separator(title_action_frame, orient="vertical").grid(row=0, column=1, sticky=tk.NS, padx=3)

        logo_sinfo = tk.PhotoImage(data=gui_things.PL_letter_i)
        B_show_spectrum_info = gui_things.Button(title_action_frame, image=logo_sinfo, hint='general spectrum information', hint_destination=localhintlabel, command=lambda : self.show_spectrum_info(parent, M))
        B_show_spectrum_info.grid(row=0, column=2, sticky=tk.E, padx=5)
        B_show_spectrum_info.image = logo_sinfo

        ttk.Separator(title_action_frame, orient="vertical").grid(row=0, column=3, sticky=tk.NS, padx=3)
        logo_speakinfo = tk.PhotoImage(data=gui_things.PL_ggear)
        B_show_peak_info = gui_things.Button(title_action_frame, image=logo_speakinfo, hint='peak information', hint_destination=localhintlabel, command=lambda : self.select_item_from_tree(parent, M))
        B_show_peak_info.grid(row=0, column=4, sticky=tk.E, padx=5)
        B_show_peak_info.image = logo_speakinfo

        ttk.Separator(title_action_frame, orient="vertical").grid(row=0, column=5, sticky=tk.NS, padx=3)
        logo_options = tk.PhotoImage(data=gui_things.PL_none)
        B_show_options = gui_things.Button(title_action_frame, image=logo_options, hint='clear emissions assignment', hint_destination=localhintlabel)
        B_show_options.grid(row=0, column=6, sticky=tk.E, padx=5)
        B_show_options.image = logo_options

        title_action_frame.pack(anchor=tk.W, fill=tk.X, expand=True, pady=5)

        alldata = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text='peaklist'), relief='solid', bd=2, padx=4, pady=4)

        #Treeview!
        defwidth = 80
        columns = (('channel', defwidth, tk.W), ('E / keV', defwidth, tk.E), ('net area / 1', 90, tk.E), ('uncertainty', defwidth, tk.E), ('FWHM / 1', defwidth, tk.E), ('n', 40, tk.CENTER), ('emitter', 130, tk.CENTER))
        self.tree = ttk.Treeview(alldata, columns=[item[0] for item in columns], show='headings', selectmode='browse', height=M.settings.get('page height'))
        for item in columns:
            self.tree.heading(item[0], text=item[0])
            self.tree.column(item[0], anchor=item[2], stretch=False, minwidth=item[1], width=item[1])
        self.tree.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.X, expand=True)
        scroll = ttk.Scrollbar(alldata, orient="vertical", command=self.tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)

        alldata.pack(anchor=tk.NW, fill=tk.X, expand=True, padx=5, pady=5)

        localhintlabel.pack(anchor=tk.W, fill=tk.X, expand=True)

        #populate treeview
        nnn = 0
        for line, ass, sus in zip(M.INAAnalysis.spectra[self.index].peak_list, M.INAAnalysis.spectra[self.index].suspected_peaks, M.INAAnalysis.spectra[self.index].assigned_peaks):
            self.tree.insert('', 'end', iid=nnn, values=(f'{line[0]:.2f}',f'{line[2]:.2f}',f'{line[4]:.1f}',f'{line[5]/line[4]*100:.1f} %',f'{line[6]:.2f}',self.lenass(ass),self.stringass(ass,sus)))
            nnn += 1

        self.tree.bind('<Double-Button-1>', lambda e='<Double-Button-1>' : self.select_item_from_tree(parent, M))
        B_show_options.configure(command=lambda : self.clear_emission_assignment(parent, M))

    def clear_emission_assignment(self, parent, M):
        if messagebox.askyesno(title='Clear assigned emissions', message=f'\nAre you sure to clear\nall currently assigned emissions?\n', parent=parent):

            try:
                self.PeakInformationSubwindow.destroy()
                self.PeakInformationSubwindow = None
            except Exception:
                pass
            
            for nn, _ in enumerate(M.INAAnalysis.spectra[self.index].assigned_peaks):
                M.INAAnalysis.spectra[self.index].assigned_peaks[nn] = -1
                self.tree.set(nn, column='emitter', value='')

    def stringass(self, ass, sus):
        if sus > -1:
            return ass[sus].emission
        elif sus == -2:
            return 'X'
        return ''
    
    def lenass(self, ass):
        if len(ass) > 0:
            return f'({len(ass)})'
        return ''

    def show_peak_info(self, parent, M, item_index):
        self.item_index = item_index
        if self.PeakInformationSubwindow is not None:
            self.PeakInformationSubwindow.focus()
            self._update_peakinfo(M)
            self.emissionslist_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._select_CB_assigned(M))
            self.B_accept_emission.configure(command=lambda : self.confirm_emission_assignment(M))
            self.B_cancel_emission.configure(command=lambda : self.cancel_emission_assignment(M))
        else:
            self.PeakInformationSubwindow = tk.Toplevel(parent)
            self.PeakInformationSubwindow.title('Peak info')
            self.PeakInformationSubwindow.resizable(False, False)
            self.PeakInformationSubwindow.geometry(f'+{parent.winfo_rootx()}+{parent.winfo_rooty()}')
            mframe = tk.Frame(self.PeakInformationSubwindow)

            #self.allemissions = []
            #self.allemissionsavailable = []

            localhintlabel = tk.Label(mframe, text='', anchor=tk.W)

            datapeak = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='peak info'), relief='solid', bd=2, padx=4, pady=4)

            tk.Label(datapeak, text='channel:', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
            tk.Label(datapeak, text='energy:', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
            tk.Label(datapeak, text='net area:', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
            tk.Label(datapeak, text='coincidence:', anchor=tk.W).grid(row=3, column=0, sticky=tk.W)
            tk.Label(datapeak, text='escape from:', anchor=tk.W).grid(row=4, column=0, sticky=tk.W)
            
            self.channel_F = tk.Label(datapeak, text='', anchor=tk.W)
            self.channel_F.grid(row=0, column=1, sticky=tk.W, padx=8)
            self.energy_F = tk.Label(datapeak, text='', anchor=tk.W)
            self.energy_F.grid(row=1, column=1, sticky=tk.W, padx=8)
            self.netarea_F = tk.Label(datapeak, text='', anchor=tk.W)
            self.netarea_F.grid(row=2, column=1, sticky=tk.W, padx=8)
            self.coincidence_F = tk.Label(datapeak, text='', anchor=tk.W, width=60)
            self.coincidence_F.grid(row=3, column=1, sticky=tk.W, padx=8)
            self.escape_F = tk.Label(datapeak, text='', anchor=tk.W, width=60)
            self.escape_F.grid(row=4, column=1, sticky=tk.W, padx=8)


            datapeak.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

            peakid = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='identity'), relief='solid', bd=2, padx=4, pady=4)
            tk.Label(peakid, text='emission', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
            self.emissionslist_CB = gui_things.Combobox(peakid, state='readonly', width=18)
            self.emissionslist_CB['values'] = []#
            self.emissionslist_CB.grid(row=0, column=1, columnspan=2, padx=5)
            self.how_many_suspects = tk.Label(peakid, text='(0)')
            self.how_many_suspects.grid(row=0, column=3, sticky=tk.W)

            nn = 2
            width=10

            tk.Label(peakid, text='TARGET', width=width, anchor=tk.W).grid(row=nn, column=0, rowspan=2, sticky=tk.W)
            tk.Label(peakid, text='element', width=width).grid(row=nn, column=1, sticky=tk.W)
            tk.Label(peakid, text='isotope', width=width).grid(row=nn, column=2, sticky=tk.W)
            tk.Label(peakid, text='Q0 / 1', width=width).grid(row=nn, column=3, sticky=tk.W)
            tk.Label(peakid, text='urQ0 / %', width=width).grid(row=nn, column=4, sticky=tk.W)

            nn += 1

            self.Telement_F = tk.Label(peakid, text='', width=width)
            self.Telement_F.grid(row=nn, column=1, sticky=tk.W)
            self.Tisotope_F = tk.Label(peakid, text='', width=width)
            self.Tisotope_F.grid(row=nn, column=2, sticky=tk.W)
            self.TQ0_F = tk.Label(peakid, text='', width=width)
            self.TQ0_F.grid(row=nn, column=3, sticky=tk.W)
            self.TurQ0_F = tk.Label(peakid, text='', width=width)
            self.TurQ0_F.grid(row=nn, column=4, sticky=tk.W)

            nn += 1
            tk.Frame(peakid).grid(row=nn, column=0, pady=5)
            nn += 1

            tk.Label(peakid, text='EMITTER', width=width, anchor=tk.W).grid(row=nn, column=0, rowspan=2, sticky=tk.W)
            tk.Label(peakid, text='isotope', width=width).grid(row=nn, column=1, sticky=tk.W)
            tk.Label(peakid, text='Eγ / keV', width=width).grid(row=nn, column=2, sticky=tk.W)
            tk.Label(peakid, text='COI', width=width).grid(row=nn, column=3, sticky=tk.W)
            tk.Label(peakid, text='γ-yield / %', width=width).grid(row=nn, column=4, sticky=tk.W)

            nn += 1

            self.Eisotope_F = tk.Label(peakid, text='', width=width)
            self.Eisotope_F.grid(row=nn, column=1, sticky=tk.W)
            self.Eenergy_F = tk.Label(peakid, text='', width=width)
            self.Eenergy_F.grid(row=nn, column=2, sticky=tk.W)
            self.ECOI_F = tk.Label(peakid, text='', width=width)
            self.ECOI_F.grid(row=nn, column=3, sticky=tk.W)
            self.Eyield_F = tk.Label(peakid, text='', width=width)
            self.Eyield_F.grid(row=nn, column=4, sticky=tk.W)

            nn += 1
            tk.Frame(peakid).grid(row=nn, column=0, pady=5)
            nn += 1

            tk.Label(peakid, text='DECAY', width=width, anchor=tk.W).grid(row=nn, column=0, sticky=tk.W)
            self.decaytype_F = tk.Label(peakid, text='')
            self.decaytype_F.grid(row=nn, column=1, sticky=tk.W)
            
            nn += 1
            tk.Label(peakid, text='nuclide', width=width).grid(row=nn, column=1, sticky=tk.W)
            tk.Label(peakid, text='half-life', width=width).grid(row=nn, column=2, sticky=tk.W)

            nn += 1
            self.signdaugI_F = tk.Label(peakid, text='', anchor=tk.E)
            self.signdaugI_F.grid(row=nn, column=0, sticky=tk.E)
            self.nucldaugI_F = tk.Label(peakid, text='')
            self.nucldaugI_F.grid(row=nn, column=1)
            self.hldaugI_F = tk.Label(peakid, text='')
            self.hldaugI_F.grid(row=nn, column=2)
            nn += 1
            self.signdaugII_F = tk.Label(peakid, text='', anchor=tk.E)
            self.signdaugII_F.grid(row=nn, column=0, sticky=tk.E)
            self.nucldaugII_F = tk.Label(peakid, text='')
            self.nucldaugII_F.grid(row=nn, column=1)
            self.hldaugII_F = tk.Label(peakid, text='')
            self.hldaugII_F.grid(row=nn, column=2)
            nn += 1
            self.signdaugIII_F = tk.Label(peakid, text='', anchor=tk.E)
            self.signdaugIII_F.grid(row=nn, column=0, sticky=tk.E)
            self.nucldaugIII_F = tk.Label(peakid, text='')
            self.nucldaugIII_F.grid(row=nn, column=1)
            self.hldaugIII_F = tk.Label(peakid, text='')
            self.hldaugIII_F.grid(row=nn, column=2)

            peakid.grid(row=1, column=0, sticky=tk.NW)

            otherpeaks = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='other peaks from same target'), relief='solid', bd=2, padx=4, pady=4)

            self.otherpeaksovervew_LB = gui_things.ScrollableListbox(otherpeaks, width=50, height=14, selectmode=tk.SINGLE)
            self.otherpeaksovervew_LB.grid(row=1, column=0, sticky=tk.NSEW)
            self._true_color, self._false_color = '#FFFFFF', '#ff474c'
            
            otherpeaks.grid(row=1, column=1, sticky=tk.NSEW, padx=5)

            buttonframe = tk.Frame(mframe)

            logo_confirm = tk.PhotoImage(data=gui_things.PL_check)
            self.B_accept_emission = gui_things.Button(buttonframe, image=logo_confirm, hint='Confirm emission assignment!', hint_destination=localhintlabel, command=lambda : self.confirm_emission_assignment(M))
            self.B_accept_emission.grid(row=0, column=0)
            self.B_accept_emission.image = logo_confirm

            logo_cancel = tk.PhotoImage(data=gui_things.PL_none)
            self.B_cancel_emission = gui_things.Button(buttonframe, image=logo_cancel, hint='Cancel emission assignment!', hint_destination=localhintlabel, command=lambda : self.cancel_emission_assignment(M))
            self.B_cancel_emission.grid(row=0, column=1)
            self.B_cancel_emission.image = logo_cancel

            ttk.Separator(buttonframe, orient=tk.VERTICAL).grid(row=0, column=2, sticky=tk.NS, padx=3)

            logo_confirm_all = tk.PhotoImage(data=gui_things.PL_letter_forall)
            self.B_accept_emission_all = gui_things.Button(buttonframe, image=logo_confirm_all, hint='Confirm also selected emissions from same target!', hint_destination=localhintlabel, command=lambda : self.confirm_all_emission_assignment(M))
            self.B_accept_emission_all.grid(row=0, column=3)
            self.B_accept_emission_all.image = logo_confirm_all

            ttk.Separator(buttonframe, orient=tk.VERTICAL).grid(row=0, column=4, sticky=tk.NS, padx=3)

            logo_exclude_selection = tk.PhotoImage(data=gui_things.PL_interdit)
            self.B_exclude_Selection = gui_things.Button(buttonframe, image=logo_exclude_selection, hint='Exclude this peak from elaboration!', hint_destination=localhintlabel, command=lambda : self.exclude_current_peak(M))
            self.B_exclude_Selection.grid(row=0, column=5)
            self.B_exclude_Selection.image = logo_exclude_selection

            buttonframe.grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)

            localhintlabel.grid(row=3, column=0, columnspan=2, sticky=tk.EW)

            mframe.pack(anchor=tk.NW, padx=5, pady=5)

            self._update_peakinfo(M)

            self.emissionslist_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._select_CB_assigned(M))

            self.otherpeaksovervew_LB.listbox.bind('<Double-Button-1>', lambda e='<Double-Button-1>' : self.switch_selection())

            self.PeakInformationSubwindow.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.PeakInformationSubwindow))

    def exclude_current_peak(self, M):
        if len(M.INAAnalysis.spectra[self.index].suspected_peaks[self.item_index]) > 0:
            M.INAAnalysis.spectra[self.index].assigned_peaks[self.item_index] = -2
            self.tree.set(self.item_index, column='emitter', value='X')

    def confirm_emission_assignment(self, M):
        if self.emissionslist_CB.get() != '':
            idx = self.emissionslist_CB['values'].index(self.emissionslist_CB.get())
            M.INAAnalysis.spectra[self.index].assigned_peaks[self.item_index] = idx
            self.tree.set(self.item_index, column='emitter', value=M.INAAnalysis.spectra[self.index].suspected_peaks[self.item_index][idx].emission)

    def confirm_all_emission_assignment(self, M):
        if self.emissionslist_CB.get() != '':
            idx = self.emissionslist_CB['values'].index(self.emissionslist_CB.get())
            M.INAAnalysis.spectra[self.index].assigned_peaks[self.item_index] = idx
            self.tree.set(self.item_index, column='emitter', value=M.INAAnalysis.spectra[self.index].suspected_peaks[self.item_index][idx].emission)

            for check, emi_data in zip(self.allemissionsavailable, self.allemissions):
                if check:
                    data_index, actual_data = emi_data
                    data_idx = M.INAAnalysis.spectra[self.index].suspected_peaks[data_index].index(actual_data)
                    M.INAAnalysis.spectra[self.index].assigned_peaks[data_index] = data_idx
                    self.tree.set(data_index, column='emitter', value=M.INAAnalysis.spectra[self.index].suspected_peaks[data_index][data_idx].emission)

            self._select_CB_assigned(M)

    def cancel_emission_assignment(self, M):
        self.emissionslist_CB.set('')
        M.INAAnalysis.spectra[self.index].assigned_peaks[self.item_index] = -1
        self.tree.set(self.item_index, column='emitter', value='')
        self._update_peakinfo(M)

    def _update_peakinfo(self, M):
        line = M.INAAnalysis.spectra[self.index].peak_list[self.item_index]
        self.channel_F.configure(text=f'{line[0]:.2f}')
        self.energy_F.configure(text=f'{line[2]:.2f} keV')
        self.netarea_F.configure(text=f'{line[4]:.1f} ({line[5]:.1f}) [{line[5]/line[4]*100:.2f} %], count rate: {line[4]/M.INAAnalysis.spectra[self.index].live_time:.2f} s⁻¹')

        coincidence = M.INAAnalysis.spectra[self.index].check_for_coincidence(line[2], comp_net_area=line[4])
        singleescape, doubleescape = M.INAAnalysis.spectra[self.index].check_for_escapes(line[2], peakthreshold=line[4])

        self.coincidence_F.configure(text=', '.join([f"{con[0]:.1f} + {con[1]:.1f}" for con in coincidence]))
        self.escape_F.configure(text=', '.join([f"{en:.1f} (SE)" for en in singleescape] + [f"{en:.1f} (DE)" for en in doubleescape]))

        self.emissionslist_CB['values'] = [item.emission for item in M.INAAnalysis.spectra[self.index].suspected_peaks[self.item_index]]
        if M.INAAnalysis.spectra[self.index].assigned_peaks[self.item_index] > -1:
            set_text = self.emissionslist_CB['values'][M.INAAnalysis.spectra[self.index].assigned_peaks[self.item_index]]
        else:
            set_text = ''    
        self.emissionslist_CB.set(set_text)
        self.how_many_suspects.configure(text=f'({len(M.INAAnalysis.spectra[self.index].suspected_peaks[self.item_index])})')

        if M.INAAnalysis.spectra[self.index].assigned_peaks[self.item_index] > -1:
            infos = M.INAAnalysis.spectra[self.index].suspected_peaks[self.item_index][M.INAAnalysis.spectra[self.index].assigned_peaks[self.item_index]]
        else:
            infos = None

        self._update_assignedinfo(infos, M)

    def _select_CB_assigned(self, M):
        index = self.emissionslist_CB['values'].index(self.emissionslist_CB.get())
        infos = M.INAAnalysis.spectra[self.index].suspected_peaks[self.item_index][index]
        self._update_assignedinfo(infos, M, index)

    def recvalues(self, value, par):
        none = (lambda x : np.nan, '.2f')
        parameters = {'Q0':(lambda x : '20', '.2f'), 'Er':(lambda x : '50', '.2f'), 'k0':(lambda x : '5', '.2f'), 'gy':(lambda x : str(x), '.3f')}
        opt = parameters.get(par, none)
        try:
            value = float(value)
            return format(value,opt[1])
        except ValueError:
            value = opt[0](value)
            rec = ' (NR)'
            if par == 'gy':
                rec = ''
            return f'{value}{rec}'

    def get_data_from_emission(self, M, idx, emission):
        np, unp = M.INAAnalysis.spectra[self.index].peak_list[idx][4], M.INAAnalysis.spectra[self.index].peak_list[idx][5]
        EE = emission.energy
        if isinstance(emission.line["GY"], str) and emission.line["GY"] != '':
            gy, ugy = emission.line["GY"].split()
            ugy = ugy.replace('(', '').replace(')', '')
            gyp = emission.line["GY"].split()[0].replace('.', '')
        else:
            gy = emission.line["GY"]
            ugy = 0.0
            gyp = 100
        try:
            gy = float(gy) / 100
            ugy = gy * float(ugy) / float(gyp)
        except ValueError:
            gy, ugy = 1.0, 0.0
        return np, unp, EE, gy, ugy

    def _update_assignedinfo(self, infos, M, index=-1):
        current_emission = None
        self.allemissions = []
        self.allemissionsavailable = []

        check_consistency_of_emissions = M.settings.get('check internal consistency')
        Z_value_limit = M.settings.get('z limit')

        if infos is not None:
            self.Telement_F.configure(text=f'{infos.target}')
            self.Tisotope_F.configure(text=f'{infos.line["T_Z"]}-{infos.line["T_A"]}')
            self.TQ0_F.configure(text=f'{infos.line["Q0"]:.2f}')
            self.TurQ0_F.configure(text=self.recvalues(infos.line["uQ0"],'Q0'))
            self.Eisotope_F.configure(text=f'{infos.line["emitter"]}-{infos.line["A"]}{infos._state(infos.line["state"])}')
            self.Eenergy_F.configure(text=f'{infos.energy:.1f}')
            self.Eyield_F.configure(text=self.recvalues(infos.line["GY"],'gy'))
            self.decaytype_F.configure(text=infos.line["type"])

            cascade = self.manage_cascade_line([[infos.line["C1"], infos.line["C1_t1/2"], infos.line["C1_unit"]],
                [infos.line["C2"], infos.line["C2_t1/2"], infos.line["C2_unit"]],
                [infos.line["C3"], infos.line["C3_t1/2"], infos.line["C3_unit"]]])

            self.allemissions = [(idx, emis) for idx, sus in enumerate(M.INAAnalysis.spectra[self.index].suspected_peaks) for emis in sus if emis.target == infos.target]
            for npop, item in enumerate(self.allemissions):
                if item[1] == infos:
                    current_emission = self.allemissions.pop(npop)
            self.allemissionsavailable = [True] * len(self.allemissions)
        
        else:
            self.Telement_F.configure(text='')
            self.Tisotope_F.configure(text='')
            self.TQ0_F.configure(text='')
            self.TurQ0_F.configure(text='')
            self.Eisotope_F.configure(text='')
            self.Eenergy_F.configure(text='')
            self.ECOI_F.configure(text='')
            self.Eyield_F.configure(text='')
            self.decaytype_F.configure(text='')

            cascade = [[''] * 4] * 3

        cline = cascade[0]
        self.signdaugI_F.configure(text=cline[0])
        self.nucldaugI_F.configure(text=cline[1])
        self.hldaugI_F.configure(text=cline[2])
        cline = cascade[1]
        self.signdaugII_F.configure(text=cline[0])
        self.nucldaugII_F.configure(text=cline[1])
        self.hldaugII_F.configure(text=cline[2])
        cline = cascade[2]
        self.signdaugIII_F.configure(text=cline[0])
        self.nucldaugIII_F.configure(text=cline[1])
        self.hldaugIII_F.configure(text=cline[2])

        #calculations
        Zs = []
        if current_emission is not None:
            np_m, unp_m, Em, gYm, ugYm = self.get_data_from_emission(M, *current_emission)

            for nn, item in enumerate(self.allemissions):
                np_a, unp_a, Ea, gYa, ugYa = self.get_data_from_emission(M, *item)
                if M.INAAnalysis.characterization is not None:
                    kede, ukede = M.INAAnalysis.characterization.reference_curve._div(Em, Ea)
                else:
                    kede, ukede = 1.0E-6, 0.0
                Cy = (np_a / np_m) * (gYm / gYa) * kede
                Cuy = Cy * np.sqrt(np.power(unp_a / np_a,2) + np.power(unp_m / np_m,2) + np.power(ugYa / gYa,2) + np.power(ugYm / gYm,2) + np.power(ukede / kede,2))

                logic_outcome = abs((Cy-1)/Cuy) < Z_value_limit
                if check_consistency_of_emissions:
                    Zs.append(logic_outcome)
                else:
                    Zs.append(True)

        strline = []
        for nnn, line in enumerate(self.allemissions):
            if M.INAAnalysis.spectra[self.index].assigned_peaks[line[0]] == -1:
                assgn = ''
                self.allemissionsavailable[nnn] = Zs[nnn]
            elif M.INAAnalysis.spectra[self.index].assigned_peaks[line[0]] == -2:
                assgn = 'X'
                self.allemissionsavailable[nnn] = False
            else:
                sidx = M.INAAnalysis.spectra[self.index].assigned_peaks[line[0]]
                sinfos = M.INAAnalysis.spectra[self.index].suspected_peaks[line[0]][sidx]
                assgn = f'({sinfos.emission})'
                self.allemissionsavailable[nnn] = False
            strline.append(f'{str.ljust(str(nnn+1),4)}{str.ljust(line[1].emission, 30)}  {assgn}')

        self.otherpeaksovervew_LB._update(strline)
        self.otherpeaksovervew_LB._colored_update(self.allemissionsavailable, self._true_color, self._false_color)

    def switch_selection(self):
        emission_index = self.otherpeaksovervew_LB.curselection()
        try:
            emission_index = emission_index[0]
        except IndexError:
            emission_index = None

        if emission_index is not None:
            self.allemissionsavailable[emission_index] = not self.allemissionsavailable[emission_index]
            self.otherpeaksovervew_LB._colored_update(self.allemissionsavailable, self._true_color, self._false_color)

            self.otherpeaksovervew_LB.listbox.selection_clear(emission_index)

    def calculate_mf_from_same_emitter(self, np_a, np_m, k0_a, COI_a, k0_m, COI_m, d, dd, d0_a, d0_m, height):
        y = (np_a * k0_m * COI_m) / (np_m * k0_a * COI_a) * np.exp(0) * ((d - d0_m) / (d + dd - d0_m))**2 / ((d - d0_a) / (d + dd - d0_a))**2 * (1 + height / (d + dd - d0_a)) / (1 + height / (d + dd - d0_m))
        return y, 0.2
    
    def manage_cascade_line(self, datalist):
        cvlist, voidlist = [], []
        for line in datalist:
            if line[0] != '':
                cvline = ['↓', line[0], f'{line[1]:.3f} {line[2]}']
                cvlist.append(cvline)
            else:
                voidlist.append(['', '', ''])
        return cvlist + voidlist

    def posplot(self, parent, screen_width, screen_height):
        values = ('peak', 'parent', 'info', 'none')

        if self.options['attach_to'] == values[0]:
            if self.PeakInformationSubwindow is not None:
                self.SpectrumPlotSubwindow.geometry(f'+{self.PeakInformationSubwindow.winfo_rootx()}+{self.PeakInformationSubwindow.winfo_rooty()+self.PeakInformationSubwindow.winfo_height()}')

        elif self.options['attach_to'] == values[1]:
            if parent.winfo_rootx()+parent.winfo_width() < screen_width:
                self.SpectrumPlotSubwindow.geometry(f'+{parent.winfo_rootx()+parent.winfo_width()}+{parent.winfo_rooty()}')
            else:
                self.SpectrumPlotSubwindow.geometry(f'+{parent.winfo_rootx()}+{parent.winfo_rooty()}')
        
        elif self.options['attach_to'] == values[2]:
            if self.SpectrumProfileSubwindow is not None:
                self.SpectrumPlotSubwindow.geometry(f'+{self.SpectrumProfileSubwindow.winfo_rootx()}+{self.SpectrumProfileSubwindow.winfo_rooty()+self.SpectrumProfileSubwindow.winfo_height()}')

    def show_spectrum_plot(self, parent, M, centroid=None):
        if self.SpectrumPlotSubwindow is not None:
            self.SpectrumPlotSubwindow.focus()
        else:
            if M.INAAnalysis.spectra[self.index].counts is not None:
                self.SpectrumPlotSubwindow = tk.Toplevel(parent)
                self.SpectrumPlotSubwindow.title('Spectrum plot')
                if self.options['resizable']:
                    res = (True, True)
                else:
                    res = (False, False)
                self.SpectrumPlotSubwindow.resizable(*res)
                screen_width, screen_height = M.winfo_screenwidth(), M.winfo_screenheight()
                self.posplot(parent, screen_width, screen_height)

                #as relative
                zoom_range = [M.INAAnalysis.spectra[self.index].number_of_channels()//div for div in (1000, 500, 400, 300, 200, 100, 75, 50, 40, 20, 10, 5, 2, 1) if M.INAAnalysis.spectra[self.index].number_of_channels()//div > 10]
                self.SpectrumPlotSubwindow.figure = Figure(figsize=(8, 4))
                self.SpectrumPlotSubwindow.figure.patch.set_alpha(0.0)
                self.SpectrumPlotSubwindow.ax = self.SpectrumPlotSubwindow.figure.add_subplot(111)
                Figur = tk.Frame(self.SpectrumPlotSubwindow)
                Figur.grid(row=0, column=0, sticky=tk.NSEW)
                self.SpectrumPlotSubwindow.canvas = FigureCanvasTkAgg(self.SpectrumPlotSubwindow.figure, master=Figur)
                self.SpectrumPlotSubwindow.canvas.draw()
                self.SpectrumPlotSubwindow.canvas.get_tk_widget().configure(background=self.SpectrumPlotSubwindow.cget('bg'))
                self.SpectrumPlotSubwindow.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

                xlimits = (0, M.INAAnalysis.spectra[self.index].number_of_channels())
                ylimits = (1, np.max(M.INAAnalysis.spectra[self.index].counts)*1.10+10)

                plot = self.SpectrumPlotSubwindow.ax.plot(np.linspace(0.5,xlimits[1]+0.5,num=xlimits[1]), M.INAAnalysis.spectra[self.index].counts, marker='o', linestyle='-', color='k', linewidth=0.5, markersize=3, markerfacecolor=M.settings.get('color01'), zorder=9)

                background = self.SpectrumPlotSubwindow.ax.plot(np.linspace(0.5,xlimits[1]+0.5,num=xlimits[1]), np.array([np.nan] * xlimits[1]), marker='', linestyle='-', color=M.settings.get('color02'), linewidth=0.5, zorder=3)
                
                otherplot = self.SpectrumPlotSubwindow.ax.plot(np.linspace(0.5,xlimits[1]+0.5,num=xlimits[1]), np.array([np.nan] * xlimits[1]), marker='o', linestyle='-', color='k', linewidth=0.5, markersize=3, markerfacecolor=M.settings.get('color03'), zorder=6)

                self.lines = [plot, background, otherplot]

                #limits
                self.SpectrumPlotSubwindow.ax.set_xlim(*xlimits)
                self.SpectrumPlotSubwindow.ax.set_ylim(*ylimits)
                self.SpectrumPlotSubwindow.ax.set_yscale('log', nonposy='clip')

                self.SpectrumPlotSubwindow.ax.set_ylabel('counts')
                self.SpectrumPlotSubwindow.ax.set_xlabel('channel')

                self.SpectrumPlotSubwindow.figure.tight_layout()
                self.SpectrumPlotSubwindow.canvas.draw()

                self.SpectrumPlotSubwindow.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.SpectrumPlotSubwindow))

                cid = self.SpectrumPlotSubwindow.canvas.mpl_connect('scroll_event', lambda event='scroll_event' : self.on_scroll(event, M))
                sid = self.SpectrumPlotSubwindow.canvas.mpl_connect('motion_notify_event', lambda event='motion_notify_event' : self.on_motion(event, M))

                infoframe = tk.Frame(self.SpectrumPlotSubwindow)
                zoomf = tk.Frame(infoframe)
                tk.Label(zoomf, text='spectrum view width').pack(side=tk.LEFT, anchor=tk.W)
                self.zoomslider = gui_things.Combobox(zoomf, width=8, state='readonly')
                self.zoomslider['values'] = zoom_range
                self.zoomslider.set(zoom_range[-1])
                self.zoomslider.pack(side=tk.RIGHT, anchor=tk.W, padx=5)
                zoomf.pack(side=tk.LEFT, anchor=tk.W)
                self.coordinates = tk.Label(infoframe, text='')
                self.coordinates.pack(side=tk.RIGHT, anchor=tk.E)
                infoframe.grid(row=1, column=0, sticky=tk.EW)

                optionframe = tk.LabelFrame(self.SpectrumPlotSubwindow, labelwidget=tk.Label(self.SpectrumPlotSubwindow, text='options'), relief='solid', bd=2, padx=4, pady=4)#options
                self.autoadjustyV = tk.IntVar(self.SpectrumPlotSubwindow)
                autoadjustyCX = tk.Checkbutton(optionframe, onvalue=1, offvalue=0, variable=self.autoadjustyV, text='autoadjust y axis')
                autoadjustyCX.pack(anchor=tk.W)
                self.autoadjustyV.set(0)
                self.display_backgroundV = tk.IntVar(self.SpectrumPlotSubwindow)
                display_backgroundCX = tk.Checkbutton(optionframe, onvalue=1, offvalue=0, variable=self.display_backgroundV, text='display background', command=lambda : self.display_background(M))
                display_backgroundCX.pack(anchor=tk.W)
                self.display_backgroundV.set(0)
                tk.Frame(optionframe).pack(pady=4)
                tk.Label(optionframe, text='comparison').pack(anchor=tk.W)
                self.other_plot_CB = gui_things.Combobox(optionframe, width=15, state='readonly')
                self.other_plot_CB['values'] = [spectrum.filename() if nn!=self.index else '' for nn, spectrum in enumerate(M.INAAnalysis.spectra)]
                self.other_plot_CB.pack(fill=tk.X)
                self.other_plot_CB.set(self.other_plot_CB['values'][self.index])
                tk.Frame(optionframe).pack(pady=4)
                self.showlegendV = tk.IntVar(self.SpectrumPlotSubwindow)
                showlegendCX = tk.Checkbutton(optionframe, onvalue=1, offvalue=0, variable=self.showlegendV, text='display legend', command=lambda : self.display_legend(M))
                showlegendCX.pack(anchor=tk.W)
                optionframe.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW, padx=5, pady=5)

                self.other_plot_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.display_other_spectrum_plot(M))

    def on_motion(self, event, M):
        #mouse motion on spectrum profile
        text=''
        if event.xdata is not None and event.ydata is not None:
            x = int(event.xdata)
            if x >= 0 and x < M.INAAnalysis.spectra[self.index].number_of_channels():
                y = int(M.INAAnalysis.spectra[self.index].counts[x])
                if M.INAAnalysis.characterization is not None:
                    EE = M.INAAnalysis.characterization._get_energy_point(x)
                    EE = format(EE, '.1f')
                else:
                    EE = None
                text = f'channel={x}, energy={EE} keV, counts={y}'
        self.coordinates.configure(text=text)

    def display_legend(self, M):
        if self.showlegendV.get() == 0:
            self.SpectrumPlotSubwindow.ax.get_legend().set_visible(False)
        else:
            handles, labels = [self.lines[0][0]], ['spectrum']
            if self.display_backgroundV.get() == 1:
                handles.append(self.lines[1][0])
                labels.append('background')
            if self.other_plot_CB.get() != '':
                handles.append(self.lines[2][0])
                labels.append('other spectrum')
            self.SpectrumPlotSubwindow.ax.legend(handles, labels, frameon=False)
        self.SpectrumPlotSubwindow.canvas.draw()

    def display_background(self, M):
        if self.display_backgroundV.get() == 0:
            self.lines[1][0].set_ydata(np.array([np.nan] * M.INAAnalysis.spectra[self.index].number_of_channels()))
            self.SpectrumPlotSubwindow.canvas.draw()
        else:
            if M.INAAnalysis.background_spectrum is not None and M.INAAnalysis.spectra[self.index].number_of_channels() == M.INAAnalysis.background_spectrum.number_of_channels():
                self.lines[1][0].set_ydata(M.INAAnalysis.background_spectrum.counts / M.INAAnalysis.background_spectrum.live_time * M.INAAnalysis.spectra[self.index].live_time)
                self.SpectrumPlotSubwindow.canvas.draw()
            else:
                self.lines[1][0].set_ydata(np.array([np.nan] * M.INAAnalysis.spectra[self.index].number_of_channels()))
                self.SpectrumPlotSubwindow.canvas.draw()

    def display_other_spectrum_plot(self, M):
        if self.other_plot_CB.get() == '':
            self.lines[2][0].set_ydata(np.array([np.nan] * M.INAAnalysis.spectra[self.index].number_of_channels()))
            self.SpectrumPlotSubwindow.canvas.draw()
        else:
            idx = self.other_plot_CB['values'].index(self.other_plot_CB.get())
            if M.INAAnalysis.spectra[idx].number_of_channels() == M.INAAnalysis.spectra[self.index].number_of_channels():
                self.lines[2][0].set_ydata(M.INAAnalysis.spectra[idx].counts)
                self.SpectrumPlotSubwindow.canvas.draw()

    def re_center_plot(self, peak_centroid, M):
        if self.SpectrumPlotSubwindow is not None:

            centroid = peak_centroid

            screen_width = int(self.zoomslider.get())
            new_limits = (int(centroid - screen_width/2), int(centroid - screen_width/2 + screen_width))
            if new_limits[0] < 0:
                new_limits = (0, screen_width)
            elif new_limits[1] > M.INAAnalysis.spectra[self.index].number_of_channels():
                new_limits = (M.INAAnalysis.spectra[self.index].number_of_channels()- screen_width, M.INAAnalysis.spectra[self.index].number_of_channels())
            self.SpectrumPlotSubwindow.ax.set_xlim(*new_limits)
            if self.autoadjustyV.get() == True:
                ylimits = (1, np.max(M.INAAnalysis.spectra[self.index].counts[new_limits[0]:new_limits[1]])*1.10+10)
                self.SpectrumPlotSubwindow.ax.set_ylim(*ylimits)

            self.SpectrumPlotSubwindow.canvas.draw()

    def on_scroll(self, event, M):
        #Scroll spectrum profile
        if event.xdata is not None and event.ydata is not None:
            current_limits = self.SpectrumPlotSubwindow.ax.get_xlim()

            centroid, diff = int((current_limits[0]+current_limits[1])/2), abs(int(event.xdata-(current_limits[0]+(current_limits[1]-current_limits[0])/2)))

            screen_width = int(self.zoomslider.get())
            new_limits = (int(centroid - screen_width/2 + event.step*diff), int(centroid - screen_width/2 + screen_width + event.step*diff))
            if new_limits[0] < 0:
                new_limits = (0, screen_width)
            elif new_limits[1] > M.INAAnalysis.spectra[self.index].number_of_channels():
                new_limits = (M.INAAnalysis.spectra[self.index].number_of_channels()- screen_width, M.INAAnalysis.spectra[self.index].number_of_channels())
            self.SpectrumPlotSubwindow.ax.set_xlim(*new_limits)
            if self.autoadjustyV.get() == True:
                ylimits = (1, np.max(M.INAAnalysis.spectra[self.index].counts[new_limits[0]:new_limits[1]])*1.10+10)
                self.SpectrumPlotSubwindow.ax.set_ylim(*ylimits)

            self.SpectrumPlotSubwindow.canvas.draw()
            self.on_motion(event, M)

    def show_spectrum_info(self, parent, M):
        if self.SpectrumProfileSubwindow is not None:
            self.SpectrumProfileSubwindow.focus()
        else:
            self.SpectrumProfileSubwindow = tk.Toplevel(parent)
            self.SpectrumProfileSubwindow.title(f'Spectrum info ({M.INAAnalysis.spectra[self.index].filename()})')
            self.SpectrumProfileSubwindow.resizable(False, False)
            self.SpectrumProfileSubwindow.geometry(f'+{parent.winfo_rootx()}+{parent.winfo_rooty()}')
            mframe = tk.Frame(self.SpectrumProfileSubwindow)

            localhintlabel = tk.Label(mframe, text='', anchor=tk.W)

            info_frame = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='info'), relief='solid', bd=2, padx=4, pady=4)

            tk.Label(info_frame, text='filename:', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
            tk.Label(info_frame, text='start acquisition:', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
            tk.Label(info_frame, text='real time:', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
            tk.Label(info_frame, text='live time:', anchor=tk.W).grid(row=3, column=0, sticky=tk.W)
            tk.Label(info_frame, text='dead time:', anchor=tk.W).grid(row=4, column=0, sticky=tk.W)
            tk.Label(info_frame, text='sample:', anchor=tk.W).grid(row=5, column=0, sticky=tk.W)
            tk.Label(info_frame, text='role:', anchor=tk.W).grid(row=7, column=0, sticky=tk.W)
            tk.Label(info_frame, text='path:', anchor=tk.W).grid(row=8, column=0, sticky=tk.W)
            tk.Label(info_frame, text='peaklist lines:', anchor=tk.W).grid(row=10, column=0, sticky=tk.W)
            tk.Label(info_frame, text='prominent peaks:', anchor=tk.W).grid(row=11, column=0, sticky=tk.W)

            self.filenameL = tk.Label(info_frame, text='', anchor=tk.W)
            self.filenameL.grid(row=0, column=1, sticky=tk.W, padx=8)
            self.startacquisitionL = tk.Label(info_frame, text='', anchor=tk.W)
            self.startacquisitionL.grid(row=1, column=1, sticky=tk.W, padx=8)
            self.realL = tk.Label(info_frame, text='', anchor=tk.W)
            self.realL.grid(row=2, column=1, sticky=tk.W, padx=8)
            self.liveL = tk.Label(info_frame, text='', anchor=tk.W)
            self.liveL.grid(row=3, column=1, sticky=tk.W, padx=8)
            self.deadL = tk.Label(info_frame, text='', anchor=tk.W)
            self.deadL.grid(row=4, column=1, sticky=tk.W, padx=8)
            self.sampleCB = ttk.Combobox(info_frame, width=20, state='readonly')
            self.sampleCB.grid(row=5, column=1, sticky=tk.W, padx=8)
            values = [item.name for item in M.INAAnalysis.samples_id]
            self.sampleCB['values'] = values
            if M.INAAnalysis.spectra[self.index].sample is not None:
                self.sampleCB.set(M.INAAnalysis.spectra[self.index].sample)

            logo_assign_all_peaks_based_on_sample = tk.PhotoImage(data=gui_things.PL_gearpeak)
            B_autoselect_peaks = gui_things.Button(info_frame, image=logo_assign_all_peaks_based_on_sample, hint='automatic peaks identification', hint_destination=localhintlabel, command=lambda : self._autoselect_peaks(M))
            B_autoselect_peaks.grid(row=5, column=2, sticky=tk.W, padx=8)
            B_autoselect_peaks.image = logo_assign_all_peaks_based_on_sample
            
            logo_check_intense_peaks = tk.PhotoImage(data=gui_things.PL_infopeak)
            B_check_intense_peaks = gui_things.Button(info_frame, image=logo_check_intense_peaks, hint='alert for intense peaks', hint_destination=localhintlabel, command=lambda : self._peak_intensity_alert(M))
            B_check_intense_peaks.grid(row=11, column=2, sticky=tk.W, padx=8)
            B_check_intense_peaks.image = logo_check_intense_peaks

            self.roleCB = tk.Label(info_frame, text='')
            self.roleCB.grid(row=7, column=1, sticky=tk.W, padx=8)
            if M.INAAnalysis.spectra[self.index].sample is not None:
                role_string = M.INAAnalysis.get_sampletype(M.INAAnalysis.spectra[self.index].sample)
                self.roleCB.configure(text=role_string)
            else:
                self.roleCB.configure(text='-')

            self.pathL = tk.Label(info_frame, text='', width=80, anchor=tk.W)
            self.pathL.grid(row=8, column=1, sticky=tk.W, padx=8)
            self.spfileL = tk.Label(info_frame, text='', anchor=tk.W)
            self.spfileL.grid(row=9, column=1, sticky=tk.W, padx=8)
            self.pllfileL = tk.Label(info_frame, text='', anchor=tk.W)
            self.pllfileL.grid(row=10, column=1, sticky=tk.W, padx=8)
            self.psfileL = tk.Label(info_frame, text='', anchor=tk.W)
            self.psfileL.grid(row=11, column=1, sticky=tk.W, padx=8)

            info_frame.pack(anchor=tk.NW)

            localhintlabel.pack(anchor=tk.NW)

            mframe.pack(anchor=tk.NW, padx=5, pady=5)
            self._update_spectrum_info(M)
            self.SpectrumProfileSubwindow.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.SpectrumProfileSubwindow))

            self.sampleCB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': self.select_sampleid(M))

    def _autoselect_peaks(self, M):
        try:
            self.PeakInformationSubwindow.destroy()
            self.PeakInformationSubwindow = None
        except Exception:
            pass
        #not that much options really

        sample = M.INAAnalysis.get_sample(M.INAAnalysis.spectra[self.index].sample)

        if sample is not None:
            elements = sample.composition.certificate.keys()
        else:
            elements = None
            
        for nn, suspt in enumerate(M.INAAnalysis.spectra[self.index].suspected_peaks):
            assignment = self.manage_assignment(M, nn, suspt, elements)
            M.INAAnalysis.spectra[self.index].assigned_peaks[nn] = assignment
            if assignment > -1:
                self.tree.set(nn, column='emitter', value=M.INAAnalysis.spectra[self.index].suspected_peaks[nn][assignment].emission)
            elif assignment == -2:
                self.tree.set(nn, column='emitter', value='X')
            else:
                self.tree.set(nn, column='emitter', value='')

    def _peak_intensity_alert(self, M):
        PIA = tk.Toplevel(self.SpectrumProfileSubwindow)
        text = M.INAAnalysis.spectra[self.index].peak_intensity_check(M.settings.get('count rate threshold'))
        PIA.title(f'Intense peak alert (threshold {M.settings.get("count rate threshold")} s⁻¹)')
        PIA.resizable(False, False)
        gui_things.ScrollableText(PIA, width=45, height=10, data=text).pack(anchor=tk.NW)

    def manage_assignment(self, M, nn, suspt, elements=None):
        assignment = -1
        if elements is not None:
            check_composition = True
        else:
            check_composition = False

        if len(suspt) == 1:
            if check_composition:
                if M.INAAnalysis.spectra[self.index].suspected_peaks[nn][0].target in elements:
                    return self._check_overwrite(M, nn, 0)
                return self._check_overwrite(M, nn, -1)
            return self._check_overwrite(M, nn, 0)
        elif len(suspt) > 1:
            return self._check_overwrite(M, nn, M.INAAnalysis.spectra[self.index].assigned_peaks[nn])

        return self._check_overwrite(M, nn, assignment)
    
    def _check_overwrite(self, M, nn, assignment):
        #end check for overwrite
        previous_value = M.INAAnalysis.spectra[self.index].assigned_peaks[nn]

        if previous_value > -1 and previous_value != assignment:
            
            if M.settings.get('overwrite manual emission selection'):
                return assignment
            else:
                return previous_value
            
        elif previous_value == -2 and not M.settings.get('overwrite manual emission selection'):
            return previous_value

        return assignment

    def select_sampleid(self, M):
        M.INAAnalysis.spectra[self.index].sample = self.sampleCB.get()
        
        sample_id = M.INAAnalysis.spectra[self.index].get_sample()
        self.labelid.configure(text=sample_id)
        role_string = M.INAAnalysis.get_sampletype(sample_id)
        self.labelrole.configure(text=role_string)
        self.roleCB.configure(text=role_string)

    def _update_spectrum_info(self, M):
        self.filenameL.configure(text=M.INAAnalysis.spectra[self.index].filename())
        if M.INAAnalysis.irradiation is not None:
            td = M.INAAnalysis.spectra[self.index].datetime - M.INAAnalysis.irradiation.datetime
            decay_time = f' ({td.days + td.seconds/86400:.3f} days from irradiation end)'
        else:
            decay_time = ''
        self.startacquisitionL.configure(text=M.INAAnalysis.spectra[self.index].readable_datetime() + decay_time)
        self.realL.configure(text=f'{M.INAAnalysis.spectra[self.index].real_time:.2f} s ({M.INAAnalysis.spectra[self.index].real_time/3600:.2f} h)')
        self.liveL.configure(text=f'{M.INAAnalysis.spectra[self.index].live_time:.2f} s ({M.INAAnalysis.spectra[self.index].live_time/3600:.2f} h)')
        self.deadL.configure(text=f'{(1-M.INAAnalysis.spectra[self.index].live_time/M.INAAnalysis.spectra[self.index].real_time)*100:.2f} %')
        if M.INAAnalysis.spectra[self.index].sample is not None:
            self.sampleCB.set(M.INAAnalysis.spectra[self.index].sample)
        self.pathL.configure(text=M.INAAnalysis.spectra[self.index].spectrumpath)
        self.spfileL.configure(text='')
        self.pllfileL.configure(text=f'{M.INAAnalysis.spectra[self.index].peak_summary()[0]}')
        self.psfileL.configure(text=M.INAAnalysis.spectra[self.index].peak_summary(8)[1])

    def on_closing(self, window):
        if window == self.SpectrumProfileSubwindow:
            self.SpectrumProfileSubwindow.destroy()
            self.SpectrumProfileSubwindow = None
        elif window == self.SpectrumPlotSubwindow:
            self.SpectrumPlotSubwindow.destroy()
            self.SpectrumPlotSubwindow = None
        else:
            self.PeakInformationSubwindow.destroy()
            self.PeakInformationSubwindow = None

    def select_item_from_tree(self, parent, M):
        curItem = self.tree.focus()
        item_index = self.tree.index(curItem)
        values = self.tree.item(curItem, 'values')
        if values != '':
            self.re_center_plot(int(M.INAAnalysis.spectra[self.index].peak_list[item_index][0]), M)
            self.show_peak_info(parent, M, item_index)


class IrradiationSampleManagementWindow:
    def __init__(self, parent, M, irrlabel):
        parent.title(f'Irradiation samples')
        parent.resizable(False,False)
        self.secondary_window = None
        self.distance_overview_window = None

        mainframe = tk.Frame(parent)

        self.hintlabel = tk.Label(mainframe, text='', anchor=tk.W)

        irradiationdataframe = tk.LabelFrame(mainframe, labelwidget=tk.Label(mainframe, text='irradiation data'), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(irradiationdataframe, text='irradiation code', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        irr_codes = self.update_irradiation_codes()
        self.irradiationcode_CB = gui_things.HelpedCombobox(irradiationdataframe, data=irr_codes, hint='insert irradiation code', hint_destination=self.hintlabel, width=20, allow_new_input=True)
        
        self.irradiationcode_CB.grid(row=0, column=1, columnspan=2, padx=5, sticky=tk.EW)
        tk.Frame(irradiationdataframe).grid(row=1, column=0, pady=5)
        tk.Label(irradiationdataframe, text='end of irradiation date', width=20, anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
        self.irradiationend = gui_things.DateLabel(irradiationdataframe, hint_destination=self.hintlabel)
        self.irradiationend.grid(row=2, column=1, columnspan=2)

        tk.Label(irradiationdataframe, text='x', anchor=tk.W).grid(row=3, column=1)
        tk.Label(irradiationdataframe, text='u(x)', anchor=tk.W).grid(row=3, column=2)
        tk.Label(irradiationdataframe, text='irradiation time / s', anchor=tk.W).grid(row=4, column=0, sticky=tk.W)
        self.irradiation_time_F = gui_things.Spinbox(irradiationdataframe, width=12, from_=0, to=500000, increment=1)
        self.irradiation_time_F.grid(row=4, column=1)
        self.uirradiation_time_F = gui_things.Spinbox(irradiationdataframe, width=8, from_=0, to=2000, increment=1)
        self.uirradiation_time_F.grid(row=4, column=2)

        tk.Frame(irradiationdataframe).grid(row=5, column=0, pady=5)
        tk.Label(irradiationdataframe, text='irradiation channel name', anchor=tk.W).grid(row=6, column=0, sticky=tk.W)

        self.ch_data = naaobject._call_database('channels', 'facilities', 'chs')
        self.ch_list = sorted(set(self.ch_data['channel_name']))

        self.irradiationchannelname_CB = gui_things.HelpedCombobox(irradiationdataframe, data=self.ch_list, hint='insert facility name', hint_destination=self.hintlabel, width=20, allow_new_input=True)
        
        self.irradiationchannelname_CB.grid(row=6, column=1, columnspan=2, padx=5, sticky=tk.EW)

        logo_lookforfluxdata = tk.PhotoImage(data=gui_things.PL_letter_phi)
        B_lookforfluxdata = gui_things.Button(irradiationdataframe, image=logo_lookforfluxdata, hint='Look for flux data', hint_destination=self.hintlabel)
        B_lookforfluxdata.grid(row=6, column=3)
        B_lookforfluxdata.image = logo_lookforfluxdata

        tk.Label(irradiationdataframe, text='x', anchor=tk.W).grid(row=7, column=1)
        tk.Label(irradiationdataframe, text='u(x)', anchor=tk.W).grid(row=7, column=2)
        tk.Label(irradiationdataframe, text='f / 1', anchor=tk.W).grid(row=8, column=0, sticky=tk.W)
        tk.Label(irradiationdataframe, text='α / 1', anchor=tk.W).grid(row=9, column=0, sticky=tk.W)
        tk.Label(irradiationdataframe, text='Φ_thermal / cm⁻² s⁻¹', anchor=tk.W).grid(row=10, column=0, sticky=tk.W)
        tk.Label(irradiationdataframe, text='Φ_epithermal / cm⁻² s⁻¹', anchor=tk.W).grid(row=11, column=0, sticky=tk.W)
        tk.Label(irradiationdataframe, text='Φ_fast / cm⁻² s⁻¹', anchor=tk.W).grid(row=12, column=0, sticky=tk.W)

        self.effe_F = gui_things.Spinbox(irradiationdataframe, width=12, from_=0.000, to=10000.000, increment=1)
        self.effe_F.grid(row=8, column=1)
        self.ueffe_F = gui_things.Spinbox(irradiationdataframe, width=8, from_=0.000, to=20.000, increment=1)
        self.ueffe_F.grid(row=8, column=2)
        self.alpha_F = gui_things.Spinbox(irradiationdataframe, width=12, from_=-1.0000, to=1.0000, increment=0.0001)
        self.alpha_F.delete(0, tk.END)
        self.alpha_F.insert(0, 0.0000)
        self.alpha_F.grid(row=9, column=1)
        self.ualpha_F = gui_things.Spinbox(irradiationdataframe, width=8, from_=0.0000, to=1.0000, increment=0.0001)
        self.ualpha_F.grid(row=9, column=2)
        self.thermal_F = ttk.Entry(irradiationdataframe, width=13)
        self.thermal_F.grid(row=10, column=1)
        self.uthermal_F = ttk.Entry(irradiationdataframe, width=10)
        self.uthermal_F.grid(row=10, column=2)
        self.epithermal_F = ttk.Entry(irradiationdataframe, width=13)
        self.epithermal_F.grid(row=11, column=1)
        self.uepithermal_F = ttk.Entry(irradiationdataframe, width=10)
        self.uepithermal_F.grid(row=11, column=2)
        self.fast_F = ttk.Entry(irradiationdataframe, width=13)
        self.fast_F.grid(row=12, column=1)
        self.ufast_F = ttk.Entry(irradiationdataframe, width=10)
        self.ufast_F.grid(row=12, column=2)

        irradiationschemeframe = tk.LabelFrame(mainframe, labelwidget=tk.Label(mainframe, text='irradiation scheme'), relief='solid', bd=2, padx=4, pady=4)

        try:
            M.INAAnalysis.irradiation.irradiation_scheme.initialize(M.INAAnalysis.samples_id)
            self.irradiation_scheme = M.INAAnalysis.irradiation.irradiation_scheme
        except AttributeError:
            self.irradiation_scheme = naaobject.IrradiationScheme(M.INAAnalysis.samples_id)

        cvs = tk.Canvas(irradiationschemeframe, height=350, width=165)
        cvs.grid(row=0, column=0, sticky=tk.NW)
        self.irradiation_scheme.draw(cvs)

        schemedataframe = tk.Frame(irradiationschemeframe)
        self.irradiation_scheme_item_LB = gui_things.ScrollableListbox(schemedataframe, width=35, height=7, data=[item.code for item in self.irradiation_scheme.scheme])
        self.irradiation_scheme_item_LB.grid(row=0, column=0, columnspan=3, padx=5, sticky=tk.EW)

        tk.Frame(schemedataframe).grid(row=1, column=0, pady=5)

        buttonframe = tk.Frame(schemedataframe)

        logo_add_modify_item = tk.PhotoImage(data=gui_things.PL_ggear)
        B_add_modify_item = gui_things.Button(buttonframe, image=logo_add_modify_item, hint='modify selected item', hint_destination=self.hintlabel, command=lambda : self.add_modify_item(cvs))
        B_add_modify_item.pack(side=tk.LEFT, anchor=tk.W)
        B_add_modify_item.image = logo_add_modify_item

        logo_delete_item = tk.PhotoImage(data=gui_things.PL_none)
        B_delete_item = gui_things.Button(buttonframe, image=logo_delete_item, hint='delete selected item', hint_destination=self.hintlabel, command=lambda : self.delete_item(parent, cvs))
        B_delete_item.pack(side=tk.LEFT, anchor=tk.W)
        B_delete_item.image = logo_delete_item

        logo_item_up = tk.PhotoImage(data=gui_things.PL_aup)
        B_item_up = gui_things.Button(buttonframe, image=logo_item_up, hint='move selected item up', hint_destination=self.hintlabel, command=lambda : self.move_item(cvs, -1))
        B_item_up.pack(side=tk.LEFT, anchor=tk.W)
        B_item_up.image = logo_item_up

        logo_item_down = tk.PhotoImage(data=gui_things.PL_adown)
        B_item_down = gui_things.Button(buttonframe, image=logo_item_down, hint='move selected item down', hint_destination=self.hintlabel, command=lambda : self.move_item(cvs, 1))
        B_item_down.pack(side=tk.LEFT, anchor=tk.W)
        B_item_down.image = logo_item_down

        logo_distances_overview = tk.PhotoImage(data=gui_things.PL_meter)
        B_distances_overview = gui_things.Button(buttonframe, image=logo_distances_overview, hint='overview distances relative to selected item', hint_destination=self.hintlabel, command=lambda : self.display_distance_overview(parent))
        B_distances_overview.pack(side=tk.LEFT, anchor=tk.W)
        B_distances_overview.image = logo_distances_overview

        buttonframe.grid(row=2, column=0, columnspan=3, sticky=tk.W)

        tk.Frame(schemedataframe).grid(row=3, column=0, pady=5)

        tk.Label(schemedataframe, text='x', anchor=tk.W).grid(row=4, column=1)
        tk.Label(schemedataframe, text='u(x)', anchor=tk.W).grid(row=4, column=2)
        tk.Label(schemedataframe, text='sample / mm', anchor=tk.W).grid(row=5, column=0, sticky=tk.W)
        tk.Label(schemedataframe, text='height / mm', anchor=tk.W).grid(row=6, column=0, sticky=tk.W)
        tk.Label(schemedataframe, text='offset / mm', anchor=tk.W).grid(row=7, column=0, sticky=tk.W)
        tk.Label(schemedataframe, text='role', anchor=tk.W).grid(row=8, column=0, sticky=tk.W)
        tk.Label(schemedataframe, text='type', anchor=tk.W).grid(row=9, column=0, sticky=tk.W)

        self.sampleheight = gui_things.Label(schemedataframe, text='-', width=8)
        self.sampleheight.grid(row=5, column=1, sticky=tk.W, padx=2)
        self.sampleuheight = gui_things.Label(schemedataframe, text='-', width=8)
        self.sampleuheight.grid(row=5, column=2, sticky=tk.W, padx=2)
        self.itemheight = gui_things.Spinbox(schemedataframe, from_=0.0, to=200.0, increment=0.1, width=8)
        self.itemheight.grid(row=6, column=1, sticky=tk.W, padx=2)
        self.itemuheight = gui_things.Spinbox(schemedataframe, from_=0.0, to=20.0, increment=0.1, width=8)
        self.itemuheight.grid(row=6, column=2, sticky=tk.W, padx=2)
        self.itemoffset = gui_things.Spinbox(schemedataframe, from_=0.0, to=200.0, increment=0.1, width=8)
        self.itemoffset.grid(row=7, column=1, sticky=tk.W, padx=2)
        self.itemuoffset = gui_things.Spinbox(schemedataframe, from_=0.0, to=20.0, increment=0.1, width=8)
        self.itemuoffset.grid(row=7, column=2, sticky=tk.W, padx=2)
        self.rolelabel = tk.Label(schemedataframe, width=20, anchor=tk.W)
        self.rolelabel.grid(row=8, column=1, columnspan=2, sticky=tk.W, padx=5)
        self.roletype = tk.Label(schemedataframe, width=20, anchor=tk.W)
        self.roletype.grid(row=9, column=1, columnspan=2, sticky=tk.W, padx=5)

        buttonframe = tk.Frame(schemedataframe)

        logo_add_item = tk.PhotoImage(data=gui_things.PL_plussign)
        B_add_item = gui_things.Button(buttonframe, image=logo_add_item, hint='add item to irradiation scheme', hint_destination=self.hintlabel, command=lambda : self.add_item(M, cvs))
        B_add_item.pack(side=tk.LEFT, anchor=tk.W)
        B_add_item.image = logo_add_item

        self.measurementsamplecode_CB = gui_things.Combobox(buttonframe, width=25, state='readonly')
        self.measurementsamplecode_CB.pack(side=tk.LEFT, padx=5)
        self.measurementsamplecode_CB['values'] = self.irradiation_scheme.samples_id
        if len(self.measurementsamplecode_CB['values']) > 0:
            self.measurementsamplecode_CB.set(self.measurementsamplecode_CB['values'][0])

        buttonframe.grid(row=10, column=0, columnspan=3, sticky=tk.W)

        tk.Frame(schemedataframe).grid(row=8, column=0, pady=5)
        legend = tk.Frame(irradiationschemeframe)
        tk.Label(legend, text='standard', bg='#FFDB58', width=10, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(legend, text='sample', bg='#89C35C', width=10, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(legend, text='dummy', bg='gray', width=10, anchor=tk.W).pack(side=tk.LEFT)
        legend.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        schemedataframe.grid(row=0, column=1, sticky=tk.NW)

        irradiationschemeframe.grid(row=0, column=1, sticky=tk.NW, padx=5)
        irradiationdataframe.grid(row=0, column=0, sticky=tk.NW, padx=5)

        decisionframe = tk.Frame(mainframe)

        self.store_data_variable = tk.IntVar(mainframe)
        SDCB = gui_things.Checkbutton(decisionframe, hint='store data in facility database', hint_xoffset=0, hint_destination=self.hintlabel, variable=self.store_data_variable, text='store in database')
        SDCB.pack(side=tk.LEFT)
        self.store_data_variable.set(0)

        logo_save_irradiation = tk.PhotoImage(data=gui_things.PL_check)
        B_save_irradiation = gui_things.Button(decisionframe, image=logo_save_irradiation, hint='confirm irradiation and save data', hint_destination=self.hintlabel, command=lambda : self.save_irradiation_data(M, irrlabel))
        B_save_irradiation.pack(side=tk.LEFT, padx=5)
        B_save_irradiation.image = logo_save_irradiation

        decisionframe.grid(row=1, column=0, columnspan=2, pady=5)

        self.hintlabel.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        mainframe.pack(anchor=tk.NW, padx=5, pady=5)

        B_lookforfluxdata.configure(command=lambda : self.seekforfluxdata(parent))

        if M.INAAnalysis.irradiation is not None:
            self.irradiationcode_CB.Combobox.set(M.INAAnalysis.irradiation.code)
            self.irradiationend.set(M.INAAnalysis.irradiation.datetime)
            self.irradiation_time_F.delete(0, tk.END)
            self.irradiation_time_F.insert(0, f'{M.INAAnalysis.irradiation.irradiation_time:.1f}')
            self.uirradiation_time_F.delete(0, tk.END)
            self.uirradiation_time_F.insert(0, f'{M.INAAnalysis.irradiation.unc_irradiation_time:.1f}')
            self.irradiationchannelname_CB.Combobox.set(M.INAAnalysis.irradiation.channel_name)
            self.effe_F.delete(0, tk.END)
            self.effe_F.insert(0, f'{M.INAAnalysis.irradiation.f_value:.3f}')
            self.ueffe_F.delete(0, tk.END)
            self.ueffe_F.insert(0, f'{M.INAAnalysis.irradiation.unc_f_value:.3f}')
            self.alpha_F.delete(0, tk.END)
            self.alpha_F.insert(0, f'{M.INAAnalysis.irradiation.a_value:.5f}')
            self.ualpha_F.delete(0, tk.END)
            self.ualpha_F.insert(0, f'{M.INAAnalysis.irradiation.unc_a_value:.5f}')
            self.thermal_F.delete(0, tk.END)
            self.thermal_F.insert(0, f'{M.INAAnalysis.irradiation.thermal_flux:.3e}')
            self.uthermal_F.delete(0, tk.END)
            self.uthermal_F.insert(0, f'{M.INAAnalysis.irradiation.unc_thermal_flux:.3e}')
            self.epithermal_F.delete(0, tk.END)
            self.epithermal_F.insert(0, f'{M.INAAnalysis.irradiation.epithermal_flux:.3e}')
            self.uepithermal_F.delete(0, tk.END)
            self.uepithermal_F.insert(0, f'{M.INAAnalysis.irradiation.unc_epithermal_flux:.3e}')
            self.fast_F.delete(0, tk.END)
            self.fast_F.insert(0, f'{M.INAAnalysis.irradiation.fast_flux:.3e}')
            self.ufast_F.delete(0, tk.END)
            self.ufast_F.insert(0, f'{M.INAAnalysis.irradiation.unc_fast_flux:.3e}')

        self.irradiation_scheme_item_LB.listbox.bind("<<ListboxSelect>>", lambda e="<<ListboxSelect>>" : self.selection_item_scheme())
        self.irradiationcode_CB.Combobox.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.recall_irradiation_data(M, cvs))

    def recall_irradiation_data(self, M, cvs):
        try:
            provisional_irradiation = naaobject._call_database(self.irradiationcode_CB.get(), 'irradiations', 'irr')
        except Exception:
            provisional_irradiation = None

        if provisional_irradiation is not None:
            self.irradiationcode_CB.Combobox.set(provisional_irradiation.code)
            self.irradiationend.set(provisional_irradiation.datetime)
            self.irradiation_time_F.delete(0, tk.END)
            self.irradiation_time_F.insert(0, f'{provisional_irradiation.irradiation_time:.1f}')
            self.uirradiation_time_F.delete(0, tk.END)
            self.uirradiation_time_F.insert(0, f'{provisional_irradiation.unc_irradiation_time:.1f}')
            self.irradiationchannelname_CB.Combobox.set(provisional_irradiation.channel_name)
            self.effe_F.delete(0, tk.END)
            self.effe_F.insert(0, f'{provisional_irradiation.f_value:.3f}')
            self.ueffe_F.delete(0, tk.END)
            self.ueffe_F.insert(0, f'{provisional_irradiation.unc_f_value:.3f}')
            self.alpha_F.delete(0, tk.END)
            self.alpha_F.insert(0, f'{provisional_irradiation.a_value:.5f}')
            self.ualpha_F.delete(0, tk.END)
            self.ualpha_F.insert(0, f'{provisional_irradiation.unc_a_value:.5f}')
            self.thermal_F.delete(0, tk.END)
            self.thermal_F.insert(0, f'{provisional_irradiation.thermal_flux:.3e}')
            self.uthermal_F.delete(0, tk.END)
            self.uthermal_F.insert(0, f'{provisional_irradiation.unc_thermal_flux:.3e}')
            self.epithermal_F.delete(0, tk.END)
            self.epithermal_F.insert(0, f'{provisional_irradiation.epithermal_flux:.3e}')
            self.uepithermal_F.delete(0, tk.END)
            self.uepithermal_F.insert(0, f'{provisional_irradiation.unc_epithermal_flux:.3e}')
            self.fast_F.delete(0, tk.END)
            self.fast_F.insert(0, f'{provisional_irradiation.fast_flux:.3e}')
            self.ufast_F.delete(0, tk.END)
            self.ufast_F.insert(0, f'{provisional_irradiation.unc_fast_flux:.3e}')

            try:
                provisional_irradiation.irradiation_scheme.initialize(M.INAAnalysis.samples_id)
                self.irradiation_scheme = provisional_irradiation.irradiation_scheme
            except AttributeError:
                self.irradiation_scheme = naaobject.IrradiationScheme(M.INAAnalysis.samples_id)

            self.irradiation_scheme.draw(cvs)
            self.irradiation_scheme_item_LB._update([item.code for item in self.irradiation_scheme.scheme])
            self.measurementsamplecode_CB['values'] = self.irradiation_scheme.samples_id
            if len(self.measurementsamplecode_CB['values']) > 0:
                self.measurementsamplecode_CB.set(self.measurementsamplecode_CB['values'][0])
        else:
            self.hintlabel.configure(text='data impossible to recall')

    def selection_item_scheme(self):
        try:
            idx = self.irradiation_scheme_item_LB.curselection()[0]
        except IndexError:
            idx = -1
        if idx > -1:
            item = self.irradiation_scheme.scheme[idx]

            if item.role != 'dummy':
                hms = f'{item.s_height:.1f}'
                uhms = f'{item.s_uheight:.1f}'
            else:
                hms, uhms = '-', '-'

            self.sampleheight.configure(text=hms)
            self.sampleuheight.configure(text=uhms)
            self.itemheight.delete(0, tk.END)
            self.itemheight.insert(0, item.height)
            self.itemuheight.delete(0, tk.END)
            self.itemuheight.insert(0, item.uheight)
            self.itemoffset.delete(0, tk.END)
            self.itemoffset.insert(0, item.loffset)
            self.itemuoffset.delete(0, tk.END)
            self.itemuoffset.insert(0, item.uloffset)
            self.rolelabel.configure(text=item.role)
            self.roletype.configure(text=item.type)

    def move_item(self, cvs, direction=1):
        try:
            idx = self.irradiation_scheme_item_LB.curselection()[0]
        except IndexError:
            idx = -1
        if idx > -1:
            tomove = self.irradiation_scheme.scheme.pop(idx)

            new_idx = idx + direction
            if new_idx < 0:
                new_idx = 0
            elif new_idx >= len(self.irradiation_scheme.scheme):
                new_idx = len(self.irradiation_scheme.scheme)

            self.irradiation_scheme.scheme.insert(new_idx, tomove)

            self.irradiation_scheme.draw(cvs)
            self.irradiation_scheme_item_LB._update([item.code for item in self.irradiation_scheme.scheme])

    def display_distance_overview(self, parent):
        try:
            idx = self.irradiation_scheme_item_LB.curselection()[0]
        except IndexError:
            idx = -1
        if idx > -1:
            reference = self.irradiation_scheme.scheme[idx]
            if reference.role in ('standard', 'sample'):

                if self.distance_overview_window is not None:
                    try:
                        self.distance_overview_window.destroy()
                    except:
                        pass

                self.distance_overview_window = tk.Toplevel(parent)
                title = f'Distances to {reference.code}'
                self.distance_overview_window.title(title)
                self.distance_overview_window.resizable(False, False)

                data_frame = tk.Frame(self.distance_overview_window)
                widhts = (18,18,10)
                bias = 2
                tk.Label(data_frame, text='code', width=widhts[0], anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
                tk.Label(data_frame, text='role', width=widhts[1], anchor=tk.W).grid(row=0, column=1, sticky=tk.W)
                tk.Label(data_frame, text='d / mm', width=widhts[2], anchor=tk.W).grid(row=0, column=2, sticky=tk.W)
                ttk.Separator(data_frame, orient="horizontal").grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)

                for nn, irradiation_item in enumerate(self.irradiation_scheme.scheme):
                    if irradiation_item.code == reference.code:
                        ddd = f'{0.0:.0f}'
                    elif irradiation_item.role in ('standard', 'sample'):
                        ddd = f'{self.irradiation_scheme.standard_sample_distance(reference.code, irradiation_item.code)[0]:.1f}'
                    else:
                        ddd = ''
                    
                    tk.Label(data_frame, text=irradiation_item.code, width=widhts[0], anchor=tk.W).grid(row=nn+bias, column=0, sticky=tk.W)
                    tk.Label(data_frame, text=irradiation_item.role, width=widhts[1], anchor=tk.W).grid(row=nn+bias, column=1, sticky=tk.W)
                    tk.Label(data_frame, text=ddd, width=widhts[2], anchor=tk.W).grid(row=nn+bias, column=2, sticky=tk.W)

                data_frame.pack(anchor=tk.NW, padx=5, pady=5)
            else:
                self.hintlabel.configure(text='a standard or sample needs to be selected')

    def delete_item(self, parent, cvs):
        try:
            idx = self.irradiation_scheme_item_LB.curselection()[0]
        except IndexError:
            idx = -1
        if idx > -1:
            todelete = self.irradiation_scheme.scheme[idx]
            if messagebox.askyesno(title='Delete irradiation scheme item', message=f'\nAre you sure to delete data\nrelated to item {todelete.code} (index {idx})?\n', parent=parent):
                self.irradiation_scheme.scheme.pop(idx)
                self.irradiation_scheme.draw(cvs)
                self.irradiation_scheme_item_LB._update([item.code for item in self.irradiation_scheme.scheme])

                self.itemheight.delete(0, tk.END)
                self.itemheight.insert(0, 0.0)
                self.itemuheight.delete(0, tk.END)
                self.itemuheight.insert(0, 0.0)
                self.itemoffset.delete(0, tk.END)
                self.itemoffset.insert(0, 0.0)
                self.itemuoffset.delete(0, tk.END)
                self.itemuoffset.insert(0, 0.0)
                self.rolelabel.configure(text='')
                self.roletype.configure(text='')

    def selection_of_code(self, M):
        if self.sample_variable.get() == 1:
            sample = M.INAAnalysis.get_sample(self.measurementsamplecode_CB.get())
            self.rolelabel.configure(text=sample.sampletype)
            self.roletype.configure(text=sample.composition.compositiontype)

    def add_item(self, M, cvs):
        scheme_item = M.INAAnalysis.get_sample(self.measurementsamplecode_CB.get())
        message = self.irradiation_scheme.add_position(naaobject.BaseItemScheme(scheme_item))
        self.hintlabel.configure(text=message)
        self.irradiation_scheme.draw(cvs)
        self.irradiation_scheme_item_LB._update([item.code for item in self.irradiation_scheme.scheme])

    def add_modify_item(self, cvs):
        advance = True
        try:
            height = float(self.itemheight.get())
        except ValueError:
            height = 0.0
        try:
            uheight = float(self.itemuheight.get())
        except ValueError:
            uheight = 0.0
                
        try:
            loffset = float(self.itemoffset.get())
        except ValueError:
            loffset = 0.0
        try:
            uloffset = float(self.itemuoffset.get())
        except ValueError:
            uloffset = 0.0

        if height <= 0.0:
            advance = False

        try:
            idx = self.irradiation_scheme_item_LB.curselection()[0]
        except IndexError:
            idx = -1
            advance = False

        if advance:
            self.irradiation_scheme.scheme[idx].loffset = loffset
            self.irradiation_scheme.scheme[idx].uloffset = uloffset

            if height < self.irradiation_scheme.scheme[idx].s_height + self.irradiation_scheme.scheme[idx].loffset:
                height = self.irradiation_scheme.scheme[idx].s_height + self.irradiation_scheme.scheme[idx].loffset

                self.itemheight.delete(0, tk.END)
                self.itemheight.insert(0, height)

            self.irradiation_scheme.scheme[idx].height = height
            self.irradiation_scheme.scheme[idx].uheight = uheight

            self.irradiation_scheme.draw(cvs)
        else:
            self.hintlabel.configure(text='an error occurred, non physical item height')

    def _facility_as_text_display(self, data, spaces=[15,8,12,12,10,10,10,10]):

        def text_cut(text,limit):
            if len(text) > limit - 1:
                return (text[:limit-3]+'..').ljust(limit," ")
            else:
                return text.ljust(limit," ")

        return [f'{text_cut(idx,spaces[0])}{format(pos,".1f").ljust(spaces[1])}{mtime.strftime("%d/%m/%Y").rjust(spaces[2]," ")}{dtime.strftime("%d/%m/%Y").rjust(spaces[3]," ")}{format(ff,".2f").rjust(spaces[4]," ")}{format(aa,".5f").rjust(spaces[5]," ")}{format(thermal,".2e").rjust(spaces[6]," ")}{format(fast,".2e").rjust(spaces[7]," ")}' for idx, pos, mtime, dtime, ff, aa, thermal, fast in zip(data['channel_name'], data['pos'], data['m_datetime'], data['datetime'], data['f_value'], data['a_value'], data['thermal_flux'], data['fast_flux'])]

    def seekforfluxdata(self, parent):
        fullchannelname = self.irradiationchannelname_CB.get()
        if fullchannelname.replace(' ','') != '':

            if self.secondary_window is not None:
                try:
                    self.secondary_window.destroy()
                except:
                    pass

            self.secondary_window = tk.Toplevel(parent)
            title = f'Display facility information ({fullchannelname})'
            self.secondary_window.title(title)
            self.secondary_window.resizable(False, False)

            partial_data = self.ch_data[self.ch_data['channel_name'] == fullchannelname]

            data_frame = tk.Frame(self.secondary_window)

            spaces = [15,8,12,12,10,10,10,10]
            header=['channel','position','meas date','eval date','f / 1', 'α / 1','thermal', 'fast']
            tk.Label(data_frame, text=f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}{header[3].rjust(spaces[3]," ")}{header[4].rjust(spaces[4]," ")}{header[5].rjust(spaces[5]," ")}{header[6].rjust(spaces[6]," ")}{header[7].rjust(spaces[7]," ")}', anchor=tk.W, font=('Courier', 10)).pack(anchor=tk.W)
            height = 25

            self.selected_facility_LB = gui_things.ScrollableListbox(data_frame, width=90, height=height, data=self._facility_as_text_display(partial_data), font=('Courier', 10))
            self.selected_facility_LB.pack(anchor=tk.NW)

            data_frame.pack(anchor=tk.NW, padx=5, pady=5)

            self.selected_facility_LB.listbox.bind('<Double-Button-1>', lambda e='<Double-Button-1>' : self.update_irradiation_facility(partial_data))

    def update_irradiation_facility(self, partial_data):
        facilityindex = self.selected_facility_LB.curselection()
        try:
            facilityindex = facilityindex[0]
        except IndexError:
            facilityindex = None

        if facilityindex is not None:
            series_data = partial_data.iloc[facilityindex]

            self.effe_F.delete(0, tk.END)
            self.effe_F.insert(0, f'{series_data["f_value"]:.3f}')
            self.ueffe_F.delete(0, tk.END)
            self.ueffe_F.insert(0, f'{series_data["unc_f_value"]:.3f}')
            self.alpha_F.delete(0, tk.END)
            self.alpha_F.insert(0, f'{series_data["a_value"]:.5f}')
            self.ualpha_F.delete(0, tk.END)
            self.ualpha_F.insert(0, f'{series_data["unc_a_value"]:.5f}')
            self.thermal_F.delete(0, tk.END)
            self.thermal_F.insert(0, f'{series_data["thermal_flux"]:.3e}')
            self.uthermal_F.delete(0, tk.END)
            self.uthermal_F.insert(0, f'{series_data["unc_thermal_flux"]:.3e}')
            self.epithermal_F.delete(0, tk.END)
            self.epithermal_F.insert(0, f'{series_data["epithermal_flux"]:.3e}')
            self.uepithermal_F.delete(0, tk.END)
            self.uepithermal_F.insert(0, f'{series_data["unc_epithermal_flux"]:.3e}')
            self.fast_F.delete(0, tk.END)
            self.fast_F.insert(0, f'{series_data["fast_flux"]:.3e}')
            self.ufast_F.delete(0, tk.END)
            self.ufast_F.insert(0, f'{series_data["unc_fast_flux"]:.3e}')

    def update_irradiation_codes(self):
        irradiations_list = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'irradiations')) if filename.lower().endswith('.irr')]
        return irradiations_list

    def save_irradiation_data(self, M, irrlabel):
        #check and save irradiation data
        advance = True
        filename = self.irradiationcode_CB.get()
        if filename.replace(' ','') == '':
            advance = False
            message = ''

        tirr, advance = self.check_value(self.irradiation_time_F, advance, check_positive=True, sign='<=')

        utirr, advance = self.check_value(self.uirradiation_time_F, advance, check_positive=True, sign='<')
        
        channelname = self.irradiationchannelname_CB.get()
        if channelname.replace(' ','') == '':
            advance = False

        effe, advance = self.check_value(self.effe_F, advance, check_positive=True, sign='<=')
        
        ueffe, advance = self.check_value(self.ueffe_F, advance, check_positive=True, sign='<')

        alpha, advance = self.check_value(self.alpha_F, advance, check_positive=False)

        ualpha, advance = self.check_value(self.ualpha_F, advance, check_positive=True, sign='<')

        thermal, advance = self.check_value(self.thermal_F, advance, check_positive=True, sign='<=')

        uthermal, advance = self.check_value(self.uthermal_F, advance, check_positive=True, sign='<')

        epithermal, _ = self.check_value(self.epithermal_F, advance, default=thermal/(effe+1E-24), check_positive=True, sign='<=')

        uepithermal, _ = self.check_value(self.uepithermal_F, advance, check_positive=True, sign='<')

        fast, _ = self.check_value(self.fast_F, advance, check_positive=True, sign='<=')

        ufast, _ = self.check_value(self.ufast_F, advance, check_positive=True, sign='<')

        if advance:
            IS = naaobject.Irradiation(filename, self.irradiationend.get(), tirr,utirr, channelname, effe, ueffe, alpha, ualpha, thermal, uthermal, epithermal, uepithermal, fast, ufast, self.irradiation_scheme)
            IS._save()
            M.INAAnalysis.irradiation = IS
            irrlabel.configure(state='normal')
            irrlabel.delete(0, tk.END)
            irrlabel.insert(0, filename)
            irrlabel.configure(state='readonly')
            self.update_irradiation_codes()
            positive_outcome = 'irradiation data confirmed'
            if self.store_data_variable.get():
                self.ch_data = self.ch_data.append(IS._to_dict(), ignore_index=True)
                naaobject._save_facility_database(self.ch_data)
                self.ch_list = sorted(set(self.ch_data['channel_name']))
                self.irradiationchannelname_CB.Combobox['values'] = self.ch_list
                positive_outcome = 'irradiation data confirmed and stored in database'
            self.hintlabel.configure(text=positive_outcome)
        else:
            self.hintlabel.configure(text='invalid data')

    def check_value(self, container, outcome, check_positive=False, sign='<=', default=0.0):
        try:
            value = float(container.get())
        except ValueError:
            value = default
            outcome = False
        if check_positive:
            if sign == '<=':
                if value <= 0.0:
                    outcome = False
            else:
                if value < 0.0:
                    outcome = False
        return value, outcome


class BlankManagementWindow:
    def __init__(self, parent, M, label):
        parent.title(f'Blank')
        parent.resizable(False,False)

        mframe = tk.Frame(parent)
        self.hintlabel = tk.Label(mframe, text='', anchor=tk.W)
        left_frame = tk.Frame(mframe)
        header = tk.LabelFrame(left_frame, labelwidget=tk.Label(mframe, text='material selection'), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(header, text='material', width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.material_selector = gui_things.HelpedCombobox(header, width=25, data=(), hint='select material', hint_xoffset=0, hint_destination=self.hintlabel, allow_new_input=False, default_invalid='')
        self.material_selector._update([os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'samples')) if filename.lower().endswith('.csv')])
        self.material_selector.pack(side=tk.LEFT, padx=5)
        header.pack(anchor=tk.NW, fill=tk.X, expand=True)

        inserter = tk.LabelFrame(left_frame, labelwidget=tk.Label(mframe, text='mass information'), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(inserter, text='x').grid(row=0, column=1)
        tk.Label(inserter, text='u(x)').grid(row=0, column=2)
        tk.Label(inserter, text='mass / g', width=10, anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
        self.mass_F = gui_things.Spinbox(inserter, width=10, from_=0.000, to=10.000, increment=0.001)
        self.mass_F.grid(row=1, column=1, padx=5)
        self.mass_F.delete(0, tk.END)
        try:
            self.mass_F.insert(0, M.INAAnalysis.blank_info.mass)
        except AttributeError:
            self.mass_F.insert(0, 0.000)
        self.umass_F = gui_things.Spinbox(inserter, width=10, from_=0.000, to=1.0, increment=0.001)
        self.umass_F.grid(row=1, column=2, padx=5)
        self.umass_F.delete(0, tk.END)
        try:
            self.umass_F.insert(0, M.INAAnalysis.blank_info.umass)
        except AttributeError:
            self.umass_F.insert(0, 0.000)
        
        inserter.pack(anchor=tk.NW, fill=tk.X, expand=True)

        displayer = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='material information'), relief='solid', bd=2, padx=4, pady=4)
        self.display_materialinfo = gui_things.ScrollableText(displayer, width=40, height=15)
        self.display_materialinfo.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        displayer.grid(row=0, column=1, rowspan=12, sticky=tk.NSEW, padx=5)

        buttons_line = tk.Frame(left_frame)

        logo_savedata = tk.PhotoImage(data=gui_things.PL_check)
        B_savesampledata = gui_things.Button(buttons_line, image=logo_savedata, hint='save composition data', hint_destination=self.hintlabel, command=lambda : self.save_blank_material(M, label))
        B_savesampledata.pack(side=tk.LEFT)
        B_savesampledata.image = logo_savedata

        logo_deletedata = tk.PhotoImage(data=gui_things.PL_none)
        B_deletesampledata = gui_things.Button(buttons_line, image=logo_deletedata, hint='ignore composition data', hint_destination=self.hintlabel, command=lambda : self.ignore_blank_material(M, label))
        B_deletesampledata.pack(side=tk.LEFT)
        B_deletesampledata.image = logo_deletedata

        buttons_line.pack(anchor=tk.N, pady=10)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)

        self.hintlabel.grid(row=12, column=0, columnspan=2, sticky=tk.EW)
        mframe.pack(anchor=tk.NW, padx=5, pady=5)

        self.material_selector.Combobox.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.disclose_material())

        try:
            self.material_selector.Combobox.set(M.INAAnalysis.blank_info.data[0][4].name)
            self.disclose_material()
        except (AttributeError, IndexError):
            pass

    def disclose_material(self):
        filename = self.material_selector.get()
        try:
            provisional_sample = naaobject.Material(f'{filename}.csv')
            text = provisional_sample._as_text_display(preamble=f'Name: {provisional_sample.name}\n\nDescription: {provisional_sample.description}\n\nType: {provisional_sample.sample_type}\n\n')
            self.display_information(text)
        except Exception:
            pass

    def display_information(self, text):
        self.display_materialinfo._update(text)

    def save_blank_material(self, M, label):
        pmoist, pumoist = 0, 0

        advance = True
        psample = naaobject.Material(f'{self.material_selector.get()}.csv')
        try:
            pmass = float(self.mass_F.get())
        except ValueError:
            pmass = -1
            advance = False
        try:
            pumass = float(self.umass_F.get())
        except ValueError:
            pumass = -1
            advance = False
        
        if pmass <= 0.0 or pumass < 0.0:
            advance = False

        if advance:
            M.INAAnalysis.blank_info = naaobject.Composition('Blank', masses=(pmass,), unc_masses=(pumass,), moistures=(pmoist,), umoistures=(pumoist,), samples=(psample,))
            label.configure(text=M.INAAnalysis.blank_info.data[0][4].name)
        else:
            self.hintlabel.configure(text='invalid data')

    def ignore_blank_material(self, M, label):
        M.INAAnalysis.blank_info = None
        label.configure(text='')
        self.hintlabel.configure(text='blank ignored')
    

class EnvironmentalManagementWindow:
    def __init__(self, parent, M):
        parent.title(f'Buoyancy')
        parent.resizable(False,False)

        mainframe = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text='environmental data and balance features'), relief='solid', bd=2, padx=4, pady=4)

        self.hintlabel = tk.Label(mainframe, text='', anchor=tk.W)

        tk.Label(mainframe, text='x').grid(row=0, column=1)
        tk.Label(mainframe, text='u(x)').grid(row=0, column=2)
        tk.Label(mainframe, text='atmospheric pressure / mbar', width=25, anchor=tk.W).grid(row=1, column=0)
        tk.Label(mainframe, text='relative humidity / %', width=25, anchor=tk.W).grid(row=2, column=0)
        tk.Label(mainframe, text='temperature / °C', width=25, anchor=tk.W).grid(row=3, column=0)
        tk.Label(mainframe, text='density of weights / g cm⁻³', width=25, anchor=tk.W).grid(row=5, column=0)
        tk.Frame(mainframe).grid(row=4, column=0, pady=4)

        self.apressure_E = tk.Entry(mainframe, width=10)
        self.apressure_E.grid(row=1, column=1, padx=5)
        self.apressure_E.delete(0, tk.END)
        self.apressure_E.insert(0, M.INAAnalysis.air_buoyancy['pressure'])
        self.u_apressure_E = tk.Entry(mainframe, width=10)
        self.u_apressure_E.grid(row=1, column=2, padx=5)
        self.u_apressure_E.delete(0, tk.END)
        self.u_apressure_E.insert(0, M.INAAnalysis.air_buoyancy['u_pressure'])
        self.rel_humidity_E = tk.Entry(mainframe, width=10)
        self.rel_humidity_E.grid(row=2, column=1, padx=5)
        self.rel_humidity_E.delete(0, tk.END)
        self.rel_humidity_E.insert(0, M.INAAnalysis.air_buoyancy['relative humidity'])
        self.u_rel_humidity_E = tk.Entry(mainframe, width=10)
        self.u_rel_humidity_E.grid(row=2, column=2, padx=5)
        self.u_rel_humidity_E.delete(0, tk.END)
        self.u_rel_humidity_E.insert(0, M.INAAnalysis.air_buoyancy['u_relative humidity'])
        self.temperature_E = tk.Entry(mainframe, width=10)
        self.temperature_E.grid(row=3, column=1, padx=5)
        self.temperature_E.delete(0, tk.END)
        self.temperature_E.insert(0, M.INAAnalysis.air_buoyancy['temperature'])
        self.u_temperature_E = tk.Entry(mainframe, width=10)
        self.u_temperature_E.grid(row=3, column=2, padx=5)
        self.u_temperature_E.delete(0, tk.END)
        self.u_temperature_E.insert(0, M.INAAnalysis.air_buoyancy['u_temperature'])
        self.steel_E = tk.Entry(mainframe, width=10)
        self.steel_E.grid(row=5, column=1, padx=5)
        self.steel_E.delete(0, tk.END)
        self.steel_E.insert(0, M.INAAnalysis.air_buoyancy['steel'])
        self.u_steel_E = tk.Entry(mainframe, width=10)
        self.u_steel_E.grid(row=5, column=2, padx=5)
        self.u_steel_E.delete(0, tk.END)
        self.u_steel_E.insert(0, M.INAAnalysis.air_buoyancy['u_steel'])

        logo_updatevalues = tk.PhotoImage(data=gui_things.PL_check)
        B_settings = gui_things.Button(mainframe, image=logo_updatevalues, hint='confirm values', hint_destination=self.hintlabel, command=lambda : self.confirm_values(M))
        B_settings.grid(row=6, column=0, columnspan=3, pady=4)
        B_settings.image = logo_updatevalues

        self.hintlabel.grid(row=7, column=0, columnspan=3, sticky=tk.W)

        mainframe.pack(anchor=tk.NW, padx=5, pady=5)

    def confirm_values(self, M):
        invalid = 0
        try:
            p_value = float(self.apressure_E.get())
            if p_value > 0:
                M.INAAnalysis.air_buoyancy['pressure'] = p_value
            else:
                invalid += 1
        except:
            invalid += 1
        
        try:
            p_unc = float(self.u_apressure_E.get())
            if p_unc >= 0:
                M.INAAnalysis.air_buoyancy['u_pressure'] = p_unc
            else:
                invalid += 1
        except:
            invalid += 1

        try:
            RH_value = float(self.rel_humidity_E.get())
            if 0 <= RH_value <= 100:
                M.INAAnalysis.air_buoyancy['relative humidity'] = RH_value
            else:
                invalid += 1
        except:
            invalid += 1

        try:
            RH_unc = float(self.u_rel_humidity_E.get())
            if 0 <= RH_unc <= 100:
                M.INAAnalysis.air_buoyancy['u_relative humidity'] = RH_unc
            else:
                invalid += 1
        except:
            invalid += 1

        try:
            temp_value = float(self.temperature_E.get())
            if -273.15 <= temp_value:
                M.INAAnalysis.air_buoyancy['temperature'] = temp_value
            else:
                invalid += 1
        except:
            invalid += 1

        try:
            temp_unc = float(self.u_temperature_E.get())
            if 0 <= temp_unc:
                M.INAAnalysis.air_buoyancy['u_temperature'] = temp_unc
            else:
                invalid += 1
        except:
            invalid += 1

        try:
            steel_value = float(self.steel_E.get())
            if 0 < steel_value:
                M.INAAnalysis.air_buoyancy['steel'] = steel_value
            else:
                invalid += 1
        except:
            invalid += 1

        try:
            steel_unc = float(self.u_steel_E.get())
            if 0 <= steel_unc:
                M.INAAnalysis.air_buoyancy['u_steel'] = steel_unc
            else:
                invalid += 1
        except:
            invalid += 1

        if invalid > 0:
            message = f'{invalid} invalid data'
        else:
            message = 'all information successfully updated'
        self.hintlabel.configure(text=message)


class MeasurementSampleManagementWindow:
    def __init__(self, parent, M, mslabel, idlabel, rolelabel):
        parent.title(f'Measurement samples')
        parent.resizable(False,False)
        self.secondary_window = None        

        mainframe = tk.LabelFrame(parent, labelwidget=tk.Label(parent, text='registered codes'), relief='solid', bd=2, padx=4, pady=4)

        self.hintlabel = tk.Label(mainframe, text='', anchor=tk.W)

        tk.Frame(mainframe).grid(row=1, column=0, pady=5)

        self.sample_selector_CB = gui_things.Combobox(mainframe, width=12, state='readonly')
        self.sample_selector_CB['values'] = ['all', 'standard', 'sample']
        self.sample_selector_CB.grid(row=2, column=0)
        self.sample_selector_CB.set(self.sample_selector_CB['values'][0])
        F_font = self.sample_selector_CB.cget('font')

        self.sampleidlist = gui_things.ScrollableListbox(mainframe, height=15, width=35, data=[item.name for item in M.INAAnalysis.samples_id], font=F_font)
        self.sampleidlist.grid(row=3, column=0, sticky=tk.NW)

        buttonframe = tk.Frame(mainframe)

        logo_new_sample = tk.PhotoImage(data=gui_things.PL_plussign)
        B_new_sample = gui_things.Button(buttonframe, image=logo_new_sample, hint='add sample / standard', hint_destination=self.hintlabel, command=lambda : self.add_sample(parent, M, mslabel))
        B_new_sample.pack(side=tk.LEFT, anchor=tk.W)
        B_new_sample.image = logo_new_sample

        logo_modify_sample = tk.PhotoImage(data=gui_things.PL_ggear)
        B_modify_sample = gui_things.Button(buttonframe, image=logo_modify_sample, hint='modify selected sample / standard', hint_destination=self.hintlabel, command=lambda : self.modify_sample(parent, M, mslabel))
        B_modify_sample.pack(side=tk.LEFT, anchor=tk.W)
        B_modify_sample.image = logo_modify_sample

        logo_delete_sample = tk.PhotoImage(data=gui_things.PL_none)
        B_delete_sample = gui_things.Button(buttonframe, image=logo_delete_sample, hint='delete selected sample / standard', hint_destination=self.hintlabel, command=lambda : self.delete_sample(parent, M, mslabel, idlabel, rolelabel))
        B_delete_sample.pack(side=tk.LEFT, anchor=tk.W)
        B_delete_sample.image = logo_delete_sample

        ttk.Separator(buttonframe, orient="vertical").pack(side=tk.LEFT, padx=5, fill=tk.Y)

        logo_showsscontributions = tk.PhotoImage(data=gui_things.PL_element_green)
        B_showsscontributions = gui_things.Button(buttonframe, image=logo_showsscontributions, hint='sample thermal self-shielding', hint_destination=self.hintlabel, command=lambda : self.show_thermal_selfshielding(parent, M))
        B_showsscontributions.pack(side=tk.LEFT, anchor=tk.W)
        B_showsscontributions.image = logo_showsscontributions

        logo_showepisscontributions = tk.PhotoImage(data=gui_things.PL_element_yellow)
        B_showepisscontributions = gui_things.Button(buttonframe, image=logo_showepisscontributions, hint='sample epithermal self-shielding', hint_destination=self.hintlabel, command=lambda : self.show_epithermal_selfshielding(parent, M))
        B_showepisscontributions.pack(side=tk.LEFT, anchor=tk.W)
        B_showepisscontributions.image = logo_showepisscontributions

        buttonframe.grid(row=4, column=0, sticky=tk.W)

        self.hintlabel.grid(row=5, column=0, sticky=tk.EW)

        mainframe.pack(anchor=tk.NW, padx=5, pady=5)
        self.sample_selector_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.update_selector(M, mslabel))

    def update_selector(self, M, mslabel):
        if self.sample_selector_CB.get() == self.sample_selector_CB['values'][1]:
            self.sampleidlist._update(data=[item.name for item in M.INAAnalysis.samples_id if item.sampletype == self.sample_selector_CB.get()])
        elif self.sample_selector_CB.get() == self.sample_selector_CB['values'][2]:
            self.sampleidlist._update(data=[item.name for item in M.INAAnalysis.samples_id if item.sampletype == self.sample_selector_CB.get()])
        else:
            self.sampleidlist._update(data=[item.name for item in M.INAAnalysis.samples_id])
        mslabel.configure(text=f'{len(M.INAAnalysis.samples_id)} samples')

    def show_thermal_selfshielding(self, parent, M):
        code = self.sampleidlist.get_selection()
        sample = M.INAAnalysis.get_sample(code)
        if sample is not None:
            try:
                self.secondary_window.destroy()
            except:
                pass
            results = sample._display_thermal_self_shielding_contributors(M.INAAnalysis.abundances_database)

            self.secondary_window = tk.Toplevel(parent)
            self.secondary_window.title(f'Measurement sample ({sample.name})')
            self.secondary_window.resizable(False, False)

            mframe = tk.Frame(self.secondary_window)
            gui_things.SelfShieldingPeriodicTable(mframe, results, Gth=sample.Gth, default_palette=M.settings.get('color palette')).pack(anchor=tk.NW)
            mframe.pack(anchor=tk.NW, padx=5, pady=5)

        else:
            self.hintlabel.configure(text='no measurement sample is selected')

    def show_epithermal_selfshielding(self, parent, M):
        code = self.sampleidlist.get_selection()
        sample = M.INAAnalysis.get_sample(code)
        if sample is not None:
            try:
                self.secondary_window.destroy()
            except:
                pass

            self.secondary_window = tk.Toplevel(parent)
            self.secondary_window.title(f'Measurement sample ({sample.name})')
            self.secondary_window.resizable(False, False)

            mframe = tk.Frame(self.secondary_window)
            gui_things.EpithermalSelfShieldingPeriodicTable(mframe, sample.epi_shielding, resolution=2, default_palette=M.settings.get('color palette')).pack(anchor=tk.NW)
            mframe.pack(anchor=tk.NW, padx=5, pady=5)

        else:
            self.hintlabel.configure(text='no measurement sample is selected')

    def delete_sample(self, parent, M, mslabel, idlabel, rolelabel):
        code = self.sampleidlist.get_selection()
        sample = M.INAAnalysis.get_sample(code)
        if sample is not None:
            try:
                self.secondary_window.destroy()
            except:
                pass
            codes = [item.name for item in M.INAAnalysis.samples_id]
            idx = codes.index(code)
            if messagebox.askyesno(title='Delete sample data', message=f'\nAre you sure to delete all data\nrelated to {code} sample?\n', parent=parent):
                M.INAAnalysis.samples_id.pop(idx)
                for itx in range(len(M.INAAnalysis.spectra)):
                    if M.INAAnalysis.spectra[itx].sample == code:
                        M.INAAnalysis.spectra[itx].sample = None
                        idlabel.configure(text='-')
                        rolelabel.configure(text='-')

                self.update_selector(M, mslabel)
        else:
            self.hintlabel.configure(text='no measurement sample is selected')

    def add_sample(self, parent, M, mslabel):
        #open the window for measurement sample record
        try:
            self.secondary_window.destroy()
        except:
            pass
        self.modify_sample_form(parent, M, mslabel)

    def modify_sample(self, parent, M, mslabel):
        code = self.sampleidlist.get_selection()
        sample = M.INAAnalysis.get_sample(code)
        if sample is not None:
            #open the window for measurement sample record
            try:
                self.secondary_window.destroy()
            except:
                pass
            self.modify_sample_form(parent, M, mslabel, sample)
        else:
            self.hintlabel.configure(text='no measurement sample is selected')

    def modify_sample_form(self, parent, M, mslabel, sample=None):
        self.secondary_window = tk.Toplevel(parent)
        try:
            title = f'Measurement sample ({sample.name})'
        except AttributeError:
            title = 'New measurement sample'
        self.secondary_window.title(title)
        self.secondary_window.resizable(False, False)
        self.composition_subwindow = None
        mframe = tk.Frame(self.secondary_window)

        hintlabel = tk.Label(mframe, text='', anchor=tk.W)

        codeframe = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='identity'), relief='solid', bd=2, padx=4, pady=4)

        tk.Label(codeframe, text='code', anchor=tk.W, width=8).grid(row=0, column=0, sticky=tk.W)
        tk.Label(codeframe, text='role', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)

        self.code_F = gui_things.Entry(codeframe, width=20)
        self.code_F.grid(row=0, column=1, sticky=tk.W)
        self.code_F.delete(0, tk.END)
        F_font = self.code_F.cget('font')
        try:
            self.code_F.insert(0, sample.name)
        except AttributeError:
            pass

        self.role_CB = gui_things.Combobox(codeframe, width=20, state='readonly', font=F_font)
        self.role_CB.grid(row=1, column=1, sticky=tk.W)
        self.role_CB['values'] = self.sample_selector_CB['values'][1:]
        try:
            self.role_CB.set(sample.sampletype)
        except AttributeError:
            self.role_CB.set(self.role_CB['values'][0])

        self.useasCRM_variable = tk.IntVar(parent)

        self.CHB = gui_things.Checkbutton(codeframe, text='use as CRM', onvalue=1, offvalue=0, variable=self.useasCRM_variable)
        self.CHB.grid(row=2, column=1, sticky=tk.W)
        try:
            self.useasCRM_variable.set(sample.asCRM)
        except AttributeError:
            self.useasCRM_variable.set(0)
        if self.role_CB.get() == 'sample':
            self.CHB.configure(state=tk.NORMAL)
        else:
            self.CHB.configure(state=tk.DISABLED)

        codeframe.grid(row=0, column=0, sticky=tk.NSEW, pady=3, padx=3)

        self.standard_choices = ['single material', 'pipetted solutions']
        self.sample_choices = ['single material']
        compositionframe = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='composition'), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(compositionframe, text='sample type', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        self.ctype_CB = gui_things.Combobox(compositionframe, width=20, state='readonly')
        if self.role_CB.get() == 'sample':
            self.ctype_CB['values'] = self.sample_choices
        else:
            self.ctype_CB['values'] = self.standard_choices
        try:
            self.ctype_CB.set(sample.composition.compositiontype)
            self.composition = sample.composition
        except AttributeError:
            self.ctype_CB.set(self.ctype_CB['values'][0])
            self.composition = naaobject.Composition(self.ctype_CB.get())
        self.ctype_CB.grid(row=0, column=1, padx=5)

        logo_composition = tk.PhotoImage(data=gui_things.PL_list)
        B_changecomposition = gui_things.Button(compositionframe, image=logo_composition, hint='manage measurement sample composition', hint_destination=hintlabel, command=lambda : self.modify_composition(M))
        B_changecomposition.grid(row=0, column=2, padx=5)
        B_changecomposition.image = logo_composition

        self.description = gui_things.ScrollableText(compositionframe, width=32, height=13, data=self.composition.get_information_text())
        self.description.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW, pady=5)

        compositionframe.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW, pady=3, padx=3)

        physicalframe = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='geometry'), relief='solid', bd=2, padx=4, pady=4)

        tk.Label(physicalframe, text='x').grid(row=0, column=1)
        tk.Label(physicalframe, text='u(x)').grid(row=0, column=2)

        tk.Label(physicalframe, text='height / mm', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
        tk.Label(physicalframe, text='diameter / mm', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
        tk.Label(physicalframe, text='density / g cm⁻³', anchor=tk.W).grid(row=3, column=0, sticky=tk.W)
        self.height_F = gui_things.Spinbox(physicalframe, width=8, from_=0.0, to=250.0, increment=0.1, font=F_font)
        self.height_F.grid(row=1, column=1, padx=3)
        self.height_F.delete(0, tk.END)
        try:
            self.height_F.insert(0, sample.height)
        except AttributeError:
            self.height_F.insert(0, 0.0)
        self.unc_height_F = gui_things.Spinbox(physicalframe, width=8, from_=0.0, to=50.0, increment=0.1, font=F_font)
        self.unc_height_F.grid(row=1, column=2, padx=3)
        self.unc_height_F.delete(0, tk.END)
        try:
            self.unc_height_F.insert(0, sample.height_unc)
        except AttributeError:
            self.unc_height_F.insert(0, 0.0)

        self.diameter_F = gui_things.Spinbox(physicalframe, width=8, from_=0.0, to=250.0, increment=0.1, font=F_font)
        self.diameter_F.grid(row=2, column=1, padx=3)
        self.diameter_F.delete(0, tk.END)
        try:
            self.diameter_F.insert(0, sample.diameter)
        except AttributeError:
            self.diameter_F.insert(0, 0.0)
        self.unc_diameter_F = gui_things.Spinbox(physicalframe, width=8, from_=0.0, to=50.0, increment=0.1, font=F_font)
        self.unc_diameter_F.grid(row=2, column=2, padx=3)
        self.unc_diameter_F.delete(0, tk.END)
        try:
            self.unc_diameter_F.insert(0, sample.diameter_unc)
        except AttributeError:
            self.unc_diameter_F.insert(0, 0.0)

        self.density_F = gui_things.Spinbox(physicalframe, width=8, from_=0.000, to=20.000, increment=0.001, font=F_font)
        self.density_F.grid(row=3, column=1, padx=3)
        self.density_F.delete(0, tk.END)
        try:
            self.density_F.insert(0, sample.density)
        except AttributeError:
            self.density_F.insert(0, 0.000)
        self.unc_density_F = gui_things.Spinbox(physicalframe, width=8, from_=0.000, to=5.000, increment=0.001, font=F_font)
        self.unc_density_F.grid(row=3, column=2, padx=3)
        self.unc_density_F.delete(0, tk.END)
        try:
            self.unc_density_F.insert(0, sample.density_unc)
        except AttributeError:
            self.unc_density_F.insert(0, 0.000)

        logo_dcalculator = tk.PhotoImage(data=gui_things.PL_operations)
        B_densitycalculator = gui_things.Button(physicalframe, image=logo_dcalculator, hint='calculate density', hint_destination=hintlabel, command=lambda : self.density_calculator(M, hintlabel))
        B_densitycalculator.grid(row=3, column=3, padx=5)
        B_densitycalculator.image = logo_dcalculator

        physicalframe.grid(row=1, column=0, sticky=tk.NW, pady=3, padx=3)

        logo_savedata = tk.PhotoImage(data=gui_things.PL_check)
        B_savesampledata = gui_things.Button(mframe, image=logo_savedata, hint='save measurement sample data', hint_destination=hintlabel, command=lambda : self.save_sample_data(M, mslabel, hintlabel))
        B_savesampledata.grid(row=2, column=0, columnspan=2)
        B_savesampledata.image = logo_savedata

        hintlabel.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        mframe.pack(anchor=tk.NW, padx=5, pady=5)

        self.role_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_role())
        self.ctype_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.select_ctype())

    def mass_calculator(self):
        m, um = 0.0, 0.0
        if self.composition.compositiontype == 'pipetted solutions':
            m = np.sum([self.composition.mass * value[0] for _, value in self.composition.certificate.items()])
            header = np.array([[self.composition.mass, self.composition.umass, 0.0]])
            m_values = np.array([[value[0], value[1], 0.0] for _, value in self.composition.certificate.items()])
            m_values = np.append(header, m_values, axis=0)
            for idx in range(m_values.shape[0]):
                #value, uncertainty, sensitivity coefficient, working column
                plus, minus = m_values[:,0].copy(), m_values[:,0].copy()
                plus[idx] = m_values[idx,0] + m_values[idx,1]
                minus[idx] = m_values[idx,0] - m_values[idx,1]
                m_values[idx, 2] = (plus[0] * np.sum(plus[1:]) - minus[0] * np.sum(minus[1:])) / (2 * m_values[idx,1] + 1E-24)

            um = np.sqrt(np.sum(np.power(m_values[:,1] * m_values[:,2], 2)))
        else:
            try:
                m = self.composition.mass
            except AttributeError:
                m = 0.0
            try:
                um = self.composition.umass
            except AttributeError:
                um = 0.0
        return m, um

    def density_calculator(self, M, hintlabel):
        #different density calculations depending on the compositiontype(solutions, single material)
        m, um = self.mass_calculator()

        try:
            h = float(self.height_F.get()) / 10
        except ValueError:
            h = 0.0
        try:
            uh = float(self.unc_height_F.get()) / 10
        except ValueError:
            uh = 0.0

        try:
            d = float(self.diameter_F.get()) / 10
        except ValueError:
            d = 0.0
        try:
            ud = float(self.unc_diameter_F.get()) / 10
        except ValueError:
            ud = 0.0

        #density in g cm-3
        den = (np.power(d/2, 2) * np.pi * h)
        if den == 0.0:
            density = 0.0
            udensity = 0.0
        else:
            density = m / den
            pdm = 1 / (np.pi * np.power(d/2, 2) * h)
            pdd = (-2 * m) / (np.pi * h * np.power(d/2, 3))
            pdh = -m / (np.pi * np.power(d/2, 2) * np.power(h, 2))
            udensity = np.sqrt(np.power(um * pdm, 2) + np.power(ud * pdd, 2) + np.power(uh * pdh, 2))

        if density > 0.0 and udensity >= 0.0:
            self.density_F.delete(0, tk.END)
            self.density_F.insert(0, f'{density:.5f}')
            self.unc_density_F.delete(0, tk.END)
            self.unc_density_F.insert(0, f'{udensity:.5f}')
        else:
            hintlabel.configure(text='invalid density calcuated')

    def select_role(self):
        self.useasCRM_variable.set(0)
        if self.role_CB.get() == 'sample':
            self.CHB.configure(state=tk.NORMAL)
        else:
            self.CHB.configure(state=tk.DISABLED)
        if self.role_CB.get() == 'sample':
            self.ctype_CB['values'] = self.sample_choices
        else:
            self.ctype_CB['values'] = self.standard_choices
        self.ctype_CB.set(self.ctype_CB['values'][0])

        try:
            self.composition_subwindow.destroy()
        except:
            pass

        self.composition = naaobject.Composition(self.ctype_CB.get())
        self.description._update(data=self.composition.get_information_text())

    def select_ctype(self):
        try:
            self.composition_subwindow.destroy()
        except:
            pass
        self.composition = naaobject.Composition(self.ctype_CB.get())
        self.description._update(data=self.composition.get_information_text())

    def modify_composition(self, M):
        forms = {'single material':self.single_material_subwindow, 'pipetted solutions':self.pipetted_solutions_subwindow}
        if self.composition_subwindow is not None:
            try:
                self.composition_subwindow.destroy()
            except:
                pass
        get_form = forms.get(self.ctype_CB.get(), None)
        if get_form is not None:
            get_form(self.secondary_window, M)
        else:
            M.hintlabel.configure(text='not implemented')

    def single_material_subwindow(self, parent, M):
        self.composition_subwindow = tk.Toplevel(parent)
        title = 'Manage composition - single material'
        self.composition_subwindow.title(title)
        self.composition_subwindow.resizable(False, False)
        mframe = tk.Frame(self.composition_subwindow)
        hintlabel = tk.Label(mframe, text='', anchor=tk.W)
        left_frame = tk.Frame(mframe)
        header = tk.LabelFrame(left_frame, labelwidget=tk.Label(mframe, text='material selection'), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(header, text='material', width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.material_selector = gui_things.HelpedCombobox(header, width=25, data=(), hint='select material', hint_xoffset=0, hint_destination=hintlabel, allow_new_input=False, default_invalid='')
        if self.role_CB.get() == 'standard':
            self.material_selector._update([os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'samples')) if filename.lower().endswith('.csv')])
        else:
            self.material_selector._update([os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'samples')) if filename.lower().endswith('.csv')] + [''])
        self.material_selector.pack(side=tk.LEFT, padx=5)
        header.pack(anchor=tk.NW, fill=tk.X, expand=True)

        inserter = tk.LabelFrame(left_frame, labelwidget=tk.Label(mframe, text='mass information'), relief='solid', bd=2, padx=4, pady=4)
        tk.Label(inserter, text='x').grid(row=0, column=1)
        tk.Label(inserter, text='u(x)').grid(row=0, column=2)
        tk.Label(inserter, text='mass / g', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
        tk.Label(inserter, text='moisture / %', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
        self.mass_F = gui_things.Spinbox(inserter, width=10, from_=0.000, to=10.000, increment=0.001)
        self.mass_F.grid(row=1, column=1, padx=5)
        self.mass_F.delete(0, tk.END)
        try:
            self.mass_F.insert(0, self.composition.mass)
        except AttributeError:
            self.mass_F.insert(0, 0.000)
        self.umass_F = gui_things.Spinbox(inserter, width=10, from_=0.000, to=1.0, increment=0.001)
        self.umass_F.grid(row=1, column=2, padx=5)
        self.umass_F.delete(0, tk.END)
        try:
            self.umass_F.insert(0, self.composition.umass)
        except AttributeError:
            self.umass_F.insert(0, 0.000)

        self.moisture_F = gui_things.Spinbox(inserter, width=10, from_=0.0, to=100.0, increment=0.1)
        self.moisture_F.grid(row=2, column=1, padx=5)
        self.moisture_F.delete(0, tk.END)
        try:
            self.moisture_F.insert(0, self.composition.moisture)
        except AttributeError:
            self.moisture_F.insert(0, 0.0)
        self.umoisture_F = gui_things.Spinbox(inserter, width=10, from_=0.0, to=10.0, increment=0.1)
        self.umoisture_F.grid(row=2, column=2, padx=5)
        self.umoisture_F.delete(0, tk.END)
        try:
            self.umoisture_F.insert(0, self.composition.umoisture)
        except AttributeError:
            self.umoisture_F.insert(0, 0.0)
        
        inserter.pack(anchor=tk.NW, fill=tk.X, expand=True)

        displayer = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='material information'), relief='solid', bd=2, padx=4, pady=4)
        self.display_materialinfo = gui_things.ScrollableText(displayer, width=40, height=25)
        self.display_materialinfo.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        displayer.grid(row=0, column=1, rowspan=12, sticky=tk.NSEW, padx=5)

        logo_savedata = tk.PhotoImage(data=gui_things.PL_check)
        B_savesampledata = gui_things.Button(left_frame, image=logo_savedata, hint='save current composition', hint_destination=hintlabel, command=lambda : self.save_single_material_data(hintlabel))
        B_savesampledata.pack(anchor=tk.N, pady=10)
        B_savesampledata.image = logo_savedata

        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)

        hintlabel.grid(row=12, column=0, columnspan=2, sticky=tk.EW)

        mframe.pack(anchor=tk.NW, padx=5, pady=5)

        self.material_selector.Combobox.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.disclose_material())

        try:
            self.material_selector.Combobox.set(self.composition.data[0][4].name)
            self.disclose_material()
        except (AttributeError, IndexError):
            pass
    
    def pipetted_solutions_subwindow(self, parent, M):
        self.composition_subwindow = tk.Toplevel(parent)
        title = 'Manage composition - pipetted solutions'
        self.composition_subwindow.title(title)
        self.composition_subwindow.resizable(False, False)

        self.index_list = 0

        mframe = tk.Frame(self.composition_subwindow)
        hintlabel = tk.Label(mframe, text='', anchor=tk.W)
        header = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='pipetted solutions'), relief='solid', bd=2, padx=4, pady=4)
        self.pipsLB = gui_things.ScrollableListbox(header, width=30, height=12, data=self._to_text(), font=('Courier', 10))
        self.pipsLB.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        header.grid(row=0, column=0, sticky=tk.NSEW)

        pipetter = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='pipetting information'), relief='solid', bd=2, padx=4, pady=4)

        action_counter = tk.Frame(pipetter)

        logo_addaction = tk.PhotoImage(data=gui_things.PL_pipet)
        B_addactiondata = gui_things.Button(action_counter, image=logo_addaction, hint='add new pipetting', hint_destination=hintlabel, command=lambda : self.add_action())
        B_addactiondata.grid(row=0, column=0, rowspan=2, padx=3, pady=3)
        B_addactiondata.image = logo_addaction

        tk.Label(action_counter, text='action').grid(row=0, column=1)
        self.n_action = tk.Label(action_counter, text='')
        self.n_action.grid(row=1, column=1)

        action_counter.pack(side=tk.LEFT, anchor=tk.NW)

        ttk.Separator(pipetter, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=5)

        action_worker = tk.Frame(pipetter)

        tk.Label(action_worker, text='m / g').grid(row=3, column=2)
        tk.Label(action_worker, text='u(m) / g').grid(row=3, column=3)
        tk.Frame(action_worker).grid(row=2, column=0, pady=3)
        tk.Label(action_worker, text='material').grid(row=0, column=2, columnspan=2, sticky=tk.EW)

        self.mass_F = gui_things.Spinbox(action_worker, width=10, from_=0.000, to=10.000, increment=0.001)
        self.mass_F.grid(row=4, column=2, padx=5)
        self.mass_F.delete(0, tk.END)
        self.mass_F.insert(0, 0.000)
        self.mass_F.configure(state=tk.DISABLED)

        self.umass_F = gui_things.Spinbox(action_worker, width=10, from_=0.000, to=1.0, increment=0.001)
        self.umass_F.grid(row=4, column=3, padx=5)
        self.umass_F.delete(0, tk.END)
        self.umass_F.insert(0, 0.000)
        self.umass_F.configure(state=tk.DISABLED)
        
        self.material_selector = gui_things.HelpedCombobox(action_worker, width=25, data=[os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'samples')) if filename.lower().endswith('.csv') and naaobject.Material(f'{os.path.splitext(filename)[0]}.csv').state=='solution'], hint='select material', hint_xoffset=0, hint_destination=hintlabel, allow_new_input=False, default_invalid='')
        self.material_selector.grid(row=1, column=2, columnspan=2, sticky=tk.EW)
        self.material_selector.Combobox.configure(state='disabled')

        logo_deletedata = tk.PhotoImage(data=gui_things.PL_none)
        B_deletesampledata = gui_things.Button(action_worker, image=logo_deletedata, hint='delete current datum', hint_destination=hintlabel, command=lambda : self.delete_pipetting(hintlabel))
        B_deletesampledata.grid(row=0, column=5, rowspan=2, padx=3, pady=3)
        B_deletesampledata.image = logo_deletedata

        logo_savedata = tk.PhotoImage(data=gui_things.PL_ggear)
        B_savesampledata = gui_things.Button(action_worker, image=logo_savedata, hint='save/modify current datum', hint_destination=hintlabel, command=lambda : self.save_modify_pipetting(hintlabel))
        B_savesampledata.grid(row=0, column=4, rowspan=2, padx=3, pady=3)
        B_savesampledata.image = logo_savedata

        action_worker.pack(side=tk.LEFT, anchor=tk.NW)

        pipetter.grid(row=1, column=0, sticky=tk.NSEW)

        displayer = tk.LabelFrame(mframe, labelwidget=tk.Label(mframe, text='material information'), relief='solid', bd=2, padx=4, pady=4)
        self.display_materialinfo = gui_things.ScrollableText(displayer, width=50, height=20)
        self.display_materialinfo.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        displayer.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW, padx=5)

        logo_savecomposition = tk.PhotoImage(data=gui_things.PL_check)
        B_savesamplecomposition = gui_things.Button(mframe, image=logo_savecomposition, hint='save current composition', hint_destination=hintlabel, command=lambda : self.save_pipetted_material_data(hintlabel))
        B_savesamplecomposition.grid(row=3, column=0, columnspan=2, padx=3, pady=3)
        B_savesamplecomposition.image = logo_savecomposition

        hintlabel.grid(row=4, column=0, sticky=tk.EW)

        mframe.pack(anchor=tk.NW, padx=5, pady=5)

        self.pipsLB.listbox.bind('<Double-Button-1>', lambda e='<Double-Button-1>': self.select_line(hintlabel))
        self.material_selector.Combobox.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.disclose_material())

    def save_pipetted_material_data(self, hintlabel):
        text = 'no pipetting data introduced'
        self.disclose_material()

        if len(self.composition.data) > 0:
            pmass, pumass, pmoist, pumoist, psample = [], [], [], [], []
            for line in self.composition.data:
                pmass.append(line[0])
                pumass.append(line[1])
                pmoist.append(line[2])
                pumoist.append(line[3])
                psample.append(line[4])
            self.composition = naaobject.Composition(self.ctype_CB.get(), masses=pmass, unc_masses=pumass, moistures=pmoist, umoistures=pumoist, samples=psample)
            self.description._update(data=self.composition.get_information_text())
            text = 'composition successfully saved'
        hintlabel.configure(text=text)

    def add_action(self):
        self.n_action.configure(text=f'{len(self.composition.data)+1}')
        self.mass_F.delete(0, tk.END)
        self.mass_F.insert(0, 0.000)
        self.umass_F.delete(0, tk.END)
        self.umass_F.insert(0, 0.000)
        self.material_selector.Combobox.set('')

        self.mass_F.configure(state=tk.NORMAL)
        self.umass_F.configure(state=tk.NORMAL)
        self.material_selector.Combobox.configure(state='normal')

        self.disclose_material()

    def delete_pipetting(self, hintlabel):
        n_action = self.n_action.cget('text')
        if n_action == '':
            proceed = False
        else:
            n_action = int(n_action)
            proceed = True

        if proceed and n_action <= len(self.composition.data):
            if messagebox.askyesno(title='Delete pipetting data', message='\nAre you sure to delete the selected entry?\n', parent=self.composition_subwindow):
                self.composition.data.pop(n_action-1)
                self.pipsLB._update(self._to_text())

                self.n_action.configure(text='')
                self.mass_F.delete(0, tk.END)
                self.mass_F.insert(0, 0.000)
                self.umass_F.delete(0, tk.END)
                self.umass_F.insert(0, 0.000)
                self.material_selector.set('')
                self.display_information('')

                if len(self.composition.data) == 0:
                    self.mass_F.configure(state=tk.DISABLED)
                    self.umass_F.configure(state=tk.DISABLED)
                    self.material_selector.Combobox.configure(state='disabled')
        else:
            hintlabel.configure(text='no datum is selected')

    def select_line(self, hintlabel):
        try:
            ixx = self.pipsLB.curselection()[0]
        except IndexError:
            hintlabel.configure(text='no selected data')
        else:
            mass, umass, _, _, psample = self.composition.data[ixx]

            self.n_action.configure(text=f'{ixx+1}')
            self.mass_F.delete(0, tk.END)
            self.mass_F.insert(0, mass)
            self.umass_F.delete(0, tk.END)
            self.umass_F.insert(0, umass)
            self.material_selector.set(psample.name)
            text = psample._as_text_display(preamble=f'Name: {psample.name}\n\nDescription: {psample.description}\n\nType: {psample.sample_type}\n\n')
            self.display_information(text)

    def save_modify_pipetting(self, hintlabel):
        n_action = self.n_action.cget('text')
        if n_action == '':
            proceed = False
            problem = 'no action selected'
        else:
            n_action = int(n_action)
            proceed = True
        try:
            mass = float(self.mass_F.get())
        except ValueError:
            mass = 0
            proceed = False
            problem = 'B'
        if mass <= 0:
            proceed = False
            problem = 'invalid mass'
        try:
            umass = float(self.umass_F.get())
        except ValueError:
            umass = -1
            proceed = False
            problem = 'D'
        if umass < 0:
            proceed = False
            problem = 'invalid mass uncertainty'

        if self.material_selector.get() != '':
            psample = naaobject.Material(f'{self.material_selector.get()}.csv')
        else:
            psample = None
            proceed = False
            problem = 'invalid material selected'

        if proceed and n_action > len(self.composition.data):
            self.composition.data.append((mass, umass, 0., 0., psample))
            self.pipsLB._update(self._to_text())
        elif proceed and n_action <= len(self.composition.data):
            self.composition.data[n_action-1] = (mass, umass, 0., 0., psample)
            self.pipsLB._update(self._to_text())
        else:
            hintlabel.configure(text=problem)

    def _to_text(self):
        return [f'{format(nn, "d").ljust(4)}{format(mass, ".2e").rjust(10)} g, {sample.name[:20]}' for nn, (mass, umass, moisture, umoisture, sample) in enumerate(self.composition.data, start=1)]

    def disclose_material(self):
        filename = self.material_selector.get()
        try:
            provisional_sample = naaobject.Material(f'{filename}.csv')
            text = provisional_sample._as_text_display(preamble=f'Name: {provisional_sample.name}\n\nDescription: {provisional_sample.description}\n\nType: {provisional_sample.sample_type}\n\n')
            self.display_information(text)
        except Exception:
            pass

    def display_information(self, text):
        self.display_materialinfo._update(text)

    def save_single_material_data(self, hintlabel):
        advance = True
        psample = naaobject.Material(f'{self.material_selector.get()}.csv')
        try:
            pmass = float(self.mass_F.get())
        except ValueError:
            pmass = -1
            advance = False
        try:
            pumass = float(self.umass_F.get())
        except ValueError:
            pumass = -1
            advance = False
        try:
            pmoist = float(self.moisture_F.get())
        except ValueError:
            pmoist = -1
            advance = False
        try:
            pumoist = float(self.umoisture_F.get())
        except ValueError:
            pumoist = -1
            advance = False
        if pmass <= 0.0 or pumass < 0.0 or pmoist < 0.0 or pumoist < 0.0:
            advance = False

        if advance:
            self.composition = naaobject.Composition(self.ctype_CB.get(), masses=(pmass,), unc_masses=(pumass,), moistures=(pmoist,), umoistures=(pumoist,), samples=(psample,))
            self.description._update(data=self.composition.get_information_text())
            text = 'composition successfully saved'
        else:
            text = 'some error occurred'
        hintlabel.configure(text=text)

    def save_sample_data(self, M, mslabel, hintlabel):
        advance = True
        msg = []
        ms_name = self.code_F.get()
        if ms_name.replace(' ','') == '':
            advance = False
            msg.append('invalid sample code')
        ms_role = self.role_CB.get()
        if ms_role == 'standard':
            if self.composition.isvoid():
                advance = False
                msg.append('invalid composition for standard')
        else:
            if self.composition.isnan():
                advance = False
                msg.append('invalid composition')
        try:
            ms_height = float(self.height_F.get())
        except (TypeError, ValueError):
            ms_height = 0.0
            advance = False
            msg.append('invalid height')
        if ms_height <= 0.0:
            advance = False
            msg.append('invalid height')

        try:
            ms_uncheight = float(self.unc_height_F.get())
        except (TypeError, ValueError):
            ms_uncheight = 0.0
            advance = False
            msg.append('invalid uncertainty of height')
        if ms_uncheight < 0.0 or ms_uncheight >= ms_height:
            advance = False
            msg.append('invalid uncertainty of height')

        try:
            ms_diameter = float(self.diameter_F.get())
        except (TypeError, ValueError):
            ms_diameter = 0.0
            advance = False
            msg.append('invalid diameter')
        if ms_diameter <= 0.0:
            advance = False
            msg.append('invalid diameter')

        try:
            ms_uncdiameter = float(self.unc_diameter_F.get())
        except (TypeError, ValueError):
            ms_uncdiameter = 0.0
            advance = False
            msg.append('invalid uncertainty of diameter')
        if ms_uncdiameter < 0.0 or ms_uncdiameter >= ms_diameter:
            advance = False
            msg.append('invalid uncertainty of diameter')

        try:
            ms_density = float(self.density_F.get())
        except (TypeError, ValueError):
            ms_density = 0.0
            advance = False
            msg.append('invalid density')
        if ms_density < 0.0:
            advance = False
            msg.append('invalid density')

        try:
            ms_uncdensity = float(self.unc_density_F.get())
        except (TypeError, ValueError):
            ms_uncdensity = 0.0
            advance = False
            msg.append('invalid uncertainty of density')
        if ms_uncdensity <= 0.0 and ms_uncdensity >= ms_density:
            advance = False
            msg.append('invalid uncertainty of density')

        if len(msg) > 0:
            main_error = msg[0]
        else:
            main_error = ''
        if len(set(msg)) > 1:
            msgtext = f'{main_error} and other {len(set(msg)) - 1} errors'
        else:
            msgtext = f'{main_error}'

        if advance:
            NMS = naaobject.MeasurementSample(ms_name, self.composition, ms_role, self.useasCRM_variable.get(), ms_height, ms_uncheight, ms_diameter, ms_uncdiameter, ms_density, ms_uncdensity, M.INAAnalysis.abundances_database)
            if NMS.name not in [item.name for item in M.INAAnalysis.samples_id]:
                M.INAAnalysis.samples_id.append(NMS)
                self.update_selector(M, mslabel)
            else:
                if messagebox.askyesno(title='Overwrite measurement sample', message=f'\na measurement sample with same code is already present in the list,\ndo you want to overwrite it?\n', parent=self.secondary_window):
                    for n, item in enumerate(M.INAAnalysis.samples_id):
                        if item.name == NMS.name:
                            M.INAAnalysis.samples_id[n] = NMS
                            break
                    self.update_selector(M, mslabel)
                else:
                    hintlabel.configure(text='changes aborted')
        else:
            hintlabel.configure(text=msgtext)


class Settings:
    def __init__(self, filename='settings.cfg', folder='data', home='.'):
        self.filepath = os.path.join(os.path.join(home, folder), filename)
        self.information = self._get_settings_from_file()

    def get(self, key):
        #get setting value
        return self.information[key]

    def set(self, key, value):
        #set setting value
        #value: any class with a get method
        dtype = type(self.information[key])
        self.information[key] = dtype(value.get())

    def dump(self):
        self.write_settings_on_file(self.filepath, self.information)

    def _get_settings_from_file(self):
        try:
            with open(self.filepath, 'r') as k0_settings_file:
                information = {line.replace('\n','').split(' <#> ')[0]: self._get_correct_datatype(line.replace('\n','').split(' <#> ')[-1], traceline[1], traceline[2]) for line,traceline in zip(k0_settings_file.readlines(), self.default_settings())}
        except (FileNotFoundError, ValueError, IndexError, KeyError):
            information = {line[0]:line[2] for line in self.default_settings()}
            self.write_settings_on_file(self.filepath, information)
        return information

    def _get_correct_datatype(self, datum, datatype=str, default=None):
        datatypes = {'str':str, 'int':int, 'float':float, 'bool': lambda x : bool(int(x))}
        func = datatypes[datatype]
        return func(datum)

    def default_settings(self):
        #master settings list
        #descriptor, datatype, default_value
        master_settings = (
		('database', 'str', 'from_k0data'),
        ('cross_chem_data', 'str', 'shielding-abundance_table'),
        ('gabs_data', 'str', 'absorptions_table'),
        ('coincidence_data', 'str', 'coi_database'),
        ('yfiss_data', 'str', 'yfiss_database'),
		('energy tolerance', 'float', 0.4),
		('page height', 'int', 25),
		('max allowed calibration uncertainty', 'int', 80),
		('calibs statistical uncertainty limit', 'int', 5),
		('standard statistical uncertainty limit', 'int', 15),
		('sample statistical uncertainty limit', 'int', 40),
		('non certified standard uncertainties', 'int', 10),
		('default tc&tl uncertainties', 'float', 0.1),
		('default td uncertainty', 'float', 10.0),
		('look for spectrum file', 'bool', 1),
        ('literature cross section non certified uncertainties', 'int', 20),
        ('lock cells in output file', 'bool', 1),
        ('display graph in flux database', 'bool', 1),
        ('color01', 'str', '#000000'),
        ('color02', 'str', '#FBB917'),
        ('color03', 'str', '#990012'),
        ('color04', 'str', '#0020C2'),
        ('color05', 'str', '#FFFFFF'),
        ('color06', 'str', '#C38EC7'),
        ('color07', 'str', '#2E8B57'),
        ('color08', 'str', '#FF8C00'),
        ('color09', 'str', '#663399'),
        ('color10', 'str', '#7F5217'),
        ('color11', 'str', '#E75480'),
        ('color12', 'str', '#4EE2EC'),
        ('overwrite manual emission selection', 'bool', 0),
        ('color palette', 'str', 'tab20b'),
        ('count rate threshold', 'int', 100),
        ('elaborate only selected emissions', 'bool', 1),
        ('max iterations', 'int', 5),
        ('excel internal links', 'bool', 1),
        ('excel worksheet lock', 'bool', 0),
        ('merge with prior', 'str', 'neglect'),
        ('average method', 'str', 'weighted'),
        ('visible models', 'bool', 1),
        ('hide grid', 'bool', 1),
        ('check internal consistency', 'bool', 1),
        ('z limit', 'float', 3.0),
        ('f&a correlation', 'float', -0.5))
        return master_settings

    def get_bool_right(self, value):
        if type(value) == bool:
            return int(value)
        return value

    def write_settings_on_file(self, filepath, information):
        with open(filepath, 'w') as missing_or_corrupted_setting_file:
            for line in self.default_settings():
                missing_or_corrupted_setting_file.write(f'{line[0]} <#> {self.get_bool_right(information[line[0]])}\n')


def main_script():
    home = os.path.abspath('.')
    settings = Settings(home=home)
    M = tk.Tk()
    MainWindow(M, settings, home)
    M.mainloop()


if __name__ == '__main__':
    main_script()