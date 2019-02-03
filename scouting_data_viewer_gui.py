#!/usr/bin/env python
"""
Created on Sun Jan 21 13:36:04 2018

@author: rober
"""

"""The module that contains the main application."""

import tkinter as tk
import math
import os

import scouting_data_getters as sdg
import games as gms
import graph as gph
import save_data as sd

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

        def get_game():
            """Return the current game."""
            return self.game
        
        #scouting methods
        def set_comp_tkevent(*args):
            """
            Set the competition and update the comp_notice label.
            Called when a competition is chosen.
            """
#            print('Setting event')
            self.comp_notice.set('Comp set to ' + self.comp_choose_var.get())
            set_comp()
        
        def year_from_comp(comp):
            """
            Return the year from the comp name.
            
            Parameters:
                comp: The comp name to get the year from.
            """
            return ''.join([c for c in comp if c in '0123456789'])
#            result = ''
#            for char in comp: #This assumes that the only digits in the comp name are in the year
#                if char in '0123456789':
#                    result += char
#                else:
#                    return result
#            return result
        
        def set_comp(startup=False):
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
            
            comp = self.state.comp #Makes the next line of code shorter
            year = year_from_comp(comp)
                  
            if year: #Don't do anything with an empty year
#                self.m_wid = 1200 #Twice the max width of graph data panels
#                                  #Don't ask why, I don't know
                
                #Get scouting
                self.game = sdg.get_game(folder=self.state.comp) #The folders are named after comp codes
                
                #Get the raw data, just as the scouters entered it
                self.state.raw_scouting = sdg.get_raw_scouting_data(folder=self.state.comp)
                
                #Get the processed data
                self.state.raw_scouting = get_game().process_scouting(self.state.raw_scouting) 
                
                #Get contrs and averages
                #Histograms for the scores a team gets in a match for each category:
                self.state.contrs = gms.contrs(self.state.raw_scouting, get_game())
                #The average a team scores in a match for each category:
                self.state.averages = gms.averages_from_contrs(self.state.contrs) 
                
                #Get categories
                #Access the first team in raw_scouting, access its first match, and get the keys
                self.state.teams = list(self.state.contrs.keys()) #The teams are the keys
                self.state.teams.sort(key=lambda s: int(s))
                
                first_team = self.state.teams[0]
                scouting_cats = self.state.raw_scouting[first_team][0][1].keys()
                
                #All the categories both in the game categories and the scouting categories
                self.state.categories = gms.get_cats(scouting_cats, get_game().categories)
                #All the number categories (pretty much everything except comments)
                self.state.numeric_cats = gms.get_cats(scouting_cats, get_game().numeric_categories, numeric=True)
                
                #Get teams
                config_teams_frame()
                config_ranking_frame()
                
                self.state.save()
                
        def config_teams_frame():
            """Set up the frame that shows a list of teams in the current competition."""
#            print('configging teams frame')
            self.state.teams.sort(key=lambda t: int(t)) #Sort the teams in increasing numerical order.
            num_in_chunk = 10 #How many teams to display per line.
            
            self.teams_text.config(state=tk.NORMAL) #Can be edited
            self.teams_text.delete('1.0', tk.END) #Clear entire panel
            self.teams_text.insert(tk.INSERT, '\n') #Start with a newline for spacing
            teams_list_title = 'Teams:\n'
            half_title_len = (len(teams_list_title) - 1) // 2
            self.teams_text.insert(tk.INSERT, ' ' * (3*num_in_chunk + 10 - half_title_len) + 'Teams:\n') #Center-align 'Teams:'
            #Explanation for 3*num_in_chunk + 10 - half_title_len:
            #When the teams are printed, they are padded so each team takes up six characters
            #and each line is padded with then spaces at the left
            #So a line might look like this:
            #0123456789012345678901234567890123456789
            #          63    830   3991  1234  4335<End of line
            #
            #The word 'Teams' should be centered above the list of teams
            #Because each team takes six characters, the spot at the center of the team list
            #Will be three characters to the right for each team:
            #                      Center:
            #                        ><
            #            1  2  3  4  5
            #          123123123123123            
            #          63    830   3991  1234  4335<End of line
            #
            #So a naïve approach would be to put 10 + 3*num_in_chunk spaces before 'Teams:':
            #                      Center:
            #                        ><
            #                         Teams:
            #            1  2  3  4  5
            #          123123123123123
            #          63    830   3991  1234  4335<End of line
            #
            #But that makes the title a bit to the right
            #instead of having the left end of the title be centered,
            #we want the center of the title to be centered
            #And the center of the title is halfway through, so if we move the title
            #n/2 characters to the left, where n = len(title),
            #the center will be centered:
            #
            #                      Center:
            #                        ><
            #                      <<<
            #                      Teams:
            #            1  2  3  4  5
            #          123123123123123
            #          63    830   3991  1234  4335<End of line
            #
            #                 Without annotations:
            #
            #                      Teams:
            #          63    830   3991  1234  4335<End of line
            
            num_teams = len(self.state.teams)
            num_of_chunks = math.ceil(num_teams / num_in_chunk)

