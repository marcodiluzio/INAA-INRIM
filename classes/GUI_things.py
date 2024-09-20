# -*- coding: utf-8 -*-

"""
Stores images data to be recalled as icons and modified tkinter Widgets Classes
"""

import tkinter
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
import os
import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib import colors as mcolors
from matplotlib import cm
from classes.naaoutputs import SingleBudgetOutput, analysisoutput, ResultReport

periodic_data = (
            (1,'H',0,0,'Hydrogen'),
            (2,'He',0,17,'Helium'),
            (3,'Li',1,0,'Lithium'),
            (4,'Be',1,1,'Beryllium'),
            (5,'B',1,12,'Boron'),
            (6,'C',1,13,'Carbon'),
            (7,'N',1,14,'Nitrogen'),
            (8,'O',1,15,'Oxygen'),
            (9,'F',1,16,'Fluorine'),
            (10,'Ne',1,17,'Neon'),
            (11,'Na',2,0,'Sodium'),
            (12,'Mg',2,1,'Magnesium'),
            (13,'Al',2,12,'Aluminium'),
            (14,'Si',2,13,'Silicon'),
            (15,'P',2,14,'Phosphorus'),
            (16,'S',2,15,'Sulfur'),
            (17,'Cl',2,16,'Chlorine'),
            (18,'Ar',2,17,'Argon'),
            (19,'K',3,0,'Potassium'),
            (20,'Ca',3,1,'Calcium'),
            (21,'Sc',3,2,'Scandium'),
            (22,'Ti',3,3,'Titanium'),
            (23,'V',3,4,'Vanadium'),
            (24,'Cr',3,5,'Chromium'),
            (25,'Mn',3,6,'Manganese'),
            (26,'Fe',3,7,'Iron'),
            (27,'Co',3,8,'Cobalt'),
            (28,'Ni',3,9,'Nickel'),
            (29,'Cu',3,10,'Copper'),
            (30,'Zn',3,11,'Zinc'),
            (31,'Ga',3,12,'Gallium'),
            (32,'Ge',3,13,'Germanium'),
            (33,'As',3,14,'Arsenic'),
            (34,'Se',3,15,'Selenium'),
            (35,'Br',3,16,'Bromine'),
            (36,'Kr',3,17,'Krypton'),
            (37,'Rb',4,0,'Rubidium'),
            (38,'Sr',4,1,'Strontium'),
            (39,'Y',4,2,'Yttrium'),
            (40,'Zr',4,3,'Zirconium'),
            (41,'Nb',4,4,'Niobium'),
            (42,'Mo',4,5,'Molybdenum'),
            (43,'Tc',4,6,'Technetium'),
            (44,'Ru',4,7,'Ruthenium'),
            (45,'Rh',4,8,'Rhodium'),
            (46,'Pd',4,9,'Palladium'),
            (47,'Ag',4,10,'Silver'),
            (48,'Cd',4,11,'Cadmium'),
            (49,'In',4,12,'Indium'),
            (50,'Sn',4,13,'Tin'),
            (51,'Sb',4,14,'Antimony'),
            (52,'Te',4,15,'Tellurium'),
            (53,'I',4,16,'Iodine'),
            (54,'Xe',4,17,'Xenon'),
            (55,'Cs',5,0,'Caesium'),
            (56,'Ba',5,1,'Barium'),
            (72,'Hf',5,3,'Hafnium'),
            (73,'Ta',5,4,'Tantalum'),
            (74,'W',5,5,'Tungsten'),
            (75,'Re',5,6,'Rhenium'),
            (76,'Os',5,7,'Osmium'),
            (77,'Ir',5,8,'Iridium'),
            (78,'Pt',5,9,'Platinum'),
            (79,'Au',5,10,'Gold'),
            (80,'Hg',5,11,'Mercury'),
            (81,'Tl',5,12,'Thallium'),
            (82,'Pb',5,13,'Lead'),
            (83,'Bi',5,14,'Bismuth'),
            (84,'Po',5,15,'Polonium'),
            (85,'At',5,16,'Astatine'),
            (86,'Rn',5,17,'Radon'),
            (87,'Fr',6,0,'Francium'),
            (88,'Ra',6,1,'Radium'),
            (104,'Rf',6,3,'Rutherfordium'),
            (105,'Db',6,4,'Dubnium'),
            (106,'Sg',6,5,'Seaborgium'),
            (107,'Bh',6,6,'Bohrium'),
            (108,'Hs',6,7,'Hassium'),
            (109,'Mt',6,8,'Meitnerium'),
            (110,'Ds',6,9,'Darmstadtium'),
            (111,'Rg',6,10,'Roentgenium'),
            (112,'Cn',6,11,'Copernicium'),
            (113,'Nh',6,12,'Nihonium'),
            (114,'Fl',6,13,'Flerovium'),
            (115,'Mc',6,14,'Moscovium'),
            (116,'Lv',6,15,'Livermorium'),
            (117,'Ts',6,16,'Tennessine'),
            (118,'Og',6,17,'Oganesson'),
            (57,'La',8,2,'Lanthanum'),
            (58,'Ce',8,3,'Cerium'),
            (59,'Pr',8,4,'Praseodymium'),
            (60,'Nd',8,5,'Neodymium'),
            (61,'Pm',8,6,'Promethium'),
            (62,'Sm',8,7,'Samarium'),
            (63,'Eu',8,8,'Europium'),
            (64,'Gd',8,9,'Gadolinium'),
            (65,'Tb',8,10,'Terbium'),
            (66,'Dy',8,11,'Dysprosium'),
            (67,'Ho',8,12,'Holmium'),
            (68,'Er',8,13,'Erbium'),
            (69,'Tm',8,14,'Thulium'),
            (70,'Yb',8,15,'Ytterbium'),
            (61,'Lu',8,16,'Lutetium'),
            (89,'Ac',9,2,'Actinium'),
            (90,'Th',9,3,'Thorium'),
            (91,'Pa',9,4,'Protoactinium'),
            (92,'U',9,5,'Uranium'),
            (93,'Np',9,6,'Neptunium'),
            (94,'Pu',9,7,'Plutonium'),
            (95,'Am',9,8,'Americium'),
            (96,'Cm',9,9,'Curium'),
            (97,'Bk',9,10,'Berkelium'),
            (98,'Cf',9,11,'Californium'),
            (99,'Es',9,12,'Einsteinium'),
            (100,'Fm',9,13,'Fermium'),
            (101,'Md',9,14,'Mendelevium'),
            (102,'No',9,15,'Nobelium'),
            (103,'Lr',9,16,'Lawrencium')
        )


def _get_final_composition(budget_list, original_composition=None):

	if original_composition is None:
		original_composition = {}
    

	def weighed_average(_all_target_list, target):
		value, sumofweights = np.average(_all_target_list[_all_target_list['target'] == target]['y'], weights=1/np.power(_all_target_list[_all_target_list['target'] == target]['uy'], 2), returned=True)

		return value, 1/np.sqrt(sumofweights)

	_all_target_list = pd.DataFrame([[ub.target, ub.y, ub.uy] for ub in budget_list], columns=['target','y','uy'])

	_targets = set(_all_target_list['target'].unique())
	updated_composition = {}

	for target in _targets:
		value, uncertainty = weighed_average(_all_target_list, target)
		
		updated_composition[target] = (value, uncertainty)

	updated_composition = {**original_composition, **updated_composition}

	return updated_composition


class Button(tkinter.Button):
    """Modified version of a tkinter Button allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Button.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())

class Label(tkinter.Label):
    """Modified version of a tkinter Label allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Label.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())

class Entry(tkinter.Entry):
    """Modified version of a tkinter Entry allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Entry.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())


class OnOffButton(ttk.Frame):
    def __init__(self, master, default=1, hint='', hint_destination=None, hint_xoffset=0, onlabel='on', offlabel='off', **kwargs):
        ttk.Frame.__init__(self, master)
        self.variable = tkinter.IntVar(master)

        Label(self, text=onlabel, anchor=tkinter.E, width=3).pack(side=tkinter.LEFT)
        Ron = tkinter.Radiobutton(self, variable=self.variable, text='', value=1)
        Ron.pack(side=tkinter.LEFT)
        Roff = tkinter.Radiobutton(self, variable=self.variable, text='', value=0)
        Roff.pack(side=tkinter.LEFT)
        Label(self, text=offlabel, anchor=tkinter.W, width=3).pack(side=tkinter.LEFT)
        
        if default in (1, 0, True, False):
            self.variable.set(default)

    def get(self):
        return bool(self.variable.get())

    def set(self, value):
        self.variable.set(value)


class DateLabel(tkinter.Frame):
    def __init__(self, master, default_date=None, hint='', hint_xoffset=0, hint_destination=None):
        tkinter.Frame.__init__(self, master)
        if default_date is None:
            self.date = datetime.datetime.today()
        else:
            self.date = default_date
        self.secondary_window = None

        self.labeldate = Label(self, text=self.date.strftime("%d/%m/%Y %H:%M:%S"), width=20, hint=hint, hint_destination=hint_destination)
        self.labeldate.pack(side=tkinter.LEFT)
        logo_ok = tkinter.PhotoImage(data=PL_ggear)
        confirm_button = Button(self, image=logo_ok, hint='change date', hint_destination=hint_destination, command=lambda : self.change_date_module())
        confirm_button.pack(side=tkinter.LEFT, padx=5)
        confirm_button.image = logo_ok

    def get(self):
        return self.date

    def get_string(self, format="%d/%m/%Y %H:%M:%S"):
        return self.date.strftime(format)

    def set(self, newdate):
        if isinstance(newdate, datetime.datetime):
            self.date = newdate
            self.labeldate.configure(text=self.date.strftime("%d/%m/%Y %H:%M:%S"))

    def change_date_module(self):
        if self.secondary_window is not None:
            self.secondary_window.destroy()
        self.secondary_window = tkinter.Toplevel(self)
        self.secondary_window.overrideredirect(True)
        self.secondary_window.geometry(f'+{self.winfo_rootx()}+{self.winfo_rooty()}')

        dframe = tkinter.Frame(self.secondary_window, highlightbackground="black", highlightthickness=2)
        tkinter.Label(dframe, text='change date', width=12, anchor=tkinter.W).grid(row=0, column=0, columnspan=4, sticky=tkinter.W)

        tkinter.Label(dframe, text='date', width=6, anchor=tkinter.W).grid(row=2, column=0)
        tkinter.Label(dframe, text='dd').grid(row=1, column=1)
        tkinter.Label(dframe, text='mm').grid(row=1, column=2, padx=3)
        tkinter.Label(dframe, text='yyyy').grid(row=1, column=3)
        self.day = Combobox(dframe, width=3, values=tuple([f'{i:02d}' for i in range(1,32)]))
        self.day.grid(row=2, column=1)

        self.month = Combobox(dframe, width=3, values=tuple([f'{i:02d}' for i in range(1,13)]))
        self.month.grid(row=2, column=2)

        today_year = datetime.datetime.today().year
        self.year = Combobox(dframe, width=5, values=tuple([f'{i:04d}' for i in range(today_year - 1, today_year + 2)]))
        self.year.grid(row=2, column=3)

        tkinter.Frame(dframe).grid(row=3, column=0, pady=10)

        tkinter.Label(dframe, text='time', width=6, anchor=tkinter.W).grid(row=5, column=0)
        tkinter.Label(dframe, text='HH').grid(row=4, column=1)
        tkinter.Label(dframe, text='MM').grid(row=4, column=2)
        tkinter.Label(dframe, text='SS').grid(row=4, column=3, sticky=tkinter.W)

        self.hours = Combobox(dframe, width=3, values=tuple([f'{i:02d}' for i in range(24)]))
        self.hours.grid(row=5, column=1)

        self.minutes = Combobox(dframe, width=3, values=tuple([f'{i:02d}' for i in range(60)]))
        self.minutes.grid(row=5, column=2)

        self.seconds = Combobox(dframe, width=3, values=tuple([f'{i:02d}' for i in range(60)]))
        self.seconds.grid(row=5, column=3, sticky=tkinter.W)

        self.day.set(f'{self.date.day:02d}')
        self.month.set(f'{self.date.month:02d}')
        self.year.set(f'{self.date.year:04d}')
        self.hours.set(f'{self.date.hour:02d}')
        self.minutes.set(f'{self.date.minute:02d}')
        self.seconds.set(f'{self.date.second:02d}')

        logo_confirmdate = tkinter.PhotoImage(data=PL_check)
        BT_confirmEexit = Button(dframe, image=logo_confirmdate, command=lambda : self.change_date_and_exit())
        BT_confirmEexit.grid(row=0, column=4, rowspan=7, padx=6)
        logo_confirmdate.image = logo_confirmdate
        #hint_label = ######

        dframe.pack(padx=5, pady=5)

    def change_date_and_exit(self):
        valid_date = True
        try:
            day = int(self.day.get())
        except ValueError:
            valid_date = False
        try:
            month = int(self.month.get())
        except ValueError:
            valid_date = False
        try:
            year = int(self.year.get())
        except ValueError:
            valid_date = False
        try:
            hour = int(self.hours.get())
        except ValueError:
            valid_date = False
        try:
            minute = int(self.minutes.get())
        except ValueError:
            valid_date = False
        try:
            second = int(self.seconds.get())
        except ValueError:
            valid_date = False
        try:
            datetime.datetime(year, month, day, hour, minute, second)
        except (ValueError, NameError):
            valid_date = False
        if valid_date:
            self.date = datetime.datetime(year, month, day, hour, minute, second)
            self.labeldate.configure(text=self.date.strftime("%d/%m/%Y %H:%M:%S"))
            self.secondary_window.destroy()
            self.secondary_window = None


class ColorButton(tkinter.Frame):
    def __init__(self, master, default_color='#FFFFFF', mode='persistent', state='active', external_variable=None, size='medium', hint_destination=None):
        tkinter.Frame.__init__(self, master)
        self.color = default_color
        self.mode = mode
        if size == 'small':
            logo = PL_s_void
        else:
            logo = PL_m_void
        fimage = tkinter.PhotoImage(data=logo)
        self.button = Button(self, image=fimage, background=self.color, command=lambda : self.open_ColorPalette(external_variable))
        self.button.pack(anchor=tkinter.NW)
        self.button.image = fimage
        self.secondary_open = False
        self.state = state
        if state != 'active':
            self.button.configure(state='disabled')

        if hint_destination is not None:
            self.button.bind('<Enter>', lambda e='<Enter>' : self.hintcolor(hint_destination))
            self.button.bind('<Leave>', lambda e='<Leave>' : hint_destination.configure(text=''))

        self.color_matrix = [['#000000', '#3B3131', '#413839', '#4C4646', '#52595D', '#666362', '#726E6D', '#797979', '#848482', '#C0C0C0', '#CECECE', '#E5E4E2', '#838996', '#6D7B8D'], ['#646D7E', '#728FCE', '#36454F', '#123456', '#000080', '#15317E', '#0020C2', '#2916F5', '#1F45FC', '#1974D2', '#2B65EC', '#1589FF', '#4682B4', '#3090C7'], ['#95B9C7', '#56A5EC', '#3BB9FF', '#82CAFF', '#A0CFEC', '#ADDFFF', '#BDEDFF', '#ADD8E6', '#D5D6EA', '#EBF4FA', '#F0FFFF', '#9AFEFF', '#00FFFF', '#4EE2EC'], ['#AFEEEE', '#77BFC7', '#7BCCB5', '#7FFFD4', '#48D1CC', '#43C6DB', '#20B2AA', '#3B9C9C', '#045F5F', '#2C3539', '#5E7D7E', '#438D80', '#2E8B57', '#34A56F'], ['#3CB371', '#617C58', '#808000', '#667C26', '#347235', '#008000', '#254117', '#6AA121', '#12AD2B', '#6CBB3C', '#32CD32', '#54C571', '#89C35C', '#B0BF1A'], ['#A1C935', '#7FE817', '#16F529', '#00FF7F', '#00FF00', '#7FFF00', '#B1FB17', '#DAEE01', '#BCE954', '#6AFB92', '#B5EAAA', '#DBF9DB', '#FFFACD', '#FAFAD2'], ['#FFF8DC', '#FAEBD7', '#FFE4C4', '#FFE5B4', '#FFDEAD', '#F0E2B6', '#ECE5B6', '#EDDA74', '#FFF380', '#FFFF00', '#FFDB58', '#FFD801', '#EAC117', '#FBB917'], ['#FFA62F', '#F4A460', '#E6BF83', '#C8AD7F', '#C8B560', '#BAB86C', '#D4AF37', '#DAA520', '#B8860B', '#CD7F32', '#966F33', '#8E7618', '#AF9B60', '#483C32'], ['#3D3635', '#49413F', '#704214', '#7F5217', '#8B4513', '#7E3517', '#C04000', '#B5651D', '#C47451', '#E56717', '#FF5F1F', '#FF8C00', '#E67451', '#F88158'], ['#E9967A', '#FA8072', '#E77471', '#CD5C5C', '#FF4500', '#FF2400', '#F62817', '#DC381F', '#B22222', '#A70D2A', '#990012', '#8C001A', '#551606', '#2B1B17'], ['#7D0541', '#7E354D', '#7F5A58', '#BC8F8F', '#C48793', '#ECC5C0', '#EDC9AF', '#FFE6E8', '#FFCCCB', '#FFC0CB', '#FAAFBA', '#E7A1B0', '#F778A1', '#D16587'], ['#E75480', '#FC6C85', '#FF1493', '#E45E9D', '#E30B5D', '#C21E56', '#CA226B', '#B3446C', '#DF73D4', '#FF00FF', '#C45AEC', '#B048B5', '#7E587E', '#5E5A80'], ['#6960EC', '#7575CF', '#5453A6', '#571B7E', '#461B7E', '#663399', '#800080', '#9400D3', '#B041FF', '#7A5DC7', '#8E35EF', '#9370DB', '#9E7BFF', '#E0B0FF'], ['#C38EC7', '#E6A9EC', '#C6AEC7', '#E9CFEC', '#E9E4D4', '#F8F0E3', '#FFF9E3', '#FFF5EE', '#FFFFF0', '#FBFBF9', '#FFFFFF']]

        self.naming_matrix = {'#000000': 'Black (W3C)', '#3B3131': 'Oil', '#413839': 'Black Cat', '#4C4646': 'Black Cow', '#52595D': 'Iron Gray', '#666362': 'Ash Gray', '#726E6D': 'Smokey Gray', '#797979': 'Platinum Gray', '#848482': 'Battleship Gray', '#C0C0C0': 'Silver (W3C)', '#CECECE': 'Platinum Silver', '#E5E4E2': 'Platinum', '#838996': 'Roman Silver', '#6D7B8D': 'Rat Gray', '#646D7E': 'Mist Blue', '#728FCE': 'Light Purple Blue', '#36454F': 'Charcoal Blue', '#123456': 'Deep Sea Blue', '#000080': 'Navy (W3C)', '#15317E': 'Lapis Blue', '#0020C2': 'Cobalt Blue', '#2916F5': 'Canary Blue', '#1F45FC': 'Blue Orchid', '#1974D2': 'Bright Navy Blue', '#2B65EC': 'Ocean Blue', '#1589FF': 'Neon Blue', '#4682B4': 'SteelBlue (W3C)', '#3090C7': 'Blue Ivy', '#95B9C7': 'Baby Blue', '#56A5EC': 'Iceberg', '#3BB9FF': 'Midday Blue', '#82CAFF': 'Day Sky Blue', '#A0CFEC': 'Jeans Blue', '#ADDFFF': 'Light Day Blue', '#BDEDFF': 'Robin Egg Blue', '#ADD8E6': 'LightBlue (W3C)', '#D5D6EA': 'Pastel Light Blue', '#EBF4FA': 'Water', '#F0FFFF': 'Azure (W3C)', '#9AFEFF': 'Electric Blue', '#00FFFF': 'Aqua or Cyan (W3C)', '#4EE2EC': 'Blue Diamond', '#AFEEEE': 'PaleTurquoise (W3C)', '#77BFC7': 'Blue Hosta', '#7BCCB5': 'Blue Green', '#7FFFD4': 'Aquamarine (W3C)', '#48D1CC': 'MediumTurquoise (W3C)', '#43C6DB': 'Blue Turquoise', '#20B2AA': 'LightSeaGreen (W3C)', '#3B9C9C': 'Deep Sea', '#045F5F': 'Medium Teal', '#2C3539': 'Gunmetal', '#5E7D7E': 'Grayish Turquoise', '#438D80': 'Sea Turtle Green', '#2E8B57': 'SeaGreen (W3C)', '#34A56F': 'Earth Green', '#3CB371': 'MediumSeaGreen (W3C)', '#617C58': 'Hazel Green', '#808000': 'Olive (W3C)', '#667C26': 'Fern Green', '#347235': 'Medium Forest Green', '#008000': 'Green (W3C)', '#254117': 'Dark Forest Green', '#6AA121': 'Green Onion', '#12AD2B': 'Parrot Green', '#6CBB3C': 'Green Snake', '#32CD32': 'LimeGreen (W3C)', '#54C571': 'Zombie Green', '#89C35C': 'Green Peas', '#B0BF1A': 'Acid Green', '#A1C935': 'Salad Green', '#7FE817': 'Hummingbird Green', '#16F529': 'Neon Green', '#00FF7F': 'SpringGreen (W3C)', '#00FF00': 'Lime (W3C)', '#7FFF00': 'Chartreuse (W3C)', '#B1FB17': 'Dull Green Yellow', '#DAEE01': 'Neon Yellow Green', '#BCE954': 'Slime Green', '#6AFB92': 'Dragon Green', '#B5EAAA': 'Green Thumb', '#DBF9DB': 'Light Rose Green', '#FFFACD': 'LemonChiffon (W3C)', '#FAFAD2': 'LightGoldenRodYellow (W3C)', '#FFF8DC': 'Cornsilk (W3C)', '#FAEBD7': 'AntiqueWhite (W3C)', '#FFE4C4': 'Bisque (W3C)', '#FFE5B4': 'Peach', '#FFDEAD': 'NavajoWhite (W3C)', '#F0E2B6': 'Dark Blonde', '#ECE5B6': 'Tan Brown', '#EDDA74': 'Cardboard Brown', '#FFF380': 'Corn Yellow', '#FFFF00': 'Yellow (W3C)', '#FFDB58': 'Mustard Yellow', '#FFD801': 'Rubber Ducky Yellow', '#EAC117': 'Golden Brown', '#FBB917': 'Saffron', '#FFA62F': 'Cantaloupe', '#F4A460': 'SandyBrown (W3C)', '#E6BF83': 'Deer Brown', '#C8AD7F': 'Light French Beige', '#C8B560': 'Fall Leaf Brown', '#BAB86C': 'Olive Green', '#D4AF37': 'Metallic Gold', '#DAA520': 'GoldenRod (W3C)', '#B8860B': 'DarkGoldenRod (W3C)', '#CD7F32': 'Bronze', '#966F33': 'Wood', '#8E7618': 'Hazel', '#AF9B60': 'Bullet Shell', '#483C32': 'Taupe', '#3D3635': 'Gray Brown', '#49413F': 'Western Charcoal', '#704214': 'Sepia Brown', '#7F5217': 'Red Dirt', '#8B4513': 'SaddleBrown (W3C)', '#7E3517': 'Blood Red', '#C04000': 'Mahogany', '#B5651D': 'Light Brown', '#C47451': 'Orange Salmon', '#E56717': 'Papaya Orange', '#FF5F1F': 'Bright Orange', '#FF8C00': 'DarkOrange (W3C)', '#E67451': 'Sunrise Orange', '#F88158': 'Basket Ball Orange', '#E9967A': 'DarkSalmon (W3C)', '#FA8072': 'Salmon (W3C)', '#E77471': 'Pink Coral', '#CD5C5C': 'IndianRed (W3C)', '#FF4500': 'OrangeRed (W3C)', '#FF2400': 'Scarlet', '#F62817': 'Fire Engine Red', '#DC381F': 'Grapefruit', '#B22222': 'FireBrick (W3C)', '#A70D2A': 'Carbon Red', '#990012': 'Red Wine or Wine Red', '#8C001A': 'Burgundy', '#551606': 'Blood Night', '#2B1B17': 'Midnight', '#7D0541': 'Plum Pie', '#7E354D': 'Velvet Maroon', '#7F5A58': 'Puce', '#BC8F8F': 'RosyBrown (W3C)', '#C48793': 'Lipstick Pink', '#ECC5C0': 'Rose Gold', '#EDC9AF': 'Desert Sand', '#FFE6E8': 'Blush', '#FFCCCB': 'Light Red', '#FFC0CB': 'Pink (W3C)', '#FAAFBA': 'Baby Pink', '#E7A1B0': 'Pink Rose', '#F778A1': 'Carnation Pink', '#D16587': 'Purple Pink', '#E75480': 'Dark Pink', '#FC6C85': 'Watermelon Pink', '#FF1493': 'DeepPink (W3C)', '#E45E9D': 'Pink Cupcake', '#E30B5D': 'Raspberry', '#C21E56': 'Rose Red', '#CA226B': 'Pink Violet', '#B3446C': 'Raspberry Purple', '#DF73D4': 'Deep Mauve', '#FF00FF': 'Fuchsia or Magenta (W3C)', '#C45AEC': 'Tyrian Purple', '#B048B5': 'Orchid Purple', '#7E587E': 'Viola Purple', '#5E5A80': 'Grape', '#6960EC': 'Blue Lotus', '#7575CF': 'Periwinkle Purple', '#5453A6': 'Deep Periwinkle', '#571B7E': 'Purple Iris', '#461B7E': 'Purple Monster', '#663399': 'RebeccaPurple (W3C)', '#800080': 'Purple (W3C)', '#9400D3': 'DarkViolet (W3C)', '#B041FF': 'Purple Daffodil', '#7A5DC7': 'Purple Sage Bush', '#8E35EF': 'Purple Plum', '#9370DB': 'MediumPurple (W3C)', '#9E7BFF': 'Purple Mimosa', '#E0B0FF': 'Mauve', '#C38EC7': 'Purple Dragon', '#E6A9EC': 'Blush Pink', '#C6AEC7': 'Wisteria Purple', '#E9CFEC': 'Periwinkle Pink', '#E9E4D4': 'Ash White', '#F8F0E3': 'Off White', '#FFF9E3': 'Egg Shell', '#FFF5EE': 'SeaShell (W3C)', '#FFFFF0': 'Ivory (W3C)', '#FBFBF9': 'Cotton', '#FFFFFF': 'White (W3C)'}

    def hintcolor(self, hintlabel):
        hintlabel.configure(text=self.naming_matrix.get(self.color, self.color))

    def cstate(self):
        if self.state != 'active':
            self.active()
        else:
            self.deactive()
    
    def active(self):
        self.state = 'active'
        self.button.configure(state='active')

    def deactive(self):
        self.state = 'disabled'
        self.button.configure(state='disabled')

    def open_ColorPalette(self, external_variable):
        if self.secondary_open == False:
            TP = tkinter.Toplevel(self)
            TP.title(f'Current value: {self.naming_matrix.get(self.color, self.color)}')
            TP.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(TP))
            TP.resizable(False, False)
            self.secondary_open = True

            if len(self.color_matrix[0]) < 16:
                data = PL_m_void
            else:
                data = PL_s_void
            
            fimage = tkinter.PhotoImage(data=data)
            nameline = tkinter.Label(TP, text='', anchor=tkinter.W)
            CP = tkinter.Frame(TP)
            for i,line in enumerate(self.color_matrix):
                for j, name in enumerate(line):
                    BGKL = tkinter.Button(CP, image=fimage, text='', background=name, command=lambda color=name : self.trigger(color, TP, external_variable))
                    BGKL.grid(row=i, column=j)
                    BGKL.image = fimage
                    BGKL.bind('<Enter>', lambda e='<Enter>', color=name : self.hover(color, nameline))
                    BGKL.bind('<Leave>', lambda e='<Leave>' : self.leavemealone(nameline))

            CP.pack(anchor=tkinter.NW)
            nameline.pack(anchor=tkinter.NW)

    def trigger(self, color, TP, external_variable):
        self.color = color
        if external_variable is not None:
            external_variable.set(color)
        self.button.configure(background=self.color)
        TP.title(f'Current value: {self.naming_matrix.get(self.color, self.color)}')
        if self.mode == 'click':
            TP.destroy()
            self.secondary_open = False

    def hover(self, color, nameline):
        nameline.configure(text=self.naming_matrix.get(color, color))

    def leavemealone(self, nameline):
        nameline.configure(text='')
    
    def on_closing(self, TP):
        TP.destroy()
        self.secondary_open = False

    def get(self):
        return self.color


class Spinbox(tkinter.Spinbox):
    """Modified version of a tkinter Spinbox allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Spinbox.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())


class Checkbutton(tkinter.Checkbutton):
    """Modified version of a tkinter Checkbutton allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Checkbutton.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())


class HelpedCombobox(tkinter.Frame):
    """Modified version of a tkinter ttk.Combobox allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, data=(), hint='', hint_xoffset=0, hint_destination=None, allow_new_input=False, default_invalid='', **kw):
        tkinter.Frame.__init__(self, master)#, **kw)
        settings = {**kw, 'state':tkinter.NORMAL}
        self.data = data
        self.new_input = allow_new_input
        self.default_invalid = default_invalid
        self.Combobox = ttk.Combobox(self, values=data, **settings)
        self.Combobox.pack()
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

        self.Combobox.bind('<Return>', lambda e='<Return>' : self.trim_selection())

    def _showhint(self):
        if self.Combobox.get() == '':
            showentry = self.hint
        else:
            showentry = self.Combobox.get()

        if self.hint_destination is not None:
            self.hint_destination.configure(text=showentry)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=showentry).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())

    def trim_selection(self):
        trimmed_data = [item for item in self.data if self.Combobox.get() in item]
        self.Combobox['values'] = trimmed_data

    def _update(self, data=()):
        self.data = data
        self.Combobox['values'] = self.data
        self.Combobox.set('')

    def get(self):
        get_value = self.Combobox.get()
        if self.new_input:
            return get_value
        else:
            if get_value in self.data:
                return get_value
            return self.default_invalid

    def set(self, name):
        if self.new_input:
            self.Combobox.set(name)
        else:
            if name in self.data:
                self.Combobox.set(name)
            else:
                self.Combobox.set(self.default_invalid)


