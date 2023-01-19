import random


POINTER_TYPES_TO_IGNORE = {';u', '-u', '<', '<x', '!', '?p'}
# usage domains/members, adjective/verb derivations, antonyms, word pivots


# todo: Use get_depth_by_synset() ?
# todo: Can add words/pos/gloss at prune phase and discard all previous instances in game_graph.


def get_synsets_by_depth(wordnet_data, target_synset_id, analysis_depth):

    visited_synsets = {target_synset_id}
    synsets_by_depth = [{target_synset_id}]
    current_generation = [('__start', target_synset_id, 0, 0)]

    for _ in range(analysis_depth):  # Each loop is one layer in a breadth-first search.

        synsets_this_depth = set()
        next_generation = []

        for parent_pointer in current_generation:

            parent_synset_id = parent_pointer[1]

            for child_pointer in wordnet_data[parent_synset_id][5]:  # "In" pointers TO parent_synset_id.

                child_pointer_symbol = child_pointer[0]

                if child_pointer_symbol in POINTER_TYPES_TO_IGNORE:
                    continue  # Ignore specified pointer types.

                child_pointer_id = child_pointer[1]

                # Add pointer to tree if not yet visited.
                if child_pointer_id not in visited_synsets:
                    visited_synsets.add(child_pointer_id)
                    synsets_this_depth.add(child_pointer_id)
                    next_generation.append(child_pointer)

        if len(next_generation) < 1:
            break

        current_generation = next_generation
        synsets_by_depth.append(synsets_this_depth)

    return synsets_by_depth


# def get_depth_by_synset(synsets_by_depth):
#     depth_by_synset = {}
#     depth_layer_num = 0
#     for depth_layer in synsets_by_depth:
#         for synset_id in depth_layer:
#             depth_by_synset[synset_id] = depth_layer_num
#         depth_layer_num += 1
#     return depth_by_synset


def get_synset_with_most_pointers(wordnet_data, synset_set, samples=10):
    """Samples is the number of random synsets from synset_set to check before returning the best found."""
    best_synset_id = None
    highest_pointer_count = -1
    for _ in range(samples):
        try:
            rand_synset = random.choice(list(synset_set))
        except Exception as e:
            # todo: Debugging.
            exception_str = f'Error choosing random synset from synset_set in get_synset_with_most_pointers().\n' \
                            f'synset_set: {synset_set}\n{e}'
            raise Exception(exception_str)
        pointer_count = len(wordnet_data[rand_synset][4])
        if pointer_count > highest_pointer_count:
            best_synset_id = rand_synset
            highest_pointer_count = pointer_count
    return best_synset_id