#            for i in range(0, int((len(self.state.teams) / num_in_chunk) + 1)): #Go through teams in chunks
            for i in range(0, num_of_chunks): #Go through teams in chunks
                string = ' ' * 10 #Buffer space
                for j in range(0, num_in_chunk):
                    index = num_in_chunk*i + j #The index of the team in the teams list
                    if(index < len(self.state.teams)): #Don't go past the end of the list
                        team = self.state.teams[index]
                        ln = len(team)
                        string += team + ' '*(6-ln) #Pad the string to six characters
                        
                self.teams_text.insert(tk.INSERT, string + '\n') #Add a line
            self.teams_text.config(state=tk.DISABLED) #Make it so the teams list can't be modified
        
        def get_weight(cat):
            """
            Return the current weight for the given category.
            
            Parameters:
                cat: The category to get the weight for.
            """
            string = self.cat_weight_fields[cat].get() #The string entered for the category weight
            return float(string) if len(string) > 0 else 0 #Empty strings are counted as 0
                                                           #slackers
        
        def get_default_weights():
            """Return the default weights for the current game."""
            weights = get_game().default_weights
            teams = self.state.teams
            result = {}
            for team in teams:
                result[team] = get_score(self.state.averages[team], weights=weights)
            return result
        
        def get_score(avs, weights=None, weight_func=None, verbose=False):
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
            for cat in self.state.numeric_cats:
                if verbose: #Debug info
                    print(avs.get(cat, 0), float(weight_func(cat)))
                score += avs.get(cat,0) * float(weight_func(cat)) #Add the average times the weight
            return score
            
        def score(team):
            """
            The score for a team given the current weightings.
            
            Parameters:
                team: The team to return the score for.
            """
            avs = self.state.averages[team]
            score = get_score(avs, weight_func=get_weight)
            return score
        
        def config_ranking_frame():
            """Set up the frame that displays scores and ranks for the teams"""
            
            def refresh_rankings():
                """Set up the rankings for each team"""
                
                self.team_ranks_panel.pack_forget() #Get rid of the old rankings
                self.team_ranks_panel = tk.Frame(self.ranking_frame) #Make a new ranks panel
                self.team_ranks_panel.grid(row=3, column=0) #Add the panel
                
                self.team_ranks_textbox = tk.Text(self.team_ranks_panel, width=24, wrap=tk.NONE) #The textbox with the ranking and score information
                self.team_ranks_textbox.pack(side=tk.TOP) #Add the team ranks textbox
                
                r_teams = self.state.teams[:] #The teams to show ranks for
                r_teams.sort(key=lambda t:-score(t)) #Sort the teams by score in descending order
                
                for i in range(0, len(r_teams)): #Add the teams to the team ranks textbox one at a time
                    team = r_teams[i] #Get the team to add
                    num_string = str(i+1)
                    num_string = num_string + ':' + (' ' * (4-len(num_string)))
                    string = num_string + str(team) #The rank and the team
                    string += ' ' * (11-len(string)) + 'with ' + '%.2f' % score(team) #The score of the team
                    if i != len(r_teams) - 1: #Add newlines after every string but the last
                        string += '\n'
                    self.team_ranks_textbox.insert(tk.INSERT, chars=string) #Add the string to the team ranks textbox
                
                self.team_ranks_textbox.config(state=tk.DISABLED, height=30) #Make it so the team ranks textbox can't be edited 
                
                do_easter_eggs() #Trigger any appropriate easter eggs
                    
            for child in self.ranking_frame.winfo_children(): #Get rid of all the child widgets
                child.destroy()
            
            #namespace = {'get_conf_canv': get_conf_canv,
            #             'refresh_rankings': refresh_rankings}
            
            self.ranking_scroll = tk.Scrollbar(self.ranking_frame, orient=tk.HORIZONTAL) #Make a scrollbar for the weight setting
            
            self.rank_box_canvas = tk.Canvas(self.ranking_frame, relief=tk.RAISED, xscrollcommand=self.ranking_scroll.set) #Make a convas to put the weight setters in
                                                                                                                           #We need to do this because we're using a scrollbar and scrollbars are jank in tk
            
            self.rank_box_canvas.grid(row=0, column=0) #Add the rank box canvas
            self.ranking_scroll.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W) #Add the rank box scrollbar
            self.rank_box_frame = tk.Frame(self.rank_box_canvas, relief=tk.RAISED) #The frame to put the weight setters in
            self.rank_box_frame.grid(row=0, column=0) #Add the rank box frame
            self.rank_box_frame.bind('<Configure>', get_conf_canv(self.rank_box_canvas, width=1343, height=50)) #Set the config method to config the canvas to the right dimensions
            self.rank_box_canvas.create_window((0, 0), window=self.rank_box_frame, tags='self.rank_box_frame') #Make a place in the canvas for the frame
                                                                                                               #(Because tk scrollbars are jank)
            self.ranking_scroll.config(command=self.rank_box_canvas.xview) #Link the scrollbar to the rank box canvas
            #*************************************************************
            self.ranking_refresh_button = tk.Button(self.ranking_frame, text='Refresh Rankings', command=refresh_rankings) #The button to refresh the rankings
            self.ranking_refresh_button.grid(row=2, column=0) #Add the ranking refresh button
            
            self.team_ranks_panel = tk.Frame(self.ranking_frame) #The panel for the team ranks
            self.team_ranks_panel.grid(row=3, column=0) #Add the team ranks panel
            
            self.cat_weight_fields = {} #Set the weight map to empty
            
            for cat in self.state.numeric_cats: #Construct weight-setting panel
                entry_panel = tk.Frame(self.rank_box_frame, relief=tk.RAISED) #An empty panel to put the weight setter in
                entry_panel.pack(side=tk.LEFT) #Add the panel
                
                label = tk.Label(entry_panel, text=cat) #The label for the category
                label.pack(side=tk.TOP) #Add the label to the entry panel
                entry = tk.Entry(entry_panel) #The textbox for entering the weight
                
                default_weight = str(get_game().default_weights[cat]) #Get the default weight for the category
                entry.insert(index=0, string=default_weight) #Add the default weight to the weight textbox
                entry.pack(side=tk.TOP) #Add the textbox to the entry panel
                
                self.cat_weight_fields[cat] = entry
            
        #end scouting methods
        
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
            for data_type in self.state.categories: #Add all the data types
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
            for data_type in self.state.categories:
                result += data_type.__str__() + '  '
                
            return result.rstrip()
        
        def do_easter_eggs():
            """Trigger any appropriate easter eggs"""
            
            ee.do_weight_eggs(get_weight, get_game().default_weights, self.state.numeric_cats)
            
            weights = {} #Collect the ranks
            for team in self.state.teams:
                weights[team] = score(team)
            ee.do_rank_eggs(weights, get_default_weights())
            ee.do_gen_eggs()
        
        def show_summary(dummy_event=None):
            """Show the graphs and whatnot for a team."""
            
            team = self.team_summary_team_field.get().strip() #Get the team from the team textbox    
            self.team_summary_inner_frame.pack_forget() #Get rid of the old frame
            key = self.state.comp, team #The key for caching data
            
            def save_summary(summary):
                """
                Save the current summary to the state variable
                
                Parameters:
                    summary: The summary to save.
                """
                
                string = summary.get("1.0",'end-1c') #Get all the text
                do_easter_eggs()
                self.state.summaries[key] = string #Add the summary data to state.summaries
                self.state.save() #Save the state (writes to a file)
            prev_summary = self.state.summaries.get(key, '') #The summary when the gui was last closed
            
            raw_scouting = self.state.read_with_default('raw_scouting', val={})
            raw_team_scouting = raw_scouting.get(team, []) #Scouting for this team
            scouting_string_list = [get_column_string()] #The column headers should be at the top
            
            lens = [len(scouting_string_list[0])] #start with len of column string
            for match, line_data in raw_team_scouting: #Collect list of scouting strings, insert later
                string = get_match_scouting_string(match, line_data) #Get the scouting string
                lens.append(len(string)) #Add the length of this string to the lens list
                scouting_string_list.append(get_match_scouting_string(match, line_data)) #Add the scouting string
            av_string = get_match_scouting_string('Avs:', self.state.averages[team]) #The string for the averages
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
            self.team_summary_inner_frame.bind('<Configure>', get_conf_canv(scouting_text_canvas, width=1000, height=400)) #Set the configuring to configure the frame to the right dimensions
            
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
            
            for category in self.state.numeric_cats: #Add a graph for each category
                prediction = self.state.contrs[team][category] #Use scouted contrs
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
        
        def config_canvas(canvas, width=1343, height=650):
            """
            Configure the given canvas with the given dimensions.
            
            Parameters:
                width: The width to configure the canvas with.
                height: The height to configure the canvas with.
            """
            
            canvas.configure(scrollregion=canvas.bbox('all')) #Make the canvas scorollable
            canvas.config(width=width,height=height) #Configure the width and height
        
        def get_conf_canv(canvas, width, height):
            """
            Return a lambda that configs the given canvas to the given width and height.
            
            Parameters:
                canvas: The canvas to config
                width: The width to set the canvas to
                height: The height to set the canvas to
            """
            
            return lambda event: config_canvas(canvas, width, height)
        
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
                        'competition_frame':self.competition_frame,
                        'ranking_frame':self.ranking_frame,
                        'parent':self.parent}