class Combobox(ttk.Combobox):
    """Modified version of a tkinter ttk.Combobox allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        ttk.Combobox.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if ttk.Combobox.get(self) == '':
            showentry = self.hint
        else:
            showentry = ttk.Combobox.get(self)

        if self.hint_destination is not None:
            self.hint_destination.configure(text=showentry)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=showentry).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())


class Slider(tkinter.Frame):
    def __init__(self, master, percent=False, label_width=4, anchor_text=tkinter.CENTER, default=0, hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.IntVar(master)
        self.percent = percent
        if self.percent == True:
            self.text = f'{self.variable.get():d} %'
        else:
            self.text = f'{self.variable.get():d}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        self.from_ = kwargs.get('from_',1)
        self.to = kwargs.get('to',10)
        self.resolution = kwargs.get('resolution',1)
        self.anchor = anchor_text
        self.Label = Label(self, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, resolution=self.resolution, showvalue=False, variable=self.variable)
        self.Scale.pack(side=tkinter.RIGHT)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()

        self.variable.trace('w', lambda a,b,c : self._update())

    def _update(self):
        if self.percent == True:
            self.text = f'{self.variable.get():d} %'
        else:
            self.text = f'{self.variable.get():d}'
        self.Label.configure(text=self.text)

    def get(self):
        return self.variable.get()


class TSlider(tkinter.Frame):
    def __init__(self, master, label_width=4, anchor_text=tkinter.CENTER, default=0, hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.BooleanVar(master)
        self.text = f'{self.variable.get()}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        self.resolution = kwargs.get('resolution',1)
        self.anchor = anchor_text
        self.Label = Label(self, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=0, to=1, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, resolution=self.resolution, showvalue=False, variable=self.variable)
        self.Scale.pack(side=tkinter.RIGHT)

        if 0 <= default <= 1:
            self.variable.set(default)
        else:
            self.variable.set(True)
        self._update()

        self.variable.trace('w', lambda a,b,c : self._update())

    def _update(self):
        self.text = f'{self.variable.get()}'
        self.Label.configure(text=self.text)

    def get(self,asint=True):
        if asint == False:
            return self.variable.get()
        else:
            return int(self.variable.get())


class FSlider(tkinter.Frame):
    def __init__(self, master, percent=False, decimals=2, label_width=4, anchor_text=tkinter.CENTER, default=0, hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.DoubleVar(master)
        self.decimals = decimals
        fmt = f'.{self.decimals}f'
        self.percent = percent
        if self.percent == True:
            self.text = f'{format(self.variable.get(),fmt)} %'
        else:
            self.text = f'{format(self.variable.get(),fmt)}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        self.from_ = kwargs.get('from_',1)
        self.to = kwargs.get('to',10)
        self.resolution = kwargs.get('resolution',0.1)
        self.anchor = anchor_text
        self.Label = Label(self, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, resolution=self.resolution, showvalue=False, variable=self.variable)
        self.Scale.pack(side=tkinter.RIGHT, fill=tkinter.X, expand=True)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()

        self.variable.trace('w', lambda a,b,c : self._update())

    def _update(self):
        fmt = f'.{self.decimals}f'
        if self.percent == True:
            self.text = f'{format(self.variable.get(),fmt)} %'
        else:
            self.text = f'{format(self.variable.get(),fmt)}'
        self.Label.configure(text=self.text)

    def get(self):
        return self.variable.get()


class MutableVFSlider(tkinter.Frame):
    def __init__(self, master, percent=False, decimals=2, limit=5.0, label_width=4, anchor_text=tkinter.CENTER, default=0, hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.DoubleVar(master)
        self.decimals = decimals
        fmt = f'.{self.decimals}f'
        self.percent = percent
        self.limit = limit
        if self.percent == True:
            self.text = f'{format(self.variable.get(),fmt)} %'
        else:
            self.text = f'{format(self.variable.get(),fmt)}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        self.from_ = kwargs.get('from_',-self.limit)
        self.to = kwargs.get('to',self.limit)
        self.resolution = kwargs.get('resolution',0.01)
        self.anchor = anchor_text
        gauge_frame = tkinter.Frame(self)
        self.Label = Label(gauge_frame, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(gauge_frame, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, resolution=self.resolution, showvalue=False, variable=self.variable)
        self.Scale.pack(side=tkinter.RIGHT, fill=tkinter.Y, expand=True)
        gauge_frame.pack(side=tkinter.LEFT, anchor=tkinter.NW)
        control_frame = tkinter.Frame(self)

        tkinter.Label(control_frame, text='limit', width=10, anchor=tkinter.E).grid(row=0, column=0, sticky=tkinter.E, padx=3)
        
        self.limit_CB = ttk.Combobox(control_frame, state='readonly', width=5)
        self.limit_CB['values'] = [1.0, 5.0, 10.0, 20.0]
        self.limit_CB.grid(row=0, column=1, padx=5)
        self.limit_CB.set(self.limit)

        control_frame.pack(side=tkinter.LEFT, anchor=tkinter.NW)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()

        self.variable.trace('w', lambda a,b,c : self._update())
        self.limit_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.change_limits())

    def change_limits(self):
        self.limit = float(self.limit_CB.get())
        self.from_ = -1 * self.limit
        self.to = 1 * self.limit
        self.Scale.configure(from_=self.from_, to=self.to)

        if self.from_ <= self.variable.get() <= self.to:
            pass
        else:
            self.variable.set(0.0)
        self._update()

    def _update(self):
        fmt = f'.{self.decimals}f'
        if self.percent == True:
            self.text = f'{format(self.variable.get(),fmt)} %'
        else:
            self.text = f'{format(self.variable.get(),fmt)}'
        self.Label.configure(text=self.text)

    def get(self):
        return self.variable.get()


class FDiscreteSlider(tkinter.Frame):
    def __init__(self, master, decimals=1, label_width=8, anchor_text=tkinter.CENTER, default=0, values=[], hint='', hint_destination=None, hint_xoffset=0, unit_format=' mm', **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.DoubleVar(master)
        self.decimals = decimals
        fmt = f'.{self.decimals}f'
        self.unit_format = unit_format
        self.text = f'{format(self.variable.get(),fmt)}{self.unit_format}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        if values == []:
            values = [default]
        else:
            values = sorted(set(values))
        self.values = values
        self.from_ = min(values)# kwargs.get('from_',1)
        self.to = max(values)#kwargs.get('to',10)
        self.resolution = kwargs.get('resolution',0.1)
        self.anchor = anchor_text
        self.Label = Label(self, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, showvalue=False, variable=self.variable, resolution=self.resolution)
        self.Scale.configure(command=lambda e=None: self.change_value())
        self.Scale.pack(side=tkinter.RIGHT, fill=tkinter.X, expand=True)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()

        self.variable.trace_add('write', lambda a,b,c : self._update())

    def change_value(self):
        newvalue = min(self.values, key=lambda x:abs(x-float(self.Scale.get())))
        self.variable.set(newvalue)

    def set_value(self, newvalue):
        if newvalue in self.values:
            self.variable.set(newvalue)
        #newvalue = min(self.values, key=lambda x:abs(x-float(self.Scale.get())))
        else:
            self.variable.set(0.0)

    def _update(self):
        fmt = f'.{self.decimals}f'
        self.text = f'{format(self.variable.get(),fmt)}{self.unit_format}'
        self.Label.configure(text=self.text)

    def get(self):
        newvalue = min(self.values, key=lambda x:abs(x-float(self.Scale.get())))
        return newvalue

    def set_values(self, values, default=0):
        if values == []:
            values = [default]
        else:
            values = sorted(set(values))
        self.values = values
        self.from_ = min(values)# kwargs.get('from_',1)
        self.to = max(values)#kwargs.get('to',10)
        self.Scale.configure(from_=self.from_, to=self.to)
        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()


class IZoomSlider(tkinter.Frame):
    def __init__(self, master, default=0, values=[], hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.IntVar(master)
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        if values == []:
            values = [default]
        else:
            values = sorted(set(values))
        self.values = values
        self.from_ = min(values)
        self.to = max(values)
        self.resolution = kwargs.get('resolution',1)
        Label(self, text='zoom\n+').pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, showvalue=False, variable=self.variable)
        self.Scale.configure(command=lambda e=None: self.change_value())
        self.Scale.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)
        Label(self, text='zoom\n-').pack(side=tkinter.LEFT)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)

    def change_value(self):
        newvalue = min(self.values, key=lambda x:abs(x-int(self.Scale.get())))
        self.variable.set(newvalue)

    def get(self):
        newvalue = min(self.values, key=lambda x:abs(x-int(self.Scale.get())))
        return newvalue


class LockedNumEntry(Entry):
    def __init__(self, master, default_value='', hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        self.variable = tkinter.StringVar(master)
        self.variable.set(default_value)
        self.subvariable = tkinter.StringVar(master)
        self.subwindow = None
        self.hint_destination = hint_destination
        self.check_not_null = True
        Entry.__init__(self, master, textvariable=self.variable, state='readonly', hint=hint, hint_destination=self.hint_destination, hint_xoffset=hint_xoffset, **kwargs)

    def change_value(self):
        x, y, width, height = self.winfo_rootx(), self.winfo_rooty(), self.winfo_width(), self.winfo_height()
        if self.subwindow is not None:
            self.subwindow.destroy()
        else:
            self.subvariable.set(self.variable.get())
        if self.subvariable.get() == '':
            self.subvariable.set(self.variable.get())
        self.subwindow = tkinter.Toplevel(self)
        self.subwindow.overrideredirect(True)
        self.subwindow.resizable(False, False)
        self.subwindow.geometry(f'{width}x{height}+{x}+{y+height}')
        entry = tkinter.Entry(self.subwindow, textvariable=self.subvariable)
        entry.pack(anchor=tkinter.W, fill=tkinter.BOTH, expand=True)
        entry.icursor(len(self.subvariable.get()))
        entry.focus_set()

        entry.bind('<Return>', lambda event : self.command_return())
        entry.bind('<Escape>', lambda event: self.command_esc())
        entry.bind('<Delete>', lambda event: self.command_canc())
        entry.bind('<FocusOut>', lambda event: self.command_esc())

    def check_function(self, string):
        response = True
        if self.check_not_null:
            try:
                float(string)
            except ValueError:
                response = False
        return response

    def command_return(self):
        messagetext='invalid string'
        new_string = self.subvariable.get()
        if self.check_function(new_string):
            self.variable.set(new_string)
            self.subvariable.set('')
            self.subwindow.destroy()
            self.subwindow = None
            messagetext='field updated'
        if self.hint_destination is not None:
            self.hint_destination.configure(text=messagetext)

    def command_esc(self):
        self.subwindow.destroy()

    def command_canc(self):
        self.subvariable.set('')


class LockedEntry(Entry):
    def __init__(self, master, default_value='', hint='', hint_destination=None, hint_xoffset=0, check_not_null=True, **kwargs):
        self.variable = tkinter.StringVar(master)
        self.variable.set(default_value)
        self.subvariable = tkinter.StringVar(master)
        self.subwindow = None
        self.hint_destination = hint_destination
        self.check_not_null = check_not_null
        Entry.__init__(self, master, textvariable=self.variable, state='readonly', hint=hint, hint_destination=self.hint_destination, hint_xoffset=hint_xoffset, **kwargs)

    def change_value(self):
        x, y, width, height = self.winfo_rootx(), self.winfo_rooty(), self.winfo_width(), self.winfo_height()
        if self.subwindow is not None:
            self.subwindow.destroy()
        else:
            self.subvariable.set(self.variable.get())
        if self.subvariable.get() == '':
            self.subvariable.set(self.variable.get())
        self.subwindow = tkinter.Toplevel(self)
        self.subwindow.overrideredirect(True)
        self.subwindow.resizable(False, False)
        self.subwindow.geometry(f'{width}x{height}+{x}+{y+height}')
        entry = tkinter.Entry(self.subwindow, textvariable=self.subvariable)
        entry.pack(anchor=tkinter.W, fill=tkinter.BOTH, expand=True)
        entry.icursor(len(self.subvariable.get()))
        entry.focus_set()

        entry.bind('<Return>', lambda event : self.command_return())
        entry.bind('<Escape>', lambda event: self.command_esc())
        entry.bind('<Delete>', lambda event: self.command_canc())
        entry.bind('<FocusOut>', lambda event: self.command_esc())

    def check_function(self, string):
        response = True
        if self.check_not_null:
            chars = set("""*"?\/|[]{}""")
            if string.replace(' ','') == '' or any((c in chars) for c in string):
                response = False
        return response

    def command_return(self):
        messagetext='invalid string'
        new_string = self.subvariable.get()
        if self.check_function(new_string):
            self.variable.set(new_string)
            self.subvariable.set('')
            self.subwindow.destroy()
            self.subwindow = None
            messagetext='field updated'
        if self.hint_destination is not None:
            self.hint_destination.configure(text=messagetext)

    def command_esc(self):
        self.subwindow.destroy()

    def command_canc(self):
        self.subvariable.set('')


class CountingDistanceLabel(tkinter.Frame):
    """A simple yet effective distance-changing mechanism"""
    def __init__(self, master, width=25, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.positions = ()
        self.distance = None
        self.dd = 0.0
        self.udd = 0.0
        self.label_position = tkinter.Label(self, text='', width=width)
        tkinter.Label(self, text='nominal position + δd / mm', width=width).grid(row=0, column=0)
        self.label_position.grid(row=1, column=0)

    def get(self):
        return self.distance, self.dd, self.udd

    def print_label(self):
        if self.distance is None:
            text = '#'
        elif self.dd >= 0.0:
            text = f'{self.distance:.1f} + {self.dd:.1f}'
        else:
            text = f'{self.distance:.1f} - {np.abs(self.dd):.1f}'
        self.label_position.configure(text=text)

    def set(self, spectrum):
        self.distance = None
        self.dd = 0.0
        self.udd = 0.0
        if spectrum is not None:
            self.distance = spectrum.counting_position
            self.dd = spectrum.positioning_variability
            self.udd = spectrum.uncertainty_positioning_variability
        self.print_label()


class ScrollableListbox(tkinter.Frame):
    """A simple yet effective scrollable listbox"""
    def __init__(self, master, width=10, height=8, data=[], **kwargs):
        tkinter.Frame.__init__(self, master)
        self.listbox = tkinter.Listbox(self, width=width, height=height, **kwargs)
        self.scrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=tkinter.LEFT, anchor=tkinter.NW, fill=tkinter.BOTH, expand=True)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._update(data)

    def _update(self, data=[]):
        self.listbox.delete(0,tkinter.END)
        for item in data:
            self.listbox.insert(tkinter.END, item)

    def _colored_update(self, condition=[], true_color='#FFFFFF', false_color='gray'):
        for nnn, cond in enumerate(condition):
            try:
                color = false_color
                if cond:
                    color = true_color
            except (IndexError, ValueError):
                color = false_color
            self.listbox.itemconfig(nnn, {'bg':color})

    def curselection(self):
        return self.listbox.curselection()

    def get_selection(self, single=True):
        values = [self.listbox.get(idx) for idx in self.listbox.curselection()]
        if single:
            try:
                return values[0]
            except IndexError:
                return None
        return values


class EpithermalSelfShieldingPeriodicTable(tkinter.Frame):
    """A periodic table to display the elemental contribution to matrix epithermal self-shielding effect"""
    def __init__(self, master, results, resolution=10, max_windows_open_at_a_time=10, default_palette='YlOrRd'):
        tkinter.Frame.__init__(self, master)
        self.periodic_data = periodic_data
        self.results = results
        self.elements = []
        self.color_gradient = []
        self.secondary_windows = []
        self.max_windows_open_at_a_time = max_windows_open_at_a_time
        HeaderLine = tkinter.Frame(self)
        PTTable = tkinter.Frame(self)
        
        tkinter.Label(HeaderLine, text='', width=6, anchor=tkinter.W).pack(side=tkinter.LEFT, anchor=tkinter.NW)
        tkinter.Label(HeaderLine, text=f'', width=8, anchor=tkinter.W).pack(side=tkinter.LEFT, anchor=tkinter.NW)
        tkinter.Frame(HeaderLine).pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=15)
        
        self.label_min = tkinter.Label(HeaderLine, text='', width=4)
        self.label_min.pack(side=tkinter.LEFT, padx=5)
        for i in range(resolution):
            gradient_label = tkinter.Label(HeaderLine, text='', width=1)
            gradient_label.pack(side=tkinter.LEFT, anchor=tkinter.NW)
            self.color_gradient.append(gradient_label)
        self.label_max = tkinter.Label(HeaderLine, text='', width=4)
        self.label_max.pack(side=tkinter.LEFT, padx=5)
        
        tkinter.Label(HeaderLine, text='palette').pack(side=tkinter.LEFT, padx=3)
        self.CB_palette_selector = ttk.Combobox(HeaderLine, width=15, state='readonly')
        self.CB_palette_selector.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5)
        self.CB_palette_selector['values'] = ('Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'viridis', 'plasma', 'cividis', 'tab20b')
        if default_palette in self.CB_palette_selector['values']:
            self.CB_palette_selector.set(default_palette)
        else:
            self.CB_palette_selector.set('YlOrRd')

        tkinter.Frame(PTTable).grid(row=7, column=0, pady=4)
        element_indicator = tkinter.Label(PTTable, text='', anchor=tkinter.W)
        element_indicator.grid(row=10, column=0, pady=3, columnspan=10, sticky=tkinter.W)
        self.default_color = element_indicator.cget('bg')
        for element in self.periodic_data:
            line = f'{element[4]}'
            CB = Button(PTTable, text=element[1], state=tkinter.DISABLED, width=3, bg=self.default_color, anchor=tkinter.W, relief='solid', hint=line, hint_destination=element_indicator)
            CB.grid(row=element[2], column=element[3], ipadx=2, ipady=2, sticky=tkinter.W)
            CB.configure(command= lambda el=element[1]: self._set_commando(el))
            self.elements.append(CB)
        
        HeaderLine.pack(anchor=tkinter.NW, pady=5)    
        PTTable.pack(anchor=tkinter.NW)

        self.by_episelfshielding_correction()
        
        self.CB_palette_selector.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.by_episelfshielding_correction())

    def get_min(self, vdict):
        if len(vdict) == 0:
            return 0.0
        return 1.0
    
    def sweep(self):
        return [window for window in self.secondary_windows if window is not None]
        
    def _get_title(self, window):
        try:
            return window.title()
        except Exception:
            return None

    def by_episelfshielding_correction(self):
        n_unceraintybudget = [self.get_min(self.results.get(item[1], {})) for item in self.periodic_data]
        cmap = cm.get_cmap(self.CB_palette_selector.get())
        nmin, nmax = 0.0, 1.0
        colors = cmap(np.array([(i-nmin)/(nmax-nmin) for i in n_unceraintybudget]))
        gradient = cmap(np.linspace(0, 1, len(self.color_gradient)))
        
        for card, color, nn in zip(self.elements, colors, n_unceraintybudget):
            card.configure(background=mcolors.to_hex(color[:3]))
            if nn == 0:
                card.configure(state=tkinter.DISABLED)
            else:
                card.configure(state=tkinter.NORMAL)
        for grad, gcard in zip(gradient, self.color_gradient):
            gcard.configure(background=mcolors.to_hex(grad[:3]))
        self.label_min.configure(text=f'{nmin:.0f}')
        self.label_max.configure(text=f'{nmax:.0f}')

    def _set_commando(self, element):
        self.secondary_windows = self.sweep()
        titles = [self._get_title(window) for window in self.secondary_windows]

        title = f'Element: {element}'

        if title in titles:
            self.secondary_windows[titles.index(title)].deiconify()
            self.secondary_windows[titles.index(title)].focus()
        else:
            EL = tkinter.Toplevel(self)
            EL.title(title)
            EL.resizable(False, False)
            self.secondary_windows.append(EL)
            if len(self.secondary_windows) > self.max_windows_open_at_a_time:
                self.secondary_windows[0].destroy()
                self.secondary_windows[0] = None
                self.secondary_windows = self.sweep()

            lines = self.results[element]
            episs_data = tkinter.LabelFrame(EL, labelwidget=tkinter.Label(EL, text='Gepi correction'), relief='solid', bd=2, padx=4, pady=4)
            
            tkinter.Label(episs_data, text='isotope', width=10).grid(row=0, column=0)
            tkinter.Label(episs_data, text='Gepi', width=10).grid(row=0, column=1)
            tkinter.Label(episs_data, text='u(Gepi)', width=10).grid(row=0, column=2)
            
            nn = 1
            for line in sorted(lines.keys()):
                tkinter.Label(episs_data, text=line, width=10).grid(row=nn, column=0)
                tkinter.Label(episs_data, text=f'{lines[line][0]:.3f}', width=10).grid(row=nn, column=1)
                tkinter.Label(episs_data, text=f'{lines[line][1]:.3f}', width=10).grid(row=nn, column=2)
                nn += 1
            
            episs_data.pack(anchor=tkinter.NW, padx=5, pady=5)


class SelfShieldingPeriodicTable(tkinter.Frame):
    """A periodic table to display the elemental contribution to matrix thermal self-shielding effect"""
    def __init__(self, master, results, resolution=10, Gth=1.0, default_palette='YlOrRd'):
        tkinter.Frame.__init__(self, master)
        self.periodic_data = periodic_data
        self.results = results
        self.elements = []
        self.color_gradient = []
        HeaderLine = tkinter.Frame(self)
        PTTable = tkinter.Frame(self)
        
        tkinter.Label(HeaderLine, text='Gth = ', width=6, anchor=tkinter.W).pack(side=tkinter.LEFT, anchor=tkinter.NW)
        tkinter.Label(HeaderLine, text=f'{Gth:.4f}', width=8, anchor=tkinter.W).pack(side=tkinter.LEFT, anchor=tkinter.NW)
        tkinter.Frame(HeaderLine).pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=15)
        
        self.label_min = tkinter.Label(HeaderLine, text='', width=4)
        self.label_min.pack(side=tkinter.LEFT, padx=5)
        for i in range(resolution):
            gradient_label = tkinter.Label(HeaderLine, text='', width=1)
            gradient_label.pack(side=tkinter.LEFT, anchor=tkinter.NW)
            self.color_gradient.append(gradient_label)
        self.label_max = tkinter.Label(HeaderLine, text='', width=4)
        self.label_max.pack(side=tkinter.LEFT, padx=5)
        
        tkinter.Label(HeaderLine, text='palette').pack(side=tkinter.LEFT, padx=3)
        self.CB_palette_selector = ttk.Combobox(HeaderLine, width=15, state='readonly')
        self.CB_palette_selector.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5)
        self.CB_palette_selector['values'] = ('Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'viridis', 'plasma', 'cividis', 'tab20b')
        if default_palette in self.CB_palette_selector['values']:
            self.CB_palette_selector.set(default_palette)
        else:
            self.CB_palette_selector.set('YlOrRd')

        tkinter.Frame(PTTable).grid(row=7, column=0, pady=4)
        element_indicator = tkinter.Label(PTTable, text='', anchor=tkinter.W)
        element_indicator.grid(row=10, column=0, pady=3, columnspan=10, sticky=tkinter.W)
        self.default_color = element_indicator.cget('bg')
        for element in self.periodic_data:
            if element[1] in self.results.keys():
                line = f'{element[4]} accounts for {100*self.results[element[1]]:.1f} % of z value'
            else:
                line = f'{element[4]} not present in matrix'
            CB = Button(PTTable, text=element[1], state=tkinter.DISABLED, width=3, bg=self.default_color, anchor=tkinter.W, relief='solid', hint=line, hint_destination=element_indicator)
            CB.grid(row=element[2], column=element[3], ipadx=2, ipady=2, sticky=tkinter.W)
            self.elements.append(CB)
        
        HeaderLine.pack(anchor=tkinter.NW, pady=5)    
        PTTable.pack(anchor=tkinter.NW)

        self.by_contribution_to_selfshielding()
        
        self.CB_palette_selector.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.by_contribution_to_selfshielding())

    def by_contribution_to_selfshielding(self):
        n_unceraintybudget = [self.results.get(item[1], 0)*100 for item in self.periodic_data]
        cmap = cm.get_cmap(self.CB_palette_selector.get())
        nmin, nmax = 0, 100
        colors = cmap(np.array([(i-nmin)/(nmax-nmin) for i in n_unceraintybudget]))
        gradient = cmap(np.linspace(0, 1, len(self.color_gradient)))
        
        for card, color, nn in zip(self.elements, colors, n_unceraintybudget):
            card.configure(background=mcolors.to_hex(color[:3]))
            if nn == 0:
                card.configure(state=tkinter.DISABLED)
            else:
                card.configure(state=tkinter.NORMAL)
        for grad, gcard in zip(gradient, self.color_gradient):
            gcard.configure(background=mcolors.to_hex(grad[:3]))
        self.label_min.configure(text=f'{nmin} %')
        self.label_max.configure(text=f'{nmax} %')


class Subwindow(tkinter.Toplevel):
    """A special Toplevel window to change colors of line in a ScrollableListbox"""
    def __init__(self, master, title='Title', true_color='#FFFFFF', false_color='#ff474c'):
        super().__init__(master)

        self.title(title)
        self.resizable(False, False)
        self._true_color, self._false_color = true_color, false_color
        #maybe here if needed!! subsubwindow count

    def _update(self, local_data):
        self.SBT._colored_update([datum.accepted_for_report for datum in local_data], self._true_color, self._false_color)


