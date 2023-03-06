import random
import pickle
import statistics
from admin import admin_alert_thread
from server_retrieval import Serve


# todo: rule out antonym connections, even if an antonym isn't the pointer used.
# todo: word list string?
# todo: Make synsets_by_depth a tuple.
# todo Wordnet data for synset 107948 has antonym listed at beginning and end!
# todo: Can add words/pos/gloss at prune phase and discard all previous instances in game_graph.

START_DEPTH = 5  # > 1 | DISTANCE BETWEEN start and target, or index of depth that is zero-indexed at target.
START_HP = 3  # > 0 | Gameplay continues until hp is 0.
GAME_NAME = 'current_game.json'
POINTER_TYPES_TO_IGNORE = {';u', '-u', '<', '<x', '!', '?p'}
#    usage domains/members, adjective/verb derivations, antonyms, word pivots

with open('wordnet-data-0.pkl', 'rb') as file:
    WORDNET_DATA = pickle.load(file)


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
        pointer_count = 0
        all_out_pointers = wordnet_data[rand_synset][4]
        for out_pointer in all_out_pointers:
            if out_pointer[0] not in POINTER_TYPES_TO_IGNORE:
                pointer_count += 1
        # pointer_count = len(wordnet_data[rand_synset][4])
        if pointer_count > highest_pointer_count:
            best_synset_id = rand_synset
            highest_pointer_count = pointer_count
    return best_synset_id


def get_depth(synset_id, synsets_by_depth):
    synset_depth = 9999  # If depth not found, return 9999, which indicates the depth is beyond synsets_by_depth.
    for search_depth in range(len(synsets_by_depth)):
        if synset_id in synsets_by_depth[search_depth]:
            synset_depth = search_depth
            break
    return synset_depth


def get_game_graph(wordnet_data, synsets_by_depth, start_synset_id, start_hp):

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

            parent_depth = get_depth(parent_synset_id, synsets_by_depth)
            best_pointers = {
                'correct': [{'rank_value': None}, {'rank_value': None}],
                'decoy': [{'rank_value': None}, {'rank_value': None}],
            }  # When actual pointers are added, other keys besides 'rank_value' are 'id' and 'symbol'.

            # Loop through all WordNet pointers, storing only the two with the highest rank_value.
            for child_pointer in wordnet_data[parent_synset_id][4]:  # "Out" pointers FROM parent_synset_id.

                child_pointer_symbol = child_pointer[0]

                if child_pointer_symbol in POINTER_TYPES_TO_IGNORE:
                    continue  # Ignore specified pointers and word pivots.

                child_pointer_id = child_pointer[1]
                child_depth = get_depth(child_pointer_id, synsets_by_depth)
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
                            {'id': child_pointer_id, 'rank_value': child_rank_value,
                             'data': (child_pointer_symbol, child_pointer[2], child_pointer[3])}
                            # {'id': child_pointer_id, 'rank_value': child_rank_value, 'symbol': child_pointer_symbol}  #todo !@#$!@#$!@#$
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
                        game_graph[parent_synset_id][pointer_category][child_synset_id] = pointer['data']  #todo !@#$!@#$!@#$
                        # game_graph[parent_synset_id][pointer_category][child_synset_id] = pointer['symbol']  #todo !@#$!@#$!@#$
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