#            print('self: ' + str(self))
            make_gui_from_html_file('menu.html', root=self, namespace=namespace)
            #add_to_namespace(widgets) None are used
        
        def setup_team_summary_frame():
            """Set up the team summary frame."""
            
            def get_config_func(canvas):
                return lambda e: config_canvas(canvas)
            
            namespace = {#'config_canvas':config_canvas,
                         'get_config_func':get_config_func,
                         'show_summary':show_summary}
#            print('config_canvas: ' + str(config_canvas))
            widgets, _ = make_gui_from_html_file('team_summary_frame.html', root=self, namespace=namespace)
            add_to_namespace(widgets)
            self.active_frame = self.scouting_frame #This frame is the frame to start from
        
        def setup_comp_frame():
            """Set up the team competition frame."""
            
            #vars
            self.comp_notice = tk.StringVar() #The variable to show any messages in
            self.contrs_from_team_from_category = {} #A dict from categories to dicts from teams to dicts to scores to probabilities
            self.state.categories = [] #The current categories
            #end vars
            
            comp = self.state.read_with_default('comp', '', write=True) #Get the comp from the state, make it '' if there is none
            
            comps = set(sdg.get_all_comps())
            self.comp_choose_var = tk.StringVar()
            self.comp_choose_var.set(comp)
            self.comp_choose_var.trace('w', set_comp_tkevent)
            
            namespace = {'comps': comps,
                         'comp_choose_var': self.comp_choose_var,
                         'comp_notice': self.comp_notice}
            
            widgets, _ = make_gui_from_html_file('comp_frame.html', root=self, namespace=namespace, add_element='none')
            add_to_namespace(widgets)
        
        def setup_ranking_frame():
            """Set up the ranking frame."""
            
            self.ranking_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1) #Make the frame
        
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
        set_comp(startup=True)

def main():
    """Run the scouting data viewer."""
    
    print('Running scouting data viewer')
    
    root = tk.Tk() #Make the root
    root.geometry('350x250+300+300') #Set the dimensions and location
    tk.app = ZScoutFrame(root) #Make the main frame
    root.mainloop() #Start

if __name__ == '__main__':
    main() #Run