class PeriodicTable(tkinter.Frame):
    """A periodic table for displaying of results"""
    def __init__(self, master, results, visualization_type='sample', display_type='results', resolution=8, default_palette='YlOrRd', colors=('#c30a00', '#fcd664', '#000000'), max_windows_open_at_a_time=10, allcolors=('#c30a00', '#fcd664', '#000000'), lock_cells=False, set_autolinks=False, origin_files=(), visible_models=True, hide_grid=True, summary='', total_contribution_summary=True):
        tkinter.Frame.__init__(self, master)
        self.periodic_data = periodic_data
        self.results = results
        self.elements = []
        self.color_gradient = []
        self.secondary_windows = []
        self.tertiary_windows = []
        self.CRM_validation_window = None
        self.analinfo_window = None
        self.totalcomposition_window = None
        self.compositionhistory_window = None
        self.summary_window = None
        self.max_windows_open_at_a_time = max_windows_open_at_a_time
        self._true_color, self._false_color = '#FFFFFF', '#ffc60a'
        self.all_colors = allcolors
        self.colors = colors
        self.lock_cells, self.set_autolinks = lock_cells, set_autolinks
        self.origin_files = origin_files
        self.summary = summary
        self.visible_models = visible_models
        self.hide_grid = hide_grid
        self.total_contribution_summary = total_contribution_summary

        if visualization_type == 'sample':
            self.sample_type(resolution, default_palette, display_type)
        elif visualization_type == 'material':
            self.material_type(resolution, default_palette, display_type)

    def material_type(self, resolution, default_palette, display_type):
        HeaderLine = tkinter.Frame(self)
        PTTable = tkinter.Frame(self)
        tkinter.Label(HeaderLine, text='Material', width=8, anchor=tkinter.W).pack(side=tkinter.LEFT, anchor=tkinter.NW)
        self.CB_material_selector = ttk.Combobox(HeaderLine, width=15, state='readonly')
        self.CB_material_selector.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5)
        self.CB_material_selector['values'] = sorted(set([ub.material for ub in self.results]))
        tkinter.Frame(HeaderLine).pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=15)
        
        self.label_min = tkinter.Label(HeaderLine, text='', width=4)
        self.label_min.pack(side=tkinter.LEFT, padx=3)
        for i in range(resolution):
            gradient_label = tkinter.Label(HeaderLine, text='', width=1)
            gradient_label.pack(side=tkinter.LEFT, anchor=tkinter.NW)
            self.color_gradient.append(gradient_label)
        self.label_max = tkinter.Label(HeaderLine, text='', width=4)
        self.label_max.pack(side=tkinter.LEFT, padx=3)
        
        tkinter.Label(HeaderLine, text='palette').pack(side=tkinter.LEFT, padx=3)
        self.CB_palette_selector = ttk.Combobox(HeaderLine, width=15, state='readonly')
        self.CB_palette_selector.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5)
        self.CB_palette_selector['values'] = ('Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'viridis', 'plasma', 'cividis', 'tab20b')
        if default_palette in self.CB_palette_selector['values']:
            self.CB_palette_selector.set(default_palette)
        else:
            self.CB_palette_selector.set('YlOrRd')

        tkinter.Frame(PTTable).grid(row=7, column=0, pady=4)
        element_indicator = tkinter.Label(PTTable, text='', anchor=tkinter.W)
        element_indicator.grid(row=10, column=0, pady=3, columnspan=10, sticky=tkinter.W)
        self.default_color = element_indicator.cget('bg')
        for element in self.periodic_data:
            CB = Button(PTTable, text=element[1], state=tkinter.DISABLED, width=3, bg=self.default_color, anchor=tkinter.W, relief='solid', hint=element[4], hint_destination=element_indicator)
            CB.grid(row=element[2], column=element[3], ipadx=2, ipady=2, sticky=tkinter.W)
            CB.configure(command= lambda el=element[1]: self._set_commando_material(el))
            self.elements.append(CB)
        
        HeaderLine.pack(anchor=tkinter.NW, pady=5)    
        PTTable.pack(anchor=tkinter.NW)
        
        self.CB_material_selector.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.by_number_of_uncertainty_budgets_material())
        self.CB_palette_selector.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.by_number_of_uncertainty_budgets_material())

        if len(self.CB_material_selector['values']) > 0:
            self.CB_material_selector.set(self.CB_material_selector['values'][0])
            self.by_number_of_uncertainty_budgets_material()

        hintlabel = tkinter.Label(self, text='', anchor=tkinter.W)
        bline = tkinter.Frame(self)

        if display_type=='results':
            logo_action = tkinter.PhotoImage(data=PL_ubj_budget)
            B_actiob = Button(bline, image=logo_action, hint='save results as Budget Objects', hint_destination=hintlabel, command=lambda : self.save_results(hintlabel))
            B_actiob.pack(side=tkinter.LEFT)
            B_actiob.image = logo_action
        elif display_type=='show':
            logo_action = tkinter.PhotoImage(data=PL_letter_i)
            B_actiob = Button(bline, image=logo_action, hint='display analysis information', hint_destination=hintlabel, command=lambda : self.show_results())
            B_actiob.pack(side=tkinter.LEFT)
            B_actiob.image = logo_action

        as_CRM = set([ub.asCRM for ub in self.results])
        if True in as_CRM:
            logo_CRM_validation = tkinter.PhotoImage(data=PL_bars)
            B_CRM_validation = Button(bline, image=logo_CRM_validation, hint='display CRM validation', hint_destination=hintlabel, command=lambda : self.display_CRM_validation(hintlabel))
            B_CRM_validation.pack(side=tkinter.LEFT)
            B_CRM_validation.image = logo_CRM_validation

        logo_show_compositionhistory = tkinter.PhotoImage(data=PL_bookmarkedlist)
        B_show_compositionhistory = Button(bline, image=logo_show_compositionhistory, hint='composition of material', hint_destination=hintlabel, command=lambda : self.show_composition_history())
        B_show_compositionhistory.pack(side=tkinter.LEFT)
        B_show_compositionhistory.image = logo_show_compositionhistory

        if self.summary != '':
            logo_display_summary = tkinter.PhotoImage(data=PL_florish)
            B_display_summary = Button(bline, image=logo_display_summary, hint='display analysis overview', hint_destination=hintlabel, command=lambda : self.display_summary())
            B_display_summary.pack(side=tkinter.LEFT)
            B_display_summary.image = logo_display_summary

        bline.pack(anchor=tkinter.NW)
        hintlabel.pack(anchor=tkinter.NW)

    def by_number_of_uncertainty_budgets_material(self):
        material = self.CB_material_selector.get()
        sub_results = [unc_budget for unc_budget in self.results if unc_budget.material == material]
        n_unceraintybudget = [self.how_many_results_per_element(item[1], sub_results) for item in self.periodic_data]
        cmap = cm.get_cmap(self.CB_palette_selector.get())
        nmin, nmax = np.nanmin(n_unceraintybudget) + 1, np.nanmax(n_unceraintybudget)
        colors = cmap(np.nan_to_num(np.array([(i-nmin)/(nmax-nmin) for i in n_unceraintybudget]), copy=False, nan=1.0, posinf=np.inf, neginf=-1.0))
        gradient = cmap(np.linspace(0, 1, len(self.color_gradient)))
        
        for card, color, nn in zip(self.elements, colors, n_unceraintybudget):
            if nn == 0:
                card.configure(state=tkinter.DISABLED)
                card.configure(background='#000000')
            else:
                card.configure(state=tkinter.NORMAL)
                card.configure(background=mcolors.to_hex(color[:3]))
            card.hint = f'{card.hint.split()[0]} ({nn})'
        for grad, gcard in zip(gradient, self.color_gradient):
            gcard.configure(background=mcolors.to_hex(grad[:3]))
        self.label_min.configure(text=nmin)
        self.label_max.configure(text=nmax)

    def _set_commando_material(self, el):
        material = self.CB_material_selector.get()
        sub_results = [unc_budget for unc_budget in self.results if unc_budget.material == material]
        local_data = [item for item in sub_results if item.target == el]
        font_datum = ('Courier', 10)

        self.secondary_windows = self.sweep()
        titles = [self._get_title(window) for window in self.secondary_windows]

        #open_subwindow
        title = f'Material: {material} | results on: {el}'

        if title in titles:
            self.secondary_windows[titles.index(title)].deiconify()
            self.secondary_windows[titles.index(title)].focus()
        else:
            EL = Subwindow(self, title, self._true_color, self._false_color)
            self.secondary_windows.append(EL)
            if len(self.secondary_windows) > self.max_windows_open_at_a_time:
                self.secondary_windows[0].destroy()
                self.secondary_windows[0] = None
                self.secondary_windows = self.sweep()

            hintlabel = tkinter.Label(EL, text='', width=100, anchor=tkinter.W)

            topdata = tkinter.Frame(EL)

            listdata = tkinter.LabelFrame(topdata, labelwidget=tkinter.Label(topdata, text='data'), relief='solid', bd=2, padx=4, pady=4)
            spaces = (4, 5, 18, 10, 9, 7, 6, 8, 3)
            tkinter.Label(listdata, text=f'{"N".ljust(spaces[0])}{"SPC".ljust(spaces[1])}{"EMITTER".ljust(spaces[2])}{"Y".rjust(spaces[3])}{"u(Y)".rjust(spaces[4])}{"ur / %".rjust(spaces[5])}{"STD".rjust(spaces[6])}{"POS".rjust(spaces[7])}{"@".rjust(spaces[8])}  {"SAMPLE"}', width=100, font=font_datum, anchor=tkinter.W).pack(anchor=tkinter.NW)
            EL.SBT = ScrollableListbox(listdata, width=100, height=12, data=self._linearize_material(local_data, spaces), font=font_datum)
            EL.SBT.pack(anchor=tkinter.NW)

            EL.SBT._colored_update([datum.accepted_for_report for datum in local_data], self._true_color, self._false_color)

            actiondata = tkinter.LabelFrame(topdata, labelwidget=tkinter.Label(topdata, text='actions'), relief='solid', bd=2, padx=4, pady=4)

            logo_checkdoe = tkinter.PhotoImage(data=PL_get_result)
            B_checkdoe = Button(actiondata, image=logo_checkdoe, hint='check DoE of selected results', hint_destination=hintlabel, command=lambda : self.calculate_average(local_data, EL))
            B_checkdoe.pack()
            B_checkdoe.image = logo_checkdoe

            logo_savegraph = tkinter.PhotoImage(data=PL_equ)
            B_savegraph = Button(actiondata, image=logo_savegraph, hint='reverse selection', hint_destination=hintlabel, command=lambda : self.reverse_selection(EL, local_data))
            B_savegraph.pack()
            B_savegraph.image = logo_savegraph

            logo_xcell = tkinter.PhotoImage(data=PL_xlsx_budget)
            B_export_uncertainty_budget = Button(actiondata, image=logo_xcell, hint='export uncertainty budget as excel workbook', hint_destination=hintlabel, command=lambda : self._export_element_budget(local_data, EL))
            B_export_uncertainty_budget.pack()
            B_export_uncertainty_budget.image = logo_xcell

            listdata.pack(side=tkinter.LEFT, anchor=tkinter.NW)
            tkinter.Frame(topdata).pack(side=tkinter.LEFT, padx=4)
            actiondata.pack(side=tkinter.LEFT, anchor=tkinter.NW, expand=tkinter.Y)
            
            plotdata = tkinter.LabelFrame(EL, labelwidget=tkinter.Label(EL, text='graphic'), relief='solid', bd=2, padx=4, pady=4)
            figure = Figure(figsize=(9, 3.5))
            axes = figure.subplots(2, 1, sharey=False, sharex=True, gridspec_kw={'height_ratios' : [1.3,1]})
            Figur = tkinter.Frame(plotdata)
            Figur.pack(anchor=tkinter.CENTER, fill=tkinter.BOTH, expand=True)
            canvas = FigureCanvasTkAgg(figure, master=Figur)
            canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
            
            figure.patch.set_alpha(0.0)
            canvas.get_tk_widget().configure(background=EL.cget('bg'))
            
            #plot
            math_range = 3
            k = 2
            width = 0.9
            yfmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
            yfmt.set_powerlimits((math_range, -math_range))
            axes[0].yaxis.set_major_formatter(yfmt)
            axes[1].set_ylim(0, 100)
            axes[0].tick_params(top=False, labeltop=False, bottom=True, labelbottom=True)
            axes[1].tick_params(top=True, labeltop=False, bottom=False, labelbottom=False)
            axes[0].set_xlim(0+0.5, len(local_data)+0.5)
            axes[0].set_ylabel(r'$w$ / g g$^{-1}$')
            axes[1].set_ylabel(r'to $u_\mathrm{c}^2$ / $\%$')
            axes[0].grid(visible=True, axis='y', linestyle='-.', linewidth=0.3)
            ticks = np.arange(1, len(local_data)+1)
            axes[0].set_xticks(ticks, minor=False)
            axes[0].set_xticklabels([f'{number:d}' for number in ticks])
            
            lim0, lim1 = axes[0].get_xlim()
            axis_lenght = lim1 - lim0
            if width > axis_lenght / 10:
                width = axis_lenght / 10
            for nn, item in enumerate(local_data, start=1):
                axes[0].errorbar(nn, item.y, yerr=k*item.uy, marker='o', color='k', markerfacecolor='k', elinewidth=0.5, markersize=3)
                
                statistics, positioning, other = item._get_uncertainty_components()
                bottom = 0
                for color, value in zip(self.colors, (statistics, positioning, other)):
                    axes[1].bar(nn, value*100, width, color=color, bottom=bottom)
                    bottom += value*100
            
            figure.tight_layout()
            canvas.draw()
            
            explanation_frame = tkinter.Frame(plotdata)
            tkinter.Label(explanation_frame, width=1, text='', bg=self.colors[0]).pack(side=tkinter.LEFT)
            tkinter.Label(explanation_frame, text='statistics', anchor=tkinter.W).pack(side=tkinter.LEFT, padx=2)
            tkinter.Frame(explanation_frame).pack(side=tkinter.LEFT, padx=10)
            tkinter.Label(explanation_frame, width=1, text='', bg=self.colors[1]).pack(side=tkinter.LEFT)
            tkinter.Label(explanation_frame, text='efficiency', anchor=tkinter.W).pack(side=tkinter.LEFT, padx=2)
            tkinter.Frame(explanation_frame).pack(side=tkinter.LEFT, padx=10)
            tkinter.Label(explanation_frame, width=1, text='', bg=self.colors[2]).pack(side=tkinter.LEFT)
            tkinter.Label(explanation_frame, text='other', anchor=tkinter.W).pack(side=tkinter.LEFT, padx=2)
            explanation_frame.pack(side=tkinter.BOTTOM, anchor=tkinter.E)

            topdata.pack(anchor=tkinter.NW, padx=5, pady=5)
            plotdata.pack(anchor=tkinter.NW, padx=5, pady=5)
            hintlabel.pack(anchor=tkinter.NW)
            
            EL.SBT.listbox.bind('<Double-Button-1>', lambda e='<Double-Button-1>' : self.dclick(EL, local_data))

    def _linearize_material(self, data, spaces, out='list'):
        lines = [self._data_from_line_material(nn, line, spaces) for nn, line in enumerate(data, start=1)]
        if out == 'list':
            return lines
        return '\n'.join(lines)
		
    def _data_from_line_material(self, nn, line, spaces):
        return f'{format(nn,"d").ljust(spaces[0])}{line.sample_code.ljust(spaces[1])}{line.emission.ljust(spaces[2])}{format(line.y,".2e").rjust(spaces[3])}{format(line.uy,".1e").rjust(spaces[4])}{format(line.uy/line.y*100,".1f").rjust(spaces[5])}{line.standard_code.rjust(spaces[6])}{format(line.counting_position_sm,".1f").rjust(spaces[7])}{line.code[0].rjust(spaces[8])}  {line.sample_id}'
    
    def reverse_selection(self, parent, local_data):
        title_pool = [f'({datum.sample_id}) {idx+1} | {datum.emission}' for idx, datum in enumerate(local_data)]
        for ii, _ in enumerate(self.tertiary_windows):
            try:
                if self.tertiary_windows[ii].title() in title_pool:
                    self.tertiary_windows[ii].destroy()
                    self.tertiary_windows[ii] = None
            except Exception:
                self.tertiary_windows[ii] = None
        self.tertiary_windows = self.sweep3()
        for datum in local_data:
            datum.accepted_for_report = not datum.accepted_for_report
        parent._update(local_data)
        
    def sample_type(self, resolution, default_palette, display_type):
        HeaderLine = tkinter.Frame(self)
        PTTable = tkinter.Frame(self)
        tkinter.Label(HeaderLine, text='Sample', width=8, anchor=tkinter.W).pack(side=tkinter.LEFT, anchor=tkinter.NW)
        self.CB_sample_selector = ttk.Combobox(HeaderLine, width=15, state='readonly')
        self.CB_sample_selector.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5)
        self.CB_sample_selector['values'] = sorted(set([ub.sample_id for ub in self.results]))
        tkinter.Frame(HeaderLine).pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=15)
        
        self.label_min = tkinter.Label(HeaderLine, text='', width=4)
        self.label_min.pack(side=tkinter.LEFT, padx=3)
        for i in range(resolution):
            gradient_label = tkinter.Label(HeaderLine, text='', width=1)
            gradient_label.pack(side=tkinter.LEFT, anchor=tkinter.NW)
            self.color_gradient.append(gradient_label)
        self.label_max = tkinter.Label(HeaderLine, text='', width=4)
        self.label_max.pack(side=tkinter.LEFT, padx=3)
        
        tkinter.Label(HeaderLine, text='palette').pack(side=tkinter.LEFT, padx=3)
        self.CB_palette_selector = ttk.Combobox(HeaderLine, width=15, state='readonly')
        self.CB_palette_selector.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5)
        self.CB_palette_selector['values'] = ('Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'viridis', 'plasma', 'cividis', 'tab20b')
        if default_palette in self.CB_palette_selector['values']:
            self.CB_palette_selector.set(default_palette)
        else:
            self.CB_palette_selector.set('YlOrRd')

        tkinter.Frame(PTTable).grid(row=7, column=0, pady=4)
        element_indicator = tkinter.Label(PTTable, text='', anchor=tkinter.W)
        element_indicator.grid(row=10, column=0, pady=3, columnspan=10, sticky=tkinter.W)
        self.default_color = element_indicator.cget('bg')
        for element in self.periodic_data:
            CB = Button(PTTable, text=element[1], state=tkinter.DISABLED, width=3, bg=self.default_color, anchor=tkinter.W, relief='solid', hint=element[4], hint_destination=element_indicator)
            CB.grid(row=element[2], column=element[3], ipadx=2, ipady=2, sticky=tkinter.W)
            CB.configure(command= lambda el=element[1]: self._set_commando(el))
            self.elements.append(CB)
        
        HeaderLine.pack(anchor=tkinter.NW, pady=5)    
        PTTable.pack(anchor=tkinter.NW)
        
        self.CB_sample_selector.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.by_number_of_uncertainty_budgets())
        self.CB_palette_selector.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.by_number_of_uncertainty_budgets())

        if len(self.CB_sample_selector['values']) > 0:
            self.CB_sample_selector.set(self.CB_sample_selector['values'][0])
            self.by_number_of_uncertainty_budgets()

        hintlabel = tkinter.Label(self, text='', anchor=tkinter.W)
        bline = tkinter.Frame(self)

        if display_type=='results':
            logo_action = tkinter.PhotoImage(data=PL_ubj_budget)
            B_actiob = Button(bline, image=logo_action, hint='save results as Budget Objects', hint_destination=hintlabel, command=lambda : self.save_results(hintlabel))
            B_actiob.pack(side=tkinter.LEFT)
            B_actiob.image = logo_action
        elif display_type=='show':
            logo_action = tkinter.PhotoImage(data=PL_letter_i)
            B_actiob = Button(bline, image=logo_action, hint='display analysis information', hint_destination=hintlabel, command=lambda : self.show_results())
            B_actiob.pack(side=tkinter.LEFT)
            B_actiob.image = logo_action

        as_CRM = set([ub.asCRM for ub in self.results])
        if True in as_CRM:
            logo_CRM_validation = tkinter.PhotoImage(data=PL_bars)
            B_CRM_validation = Button(bline, image=logo_CRM_validation, hint='display CRM validation', hint_destination=hintlabel, command=lambda : self.display_CRM_validation(hintlabel))
            B_CRM_validation.pack(side=tkinter.LEFT)
            B_CRM_validation.image = logo_CRM_validation

        if self.summary != '':
            logo_display_summary = tkinter.PhotoImage(data=PL_florish)
            B_display_summary = Button(bline, image=logo_display_summary, hint='display analysis overview', hint_destination=hintlabel, command=lambda : self.display_summary())
            B_display_summary.pack(side=tkinter.LEFT)
            B_display_summary.image = logo_display_summary

        bline.pack(anchor=tkinter.NW)
        hintlabel.pack(anchor=tkinter.NW)
        
    def how_many_results_per_element(self, element, data):
        return len([item for item in data if item.target == element])
        
    def by_number_of_uncertainty_budgets(self):
        sample = self.CB_sample_selector.get()
        sub_results = [unc_budget for unc_budget in self.results if unc_budget.sample_id == sample]
        n_unceraintybudget = [self.how_many_results_per_element(item[1], sub_results) for item in self.periodic_data]
        cmap = cm.get_cmap(self.CB_palette_selector.get())
        nmin, nmax = np.nanmin(n_unceraintybudget) + 1, np.nanmax(n_unceraintybudget)
        colors = cmap(np.nan_to_num(np.array([(i-nmin)/(nmax-nmin) for i in n_unceraintybudget]), copy=False, nan=1.0, posinf=np.inf, neginf=-1.0))
        gradient = cmap(np.linspace(0, 1, len(self.color_gradient)))
        
        for card, color, nn in zip(self.elements, colors, n_unceraintybudget):
            if nn == 0:
                card.configure(state=tkinter.DISABLED)
                card.configure(background='#000000')
            else:
                card.configure(state=tkinter.NORMAL)
                card.configure(background=mcolors.to_hex(color[:3]))
            card.hint = f'{card.hint.split()[0]} ({nn})'
        for grad, gcard in zip(gradient, self.color_gradient):
            gcard.configure(background=mcolors.to_hex(grad[:3]))
        self.label_min.configure(text=nmin)
        self.label_max.configure(text=nmax)

    def sweep(self):
        return [window for window in self.secondary_windows if window is not None]
    
    def sweep3(self):
        return [window for window in self.tertiary_windows if window is not None]
        
    def _set_commando(self, el):
        sample = self.CB_sample_selector.get()
        sub_results = [unc_budget for unc_budget in self.results if unc_budget.sample_id == sample]
        local_data = [item for item in sub_results if item.target == el]
        font_datum = ('Courier', 10)

        self.secondary_windows = self.sweep()
        titles = [self._get_title(window) for window in self.secondary_windows]

        #open_subwindow
        title = f'Sample: {sample} | results on: {el}'

        if title in titles:
            self.secondary_windows[titles.index(title)].deiconify()
            self.secondary_windows[titles.index(title)].focus()
        else:
            EL = Subwindow(self, title, self._true_color, self._false_color)
            self.secondary_windows.append(EL)
            if len(self.secondary_windows) > self.max_windows_open_at_a_time:
                self.secondary_windows[0].destroy()
                self.secondary_windows[0] = None
                self.secondary_windows = self.sweep()

            hintlabel = tkinter.Label(EL, text='', width=100, anchor=tkinter.W)

            topdata = tkinter.Frame(EL)

            listdata = tkinter.LabelFrame(topdata, labelwidget=tkinter.Label(topdata, text='data'), relief='solid', bd=2, padx=4, pady=4)
            spaces = (4, 5, 18, 10, 9, 7, 6, 8, 3)
            tkinter.Label(listdata, text=f'{"N".ljust(spaces[0])}{"SPC".ljust(spaces[1])}{"EMITTER".ljust(spaces[2])}{"Y".rjust(spaces[3])}{"u(Y)".rjust(spaces[4])}{"ur / %".rjust(spaces[5])}{"STD".rjust(spaces[6])}{"POS".rjust(spaces[7])}{"@".rjust(spaces[8])}  {"MATERIAL"}', width=100, font=font_datum, anchor=tkinter.W).pack(anchor=tkinter.NW)
            EL.SBT = ScrollableListbox(listdata, width=100, height=12, data=self._linearize(local_data, spaces), font=font_datum)
            EL.SBT.pack(anchor=tkinter.NW)

            EL.SBT._colored_update([datum.accepted_for_report for datum in local_data], self._true_color, self._false_color)

            actiondata = tkinter.LabelFrame(topdata, labelwidget=tkinter.Label(topdata, text='actions'), relief='solid', bd=2, padx=4, pady=4)

            logo_checkdoe = tkinter.PhotoImage(data=PL_get_result)
            B_checkdoe = Button(actiondata, image=logo_checkdoe, hint='export uncertainty budget as excel workbook', hint_destination=hintlabel, command=lambda : self.calculate_average(local_data, EL))
            B_checkdoe.pack()
            B_checkdoe.image = logo_checkdoe

            logo_savegraph = tkinter.PhotoImage(data=PL_equ)
            B_savegraph = Button(actiondata, image=logo_savegraph, hint='reverse selection', hint_destination=hintlabel, command=lambda : self.reverse_selection(EL, local_data))
            B_savegraph.pack()
            B_savegraph.image = logo_savegraph

            logo_xcell = tkinter.PhotoImage(data=PL_xlsx_budget)
            B_export_uncertainty_budget = Button(actiondata, image=logo_xcell, hint='export uncertainty budget as excel workbook', hint_destination=hintlabel, command=lambda : self._export_element_budget(local_data, EL))
            B_export_uncertainty_budget.pack()
            B_export_uncertainty_budget.image = logo_xcell

            listdata.pack(side=tkinter.LEFT, anchor=tkinter.NW)
            tkinter.Frame(topdata).pack(side=tkinter.LEFT, padx=4)
            actiondata.pack(side=tkinter.LEFT, anchor=tkinter.NW, expand=tkinter.Y)
            
            plotdata = tkinter.LabelFrame(EL, labelwidget=tkinter.Label(EL, text='graphic'), relief='solid', bd=2, padx=4, pady=4)
            figure = Figure(figsize=(9, 3.5))
            axes = figure.subplots(2, 1, sharey=False, sharex=True, gridspec_kw={'height_ratios' : [1.3,1]})
            Figur = tkinter.Frame(plotdata)
            Figur.pack(anchor=tkinter.CENTER, fill=tkinter.BOTH, expand=True)
            canvas = FigureCanvasTkAgg(figure, master=Figur)
            canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
            
            figure.patch.set_alpha(0.0)
            canvas.get_tk_widget().configure(background=EL.cget('bg'))
            
            #plot
            math_range = 3
            k = 2
            width = 0.9
            yfmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
            yfmt.set_powerlimits((math_range, -math_range))
            axes[0].yaxis.set_major_formatter(yfmt)
            axes[1].set_ylim(0, 100)
            axes[0].tick_params(top=False, labeltop=False, bottom=True, labelbottom=True)
            axes[1].tick_params(top=True, labeltop=False, bottom=False, labelbottom=False)
            axes[0].set_xlim(0+0.5, len(local_data)+0.5)
            axes[0].set_ylabel(r'$w$ / g g$^{-1}$')
            axes[1].set_ylabel(r'to $u_\mathrm{c}^2$ / $\%$')
            axes[0].grid(visible=True, axis='y', linestyle='-.', linewidth=0.3)
            ticks = np.arange(1, len(local_data)+1)
            axes[0].set_xticks(ticks, minor=False)
            axes[0].set_xticklabels([f'{number:d}' for number in ticks])
            
            lim0, lim1 = axes[0].get_xlim()
            axis_lenght = lim1 - lim0
            if width > axis_lenght / 10:
                width = axis_lenght / 10
            for nn, item in enumerate(local_data, start=1):
                axes[0].errorbar(nn, item.y, yerr=k*item.uy, marker='o', color='k', markerfacecolor='k', elinewidth=0.5, markersize=3)
                
                statistics, positioning, other = item._get_uncertainty_components()
                bottom = 0
                for color, value in zip(self.colors, (statistics, positioning, other)):
                    axes[1].bar(nn, value*100, width, color=color, bottom=bottom)
                    bottom += value*100
            
            figure.tight_layout()
            canvas.draw()
            
            explanation_frame = tkinter.Frame(plotdata)
            tkinter.Label(explanation_frame, width=1, text='', bg=self.colors[0]).pack(side=tkinter.LEFT)
            tkinter.Label(explanation_frame, text='statistics', anchor=tkinter.W).pack(side=tkinter.LEFT, padx=2)
            tkinter.Frame(explanation_frame).pack(side=tkinter.LEFT, padx=10)
            tkinter.Label(explanation_frame, width=1, text='', bg=self.colors[1]).pack(side=tkinter.LEFT)
            tkinter.Label(explanation_frame, text='efficiency', anchor=tkinter.W).pack(side=tkinter.LEFT, padx=2)
            tkinter.Frame(explanation_frame).pack(side=tkinter.LEFT, padx=10)
            tkinter.Label(explanation_frame, width=1, text='', bg=self.colors[2]).pack(side=tkinter.LEFT)
            tkinter.Label(explanation_frame, text='other', anchor=tkinter.W).pack(side=tkinter.LEFT, padx=2)
            explanation_frame.pack(side=tkinter.BOTTOM, anchor=tkinter.E)

            topdata.pack(anchor=tkinter.NW, padx=5, pady=5)
            plotdata.pack(anchor=tkinter.NW, padx=5, pady=5)
            hintlabel.pack(anchor=tkinter.NW)
            
            EL.SBT.listbox.bind('<Double-Button-1>', lambda e='<Double-Button-1>' : self.dclick(EL, local_data))

    def show_composition_history(self):
        material = self.CB_material_selector.get()
        sub_results = [unc_budget for unc_budget in self.results if unc_budget.material == material and unc_budget.accepted_for_report]

        averaged_compositions = get_averages_compositions(sub_results, material)

        if len(self.results) > 0:
            icomposition = self.results[0].original_composition
            calcomposition = self.results[0].iterated_composition
            _density, _udensity = self.results[0].EF.rho_a.value, self.results[0].EF.rho_a.uncertainty
        else:
            icomposition = {}
            calcomposition = {}
            _density, _udensity = 1.0, 0.0

        fcomposition = {**icomposition, **averaged_compositions}

        try:
            self.compositionhistory_window.destroy()
        except Exception:
            pass
        self.compositionhistory_window = tkinter.Toplevel(self)
        self.compositionhistory_window.title(f'{material} composition')
        self.compositionhistory_window.resizable(False, False)

        info_sheet = tkinter.LabelFrame(self.compositionhistory_window, labelwidget=tkinter.Label(self.compositionhistory_window, text='compositions'), relief='solid', bd=2, padx=4, pady=4)

        defwidth = 150

        columns = tuple([('element', 50, tkinter.W), ('w / g g⁻¹ (original)', defwidth, tkinter.CENTER), (' ', 30, tkinter.CENTER), ('w / g g⁻¹ (analyst selection)', defwidth, tkinter.CENTER), ('w / g g⁻¹ (full result)', defwidth, tkinter.CENTER)])

        viewtree = ttk.Treeview(info_sheet, columns=[item[0] for item in columns], show='headings', selectmode='browse', height=25)
        for item in columns:
            viewtree.heading(item[0], text=item[0])
            viewtree.column(item[0], anchor=item[2], stretch=False, minwidth=item[1], width=item[1])
        viewtree.grid(row=0, column=0)
        scroll = ttk.Scrollbar(info_sheet, orient="vertical", command=viewtree.yview)
        scroll.grid(row=0, column=1, sticky=tkinter.NS)
        viewtree.configure(yscrollcommand=scroll.set)

        keys = set()
        keys = sorted(keys.union(*[set(item.keys()) for item in (icomposition, fcomposition)]))

        #populate treeview
        nnn = 0
        for element in keys:
            values_data = tuple([f'{element}', self.find_itervalue(icomposition, element), self.elaboration_sing(averaged_compositions, element), self.find_itervalue(fcomposition, element), self.find_itervalue(calcomposition, element)])
            viewtree.insert('', 'end', iid=nnn, values=values_data)
            nnn += 1

        buttonframe = tkinter.Frame(info_sheet)
        hintlabel = tkinter.Label(info_sheet, text='', anchor=tkinter.W)

        logo_savecomposition = tkinter.PhotoImage(data=PL_budget)
        B_savecomposition = Button(buttonframe, image=logo_savecomposition, hint='save material composition', hint_destination=hintlabel, command=lambda : self.save_composition(self.compositionhistory_window, material, fcomposition, calcomposition, hintlabel, _density, _udensity))
        B_savecomposition.pack(side=tkinter.LEFT)
        B_savecomposition.image = logo_savecomposition

        buttonframe.grid(row=1, column=0, columnspan=2, pady=3, sticky=tkinter.W)
        hintlabel.grid(row=2, column=0, columnspan=2, sticky=tkinter.W)

        info_sheet.pack(anchor=tkinter.NW, padx=5, pady=5)

    def find_itervalue(self, iterstep, element):
        value = iterstep.get(element, (np.nan, np.nan))
        if np.isnan(value[0]):
            return ''
        return f'{value[0]:.2e}'
    
    def elaboration_sing(self, iterstep, element):
        value = iterstep.get(element, (np.nan, np.nan))
        if np.isnan(value[0]):
            return ''
        return '->'

    def calculate_average(self, local_data, parent):
        sublocal_data = [local_datum for local_datum in local_data if local_datum.accepted_for_report]
        if len(sublocal_data) > 0:
            values = [local_datum.y for local_datum in sublocal_data]
            samples = [local_datum.sample_id for local_datum in sublocal_data]
            samples_list = sorted(set(samples))
            nn = np.array([_nitem for _nitem, local_datum in enumerate(local_data, start=1) if local_datum.accepted_for_report])
            uncertainties = [local_datum.uy for local_datum in sublocal_data]
            contributions = [local_datum._get_uncertainty_components() for local_datum in sublocal_data]

            #create plot
            TP = tkinter.Toplevel(parent)
            TP.resizable(False, False)

            plotdata = tkinter.LabelFrame(TP, labelwidget=tkinter.Label(TP, text='DoE'), relief='solid', bd=2, padx=4, pady=4)

            selectdata = tkinter.Frame(plotdata)
            tkinter.Label(selectdata, text='sample', anchor=tkinter.W, width=8).pack(side=tkinter.LEFT)
            sample_CB = Combobox(selectdata, width=20, state='readonly')
            sample_CB['values'] = [''] + samples_list
            sample_CB.set('')
            sample_CB.pack(side=tkinter.LEFT)
            if len(samples_list) > 1:
                selectdata.pack(side=tkinter.TOP, anchor=tkinter.NW)

            figure = Figure(figsize=(9, 3))
            axes = figure.subplots(1, 1)
            Figur = tkinter.Frame(plotdata)
            Figur.pack(anchor=tkinter.CENTER, fill=tkinter.BOTH, expand=True)
            canvas = FigureCanvasTkAgg(figure, master=Figur)
            canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
            
            figure.patch.set_alpha(0.0)
            canvas.get_tk_widget().configure(background=TP.cget('bg'))

            math_range = 3
            yfmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
            yfmt.set_powerlimits((math_range, -math_range))
            axes.yaxis.set_major_formatter(yfmt)
            axes.tick_params(top=False, labeltop=False, bottom=True, labelbottom=True)

            plotdata.pack(anchor=tkinter.NW, padx=5, pady=5)

            self._update_calculate_average_plot(sample_CB, values, uncertainties, contributions, nn, samples, sublocal_data[0], axes, figure, canvas, TP)

            plotdata.pack(anchor=tkinter.NW, padx=5, pady=5)

            sample_CB.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : self._update_calculate_average_plot(sample_CB, values, uncertainties, contributions, nn, samples, sublocal_data[0], axes, figure, canvas, TP))

    def _update_calculate_average_plot(self, sample_CB, values, uncertainties, contributions, nn, samples, subloc, axes, figure, canvas, parent):
        axes.clear()

        sstring = sample_CB.get()
        if sstring != '':
            _TF = [item == sstring for item in samples]

            values = [_value for _value, _BOOL in zip(values, _TF) if _BOOL]
            uncertainties = [_value for _value, _BOOL in zip(uncertainties, _TF) if _BOOL]
            contributions = [_value for _value, _BOOL in zip(contributions, _TF) if _BOOL]
            nn = [_value for _value, _BOOL in zip(nn, _TF) if _BOOL]

        VALS, UVALS, how_many = subloc.doe_check(values, uncertainties, contributions)

        axes.set_xlim(0+0.5, len(VALS)+0.5)
        ticks = np.arange(1, len(VALS)+1)
        axes.errorbar(ticks, VALS, yerr=[UVALS, UVALS], marker='o', color='k', markerfacecolor='k', elinewidth=0.5, linestyle='', markersize=3)
        axes.hlines(0, xmin=ticks[0], xmax=ticks[-1], linestyles='solid', linewidth=0.5, color='r')
        axes.set_ylabel(r'$\Delta w$ / g g$^{-1}$')
        axes.grid(visible=True, axis='y', linestyle='-.', linewidth=0.3)
        axes.set_xticks(ticks, minor=False)
        axes.set_xticklabels([f'{number:d}' for number in nn])
        
        figure.tight_layout()
        canvas.draw()

        if sstring != '':
            _sample = f' for sample {sstring}'
        elif len(set(samples)) > 1:
            _sample = ' for all samples'
        else:
            _sample = f' for sample {subloc.sample_id}'
        parent.title(f'DoE graph{_sample}: ({len(VALS)} data with {how_many} suspected outliers)')

    def _export_element_budget(self, local_data, parent):
        title = parent.title().replace(' | results on: ', '_').replace(':', '')
        sublocal_data = [local_datum for local_datum in local_data if local_datum.accepted_for_report]
        if len(sublocal_data) > 0:
            filetypes = (('HyperLab peak list','*.xlsx'),)
            namefile = asksaveasfilename(parent=parent, initialfile=f'{title}.xlsx', filetypes=filetypes)
            if namefile != '':
                SingleBudgetOutput(sublocal_data, namefile, lock_cells=self.lock_cells, set_autolinks=self.set_autolinks, visible_models=self.visible_models, hide_grids=self.hide_grid, total_contribution_summary=self.total_contribution_summary)
                messagebox.showinfo(title='Success', message='Uncertainty budget is saved', parent=parent)
            
    def _linearize(self, data, spaces, out='list'):
        lines = [self._data_from_line(nn, line, spaces) for nn, line in enumerate(data, start=1)]
        if out == 'list':
            return lines
        return '\n'.join(lines)
		
    def _data_from_line(self, nn, line, spaces):
        return f'{format(nn,"d").ljust(spaces[0])}{line.sample_code.ljust(spaces[1])}{line.emission.ljust(spaces[2])}{format(line.y,".2e").rjust(spaces[3])}{format(line.uy,".1e").rjust(spaces[4])}{format(line.uy/line.y*100,".1f").rjust(spaces[5])}{line.standard_code.rjust(spaces[6])}{format(line.counting_position_sm,".1f").rjust(spaces[7])}{line.code[0].rjust(spaces[8])}  {line.material[:20]}'
    
    def _get_title(self, window):
        try:
            return window.title()
        except Exception:
            return None
        
    def _get_legend(self, parent, legend, colors, button):
        TP = tkinter.Toplevel(parent)
        TP.title('Legend')
        TP.resizable(False, False)
        TP.geometry(f'+{button.winfo_rootx()}+{button.winfo_rooty()}')
        nrow = 0
        for item_legend, item_color in zip(legend, colors):
            tkinter.Label(TP, text='', width=1, bg=item_color).grid(row=nrow, column=0)
            tkinter.Label(TP, text=item_legend.symbol, anchor=tkinter.W, width=30).grid(row=nrow, column=1, sticky=tkinter.W, padx=5)
            nrow += 1

    def _export_pie_image(self, parent, figure, legend, L_hintlabel):
        filetypes = (('PNG','*.png'),('JPEG','*.jpeg'))
        namefile = asksaveasfilename(parent=parent, filetypes=filetypes, initialfile=parent.title().replace(' | ', '_')+'.png')
        if namefile != '':
            figure.savefig(namefile)

            legend_elements = [Patch(facecolor=self.all_colors[nn], edgecolor='k', label=_name.symbol) for nn, _name in enumerate(legend)]

            leg_fig = Figure(figsize=(2.8, 2.8), dpi=100)
            leg_fig.legend(handles=legend_elements, loc='center')
            leg_fig.patch.set_alpha(0.0)
            if namefile.endswith('.png'):
                nnamefile = namefile[:-4] + '_legend.png'
            else:
                nnamefile = namefile[:-5] + '_legend.jpeg'
            leg_fig.savefig(nnamefile)

            L_hintlabel.configure(text='image (and legend) saved!')
        else:
            L_hintlabel.configure(text='canceled')

    def _get_symbol_to_contrib(self, budget, item):
        if item == 'net area ratio':
            return budget.NAP
        if item == 'decay ratio':
            return budget.CS
        if item == 'k0 ratio':
            return budget.SC
        if item == 'neutron flux ratio':
            return budget.NF
        if item == 'efficiency ratio':
            return budget.EF
        if item == 'mass ratio':
            return budget.MSS
        if item == 'blank correction':
            return budget.BNK
        if item == 'U fission correction':
            return budget.FSS
        return None

    def _get_parameters_details(self, parent, budget):
        TP = tkinter.Toplevel(parent)
        TP.title(f'{parent.title()} (contribution detail)')
        TP.resizable(False, False)

        clist = sorted([(key, value) for key, value in budget.contributions_to_variance.items()], key=lambda x:x[1], reverse=True)

        first_level_data = tkinter.LabelFrame(TP, labelwidget=tkinter.Label(TP, text='first-level parameter'), relief='solid', bd=2, padx=4, pady=4)

        Label(first_level_data, text='contributor').grid(row=0, column=0)
        Label(first_level_data, text='index').grid(row=0, column=1)
        contribution_CB = Combobox(first_level_data, width=35, state='readonly')
        contribution_CB['values'] = [item[0].symbol for item in clist]
        contribution_CB.grid(row=1, column=0)

        contribution_PB = ttk.Progressbar(first_level_data, length=100, orient='horizontal')
        contribution_PB.grid(row=1, column=1, padx=10)
        contribution_PB['maximum'] = 1

        first_level_data.pack(anchor=tkinter.NW, padx=5, pady=5)

        second_level_data = tkinter.LabelFrame(TP, labelwidget=tkinter.Label(TP, text='second-level parameters'), relief='solid', bd=2, padx=4, pady=4)

        fm_second_level = tkinter.Frame(second_level_data)
        fm_second_level.pack(anchor=tkinter.NW)

        second_level_data.pack(anchor=tkinter.NW, padx=5, pady=5)

        contribution_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._update_detail(contribution_CB, contribution_PB, clist, fm_second_level, budget))

        contribution_CB.set(contribution_CB['values'][0])
        self._update_detail(contribution_CB, contribution_PB, clist, fm_second_level, budget)

    def _update_detail(self, contribution_CB, contribution_PB, clist, fm_second_level, budget):

        contribution_CB.unbind('<<ComboboxSelected>>')

        idx = contribution_CB.current()
        local_space = clist[idx]

        contribution_PB['value'] = local_space[1]
        contribution_PB.update()

        cdn = fm_second_level.winfo_children()
        for i in cdn:
            i.destroy()

        Label(fm_second_level, text='parameter').grid(row=0, column=0)
        Label(fm_second_level, text='local index').grid(row=0, column=1)
        Label(fm_second_level, text='index to result').grid(row=0, column=2)

        subcontribution = self._get_symbol_to_contrib(budget, local_space[0].symbol)
        slist = subcontribution.contribution_list()

        for nline, item in enumerate(slist):

            fig = Figure(figsize=(1.25, 0.25), dpi=100)
            ax = fig.add_subplot(111)
            canvas = FigureCanvasTkAgg(fig, master=fm_second_level)
            canvas.get_tk_widget().grid(row=1+nline, column=0)
            canvas._tkcanvas.grid(row=1+nline, column=0)
            ax.set_axis_off()
            ax.text(0.25, 0.25, item[0], fontsize=9)

            fig.patch.set_alpha(0.0)
            canvas.get_tk_widget().configure(background=fm_second_level.cget('bg'))
            canvas.draw()

            contribution_local = ttk.Progressbar(fm_second_level, length=100, orient='horizontal')
            contribution_local.grid(row=1+nline, column=1, padx=10)
            contribution_local['maximum'] = 1
            contribution_local['value'] = item[1]
            contribution_local.update()

            contribution_total = ttk.Progressbar(fm_second_level, length=100, orient='horizontal')
            contribution_total.grid(row=1+nline, column=2, padx=10)
            contribution_total['maximum'] = 1
            contribution_total['value'] = local_space[1] * item[1]
            contribution_total.update()

        contribution_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._update_detail(contribution_CB, contribution_PB, clist, fm_second_level, budget))

    def change_selection(self, local_data, idx, variable, parent):
        local_data[idx].accepted_for_report = variable.get()
        parent._update(local_data)

    def _export_single_budget(self, local_budget, parent):
        filetypes = (('HyperLab peak list','*.xlsx'),)
        ftitle = parent.title().replace(' | ', '_')
        namefile = asksaveasfilename(parent=parent, initialfile=f'{ftitle}.xlsx', filetypes=filetypes)
        if namefile != '':
            SingleBudgetOutput(local_budget, namefile, lock_cells=self.lock_cells, set_autolinks=self.set_autolinks, visible_models=self.visible_models, hide_grids=self.hide_grid, total_contribution_summary=self.total_contribution_summary)
            messagebox.showinfo(title='Success', message='Uncertainty budget is saved', parent=parent)

    def save_results(self, hintlabel):
        if len(self.results) > 0:
            filetypes = (('Budget Object','*.boj'),)
            namefile = asksaveasfilename(parent=self, initialfile=f'Analysis.boj', filetypes=filetypes)
            if namefile != '':
                ResRep = ResultReport(self.results)
                analysisoutput(ResRep, namefile)
                hintlabel.configure(text='Uncertainty Budget object saved')
            else:
                hintlabel.configure(text='invalid name')

    def display_CRM_validation(self, hintlabel):
        sub_result = [bud for bud in self.results if bud.asCRM and bud.accepted_for_report]
        if len(sub_result) > 0:
            try:
                self.CRM_validation_window.deiconify()
                self.CRM_validation_window.focus()
            except Exception:
                self.CRM_validation_window = tkinter.Toplevel(self)
                self.CRM_validation_window.title('internal CRM validation')
                self.CRM_validation_window.resizable(False, False)
                self.CRM_validation_window.index = 0

                zs = np.array([ress._get_z_score_info() for ress in sub_result])
                xx = np.arange(len(zs))
                text1 = [ress.emission for ress in sub_result]
                text2 = [ress.sample_id for ress in sub_result]
                text3 = [ress.material for ress in sub_result]
                texts = (text1, text2, text3)
                idxs = list(set(text3))
                colors = [self.set_color_CRM(idxs, tex) for tex in text3]

                plotdata = tkinter.LabelFrame(self.CRM_validation_window, labelwidget=tkinter.Label(self.CRM_validation_window, text='graphic'), relief='solid', bd=2, padx=4, pady=4)
                figure = Figure(figsize=(9, 4.5))
                axes = figure.subplots(1, 1)
                Figur = tkinter.Frame(plotdata)
                Figur.pack(anchor=tkinter.CENTER, fill=tkinter.BOTH, expand=True)
                canvas = FigureCanvasTkAgg(figure, master=Figur)
                canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
                
                figure.patch.set_alpha(0.0)
                canvas.get_tk_widget().configure(background=self.CRM_validation_window.cget('bg'))

                if len(sub_result) < 4:
                    width = len(sub_result) / 10
                else:
                    width = 0.5
                axes.bar(xx, zs, width, color=colors, edgecolor='k', linewidth=0.15)
                axes.axhline(0, 0, 1, linestyle='-', linewidth=0.35, color='k')
                xxx = np.array([np.min(xx) - 0.5, np.max(xx) + 0.5])
                axes.fill_between(xxx, y1=-2, y2=2, color='green', alpha=0.15)
                axes.fill_between(xxx, y1=-3, y2=-2, color='yellow', alpha=0.15)
                axes.fill_between(xxx, y1=2, y2=3, color='yellow', alpha=0.15)
                axes.fill_between(xxx, y1=-4, y2=-3, color='red', alpha=0.15)
                axes.fill_between(xxx, y1=3, y2=4, color='red', alpha=0.15)
                axes.set_ylim(-4, 4)
                axes.set_xlim(xxx[0], xxx[1])
                axes.set_xticks(xx, minor=False)
                axes.set_xticklabels(texts[self.CRM_validation_window.index], rotation=90)
                figure.tight_layout()
                
                canvas.draw()

                buttondata = tkinter.Frame(plotdata)
                L_hintlabel = tkinter.Label(self.CRM_validation_window)

                logo_cycletexts = tkinter.PhotoImage(data=PL_frame)
                B_cycle_text = Button(buttondata, image=logo_cycletexts, hint='cycle through labels', hint_destination=L_hintlabel)
                B_cycle_text.pack(side=tkinter.LEFT)
                B_cycle_text.image = logo_cycletexts
                B_cycle_text.configure(command=lambda : self.cycle_through(axes, figure, canvas, texts))

                logo_savefigure = tkinter.PhotoImage(data=PL_save)
                B_savefigure = Button(buttondata, image=logo_savefigure, hint='save figure', hint_destination=L_hintlabel)
                B_savefigure.pack(side=tkinter.LEFT)
                B_savefigure.image = logo_savefigure
                B_savefigure.configure(command=lambda : self.save_figure_CRM(axes, figure, canvas, texts, idxs, L_hintlabel))

                buttondata.pack(anchor=tkinter.NW)

                plotdata.pack(anchor=tkinter.NW, padx=5, pady=5)
                L_hintlabel.pack(anchor=tkinter.NW)

        else:
            hintlabel.configure(text='error message!')

    def set_color_CRM(self, idxs, tex):
        ridx = idxs.index(tex)
        ridx = ridx % len(self.all_colors)
        return self.all_colors[ridx]
        
    def cycle_through(self, axes, figure, canvas, texts):
        if self.CRM_validation_window.index == len(texts) - 1:
            self.CRM_validation_window.index = 0
        else:
            self.CRM_validation_window.index += 1
        axes.set_xticklabels(texts[self.CRM_validation_window.index], rotation=90)
        figure.tight_layout()
        canvas.draw()

    def save_figure_CRM(self, axes, figure, canvas, texts, idxs, L_hintlabel):
        filetypes = (('PNG','*.png'),('JPEG','*.jpeg'))
        namefile = asksaveasfilename(parent=self.CRM_validation_window, filetypes=filetypes)
        
        axes.set_xticklabels(texts[self.CRM_validation_window.index], rotation=90)
        figure.tight_layout()
        canvas.draw()

        if namefile != '':
            figure.savefig(namefile)

            legend_elements = [Patch(facecolor=self.all_colors[nn], edgecolor='k', label=_name) for nn, _name in enumerate(idxs)]

            leg_fig = Figure(figsize=(5, 3.5), dpi=100)
            leg_fig.legend(handles=legend_elements, loc='center')
            leg_fig.patch.set_alpha(0.0)
            if namefile.endswith('.png'):
                nnamefile = namefile[:-4] + '_legend.png'
            else:
                nnamefile = namefile[:-5] + '_legend.jpeg'
            leg_fig.savefig(nnamefile)

            L_hintlabel.configure(text='image (and legend) saved!')
        else:
            L_hintlabel.configure(text='canceled')

    def show_results(self):
        header = 'Analysis files:\n' + '\n'.join(self.origin_files) + '\n\n'
        summary = []
        for item in self.results:
            text_data = self.devoile(item.info_data, item.CS.irr_time)
            if text_data not in summary:
                summary.append(text_data)

        if len(summary) > 0:
            try:
                self.analinfo_window.deiconify()
                self.analinfo_window.focus()
            except Exception:
                self.analinfo_window = tkinter.Toplevel(self)
                self.analinfo_window.title('Analysis information')
                self.analinfo_window.resizable(False, False)
                _txt = ScrollableText(self.analinfo_window, width=45, height=10, data=header + '\n\n##########\n\n'.join(summary))
                _txt.pack(anchor=tkinter.NW, padx=5, pady=5)

    def devoile(self, infobit, timebit):
        return f'irradiation: {infobit["irr_code"]}\nend date: {(infobit["irr_datetime"]).strftime("%d/%m/%Y %H:%M:%S")}\nirradiation time: {timebit.get_value():.0f} s\nchannel: {infobit["irr_channel"]}\ndetector: {infobit["detector"]}'

    def save_composition(self, parent, material_name, composition1, composition2, ehintlabel, _density, _udensity):

        #save material information
        description = 'no description'
        stype = 'unknown'
        state = 'unknown'
        ddensity = _density
        uddensity = _udensity

        if composition1 != {} and composition2 != {}:
            try:
                self.totalcomposition_window.destroy()
            except Exception:
                pass
            self.totalcomposition_window = tkinter.Toplevel(parent)
            self.totalcomposition_window.title(f'{material_name} composition')
            self.totalcomposition_window.resizable(False, False)

            hintlabel = tkinter.Label(self.totalcomposition_window, text='', anchor=tkinter.W)

            info_header = tkinter.LabelFrame(self.totalcomposition_window, labelwidget=tkinter.Label(self.totalcomposition_window, text='information'), relief='solid', bd=2, padx=4, pady=4)

            tkinter.Label(info_header, text='composition', anchor=tkinter.W, width=15).grid(row=0, column=0, sticky=tkinter.W)

            tkinter.Label(info_header, text='name', anchor=tkinter.W).grid(row=1, column=0, sticky=tkinter.W)

            tkinter.Label(info_header, text='description', anchor=tkinter.W).grid(row=2, column=0, sticky=tkinter.W)

            tkinter.Label(info_header, text='type', anchor=tkinter.W).grid(row=3, column=0, sticky=tkinter.W)

            tkinter.Label(info_header, text='state', anchor=tkinter.W).grid(row=4, column=0, sticky=tkinter.W)

            tkinter.Label(info_header, text='density / g cm⁻³', anchor=tkinter.W).grid(row=5, column=0, sticky=tkinter.W)

            selection_CB = Combobox(info_header, state='readonly')
            selection_CB['values'] = ('analyst selection', 'full result')
            selection_CB.grid(row=0, column=1, padx=3)
            selection_CB.set(selection_CB['values'][0])

            filename_E = Entry(info_header)
            filename_E.grid(row=1, column=1, padx=3, sticky=tkinter.EW)
            filename_E.insert(0, material_name)

            Label(info_header, text=description, anchor=tkinter.W).grid(row=2, column=1, padx=3, sticky=tkinter.E)
            Label(info_header, text=stype, anchor=tkinter.W).grid(row=3, column=1, padx=3, sticky=tkinter.E)
            Label(info_header, text=state, anchor=tkinter.W).grid(row=4, column=1, padx=3, sticky=tkinter.E)
            Label(info_header, text=f'{ddensity:.3f}', anchor=tkinter.W).grid(row=5, column=1, padx=3, sticky=tkinter.E)

            logo_savecomposition_forreal = tkinter.PhotoImage(data=PL_save)
            B_savecomposition_forreal = Button(info_header, image=logo_savecomposition_forreal, hint='save material composition', hint_destination=hintlabel, command=lambda : self.save_selected_composition(selection_CB, filename_E, composition1, composition2, description, stype, state, ddensity, uddensity, hintlabel))
            B_savecomposition_forreal.grid(row=6, column=0, columnspan=2, pady=5)
            B_savecomposition_forreal.image = logo_savecomposition_forreal

            info_header.pack(anchor=tkinter.NW, padx=5, pady=5)
            hintlabel.pack(anchor=tkinter.NW)
        else:
            ehintlabel.configure(text='no composition to save')

    def save_selected_composition(self, selection_CB, filename_E, composition1, composition2, description, stype, state, ddensity, uddensity, hintlabel):

        def not_cert(value):
            if np.isnan(value):
                return ''
            return value

        def _to_csv(certificate):
            text = [f'{key},{item[0]},{not_cert(item[1])}' for key,item in certificate.items()]
            return '\n'.join(text)

        if selection_CB.get() == selection_CB['values'][0]:
            composition = composition1
        else:
            composition = composition2

        name_of_material = filename_E.get()

        if name_of_material.replace(' ','') != '':

            with open(os.path.join(os.path.join('data','samples'),f'{name_of_material}.csv'),'w') as saved_sample:
                    saved_sample.write(f'{description}\n')
                    saved_sample.write(f'{stype}\n')
                    saved_sample.write(f'{state}\n')
                    saved_sample.write(f'{ddensity}\n')
                    saved_sample.write(f'{uddensity}\n')
                    saved_sample.write(f'{_to_csv(composition)}')

            hintlabel.configure(text='composition saved in "samples" folder')
        else:
            hintlabel.configure(text='invalid name')
        
    def dclick(self, parent, local_data):
        try:
            idx = parent.SBT.curselection()[0]
        except IndexError:
            idx = None
        if idx is not None:
            title = f'({local_data[idx].sample_id}) {idx+1} | {local_data[idx].emission}'

            self.tertiary_windows = self.sweep3()
            titles = [self._get_title(window) for window in self.tertiary_windows]
            if title in titles:
                self.tertiary_windows[titles.index(title)].deiconify()
                self.tertiary_windows[titles.index(title)].focus()
            else:
                EL = tkinter.Toplevel(parent)
                EL.title(title)
                EL.resizable(False, False)
                self.tertiary_windows.append(EL)
                if len(self.tertiary_windows) > self.max_windows_open_at_a_time:
                    self.tertiary_windows[0].destroy()
                    self.tertiary_windows[0] = None
                    self.tertiary_windows = self.sweep3()

                listdata = tkinter.LabelFrame(EL, labelwidget=tkinter.Label(EL, text='measurement result'), relief='solid', bd=2, padx=4, pady=4)

                L_hintlabel = tkinter.Label(EL, text='', anchor=tkinter.W)

                tkinter.Label(listdata, text='target', width=10, anchor=tkinter.W).grid(row=0, column=0)
                tkinter.Label(listdata, text='w / g g⁻¹', width=13, anchor=tkinter.W).grid(row=0, column=1)
                tkinter.Label(listdata, text='u(w) / g g⁻¹', width=13, anchor=tkinter.W).grid(row=0, column=2)
                tkinter.Label(listdata, text='ur(w) / 1', width=13, anchor=tkinter.W).grid(row=0, column=3)

                tkinter.Label(listdata, text=local_data[idx].target, width=10, anchor=tkinter.W).grid(row=1, column=0)
                tkinter.Label(listdata, text=f'{local_data[idx].y:.3e}', width=13, anchor=tkinter.W).grid(row=1, column=1)
                tkinter.Label(listdata, text=f'{local_data[idx].uy:.1e}', width=13, anchor=tkinter.W).grid(row=1, column=2)
                tkinter.Label(listdata, text=f'{local_data[idx].uy / local_data[idx].y*100:.1f} %', width=13, anchor=tkinter.W).grid(row=1, column=3)

                tkinter.Frame(listdata).grid(row=2, column=0, pady=3)
                EL.user_accepted_variable = tkinter.BooleanVar(EL)

                CB_accept = Checkbutton(listdata, text='accepted result', onvalue=1, offvalue=0, variable=EL.user_accepted_variable, command=lambda : self.change_selection(local_data, idx, EL.user_accepted_variable, parent))
                CB_accept.grid(row=3, column=0, columnspan=4, sticky=tkinter.W)
                EL.user_accepted_variable.set(local_data[idx].accepted_for_report)

                buttons_frame = tkinter.Frame(listdata)

                logo_excel = tkinter.PhotoImage(data=PL_xlsx_budget)
                B_export_uncertainty_budget = Button(buttons_frame, image=logo_excel, hint='export uncertainty budget as excel workbook', hint_destination=L_hintlabel)
                B_export_uncertainty_budget.pack(side=tkinter.LEFT)
                B_export_uncertainty_budget.image = logo_excel
                B_export_uncertainty_budget.configure(command=lambda : self._export_single_budget(local_data[idx], EL))
                
                buttons_frame.grid(row=4, column=0, columnspan=4, sticky=tkinter.W, pady=3)

                listdata.grid(row=0, column=0, sticky=tkinter.NW, padx=3, pady=3)

                graphdata = tkinter.LabelFrame(EL, labelwidget=tkinter.Label(EL, text='contribution to variance'), relief='solid', bd=2, padx=4, pady=4)

                contr_figure = Figure(figsize=(3, 3))
                contr_figure.patch.set_alpha(0.0)
                contr_ax = contr_figure.add_subplot(111)
                Figur = tkinter.Frame(graphdata)
                Figur.grid(row=0, column=0, sticky=tkinter.NSEW)
                contr_canvas = FigureCanvasTkAgg(contr_figure, master=Figur)
                contr_canvas.draw()
                contr_canvas.get_tk_widget().configure(background=graphdata.cget('bg'))
                contr_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

                legend = local_data[idx].contributions_to_variance.keys()
                values = [local_data[idx].contributions_to_variance[key] for key in legend]
                contr_ax.pie(values, explode=[0.05]*len(legend), colors=self.all_colors, autopct='%1.1f%%', wedgeprops={'ec':'k', 'lw':0.3}, pctdistance=1.15)

                contr_figure.tight_layout()
                contr_canvas.draw()

                LFM = tkinter.Frame(graphdata)

                logo_legend = tkinter.PhotoImage(data=PL_list)
                B_legend = Button(LFM, image=logo_legend, hint='legend', hint_destination=L_hintlabel)
                B_legend.pack(side=tkinter.LEFT)
                B_legend.image = logo_legend
                B_legend.configure(command=lambda : self._get_legend(EL, legend, self.all_colors, B_legend))

                logo_details = tkinter.PhotoImage(data=PL_budget)
                B_parameterdetails = Button(LFM, image=logo_details, hint='details of parameters', hint_destination=L_hintlabel, command=lambda : self._get_parameters_details(EL, local_data[idx]))
                B_parameterdetails.pack(side=tkinter.LEFT)
                B_parameterdetails.image = logo_details

                logo_save_pie = tkinter.PhotoImage(data=PL_cake)#or PL_save
                B_save_pie = Button(LFM, image=logo_save_pie, hint='save pie image', hint_destination=L_hintlabel)
                B_save_pie.pack(side=tkinter.LEFT)
                B_save_pie.image = logo_save_pie
                B_save_pie.configure(command=lambda : self._export_pie_image(EL, contr_figure, legend, L_hintlabel))

                LFM.grid(row=1, column=0, sticky=tkinter.W)
                
                graphdata.grid(row=0, column=1, rowspan=2, sticky=tkinter.E, padx=3, pady=3)

                additionaldata = tkinter.LabelFrame(EL, labelwidget=tkinter.Label(EL, text='additional information'), relief='solid', bd=2, padx=4, pady=4)

                tkinter.Label(additionaldata, text='standardization', width=15, anchor=tkinter.W).grid(row=0, column=0, sticky=tkinter.W)
                if local_data[idx].method == 'k0':
                    ad_text = f'{local_data[idx].method} ({local_data[idx].monitor})'
                else:
                    ad_text = local_data[idx].method
                tkinter.Label(additionaldata, text=ad_text, width=20, anchor=tkinter.W).grid(row=0, column=1, columnspan=2, sticky=tkinter.W)
                tkinter.Frame(additionaldata).grid(row=1, column=0, pady=3)
                tkinter.Label(additionaldata, text='standard code', width=15, anchor=tkinter.W).grid(row=2, column=0, sticky=tkinter.W)
                tkinter.Label(additionaldata, text=local_data[idx].standard_id, width=8, anchor=tkinter.W).grid(row=2, column=1, sticky=tkinter.W)
                tkinter.Label(additionaldata, text='standard mass', width=15, anchor=tkinter.W).grid(row=2, column=2, sticky=tkinter.W)
                masss = local_data[idx].MSS.m_m.value
                tkinter.Label(additionaldata, text=f'{masss:.4f} g', width=11, anchor=tkinter.W).grid(row=2, column=3, sticky=tkinter.W)
                tkinter.Label(additionaldata, text='spectrum code', width=15, anchor=tkinter.W).grid(row=3, column=0, sticky=tkinter.W)
                tkinter.Label(additionaldata, text=local_data[idx].standard_code, width=8, anchor=tkinter.W).grid(row=3, column=1, sticky=tkinter.W)
                tkinter.Label(additionaldata, text='counting position', width=15, anchor=tkinter.W).grid(row=3, column=2, sticky=tkinter.W)
                tkinter.Label(additionaldata, text=f'{local_data[idx].counting_position_std:.1f} mm', width=11, anchor=tkinter.W).grid(row=3, column=3, sticky=tkinter.W)
                tkinter.Frame(additionaldata).grid(row=5, column=0, pady=3)
                tkinter.Label(additionaldata, text='sample code', width=15, anchor=tkinter.W).grid(row=6, column=0, sticky=tkinter.W)
                tkinter.Label(additionaldata, text=local_data[idx].sample_id, width=8, anchor=tkinter.W).grid(row=6, column=1, sticky=tkinter.W)
                tkinter.Label(additionaldata, text='sample mass', width=15, anchor=tkinter.W).grid(row=6, column=2, sticky=tkinter.W)
                masss = masss = local_data[idx].MSS.m_a.value
                tkinter.Label(additionaldata, text=f'{masss:.4f} g', width=11, anchor=tkinter.W).grid(row=6, column=3, sticky=tkinter.W)
                tkinter.Label(additionaldata, text='spectrum code', width=15, anchor=tkinter.W).grid(row=7, column=0, sticky=tkinter.W)
                tkinter.Label(additionaldata, text=local_data[idx].sample_code, width=8, anchor=tkinter.W).grid(row=7, column=1, sticky=tkinter.W)
                tkinter.Label(additionaldata, text='counting position', width=15, anchor=tkinter.W).grid(row=7, column=2, sticky=tkinter.W)
                tkinter.Label(additionaldata, text=f'{local_data[idx].counting_position_sm:.1f} mm', width=11, anchor=tkinter.W).grid(row=7, column=3, sticky=tkinter.W)
                tkinter.Frame(additionaldata).grid(row=9, column=0, pady=3)
                tkinter.Label(additionaldata, text='assigned value', width=15, anchor=tkinter.W).grid(row=10, column=0, sticky=tkinter.W)
                if np.isnan(local_data[idx].cert_x):
                    labeltext = '-'
                else:
                    labeltext = f'{local_data[idx].cert_x:.2e}'
                tkinter.Label(additionaldata, text=labeltext, width=8, anchor=tkinter.W).grid(row=10, column=1, sticky=tkinter.W)
                tkinter.Label(additionaldata, text='uncertainty', width=15, anchor=tkinter.W).grid(row=10, column=2, sticky=tkinter.W)
                if np.isnan(local_data[idx].cert_ux):
                    labeltext = '-'
                else:
                    labeltext = f'{local_data[idx].cert_ux:.1e}'
                tkinter.Label(additionaldata, text=labeltext, width=8, anchor=tkinter.W).grid(row=10, column=3, sticky=tkinter.W)
                tkinter.Label(additionaldata, text='z score', width=15, anchor=tkinter.W).grid(row=11, column=0, sticky=tkinter.W)
                tkinter.Label(additionaldata, text=f'{local_data[idx]._get_z_score_info():.1f}', width=8, anchor=tkinter.W).grid(row=11, column=1, sticky=tkinter.W)
                #tkinter.Label(additionaldata, text='likelihood', width=15, anchor=tkinter.W).grid(row=11, column=2, sticky=tkinter.W)
                #if 0.001 <= local_data[idx].likelihood <= 1:
                #    likeli = f'{local_data[idx].likelihood:.3f}'
                #elif local_data[idx].likelihood < 0.001:
                #    likeli = '< 0.001'
                #else:
                #    likeli = '> 1!'
                #tkinter.Label(additionaldata, text=likeli, width=8, anchor=tkinter.W).grid(row=11, column=3, sticky=tkinter.W)
                additionaldata.grid(row=1, column=0, sticky=tkinter.EW, padx=3, pady=3)

                L_hintlabel.grid(row=2, column=0, columnspan=2, sticky=tkinter.EW)

    def display_summary(self):
        try:
            self.summary_window.deiconify()
            self.summary_window.focus()
        except Exception:
            self.summary_window = tkinter.Toplevel(self)
            self.summary_window.title('Summary')
            self.summary_window.resizable(False, False)
        
            Data_frame = tkinter.LabelFrame(self.summary_window, labelwidget=tkinter.Label(self.summary_window, text='Full overview of analysis'), relief='solid', bd=2, padx=4, pady=4)

            overview = ScrollableText(Data_frame, width=70, height=25, data=self.summary)

            overview.pack()
            Data_frame.pack(anchor=tkinter.NW, padx=5, pady=5)


