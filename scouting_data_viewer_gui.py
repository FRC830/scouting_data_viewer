#!/usr/bin/env python
"""
Created on Sun Jan 21 13:36:04 2018

@author: rober
"""

"""The module that contains the main application."""

import tkinter as tk
import math
import os

#import scouting_data_getters as sdg
#import games as gms
import graph as gph
import save_data as sd

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
        
        canvas.configure(scrollregion=canvas.bbox('all')) #Make the canvas scorollable
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
        
        #team summary methods
        def get_match_scouting_string(match, line_data):
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
                length = len(line_data_type) #The length of the category string
                inner_length = length - len(data.__str__()) #The whitespace around the data
                result += ' '*math.floor(inner_length /2) + data.__str__() + ' '*math.ceil(inner_length / 2) + ' '*2 #Center-align the info
            
            return result.rstrip()
        
        def get_column_string():
            """Return the string at the top of the scouting summary that labels the columns."""
            result = 'match_id  '
            for data_type in self.get_categories():
                result += data_type.__str__() + '  '
                
            return result.rstrip()
        
        def show_summary(dummy_event=None):
            """Show the graphs and whatnot for a team."""
            
            team = self.team_summary_team_field.get().strip() #Get the team from the team textbox    
            self.team_summary_inner_frame.pack_forget() #Get rid of the old frame
            key = self.get_comp(), team #The key for caching data
            
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
            
            raw_scouting = self.state.read_with_default('raw_scouting', val={})
            raw_team_scouting = raw_scouting.get(team, []) #Scouting for this team
            
            if raw_team_scouting:
                scouting_string_list = [get_column_string()] #The column headers should be at the top
                
                lens = [len(scouting_string_list[0])] #start with len of column string
                for match, line_data in raw_team_scouting: #Collect list of scouting strings, insert later
                    string = get_match_scouting_string(match, line_data) #Get the scouting string
                    lens.append(len(string)) #Add the length of this string to the lens list
                    scouting_string_list.append(get_match_scouting_string(match, line_data)) #Add the scouting string
                av_string = get_match_scouting_string('Avs:', self.get_averages()[team]) #The string for the averages
                lens.append(len(av_string)) #Add the len of the av string to the lens
                scouting_string_list.append(av_string) #Add the av string
                
                scouting_text_pane = tk.Text(self.team_summary_canvas, wrap=tk.NONE) #The text pane with the scouting data in it
                scouting_text_pane.grid(row=0, column=0) #Add the scouting text pane
                
    #            namespace = {'save_summary': save_summary,
    #                         'prev_summary': prev_summary,
    #                         'get_conf_canv': get_conf_canv,
    #                         'scouting_text_pane': scouting_text_pane}
    #            
    #            widgets, _ = make_gui_from_html_file('team_summary_inner_frame.html', root=self.team_summary_canvas_frame, namespace=namespace)
    #            scouting_text_pane = widgets['scouting_text_pane']
                
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
                    
                    graph_data = gph.get_scouting_graph_data(prediction, red_and_blue=False, num_margins=None) #The data to display in the graph
    #                graph_frame = gph.GraphDataPanel(self.team_summary_inner_frame, graph_data, g_height=100, max_width=self.m_wid/2)#, red_and_blue=False) #The graph
                    graph_frame = gph.GraphDataPanel(self.team_summary_inner_frame, graph_data, g_height=100, max_width=GRAPH_WIDTH) #The graph
                    graph_frame.pack(side=tk.TOP, padx=5, pady=5) #Add the graph frame
                    
                    first = False #Now we're not on the first one
        #end team summary methods
        
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
                        'scouting_frame':self.scouting_frame,
                        'teams_frame':self.teams_frame,
                        'competition_frame':self.comp_frame.competition_frame,
                        'ranking_frame':self.ranking_frame.ranking_frame,
                        'parent':self.parent}
#            print('self: ' + str(self))
            make_gui_from_html_file('menu.html', root=self, namespace=namespace)
            #add_to_namespace(widgets) None are used
        
        def setup_team_summary_frame():
            """Set up the team summary frame."""
            
            def get_config_func(canvas):
                return lambda e: self.config_canvas(canvas)
            
            namespace = {#'config_canvas':config_canvas,
                         'get_config_func':get_config_func,
                         'show_summary':show_summary}
#            print('config_canvas: ' + str(config_canvas))
            widgets, _ = make_gui_from_html_file('team_summary_frame.html', root=self, namespace=namespace)
            add_to_namespace(widgets)
            self.active_frame = self.scouting_frame #This frame is the frame to start from
        
        def setup_comp_frame():
            """Set up the team competition frame."""
            
            self.comp_frame = comp_frame.CompFrame(self)
        
        def setup_ranking_frame():
            """Set up the ranking frame."""
            
#            self.ranking_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1) #Make the frame
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
