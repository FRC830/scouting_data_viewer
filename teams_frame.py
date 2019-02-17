# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 15:23:21 2019

@author: rober
"""

import math

import tkinter as tk

class TeamsFrame:
    def __init__(self, parent):
        self.parent = parent
        
        self.setup_gui()
    
    def setup_gui(self):
        self.teams_frame = tk.Frame(self.parent, relief=tk.RAISED, borderwidth=1) #The teams frame
        self.teams_text = tk.Text(self.teams_frame, wrap=tk.NONE, width=1200) #The text to show the teams in
        self.teams_text.pack(side=tk.TOP, padx=0, pady=5) #Add the teams text
    
    def get_teams(self):
        return self.parent.get_teams()
    
    def config(self):
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