def get_averages_compositions(budget_list, material):
	#call of pandas dataframe for a better data management
	_all_target_list = pd.DataFrame([[ub.target, ub.y, ub.uy, ub.material] for ub in budget_list], columns=['target','y','uy', 'material'])

	_sub_target_list = _all_target_list[_all_target_list['material'] == material]

	v_counts = _sub_target_list['target'].value_counts()
	averages = {}

	for idx in v_counts.index:
		ave, sumofweights = np.average(_all_target_list[_all_target_list['target'] == idx]['y'], weights=np.power(_all_target_list[_all_target_list['target'] == idx]['uy'], 2), returned=True)
		averages[idx] = (ave, np.sqrt(sumofweights))

	return averages


class ScrollableText(tkinter.Frame):
    """A simple yet effective scrollable text"""
    def __init__(self, master, wrap=tkinter.WORD, state='disabled', width=30, height=8, data='', **kwargs):
        tkinter.Frame.__init__(self, master)
        self.text = tkinter.Text(self, width=width, height=height, state=state, wrap=wrap, **kwargs)
        self.scrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        self.text.pack(side=tkinter.LEFT, anchor=tkinter.NW, fill=tkinter.BOTH, expand=True)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._update(data)

    def _update(self,data=''):
        original_state = self.text.cget('state')
        self.text.configure(state='normal')
        self.text.delete('0.0',tkinter.END)
        self.text.insert(tkinter.END, data)
        self.text.configure(state=original_state)

    def get(self):
        return self.text.get('0.0',tkinter.END)


