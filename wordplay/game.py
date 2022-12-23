import colorsys
import random
import wordplay.find_connection as find_connection
import wordplay.manage_database as manage_database
from copy import deepcopy

POINTER_SYMBOL_KEY = manage_database.POINTER_SYMBOL_KEY
POINTER_TYPES_TO_IGNORE = manage_database.POINTER_TYPES_TO_IGNORE
IGNORE_ANTONYMS = manage_database.IGNORE_ANTONYMS
POINTER_SEQUENCES_TO_IGNORE = manage_database.POINTER_SEQUENCES_TO_IGNORE


def hsv_to_hsl(hsv):
    h, s, v = hsv
    rgb = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
    r, g, b = rgb
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100


def get_game_data(wordnet_data, start_synset_id, depth):
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

    path_memory = [[[[('__start', start_synset_id, 0, 0)]]]]  # todo only need last generation pointers from here.
    visited_synsets = {start_synset_id}

    synsets_by_depth = [{start_synset_id}]
    lateral_connections = {}

    # synsets_this_depth = set()
    synsets_this_depth = visited_synsets

    for _ in range(depth):  # Each loop is one layer in a breadth-first search.

        synsets_prev_depth = synsets_this_depth
        synsets_this_depth = set()

        print(path_memory[0][-1])
        print(synsets_prev_depth)

        next_generation = []

        for parent_group in path_memory[0][-1]:  # Getting pointer groupings from previous generation.
            for parent_pointer in parent_group:  # Find neighbor_synsets of synsets_currently_visiting.

                sibling_group = []

                parent_synset_id = parent_pointer[1]

                for child_pointer in wordnet_data[parent_synset_id][5]:  # "In" pointers TO parent_synset_id.

                    child_pointer_symbol = child_pointer[0]
                    if child_pointer_symbol in POINTER_TYPES_TO_IGNORE or child_pointer_symbol == '?p':
                        continue  # Ignore specified pointers and word pivots.

                    if child_pointer_symbol in POINTER_SEQUENCES_TO_IGNORE:
                        if POINTER_SEQUENCES_TO_IGNORE[child_pointer_symbol] == parent_pointer[0]:
                            continue  # Ignore specified pointer type sequences.

                    child_pointer_id = child_pointer[1]

                    # Add pointer to tree if not yet visited.
                    if child_pointer_id not in visited_synsets:
                        synsets_this_depth.add(child_pointer_id)
                        sibling_group.append(child_pointer)

                    # Add pointer to visited_synsets.
                    visited_synsets.add(child_pointer_id)

                    # Tally lateral connections "IN".
                    if child_pointer_id in synsets_prev_depth:
                        # Child_pointer_id points to parent_synset_id.
                        if child_pointer_id in lateral_connections:
                            lateral_connections[child_pointer_id].add(parent_synset_id)
                            # lateral_connections[child_pointer_id] += 1
                        else:
                            lateral_connections[child_pointer_id] = {parent_synset_id, }

                # Tally lateral connections "OUT".
                for child_pointer in wordnet_data[parent_synset_id][4]:  # "Out" pointers FROM parent_synset_id.

                    child_pointer_symbol = child_pointer[0]
                    if child_pointer_symbol in POINTER_TYPES_TO_IGNORE or child_pointer_symbol == '?p':
                        continue  # Ignore specified pointers and word pivots.

                    if parent_pointer[0] in POINTER_SEQUENCES_TO_IGNORE:
                        if POINTER_SEQUENCES_TO_IGNORE[parent_pointer[0]] == child_pointer_symbol:
                            continue  # Ignore specified pointer type sequences.

                    child_pointer_id = child_pointer[1]
                    if child_pointer_id in synsets_prev_depth:
                        # Parent_synset_id points to child_pointer_id.
                        if parent_synset_id in lateral_connections:
                            lateral_connections[parent_synset_id].add(child_pointer_id)
                            # lateral_connections[parent_synset_id] += 1
                        else:
                            lateral_connections[parent_synset_id] = {child_pointer_id, }
                            # lateral_connections[parent_synset_id] = 1

                next_generation.append(sibling_group)

        empty_generation = True
        for sibling_group in next_generation:
            if len(sibling_group) > 0:
                empty_generation = False
                break
        if empty_generation:
            # Desired depth unreachable. Returning shorter tree.
            return synsets_by_depth, lateral_connections

        path_memory[0].append(next_generation)

        synsets_by_depth.append(synsets_this_depth)

    return synsets_by_depth, lateral_connections


def random_main_group_synset(wordnet_data):
    while True:
        rand_synset_id = random.randint(0, len(wordnet_data))
        if wordnet_data[rand_synset_id][0] == -1:
            return rand_synset_id
            # word = random.choice(wordnet_data[rand_synset_id][3])
            # formatted_word = word.replace('_', ' ').split('(')[0]
            # return formatted_word, rand_synset_id


def game(wordnet_data):
    rand_synset_id = random_main_group_synset(wordnet_data)
    game_data = get_game_data(wordnet_data, rand_synset_id, 3)
    print(f'\nsynsets_by_depth = {game_data[0]}')
    print(f'lateral_connections = {game_data[1]}')
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
