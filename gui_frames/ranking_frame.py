# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 13:41:14 2019

@author: rober
"""

import tkinter as tk

class RankingFrame:
    def __init__(self, parent):
        self.parent = parent
        self.setup_gui()
    
    def setup_gui(self):
        self.ranking_frame = tk.Frame(self.parent, relief=tk.RAISED, borderwidth = 1)
        
        self.ranking_scroll = tk.Scrollbar(self.ranking_frame, orient=tk.HORIZONTAL)
        self.ranking_scroll.grid(row=1, column=0)
        
        self.rank_box_canvas = tk.Canvas(self.ranking_frame, relief=tk.RAISED, xscrollcommand=self.ranking_scroll.set)
        self.rank_box_canvas.grid(row=0, column=0)
        
        self.rank_box_frame = tk.Frame(self.ranking_frame, relief=tk.RAISED)
        self.rank_box_frame.grid(row=0, column=0)
        
        self.rank_box_frame.bind('<Configure>', self.parent.get_conf_canv(self.rank_box_canvas, width=1343, height=50))
        self.rank_box_canvas.create_window((0, 0), window=self.rank_box_frame, tags='rank_box_frame')
        self.ranking_scroll.config(command=self.rank_box_canvas.xview)
        
        self.ranking_refresh_button = tk.Button(self.ranking_frame, text='Refresh Rankings', command=self.refresh_rankings)
        self.ranking_refresh_button.grid(row=2, column=0)
        
        self.team_ranks_panel = tk.Frame(self.ranking_frame)
        self.team_ranks_panel.grid(row=3, column=0)
    
    def get_game(self):
        return self.parent.get_scouting_data().game
    
    def get_teams(self):
        return self.parent.get_scouting_data().teams
    
    def get_numeric_categories(self):
        return self.parent.get_scouting_data().game.numeric_categories
    
    def get_averages(self):
        return self.parent.get_scouting_data().averages
    
    def get_scouting_data(self):
        return self.parent_get_scouting_data()
    
    def get_conf_canv(self, canvas, width, height):
        return self.parent.get_conf_canv(canvas, width, height)
    
    def get_weight(self, cat):
        """
        Return the current weight for the given category.
        
        Parameters:
            cat: The category to get the weight for.
        """
        string = self.cat_weight_fields[cat].get() #The string entered for the category weight
        return float(string) if len(string) > 0 else 0 #Empty strings are counted as 0
                                                           #slackers
    
    def get_default_points(self):
        """Return the default weights for the current game."""
        weights = self.get_game().default_weights
        teams = self.get_teams()
        result = {}
        for team in teams:
#                result[team] = get_score(self.state.averages[team], weights=weights)
            result[team] = self.score(team, weights=weights)
        return result
    
    def get_score(self, avs, weights=None, weight_func=None, verbose=False):
        """
        Return the score for a team with avs given a function from categories to weights.
        
        Parameters:
            avs: The average scores for the team. A dict from categories to doubles.
            weights: The weights for each category. A dict from categories to doubles.
            weight_func: The weights for each category. A function from categories to doubles.
            verbose: Whether to print debug info
        """
        if not weights is None:
            weight_func = lambda a: weights[a] #Make a weight_func equivalent to weights
        if weights is None and weight_func is None:
            weight_func = lambda a:0 #If no weight info is passed, all weights are zero
        
        score = 0
        for cat in self.get_numeric_categories():
            if verbose: #Debug info
                print(avs.get(cat, 0), float(weight_func(cat)))
            score += avs.get(cat,0) * float(weight_func(cat)) #Add the average times the weight
        return score
            
    def score(self, team, weight_func=None, weights=None):
        """
        The score for a team for the given weightings.
        
        Parameters:
            team: The team to return the score for.
        """
        weight_func = weight_func if weight_func else self.get_weight
        weight_func = (lambda a: weights[a]) if weights else weight_func
        
        avs = self.get_averages()[team]
        score = self.get_score(avs, weight_func=weight_func)
        return score
    
    def config(self):
        for child in self.ranking_frame.winfo_children(): #Get rid of all the child widgets
            child.destroy()
        
        self.ranking_scroll = tk.Scrollbar(self.ranking_frame, orient=tk.HORIZONTAL) #Make a scrollbar for the weight setting
        
        #Make a convas to put the weight setters in
        #We need to do this because we're using a scrollbar and scrollbars are jank in tk
        self.rank_box_canvas = tk.Canvas(self.ranking_frame, relief=tk.RAISED, xscrollcommand=self.ranking_scroll.set)
        
        self.rank_box_canvas.grid(row=0, column=0) #Add the rank box canvas
        self.ranking_scroll.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W) #Add the rank box scrollbar
        self.rank_box_frame = tk.Frame(self.rank_box_canvas, relief=tk.RAISED) #The frame to put the weight setters in
        self.rank_box_frame.grid(row=0, column=0) #Add the rank box frame
        self.rank_box_frame.bind('<Configure>', self.get_conf_canv(self.rank_box_canvas, width=1343, height=50)) #Set the config method to config the canvas to the right dimensions
        self.rank_box_canvas.create_window((0, 0), window=self.rank_box_frame, tags='self.rank_box_frame') #Make a place in the canvas for the frame
                                                                                                           #(Because tk scrollbars are jank)
        self.ranking_scroll.config(command=self.rank_box_canvas.xview) #Link the scrollbar to the rank box canvas
        #*************************************************************
        self.ranking_refresh_button = tk.Button(self.ranking_frame, text='Refresh Rankings', command=self.refresh_rankings) #The button to refresh the rankings
        self.ranking_refresh_button.grid(row=2, column=0) #Add the ranking refresh button
        
        self.team_ranks_panel = tk.Frame(self.ranking_frame) #The panel for the team ranks
        self.team_ranks_panel.grid(row=3, column=0) #Add the team ranks panel
        
        self.cat_weight_fields = {} #Set the weight map to empty
        
        for cat in self.get_numeric_categories(): #Construct weight-setting panel
            entry_panel = tk.Frame(self.rank_box_frame, relief=tk.RAISED) #An empty panel to put the weight setter in
            entry_panel.pack(side=tk.LEFT) #Add the panel
            
            label = tk.Label(entry_panel, text=cat) #The label for the category
            label.pack(side=tk.TOP) #Add the label to the entry panel
            entry = tk.Entry(entry_panel) #The textbox for entering the weight
            
            default_weight = str(self.get_game().default_weights[cat]) #Get the default weight for the category
            entry.insert(index=0, string=default_weight) #Add the default weight to the weight textbox
            entry.pack(side=tk.TOP) #Add the textbox to the entry panel
            
            self.cat_weight_fields[cat] = entry
    
    def refresh_rankings(self):
        """Set up the rankings for each team"""
        
        self.team_ranks_panel.pack_forget() #Get rid of the old rankings
        self.team_ranks_panel = tk.Frame(self.ranking_frame) #Make a new ranks panel
        self.team_ranks_panel.grid(row=3, column=0) #Add the panel
        
        self.team_ranks_textbox = tk.Text(self.team_ranks_panel, width=24, wrap=tk.NONE) #The textbox with the ranking and score information
        self.team_ranks_textbox.pack(side=tk.TOP) #Add the team ranks textbox
        
        r_teams = self.get_teams()[:] #The teams to show ranks for
        r_teams.sort(key=lambda t:-self.score(t)) #Sort the teams by score in descending order
        
        for i in range(0, len(r_teams)): #Add the teams to the team ranks textbox one at a time
            team = r_teams[i] #Get the team to add
            num_string = str(i+1)
            num_string = num_string + ':' + (' ' * (4-len(num_string)))
            string = num_string + str(team) #The rank and the team
            string += ' ' * (11-len(string)) + 'with ' + '%.2f' % self.score(team) #The score of the team
            if i != len(r_teams) - 1: #Add newlines after every string but the last
                string += '\n'
            self.team_ranks_textbox.insert(tk.INSERT, chars=string) #Add the string to the team ranks textbox
        
        self.team_ranks_textbox.config(state=tk.DISABLED, height=30) #Make it so the team ranks textbox can't be edited 
        
        self.parent.do_easter_eggs() #Trigger any appropriate easter eggs