#############################
###    BRAND NEW ICONS    ###
#############################

PL_m_void = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAcSURBVFiF7cGBAAAAAMOg+VMf4QJVAQAAAADHABNHAAHPMYCrAAAAAElFTkSuQmCC'

PL_s_void = 'iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAZSURBVEiJ7cEBDQAAAMKg909tDwcUAAA3BgndAAF85o4iAAAAAElFTkSuQmCC'

PL_letter_phi = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJWSURBVFiF7dfPbw1RFAfwz2tf60eFNo1qrIlIWDRN/AgLEYSFDRthJRZ2CKF2Fv4CO3uJpGXTIsSClkglFhZ+RDckFrQiPEWL0FrMa96d6bz2dd7r7n2TSebO98w533vnnHPvUEcdC0Ouinc7sAIFTM9jm0cTPlQRryxy+FQUUek1Op/TfEYxefSJZpsTrdJeLA9sXuE1vmEKzzPGyoSHSqswLEMKNNRISCO6g/GA+fNo0dAtnh/bsjhprELAMuzAQZzE+oAbRSs+Y6KKGHOiCYdwqxhkWlTav5RW5Qsmi/f/cB/7aikih2N4WwzyET1YJ6qs8UDMBSzBATwJnveJ+lJV6MCdwOk1tAT8FvF82RpwDbgZcI/RnFXIWowEzm6YXbLnA37c7N61OSH2TBYhjXgaOClgdYrd7cDmbgq/NCFmOIuYEwknV8oILgQ2PSk2nQk/78oFnKvpHUmM+1NsurAqGA+VsQkxMkfMsngvPqP2FJtzAf9dVPpJXE34OZpFTJgv09KrYCDg76XwnfgZ2AzKuAWdSojZkOAbRA1uhr+YwvcH/EvpBVAR8ngUOLsuPquuhNjtAdeK3oAbQFtWITNYKd60hrBHlBunxfOlGRtxCWPF5y9wWHUnylnYXxQyVQzyQ7QJzoiZwFelftQr2sNqdURJxRrRTC+Lf6IHohzbJb2iFhXJ/WhnLZxmXcbdwf0kntVASybkxM+7g7V0PB+OKx0j20X9ZlPAT4iSewx/8Bdn8btWIkO8sbD/o4KMv0CVrEyLyg9EbaL2P5ZFTB11LBT/AUG7zP4S4blyAAAAAElFTkSuQmCC'

PL_letter_gamma = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGPSURBVFiF7da/S1ZRHMfxl4qKSkmb2lA0uWTUHyApToKgS25B0CKB0OSfYKsFDkFrIKi1Cg4O4o8aWzIIXCIDRUQHNVGHc4KbPdjzXI9cxOcDhwvnnO/nvO/5nnvul6qqusKqyRFzC8N4gFp8xztsnRNTi8f4jN0ca/6jGryMZidn2ia6z4l9iiPcSwFSh/clILJtGx0lYuuxjqkUIPA6s+hPfMAbTONXZmyyROyzOPYoBUhvNNvFczScGW/Gqzjn0N+7U4evmEsBAkvY8f83m4hALzJ9T2JfTwqQzmg2VsbcG8JBns/0LWElBQi0YxRNZc6fFFLViIfCiwymgqlUQxGgC2+xJtwxhehuhBnBnvLSe2lqiTAb+I22ImFgXwD6WDQIYVdOMFA0CPwQbun6SgMv46S3YFY4MxUpNcx9tGI5T3BqmP74/JbYN5cWcCwUYIXqpvAryL0rKdPUJ3xBq3kNUsL8KTsXE3rm1ifhsrtTNEgTDvDlIiap0nRbKEdnEvldSA0YF6q9qqq6njoFXJlU98CsgrEAAAAASUVORK5CYII='

PL_get_result = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALASURBVFiF7djPi5VVGMDxzzn3Mg1IP8zIlCKV5tImB3JcBIEVbQo3CUELLaJW/QGRBEH6DwRN0C536bRo26ICI1qIzlzBRSTqwjQX0g/FMpv7nhb33OvM+L5zf3Jx4Xdzn/ecc8/zvefAe85zuYsIE8z1IHbneBr/oYW/8RPUJigTsIw/8D4u4Ex+vgb1PPAhzOW41HoM3MT5HF/H5RXPIK4ZeB5v4+EcXxyTSF90VqandQkzeKCk/QJ+H0Ym9h5Syf3YiKcxn+ONmBp2wnrvIZUs5s/teAffjjAXRluZsXNPpoqJyyxQe55N79FY6OOlewR7Bph/O77vZ2CTvc3o1MlgeTG41YxOLfFqp3/VygxqPQhLzKTg05TsDO28MSU7U/B5k8YqmSZ7G9GJT4JX3g0+a0QnVlqPSojexON3tLOliA50ZfqxrmKasJWp1OMGkHi0UpTNXRnRW1XWov1lEyxQW4wO/xB993Xw3Ono58XoUNX2hnWOl8C52zLrWKdsvZZG9FFIPqgnT9QJKdkRkoMz0celCQvzouYdHVEzFOa7MutZp5K+vCVvlCbl9bItm+VGvWVfCI5eDa79E1wSHK237JvlRv4up9mQao6nwmxBLVAEkqjZatkz177XdDnJlnpwNnFfIiRibN9/BP5dTmbm+K3qB2q/Pr7A8dWLlK1rLa+VWa8VgV1cEVwqy5KCX3dxZR2RSrqn9jNcVDhQZb2SQFriS3y4ph2+CqSRZAblbOHwU1Fssb9InpwKzuHYL4VDw85ZxhEDHAfT7NjKj73eM/3kGPmgvEm6zK1ht2asMuPknkwVo1zIB2UTXsrxNrygfQxdxzeTlvnL7QpiZSXR6gQdmUfwYo63KbEeA506u5KOzJ96WE+CjkxP6xKe1a7JH9OuJF/O7WcMeTaN8v9Mp9auZZmruX3oWvuu4n+/GszQUYoUZAAAAABJRU5ErkJggg=='

PL_confirm_bullseye = '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'

PL_k0circle = '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'

PL_letter_i = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFFSURBVFiF7dUxSxxBGIfxnxdjZRWRdBbBTpSAuUKIaCFWWvgVDmxs9BtYBXsLOW1sLCxFkEhIY6ESBMFKEEFIp5YWIscZi51jp0ihyzFbuA8M7PyXfXl4Z3iXiooKUMMPXGE77EtjCf+i9fWtBbppPx493+G6i7XfTB2XOMa3MkUqKl5LHbs4kc2WkbJEGmjhFAey2fKI0dQiE0FkLeyH5MNuK6VID85kR/MhkuvIHBYt3FvgmynZUJtHO2Rz0fuLojJF2MAtPoZ9DX/lnRlLKTMcVoeZSOQ8pcj/2JHLLJcp0o+HINLC5zJlGvKu7JUpAkdymYUoH8CnlCJf8BxE7tEX8hpu0EwpsyrvynqUT4dsMqXMfiTzPcp/4U9KEdiMZAZDtoIniQcf2f+oHWSask61sZhapMMsfssu7E/ZfamoeJ+8AGkaSqehB+jMAAAAAElFTkSuQmCC'

PL_ggear = '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'

PL_save = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJ/SURBVFiF7ZZLaBNRFIb/MxNNMklaMVUbsDY+U8GCaQRbX5GCrS7c1IKIIqJWRRBxVaS6cSMV3LvUSgm6cqkIgoitD2zRaqKgUqpWi32YNiGJNrkuNNjJTO7M5InQfzX35Mw5X849Z+4F5vUfiLR+lyTHnRV1DesXLauJAcD3N31uyeFgas6p5Kwwdy2IplT6OR5LJJ2eTZ/T68nh4IKx0MDWMDCVtpk4IBZJsj93e7evajlz1Zw2vrrVLazZ4NP4D0p9CA2hvv1cZXodvHtjbDQ0IMufDcZtsUpPm/afraxvPcQDLqgUicwmU6tott7e23nN5lrXUCoOVRiqqHLdbLsUsFkrnCUFAQAhc13XuCdaDhA1GAIxrQkrmpQwZZRyUojPk4hMY+rriOFEs4mYYRgSSOS+4N7Wxn79jBuGqV292TgMNLZqicen+vUthJQ9I2SaSidZZZYDJMzpmej4FwxdvyCuXOvJO9Hb1y/h7wokdcNkijGG5pbd7PzFrrynrOPIUU0f2Z6kAGJlHG9ZZZIAEWe0Dx88gMHBF7qDe70+9PQGcoNJASRQ9gY+fuIkJibGdQd3Oqt0+ypgGECMU5od/p2qdsYYwuEfyuCisduHojI8513Nfjzp79MdvLFpC+4/eJgbDADweqanN4BEPKE7uNli1nbKBsMA4tFEZiKIRCO6g9ttdsCVBwyvMqdPdZRum/5WJquzkcC5SDbHf2D4p3YxVb5TUUXKnskY72ePH9GVy915XxvevwtStREYAETCPxZpcTVq93UmR/MlAbDxmMHLVWYDC6IJjqU1BUDRJxkMAWy4/97M9LdP+g+gHDX5MbiQgKLdGudVNP0GqSGghmJ5ib8AAAAASUVORK5CYII='

PL_letter_beta = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJESURBVFiFxde7axRRGMbhRyMoRkMwCaKEqGihIGgREQRxLQRL0QjaxYA22up/EJsUFnYKYiE2ChY2GjFosIjaJV5AFG9o8IaExASva3HOkCXGzGzcE18Y5szuy57fvOeb78zWSaNFaMAP/Eo0x4xagC7cwFeU47kX2+cSpBUD+IIz6MRB9GBcSKhzLkDW4CXuYfU03+8TUhoXoJNpMR4JqdT/xTMPYxHoeEqYHozIv+MM5lwqkHahFo7m+BojSBmnUsFcxQPMz/HtroA5nAKkTUjlWAHv2QgyhqYUMN3CY9yY42vFaITpTgECg7ic41koNLwy+oWmWHM1Cy0+W6IO3McnTGAYN3EnglyXn+CstTdOsjFefzBZoFOPCawt+sOzia4UAR7G6wPxWI5vQjID2COkdgVbI1jNNYhLBXzNwhZQxokUIFm95DW6TH0R5nERc17Dmqodwl5zq6B/OJ7XY1kKmPfC5lhESyvGLbWGKeG2EH0RtVWMP1c514yqtl7q8V0AHxWWd0ZVk0xWL/0F/TtNto5rCqRZDUwpnt8V9B+qGNf8PWZIuLsNBbzt+Bn9vbUGaRHqpSy/ZhqExljGa6yoNUz2Uv0Gr4Rink4rTW6QzxRLsWqdxltsEt5jnmC/kFiTsCwn8VFI8MIMwP+sIVyM4y24688degTn4/fJlNXLkSmfrxIe313YjLqUEJk6hDtfl3qiIn2mJNTL07QoxWH6EnMUUlYvXf8bhPD4loU/98mVt0zb8ALP06PkqxFL5mqy352jjTacwzV2AAAAAElFTkSuQmCC'

PL_none = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADYSURBVFiF7dcxDsIwDAXQLydbT8ZSuBADDFyvaafuvQEHoCyAECpqnHwnS/5YpdFLq9gy0NJCyAh0NfaXrYWrYB4dehOIQ78K5ugDTw6HILgPDicm5GvfY+qLFFAyhA3KhrBANEguiA5JBZlBtCBzSCyoGGQPVBzyD1QN8gsKHteqkA/I4xwEj8HjVhfy+jKTx8Wil6kh719j1VzVkI3nZUB7t6YYKPb6moO0dcQMlFrQ6KDcykoDsUp8Nojda5JBVk1PDRqBLggWy7kpCJbouanWRNnSos0THO3FyyeQ5V8AAAAASUVORK5CYII='

PL_letter_lambda = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGOSURBVFiF7daxS1VRHAfwj08loUEho0UwCHF0UFpaHKKpoE38ByRaHRwcBMHFQIeGFkGKJtGt/6AgENwUQhcVTWjISMQeiTbcC+fcCPXK9R2I94ULD+7v3PPhnnfO79JMM+XSeo0x9zGBIdzDPuoVmkrlGQ5wnl8/MJIKA21YjEC/0JMS1IWfEWgiJQbeCpiNxBZPBMw5BlJiatiLMLMpMTAnYPZd77ioLIOKS/U4JQbWBcxiYotJAXOE2ykxvTiLQKMpMfBRwHxIbPFCwPyWNdFSqVWIuRv9bpOweU7J3sip8HZWU0Cmhd40pnjm9DcK0YL5fNKvsh3VgcMIM90oyOt8wmM8jO4tRJjtvPbGUhM+rE7x9K/7w4pL9eimIK14F0308h81NexENW8aAXl1Qe1MVPcdt6qGvI8mWHLxGdWn2B6eVwVpx3L04E+yXXNZPkdjVqrCxLtjE91XHBe3hzruVIH5kj/wGx6UGNep+EeeuWzAVT4R17CLcWyVwNRly3siW7IDiVpEM/9v/gCsEX9lSuTosQAAAABJRU5ErkJggg=='

PL_cake = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAR0SURBVFiF7ZdraBxVFMf/d3ZmZ9/ZdGfzaLLZbB6bx6a2NTaBgqRKbFobGqXio60Rq6KCIGi/VSKIgqDFR0UMfQktqa2xoJRoLVKwaluaSIyWhG5N3KQxsbubJdlNNrvz8kND6GYzuzNBPyj9f5s55577u3fOOXcucEf/ARGtA6wAV8Jyu6tp7rnVhOY40EZCdJQEWQzJfHwCfGhQDHeOxYNdUSD8r8BYgar7zd5TzSTXWyvCQMuioq9A6fADQ2Y/lCYu89HACzOA/5+CYe81V3Q/RbjNlYKgVwt/pu4ZnFndiEjvq5NC1H8uFL3xLIDkimHMQP4jJu+VXVjlYiVBLQcEikHHtpOIsrkAgPjYl3ykb9/gfCzwQAy4qTSOygSyy1x7dY9k0wQCAP1FTYsgAGB0tTHOps/WGGzuixYgTysMs8NUdWmnaHZooljQhfLt6QFz64izqdtjsLi+BcCqhrnH4vl8N3GUEsiaQcbt5Rjm1ixrY3Kqib3+7WrOWnxQFYwV8L6IvK2smDHXFHWhrC2j3eTaztKWis0OoDorTJPZe7JCEFVXze2aZ4zoczVn9Vu1YX8+rO6PM8JYAW4LsdesBAQALru3YJ4xZvWjbV4w5pIqK5CSkykwLta5s0YkyyaXGv3oSU9cJZk8j3GMKedhRZhaxvF8ps6aSX7nekzklKr2Nxa36ild7pOKMAVguBWRAPi+4iFN/jrWAehS50uB4QhjWAnItIHDr4UbNY8jFJsyH337gw5Epz0iwD86jU1ubTsDADEmUXDwqAKMAEkE1PNQehme1wJoeHAKPb3F+Clk1gSzySukFEvKZ4rIYkJtICZXQM0nfji3TYEiwFtrJ5Bv4DXBGOKp1ZICMyon/1IVxJWA7/A1WNfGFt/l6kW8s34CDKX+CImNIqIIMyyFDwlE8SAHANgaoqg7NgSDez7Ndpc9jleqgqpAaCJjqH/2A0WYkXjw+G80SZ9lQXltYdQcuA7aqtyLniiNoKUwmhVmHZWUf+kPdirCRIHweXFqKG0kBbhfHkdZRwCEzv4ZOuom4TFnPmiNA9LEDDClCAMA5+f8OwZp3WIkipVQ+eYICttVpRMAwExLeO/ucZhpaVm7j0nidNcf9y19nwYzDQyfkINnExQNxsmj9rAfjpbIUresKrUksc+XvgADJYM5x18MJXBtqW3ZphLgI90GJ9vefmzEbixVTKGsqrQmMJWkcXX6VqMlAJpG4rEjx0d9ANIST6l0+BN//t5w9pR9bsUkC9pbcxM+260FNYfj/KcfBcoALNvPFNttEpjt6Y0dKorm7/HVx00Uo/0XFAB0BGi0xRG8xEaPvBtwxwDF2s/Y+5PA7FcDsfcnBwo21pcQj6UwqfkGOtlvld943f5d5+mxdUkgY82rDm4DKve2FvU83jpX5mqcoSi98k5JPMGNK1ap6wvz8P5vxrfOANfVzLGSu7ZjQ3nO0y01lpeqykRHfp6g1+kIJQiyFAwyyaFREv66L3ng57HQ0aV95I7+F/obV6ZqAbjqw5cAAAAASUVORK5CYII='

PL_letter_alpha = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIQSURBVFiF7dZPiI1RGMfxzzWG8a+MEWJKWViIolkQ2bGxs7KxYzcZjZU1RSghiRILRUQWFmqKhX+zYGNhoRTNhkIRY8wYrsU505w5jHnf99rQ/dWt95z3+T3ne/68z7k01VRT/6FaGvS3YjnaMYJvDROV1HzsRT+GUI+/UTzBbo1Pckq1oAcf4+DDuIr9OIDHCdg9YbV+p1mY2QhIO+4kg93GsiymhtNJzH2/rlCnsILHqoIsxLNkkPOYNknsDLxOYnuy9/ti/7YqIG14aOJsW6fwnEjiBzLwfmGbK23T0STxD3QV8OxIPHVsjP2rY/tCFZA1wqc6lvRWQV9XBrMn9p+L7XVVYC5lSXcW9HVmviNYKdShu1VAFkTzWMJhob4U9aYwZ3Fd2Ob1VWC2ZwkflPC2Zd6nEeRKFRA4lCU8XMJbw/fM/xZLpjJOVi86snZ/CZixbU3VjTdVYfJa8qoEDHxNnvtwrYhpMpgXWftdSZiR5DlfpdIwfVm7s2C+FqECL076FhWF+ZMeGT+AvQXiu4zf3B8S78skZja2YF5ZmLUYjAnfY9UkcRuEy3NU2M5d2JTAjGBOjD0e+zaXhYGtEaSOL8K90ouDuIzn8d0gTpr4Fd5MgC4KdaaOG1VAxrRUmNGAibXjk3C2uoWqm2suzuBzjB/CKQ3+sUrVgRXCoawV9NSECU3/WxBNNdXUP6WfC06eXlsKD/8AAAAASUVORK5CYII='

PL_aback = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADfSURBVFiF7dc9TgJRFIbhB7WiM6FkGRrZgFbugB2QsAA3YucqINpALCilYiHCDqCYOxHNAMEZZqY4b3KTOfP75puTk1yCoH5uqnrRdcnnu3hHH4vyOuVEPrFNa9ykyHxPZI27EAmREAmRAjoHzvcwxUOqN3jEMtVD2dQtwwofp27q4dvxRBZ71/+73v5++KpAZorbdLzFyE8iF6VI5lmWDNlvfMV9HTLHemaCQao3eMJXqmvrmZwuZn73Ti0JnSPUyJxptVArJnEIhVCVQq3YHeTkCb00LZJT2Y4yCM5lB+3AbErAfggOAAAAAElFTkSuQmCC'

PL_letter_phi = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHuSURBVFiF7dbPi01hHMfxlzFSfiSjCVkoFpJkY8NKDZKSXxuU2FhNKRs2/gbZaZrUlCzM9k5MKYrFtfKrSUqmSFySbAxXBovnuTmmc8+5554jTd1Pnc6p7+f5Pu/7fb7P81x66mkea0EB73qswsMOvDtwOI75jBomCtO10Vq8xliObznG8SvluVoVTA0v4mTttAz1NiCt52hZkD0x0YEc3/Xoe44TwpIO4BCmY6xWFmYST3I8B+Nkt7A0Jb4FTaG6XWsDfmI4w7MILzElexnrmCkDczbCrMvwnMYPbM7JdQMfy8BMyN/KU7jWQa57uF0GZhqjGfGdQuU25eRZje+4UAbmi+xfPYoHHeS5LDTwmjIwDWEZ0tQv9MDFnBy7hZ4aKQMCN4UtezIl1jp/9mWMHxKug/fCmVNKx+KEX1OARmJsMGVcP84JfdLErrIg0Ie7/hzn93EqAjTwao5/Bc7gWfQ3cbwKkJYGhe2dvGNm4/uTcDFOCr01m/C8VVFF5moJLgm7K+sibFXjClb+C5CkBnDe3xX4JizXnRjLOq0r17YEyPYqE/d1MeZIfM/gUYUsXempUJV61YmLVmYjtsbvxxWzFIbZn/ju5I95IRWF2Zv4/u/90hD65QMWV518YUH/O+HgG8abqmF66mle6zfl24RM6mFhhwAAAABJRU5ErkJggg=='

PL_aup = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADrSURBVFiF7dZBSgMxAEDRpxURd5buxROI1Dso9jCuew/voJfwHm7dW4W60EJBNxbTQpqMM04U8iG7ZHgkE2ao1fpviP3SCBjhGY84KAk5xAwfX+MBg1KQ+wCyGnfYKwl5xaIEaBPygnNc4K1PUAyyqjdQCtIbKBcSA912BdoGGWAcjNPfBKV25Mj6tX7aWH/ZFSjnaFKYTkC570gOpjXoOlg4w1lkXi4GJngP5l7lYnZwI31rmmD43qFpLiQEHSfmNMXASVNIbj/BbG237QO6rGJiVUysiolVMbH+FKbN39fc+od02dJS+x99AjG9er5rk5JGAAAAAElFTkSuQmCC'

PL_plussign = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAC8SURBVFiF7ZVNCsJADEbjD4QsivEGrvQC3v8EvYBdeQNTugizKLgaEDETdBSHkrf7SGZ40HQCEATBAllVnu+IqM9BVc8AMP1Fhpk5pXTLGRH3IiKf3reukfk2IWMRMhZNyWydesfMm0J995yZ2WwWkRkK71DxnSGiCwAcSz1vMqjqySo29ZmakvHWgTszKaVrDoh4AIDRavZmxhvgqbRqXgzrGLvpF4SMRchYeL92ERGZiWh4zPVKQRAsjDscQzKutXkrIwAAAABJRU5ErkJggg=='

PL_pluspeak = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANsSURBVFiFzZfPbxtFFMc/szu76521HW/i/LDzg0ZBlQBVKKISFaVceqjEBVXqX0DpBSRuHOBf4MoF1AMSJy5IvSGi3IqaCxIKbQFRCRqkhFiOldi1dxPHOxxsS26bON7VFvOkObw333n7Wc+8t2PB6WYqpW4CCCHuNJvN3SHaF24Z13V1b7z9XzzQSDnfBCCSLk4TZhrYAT5ImiBNmMtSek+A9/8PMOfL5Xc2DMN6DcgmhTGBzCkDAK21fcq8HMg1p1S5kc+v/A68lQRGKqVuaq2/HCYSQqy7rvtcXGt9OwzDWz13xrb99tTU61v7+79dBn6IDRN3wRCbcpzJHcvyQuDVJAmkEOKO1vrhsxNaa1sIsQ4ghPhIa715guafAde37dyulHMyMUyvs57UXTP9rdFabwZBcPeMXAUps4bj+HkhjGWtIxs4igOTZjX5pplxhBDStv1t4OW4CdKEmZDScQCUmt8CXhkXjAeiA4YLkMst1YCVccEUTNM9EEIYANnsUgici5tkWGkfa61vw3NVc5L5luXV+47nLerUYQYa2lnm23buSd9RakYmgUlrm3wpc62+4zgFD3iJmNeJ1M6M4+SDviOEdE1TNYHZccD4llU4HAy47swOMbcqNRjHybcHA55X3hsXTMGyJo4HA9nsUmNcML7jFKLBgFLzsXtNnCvEDeAWsDkwHgJtYELKbDAoVqrUAZaTwGSAcIjuU9NUH1648PF6EFSW9vd/XT04eLQYhtVF0H8AZdvOrg8ucN1pg4S/zNfAm8CPwD3gLnC/N/+V5y2sXrr0+YaUar4rf08DW1pHj8Kw0qjX/3yQycw+dRW07bwDLNLtNXoUGAFw9ep3U51O/Yta7X5Urf40Wav9shKG1VmgWixefLy6+lnLMEwnzlsCem3txhtR1D4P7I2yQHbf4tiIIr9YKl2hVLoC8LjTOXzQbG63crlzRSFEXBAA4TiTlSDYXRgV5tRqMk0nm88vz/S/xEkskynuAfOj6tP+e/uUKVU6ABZG1UsAKV19dBSdpU0AMxcA7z7zvNwJ0m3gGwnQarW1lGbqMNPTF4Nm8++CabrXAYQwOkLIAARSunZfV6ls3Gs0/upW07Vr30/C4bep04xoURR9srZ2/efemakPV79gk9IQ0DvAh4dW+gcmhkVRF+ZfOZH1ZSIKSi8AAAAASUVORK5CYII='

PL_adown = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADqSURBVFiF7dUxCsIwGEDh11YQF8UziLOCqHfQwat4Ac/h5C28iODiEURBBwcFQRcDEUz7xzSpQh5kKE2aj1BaiMXsShzWZkBfu74DGzfO97WBhzaOrg9MXR9QZhFjKmJMRYypiDH1F5gU6HjYr2u7IAGWwBkY58yz/TdNgCuwsMHMtQ1OwLAEzAy4aXOnUkwdWGsLTSckxagTUfNWWL6rEpAE4wyRgoowpUHyQKPXvQwYaKPnEyIBfcobxBbkHSIFBYMUgYJDTKAL7x+0YBATqDKIqgEcNMi2KoiqCeyBHVCrEqJq8SOQWJCeU1J15Riy/08AAAAASUVORK5CYII='

PL_nonepeak = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOZSURBVFiFxZfdaxxVFMB/986duTsfu9lNdpNsPrYNEUGlxGDBoPSpD0VftFD8D0Tog28K+i/0TUVEQUQR9EXQJyH0TW0e1KbaKJJCbYqpLklsNt2PZLMzPuxuXcJmd2Y62gP3Yc45985v7j3n3DN8DyM/whQR5Tuwr8LJqPMGiZTgGoIPVmE6Cogt+FjCRJIwAKzB5FXBl2GA1kFfk3x6DZb6mEcA8b8ADQEpADXg5QeGGQY0BATgRaXcMnAlEZjjgEKAALxeKj33lZRmBfDivFseVTwBf1oBrwSCd1dheh10TfIhPm8vwMqAtSYdZ2ovk5n/DXgmEZheIATvVQWfhQABGLesXHNsbGEDeDYOjDrOYMHfh3AQQCGA2yHWGtN69I5pug3g8TgwfXfm/tEEXDIDXuoe2ZC1cpaVlp53QiUGczRGjsbQgLWySnlS69GMEHIOsB4I5rhgDQmUM4yUFkIoy8ptAo/EhhmWNSGARpTSGsBxpjeAx2LBhE3fAUAuiBZIGyCdLu0A85FhItSRQUBZw7B3hRASwPNKDWLc6LIGU/i8FQakF0gEXATmOqqcabqVrt11Z4M4MGoBbtIekeRJ+IP2gHZa3+vaHGdcxYHpW2diSE6pdK37oHXWBU4QsZ1ICiardabefRBC2YbhVInYfCW2M6aZ3e9V2Pb4HSIeVWIwWmeavQrXndp+WDBZ0xw57FV4XmnvYcHktM76vQrHmY5ca45tIfrIBdr97U894xegCYwo5dV7nR2n2OLfOhQJJgU0Bvi9YRjOxVOnXr1cr5dLd+/+uri7e2O20diahWAdmLIs73LvBNsuSGLuzEfA08C3tBvqb4DrHfv7rjuzuLR0aUUpp1P+XwiAjSDwbzQa5b1K5eZaKjVh9y5sWRkNzNKuNUEYGAFw9uwXY61W5Z2dnev+1tYPozs7P883GlsTwFY+f/rW4uKbNSkNHeUrgWB5+cJTvt98FNgOM0G1v+JQ+n4uXyyeoVg8A3Cr1dpfq1Y3a+n0ybwQIioIgNB6tFyv/zUTFubYbDIM7WUyc+PdmziOpFL5bSL8NieV2n3FcYq7wExYfwWglB0cHPjDfGPATNaB54+8L93HdRP4RAHUas1AKSNxmELhdL1avZ01DPs8gBCyJYSqg0Ap+37DXi6vXNnb+72dTefOfT0K+58nThNSfN9/bXn5/GonZiqDvf9jUUoK6ATw/r6ZfMBEEN9vw/wDPjwrLiuthOEAAAAASUVORK5CYII='

