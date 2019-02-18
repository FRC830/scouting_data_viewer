# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 18:36:31 2019

@author: rober
"""
#import os

import tkinter as tk

import scouting_data_getters as sdg
from save_data import SaveData
#import games
from scouting_data import ScoutingData

def year_from_comp(comp):
    return [c for c in comp if c in '0123456789']

class CompFrame:
    def __init__(self, parent):
        
        self.parent = parent
        
#        dirname = os.path.dirname(os.path.realpath(__file__))
        self.state = SaveData('comp_frame_state')
        
        self.comp_notice = tk.StringVar() #The variable to show any messages in
        
#        self.parent.state.categories = [] #The current categories
        #end vars
        
        comp = self.state.read_with_default('comp', '', write=True) #Get the comp from the state, make it '' if there is none
        
        self.comps = set(sdg.get_all_comps())
        self.comp_choose_var = tk.StringVar()
        self.comp_choose_var.set(comp)
        self.comp_choose_var.trace('w', self.set_comp_tkevent)
        
        self.setup_gui()
        
    def setup_gui(self):
        self.competition_frame = tk.Frame(self.parent, relief=tk.RAISED, borderwidth=1)
        
        tk.Label(self.competition_frame, text='Competition:').pack(side=tk.TOP, padx=5, pady=5)
        
        comp_choose = tk.OptionMenu(self.competition_frame, self.comp_choose_var, *self.comps)
        comp_choose.pack(side=tk.TOP, padx=5, pady=5)
        
        tk.Label(self.competition_frame, textvariable=self.comp_notice).pack(side=tk.TOP, pady=5)
        
    def set_comp_tkevent(self, *args):
        """
        Set the competition and update the comp_notice label.
        Called when a competition is chosen.
        """
        #            print('Setting event')
        self.comp_notice.set('Comp set to ' + self.comp_choose_var.get())
        self.set_comp()
        
    def set_comp(self, startup=False):
        """
        Set the current competition to the one specified in the comp_choose field, set relevant variables, and get team contribution data.
        
        Parameters:
            startup: Whether the gui is just starting up.
        """
#            self.comp = self.comp_choose.get()
        
        if not startup:
            #If starting up, we should use the competition last opened in a previous run
            
            #If not starting up, then the comp was selected with the dropdown menu
            #we should use the competition entered in the comp text field
            self.state.comp = self.comp_choose_var.get()
        
        if not self.state.comp:
            return
        
        self.state.scouting_data = ScoutingData(self.state.comp)
        
        #Get teams
        self.parent.config_teams_frame()
        self.parent.config_ranking_frame()
        
        self.state.save()
    
    def get_scouting_data(self):
        return self.state.scouting_data