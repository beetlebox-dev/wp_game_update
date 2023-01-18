import colorsys
import random
import wordplay.find_connection as find_connection
import wordplay.manage_database as manage_database
from copy import deepcopy

POINTER_SYMBOL_KEY = manage_database.POINTER_SYMBOL_KEY
# POINTER_TYPES_TO_IGNORE = manage_database.POINTER_TYPES_TO_IGNORE

POINTER_TYPES_TO_IGNORE = {';u', '-u', '<', '<x', '!', '?p'}
# usage domains/members, adjective/verb derivations, antonyms, word pivots

# IGNORE_ANTONYMS = manage_database.IGNORE_ANTONYMS
# POINTER_SEQUENCES_TO_IGNORE = manage_database.POINTER_SEQUENCES_TO_IGNORE


def hsv_to_hsl(hsv):
    h, s, v = hsv
    rgb = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
    r, g, b = rgb
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100


def get_game_data(wordnet_data, target_synset_id, analysis_depth, start_depth):
    """Returns list: [synsets_by_depth, lateral_connections]

Returns a "tree", or a list of recursively nested lists encoding various paths from start to end synsets.

Start_word should be lower case, and spaces should be replaced with underscores.

Returns dictionary with keys "status" and "data". Status can be "ok" or "error".
If status is ok, data is path_memory tree. If status is error, data is a string describing the error.

TREE DATA STRUCTURE: tree[direction][generation][sibling_group_index][sibling_index]
    DIRECTION: Always 0. Vestigial from find_connection, and needed to be compatible with other functions.
    GENERATION: 0 is the first/oldest generation where branching begins at start and end synsets.
    -1 is last/newest generation where connecting synsets are found in common for both directions.
    SIBLING GROUP INDEX: Index of sibling group, containing pointers from the same parent synset in previous generation.
    SIBLING_INDEX: Index of pointer within sibling group."""

    path_memory = [[('__start', target_synset_id, 0, 0)]]  # todo only need last generation pointers from here.
    visited_synsets = {target_synset_id}

    synsets_by_depth = [{target_synset_id, }]
    # lateral_connections = {}

    # synsets_this_depth = set()
    # synsets_this_depth = visited_synsets

    # print(f'DEPTH: {depth}')

    for n in range(analysis_depth):  # Each loop is one layer in a breadth-first search.

        # print(f'current depth: {n}')
        # print(synsets_by_depth)

        # visited_synsets_this_depth = set()

        # synsets_prev_depth = synsets_this_depth
        synsets_this_depth = set()

        # print(path_memory[-1])
        # print(synsets_prev_depth)

        # next_generation = []
        sibling_group = []

        for parent_pointer in path_memory[-1]:
            # for parent_group in path_memory[0][-1]:  # Getting pointer groupings from previous generation.
            #     for parent_pointer in parent_group:  # Find neighbor_synsets of synsets_currently_visiting.

            # sibling_group = []

            parent_synset_id = parent_pointer[1]

            for child_pointer in wordnet_data[parent_synset_id][5]:  # "In" pointers TO parent_synset_id.

                child_pointer_symbol = child_pointer[0]
                if child_pointer_symbol in POINTER_TYPES_TO_IGNORE:
                    continue  # Ignore specified pointers and word pivots.

                # if child_pointer_symbol in POINTER_SEQUENCES_TO_IGNORE:
                #     if POINTER_SEQUENCES_TO_IGNORE[child_pointer_symbol] == parent_pointer[0]:
                #         continue  # Ignore specified pointer type sequences.

                child_pointer_id = child_pointer[1]

                # Add pointer to tree if not yet visited.
                if child_pointer_id not in visited_synsets:
                    synsets_this_depth.add(child_pointer_id)
                    sibling_group.append(child_pointer)
                    visited_synsets.add(child_pointer_id)

                # Add pointer to visited_synsets.
                # visited_synsets.add(child_pointer_id)
                # visited_synsets_this_depth.add(child_pointer_id)

                # # Tally lateral connections "IN".
                # if child_pointer_id in synsets_prev_depth:
                #     # Child_pointer_id points to parent_synset_id.
                #     if child_pointer_id in lateral_connections:
                #         lateral_connections[child_pointer_id].add(parent_synset_id)
                #         # lateral_connections[child_pointer_id] += 1
                #     else:
                #         lateral_connections[child_pointer_id] = {parent_synset_id, }

            # # Tally lateral connections "OUT".
            # for child_pointer in wordnet_data[parent_synset_id][4]:  # "Out" pointers FROM parent_synset_id.
            #
            #     child_pointer_symbol = child_pointer[0]
            #     if child_pointer_symbol in POINTER_TYPES_TO_IGNORE or child_pointer_symbol == '?p':
            #         continue  # Ignore specified pointers and word pivots.
            #
            #     if parent_pointer[0] in POINTER_SEQUENCES_TO_IGNORE:
            #         if POINTER_SEQUENCES_TO_IGNORE[parent_pointer[0]] == child_pointer_symbol:
            #             continue  # Ignore specified pointer type sequences.
            #
            #     child_pointer_id = child_pointer[1]
            #     if child_pointer_id in synsets_prev_depth:
            #         # Parent_synset_id points to child_pointer_id.
            #         if parent_synset_id in lateral_connections:
            #             lateral_connections[parent_synset_id].add(child_pointer_id)
            #             # lateral_connections[parent_synset_id] += 1
            #         else:
            #             lateral_connections[parent_synset_id] = {child_pointer_id, }
            #             # lateral_connections[parent_synset_id] = 1

            # next_generation.append(sibling_group)

        # empty_generation = True
        # for sibling_group in next_generation:
        #     if len(sibling_group) > 0:
        #         empty_generation = False
        #         break
        if len(sibling_group) == 0:
            # empty_generation = False
            break
        # if empty_generation:
        #     # Desired depth unreachable. Returning shorter tree.
        #     break

        # visited_synsets.update(visited_synsets_this_depth)  # Adds items this depth to visited_synsets.

        # path_memory[0].append(next_generation)
        path_memory.append(sibling_group)

        synsets_by_depth.append(synsets_this_depth)

    lateral_connections_new = {}
    non_lateral_connections = {}

    for depth_index in range(len(synsets_by_depth)):
        for synset_num in synsets_by_depth[depth_index]:
            for child_pointer in wordnet_data[synset_num][4]:  # "In" pointers TO parent_synset_id.

                child_pointer_symbol = child_pointer[0]
                if child_pointer_symbol in POINTER_TYPES_TO_IGNORE:
                    continue  # Ignore specified pointers and word pivots.

                child_pointer_id = child_pointer[1]
                if child_pointer_id in synsets_by_depth[depth_index]:
                    # This is a lateral connection.
                    if synset_num in lateral_connections_new:
                        lateral_connections_new[synset_num].add(child_pointer_id)
                    else:
                        lateral_connections_new[synset_num] = {child_pointer_id, }
                else:
                    if synset_num in non_lateral_connections:
                        non_lateral_connections[synset_num].add(child_pointer_id)
                    else:
                        non_lateral_connections[synset_num] = {child_pointer_id, }

    # Select start synset id
    # deepest_depth = len(synsets_by_depth) - 1
    best_start_synset_id = None
    best_start_synset_connection_count = -1
    for _ in range(10):  # Finds best lateral connections at greatest depth/distance from target out of 10 random ones.

        # print(synsets_by_depth)
        # print(start_depth)
        rand_start_synset = random.choice(list(synsets_by_depth[start_depth]))

        connection_count = len(wordnet_data[rand_start_synset][4])
        if connection_count > best_start_synset_connection_count:
            best_start_synset_id = rand_start_synset
            best_start_synset_connection_count = connection_count

        # if rand_start_synset not in lateral_connections_new:
        #     num_lat_connections = 0
        # else:
        #     num_lat_connections = len(lateral_connections_new[rand_start_synset])
        # # print(num_lat_connections)
        # if num_lat_connections > best_start_synset_connection_count:
        #     best_start_synset_id = rand_start_synset
        #     best_start_synset_connection_count = num_lat_connections

    # print(f'Start Connections: {best_start_synset_connection_count}')

    return synsets_by_depth, lateral_connections_new, non_lateral_connections, best_start_synset_id

    # return synsets_by_depth, lateral_connections