def prune_and_reindex_game_data(game_graph, synsets_by_depth, dead_ends, start_synset_id):

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
                # pointer_symbol = pointers[pointer_wordnet_index]  #todo!@#$!@#$!@#$
                # pointers_reindexed[pointer_category][pointer_new_index] = pointer_symbol
                pointer_data = pointers[pointer_wordnet_index]
                pointers_reindexed[pointer_category][pointer_new_index] = pointer_data

        # cleaned_string = extra_spaces_removed_string.replace(' ', '_')
        word_list_underscores_to_spaces = [word.replace('_', ' ') for word in game_graph[wordnet_index]['words']]
        revised_node = [
            pointers_reindexed['correct'],
            pointers_reindexed['decoy'],
            # todo: Don't need to store words/pos/gloss in game_graph before now.
            word_list_underscores_to_spaces,
            # list(game_graph[wordnet_index]['words']),
            game_graph[wordnet_index]['pos'],
            game_graph[wordnet_index]['gloss'],
        ]
        game_graph_reindexed[new_index] = revised_node

    nodes_by_depth_pruned_and_reindexed = []
    for synsets_this_depth in synsets_by_depth:
        nodes_this_depth_reindexed = set()
        for wordnet_index in synsets_this_depth:
            if wordnet_index in game_graph:
                new_index = new_index_by_wordnet_index[wordnet_index]
                nodes_this_depth_reindexed.add(new_index)
            # Else continue. Ok, because most synsets in original synsets_by_depth do not become part of game_graph.
        nodes_by_depth_pruned_and_reindexed.append(nodes_this_depth_reindexed)

    dead_ends_reindexed = set()
    for wn_syn_id in dead_ends:
        new_dead_end_index = new_index_by_wordnet_index[wn_syn_id]
        dead_ends_reindexed.add(new_dead_end_index)

    start_node_reindexed = new_index_by_wordnet_index[start_synset_id]

    return game_graph_reindexed, nodes_by_depth_pruned_and_reindexed, start_node_reindexed, dead_ends_reindexed


def random_main_group_synset(wordnet_data):
    while True:
        rand_synset_id = random.randint(0, len(wordnet_data))
        if wordnet_data[rand_synset_id][0] == -1:
            return rand_synset_id


def rand_synset_max_in_pointers(wordnet_data, samples=10):
    best_synset_id = None
    best_pointer_count = -1
    for _ in range(samples):
        rand_synset_id = random_main_group_synset(wordnet_data)
        all_in_pointers = wordnet_data[rand_synset_id][5]
        in_pointer_count = 0
        for in_pointer in all_in_pointers:
            if in_pointer[0] not in POINTER_TYPES_TO_IGNORE:
                in_pointer_count += 1
        # pointer_count = len(wordnet_data[rand_synset_id][5])  # Number of IN-pointers.
        if in_pointer_count > best_pointer_count:
            best_synset_id = rand_synset_id
            best_pointer_count = in_pointer_count
    return best_synset_id


