# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 15:39:20 2019

@author: rober
"""

import games

def steamworks_process_match(match):
    """
    Process the match for steamworks.
    
    Parameters:
        match: The match to process.
    """
    if 'caught_rope' in match:
        match = match.copy()
        
        #If the robot hung, it caught the rope.
        match['caught_rope'] |= match['hanging']
    return match

def steamworks_process_scouting(scouting):
    """
    Process the scouting for steamworks.
    
    Parameters:
        scouting: The scouting data to process.
    """
    return games.process_scouting_by_match(scouting, steamworks_process_match)

steamworks_cats = ['auton_lowgoal',
                   'auton_highgoal',
                   'auton_gears',
                   'try_lft_auton_gears',
                   'try_cen_auton_gears',
                   'try_rgt_auton_gears',
                   'lft_auton_gears',
                   'cen_auton_gears',
                   'rgt_auton_gears',
                   'crossed_baseline',
                   'pickup_gears',
                   'dropped_gears',
                   'teleop_lowgoal',
                   'teleop_highgoal',
                   'teleop_gears',
                   'hanging',
                   'caught_rope',
                   'comments']

steamworks_rankings = {'auton_lowgoal':1,
                       'auton_highgoal':3,
                       'auton_gears':30,
                       'try_lft_auton_gears':0,
                       'try_cen_auton_gears':0,
                       'try_rgt_auton_gears':0,
                       'lft_auton_gears':30,
                       'cen_auton_gears':30,
                       'rgt_auton_gears':30,
                       'crossed_baseline':5,
                       'pickup_gears':0,
                       'dropped_gears':0,
                       'teleop_lowgoal':0.3333,
                       'teleop_highgoal':1,
                       'teleop_gears':20,
                       'hanging':50,
                       'caught_rope':0}

STEAMWORKS = games.Game(steamworks_cats, steamworks_cats[:-1], None, steamworks_process_scouting, steamworks_rankings)
games.GAMES_FROM_YEARS['2017'] = STEAMWORKS