PL_infopeak = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOUSURBVFiFxZdNbBtFGIaf2Z3d8f7Y8TpOUjuJ2yhVxY8qCFSiAgKHVipCQrSoB+DCCVGQ4AQHOHPjhMSJEz8SoheuIEU9IIGaC1KBpgW1EjSVEmE5VmNjr53Uaw7rFAfZ8drdkFdajWbm23efnZ2ZbxYG61Hg2Qhx+645YAsIAHe/HyYH9G8D14Fvgb8j+I0BFaB9n1z3rQmgDrx+0CAAZ6V0isDlUQ20Pu068CrwLlCI6HUsn39mWdOMhxlxfvWCEcBF4DHgNLAM2BG8Dtl2vppKzf8OPBkXzEtAmXBUbgM54EgEr0nT9LbHxx9ZBZ4aBabXanobuNDpewEoAjcieI0rlVk3DKcBPDQKTK+ReQX4DXgOmAK+Ilzig+SZZlJz3cMyTpj1Tvlap/w8oldaSldTKpMSQpsDzDhgADKEn+hn4ErH2Bjg5el6QgkhpGl6a8DRuGBeBhT/jsoXwNMDvMakVArAtqdXgQfjgjndKb8GDgMPAN/v4eOAaIFmASSThTIwHxfMCtACniAclTcIk2U/pXXd2hRCaACuW2gQbTvYpX6J8kOgBCwCbwLXBvh4huFUdiqOM9uOE6YJfDyEj2eayXtZ3bYn5Sgw/T7TsPKkTNZ3KkqlHcK5Jg4CJq1Uyt+pCCEtXbdrhJvm/w7jGUa62d1gWZPrDPmpYoNRKrUrZThOfuOgYNKGMXa3u8F1C9WDgvGUSu/ah2x7eui9ZtCBvFvnCc+3v3Rd1wgz+piUrt8dbNu5FuHfxdAwCaCxR9z7um6/dfz4O5d8v1i4c+f6wubmzdlGozQL7RtA3jTdS903WNaExogj8xnh1v8j4YH6B+Bqp/9Tx5lZOHnyo2Up7ekw/MU2sNpuBzcbjWK1UvljJZGYsrqNTTOlgFnCvSbSr4sAOHXqm/FWq/JJuXw1KJV+ypTLv843GqUpoJTNnri1sPBBXdN0NcxbAu2lpfOPB8H2MWAjyg0yfIu7WhB42VxukVxuEeBWq9VcqdXW6snkkawQYlgQAKFUpuj7f81Ehem7mnRduanU3OROJh5FiUR2A5iOGh/X0u4p285tAjNR4yWAlFZ7a2uv48qoMId84Pn/PC/ZI3QN+FIC1OvbbSn12GEmJk74tdrttK5b5wCE0FpCSB8EUlr3DuzF4vLlavXPcDWdOfNdBpoXY6eJqCAI3ltaOnelM2cqe0fvs6TUBHQmcLNpxD9hhlAQhDD/ABnC0XWgXWxkAAAAAElFTkSuQmCC'

PL_peak = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALZSURBVFiF7Ze7ixNRFIe/O3NnbuaRbJLNPpJ96LKyoLLIoqAo2lgINir4L9hY2Fnov2BrZSVY2VgLi52y2yiiqyIK6iorhmxwE5OZGDNjkY0En8kwOo0/mOKcOffMd+eeufcM/Ne/0Qggog7WYwQZA94BZeBBjHkj6bSUThlYiZpAixFmoVQ6tqppxl7ATRpm0rZL9Uxm/jlwOGmYcdPMtUdH960DR6IkkDHCjCqVf28Yjg/sSRomZ5rpD1JOyqgwcS5TVkpXUyqfEUKbA8wkYXK6nlJCCGmauQ1gV5IwI1IqBWDbU+vA7qRgHBAd0CyAdHq2CswnBZPVdWtLCKEBuO6sD+xMCiZnGE6tZzjOTJgojGmmP/UM2x6XicJImW72DKWyDrCDIduJ2GpGqYzXM4SQlq7bDWAiCZicYWRb/Q7LGn/PkEsVG4xSmXa/w3FKm0nBZA1j5Eu/w3Vn60nB5JTKBv0O254aeq8Z5tQ+C5wDHvVdT4E2MCKl6/UH23axA8xFgUkB/m/iLum6fX5x8cIdzyvPfvz4bGlr6+WM71dmIHwBlEzTvdM/wLLGNCK+mevAQeAe3Yb6LrC2ff+a40wvHTp0ZVVKe6obfioE1sMweOn75Xqt9upJKjVh9Sc2zYwCZujuNeEgMALg+PFbo51O7Wq1uhZUKvfz1erjed+vTACVQuHAm6Wly01N09UwswTC5eWz+4OgvQBsDjJAdmfxRQuCXKFYPEqxeBTgTafTetJobDTT6Z0FIcSwIABCqXzZ8z5MDwrzy69J15WbycyN907iKEqlCpvA1KDxcTZXP8i2i1vA9KDxEkBKK/z8OfhTbASYSQ84+d3z0j8J3QBuSIBmsx1KGedvd1djYwe8RuNtVtetMwBCaB0hpAcCKa1vDXu5vLpSr7/ufk0nTtzOQ+tm7DQDKgiCi8vLZx5u10zt99F/WVJqArYLuNUy4i+YIRQEXZivBiuva3NKy68AAAAASUVORK5CYII='

PL_gearpeak = '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'

PL_curve = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGXSURBVFiF7ZK/a1VBEEa/ucnOt89HFEFQIZ2BCKKv0dcKQQh2doqFIEha/4H0CsFCbIKNYGUrghCrYGFICm20EPyFooQglsndWXljIaYIIZjrS27hnmKLZeZwigEKhUKh0A6y9cOBTiavO3BRRI7DvQbwGiLLoa4fC/BjX2JqcrICngrwcuD+SNw/yehoxweD0xA5D/dpARZRVXNhY+PFXkXBgYNGfrQYr+04E+OMkR8SuWAh9PckJsV4y8j7fzPrQLAYb2Tyi5HzDhweWogDYuRqTZ7Y5d4hI+9l8mtSvTqUmKR60sj3TfcthL6Rr4x8VpMTTT3V77c6C5HlphLNeSWkdE6AhQpYyqqzDmijmMr9KNy/NY0BAAF+hpTu5JGRHkR6mXyTY7ywa1FSvZxUr/xLzDbOS0Z+NtUHPjZ2ZJjuRjhwIMV428g1I2/6n7NoEwuhZ6pLRj5Pqqfa7oEDlcU4Y6rfjbzrQLftJni3e8xUHxr5LpPTbfcAAHKMU0a+TeST9U5nvO2ezQNPqmfabikUCoX/m1/B5YvYncRCkgAAAABJRU5ErkJggg=='

PL_aforward = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAC8SURBVFiF7Ze7DcIwEECfERI7MAC7QE3LSnT8imSEIBrECLQp2YQCCRpHWE6InBBxJ3FPusIn2X4++wqDYcgw8iGOA3ZAjgKhPfD0kSEsNAfugZB4hUzIhIYWUtdl4kKLLkKuIbcCpl9KlMAlECqAiR+fgCXwSFnoyvskfeMQrRlX6AaM441/dYdnYB2MZ8AmZaJYZWoJb3xMsW6hjER6v5kh6dRNJmIiJmIiH1D1O3DAVoNIhZofpfFfvAA6gX3GFj6u5AAAAABJRU5ErkJggg=='

PL_florish = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGlSURBVFiF7ddPSxVRHMbxTym0KOhmpkibdoIILYKCkNr4FnoX7X0LbVtptXMpCO4talctIi4E9QpcSGqSCGE5LuYI49yZO2fuzC2r+8BZHOac53zPv9/5DSP9B5rHZqbMNzEbbwjTwWKuPrAuNmNpVyOYMpXB3Nb8PJVpPPhHwUzgFT45ezjb0AI+4DUmYzqsIAnlGKuY7mOeZMpCSbsJPMWvTNvlKpAOtnMDJNjDY4zVhBkL/fYKPLdFhIIrWML3AoOPuB8JcwfvCzwO8SQGJKubeIajnNnp1k2VwFzTuyVJqK/hVh2IvOawoXeGO86eryTUdwrabgSf1nQPbwoG6lfe4WGbEHktolsB8RmPcGGYIKe6JH2li0A2w/ffonOxMnfVPzNv8aBNiFmsS6/0ILfpOPSfbQIxKQ1OPwrMB4kzR9K4NVMH4rI0Au/rXfY2IvBBmOTVKpAOtgoMhvE2bYl4El7o3ZJhvNrPq0DgOr7ii+p8JhYm276LXdyIgSE+06sLQ59Mr2zAboTpoPpZ5v9XJOR/ROcKpunvyDe8zNVH+rd1Agdl42R+VmOAAAAAAElFTkSuQmCC'

PL_name = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJQSURBVFiF7dNBaFxVFAbg775JqBoL1baGJpPJNLZaUu2mCxVpN0IFKUVcWBBBaDXToiIIUgQXgwu3gtQ2M4kGglIR6cJVREQKWosgSBERXOgzaTBYXFhEEvvmuMiMTIOuXfi+3X+475x77+NSKpVKpVKpVPofeJ9Kq25PkOaHDbWq7m2S9a95626bz9RM3FAbM3J61FaYGbdzZlQVWiO2TddMbpzzxi6bzo65p7XfYH899Yd2zQuRmYwwlLiUks0RJhq5Z6A95khkDuEiTkXm+U3h8lp4Fk+mcK6TfJOFU53MQgqLiX3Bz43ca9CqOylMYgGP9nqz4dQyK8K1RN7InY5wSah1m+yJzOu/F16ayp3DSFr17WrH/krmHeyohNkTufORWUlhsZGbxde9Hu26h4XnBge9msIqVm4c32fqR++lcKDDB91rOyyzAMIxfP7ikj9m1q/+amPZ1RM/+aTomAi+Or5ouUkm3F8pnIcOh1PyEUQ4iu+u/+lQUfFbI/fKv27mze1ujaS+NXd5fb4jCh+2xj2BbZIvuvWHcHG67iikcACfwo6qvbjy9JJf5+puShwcGPTZ9LjHumsXpnLvnvzBl9NVu/vnD/SHys3uk1x4nKK5vtEikkcqmQtF4Rc81R63GhyM9d9Zg0geSEkTYsCDKXwMxXW3qLiytuZYSuZTx2In83J73FIn7MtYxvf+yfywoTM1t/Xy27tsn9lpuJfP3umO3ktpT7ir2T1MrwazVbfPDxv6+5uq0bm6Lb08V7elXbN340sqlUql0n/pL8iaxspvFtImAAAAAElFTkSuQmCC'

PL_florishname = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVFiF7dZfiJRVGMfxz3nHzWpdsPyzqbuz42ataArlRUm4N8FKIRJdaEQUWO0qFVEQEnSxCHUbhenu7NrGUhgRXlQXGxZhlFlQhERIXti0qyXZH8qIVWdOF/NOOw6rloxbwX5hmHnOe875/eY85zzn5fxsQDcaLtBvSjiEiFlTIZZMhcjfpWJmDZr+wbgMuupvh/n4GcdwX82zydK0Cp+ghM56m7kGL6OYCu9FxyRm5mIwNRHxLlbU20yFFXg7FRrHMziSxo/jx/T35y5RiiZjNT5Ihas/BeVjnpkqIxUW4GCVkRO4aapNNGEbTqYmTld9n8EutFxqEw3KKfguFf8aa01s4BsxYmI/PY/Zl8JIBw6nQiex1UT5rz3ad+OoidTdXm8zl6Wib6Gt5tlkdaYRvcq1qbZ/XTjXkp/vbqp7mirXwS8XMfZixpyX/9RFeSFa0e5/Zrr+vE6mP2dpJAw3a+xvsaK3ZlV2dWjakdV+VlurhdsXmQMDbRYPLCoXxv6F5vZlLavVeWGJmTtb3dC/6uw3yFAd5LMei4llMWoMHAhBU4zaewoegnyr9THRhf3YGhOPzowOnooexr0h2l0KvkyiraXESIhGAysj3/cUPAv9OVtEy5SL6J2VuandC4njot8ChZ6C7TE6IMqmkyyNied+L3qyu2A3FoZxX42XrMokXsGCTDS4uWBPTBwP0WhPwSC+qMyRz1kreqShwbYQjeP42fJVdH/jtRCtKfFGumzrJEZAtAkfPTHmj4Hy0p/oOebE5m+9Vyxpj3z2wKhjvSSiWzJFe6DEuhC8AzHaiENnTusqZvzaU/D0Oc28OM+sGOTmFBws61uv6M3+NvdgruDjtP027O/L2QghWoP3YUGL5Tj64JifhnIuD3TOaPBhX5u70r4j3QWvbjni074W11Xrz6gOMle4WbBvA8XestFiDO7IJPYVi37A/fk245HOWE5nFmKwOgS9EGe4NUR7oXjGlTKOnjplUwiGQ8loKfFUvs1YKVqZlF91D5uM4WaNO7KuqsQvLTFvYLHmSrzzWvMrJyXf7vre9M9U2mCwxdXDzRr/GtNi0VBu4uoYypmdz1pee5KmmWaaaab5N/kTfnQOjEC2Ex4AAAAASUVORK5CYII='

PL_neutronflux = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAN6SURBVFiF7ZZdaFtlGMd/J8k5+WoTY9qGtLOxZZsuk1Zpa7u5oYyKRXEoouIHDJyCl+KdyIQhDMfAO8WbIYhYEHEqGziq1drSakunBdttpavNktrmazVpm/Sc9JzjRZdx+mVPemt+8Fw87/t/n/fP+z7nA8qUKVPmf4QAPL/NnApkDfmfwPy6tSIPWySxA0Hwo+tpTSkMUWAE0Hdr5stt5qyAx5CfAX4CsDqtL+JxdjpaA9edL4SvuTpDC7kfIr5898SBld/j+8nmL6t59avdmClJb6mUzri6Gmf9n3SNbidKv/F9a65nOqgtKu9SwilZS3FicUvveF5vuuE7d2z8v3Su43v/ZlHWlPHUk7qiDpiuD9zaEHHghiEuAyBxUDrgd3tPHZkyU9h76siUtNdXiUTYrBkB8G0YE4EKQ64AMctd9g/rfnvtgqXKvgrQdOlqwz2jsUPDrz70Xf1wrD44mWzJ1Hmu959sHy4u1OKL4uzhz5/R/pHfNmPGAixsiAQwbYgYYBO8drFoxLaqCQ0DM11WWa3oPNv3kXd+MTh4ouXre4dunm4YnAncKR6oLAheu4TJdrABHxjyLGuPtJFvgRWxzpMqDtSNxKoS99cM7hmbfXa5pqK/962jP7oyeRFNlwRdWNewYtCTUiPZWiBa6sm4Wbs2Y4iAz+p3LhcXRQ7VJ4dOtIw5snJzrCk4ANDa/UfbqmiNTT8SShg3sFY7lwD/TkZg7WTOmtCF1GTe2Efs65sOouvuiafDkwBV0+mjuZqKXw6fH26NNtf+FW3dkwZQE8seILVFzU1YgEZD+Nl8MpVArDCXrVrnbjTarLjtV1YcNg3AvqQ0LtRWTlZPpTuKRgAK80t3A3NmzNiAHkPuvW3QyCjwuJ6RFS0l24pNnAl6o+mQ79Oi6FrXfeeCY3Nt/W+23xnT4ouinpFlNvfhlph/A0uEHQ8EXgn0vHTR7JK5zu7jynj8MxSumtGbfwOrJLWlQhtZWXI8Wn9rJ3nmdP/+fG/EpufVb8xuIbD+mgBygLyFtg/42OKR3nceCyWrzj81vIUGgMTJi+1y702/llXeo4RvkwB0bhhzAfYttDPACIDVaX0Oj/0J6cHglPvl8ITrsdBC7ueIb/mL8YPKlfl9LMmX1Lx6wawJo5ndI9JmsYsdIFSDntTkwq+3/2fKlClTpsxO/AvA7EHKfojHTgAAAABJRU5ErkJggg=='

PL_neutron = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAL6SURBVFiF7ZZLTBNRFIbPtJ2ZvmttSy2URwmgFANGioBCMEpCQyIujDHgAhM1cacrE2JYkBgTw8KViRtjwkJcgQuIEiIRIcWIEAy2mFLLqwj0AZa+mJnOjAstwQVyC+ycb3dO/nPOPyc3dy6AgICAwH8EdqBaHM6ICLwKMEwHPB/iaGYMGBgHAH4/DcX7KpKJr4l0irvy2myF+n71rO7Jxa+SYkMCi7E2LsLcEHEsySd5V7p9090MJlIRj+T2/GXdM/vEbqLQ7be2+KDXxEXoB5DGltLajEhBtKlvlX7Xdl5w/ksnbyr4ARGKo53BRp5mR5H7IzshoIQo1ik07TUeFLmmvcZDFGhVQIAVdQTyZkQqsu3Ym+Y+TC7hAABK+2cstldTjT+zNXPFA+6C8p5pu9ETlC6eNi+nauQNeXPRLlcLv8UOIM1A9CLBNCQu0pNJAABJksMso/N2McUq6x8PP9WsRkyO1vKevLHFDotj3rjd3KhiMA1JoH40qhkznqUOpoKscZ/efyLDQSbozFiGcmToXu27rSMyGjiewHjsrwOLm9RBAMg8TDNasU4WSwUL1TmBsdbyL9JNqsxXahoFALB1T1UkcbHPey7Xv7NQbJBFAUB3mGbW2UBCuTNROOw1Ac8rXJesbgAAvTdUG89Qfjj7/JMt+7Nvezjrj6kBIAgIoJrxMSub+p2J3ImlMlpBTm5Jfx9oMkrnb2Sq3AZPqGrJZg6ldMxq9CgArBymGZYPUzQXpCSpRNikWXLXWV6k4m/2453KYNw8cqdyO8etRXA+TFEAwKIMQb+BCbBKTxqvGweb+1BLVuq7m2jnWhfQMIOiR7+BWQhwUaYCNilCWpezvpc83DFSlBhakPAJ9jXqiLR+BzzNOuiZ4FVm2q+VXy5a3k3nv9lXGe+dNXMR+mE6/ff1hBDLxFdATTYQp0weRYvVJT+fuxF/v6CNvXSW0JOrhRCl+tkE25tu34O8ZwBwqBCReBUAZgDgAxzFfPzznhEQEBAQ2Itf0/MXiol/eWMAAAAASUVORK5CYII='

PL_list = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABUSURBVFiF7dWxDcAgDAXRowxb0Gf/SdIzRkooWIAIC6HonuQO2b+wDEiSRJp4cwFPwKwbeFfDJKAEhKlAC+gjfZIZi7daeXdw/d9RF/iov0mSJKADj/0ZCFf/9fwAAAAASUVORK5CYII='

PL_letter_n = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAG9SURBVFiF7da/jw1RGMbxz7VClmI1NshWBLudRiQiIdGq2KBRKGQVOgqNSsM/oCCRoEBWQkEkNpvYKCQKla2EBCEkW7ASxI9cxZmb++a69+yMjMp8m/ueOc+b55mZM+dcGhoaGhr+YAK3MY872NMzvwXn8BDPMIPz2FB3kDG8wyxuoY1f2IcWzuA7XuAiLuB9oVvA1jrD3JTudgVWF0HaeIpL+IgjPT3bC01beqK1sLEwnyrGLXwLRovY0advKIReqCvMKfzA2mI8HoK0cXRA36qg+VRXmAfSouwwFUxmM33bgm6+rNnyJeaP43MY7w71dKZvb6jnyoapylvdO57I6O4H3f5/EWRzMPggLeZ+rNFd5F8xUtZgWYUw8RXNFWb9mMTKor6nwgKuEmZXT5hBHA71jVCPYlMFvyzPdV/T+ADNevzU/aSHw9wT3K0jyLoQ5HVGdzLoroXrnf2pd6f+Kw4Ek8sZ3dWgmwzXr+ONtBkOZKl9psPOUM9kdC9D/ar4PYaDOIQvJf2yPNY9rUczujHpvOockNPSGjpdxmSoZJgRaf84i0cZ3aL0N2NYOmRbOIErJX0aGhoa/h9+AxFWb8BOWOX9AAAAAElFTkSuQmCC'

PL_check = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALtSURBVFiF7dVfSFNRHAfwr9u93j9zTuc2nZvpcEpZKBhmKtVLRWkUIYlGERY9FREhSAQ9SESFhPUQPhSEPdRLJpL0R9GQSrS/+qCRmqbZdF6n+7+7Te1pICW66zYvgd+3c+4953z4nXPPBTaykf8gBIOi5fol6w1RKKNLSQlxaL3X/SeMktxJy4gBALSoEJpGWjQrnZFrmEJRIQBi1TqmV6Vj7okNIbXpbEuyke3CKtsT6QMcpdEzD7QGVu+cXbgCwCMaRqWlaguPJm7+PejstM542iO51opJSKYuHDmf+jY9R9EGgAlmTEQqE59ElWTvSihz2/wSbtxzE4BbFIxMFp1t2Cavzt2rmu97M9trtfCt4V4juDDQZeTGdtY05bWl58g7AMQIGR7Oysg3pcY0HL+c4XvfPMXOmrw3ADiETECECSLVprEN5dVGwu2Yx5d2rs9i5l8JnWTFylAyYr9cJV31p6ZOoe+XXjIkxKpIb+PdkcWpUVeVUAiwSmV4p78bC5LvYJALNyaWhejoawfPbDImGVhPV/MUazZ5rkPg9gSy2pmxxmnod9ok9iEA8u+HykT6dMHhpN2Z2xUem8VHfmrlvtkm+Za1QILBYG7OW5+ZF6dS65napf0KJbUvqyi+ckexmgeAZ3UjmBx1XVwrJCgMb/W3moacXH6xOi9eQ58AgBhl9NaULWzNgUq9BwB6Xprp6TF3HQB7RDEAFi1T3r6sAqVPn8meYxgyX5NC1ZdVGZ0A4LD4yJ6W6eG5GW9TKBAAkAbzksvu70fUYnnJ2VT3+KCjoqLaaCcpyQIAPLn1g/jZbz8FgA8VE+w982tswDlN0hL25NWMyUDnx9fTLDfhug3AGioEEHADz3F84/BXGxtoO61+ovu5echi8j4NB0QQxj7je9zzwuwLtBvvjEhNI6F9PWvGAPByE+5h3jUv/dzGMeYxVz2A2XBiBIWUIWfPMe0HrYF5JBpiaRg50QFAKbYjEEpswEZEzR8Vy/CzMTHLRwAAAABJRU5ErkJggg=='

PL_peak_list = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMUSURBVFiFzZfLj9tUFIe/a1/7xq+Mk8k8knnQ0aBKFFVoxEhUoLLpohIbqNQ/gA0bFuxYwL/AllVXSF2xYY0YVWyoOhskBG0pohJ0kKZqlESZhMR209gs3CCLR4ldl/QneXGuzjn+ru+59x7DcyQBeMDXBePfBW6WCSMAv2D8EHiUsZeAAZA8JddTawUYA+8tGgTgHSmdNnCjaAKtRJjTrdabh5pmvAy4RRJIyivgddtuDavV3Z/6/TuvA18VgRkC+wVhslo1zdpkefmVo37/zhtFYcrSslL1+4bhhMCZIgnKhKmZpvdAynVZFKbMAvaldDWl6lUhtB3AzJugzAKu6XpFCSGkadaOo6j7InA7L0xZBbwkpVIAtr1xFEXdl/LClLVMDogpaBaA5233gN28ScqC8XXdOhFCaACuux0CpxYFUzMMZzAzHGcrWSiMaXq/zwzbXpULhZHSG88MpXwHeIG0PfnfYXylqsHMEEJaum6PgLVFwNQMw4+yA5a1ep+cS1UajFLVSXbAcVrdRcH4hrGUbT9x3e3homBqSvlxdsC2N3KfNXlu7cuk/e33mec2MAGWpHSDrLNtN6fAThGYChA+we8jXbffP3v2g2tB0N7u93/cOzm5uxWGnS1IfgZapuleywZY1opGwS/zGfAacJ20of6G9DaWwBXH2dw7d+6TQyntjdT97QQ4SpL4bhi2h4PBL7cqlTUrm9g0qwrYIj1r5vp1EQAXLnyxPJ0OPu31bsadzrf1Xu+H3TDsrAGdRmP/3t7ex2NN01WeWQLJwcHlV+N4chrozhMg01k80uK41mg2z9Nsnge4N51Gt0aj47HnnWoIIfKCAAil6u0geLA5L8y/7iZdV261urM6u4mLqFJpdIGNef3LbDv/JttungCb8/pLACmt5OHD+L98C8CsB8Bbf3mf9w+ux8BVCTAeTxIp9dJhVlb2g9HoN1/XrUsAQmhTIWQAAimtPxv2dvvwxnD4a7qbLl78sg7R56XTzKk4jj88OLj03eOaGTzZ+xlLSk3A4wKOIqP8gsmhOE5h/gCEici9hcFvbQAAAABJRU5ErkJggg=='

PL_neutron_flux2 = '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'

PL_pluscurve = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIPSURBVFiF7ZQ9a1RBFIbfuXvvvDP3uhE/0ATsDCj4sQgasLEQIdjZGSwEQYKdf8DCQlAUhWAjaRQrWxGFWImCIRYRRAvFLxRFRSzNnTPLHgtBJBsXd83uKu5TnjPnnaeYMxX0kGq1uqZSqZxK03RdvV5/1Mu7myA56r1X7/21pfpJr4VaMZD5FWm3gouiGFbVYz/XVHU1ABhjtuZ5fnJR75nplkye5ztUdb6NkZtdkwEwlOf5nkW1EVWdBnDPGHN2Ue9jF12a+adWu+kBK+AjeUSB/caYEaiWAB7DmLmsLK8b4EtPZEpyUwRuGWBeVa+g0Xht0tRro7ENwHgkL0TgDpLkXLawcL9bUlBgSMhX4tzhlmecmxTyZSBnJMvG2rxmhfd+wnu/u+Wp4NxpIad/UzwT545G8q2QlxRY1aZUy3Aj5IeS3Njm3EohL0byXbD20LLIBGs3C/mi03nJsjEhHwp5uyRHO835vtpJshPGzHUaYmN8kIWwywAzCTAbrT2hgO1IJlFdD9X3ncoAgAHqWQjnY6VSgzG1SD6Jzu1rOyhYezBYO/EnMktkHhDyjVh7WavVtcuZ3REK5MG5M0J+EvK4/g0/vmRZTaydFfJusHZLv32gQCLOTYq1n4WcUqDotxO0KIbF2qtCPo/keL99AADRub1CPg3kja/eb+i3z48HHqzd3m+XAQMGDPi/+QaAH61RKrFLTwAAAABJRU5ErkJggg=='

PL_nonecurve = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJHSURBVFiF7ZY9aBRBGIbfmXPmnb2QSEDQiMWJERXBA40p1EoEsRMsFAtBlICNgpDOzkILA4qIYiNYCRYiVrG0CZFLLpFYiEbBP0REO7n5Jt5YhAS93OV+zGUL7yn3m/fbh5n9dlehTUwDmwPwcQAIDaztAtCr2yVTBqLRuP4a4HLrCkA2alz7BZTb5QIAKAK5aY1btYQKQHZK4/YksLGtIvWEVl2kllBqIpVCL4DeVEUWmAB2TCnMFIFctXrbpqmSApDNaJyfizijNYbrTVlbRf48mnpTtmoiC1QTUpXhCCSBPB2BI0qpPsRYAjADpcZNqfRYAd+bEVmjMVIu4/Ju4HNlvQjktMZwtoyLWwH/V7FEbhNyNpAPvbXHxJg9IUkOCHlOnHsg5I9APgpJsq/VHakmtOTIItAj5Dtx7lStYAR6xLkhId96clSMGVzmJvsLQF89aQCYAPongfziBe/cFSHvNhKOgBHnzgbyg5B3ItDbSK4hIqCE/FIitzSZWyvkzUB+8taeXBEZb+12IWdbzYsxg0IWhXxaIvtb7TP/0tN6AEqNt9rEhvDceL9XAaMaGAvWXoqAbUlGx7geMS4ZvWZQwJzxfiRkMnkolQ/ky+DcoaYbeWuPe2tP/ItMlZ5HhXwv1t6L3d3rVrJ3S0Qg6527KuRXIS/EVfwW1kSMyYu1Y0I+89buTNsHEdDi3JBY+03IG3H+Jzxlqa6uDWLtfSHfBPJw2j4AgODcQSFfefLJzyTZlLbP4gPurd2VtkuHDh06/N/8BkJp14gAdAfWAAAAAElFTkSuQmCC'

PL_antenna = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANZSURBVFiF7ddbiJZFGAfw33ZwO2tbW1lkq5sSERQY2o2UUQRRUbSKSVRUtxJREAR1ER0oL6SbiqCgLowOVBcFQZloFNlSguiqHWwjcDtp6WZufpFdPPO6s+P3uuy3XwtBf3gZvv88M/P/Zp7DDP/jP4CO1N6DSzCCAxjCt9iBzdg/lWK+w9k1NgfwOT7G2/gMB/9NMTNxYfo9A2dgDuZiAU7PxgxiNZ4TOzil6MAFWIGPxE418Duex+ypFpSjByux26ioR3FSuxaYj2XowzXieKaNM2Y6HsaeJGoHLm+HmKE0Yf6NoB+rcO0RxM3Cq9mYR3BMKyIqB74eC9GJLnEU83BWZrsbr+NpfNVkrj48KwLgAyzFcCui6tCD2/AW9ol//ydeQ28T+16Rlxr4BN3tFJOjCw/ge2Mdt7OwOw3rk02/8K0J4QSR9E41enR1OB4P4rdswXlNbNak/jU4biJiBow67jA24UXcIf5pM8zCh2nMLlxV9J8isnUDL0xEzFPYINL+j8ZG1R94E4uajDtaRE9lt6zoP1Nk7AZun4igHN24Ac/gh0zYe6JslLhTFNP9uK7oW5T4PTi/VUEVpomI2pIE7cN9OKqwu1WUir24tOh7KI19d7JiKhybRAynid8Qjprj3tT3tQiGCp1G/fLmdgmCi7AtTbwWJxb9r6S+1QV/deIHhK+1Dd34NE3+jti1CtNFnWqIOpejir4ldRMvwUsinHelb1Pi+tTXpBki+hp4vOi7yegu5HWq2p3+OjEj43wDuLFm7Gz8LBx3cdH3flp4ecFvTPzFrYipviccHkFwS5p8s7G7uDjxGwv7+xP/5GTEjOCxZhOI/NPA3QVfZeA81M8RxfabyYoZEcmwxIK06HZjd29F4lcV9v2JnzNZMds0d+q1aYErMm6m8Kfthe3KZHtXTjbzgfHQIy5jJV5O7dKMG8JWsQPnZfz61F42WTEcXn+IVH8QVxb8utQuzLitqZ3bDjHzm3A/iePoFe+uIy08KI5vzD2oVTF1r88tqc0X+TK1ecX+CztFJj90U2xVzN81/GBqz824X1LbVdjuTe2h91arYuqetYctkHEnF7bDpW1L7xt8UcNvEDfFPJR3ipJSZuJ14ib4a0V0iNwxUSwXV9G24h/ybwkIYxulfQAAAABJRU5ErkJggg=='