def curate_game_data(wordnet_data, start_depth, start_hp, samples=10):

    analysis_depth = start_depth + start_hp - 1
    curated_game_graph = None
    curated_start_node_index = None
    curated_target_node_index = None

    lowest_nodes_decoy_count_index = 9999  # Primary factor in choosing game_graph.
    lowest_depth_node_counts_sdev = 9999  # Breaks ties of lowest_non_double_decoy_nodes_index.

    for _ in range(samples):

        # Generate random game_graph.
        target_synset_id = rand_synset_max_in_pointers(wordnet_data)
        synsets_by_depth_wn_index = get_synsets_by_depth(wordnet_data, target_synset_id, analysis_depth)
        if len(synsets_by_depth_wn_index) != analysis_depth + 1:
            # The randomly selected target_synset_id could lead to a dead end, which is handled by this block.
            print('*****************************')
            print(wordnet_data[target_synset_id])
            print(target_synset_id)
            print(synsets_by_depth_wn_index)
            print(start_depth)
            print(analysis_depth)
            continue
        start_synset_id = get_synset_with_most_pointers(wordnet_data, synsets_by_depth_wn_index[start_depth])
        get_game_graph_result = get_game_graph(wordnet_data, synsets_by_depth_wn_index, start_synset_id, start_hp)
        game_graph = get_game_graph_result[0]
        dead_ends_wn_indices = get_game_graph_result[1]
        prune_and_reindex_game_data_result = \
            prune_and_reindex_game_data(game_graph, synsets_by_depth_wn_index, dead_ends_wn_indices, start_synset_id)
        this_game_graph = prune_and_reindex_game_data_result[0]
        nodes_by_depth = prune_and_reindex_game_data_result[1]
        this_start_node_index = prune_and_reindex_game_data_result[2]
        dead_ends = prune_and_reindex_game_data_result[3]

        # Analyze random game graph.

        nodes_decoy_count_index = 0
        #    A value representing how often there aren't two decoy pointers in this_game_graph.
        graph_node_index = -1
        for node_data in this_game_graph:
            graph_node_index += 1

            if graph_node_index in dead_ends:
                continue  # Dead end nodes intentionally have no pointers.
            depth = get_depth(graph_node_index, nodes_by_depth)
            if depth < 2:
                continue  # Nodes at depths 0 and 1 intentionally have no pointers.

            decoy_pointer_count = len(node_data[1])
            if decoy_pointer_count == 1:
                nodes_decoy_count_index += 1 / max(depth, 1)
            elif decoy_pointer_count < 1:
                nodes_decoy_count_index += 3
                # 1 node with no decoy pointers is equivalent to having 3 nodes at depth 1 with only one decoy pointer.
            # Else, decoy_pointer_count > 1. This is desirable, so nothing is added to non_double_pointers_index.

        # Dividing non_double_decoy_nodes_index by the number of nodes in this_game_graph
        # for apples-to-apples comparisons with other game_graphs.
        nodes_decoy_count_index /= len(this_game_graph)

        if nodes_decoy_count_index > lowest_nodes_decoy_count_index:
            continue

        # For breaking ties of equal lowest_non_double_decoy_nodes_index.
        node_count_all_depths = 0
        node_counts_each_depth = []
        for nodes_at_this_depth in nodes_by_depth[1:]:  # Ignoring target depth with always one node.
            num_nodes_this_depth = len(nodes_at_this_depth)
            node_count_all_depths += num_nodes_this_depth
            node_counts_each_depth.append(num_nodes_this_depth)
        mean_nodes_per_depth = node_count_all_depths / len(nodes_by_depth[1:])
        #    Ignoring target depth with always one node.
        depth_node_counts_sdev = statistics.pstdev(node_counts_each_depth, mean_nodes_per_depth)
        depth_node_counts_sdev_in_mean_units = depth_node_counts_sdev / mean_nodes_per_depth

        # True (after continue above): non_double_pointers_index <= lowest_non_double_decoy_nodes_index
        if nodes_decoy_count_index < lowest_nodes_decoy_count_index \
                or depth_node_counts_sdev_in_mean_units < lowest_depth_node_counts_sdev:
            curated_game_graph = this_game_graph
            curated_start_node_index = this_start_node_index
            curated_target_node_index = list(nodes_by_depth[0])[0]  # Only node at depth 0.
            lowest_nodes_decoy_count_index = nodes_decoy_count_index
            lowest_depth_node_counts_sdev = depth_node_counts_sdev_in_mean_units

    return curated_game_graph, curated_start_node_index, curated_target_node_index


if __name__ == "__main__":

    try:

        serve = Serve()
        curated_game_data = curate_game_data(WORDNET_DATA, START_DEPTH, START_HP)
        export_data = list(curated_game_data)
        export_data.append(START_HP)
        serve.upload(GAME_NAME, export_data)

        game_graph = export_data[0]
        start_node_index = export_data[1]
        target_node_index = export_data[2]
        alert_message = f'New wordplay game generated.\n' \
                        f'Start word: {game_graph[start_node_index][2][0]}\n' \
                        f'Target word: {game_graph[target_node_index][2][0]}\n' \
                        f'Synset count: {len(game_graph)}'
        print(alert_message)
        admin_alert_thread('Web App - Log', alert_message)

    except Exception as e:
        print(e)
        admin_alert_thread('Web App - ERROR', f'Error generating new wordplay game.\n{e}')
