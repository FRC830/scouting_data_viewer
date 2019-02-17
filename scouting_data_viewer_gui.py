#!/usr/bin/env python
"""
Created on Sun Jan 21 13:36:04 2018

@author: rober
"""

"""The module that contains the main application."""

import tkinter as tk
#import math
import os

import save_data as sd

import menu
import team_summary_frame
import teams_frame
import comp_frame
import ranking_frame

import easter_eggs as ee

class ZScoutFrame(tk.Frame):
    """The frame the ZScout Gui is in."""
           
    def __init__(self, parent):
        """
        Make a ZScoutFrame.
        
        Parameters:
            parent: The parent of the frame.
        """
        
        tk.Frame.__init__(self, parent, background='white')
        self.parent = parent
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        
        self.state = sd.SaveData('Gui_state') #The state holds all data that should be persistent across runs
        self.init_state()
        
        self.initUI()
    
    def init_state(self):
        """Initialize the state variable."""
        #If there is not already a 'summaries' variable in state, add one and make it equal to {}
        self.state.non_override_write('summaries', {})
    
    def get_categories(self):
#        return self.state.categories
        return self.competition_frame.get_scouting_data().categories
    
    def get_numeric_categories(self):
#        return self.state.numeric_cats
        return self.competition_frame.get_scouting_data().numeric_cats
    
    def get_contr(self, team, category):
#        return self.state.contrs[team][category]
        return self.competition_frame.get_scouting_data().contrs[team][category]
    
    def get_averages(self):
#        return self.state.averages
        return self.competition_frame.get_scouting_data().averages
    
    def get_teams(self):
#        return self.state.teams
        return self.competition_frame.get_scouting_data().teams
    
    def get_comp(self):
        return self.competition_frame.get_scouting_data().comp
    
    def get_raw_scouting(self):
        return self.competition_frame.get_scouting_data().raw_scouting
    
    def get_weight(self, cat):
        return self.ranking_frame.get_weight(cat)
    
    def score(self, team):
        return self.ranking_frame.score(team)
    
    def get_default_points(self):
        return self.ranking_frame.get_default_points()
    
    def config_ranking_frame(self):
        """Set up the frame that displays scores and ranks for the teams"""
        self.ranking_frame.config()
    
    def config_teams_frame(self):
        """Set up the frame that shows a list of teams in the current competition."""
        self.teams_frame.config()
    
    def do_easter_eggs(self):
        """Trigger any appropriate easter eggs"""
        
        ee.do_weight_eggs(self.get_weight, self.get_game().default_weights, self.get_numeric_categories())
        
        weights = {} #Collect the ranks
        for team in self.get_teams():
            weights[team] = self.score(team)
        ee.do_rank_eggs(weights, self.get_default_points())
        ee.do_gen_eggs()
    
    def get_game(self):
        """Return the current game."""
        return self.competition_frame.get_scouting_data().game
    
    def config_canvas(self, canvas, width=1343, height=650):
        """
        Configure the given canvas with the given dimensions.
        
        Parameters:
            width: The width to configure the canvas with.
            height: The height to configure the canvas with.
        """
        
        canvas.configure(scrollregion=canvas.bbox('all')) #Make the canvas scrollable
        canvas.config(width=width,height=height) #Configure the width and height
    
    def get_conf_canv(self, canvas, width, height):
        """
        Return a lambda that configs the given canvas to the given width and height.
        
        Parameters:
            canvas: The canvas to config
            width: The width to set the canvas to
            height: The height to set the canvas to
        """
        
        return lambda event: self.config_canvas(canvas, width, height)
    
    def initUI(self):
        """Initialize the user interface."""
        
        def setup_menu():
            """Set up the menu frame menu."""
            self.menubar = menu.Menubar(self)
        
        def setup_team_summary_frame():
            """Set up the team summary frame."""
            
            self.team_summary_frame = team_summary_frame.TeamSummaryFrame(self)
            
            self.active_frame = self.team_summary_frame.scouting_frame #This frame is the frame to start from
            self.team_summary_frame.scouting_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        def setup_comp_frame():
            """Set up the team competition frame."""
            self.competition_frame = comp_frame.CompFrame(self)
        
        def setup_ranking_frame():
            """Set up the ranking frame."""
            self.ranking_frame = ranking_frame.RankingFrame(self)
        
        def setup_teams_frame():
            """Set up the teams frame."""
            self.teams_frame = teams_frame.TeamsFrame(self)
        
        self.parent.title('Scouting Viewer') #Set the title of the gui
        self.pack(fill=tk.BOTH, expand=True) #Add the frame
        
        #Set up all the frames
        setup_team_summary_frame()
        setup_comp_frame()
        setup_ranking_frame()
        setup_teams_frame()
        setup_menu()
        
        self.competition_frame.set_comp(startup=True)

def main():
    """Run the scouting data viewer."""
    
    print('Running scouting data viewer')
    
    root = tk.Tk() #Make the root
    
    root.state('zoomed')
    tk.app = ZScoutFrame(root) #Make the main frame
    root.mainloop() #Start

if __name__ == '__main__':
    main() #Run