PL_antenna2 = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALrSURBVFiF7dZLqJVVFAfw3/VBXDVL0YuBiij4Nk3QykwQByEYahHkA0eCDhQaCA6KBncgSAWF4ExoEok2COzlJKwGig7CnvhO5Eo+Ss3Ue+/pYoO1D+fz8zue8x3DJucPe/LttdZe33//19qLNtooh44W/cbhGUzGaHSigr/wG37EGQw8fIrFeBbv4FQ6uNH6HR9iFYY0c0AjZjqwGtuwIH0bwC/4HidxRTAyAsMxDbOSfWfyuYDdad1uJrE8nsY3an/6LTaiq0n/YXgZH+NOinEWa8okMQhvZgJ8iUVlAhRgInZlYu7DqEZOT+JAcjiHVxrYj8ZUzMcMIewHYZYa26cxu55hF44lw88xpsBmFDZgv6iaIuFeSv5bML4gxhB0o0/obXHeYCx+SsHeE1eVxQS8j+uZQ+/gBxwUuvgKR3EzZ/NRYiSPV/G3EP8L1Y+d+C45v51zGIrtmSQu4QMsVauUPAaLSupWY69XaObxnO1S3MBlzIQ9GUayGC8qqJKM3xDlWwZDsU5UUQW/imaZxQrB4BGClf3uvZrZojdUxBU0W871MAzvol+wvDy3vxZvwWO5ROaJ6+jF1oLAHaIbd+MzHBfN72d8gR140f26I1i4JhrfykZ/MAHncQuv5fYGiUqqCr3ROoFN7n8KFoin4h7hFuGgoHJt7vt0HE6H9Ce7zYLFJ5LNSNG1N4pe1Zfsjye7LJ4Twv36QcnsFELNYpWgtoJPFZdpEaaIsu4XJbw+t78ELzUZC1EJvSmZ18s4ZrBCXEu/YLMlLBNC68HcOjZzRLf9U3TTvZhUYDdVtP8+wXRpHMEf6r8fqwVrFfyTVnXAKhLmFFzEJ60ksxLP19nrwlW17lpdVdGeUdyhJ4mK/U+xWQxZfblkeoU2BsQsUwpFjakZVF/juwV7d0VjLM1Aq8n0pAOLxtaOlFBPi7FL4ylRQfU0c17Mw48MazKHZ6vpthgNHjkW4pAYAW6Jh3P6/5FIG220kcW/T7HfMglTf34AAAAASUVORK5CYII='

PL_frame = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADmSURBVFiF7dY7CsJAFIXhc2M0PjABC21EsFHBSrRyE4KrcBOWuhdBe2uXIIJY2ItgERAfRCZWwhRe0CSYCPeHwBCGmY9MMQGk95E2PgIoAVAADiHWbAK4hkEBwAWAH8FTCArQv4xbtk17PKjAStM56ILDrjPPmPT4dL7vGwtntF4CgKm931smddrVrOrV85ugGACtr2aTWr2GRohNI08wXILhEgyXYLgEwyUYLh1zI8LdIFJxYfRfiP5u2qh5ZMziwiT2mGJPMFyC4RIMl2C4EoXR7ya4udSpeFOTXwI8H9tf7vefPQHJLDNwPVt98wAAAABJRU5ErkJggg=='

PL_frame_peak = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAP2SURBVFiF3Zbba1xVFMa/fZlzzpw5czuZTJIm1vRC1JgKEc2DVEGEWgQVH8SnKgpC8dlX9aWIoP4DvgmCCFZERIUggvZFvFBalTbmRnPtZDKTzPVc9sUXJ53UxM6ZTg34wYG9Ya11fqy99l4L+J/KAvA1gIe7DcDb1gUALgAFYL2LWCYhtF9rpQE81S1QSw0A+na+bHZcA6QMgHUD0J6ZMJ/i8TeeHYAZI7Wogc7/tG3Ekofp7/NV8u7z7NNTE06xEz+t6fn02Uvf3AwzZ3Iyef+IpR46Yv8WFebLi5Vjd+VcGHQs9vPC5clTJ5JrHTkS9X1rSaP+dD+V64obZgJ5d1j8serZ3cTgtzbpTNtNwTmzhWVlydz1wDpQmJqnGGEJoqlLF4pBXAMgEWP07JgqTcVBLEhtUcdKqMVCYESN0TOYqie50hYFgKNDQ97FpWbkuukJTCAUkRJEwKQAMNyXFzPrfuS66QlMsSZ50raEUIwAQDrZr5Y2Q/NgYKqSZxKOau0du1+vlIKDgSnVBUvZtmztmZEly+UDyky5JrkTd3ZgKHPJ6kHBlOqSO/HEzjEFymYanJTrMlLD7E1m6oLFLVu39hoEh3K5YPa6Hyk7PYGpNCW3rRuZAYDBbF7MF7qH8QiBTwlR+1rvo3JDcTN2IzMAkMvk5UIxWt2096ZHrr49djgk9JOoMNsNyQazux/cjNMX+a3p+JgWCoHx3leFgenL1WSxKnY12KqnOGOJXfaJeFZdi/jWdNS1f7had1764NrY5PGJ5heXtvMzK3NW2lLi+KDVuO+Q2Zgr+PGJcbMh23wMI0PWIl7vFsybAPqmzs3OfHR21DjSbwQtgw8vlPre+qw4+uLpV7ZE7AHjHkA8RnQ1hrIKvHW1VV2JHx1eCilLk3YYsDRZ2+oCJpkc+254+NHXSlu/Tj3+zsyJGPHV5Gi8mrKovDBHMy8//XrFx9DOSKA0IT5cBtNlaXMc6Rx0eNMQLrRNQ0VozZPUsVhHl4IDwMmT564oZebMY6fF3an1hkHKollfxEZ5yXjhySfqvnYiD2FSEzKYzYaLxdCYGGFexzDt0iDwtcup7WLAfhCh3sutM+UzfeG1Tc+YGLE6gunZcLWX3FRWLm+GHU98PZuB91Im6crZwp/W4kZg+EL9YyQOJciP841RAPcCuMIBIAi44ncAK+3k1MffeoOf/7Ka55xoEApGzR0oSqH9EK8yZo1J6Z3hAMC5rQG/5zCxxFTszDNT9X+zKXnJykYt9f709HOtmqn0HCSKOKcE+LtmOLe1EBJCxsKNRmbhvwTxhFVXqg1GKSoBtSY1wZaXWo4SjBA0tdby1pb7S2s0bsf/jugvMSKV430X0woAAAAASUVORK5CYII='

PL_droplet = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOjSURBVFiF7ZVdaBxVGIbf8zM7Z39mskmapGk2sVJrbRqS2FBI1CrWmyCiUGkV0xsrCmKxIlrqTwUFhYoVKigISqk3or3xxuqVtFVCbWqhlhpp0ka70cT8LDFJN+7Ozvm82Kxso92Z2VUr2O9ihh1mvvc5z5lvFrhW/6NqvdoAhVoBIAlg7dUGAYR4X65K9IKxQ5W24hU+381t61L8wP7TPBr+FsDdlQKVW5yZocP2G3s2VB39+PrqD/a3QLBPAYTKblg2imE8bKy78WtzQ0dOQip9XaMQzYlD4PzxfxvGYsp8yH7z5WOuYCaHVhJSxQ7uOwopbwewrJymoiyUcHhvdNuWU6LzphQHh+aAIGIMAnpifMg9f/FREH0WtG05ZlaJ+trV4b77RhkxpUGKE1cFQ7FndiR5RFkA2oI2DmyG2dZB65Vnv+J1NRmWvwJihGJDvKbuTPb4yReg9UdBegczY5q9RlebI1pvyDAwRSDFQGqpIdV7W1o2NnwPIe79p2AMEYu+ZO3a8V0hvBRQ1b4XP2FSPAHA9Bvge5t4lbU70rfZkp2tM5dvDwOBsHTLyI64+uy5tDs2eQu07veV4ZOlntdWbw5tuWcSYIqAy2xcyVD09edPMDN0J4B6PyG+zPDq+DvRnY9I0dy0kLdQ8JA/ljKkp3+dyA2NPAitD3vm+GBZLlqaOoye9WlWZMGvodjO7cMsGmkE0OAV5GmG11Y/GX2sb61obsqgeOUBDGFiai43/EM7tD5eMssLhilzk9HV6QBYtLG48gCG1PYHLnApe7yypCdMWFkUkiYDCIXV/oWh/JkAYtBLDHHL/o2k8BxxTxhwzhlIETEw9gdiYCAI7rkLnjDkOBmA1TEQKgGCq3XlMJncYO7i6BrZkkC5QLkvB5aTds95ZXlOE83Nj/NoZKuxvt1AUVQxkNeUpd8+cLM7knwXwM+lsvx8Zwayx04kaXYujMWJyr9DUPnfpadMT0zFncHhGICTXkG+vsDk5E6553+839x0aySvxL+h2af2dOvJ1NPQevxvgYHjjCGbmXeTP20MdXcpX0CuZrPPvdpGF0bfo4WFz/3E+P7Xpkvpbyg1k8z2D2yU69bYvMqmKwHlBodic7tfW0kjo3vd+fkP/WYw71v+VCtEovEt3rCsI3RHjyVWNhOviaf1VMp1h0aczJF+R/8yfUZPTe8CMBakcTkwhYrANO/icbsdUiSQdZI6NXMarvsFgIUK+l6r/3b9Du6fshC2h2wFAAAAAElFTkSuQmCC'

PL_neutrons = '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'

PL_get_result2 = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFlSURBVFiF7ZdPSwJBGIefdVclrcwyM+wPRkFng+jSra8QVPQpunXT79ChL1ARQR+hS0FEt7Cb0MVA0qKIdf0/HVwCwb3MDGKxz2l5h/nxMLO8LwMjhKGwdw2YHFB/AT5kAgMKMhNAHFgHTtzvOBBSyFQmA9zoCFI5Ge34Ml74Ml74Ml7okDHoNTqVbv4bJIs5M3uQi0Q3Di1zfqndrRQd++Gy+naeBzpSgbImieR+Ljl3dBwKr8YsKxEIhzNTkejmthD1oFN7kurIstdkjEW39gyjfwwZRojIeHYXyROXlUkFrYX0oIWgtZgGUsOUKbfapddBC+1WqQSUhykjnO/7CyGa/UXRxLYfrwAhEyr9A9dqhVuwTSGc5W6nEWvUn4tfn9en75WzvKyMDlaAOzT0GR1NTwBNNJzGvxsH2vBlvPBlvBgpGUthbxaYpjcU48COWy8gOZt0vLVNV6bq1qXf2j4+f5ofq5pTdnGBZ+0AAAAASUVORK5CYII='

PL_output_pdf = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAQjSURBVFiF7ZhdTFtlGMf/59AP2kJLqYVRxzoHq9SdicUY0bl5Q5WL1Tg1hI3puFgsRFiaZVS5mhdLOmmIJGiWqEOLS8bgwgvCJvOuGtBZAaFx2MxtfNgOSCn9oN/nHC9MZ4cthQWYifwv3+f5P8/vvB/nvDkE/pFSoVB8wuPxGGyRotEo6XQ6mwBMAQAnKZZXXV0tMhqNf24VTFtb2+NdXV15CRhyqxqvRdsw6bQNk06clQMFLS0a0dCQMqpUeliSZFiSBMEwWKqvnwxWVS0AAN9uzy00Gl9kAdD5+UEAIGiaXD50aHapsfGPRC1pR4dKPDBQSgsEMUYsDif34TmdElRXj64KM282jyr0ev49s9nGiMVxACADgawivf5AbO/eQEypDEUoyu+vqZlkuFzGW1c3k/DKTCa1rK2tzG00TgKAx2BwkPE4ES4vX1zWaheS+yhOnHhpZe81LROTk0MHtNopodUqXy3P3dp6k2e3yzluNzdVnPT5OKBpAgBCBw/OPhQMAAhv3CgMU9RSpryoRjMnGBqSpYpJL1woFQwPSwHAc/Lk3ZXxfy1TQpKenmKGz2dIr5eXPTJSGK6omItoNL5MMIxUGiF9vgdmRtrZ+YzEYglzXC5xqLJyIZ03LUxCsZISn+/o0SlaLo9mygUA0u3OjqlU3uQxT3Pz2LJWuyC5dGkXXVAQWTeMt7Z2JrGB16PskZHCpfr62ylrHj8+vZo348ysWQwD+blzVFijmaNlstjDlEj5nuHb7TuKGhoOsCTJBCsrXUtNTbeSc/h2e25ub28ZC0B07dpulmWJrGiUs1xVddej19+fFWlHhypncLBEYLXuklgs4XhxsW/eZPp1zTDzZvMogNEUufcVoSj/9NWrg5me1GMwODwGgyNTXkL/qc/BNkw6/T9gurstyvV6NgXG7/dzLn/98fNffvFR2SOHGRsbE59+BwTp66P6rnz2BAAEg8Esm82W19/fvyOdb+PewEly3LQ9dnh/mNvwFritnRcrzp65vC9HEOaGgiGeUP6KQ6fT3dt0GJqmib6ei7t/+fGbsveP/D1mavYKAK+AZYE3Wgp8Z059OJ7OvyEwsViM6Pq8vex3+7elda8uij7ojHKyVmyA3uu8ePlzNb8JhUI6XZ0N2TNcLpdV7NzjZ1kOQ9MEiBQ5E7d48X1Pv5D2LrNhMACge61mtv3T6wO3Q+/9pDPIAiz7YNxQF8i+0n3+2S2BAQCSJFFb9+6dop37XXOLAMsCZosoYurKCY87CFYmupM/MTGeuyUwCckL93hnXMDp9twQLW20PfXyV4PWKcNwEJTrB+t3inS+TTna8iKVt+l8dqzm2KmfX3/z7WkAoCjKD+hT3gA3FUaletJ/rP7s94d1R5zr8W0KjFqtDqjV6sB6fcmn8JH/ufoLR0GTmymKdxYAAAAASUVORK5CYII='

PL_output_excel = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALQSURBVFiFzZbNS1RRGMaf99w7ON+MEYoaMU1tUirTMCFLzUX2QYuIqDYuKnDl/9AqaFe7qE0ZBC76IE0KUvuggsrCkL6sLHJMNw5cnXFmnDkt2t1zLrwHhrjP8rkPv/flnnve+xJ0IkxjDK3aZzr1YBLD2MnOH8E73Kvf5bZtAPs08SiOo4MNB6I4ZZg/s6jkCcCwJtwFwhM2mqhHNFgz3LicL6UQwCtdMzpNA2hi9xKm2eoHDde5+aWj6b74nfU9bl9wAf9DhH9vwa0UgO8GlC0UpDQ3LvOyDhZmdc3oZHRMxnmBaYzWtqm2j+R5m6iKXnIhsiD3ABg3qNuJAD1zmzaAi25TxERrqD/+m0vOXXNWqMa+ws2XvuS3oSAv6Jp5qqQDyFYdjv5iN3PTyYYuJ5S54aXl3oVlXV39BC4inB9Z3siFo4hwbiDTzs4DUV1dAmFEMSOi224MzHLJpU/FVNkpP2a3ItEJYEJtZgiW2xT94mvidv0gl505Od9X/lNKspvxGAW+u9rKBKYQbaK4WOBCpCPrZLb8zaBuEjCZwEPYzkafwBQqMLH9dUwUortuU+axH1I+YlMkegGMGtQ9AOCh27TDA4mc28xeyqzKVbD3EwDtAG4Y5Hfr8rRuYsN5t7l0aK5PZmXSAF6Rv7xd/FyoVaISQQDNBvCIYT6syxNF6LUSzaNJrsn3BvAWAJPcMNnUgmqaU3yPvPlrH8cOblictmYSt+qUb9JfVxuk2YEJSQj8ZFPKSKEM/gS2kaKgWFTL3q8PK+Fj6beR0ZouLnvl4OIEitjKbiaAjzq+z47JJnVySrmXYtYbLkQ6pTaUMMauaqGbYpZyi22sqbuoiInm0LnYDy47d9VpLGdKyi7tJRG32kJnVX5lduBBJ6vleCmo51dsB9ZyvLSq51OgteqDwp4qbCbgOZct12QHpME3Q+gim14otp9+lL662n8BQO7jQvQCf9sAAAAASUVORK5CYII='

PL_output_sam = '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'

PL_output_mat = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAT+SURBVFiF7ZhtUFRVGMf/9x3YXeSdDQTW1WTWKBu0LSk1HCdpdLRoBkbGZpvaGB2ZMWvii1NMZS9DKpPmMBkymmhFjBKNOVmkKCEug+WEjbKCSwO7wArxsuzLvXvv7UNDLfsCriPmB/8fz/M/z/ndc85z7rmXwH/KSElJ+ZRlWQl3STzPk1artQRADwDQPrGYvLw8RWlpad/dgikvL0+trq6OmYQh79bAt6L7MKF0HyaUfKsJskQS+15wrBq8IcYbqxSnM7Lp0clYy1E+7dRu17IFyyiLYb/SNNwrR9TtcC6VRZkY6BITHtBRA69WK1t8843ZJXbv845nEzXkMAAMdImJyfMpOwCMDsgqXpdmCQlDkJK84mXuSmeLoD57kM80ZNOmydjl7z3zFubQN57Zzl0BgLi5hLv4sKL5+gUx9upZQW3r9MaN2SU2OpHkfXOmLSZthv1KEwAcMEw8VXxY0QwAp3a7Mtt7ZMrXG3SZopNIp+SVyeFeOQIArp3zxifOo0ZIFgEH4sVv3NonNjKWxWsZy4UaXjMlTyLJr30z8vdgYzy5ibvBqPvHZ4QBgJWvcFcbK12ZAND8hWfhqs2Rnf4eUQDhHpPZBA3lWrKBtXa3edX+ngQN5Qr6wMkkT9DeKQ8XEkarp0eGe6ToPy97o2lOFuPmEm5/j6mOT12QQ9sAgGIIOS6NGOs2eWNC5ZxJ9HTB7OeYriMlE7kbKxRNweK/fcdrJRHk1Z8daQDgHJUiL3p5UqunL91xmCX5nBUk2rRL6RH/2Gi/zCkTCNeLexVtvu2VRY4VogCCYiCHCzPtOUOSwGP5nDVYrOWoR5O9nrX4ty/Ioa3tJ4SUcEEAv5kRHSr2zOcuHe8Ea/1DjDdUKlpJEhgfkpgv33A+bu+W4urL3FHzlzHWtjrPIsslcmi4T4pabuB6AOCHT9wPdjZ708YGeKVrTGJWGjkLABx/2/WwvVuMGegSEz/b5FjOKgjBUKlonRaGUo7zr9VH/+RvUsWTQvEhZbNv2+qtXJe/b822CPOabTD7t+e/G7y8/XVPvQ7uw4TSPQUTcM5UVVVpamtrF4WbaM+ePeezsrKmvGtOHD+e8nRurj02Nla4LRij0WgxGo2WcGGCqfVYja6puuqRD2rrfoyKihJn8s/qMtGOce5DuyX+rU1FuYIgEJIkwWw2K06ePJnc29sbEeCfLRBBEIgIt5PNIiSitM+ctCNv9TqVKJLpooduECn52Jmm+hlhhoaGmMHBQS7cwbVarZPjOAkAOjo6VDXv71yywTPBAkAOIZI5EwNzAKCa4ISizdtbJ73TwjQ2NiY1NDRow4UpKyu71N/fz31bsStbZ7fO2ecZj1T7bYIJGaiPTxmtMLzUEyxHAExBQUFfQUHBbX1VMgwjRahUHredlCkiMH5TBlRq9Xhg5B/d0Q2s0WhcOw/XnF914NBp41ydrRH0lArKIIHI69eS+vr6AjbvHYeZlE6nc2wt33XhPKvgAcAEStrOxDi/khgxf+IvxcH33nk0WL+AZTKZTDGtra2J4QIUFhb2JCcn//tlkJ6e7vqaoMVfZFr6OCOz//WKvS2/trfHnms+p75p61c5nU7KP8eslTbDMLJZklEx7yHrR0dqmhiGkVNTU23r1q+3heoTAKPX60f0en3ANfN2pC8s6ijesqWLoqhbuoLO2swAwJaSkuvh+H0L8H//c/U3ZRTyR79wIBEAAAAASUVORK5CYII='

PL_meter = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAM/SURBVFiFvZi9jxxFEMV/1bNfNnu39lk+DmM+ZBE4MQ4QjhBCIrGITGhAghhEwgkkIovIsgNi/gKEZEFkIgguQA5sIQKHRkK2ASPkmxXc7K5ndrqLYGaOvbnZ2blz+560Uqu3t/p1db2q2hb84Xmg1XDtb4CWJ8UXk7de795+/8LhvrVESUqUTDWKE42SqURx7LbGsUbRyG5990P88r0H9j0gLttoepKFOLkWpOdf6/UERsBUlZGKDsGEqIaBYRPR8KefN1fuPbCVNuaR6QOr+bgHHMrHvwL/1JFSRURADOjMRViHBEH9gcyc+WPAWeAU8D2wBhytIf8/JCOUGTc7drGuPizmGb+bfwCOAxtk7m8MVRURwSi42S/mHb+GzCxcvYkMt24nqx98PhyMH+nhacpqakkuf7J848xL7dBQIvQYZJQGqjt7uvPw0odLLZChVR12W2wu94Mo8xAEAdgFjLyR6bRxKwOjKE6MpKqaScaAcwiisiB+F7ufhtc0i0JRZVi0anpPZBp5ppLQrtkAdL4tb57Z3mFm5Tahhn716hkpLxRQx8JYKeBN2hu34pMXPx0ubUXuqUmsz6SW6Tdfrvy4tmJwigTmANX0xqvd36+uD04ghCJsohoqJilqgmvgIb9qyikX5aAcL84hdYaenJowolqS8j4L5X7IVOYQVcR4VFPja1Kqk51zWns9eyHTzDMz8VKVc7bj5SCq9sbN+Nl3Pxsupan2orGujiZqv/riyMbpF1shAEFeo2rgT9rnun9cXR+cAELQEDWhGB3rrrb7AMpB1TbqEFN1Z49BZk/loGzZ6UxuWbCbVzJ5stu11lGf7Ap4C+CdrJAypTx4aw/1xDIwTmWPR/DbkL/9cbjcadNNrRz7N7Luo3f6v1x4s5dJu0FX7k3a5850/r6yPmgDIUiIaogQNvltAd89cHWPW7SaCwrlPM+0yF4VANrAc8CE7I/cn3UGi2ZcDTvfGRyyXzJd4JV8/C3QAV4ge8qoh8wQKuaKeHG6r3IwAq7l42tz1tRim1CpHNT9V/H2JHLnrm1/fX0yTq3aNKWVTLWfTFUeTTk0id2RyUSeHsd2dP8vd2qeDW+PRXh4ufoPFZ1OONfS2g0AAAAASUVORK5CYII='

PL_flasks = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAASXSURBVFiF7ZVbbBRVHMa//zlzP9udbbftVtou3XK/KSTEmIqaGhswGjGaKEZNREEeQIqogSCmVqwhaAIao0Z58cEQXnlpvISEFxTxUkCUixIwMa3RUEqgnd2ZM38f6BLcQnd9UR/293bmfHPOd34zmQGqVKlSpUqVKlX+MVR6wbbNNURyiWad12E4Esd4YZL7O2zbepkJQzoMp2rN90yStU3TOCilcSQMwzat9QYAR68NiNI7pDRbVz+35cMDhwZ7pJT+ZCcxDLizFyz8Yv+3Q72maf86WRYAkkn/2KcDZ7elGxr6AcjS+QllhBCkkglXg5WUcoK5UlzHs3QcKCnlhMVLkYYhjTyU7brm9eYnlCEiUq7yhMmeEMaE+VIsx3Fsw/SkaZYvY1qSDMNzbdeqqAyEINN2PcGsSMqyZVzXtTSzkkKUzRqGYcTMynKcyswIAbIcx40ZShKV38B0bGaoSswYwhDMUJZpV2ZGCEG2ZbskpVeJGdu0LRLSM4RRtowwDMMQwrNsq7IyxERCml7MrEQlZizTIc1KSFH+nZFSxtDKtCp8TCRlQ23KNxlQQghvssVdV2Xr6hvBrJVl2wJAzSTxttq6es2A8mvTZNtGplyZXEu2vbm1fQYkwbt5ccew53n33WBxy0+lVz721LrfIIS3au3mgWQq1XujJo2Zph0bt+44TSS89Zv6TqiaVHfp/n8bZJqm7Nrcu+ssMxSDVc/2946qRKIbwASt9Y2NW59et3nIkIbHgOpcuvxiSzY3DcCs0qzv+10ddy+zW7I5ImalEjX2Aw8/fibh+89et4zj1NzRcVdXKts2nQjCY4YyLct9cs3G477vbyw9aHNrrmvp/Y9cIiKPGIoB1fvmR4fr0uk3SrLSr02/2v3itj9A8BhQxKxWd79yzvdrHwKQuhoslmpubd3T9/bHw4ZxRQKRAINp7oJFI/379nZeOH/+cwCXAGBKc+vunh0fWKm6dAQQiAhgUMJPRefOnEwNDp6LCkHhJADUZzIbnlm7ac7sebfkmQESdGV5AFOyueHDB/d3BUHQf9VMJpNZ+8Sq9a7tuC4IHgAFZlU0tOX1dwfq0uk+APA8b9HijrvmtU+fQ0TkMWLFgCoaeqln5ynPqVkPwAZQ09TUsvLe5Ss0EXkEKI5ZFQ0tubPrctu0We2WZc0vmklMmzX3/ee3bGcCE4Ou1B7/oxMJ1Gea8gPffJn78/fBMzc1Z3e99tZuz7LtcYMEBlPRkCABVZMMfjj61fz6hsyjW/vemVHX0BQXswDoWkO33d451L9v74qx0dE9RnZqbueSzmUtBw98NhpzHMQ6CmIdB3GsAx1FeR3rIAx1sPDWjvyPx777ZOacBbVHvj9U4Dj2wqiQv3hhONJaBzoKC1rrQGud11GYFyy6XM9L/nz6p0unThxP6lg7sdaJONZ5HYWFYHQsvHh5hHUhDBOJ5NSx0csP0syc8wsJSxgGNDODADADAAMA4jjiKIwYAMaC2HVsyhNRfPWlk9BCjIevoVBgE0RsmYhK58a1syDo4tgwEdHI103h9cL/BWU/9/8m/6syfwFG/IjarX6XAAAAAABJRU5ErkJggg=='

PL_budget = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJmSURBVFiF7ZXPa9NgGMc/SdukpXP+onUMwY3hNnVQD3bC3ASHriDiqOKl4EWEicedRPY3iA4ZeFRBmDvoDjLYSdyGFz3o1G0dVphDWyZTHLZp7RoPaSFLE500TQX3gZC87/t9837zPs+TF/53Qu1ya9dhqd/YL9bAi3i6xzN8/IgcrbmZCxHv0NWYv7dpr3gU8OjH3LrnCLCvCuuPnz/lGz/X590O0NbsCtb7BSHSLbec6ZVvLMypI4ufc3MAgm7SY6AsjjYQ6Dsmh4cGtt0Ntbt3Ggdn4/nM6ER6/slUbtCRME3OZCeGH6TvKFm1bGw5tZ5aShVuJ5by026TuVXB5SookkfY0Dc2qby7dU+JzsaVBGzMmSvAYBV8fAUItUpdogiJ5fWcVxZoDIhSOqOulowYzSSrYASAujqCbxd/Nl6/uTYy8zo72tIgdcTOytdEQXUsMnpkNhYL4ZB06ESn9LAWZqwQ/izZwrlt6gH2o1XWIyuRU2eTD/hSvFti3BkZuG/D4heBrK7tBqKAC1DQjp4yjHWeB8ZsMJM3tEPAAhAGPtnw/orpB4LAJSuByyEjXrSwhYGnwFotzVwurpUC5q1ETlXTN6AJWEELlSnGBPYC0zYs3o1WNSU+AirQCTzfrJkcMGCDmZyh/R4IFK/6zZopAC9tMGMkCewG4kAD8MZM5FQC+9E+PAm8sBI5lcAx4DvQ9juRUzuzBzgAvAJ2AKtmImPO+LCI51/SAWR07Szaj+4gMGU1yXhQCkCzDWY+oJVyCT9wEtiFVlnPzCYZd0YFEmbCCvlRNLRSvP8TBGptYIuK+QWpYozcBuugGwAAAABJRU5ErkJggg=='

PL_interdit = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMbSURBVFiF1dhLb1VlFMbx3z62tEU0UbReotIOJAgoDkw0psSUkRcaiQNjR5r6NUSNH8CgfgGxRnBiYhQLAYVg46gpZ+22aUIH9ZIgEMDYqr3Rsx3sfZo22tvpBX1mZ+/1rPefs9de79ov/yEltZhGaRxjX8ZONJeoq3ATVxJG7iRamdwwmB9o2kpnQifa0Ii/cFkOUocH0ITJjO9LfHYHx1cKtizMWeq205VxGNvxZcaJjN4n+Skhq8ZmJCktGW0lDmZ04Breu8HH7Tl0bSqzJxgOJsq838+9q/EHzcGRYDJlqJ/dtYK8EowH3w3wcE1JCvWzIzgXjKUcWpU5eDOoBEfO5rWwZvVRn9KdUinTtVKQA8F0Oa+RdVOZncEvKV8U+duXNFygJbgRHM1qfO2XAgleL4q8O7h+gZZFTcHxYHCEho0AqV4boSGI4JvFQJ4JKikvbCRIVQM8G2TBgX8YU04FpzcDpKqgJ+XUgotDPBLMljm4WSAFTEcwGzwEJZjJH834b5xcD5CEb/HWPo4uFTuTr/cnnp+DKdGW0Lumdr1KEHiKGfRi/xxMxq4Kg5sJMk+DCY/NweD+hEu3AAQuZTTPh2lKmLgFIJK8Zm6fDzOR5XNILSBnagUptE0ONAdzOePBGkEOrwFEse6V+TDDJfZuNkihvRieg0mK12sl48J6ggyxRT7C9s6H6cnYdlfRfDYDBG7m6zVl9Cy4UexNZ5YCCX5ersWvRsHJ+LeuHzxd7NovbhLI/iBbdMgKjqUMzZ9nNgJklMZgIOXrRYOKwfl6SndGshEgRd5Pg2v97FgyuEx7MB18sN4gRf63g6mU51Zq6Crq53Qf9esB0Ud9mY+KvG+sypxyKBgLzi37dy6joDU4n/J7yss1Jelnd8pQMFk8tubV+Ae4L+XDYKoo2F1Lxa/oW/vuvG7ewT04ga8Seh/nx4RKNTajNEhrJe+qHXgJVzPevcgnrzK7JpiqRmkc5zV0Zvlk1iQ/XfjVwlOI6unEeRzbyuePMrWSNWr6UBuh4Q+euK04n5HvMdO4OsvFLcSe/Pf/V38DxzNSC5BSaf4AAAAASUVORK5CYII='

