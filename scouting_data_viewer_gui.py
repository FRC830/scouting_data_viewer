#!/usr/bin/env python
"""
Created on Sun Jan 21 13:36:04 2018

@author: rober
"""

"""The module that contains the main application."""

import tkinter as tk

import os
import sys
dirname = os.path.dirname(os.path.realpath(__file__))
directory = os.path.join(dirname, 'gui_frames')
sys.path.append(directory)

import menu
import team_summary_frame
import teams_frame
import comp_frame
import ranking_frame

import easter_eggs as ee

class ScoutingDataViewerFrame(tk.Frame):
    """The frame the ZScout Gui is in."""
           
    def __init__(self, parent):
        """
        Make a ZScoutFrame.
        
        Parameters:
            parent: The parent of the frame.
        """
        
        tk.Frame.__init__(self, parent, background='white')
        self.parent = parent
            
        self.init_gui()
    
    def get_scouting_data(self):
        return self.competition_frame.get_scouting_data()
    
    def get_scouting_datas(self):
        return self.competition_frame.get_scouting_datas()
    
#    def get_categories(self):
#        return self.competition_frame.get_scouting_data().categories
#    
#    def get_numeric_categories(self):
#        return self.competition_frame.get_scouting_data().numeric_cats
#    
#    def get_contr(self, team, category):
#        return self.competition_frame.get_scouting_data().contrs[team][category]
#    
#    def get_averages(self):
#        return self.competition_frame.get_scouting_data().averages
#    
#    def get_teams(self):
#        return self.competition_frame.get_scouting_data().teams
#    
#    def get_comp(self):
#        return self.competition_frame.get_scouting_data().comp
#    
#    def get_raw_scouting(self):
#        return self.competition_frame.get_scouting_data().raw_scouting
#    
#    def get_game(self):
#        """Return the current game."""
#        return self.competition_frame.get_scouting_data().game
    
#    def get_weight(self, cat):
#        return self.ranking_frame.get_weight(cat)
#    
#    def score(self, team):
#        return self.ranking_frame.score(team)
#    
#    def get_default_points(self):
#        return self.ranking_frame.get_default_points()
        
#    def get_game_datas(self):
#        return self.self #TODO real implementation
    
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
    
    def init_gui(self):
        """Initialize the user interface."""
        
        self.team_summary_frame = team_summary_frame.TeamSummaryFrame(self)
        self.active_frame = self.team_summary_frame.scouting_frame #This frame is the frame to start from
        self.team_summary_frame.scouting_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.competition_frame = comp_frame.CompFrame(self)
        
        self.ranking_frame = ranking_frame.RankingFrame(self)
        
        self.teams_frame = teams_frame.TeamsFrame(self)
        
        self.parent.title('Scouting Viewer') #Set the title of the gui
        self.pack(fill=tk.BOTH, expand=True) #Add the frame
        
        self.competition_frame.set_comp(startup=True)
        
        self.menubar = menu.Menubar(self)

def main():
    """Run the scouting data viewer."""
    
    print('Running scouting data viewer')
    
    root = tk.Tk() #Make the root
    
    root.state('zoomed')
    tk.app = ScoutingDataViewerFrame(root) #Make the main frame
    root.mainloop() #Start

if __name__ == '__main__':
    main() #Run
