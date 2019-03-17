# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 19:02:05 2019

@author: rober
"""

import scouting_data_getters as sdg
import games

def year_from_comp(comp):
    return [c for c in comp if c in '0123456789']

def get_scouting_datas(comp):
    found_games = sdg.get_games(folder=comp)
    return [ScoutingData(comp, game.game_id) for game in found_games]

class ScoutingData:
    def __init__(self, comp, game_id='matches'):
        year = year_from_comp(comp)
        if not year:
            raise ValueError('comp has no year: ' + comp)
        
        self.comp = comp
        found_games = sdg.get_games(folder=self.comp)
        
        self.game = [game for game in found_games if game.game_id == game_id][0]
#        self.game = sdg.get_game(folder=self.comp) #The folders are named after comp codes
        
        #Get the raw data, just as the scouters entered it
        self.raw_scouting = sdg.get_raw_scouting_data(folder=self.comp)
        
        #Get the processed data
        self.raw_scouting = self.game.process_scouting(self.raw_scouting) 
        
        #Get contrs and averages
        #Histograms for the scores a team gets in a match for each category:
        self.contrs = games.contrs(self.raw_scouting, self.game)
        #The average a team scores in a match for each category:
        self.averages = games.averages_from_contrs(self.contrs) 
        
        #Get categories
        #Access the first team in raw_scouting, access its first match, and get the keys
        self.teams = list(self.contrs.keys()) #The teams are the keys
        
        self.teams.sort(key=int)
        
        first_team = self.teams[0]
        scouting_cats = self.raw_scouting[first_team][0][1].keys()
        
        #All the categories both in the game categories and the scouting categories
        self.categories = games.get_cats(scouting_cats, self.game.categories)
        
        #All the number categories (pretty much everything except comments)
        self.numeric_cats = games.get_cats(scouting_cats, self.game.numeric_categories, numeric=True)