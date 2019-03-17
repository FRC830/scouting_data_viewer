# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 13:38:09 2018

@author: rober
"""

class Game:
    """The game for a year."""
    
    def __init__(self,
                 categories,
                 numeric_categories,
                 get_scouting_from_match,
                 process_scouting=lambda s:s,
                 default_weights=None,
                 game_id='matches'):
        
        self.categories = categories
        self.numeric_categories = numeric_categories
        self.get_scouting_from_match = get_scouting_from_match
        self.process_scouting = process_scouting
        
        self.default_weights = default_weights.copy() if default_weights else {}
        for category in self.numeric_categories:
            if not category in self.default_weights:
                self.default_weights[category] = 0
        
        self.game_id = game_id

def put_in_histogram(scouted_amounts):
    """
    Return a one-sum histogram made from the list of contributions given.
    
    Parameters:
        contrs: A list of contributions for one category.
    """
    result = {}
    tot = 0
    for amount in scouted_amounts:
        result[amount] = result.get(amount, 0) + 1
        tot += 1
        
    for amount in result:
        result[amount] = result[amount] / tot
    
    return result

def averages_from_contrs(contrs):
    """
    Return a dict from teams to dicts from categories to average scores.
    
    Parameters:
        contrs: A dict from teams to category contrs.
    """
    result = {}
    for team in contrs.keys():
        result[team] = averages_from_contrs_for_team(contrs[team])
    return result

def averages_from_contrs_for_team(contrs):
    """
    Return a map from categories to average scores.
    
    Parameters:
        contrs: A dict from categories to a dict from amounts scored to probabilities of that amount being scored.
    """
    
    result = {}
    for cat in contrs.keys():
        tot = 0
        cc = contrs[cat]
        for num in cc.keys():
            tot += num * cc[num]
        result[cat] = int(tot*100)/100 #Two decimal places
    return result

def contrs(raw_scouting, game):
    """
    Return a dict from teams to contrs.
    
    Parameters:
        raw_scouting: A dict from teams to scouting data for the teams.
        game: The game.
    """
    contrs = {}
    for team in raw_scouting.keys():
        contrs[team] = team_contrs(raw_scouting[team], game)
        
    return contrs

def team_contrs(team_scouting, game, pr=False):
    """
    Return the contrs from the scouting data.
    
    Parameters:
        team_scouting: The scouting data for the team.
        game: The game.
    """
    cats = game.numeric_categories
    
    contrs = {}
    for num, results in team_scouting:
        if pr:
            print('num, results:', num, results)
            print('')
        for cat in cats:
            if cat in results:
                if not cat in contrs:
                    contrs[cat] = []
                result = results[cat]
                if type(result) in [int, float]: #Ignore 'NA'
                    contrs[cat].append(results[cat])
                
    for cat in contrs:
        contrs[cat] = put_in_histogram(contrs[cat])
        
    return contrs

def get_cats(scouting_cats, game_cats, numeric=False):
    """
    Return all the categories to show.
    
    Parameters:
        scouting_cats: All the categories in the raw scouting data.
        game_cats: The categories the game has.
        numeric: Whether to return all categories or only numeric ones.
    """
    if len(game_cats) == 0:
        result = scouting_cats[:]
        if numeric and 'comments' in result:
            result.remove('comments')
        return result
    return [cat for cat in game_cats if cat in scouting_cats] #intersection

def change_names(name_dict, match_dict):
    """
    Return a new dict with the key names changed as specified in name_dict.
    Keys without a new name specified in name_dict will not be in the returned dict.
    
    Parameters:
        name_dict: The dict from old names to new names.
        match_dict: The scouting data for the match.
    """
    result = {}
    for cat in match_dict:
        if cat in name_dict:
            result[name_dict[cat]] = match_dict[cat]
#        else:
#            result[cat] = match_dict[cat]
#            print('Couldn\'t convert:', cat)
    return result

def process_scouting_by_match(scouting, process_match):
    """
    Return the scouting, processed matchwise with process_match.
    
    Parameters:
        scouting: The data to process.
        process_match: The function that processes a match.
    """
    result = {}
#    print('process_scouting_by_match')
#    print(scouting['830'][0])
    for team in scouting:
        matches = []
        for match in scouting[team]:
            matches.append((match[0], process_match(match[1])))
        result[team] = matches
    return result

def choose_match_from_sources(matches, source_order):
    """
    Return the match data from the best source.
    
    Parameters:
        matches: The list of matches.
        source_order: The order of sources, with best first.
    """
    matches_from_source = {}
    for match_id, match in matches:
        matches_from_source[match['source']] = match_id, match
        
    for source in source_order:
        if source in matches_from_source:
            return matches_from_source[source]
    return None

def combine_scouting_from_sources(scouting, source_order):
    """
    Combine the scouting data from multiple sources.
    
    Parameters:
        scouting: The scouting data.
        source_order: The order of sources, with best first.
    """
    result = {}
    for team in scouting:
        t_scouting = scouting[team]
        ts_from_match_id = {}
        for match_id, match in t_scouting:
            l = ts_from_match_id.get(match_id, [])
            l.append((match_id, match))
            if not match_id in ts_from_match_id:
                ts_from_match_id[match_id] = l
        
        n_ts = []
        match_ids = list(ts_from_match_id)
        match_ids.sort()
        for match_id in match_ids:
            matches = ts_from_match_id[match_id]
            match = choose_match_from_sources(matches, source_order)
#            print(match)
            if match:
                n_ts.append(match)
                
        result[team] = n_ts
    return result

GAMES_FROM_YEARS = {}

import os
import sys
dirname = os.path.dirname(os.path.realpath(__file__))
directory = os.path.join(dirname, 'games')
sys.path.append(directory)

import steamworks
import powerup
import deepspace