# todo on average 350 characters per tree item, or 280 bytes.
def get_game_tree(wordnet_data, synsets_by_depth, start_synset_id, dist_from_target, hp):
    """Returns list: [synsets_by_depth, lateral_connections]

Returns a "tree", or a list of recursively nested lists encoding various paths from start to end synsets.

Start_word should be lower case, and spaces should be replaced with underscores.

Returns dictionary with keys "status" and "data". Status can be "ok" or "error".
If status is ok, data is path_memory tree. If status is error, data is a string describing the error.

TREE DATA STRUCTURE: tree[direction][generation][sibling_group_index][sibling_index]
    DIRECTION: Always 0. Vestigial from find_connection, and needed to be compatible with other functions.
    GENERATION: 0 is the first/oldest generation where branching begins at start and end synsets.
    -1 is last/newest generation where connecting synsets are found in common for both directions.
    SIBLING GROUP INDEX: Index of sibling group, containing pointers from the same parent synset in previous generation.
    SIBLING_INDEX: Index of pointer within sibling group."""

    def get_depth(synset_num):
        deepest_depth = len(synsets_by_depth) - 1
        # print('TESTING!!!!!!!!')
        # print(f'synset num: {synset_num}')
        # print(f'deepest depth: {deepest_depth}')
        synset_depth = 9999  # If depth not found, return this which makes obvious that the depth is larger than the depth of the data.
        # synset_depth = deepest_depth + 1
        for search_depth in range(deepest_depth + 1):
            if synset_num in synsets_by_depth[search_depth]:
                synset_depth = search_depth
                break
        # print(f'synset depth: {synset_depth}')
        # print('endtest')
        # print(f'synset_num: {synset_num} | synset_depth: {synset_depth}')
        return synset_depth

    # todo no pointers for current_hp<1 or current_depth<2 or current_depth>=depth+hp

    target_synset_id = list(synsets_by_depth[0])[0]  # The only synset contained within the first set in synsets_by_depth.

    tree = {
        start_synset_id: {
            'depth': dist_from_target, 'in': set(), 'correct': {}, 'decoy': {},
            'words': wordnet_data[start_synset_id][3], 'pos': wordnet_data[start_synset_id][1],
            'gloss': wordnet_data[start_synset_id][2], 'pointers_gathered': False,
        },
        target_synset_id: {
            'depth': 0, 'in': set(), 'correct': {}, 'decoy': {},
            'words': wordnet_data[target_synset_id][3], 'pos': wordnet_data[target_synset_id][1],
            'gloss': wordnet_data[target_synset_id][2], 'pointers_gathered': True,
            # Correct and decoy will not be used at target, and pointers will not be gathered.
            # todo error thrown if keys arent in target key???
        },
    }

    current_out_pointers_missing_in_tree = {start_synset_id, }
    next_decoy_out_pointers_missing_in_tree = set()
    current_hp = hp
    dead_ends = set()

    new_index_by_wordnet_index = {start_synset_id: 0, target_synset_id: 1}

    # max_iters = hp * 2 + dist_from_target  # A maximum possible round length
    # # where each hp lost moves the player a distance of 1 further away from the target,
    # # and all but one hp is used 1 distance away from the target before the round is terminated.
    # print(f'max iters: {max_iters}')

    while True:

        if current_hp < 1:
            # Redundant. Should not be needed. No further decoy pointers are added when current_hp drops below 1.
            break
        # Loops through all correct pointers to find all synsets at current_hp.

        # for _ in range(max_iters):  # Each loop is one layer in a breadth-first search.

        # synsets_this_depth = set()
        # sibling_group = []

        next_correct_out_pointers_missing_in_tree = set()

        for parent_synset_id in current_out_pointers_missing_in_tree:

            if parent_synset_id in tree and tree[parent_synset_id]['pointers_gathered']:
                # TODO always in tree????
                continue

            tree[parent_synset_id]['pointers_gathered'] = True

            correct_pointers = [{'id': None, 'sort_value': None}, {'id': None, 'sort_value': None}]
            decoy_pointers = [{'id': None, 'sort_value': None}, {'id': None, 'sort_value': None}]

            # OLD
            # Sort by distance from target (prioritize closer), then by in_tree, then by connection_count.
            # sort_value = depth_change * 2000 + in_tree * 1000 + connections
            # Assumes: max number of connections possible < 1000. In_tree is either 1 (true) or 0 (false).

            # NEW
            # sort_value(0-11999) = one_way(0-1) * 6000 + in_tree(0-1) * 3000 + depth_change(0-2) * 1000 + connections(0-999)

            parent_depth = get_depth(parent_synset_id)

            for child_pointer in wordnet_data[parent_synset_id][4]:  # "Out" pointers FROM parent_synset_id.

                child_pointer_symbol = child_pointer[0]
                if child_pointer_symbol in POINTER_TYPES_TO_IGNORE:
                    continue  # Ignore specified pointers and word pivots.

                child_pointer_id = child_pointer[1]

                child_depth = get_depth(child_pointer_id)  # todo no need to continue beyond depth 1.

                # print(f'child_pointer_id: {child_pointer_id} | child_depth: {child_depth}')
                depth_change = parent_depth - child_depth  # depth_change=1 means getting 1 degree CLOSER to target.
                # Or a distance DECREASE of 1.

                sort_value = (depth_change + 1) * 1000

                if child_pointer_id in tree:
                    sort_value += 3000  # In-tree.
                    if parent_synset_id not in tree[child_pointer_id]['correct'] and parent_synset_id not in tree[child_pointer_id]['decoy']:
                        # One-way.
                        sort_value += 6000
                    # Else not one-way.
                else:
                    # Not in-tree, and also therefore one-way.
                    sort_value += 6000

                num_connections = len(wordnet_data[child_pointer_id][4])
                sort_value += num_connections

                if depth_change > 0:
                    pointer_group = correct_pointers
                else:
                    pointer_group = decoy_pointers

                for index in range(2):
                    if pointer_group[index]['sort_value'] is None or pointer_group[index]['sort_value'] < sort_value:
                        child_pointer_symbol = child_pointer[0]
                        trump_pointer = {'id': child_pointer_id, 'sort_value': sort_value, 'symbol': child_pointer_symbol}
                        pointer_group.insert(index, trump_pointer)
                        del pointer_group[2]
                        break

            if parent_depth == 1:
                # Only need 1 correct pointer to target. Don't need decoys.
                pointer = correct_pointers[0]
                child_synset_id = pointer['id']
                tree[parent_synset_id]['correct'][child_synset_id] = pointer['symbol']
                tree[child_synset_id]['in'].add(parent_synset_id)  # todo 'in' key used????
                continue  # Do not gather more pointers.

            for pointer in correct_pointers:
                if pointer['sort_value'] is not None:
                    child_synset_id = pointer['id']
                    tree[parent_synset_id]['correct'][child_synset_id] = pointer['symbol']

                    if child_synset_id in tree:
                        tree[child_synset_id]['in'].add(parent_synset_id)
                    else:
                        child_depth = get_depth(child_synset_id)
                        new_index_by_wordnet_index[child_synset_id] = len(new_index_by_wordnet_index)
                        tree[child_synset_id] = {
                            'depth': child_depth, 'in': {parent_synset_id, }, 'correct': {}, 'decoy': {},
                            'pos': wordnet_data[child_synset_id][1], 'gloss': wordnet_data[child_synset_id][2],
                            'words': wordnet_data[child_synset_id][3], 'pointers_gathered': False,
                        }
                        next_correct_out_pointers_missing_in_tree.add(child_synset_id)
            # todo can do above and below at once. combine both lists into dicts. iter through ['correct', 'decoy']
            for pointer in decoy_pointers:
                if pointer['sort_value'] is not None:
                    child_synset_id = pointer['id']
                    tree[parent_synset_id]['decoy'][child_synset_id] = pointer['symbol']

                    if child_synset_id in tree:
                        tree[child_synset_id]['in'].add(parent_synset_id)
                    else:
                        child_depth = get_depth(child_synset_id)
                        new_index_by_wordnet_index[child_synset_id] = len(new_index_by_wordnet_index)
                        tree[child_synset_id] = {
                            'depth': child_depth, 'in': {parent_synset_id, }, 'correct': {}, 'decoy': {},
                            'pos': wordnet_data[child_synset_id][1], 'gloss': wordnet_data[child_synset_id][2],
                            'words': wordnet_data[child_synset_id][3], 'pointers_gathered': False,
                        }
                        if current_hp > 1:
                            next_decoy_out_pointers_missing_in_tree.add(child_synset_id)
                        else:
                            # Else, hp after this set of decoys will be 0, and no more pointers are required.
                            # Reaching this synset means game over.
                            dead_ends.add(child_synset_id)

            # print(f'decoy pointers: {decoy_pointers}')

        if len(next_correct_out_pointers_missing_in_tree) > 0:
            current_out_pointers_missing_in_tree = next_correct_out_pointers_missing_in_tree
        elif len(next_decoy_out_pointers_missing_in_tree) > 0:
            current_out_pointers_missing_in_tree = next_decoy_out_pointers_missing_in_tree
            next_decoy_out_pointers_missing_in_tree = set()
            current_hp -= 1
        else:
            break  # No more synsets are added to next_decoy_out_pointers_missing_in_tree when current_hp <= 1.

    dead_ends_new_index = set()
    for wn_syn_id in dead_ends:
        new_ndex = new_index_by_wordnet_index[wn_syn_id]
        dead_ends_new_index.add(new_ndex)


    # condensed_tree = []
    condensed_tree = [None for _ in range(len(tree))]
    # todo working here!!!!!!!!!! new index from old
    for wordnet_synset_id in new_index_by_wordnet_index:

        new_index = new_index_by_wordnet_index[wordnet_synset_id]

        old_correct = tree[wordnet_synset_id]['correct']
        new_correct = {}
        for wn_synset_id in old_correct:
            new_id = new_index_by_wordnet_index[wn_synset_id]
            symbol = old_correct[wn_synset_id]
            new_correct[new_id] = symbol
        # todo combine above and below.
        old_decoy = tree[wordnet_synset_id]['decoy']
        new_decoy = {}
        for wn_synset_id in old_decoy:
            new_id = new_index_by_wordnet_index[wn_synset_id]
            symbol = old_decoy[wn_synset_id]
            new_decoy[new_id] = symbol

        new_branch = [
            new_correct,
            new_decoy,
            list(tree[wordnet_synset_id]['words']),
            tree[wordnet_synset_id]['pos'],
            tree[wordnet_synset_id]['gloss'],
        ]
        condensed_tree[new_index] = new_branch

    for item in condensed_tree:
        if item is None:
            'None in condensed tree'
            exit()
    # print(f'condensed tree length vs og tree length: {len(condensed_tree)} - {len(tree)}')
    synsets_by_depth_total_length = 0
    for depth in synsets_by_depth:
        # print(f'synsets at depth: {len(depth)}')
        synsets_by_depth_total_length += len(depth)
    # print(f'total synsets_by_depth items: {synsets_by_depth_total_length}\n')

    new_synsets_by_depth = []
    # print(f'new_index_by_wordnet_index: {new_index_by_wordnet_index}')
    depth = -1  # todo debug only
    for old_depth_layer in synsets_by_depth:
        depth += 1
        new_depth_layer = set()
        for wn_synset_id in old_depth_layer:
            # if wn_synset_id in new_index_by_wordnet_index:
            if wn_synset_id in tree:
                new_synset_index = new_index_by_wordnet_index[wn_synset_id]
                if new_synset_index > len(condensed_tree) - 1:
                    raise Exception('Condensed tree appears incomplete!')
                new_depth_layer.add(new_synset_index)
            # Else, ok because most synsets in full depth search are not in tree.
        new_synsets_by_depth.append(new_depth_layer)

    # print(f'synsets_by_depth: {synsets_by_depth}')
    # print(f'new_synsets_by_depth: {new_synsets_by_depth}')

    new_start_synset_id = new_index_by_wordnet_index[start_synset_id]

    return condensed_tree, new_synsets_by_depth, new_start_synset_id, new_index_by_wordnet_index, dead_ends_new_index


