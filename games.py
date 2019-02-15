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
                 default_weights={}):
        self.categories = categories
        self.numeric_categories = numeric_categories
        self.get_scouting_from_match = get_scouting_from_match
        self.process_scouting = process_scouting
        
        self.default_weights = default_weights.copy()
        for category in self.numeric_categories:
            if not category in self.default_weights:
                self.default_weights[category] = 0

def put_in_histogram(scouted_amounts):
    """
    Return a zero-sum histogram made from the list of contributions given.
    
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

###STEAMWORKS
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
    return process_scouting_by_match(scouting, steamworks_process_match)

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
STEAMWORKS = Game(steamworks_cats, steamworks_cats[:-1], None, steamworks_process_scouting, steamworks_rankings)

###Code for using scouting data from 3322.
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

#POWERUP
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
        n_match = change_names(EAGLE_NAME_DICT, match)
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
    preprocessed = process_scouting_by_match(scouting, powerup_process_match)
    result = combine_scouting_from_sources(preprocessed, ['RAT', '3322'])
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
POWER_UP = Game(powerup_cats, powerup_cats[:-2], None, powerup_process_scouting, powerup_rankings)

#DEEP SPACE
def deepspace_process_match(match):
    """
    Process a match for deepspace.
    
    Parameters:
        match: The match to process.
    """
#    match = match.copy()
    match = change_names(deepspace_name_dict, match)
#    print(match)
#    print('')
    match['source'] = '830' #For now
    
    crossed_line = match.get('auton_cross_line', 'FALSE') == 'TRUE'
    start_level = int(match.get('hab_start_robot', 0))
    match['cross_line_from_l1'] = crossed_line and start_level == 1
    match['cross_line_from_l2_or_l3'] = crossed_line and start_level in [2, 3]
    
    end_habitat = int(match.get('hab_end_robot', 0))
    match['endgame_ramp_l1'] = end_habitat == 1
    match['endgame_ramp_l2'] = end_habitat == 2
    match['endgame_ramp_l3'] = end_habitat == 3
    
    return match

def deepspace_process_scouting(scouting):
    """
    Process scouting for deepspace.
    
    Parameters:
        scouting: The scouting data to process.
    """
    processed = process_scouting_by_match(scouting, deepspace_process_match)
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
#                  'endgame_helped_l2',
#                  'endgame_helped_l3',
                  
                  'fouls',
                  'tech_fouls',
                  'source',
                  'comments']

deepspace_name_dict = {'auton_ci_ball_cargo':'sandstorm_balls_in_cargo_ship',
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
                       
                       'helping_robot_climb':'endgame_helped_climb'}

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
#                      'endgame_helped_l2':6,
#                      'endgame_helped_l3':12,
                      'endgame_helped_climb':0, #oh well
                      
                      'fouls':-3,
                      'tech_fouls':-10}

DEEP_SPACE = Game(deepspace_cats, deepspace_cats[:-2], None, deepspace_process_scouting, deepspace_rankings)

GAMES_FROM_YEARS = {'2017':STEAMWORKS,
                    '2018':POWER_UP,
                    '2019':DEEP_SPACE}