def get_game_graph(wordnet_data, synsets_by_depth, start_synset_id, start_hp):

    def get_depth(synset_id):
        synset_depth = 9999  # If depth not found, return 9999, which indicates the depth is beyond synsets_by_depth.
        for search_depth in range(len(synsets_by_depth)):
            if synset_id in synsets_by_depth[search_depth]:
                synset_depth = search_depth
                break
        return synset_depth

    target_synset_id = list(synsets_by_depth[0])[0]
    # The only synset contained at depth 0 in synsets_by_depth.

    game_graph = {
        start_synset_id: {
            'pointers_gathered': False, 'correct': {}, 'decoy': {}, 'words': wordnet_data[start_synset_id][3],
            'pos': wordnet_data[start_synset_id][1], 'gloss': wordnet_data[start_synset_id][2],
        },
        target_synset_id: {
            'pointers_gathered': True, 'correct': {}, 'decoy': {}, 'words': wordnet_data[target_synset_id][3],
            'pos': wordnet_data[target_synset_id][1], 'gloss': wordnet_data[target_synset_id][2],
            # Correct and decoy pointers will not be used at target and will remain empty.
            # todo: Error thrown if correct/decoy keys aren't present???
        },
    }

    current_pointers_missing_in_graph = {start_synset_id}
    next_decoy_pointers_missing_in_graph = set()
    dead_ends = set()
    current_hp = start_hp

    while True:

        if current_hp < 1:
            raise Exception('No further decoy pointers should be added when current_hp drops below 1.')

        next_correct_pointers_missing_in_graph = set()

        for parent_synset_id in current_pointers_missing_in_graph:

            if game_graph[parent_synset_id]['pointers_gathered']:  # (Parent_synset_id is always in game_graph.)
                continue
            else:
                game_graph[parent_synset_id]['pointers_gathered'] = True

            # Gather pointers.

            # RANKING EQUATION: rank_value(0-11999) = one_way(0-1) * 6000 + in_tree(0-1) * 3000 +
            #                                         depth_change(0-2) * 1000 + pointer_count(0-999)
            # One_way and in_tree represent booleans where False is 0 and True is 1.
            # Depth_change is normalized to the range 0-2 (initially -1 to +1).
            # Pointer_count is the number of total WordNet pointers.
            # Parentheses contain possible variable ranges (inclusive).

            parent_depth = get_depth(parent_synset_id)
            best_pointers = {
                'correct': [{'rank_value': None}, {'rank_value': None}],
                'decoy': [{'rank_value': None}, {'rank_value': None}],
            }
            # best_correct_pointers = [{'rank_value': None}, {'rank_value': None}]
            # best_decoy_pointers = [{'rank_value': None}, {'rank_value': None}]
            # When actual pointers are added, other keys besides 'rank_value' are 'id' and 'symbol'.

            # Loop through all WordNet pointers, storing only the two with the highest rank_value.
            for child_pointer in wordnet_data[parent_synset_id][4]:  # "Out" pointers FROM parent_synset_id.

                child_pointer_symbol = child_pointer[0]

                if child_pointer_symbol in POINTER_TYPES_TO_IGNORE:
                    continue  # Ignore specified pointers and word pivots.

                child_pointer_id = child_pointer[1]
                child_depth = get_depth(child_pointer_id)
                depth_change = parent_depth - child_depth
                #    A depth change of +1 means getting 1-degree CLOSER to the target, or a distance DECREASE of 1.

                # Init rank_value with depth_change and pointer_count.
                pointer_count = len(wordnet_data[child_pointer_id][4])
                child_rank_value = (depth_change + 1) * 1000 + pointer_count
                # Depth_change is normalized to the range 0-2 (initially -1 to +1).

                # Update rank_value adding one_way and in_tree.
                if child_pointer_id in game_graph:
                    # In-tree.
                    child_rank_value += 3000
                    if parent_synset_id not in game_graph[child_pointer_id]['correct'] \
                            and parent_synset_id not in game_graph[child_pointer_id]['decoy']:
                        # One-way.
                        child_rank_value += 6000
                    # Else not one-way.
                else:
                    # Not in-tree, and therefore one-way.
                    child_rank_value += 6000

                # Replace an existing best pointer if child_rank_value is greater.
                if depth_change > 0:
                    pointer_group = best_pointers['correct']
                else:
                    pointer_group = best_pointers['decoy']
                for rank_index in range(2):
                    if pointer_group[rank_index]['rank_value'] is None \
                            or pointer_group[rank_index]['rank_value'] < child_rank_value:
                        child_pointer_data = \
                            {'id': child_pointer_id, 'rank_value': child_rank_value, 'symbol': child_pointer_symbol}
                        pointer_group.insert(rank_index, child_pointer_data)
                        del pointer_group[2]
                        break

            # Add final top-two pointers in each category to game_graph.
            for pointer_category in ['correct', 'decoy']:
                if parent_depth == 1 and pointer_category == 'decoy':
                    continue  # No need for decoy pointers at depth 1.
                for pointer in best_pointers[pointer_category]:
                    if pointer['rank_value'] is not None:
                        child_synset_id = pointer['id']
                        game_graph[parent_synset_id][pointer_category][child_synset_id] = pointer['symbol']
                        if child_synset_id not in game_graph:
                            game_graph[child_synset_id] = {
                                'pointers_gathered': False, 'correct': {}, 'decoy': {},
                                'words': wordnet_data[child_synset_id][3], 'pos': wordnet_data[child_synset_id][1],
                                'gloss': wordnet_data[child_synset_id][2],
                            }
                            if pointer_category == 'correct':
                                next_correct_pointers_missing_in_graph.add(child_synset_id)
                            else:
                                # pointer_category == 'decoy':
                                if current_hp > 1:
                                    next_decoy_pointers_missing_in_graph.add(child_synset_id)
                                else:
                                    # Hp after this set of decoys will be 0, and no more pointers are required.
                                    # Anotherwords, reaching this synset causes game-over.
                                    dead_ends.add(child_synset_id)

        if len(next_correct_pointers_missing_in_graph) > 0:
            current_pointers_missing_in_graph = next_correct_pointers_missing_in_graph
        elif len(next_decoy_pointers_missing_in_graph) > 0:
            current_hp -= 1
            current_pointers_missing_in_graph = next_decoy_pointers_missing_in_graph
            next_decoy_pointers_missing_in_graph = set()
        else:
            break  # No more synsets are added to next_decoy_pointers_missing_in_graph when current_hp <= 1.

    return game_graph, dead_ends


