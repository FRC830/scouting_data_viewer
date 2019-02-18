# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 15:32:03 2019

@author: rober
"""

import tkinter as tk

class Menubar:
    def __init__(self, parent):
        self.parent = parent
        self.setup_gui()
    
    def setup_gui(self):
        self.menubar = tk.Menu(self.parent)
        
        self.frame_select = tk.Menu(self.menubar, tearoff=0)
        
        scouting_frame = self.parent.team_summary_frame.scouting_frame
        teams_frame = self.parent.teams_frame.teams_frame
        competition_frame = self.parent.competition_frame.competition_frame
        ranking_frame = self.parent.ranking_frame.ranking_frame
        
        self.frame_select.add_command(label='Scouting', command=self.get_go_to_frame(scouting_frame))
        self.frame_select.add_command(label='Teams', command=self.get_go_to_frame(teams_frame))
        self.frame_select.add_command(label='Competition', command=self.get_go_to_frame(competition_frame))
        self.frame_select.add_command(label='Ranking', command=self.get_go_to_frame(ranking_frame))
        
        self.menubar.add_cascade(label='Sections', menu=self.frame_select)
        
        self.parent.parent.config(menu=self.menubar)
    
    def get_go_to_frame(self, frame):
        """
        Return a function that goes to the frame.
        
        Parameters:
            frame: The frame the function will go to when called
        """
        return lambda *args, **kwargs: self.go_to_frame(frame)
    
    def go_to_frame(self, frame):
        """
        Go to the passed frame.
        
        Parameters:
            frame: The frame to go to
        """
        
        if self.parent.active_frame == frame: #Already at the frame to go to
            return
        
        self.parent.active_frame.pack_forget() #Remove the current frame from the gui
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True) #Add the new frame to the gui
        self.parent.active_frame = frame #Update the active frame
    #end frame methods