PL_xlsx_budget = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAM1SURBVFiF7ZffaxRXFMc/szPZ2Z3dnUlMYgw0GqGJRsRCNZYWfet7tS9CRQQV8+yzYOkfIPuSBxFExAcFW6IgiBBQ20Kh2qqtmjSNxtgaNybd7Ozu7GZmd2Z82ESzw27WxsmuD35hGO5wzj2fe8+5P0bo2x97Kq8TTRosM2HLUvMOWencE2k0C4krhiKt1Nn6zw48u2oobhGh57Ca8QMosFLHYKvofHxQzTqWK/gBUhMmP10U7x5PrtEfmk2Wbgfuf5dsmf11Xq7V6bMhQxmJp7TRQV0dP5uOAbg23DuRbEnczIcARuIpbfIHo6w+lk1TuEOy13+tZGfumLKWdgva5iarbWeoZrGn/rDkbd+2zAEkbpSCCyL0HlXTExez0UiXVBREwV2/N2Is9auZptbtIcvJu8LEhUy0e1/MqGUPsGFfNDt2Wo+NxFOanX+TRuUjyW77TDZvH5tt6xmIZQRP9LLm5PdGJDtZLJutqeu5cLhTsjcNqOnRQV3FXR4kN1UUHcsReo9qmb5jzfrcn6a86DP3wAzqD62mL86snXl0Utfseaes3l7DuA78fUZXk7+bwcVvyXtm8MVwPqz2SgWlq8m2Uk5g4kImCjB9Kx8aP5eOzidscfxcOvpiOB8GcAoIz6/llLFTemx0UFej3VIBAXL/FqXHZ7MxbWuwEGoX7aAWcB7FdW0pjPB5vO1l555Ibvnxrr4SVwxlxUt7NSR0fRq602iIRQkd0Piz4H2Ub1t5De0GeoA5YKiaUb0KOAzMLryryjszMnDeh+AHgKXHhgTsBURgHrhcycl7NhWBSz7AFD3tT4C/gH5gyof+31lfAWuBQ9UMxDqBhCilrR+4CVS8jNUL5shCrGlgtJpRvVZTCugGZiilqqK8BRwCfvYh+C5Kq2ZR/wAusBP45W1hLGDABxjL034MtC886tvCOMBvPsB4lQBagTFgHfCgklG9CjhCaeAJoOotoV4F/A2QBjYtZ1SvmekA+oD7QDOQrGTkrZkwVfL5P7UVyC9pm5Q2ui3AT9WcvAelAGz0AWYCyv4jIsCXwBpKK+vHSk7emXGBJz7AeGUsAM3wHt0s2xsN8EHvrFdQhgcK7EiqVQAAAABJRU5ErkJggg=='

PL_element_green = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAP6SURBVFiF7ZhdaBxVFMf/92P2I7vZbdLEdhPTNE0irUiNCiWxohXjQ0WULemLH9CX0Pqggl8Iok8K+iDEkicDviiKRI1tH7QgKNKaNi1EUmho0mKySdltsptk1/2anbn3+rC7srW77c1uWxDyf5m5M+ec+c3hzL1nLkGJGMMBfzPvxV1SfNmeFALfFMe89Ka3ke/pDdLnW7qQutMg1+ZQ9+vX3JmM2eVhACDQodJ7nmWxWwWb/kP6zp4QWwDg0EfG7E+fi9boonS//KFxWQfmz1+k/O81quNYTrPnpL//EF90uiEWL8m6/UfYVcqgqo1XE8wTL/LImWP2lqV55aGc1ARRM0wurSjjRG7tJMmWbpIZHxPNkTnlmZmQ9dXGvKFmdNW8jZjBN3ioOO4LsuW+IFuuNp42THIV/OhgbjcA7OqjseCbfP5WPmOf2u3T43IzALw24pjyNsC+LTC2BTJ3QTYCQMNWZHV8In9JT9HHtkB0fKqumTuhDZhK2oCppA2YStqAqaT/H0zpXC5tvam91E7LQRfG7YMonptZMB2fbKZgRwCdRVIbxuGCdHlgAcBKWLl1fFYLdm4PLGbodYDaNRPopgkAiIaUdyWsHDcFicARXVBeAGi9j8Z1n6EN83A/uwYAUoKcGLbbb2Z7/KjVLmW+VHqeZku3HWbfSyzSGCBpADj9vWj/6gOrM7V6fT+UXAX/8n2r6/QPoh0AmlpJat8LLKL7DO220+mGHBwypoYPWw+l1pTz929Fx6lRsb2pjSTd9cRKJ5Qjtqg8xYx4G4g5OGRMOVy44ZekZhgA6Oyhyfe+c0yMfmLtuPCbDNgW6NK8qkdJfXIDcveTNHzwXePK5laSW0/8dTfkTW3EfGXYMW2mcGl6XPiXF+Ay02DOOojmNmR39bG406OfjZpginJ6IHv62Wq1/uVUsYB/HhGt8SgMyHynrxPs7HHRVAtMxcxkEoqrQrJTccWPfWZvY5zIrkdI4vJ56U8lFH/uVSP0xdu5nd5GknvsIAsvL8A1MyHrrWz+JR1uyFOjIlDfhFzmb3BKoR58ikUfeLz83FMxM4RBSaGIkCCE5eH2H2ZXAcAyQRcuKp+0QVq6afKZIzx0ZVL5UnFpWFlQM6tYNqNYzgR1eWEPvGPMUQp14C1jbva89K87Mzt76drJEftewwl5/6N0Zeac3MQ4VOii8rp9xLas/ItwA5IyKFVYve7pINkfh8R2JRTZO8DDlOc/Ne6EpBwKqvK6ed0NfzP/eO8ADRb3Z+wcKFQ+kLBAmZH/Ssw0GDegmFG4zqFEYZVmBmQuA8Y4FGVQUoD8a1dyzO/PyJPJmP162cwkV+yJM2P8rvU4mTV7snT8D15Omi4RtzENAAAAAElFTkSuQmCC'

PL_element_yellow = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAQQSURBVFiF7ZhbaBxVGMf/5za7m72k2SSkJeZGkqZPxVKUVlpBbEsrQok24g2joLSIxXsJoj6plJaWKDWCeSvSEmKMFxQF3yq22RYiqbYUg002l40mm71kd7O7M+ccHzYLW5tNJ0lbEPJ/mTkz33fmN9+cc77vDEGBDIbHKir5NtwlzUxbg1mJs/k2L7xZ5uf3P95K929qQvJOgwyPoOT0Ge4Ih63FYQCgsUGn9j/Kwrfq7Nyvyvf1d7IKAI5/KP789HNZHRxXruMfiGE7MD/+rNR/r1E7jotp4KIqffF5Pu5yQV69pkoOH2ITnEGvtL9VwbQ/w6f6vrGqRka1m3OyKohVwyRTmnJOVFMjSbQ0k/nefln514h2Xwgo70r7vGnM2FV9Lcl0vMGD+XZbK5tua2XTK+3PNsxsBPy5l7KbAWDHdhrueJOP3srn6Amr7pfzqhwATncbQ/4yWLcFxjRBfrus/ACwfj3SdnyGryt33sc0Qez4rHjM3AmtwRTTGkwxrcEU0xpMMf3/YArXcmnZW9oL7Ww52IXx+SDz56k0mB2f5HzOjhBgnY0kaRvG6YTyuGECwGRIu+z4hBbsPG6YhrBXAdoeMxubaRwAgkHtmQxpYynbySkYwTHtAYCWjTRm9xm2YfbuYn8DgFQgJ09ZdUvZnvzErJMqN1T27Wb/3HaYF55lU9UbSAoAevpkXcf7ZmMkcmM9NBsBP/Ke2dTzlawDgJpqkmx/mk3ZfYbtstPlgurqFEPtB80t0ah2fNEjG872yvraGpLweokZi2tjfFy78xEpLyOZrk4x5HTipi1JMS1rndl6L0388KUR2LebTggBJRXI9VHtHfpd+UeD2iMViBBQj+yhE9/3GQNbNtNlbQaXXZDX1pBM9ynjajKJa+fOy9LgGJypFFhJCWRtDdI7t7OY220/GquCycvthtq7i0VW6r+Yin6mrm5ZPT0DoRTw0YmlZ09e/d/KitXAFI1MNK55fjccj2l+7GOr1uBE3beVxAOXVGksrvnrh0Xwtbezm8r9JPtUGwuNjsF5IaC86XTuJV0uqDO9ckNlBbLxOXBGofc8zGYeenDxtadoZDiDtqQmlgKhDJiLa/7yQTZBAGQyoH9c0T5lgbQ008Qrh3gwMKh90ZgS6TRoKq1ZYl6z+Qyo1wPr3SNihFHod94SIwOXVOmyI7NjG41+1m3dYzigdj5AZwcuqnUGh758RXt8PmJlzNyLCAHFGbReyF4NDSR9rFPWS6nJkwd4iPNcKnA4oDiHVrp43rzhRlUlP/rEAdqa/z+TyYIqDbgcUFkT1BC5WZJIgRkC2hC564JDmwtZ2hBQqXkwzqEpg1YSJG9XeMz9n1E/hcPWq4tGJjJrBfr6+V2rceai1mBh+1/Oo6IEjIadZgAAAABJRU5ErkJggg=='

PL_ubj_budget = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALsSURBVFiF7ZbbSxRRHMc/s7O2OzvresPUerAeooxACTQCexC0sh5KTIgiK4lubmD00P/QQ2+SkBQYQhBSLxHRS3TBF4NukF1cA8UMw9JZd2f2MtPDrCnTjqs27PrQF4bhnPM75/c9v9/3d84ROk/lf63YIGrkGN8mkh533S6Pr7VNzjUXBgbmfC4nFnr8JOrt61cy7ih4ebo4quqC3bgjZPY1SerUlC5msms/Loclr8uwG3evxGn/3Tm5qNClH9gvRR8+ikifR+LurmCBApDU4cbNWb+mIcRihtB5Pl+RfabjW32KrKqGEIsZQixuCPW7vWk1uqLIHGmRIl9CcTfAwWZfNJngT8hfDqreo21ypCsYUE6f9Ie7e5T8+bGO9vy5i2cD4dbDcmR8LGkbQUfSBLCzxqMVFYo6QGmJqIurWNl2ysyM7urpnfVr2oLgRNFl6LqZclXVhYmJhV2+fqutU1PiDIftRboUbDUz+jUudvcogeYmn1pZ6UoAuN2gaQjXrs8EXAIUl7j0D8PxvLHxhNjYIKk9vWF/MmEIEdUQLl0IKI6Rqan2xN8NbZyw9l+9UjBr7avalhff2yipmZyFQgl3RbmYXDEZJ9F7W/GrqiEABJeImNBQ6x3KBqHlQCiD3N8FaxGrKsFVYA+wBfgJ3LczcuzQywAJ+JH628IaGQ9wxwHnJ4DF948baAFEQAUepJtkLe0EcM8BMglLuxr4CNQCf51ducAhYD3QYWeQ8Q3iELyYaasFngJpD75skTmT8vUdGLYzylY1/QI2AVOYqUoLq4C9wAsHnNdjVs08xgADqAMGl0smBpxzgEzM0h4BSlNfYLlkdOCVA2SsmARKgE9AOfA+nVG2BCxjbnwSsH0lZEvAx4BZYOtSRtmKTBlQBbwBCoHpdEZWzUjY5HOF2AFEF7U1zINuO/DcbpL1ohSAzQ6QGcUs5XnIQCNQjFlZz9JNskbGAEIOkLFiLkVoijX0sizNNYH/+Gf8BgTJ3DE3mfPVAAAAAElFTkSuQmCC'

PL_element_red = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAPlSURBVFiF7ZhNaFxVFMf/9+PdefPdTD6a2jRTa1tdKUUQqYILIXQhiAFd1Y0KIi66aLtQcCtFRbEgFMSlX6DBuhAFtxVMxUIUi/iVJp120jQzmcm8+Xjv3nNdzEyZaCa5SVpByH933zvnnt+777xzz7sMPVICkzkhH8Z/pJLRl0KDj7tj2XszK+RDk7vEk/f6PLjTIH+ElPhwCbElo9eGAYADitefyIqljSa7UDOZL5f1bgA4Mxb77dxiuHe+ZeOvj8V+d4H5tgoCzKpr3MVxLV0MTPa5Qe+qz2AuNyjx0rAqCAa71fm2BXN80CtOVfTuuZCSkm8PYtswdQJXAB3wRe1wjDemytHwXyElpwOT3uqc/8oZV40r1jo5qua648kBb3FywFvc6nzOMCVt5fNXGvcDwNGkXDo9qq5s5PNmMcx/F+hBAPggH5/JSaZvC0xkwWbqlAOAUWmaLj5/tkyy6xNZMBefLefMndAOTD/twPTTDkw/7cD00/8PhvUUc+NY2nvtmJOHI0yGs1stWcNCuPgE1LZjAAb4xpukM4zPQUnOIgC4Ftq4i08xatulBIs8x+bLOWcO+7wKAPMRpa5HVm0AouYjSnX8Kq4xnGEmMnIBaOfCuwthfj3bdxbCfDdnJjLyxm2HeXbQK97lsToAfFaO8q8VWveU9ep+qKStfLXQOvh5OcoDwJjHguM5r+gaw7ntjHPQ2XF/5oXZ5pFlY2MflaK7Py1H+/d5vJaWiCoaqhBRsrsiA4K1zubjMz4HucbYVJ05khC1Lw4mpo9lZcFjIGPBZkNK/1Sn3FxIKWPBPAY6lpWF84cS3z8Q39zP4KYb8n2Ktd4b9y8HhF8v1Ez2akh+naxIcGbGFG8+khKV5CZWY1swXSU5aCIjynArO07q+5rOLYZ7b2rrWQBvFNf/ero6X46GtgPTd2WqBtJ0StWKsfLthXBcMdCDCVG9GJhshSBPjKi5U/ON+wYkD5/JyevzkfWnA5Nu2vZDxhnok5LeM+SxcMVYKQH7eEbefCwt1qw9fVdGMlgNME3traVKkC8OqQID0LLgvzRMxliwQ76ovTyi5n4MKLNs4DUteN1ABAaiYcFTHPqVUTUrAHt6T2z2h8Bk+8XsC3M0KZbfvxGOvbUQ5h9Ny5IErMdhf25SKi2gQ2s5ACgGEgy2W+/3K978uqqHv6pEIwDgcWYBIMYZScAa9N9oV90YVvLM07vEU93zmSaBW7RrTEjgqvOV1IiEArceB2kCFxzWEJgFoDgoIAgFWN4Jrjr+HgdFnXna5zPmm6VIn7j1NnphKkZPTy2D//PcZG252KyvFdKXesd/A2Rln2PnBPYcAAAAAElFTkSuQmCC'

PL_pipet = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAS1SURBVFiF7ZddbBRVFMf/M3fu7Ed3t7tt2bVAU2prBQTFoAVBYiU8iRqLASERTA0CCiZqeID48SjyYCAQIQKVqAmKmiASQiBUg5igCxQBBcpHpGUL7HTZdr93Z+6944ub4HZLl+6WJ/5Pk3PuOfeXM+fcuQPcV35JI5S3HMDUCkrrZICEDKMbQAcA7V7CKB5VXVhPxBszbUpVPZXtBEAPNzPtSRb+x8BXmmHsBJAZaRgyWlU+mFumvLLcpYoqIvPbnTHTlLdHdPpj3NjTrbMPAbABCUpFYiOY1+JQV63xWLlTlkSu3yJJZpNVEdeZmHDBYD3MxIXcNXKJWOyNVFm5zKWCSjAHW0QAc4mLSvVUWQpAKSVMGYDm/56nNNlo5QOKPKD0uapViDGOyqMA1Ob6BtAVKLlGVdbWUfmFTt1siwoRaqSyE0CskOBqRaIAKgBc+V/S4ZCohLw81ULmb6qyknkOssIhoYXBLDhXQkAASOfah9XA3DRDhoR6BqluRbmVOYg0NsRNdbpVSQ0VmzRNeUdEj19nYgtyRny405To4+bhLg5nNxeTWp2UlxPZrC6gZ/YnDPvhFN8T4eJQrq+Y0WYxLo4GhNx/JsOeabYpShWRjTsFnM1w68b+zLXODHsfQLyUMACANOd91yxlz3akjNpqYtI6Sgb0QsqEvD+h2zZG9a5TKfYucho3q2JPYAd1udeVN89WTapy18GfXmq1QV7sVIPtSeY4neFSrxDRK7pIaNxs79LZVgA3BktWTGWI4nCsKZv06NhRS5efsD8yWUt6qy/7O06N783o7vkOGglxkH0JI3A2zVZHuNiFPK+mJDCUWlvVB+ue9q5855hssXIAEJEIvfXXaXoxHDt61RC1i1wUUyykMsDMWUEmLgugeyRg5ljGjF7iW7bqD+r1pQDA0II2rW3rjHQgsDPN+aarnAfPZcS0Zhu1aNy0dQnpUkqIjjslHc4JPFH1+d7yLFz8p1o7LgYAZiZNendum856Ar+A870AzBTHniNJozsszPURAX/YYF8MlfhuG7iKejyfup9vCXvmvngpa9S2b2mK+48FWSz2EQbeVWoA9GGIfgHurjJWxela62yawW4HufXDtxMTJ08IFoutzwMCANcK3aDQ74mklJW9bW18uKbq1ddOZY2x338bHTvS7jP6w58ACBe6aVEwRFUXqWPGzvQuffMYqCoAIH3lUnn4+92T9d7ezQAuFgtSKMwMxetbULmk1a94KjIAwCJ9aujLL55kvcFvAPxaCpBCYBrUUd73KloW/G1rGN8PAGBMCu34fLre0+3nuv5dqUCGgqmkbvfa8tlzbjhnzurJGkNft01Ndp67yRKJTQAG3HWL0WDTpKpO52r7408onpYF57PG/gP7G+J+P2XR6DoAyVKCAINUhhDynFrf0OB9fdnxrC1+8riv/8C+Wr3v1scAgqUGGRRGstsfsjROCGYnRw90Ofp273pM125+BuB8vpiRg1HUcaqvOgIALKRZtbZt05h2Yy+An0cKBMjfM1SSUc3CIaZt3vBU6nKni8eiZ1g6fXAkQYD836Yaxe3eIMlyVMTjh7iuHwXQk2fdPdEYAFNQwl/f+ypW/wLRoee8kg+rQQAAAABJRU5ErkJggg=='

PL_parabole = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAULSURBVFiF7ZZLiBxFGMd/1Y/pnul57cxkd7MxDzEivlBEkCA+wIjgQUUTPCgoiiJ69HER9CwIKoigHgOCRjSRHHIxxoNGNCh6SEAUNZrHbmZnM9sz09Nd1dUeuieZbGbcbOKih/xhmO6q6qpf/7/6vi64pEv6f+tF4A/gJ+CO/xJkG+ADSfbzgenhAcYqA5jAPdn1vUBxqC8Gblnl9QEQwEPAIWA/UACeBbqccaYDXLnaIFuB70j3xfaszSZ1ZScQAb0MbtW0BdhH6sZ2UncAcsAnwMvZvUsavlXRdcBHwO/A00sWygGfAnsAJ2uzVjL5jYWC+2qxmH8nn3deAG4D8mPGloDDwDOkoRhWDthFGppB3xbgy3ELi+Eby+KuSqX0xmStvN6yTR1FsdHtBq12J/grDOP3oijaRboJl86RLGlzMog+8AggSTP3APAW8MFyMDMlL7978+VTlzuOHQ8PilRszLf8fqvV+dHvBq8A3497O1IXdwMLGYjK2p8CHiN1eik8MBRfx7afLOSd+ybXlM8ZaBpGUvJc0/OcjXGs79Y60XGsfxgxaQH4DJgHHh0CKQMfA48Dx8a9xWmYvOu85DjWhtpE0R2a5CzlbEtXK4ViHOstKk4mlVJfk4YA0n2xFziSOTDs7mvAL8D740CGYWp513nYtqxqseiWTNMwxgEZQlAu5i0EN0SRmpEq3p+N1UALeD27HuiarG07aX1ZFqZeKuTvLXoFmZCsc52cEIKxQEIIip4rErhapkBfkDrxM+eGbgepI2Oz6PSLZv+xBtGoln7xO0GWLcJCCGfsk8D0mopZr5e3uW7ueZZkZqaHgMuAd5cDGYaZl1IZtUp1PlZ6vheEBoBA2MsCTVbsarnwhGmaD47ofhx4jjEOL9UgTHHONm+rVYpuzsqdnG8vbiyXClYGZAqRwNkb8rSEEHiem+/2wmv7ofycNKUH+pC0Mp+XzpRuYZRcy75584aZ347OtaaSRNddNzfoNAXjgUzDSGzbbASBnJFS7eHMBh5ZT5aFiePY1zq5f/1Uo1ksuLNHTjQ3FT0nb5pZJIUwRTq5HjWR69g6jOTaoN8/pDW/rgTiHBignQiuME1r88ya+my/HwXNtr++5LmWEGIAZPEPQE7Oyvs9uSGK5MeMcfF8YVAqPhpJ9cBUvXpqqj4x11pYtDv9/nTRc0+fCIUQJmI0kGWZSRjKkt8JDpKedS8cBlhAJ7lQqlunG7WTjWrp+PG5VjkMo4bnuYPUFQJhItCM2BOGYXi9QEop1d6LhUFpfTiM5E0JyabGRHW+Uan8eby5UAoiWffyziBiQiCsUUCWZSStBT8fRmoHKwzVqBNXrOL4YDfobzWEUWtMlFuNSuXI3MmFfCcIal4hZwhhDAPFw0CGELQXe2EviHYDixcLAxBIpb7xu8GdOkmmJmvV5mRt4o+Ftq+bp/yGa1uOZVsJIBgBdKrd63WDcCdn15wLhgHoSKW+8oPg+rbfuXaiXFxcN9k4kmhmj8216iqOC45jGek3FYs0JImKtZhttufCSL7NeVbe84EB6CkV7wsipU80F26XWlWmG7UTa+u1w20/CGabp8pSKjtJsBKRWGGkkrmTbb/T67+plP52JSAw+uM2TlOO4zycM82t1UpRVz1PWpYh/W5Q6/bDDVKpcqSk7HT7b2mtV+zKSmEG8oAbXdu+yrDNTYYQJR0nLaX1z1EUHSA9XF3Sv6q/AcbyAkDAxTKFAAAAAElFTkSuQmCC'

PL_bookmarkedlist = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADxSURBVFiF7ZU9DgFBGIafGT/xU2jUEs1WEg1u4AYO4CwKzuEIKqUDEJVeo1MqiLCjmCUEu37WZCPfk2x2svMm75PZzbeKgBmUgTXhdBswjMh8jH4ju/2VxBl9tShGZH2g5ETmCKmwoLH7GScyCg5hQQVGwdGJTPpxkbleG1cy+/uiHfbZWcgQcXqxyeigyNj73oeBgQ6wMlYs6+w1ZYMiDWMNXgt6TRhtwFPQB3z/xydzYQK5KbSf7c+gMoe6E5kkoF7I5IFFDF01Iqb4KzIKqMYgs+R2VAiCEwrYD+/bq+BaXPh/EjWBE/VvEgRBEATgBPH7RY/L0Db2AAAAAElFTkSuQmCC'

PL_bookmark = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAI7SURBVFiF7Zc/axRBGMZ/t0nQYApTKCJXSTRBCBG0E0HEJpWfIIWdghZ+AnubVBZJFVKGlAkEIQmCjWAk2GgwYEL+NBerOw3u7uxY7E54b27vbjY7ORHywLLH8O7sb5/3z+7Buf4DVRxiguvwqOyNDmEdUKVgRuDCfdiZhGtFATToCPQq1Jbh5hHUO8X3u2x6BcKRgiAJEAMR6GEIXa4JugXUoV+7pbNJCnScHQq0FxgFwYBDnJSBiNKzG4kLTFGpzInYOvccJslgIpGiDMZJ3mA0aXoiy5UYdNJrGAFw4o7yDVNxyLepE5GeJqDEc8203SwRnWNDmd++YdqBENGUohMoud6TmpFtHFtuWAV8ts7Ygy0PyNSON2eCnM3sUR/nHGY9TEH9wABUxLvJDLYcAPKAskMNpeVVHkZnOe802GRLW6nSCriUPkd5GKNOg03WkL3mvZu6DTYJas8dr92k2ww2MVNs0LN7NynyB1tsrQvQpmLWvpzpy2xuN9gawAr8bNDSTYh4JxVxpmWw/YBwHt5/gAcLsLYLoV3Axq2LDu44fZCblpYdswa1TZjbgNcAh/AkgldVeHEHLkt3XD87nWDEk9IAFmFrD559gY8y7jNM12H9CN7eg9GgYM0UcmYbfi/B6hY8raVcLfoOm8fw+BfMjsLDYRhwuYczjAL9Dg42YOYTvOkWvw/H+zD1B15eheec4q9OrqoweBu+jsH4aa6/BRM34NvdAg51UlCFwTIbZNf7cedc/1p/AeSIDJKIHGQkAAAAAElFTkSuQmCC'

PL_convergence = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJUSURBVFiFzda/axNhGAfw73u+SRNzSWwStVBBRBQFhw6KNkijDmIidujQwUkcHAqlVLBQtC04uDgICg4O/glO4laoRRBdS9pqG6pFkpi0sWqS5n7kXoeYeldNvb69vOkz3b13z8uH97nnvZd0HnmyDI7oS8z77gy8CQHAw6fnCy9enSjxzGMOyXxzMbrkHbjxPrjTSXmD1i96zn323B+ZClNaJW3uKnn0rHtNNEYCgFj3J++D0ckIpVUCAP29Sf/gzXfCV0gCgNyqrJfXKTM/uN43Exi+9XafcMzcx4g2NJ7I/Sy6DfPD/t6kXyRo4wPeDSBLN7UaJG0eaCXoL0wrQf/EtArUEPM/0IVoaq9QzFagM10Zj3DMBmjsSr5YsoKcDjp++3W73ZdnZjsqp7u+eF0ugzAGEFIb7+z4TrfOtImJX1qQeRLrEACItK/vcQJjq0yiglyO38vyJPp9ComEyxQAFueC2rXKrB8Aioa3uqwGdZ45aXL+oMqT+DsUADjsWqPRQ0s7bvVdVSZHuqDM/pyFDBBIqN0uVPar06WjJcZIw1zHMZoJU4cAwDFP3p3Wg9rjlVjBsAFyvEyqYT0xxuRF31BkKiQR1iileZgPygFlRZct3dQjp2yBHMcojLKxTCLPA2pKN2X1gM4Dalpr84Caus9sF9T0TW87ICE7sF2QsN9BVg/oE9l4vqD7qptBg+HpkFAMAKS1oH43czVnXiEGgpQaVoVjAGvJGAier5799vLHqSLg0L+JBzSRjedPtn11TxaPl+vjLcEAtZKlNesh7BdVCUsUVUtavQAAAABJRU5ErkJggg=='

PL_bars = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFqSURBVFiFY2AYBUMAMJKq4bSjQdpXBtZiAsr+czH9qjfbe3ElKWazkOqYf4wMUie/ykvt+KjxFZeaUP6LHMbcj8RINZtkxzAwMDC8/83179ZP8V+45D/+5yDLXCZyNNEKjDoGFxh1DC4w6hhcYNQxuMCgcgzLGWNj1u+cv3gIKeTjYvylv+sSzvoIFzjhac73+/M3ZkLqOL+zfWFkYGD4T6oFtAKMp50NXG//EF5S+izgJy5FTjy3uBKETx53PnDK95ilJedf5i8chAyW4P3+TXX7nZ8H7U2elr3wZ3zyS+APLrXNklvZtTmeZ5Bcu1odP/6dgYHhO6n6iAGDKgEPKseQ1QgiBTAyMvzLFj7C/eMf819cahRY33HRxTEczL9S1Tle8hJS95eB4RTNHWO299IOYtUOvjQjzfaJp0FiO85uiwDzd1bm////0dwxfxn+XOJgZEjQ43yGV+H/f/8e09oxo2AUjIJhCQAz2GOzac75qgAAAABJRU5ErkJggg=='

PL_operations = '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'

PL_letter_forall = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHRSURBVFiF7ZfLK0RRHMc/w0SKxAKh5LGjZum1sFDYCVn4D2Q1K6KslIVkOcrCoxRlheymzFZqNoqkZKRsvPJoCg2Lubd+546Z6z4tzLdOnXvu7/f9fe6959xzL+SVlztaAR5Ea3Po12DwW7GSPAB8iTbvEGba4NdvJbkASIjkBBBwAHMivG6AQqsGc6hX020TJGTwmbNj0gikhEnEJsyC8EgBLTZ9iAmje6DIYn4AuBIesVzBQROzVaBH61cCg0DUAkwH6ZWka81CboZKgEfUZ263vQCluYoVmMAkgR1715GhbeDVqUkn7tyZLqcguk6F6eEvc6Ii5xxn7ylFk8I4BTSZxNcBnyJnyi0QgGrgXZjPmsTPiNgPoNZNGIA9UeCC3Lf9TMTuuw0CMMTvJmS7IW7YC5ggcCuKLGeJi4iYO6DYCxiARVHoifRLUapIA9BjlrwCAWhFfQSjhvMjhvMhL2EAjsg+OeUkP/YaBGAcddnWaONVqMt/wg+YcuBNFA1r42ExlgQq/IAB2BSF49pYXIxt+QUC0Is6UccMx31+wgSAS1H8WfSvMf80+VG2krSiG+K4TPTXSW+mvqoedWfWd/Rmv0F07aL+KR78FUhe/1Pfj6HFIWtnXJQAAAAASUVORK5CYII='

PL_equ = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEGSURBVFiF7dSvSwNhHMDh55xZNhGMhlVRMJwgDA1W/wNxYFM3ZvUvMBhFEASxu2axim2IYFkTZtCiYDP4gxluiKgb/jg5kfeJd/d9+XDf4wiCIAj+i1V5K8rfGe1Lu8WTksiOirolhWxjNh1gCuNyzlSVPjuaSz0GGq7M2PNgFBtiOSOONbV7jUW/EvNa1YK2LZx4NG/b5ddiKtZRTDGpiAmRGyx2VvnOx2uKzWIwxZhbNNESGTPpWsNFiuenr9s3M43lHvd/6hxrby/2d3n4CAPYxRBOOwdkahiHuEMt4xYkq6rhHvvIZ5uTiCWrakn+sJkroC55S3MZt7wo+yPrCoIgCNLwDFFNLXUN09STAAAAAElFTkSuQmCC'

PL_logoinaa = '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'

PL_logoinrim_white = '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'

PL_logoinrim = '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'