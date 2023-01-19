import pickle
from wordplay.manage_database import POINTER_SYMBOL_KEY
from wordplay.game import POINTER_TYPES_TO_IGNORE
from game import game, get_game_graph, prune_and_reindex_game_data, get_depth, curate_game_data


with open('wordnet-data-0.pkl', 'rb') as file:
    wordnet_data = pickle.load(file)


# todo: Make synsets_by_depth a tuple.


start_depth = 3  # > 1 | DISTANCE BETWEEN start and target, or index of depth that is zero-indexed at target.
start_hp = 2  # > 0 | Gameplay continues until hp is 0.
curated_game_data = curate_game_data(wordnet_data, start_depth, start_hp)


game_tree = curated_game_data[0]
start_synset_num = curated_game_data[1]


print('')
print(f'game_tree = {game_tree}')
print(f'size of tree: {len(game_tree)}')
print(f'start_synset_num: {start_synset_num}')





wn_index_by_new_index = {}
for wn_index in new_index_by_wordnet_index:
    new_index = new_index_by_wordnet_index[wn_index]
    wn_index_by_new_index[new_index] = wn_index

target_synset_num = list(synsets_by_depth[0])[0]  # The only synset contained within the first set in synsets_by_depth.


def print_synset_info(synset_num, synsets_by_depth, deepest_depth, prefix=''):
    # i.e. 2 | throw, chuck | To toss

    # wn_synset_num = new_index_by_wordnet_index[synset_num]

    # print(wordnet_data[synset_num])

    # todo getting depth twice
    current_synset_depth = get_depth(synset_num, synsets_by_depth)
    # current_synset_depth = deepest_depth + 1
    # for depth in range(deepest_depth + 1):
    #     if synset_num in synsets_by_depth[depth]:
    #         # print('found depth!')
    #         current_synset_depth = depth
    #         break

    # Add depth.
    print_string = f'{prefix}{synset_num} | dist-{current_synset_depth} '

    # Add all words.
    # for word in wordnet_data[wn_synset_num][3]:
    #     print_string += f'{word}, '
    try:
        for word in game_tree[synset_num][2]:
            print_string += f'{word}, '
    except:
        print('!!!!!!!@@@@@@@')
        print(game_tree)
        print(synset_num)

    # Set words/gloss separator.
    print_string = print_string[:-2]  # Delete final ', '.
    # todo: Error if no words and length is 0???
    print_string += ' | '

    # Add gloss.
    print_string += game_tree[synset_num][4]

    print(print_string)


def print_synset_info_wn(synset_num, synsets_by_depth, deepest_depth, prefix=''):
    # i.e. 2 | throw, chuck | To toss

    # tree_synset_num = new_index_by_wordnet_index[synset_num]

    # current_synset_depth = get_depth(tree_synset_num)


    # Add depth.
    print_string = f'{prefix}{synset_num} '

    # Add all words.
    # for word in wordnet_data[wn_synset_num][3]:
    #     print_string += f'{word}, '
    try:
        for word in wordnet_data[synset_num][3]:
            print_string += f'{word}, '
    except:
        print('!!!!!!!@@@@@@@')
        print(game_tree)
        print(synset_num)

    # Set words/gloss separator.
    print_string = print_string[:-2]  # Delete final ', '.
    # todo: Error if no words and length is 0???
    print_string += ' | '

    # Add gloss.
    print_string += wordnet_data[synset_num][2]

    print(print_string)


print('')
print_synset_info(target_synset_num, synsets_by_depth, deepest_depth, 'TARGET: | ')
print('')

current_synset_num = start_synset_num
last_pointer_symbol = None

visit_order = {}
visit_number = 0