def random_main_group_synset(wordnet_data):
    while True:
        rand_synset_id = random.randint(0, len(wordnet_data))
        if wordnet_data[rand_synset_id][0] == -1:
            return rand_synset_id
            # word = random.choice(wordnet_data[rand_synset_id][3])
            # formatted_word = word.replace('_', ' ').split('(')[0]
            # return formatted_word, rand_synset_id


def rand_synset_max_connections(wordnet_data, samples=10):
    best_synset_id = None
    best_synset_connection_count = -1

    for _ in range(samples):
        rand_synset_id = random_main_group_synset(wordnet_data)
        connections = len(wordnet_data[rand_synset_id][5])  # Number of IN-pointers.
        if connections > best_synset_connection_count:
            best_synset_id = rand_synset_id
            best_synset_connection_count = connections

    # print(f'Target Connections: {best_synset_connection_count}\n')

    return best_synset_id


def game(wordnet_data, analysis_depth, start_depth, target=None):
    if target is None:
        rand_synset_id = rand_synset_max_connections(wordnet_data)
    else:
        rand_synset_id = target
    # rand_synset_id = random_main_group_synset(wordnet_data)
    game_data = get_game_data(wordnet_data, rand_synset_id, analysis_depth, start_depth)
    # print(f'\nsynsets_by_depth = {game_data[0]}')
    # print(f'lateral_connections = {game_data[1]}')
    # print(f'non_lateral_connections = {game_data[2]}')
    return game_data

# # todo delete when incorporating into app.
# import pickle
#
# with open('wordnet-data-0.pkl', 'rb') as file:
#     loaded_wordnet_data = pickle.load(file)
#
# this_game_data = game(loaded_wordnet_data)

# current_synset = None
# for synset in treegame[0]:
#     current_synset = synset
#     break
#
# for child_pointer in wordnet_data[current_synset][4]:
#     pointer_synset = child_pointer[1]
#     target_word_index = child_pointer[3]
#     if target_word_index != -1:
#         key_words.append(target_word)


# todo don't use word-dependent pointers??????
