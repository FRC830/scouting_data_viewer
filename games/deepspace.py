# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 15:35:48 2019

@author: rober
"""

import games

def bool_conv(val):
    if type(val) is int:
        return val
    if val.lower() == 'true':
        return 1
    if val.lower() == 'false':
        return 0
    return val

def deepspace_process_match(match):
    """
    Process a match for deepspace.
    
    Parameters:
        match: The match to process.
    """
#    match = match.copy()
#    print(list(match))
#    print('')
    match = games.change_names(deepspace_name_dict, match)
#    print(match)
#    print('')
    match['source'] = '830' #For now
    
#    print(match.get('auton_cross_line', 'NONE'))
    
#    crossed_line = int(match.get('auton_cross_line', 'FALSE') == 'TRUE')
    crossed_line = bool_conv(match.get('auton_cross_line'))
    start_level = int(match.get('hab_start_robot', 0))
    start_level = 1 if start_level == 0 else start_level
    match['cross_line_from_l1'] = int(crossed_line and start_level == 1) #==1 kludge
    match['cross_line_from_l2_or_l3'] = int(crossed_line and start_level in [2, 3])
    
    end_habitat = int(match.get('hab_end_robot', 0))
    match['endgame_ramp_l1'] = int(end_habitat == 1)
    match['endgame_ramp_l2'] = int(end_habitat == 2)
    match['endgame_ramp_l3'] = int(end_habitat == 3)
    
#    if('830' in str(match['team_id'])):
#        print('robot: ', match['team_id'])
#    print('crossed_line: ', crossed_line)
#    print('hab_start: ', start_level)
#    print('crossed l1: ', match['cross_line_from_l1'])
#    print('crossed l2 or l3: ', match['cross_line_from_l2_or_l3'])
#    print('')
    
    del match['hab_end_robot']
    del match['hab_start_robot']
    del match['auton_cross_line']
#    del match['team_id']
    
    return match

def deepspace_process_scouting(scouting):
    """
    Process scouting for deepspace.
    
    Parameters:
        scouting: The scouting data to process.
    """
    processed = games.process_scouting_by_match(scouting, deepspace_process_match)
    return processed

deepspace_cats = ['cross_line_from_l1',
                  'cross_line_from_l2_or_l3',
                  'sandstorm_balls_in_cargo_ship',
                  'sandstorm_balls_in_rocket_l1',
                  'sandstorm_balls_in_rocket_l2',
                  'sandstorm_balls_in_rocket_l3',
                  'sandstorm_hatches_in_cargo_ship',
                  'sandstorm_hatches_in_rocket_l1',
                  'sandstorm_hatches_in_rocket_l2',
                  'sandstorm_hatches_in_rocket_l3',
                  
                  'teleop_balls_in_cargo_ship',
                  'teleop_balls_in_rocket_l1',
                  'teleop_balls_in_rocket_l2',
                  'teleop_balls_in_rocket_l3',
                  'teleop_hatches_in_cargo_ship',
                  'teleop_hatches_in_rocket_l1',
                  'teleop_hatches_in_rocket_l2',
                  'teleop_hatches_in_rocket_l3',
                  'teleop_balls_dropped',
                  'teleop_balls_picked_up',
                  'teleop_hatches_dropped',
                  'teleop_hatches_can_pick_up',
                  
                  'endgame_ramp_l1',
                  'endgame_ramp_l2',
                  'endgame_ramp_l3',
                  'endgame_helped_climb',
                  
                  'fouls',
                  'tech_fouls',
                  'source',
                  'comments']

deepspace_name_dict = {'hab_end_robot':'hab_end_robot',
                       'auton_cross_line':'auton_cross_line',
                       'hab_start_robot':'hab_start_robot',
                       'auton_cross_line':'auton_cross_line',
        
                       'auton_ci_ball_cargo':'sandstorm_balls_in_cargo_ship',
                       'auton_ci_ball_rock_1':'sandstorm_balls_in_rocket_l1',
                       'auton_ci_ball_rock_2':'sandstorm_balls_in_rocket_l2',
                       'auton_ci_ball_rock_3':'sandstorm_balls_in_rocket_l3',
                       'auton_ci_hatch_cargo':'sandstorm_hatches_in_cargo_ship',
                       'auton_ci_hatch_rock_1':'sandstorm_hatches_in_rocket_l1',
                       'auton_ci_hatch_rock_2':'sandstorm_hatches_in_rocket_l2',
                       'auton_ci_hatch_rock_3':'sandstorm_hatches_in_rocket_l3',
                       
                       'ball_cargo':'teleop_balls_in_cargo_ship',
                       'ball_rock_1':'teleop_balls_in_rocket_l1',
                       'ball_rock_2':'teleop_balls_in_rocket_l2',
                       'ball_rock_3':'teleop_balls_in_rocket_l3',
                       'hatch_cargo':'teleop_hatches_in_cargo_ship',
                       'hatch_rock_1':'teleop_hatches_in_rocket_l1',
                       'hatch_rock_2':'teleop_hatches_in_rocket_l2',
                       'hatch_rock_3':'teleop_hatches_in_rocket_l3',
                       'ball_dropped':'teleop_balls_dropped',
                       'ball_count':'teleop_balls_picked_up',
                       'hatch_pickup':'teleop_hatches_can_pick_up',
                       'hatch_dropped':'teleop_hatches_dropped',
                       
                       'fouls':'fouls',
                       'tech_fouls':'tech_fouls',
                       
                       'helping_robot_climb':'endgame_helped_climb',
                       
                       'comments':'comments'}

deepspace_rankings = {'cross_line_from_l1':3,
                      'cross_line_from_l2_or_l3':6,
                      'sandstorm_balls_in_cargo_ship':3,
                      'sandstorm_balls_in_rocket_l1':3,
                      'sandstorm_balls_in_rocket_l2':3,
                      'sandstorm_balls_in_rocket_l3':3,
                      'sandstorm_hatches_in_cargo_ship':2,
                      'sandstorm_hatches_in_rocket_l1':2,
                      'sandstorm_hatches_in_rocket_l2':2,
                      'sandstorm_hatches_in_rocket_l3':2,
                      
                      'teleop_balls_in_cargo_ship':3,
                      'teleop_balls_in_rocket_l1':3,
                      'teleop_balls_in_rocket_l2':3,
                      'teleop_balls_in_rocket_l3':3,
                      'teleop_hatches_in_cargo_ship':2,
                      'teleop_hatches_in_rocket_l1':2,
                      'teleop_hatches_in_rocket_l2':2,
                      'teleop_hatches_in_rocket_l3':2,
                      'teleop_balls_dropped':0,
                      'teleop_balls_picked_up':0,
                      'teleop_hatches_dropped':0,
                      'teleop_hatches_can_pick_up':0,
                      
                      'endgame_ramp_l1':3,
                      'endgame_ramp_l2':6,
                      'endgame_ramp_l3':12,
                      'endgame_helped_climb':0, #oh well
                      
                      'fouls':-3,
                      'tech_fouls':-10}

DEEP_SPACE = games.Game(deepspace_cats, deepspace_cats[:-2], None, deepspace_process_scouting, deepspace_rankings)
games.GAMES_FROM_YEARS['2019'] =  DEEP_SPACE

def get_game():
    return DEEP_SPACE