def prune_game_data(game_graph, synsets_by_depth, dead_ends, start_synset_id):

    # Assign new indices for game_graph synsets.
    new_index_by_wordnet_index = {}
    for wordnet_index in game_graph:
        new_index_by_wordnet_index[wordnet_index] = len(new_index_by_wordnet_index)

    game_graph_reindexed = [None for _ in range(len(game_graph))]
    for wordnet_index in new_index_by_wordnet_index:
        new_index = new_index_by_wordnet_index[wordnet_index]
        pointers_reindexed = {}
        for pointer_category in ['correct', 'decoy']:
            pointers_reindexed[pointer_category] = {}
            pointers = game_graph[wordnet_index][pointer_category]
            for pointer_wordnet_index in pointers:
                pointer_new_index = new_index_by_wordnet_index[pointer_wordnet_index]
                pointer_symbol = pointers[pointer_wordnet_index]
                pointers_reindexed[pointer_category][pointer_new_index] = pointer_symbol
        revised_node = [
            pointers_reindexed['correct'],
            pointers_reindexed['decoy'],
            list(game_graph[wordnet_index]['words']),
            game_graph[wordnet_index]['pos'],
            game_graph[wordnet_index]['gloss'],
        ]
        game_graph_reindexed[new_index] = revised_node

    synsets_by_depth_pruned_and_reindexed = []
    for synsets_this_depth in synsets_by_depth:
        synsets_this_depth_reindexed = set()
        for wordnet_index in synsets_this_depth:
            if wordnet_index in game_graph:
                new_index = new_index_by_wordnet_index[wordnet_index]
                synsets_this_depth_reindexed.add(new_index)
            # Else continue. Ok, because most synsets in original synsets_by_depth do not become part of game_graph.
        synsets_by_depth_pruned_and_reindexed.append(synsets_this_depth_reindexed)

    dead_ends_reindexed = set()
    for wn_syn_id in dead_ends:
        new_ndex = new_index_by_wordnet_index[wn_syn_id]
        dead_ends_reindexed.add(new_ndex)

    start_synset_id_reindexed = new_index_by_wordnet_index[start_synset_id]

    return game_graph_reindexed, synsets_by_depth_pruned_and_reindexed, start_synset_id_reindexed, \
           dead_ends_reindexed, new_index_by_wordnet_index






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
    synsets_by_depth = get_synsets_by_depth(wordnet_data, rand_synset_id, analysis_depth)
    start_synset_id = get_synset_with_most_pointers(wordnet_data, synsets_by_depth[start_depth])
    return synsets_by_depth, start_synset_id

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
