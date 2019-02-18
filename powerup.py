# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 15:37:37 2019

@author: rober
"""

import games

EAGLE_NAME_DICT = {'Crosses the auto line (auto-run)':'cross_line',
                   'Number of Cubes in Exchange':'cube_vault',
                   'Number of cubes in auton':'auton_cube_count',
                   'Number of Cubes on Scale':'cube_scale',
                   'Extra Notes':'comments',
                   'source':'source'}

def zealous_convert(token):
    """
    Convert a token (probably scouted by team 3322) into a 1 or 0.
    
    Parameters:
        token: The token to convert.
    """
    if type(token) is int:
        return token
    if token.lower() in ['yes', 'same side', 'from center', 'in position', 'in the middle', 'true']:
        return 1
    return 0

def eagle_convert_parked(token):
    """
    Convert whether an answer from 3322 about whether a robot parked into a 0 or a 1.
    
    Parameters:
        token: The token to convert.
    """
    if type(token) is int:
        return 0
    if 'parked' in token.lower():
        return 1
    return 0

def eagle_convert_climb(token):
    """
    Convert whether an answer from 3322 about whether a robot climbed into a 0 or a 1.
    
    Parameters:
        token: The token to convert.
    """
    if type(token) is int:
        return token
    if token.lower() == 'yes':
        return 1
    return 0

def powerup_process_match(match):
    """
    Process a match for powerup.
    
    Parameters:
        match: The match to process.
    """
    match = match.copy()
    
    if match['source'] == 'RAT':
        endgame_action = match.pop('endgame_action')
        match['climbing'] = int(endgame_action == 0) #climbing is action 0
        match['parking'] =int(endgame_action == 1) #parking is action 1
#    if not 'source' in match:
#        match['source'] = 'RAT'
    
    elif match['source'] == '3322':
        n_match = games.change_names(EAGLE_NAME_DICT, match)
#        print(list(n_match))
        n_match['auton_ci_switch'] = zealous_convert(match['Switch capabilities'])
        n_match['auton_ci_scale'] = zealous_convert(match['Scale capabilities'])
        n_match['auton_cube_count'] = 'NA'
        n_match['parking'] = eagle_convert_parked(match['Climb'])
        n_match['climbing'] = eagle_convert_climb(match['Climb'])
        n_match['cube_switch'] = match['Number of Cubes on Own Switch'] + match['Number of Cubes on Opponent\'s Switch']
        n_match['cube_count'] = 'NA'
        n_match['fouls'] = 'NA'
        n_match['tech_fouls'] = 'NA'
        match = n_match
#        print(list(match))
#        print('')

    return match

def powerup_process_scouting(scouting):
    """
    Process scouting for powerup.
    
    Parameters:
        scouting: The scouting to process.
    """
    preprocessed = games.process_scouting_by_match(scouting, powerup_process_match)
    result = games.combine_scouting_from_sources(preprocessed, ['RAT', '3322'])
    return result

powerup_cats = ['cross_line',
                'auton_ci_switch',
                'auton_ci_scale',
                'auton_cube_count',
                'cube_count',
                'cube_switch',
                'cube_scale',
                'cube_vault',
                'fouls',
                'tech_fouls',
                'parking',
                'climbing',
                'hanging',
                'helping_robot',
                'source',
                'comments']
powerup_rankings = {'tech_fouls':0}

POWER_UP = games.Game(powerup_cats, powerup_cats[:-2], None, powerup_process_scouting, powerup_rankings)
games.GAMES_FROM_YEARS['2018'] = POWER_UP