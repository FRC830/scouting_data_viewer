#!/usr/bin/env python
"""
Created on Sun Jan 21 13:36:04 2018

@author: rober
"""

"""The module that contains the main application."""

import tkinter as tk
import math
import os

import save_data as sd

import team_summary_frame
import comp_frame
import ranking_frame

import easter_eggs as ee

from html_to_tk import make_gui_from_html_file

GRAPH_WIDTH = 600

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
        return self.comp_frame.get_scouting_data().categories
    
    def get_numeric_categories(self):
#        return self.state.numeric_cats
        return self.comp_frame.get_scouting_data().numeric_cats
    
    def get_contr(self, team, category):
#        return self.state.contrs[team][category]
        return self.comp_frame.get_scouting_data().contrs[team][category]
    
    def get_averages(self):
#        return self.state.averages
        return self.comp_frame.get_scouting_data().averages
    
    def get_teams(self):
#        return self.state.teams
        return self.comp_frame.get_scouting_data().teams
    
    def get_comp(self):
        return self.comp_frame.get_scouting_data().comp
    
    def get_raw_scouting(self):
        return self.comp_frame.get_scouting_data().raw_scouting
    
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
        ### Setup Variables
#            self.state.teams.sort(key=lambda t: int(t))
        teams_in_row = 10
        left_padding_size = 10
        teams_displayed = 10

        # Reset Panel
        self.teams_text.config(state=tk.NORMAL)
        self.teams_text.delete('1.0', tk.END)
        self.teams_text.insert(tk.INSERT, '\n')

        # Center-align 'Teams:'
        teams_list_title = 'Teams:\n'
        half_title_len = (len(teams_list_title) - 1) // 2
        title_padding = (left_padding_size + 3 * teams_in_row - half_title_len) * ' '
        self.teams_text.insert(tk.INSERT, title_padding + teams_list_title)

        num_teams = len(self.get_teams())
        rows = math.ceil(num_teams / teams_in_row)

        # Display teams
        for i in range(rows):
            if (i + 1) * teams_in_row > num_teams: # change the number of teams to the leftover
                teams_displayed = num_teams % teams_in_row
            format_code = left_padding_size * " " + "{: <6}" * teams_displayed+ "\n"
#                print("starting team:", i * teams_in_row, i * teams_in_row + teams_displayed)
            team_list = self.get_teams()[i * teams_in_row:i * teams_in_row + teams_displayed]
            self.teams_text.insert(tk.INSERT, format_code.format(*team_list))
        self.teams_text.config(state=tk.DISABLED)
    
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
        return self.comp_frame.get_scouting_data().game
    
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
        
        def get_go_to_frame(frame):
            """
            Return a function that goes to the frame.
            
            Parameters:
                frame: The frame the function will go to when called
            """
            return lambda *args, **kwargs: go_to_frame(frame)
        
        def go_to_frame(frame):
            """
            Go to the passed frame.
            
            Parameters:
                frame: The frame to go to
            """
            
            if self.active_frame == frame:
                #Already at the frame to go to
                return
            
            self.active_frame.pack_forget() #Remove the current frame from the gui
            frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True) #Add the new frame to the gui
            self.active_frame = frame #Update the active frame
        #end frame methods
        
        def add_to_namespace(widgets):
            """
            Make variables for the given widgets.
            
            Parameters:
                widgets: The widgets to add variables for.
            """
            for name in widgets:
                widget = widgets[name]
                setattr(self, name, widget)
        
        def setup_menu():
            """Set up the menu frame menu."""
            namespace = {'get_go_to_frame':get_go_to_frame,
                        'scouting_frame':self.team_summary_frame.scouting_frame,#self.scouting_frame,
                        'teams_frame':self.teams_frame,
                        'competition_frame':self.comp_frame.competition_frame,
                        'ranking_frame':self.ranking_frame.ranking_frame,
                        'parent':self.parent}
            make_gui_from_html_file('menu.html', root=self, namespace=namespace)
        
        def setup_team_summary_frame():
            """Set up the team summary frame."""
            
            self.team_summary_frame = team_summary_frame.TeamSummaryFrame(self)
            
            self.active_frame = self.team_summary_frame.scouting_frame #This frame is the frame to start from
            self.team_summary_frame.scouting_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        def setup_comp_frame():
            """Set up the team competition frame."""
            self.comp_frame = comp_frame.CompFrame(self)
        
        def setup_ranking_frame():
            """Set up the ranking frame."""
            self.ranking_frame = ranking_frame.RankingFrame(self)
        
        def setup_teams_frame():
            """Set up the teams frame."""
            
            self.teams_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1) #The teams frame
            self.teams_text = tk.Text(self.teams_frame, wrap=tk.NONE, width=1200) #The text to show the teams in
            self.teams_text.pack(side=tk.TOP, padx=0, pady=5) #Add the teams text
        
        self.parent.title('Scouting Viewer') #Set the title of the gui
        self.pack(fill=tk.BOTH, expand=True) #Add the frame
        
        #The only place where self.year is accessed is right after it's set
        #So setting it anywhere else is pointless
        
        #Set up all the frames
        setup_team_summary_frame()
        setup_comp_frame()
        setup_ranking_frame()
        setup_teams_frame()
        setup_menu()
        
#        set_comp(startup=True)
        self.comp_frame.set_comp(startup=True)

def main():
    """Run the scouting data viewer."""
    
    print('Running scouting data viewer')
    
    root = tk.Tk() #Make the root
    root.geometry('350x250+300+300') #Set the dimensions and location
    tk.app = ZScoutFrame(root) #Make the main frame
    root.mainloop() #Start

if __name__ == '__main__':
    main() #Run