while True:

    visit_number += 1

    visit_order[current_synset_num] = visit_number

    # # First item is the pointer, and the second is the number of connections.
    # decoy_synsets = [[None, -1], [None, -1], [None, -1]]  # [lateral, ==1_away, >1_away]
    # toward_synset = [None, -1]

    # todo getting depth twice
    current_synset_depth = get_depth(current_synset_num, synsets_by_depth)
    # print(f'current depth: {current_synset_depth}')
    # current_synset_depth = deepest_depth + 1
    # for depth in range(deepest_depth + 1):
    #     if current_synset_num in synsets_by_depth[depth]:
    #         # print('found depth!')
    #         current_synset_depth = depth
    #         break

    print_synset_info(current_synset_num, synsets_by_depth, deepest_depth, 'CURRENT: | ')
    print('')

    wn_current_synset_num = wn_index_by_new_index[current_synset_num]

    pointer_num = 1
    for pointer in wordnet_data[wn_current_synset_num][4]:
        # todo: If not pointer ignore type/sequence:
        # todo: Check pointer types.

        pointer_prefix = '    '

        pointer_synset_id = pointer[1]

        # connections = len(wordnet_data[pointer_synset_id][4])  # Number of OUT-pointers.

        child_pointer_symbol = pointer[0]
        if child_pointer_symbol in POINTER_TYPES_TO_IGNORE:
            pointer_prefix += 'IGNORED '
        pointer_prefix += f'{pointer_num}) {POINTER_SYMBOL_KEY[child_pointer_symbol]["phrase"]} | '
        print_synset_info_wn(pointer_synset_id, synsets_by_depth, deepest_depth, pointer_prefix)
        pointer_num += 1

    print('')
    print_synset_info(target_synset_num, synsets_by_depth, deepest_depth, 'TARGET: | ')
    print_synset_info(current_synset_num, synsets_by_depth, deepest_depth, 'CURRENT: | ')
    print('')

    # correct_pointers = game_tree[current_synset_num]['correct']
    # decoy_pointers = game_tree[current_synset_num]['decoy']


    for pointers_group in [0, 1]:  # 0 is index for correct pointers, and 1 is index for decoy pointers.
        ptr_grp = game_tree[current_synset_num][pointers_group]

        oldest_order = 99999  # todo use infinity?
        chosen_pointer_id = None

        for pointer_id in ptr_grp:
            if pointer_id not in visit_order:
                this_order = -1
            else:
                this_order = visit_order[pointer_id]
            if this_order < oldest_order:
                oldest_order = this_order
                chosen_pointer_id = pointer_id

        if chosen_pointer_id is None:
            pointer_type = ['correct', 'decoy'][pointers_group]
            print(f'No {pointer_type} pointers!')
        else:
            print(f'Visit number: {visit_number} | Oldest order: {oldest_order} | Chosen id: {chosen_pointer_id}')
            pointer_symbol = ptr_grp[chosen_pointer_id]
            # pointer = ptr_grp[chosen_pointer_id]
            # pointer_symbol = pointer['symbol']
            prefix = f'    {pointers_group}: {POINTER_SYMBOL_KEY[pointer_symbol]["phrase"]} | '
            print_synset_info(chosen_pointer_id, synsets_by_depth, deepest_depth, prefix)

        for option_pointer_id in ptr_grp:
            pointer_symbol = ptr_grp[option_pointer_id]
            # pointer = ptr_grp[option_pointer_id]
            # pointer_symbol = pointer['symbol']
            prefix = f'    {pointers_group}opt: {POINTER_SYMBOL_KEY[pointer_symbol]["phrase"]} | '
            print_synset_info(option_pointer_id, synsets_by_depth, deepest_depth, prefix)

    print('')

    # print_synset_info(toward_synset[0][1], f'    CORRECT: {POINTER_SYMBOL_KEY[toward_synset[0][0]]["phrase"]} | ')
    # decoy_synset = None
    # for decoy_level in decoy_synsets:
    #     if decoy_level[0] is not None:
    #         decoy_synset = decoy_level[0][1]
    #         print_synset_info(decoy_synset, f'    DECOY: {POINTER_SYMBOL_KEY[decoy_level[0][0]]["phrase"]} | ')
    #         break

    user_response = input('    Which synset next? ')
    print('')

    current_synset_num = int(user_response)

    # if user_response == 'a':
    #     current_synset_num = toward_synset[0][1]
    # elif user_response == 'b':
    #     current_synset_num = decoy_synset[1]
    # else:
    #     next_pointer_index = int(user_response) - 1
    #     current_synset_num = wordnet_data[current_synset_num][4][next_pointer_index][1]














