# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 14:45:12 2019

@author: rober
"""

import math

import tkinter as tk

import graph
from save_data import SaveData

_GRAPH_WIDTH = 600

class TeamSummaryFrame:
    def __init__(self, parent):
        self.parent = parent
        
        self.state = SaveData('team_summary_frame_state')
        self.state.non_override_write('summaries', {})
        
        self.init_gui()
        
    def init_gui(self):
        self.scouting_frame = tk.Frame(self.parent, relief=tk.RAISED, borderwidth=1)
        
        self.team_summary_y_scroll = tk.Scrollbar(self.scouting_frame, orient=tk.VERTICAL)
        self.team_summary_y_scroll.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.team_summary_canvas = tk.Canvas(self.scouting_frame, yscrollcommand=self.team_summary_y_scroll.set)
        self.team_summary_canvas.grid(row=0, column=0)
        
        self.team_summary_canvas_frame = tk.Frame(self.team_summary_canvas)
        self.team_summary_canvas_frame.bind('<Configure>', self.get_conf_canv(self.team_summary_canvas, width=1343, height=650))
        self.team_summary_canvas.create_window((0,0), window=self.team_summary_canvas_frame, anchor='nw', tags='team_summary_canvas_frame')
        self.team_summary_y_scroll.config(command=self.team_summary_canvas.yview)
        
        self.team_summary_team_label = tk.Label(self.team_summary_canvas_frame, text='Team:')
        self.team_summary_team_label.pack(side=tk.TOP, padx=5, pady=5)
        
        self.team_summary_team_field = tk.Entry(self.team_summary_canvas_frame)
        self.team_summary_team_field.pack(side=tk.TOP, padx=5, pady=5)
        
        self.team_summary_team_field.bind('<Return>', self.show_summary)
        
        self.team_summary_button = tk.Button(self.team_summary_canvas_frame, command=self.show_summary, text='Show Summary')
        self.team_summary_button.pack(side=tk.TOP, padx=5, pady=5)
        
        self.team_summary_inner_frame = tk.Frame(self.team_summary_canvas_frame, relief=tk.RAISED, borderwidth=1)
    
    def config_canvas(self, canvas):
        return lambda e: self.parent.config_canvas(e)
    
    def get_conf_canv(self, canvas, width, height):
        return self.parent.get_conf_canv(canvas, width, height)
    
    def get_scouting_data(self):
        return self.parent.get_scouting_data()
    
    def get_comp(self):
        return self.parent.get_scouting_data().comp
    
    def do_easter_eggs(self):
        return self.parent.do_easter_eggs()
    
    def get_categories(self):
        return self.parent.get_scouting_data().game.categories
    
    def get_contr(self, team, category):
        return self.parent.get_scouting_data().contrs[team][category]
    
    def get_raw_scouting(self):
        return self.parent.get_scouting_data().raw_scouting
    
    def get_averages(self):
        return self.parent.get_scouting_data().averages
    
    def get_numeric_categories(self):
        return self.parent.get_scouting_data().game.numeric_categories
    
    def get_match_scouting_string(self, match, line_data):
            """
            Return a string describing the match and line data in human-readable format.
            
            Parameters:
                match: The match to return a scouting string for
                line_data: The data for the match
            """
            
            result = ''
            
            line_data_types = ['match_id'] #The types to put in the scouting string
            line_data['match_id'] = match #Add the match_id to the line_data
            for data_type in self.get_categories(): #Add all the data types
                line_data_types.append(data_type)
                
            for line_data_type in line_data_types: #Add the info for each data type
                data = line_data.get(line_data_type, '') #Retrieve the info, use an empty string if none
                data_str = str(data).replace('\n', ' ')
                length = len(line_data_type) #The length of the category string
                inner_length = length - len(data_str) #The whitespace around the data
                result += ' '*math.floor(inner_length /2) + data_str + ' '*math.ceil(inner_length / 2) + ' '*2 #Center-align the info
            
            return result.rstrip()
    
    def get_column_string(self):
            """Return the string at the top of the scouting summary that labels the columns."""
            result = 'match_id  '
            for data_type in self.get_categories():
                result += data_type.__str__() + '  '
                
            return result.rstrip()
    
    def show_summary(self, dummy_event=None):
        """Show the graphs and whatnot for a team."""
        team = self.team_summary_team_field.get().strip() #Get the team from the team textbox    
        self.team_summary_inner_frame.pack_forget() #Get rid of the old frame
        key = tuple(self.get_categories()), team #The key for caching data
        
        def save_summary(summary):
            """
            Save the current summary to the state variable
            
            Parameters:
                summary: The summary to save.
            """
            
            string = summary.get("1.0",'end-1c') #Get all the text
            self.do_easter_eggs()
            self.state.summaries[key] = string #Add the summary data to state.summaries
            self.state.save() #Save the state (writes to a file)
        
        prev_summary = self.state.summaries.get(key, '') #The summary when the gui was last closed
        
        raw_scouting = self.get_scouting_data().raw_scouting#self.state.read_with_default('raw_scouting', val={})
        raw_team_scouting = raw_scouting.get(team, []) #Scouting for this team
        
        if raw_team_scouting:
            scouting_string_list = [self.get_column_string()] #The column headers should be at the top
            
            lens = [len(scouting_string_list[0])] #start with len of column string
            for match, line_data in raw_team_scouting: #Collect list of scouting strings, insert later
                string = self.get_match_scouting_string(match, line_data) #Get the scouting string
                lens.append(len(string)) #Add the length of this string to the lens list
                scouting_string_list.append(self.get_match_scouting_string(match, line_data)) #Add the scouting string
            av_string = self.get_match_scouting_string('Avs:', self.get_averages()[team]) #The string for the averages
            lens.append(len(av_string)) #Add the len of the av string to the lens
            scouting_string_list.append(av_string) #Add the av string
            
            scouting_text_pane = tk.Text(self.team_summary_canvas, wrap=tk.NONE) #The text pane with the scouting data in it
            scouting_text_pane.grid(row=0, column=0) #Add the scouting text pane
            
            #********************************************************
            self.team_summary_inner_frame = tk.Frame(self.team_summary_canvas_frame, relief=tk.RAISED, borderwidth=1) #The frame for the team summary
            self.team_summary_inner_frame.pack(side=tk.TOP) #Add the team summary inner frame
            
            #Make scouting data viewer
            scouting_text_scrollbar = tk.Scrollbar(self.team_summary_inner_frame, orient=tk.HORIZONTAL) #The scrollbar for the scouting text
            scouting_text_canvas = tk.Canvas(self.team_summary_inner_frame, xscrollcommand=scouting_text_scrollbar.set, width=1000) #The canvas to put the scouting text in
            scouting_text_canvas.pack(side=tk.TOP, fill=tk.NONE) #Add the scouting text canvas
            self.team_summary_inner_frame.bind('<Configure>', self.get_conf_canv(scouting_text_canvas, width=1000, height=400)) #Set the configuring to configure the frame to the right dimensions
            
            scouting_text_scrollbar.pack(side=tk.TOP, fill=tk.X, padx=150, pady=2) #Add the scouting text scrollbar
            scouting_text_scrollbar.config(command=scouting_text_canvas.xview) #Set the scrollbar to horizontal scrolling on scouting_text_canvas
            
            scouting_text_canvas.create_window((0, 0), window=scouting_text_pane, anchor='nw', tags='scouting_text_pane') #Make a place in the scouting text canvas for the pane
            
            #Make editable summary pane
            scouting_editable_summary = tk.Text(self.team_summary_inner_frame, height=5) #The editable summary
            scouting_editable_summary.insert('1.0', prev_summary) #Add the previous summary to the summary textbox
            scouting_editable_summary.pack(side=tk.TOP) #Add the scouting editable summary
            
            save_button = tk.Button(self.team_summary_inner_frame, text='Save', command=lambda *args:save_summary(scouting_editable_summary)) #The button to save the editable summary
            save_button.pack(side=tk.TOP) #Add the save button
            #********************************************************
            #Expand text box to right width
            scouting_text_pane.config(width = max(lens) + 1) #Make the text pane wide enough to hold all its text
            
            for s in scouting_string_list: #Add the strings to the pane
                scouting_text_pane.insert(tk.INSERT, s + '\n') #Add the current string
            scouting_text_pane.config(state=tk.DISABLED) #Make the scouting text pane not editable
            
            #Add the category charts
            
            first=True #To track whether we're on the first category chart
            
            for category in self.get_numeric_categories(): #Add a graph for each category
#                    prediction = self.state.contrs[team][category] #Use scouted contrs
                prediction = self.get_contr(team, category) #Use scouted contrs
                if not first: #Add spacing between the graphs
                    tk.Label(self.team_summary_inner_frame, text=' ').pack(side=tk.TOP, padx=0, pady=5)
                    
                label = tk.Label(self.team_summary_inner_frame, text=category + ':') #The category label
                label.pack(side=tk.TOP, padx=5, pady=5) #Add the label
                
                graph_data = graph.get_scouting_graph_data(prediction, red_and_blue=False, num_margins=None) #The data to display in the graph
#                graph_frame = gph.GraphDataPanel(self.team_summary_inner_frame, graph_data, g_height=100, max_width=self.m_wid/2)#, red_and_blue=False) #The graph
                graph_frame = graph.GraphDataPanel(self.team_summary_inner_frame, graph_data, g_height=100, max_width=_GRAPH_WIDTH) #The graph
                graph_frame.pack(side=tk.TOP, padx=5, pady=5) #Add the graph frame
                
                first = False #Now we're not on the first one