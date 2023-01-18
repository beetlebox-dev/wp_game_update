import pickle
import random
import statistics

from wordplay.manage_database import POINTER_SYMBOL_KEY
from wordplay.game import POINTER_TYPES_TO_IGNORE
from game import game, get_game_tree


with open('wordnet-data-0.pkl', 'rb') as file:
    wordnet_data = pickle.load(file)



# todo: don't need pointers away from target. Don't need pointers after last breadth, or beyond certain depth.

# todo: Make analysis look at in-pointers, and execution look at out-pointers.

# todo: Make synsets_by_depth a tuple.



start_depth = 3  # > 1 | DISTANCE BETWEEN start and target, or index of depth that is zero-indexed at target.
hp = 2  # > 0 | Gameplay continues until hp is 0.
analysis_depth = 4  # start_depth + hp - 1





game_tree = None
synsets_by_depth = None
start_synset_num = None
new_index_by_wordnet_index = None
dead_ends = None
deepest_depth = None


def get_depth(current_synset_num, synsets_by_depth, deepest_depth):
    # todo getting depth twice
    # current_synset_depth = deepest_depth + 1
    current_synset_depth = 9999
    for depth in range(deepest_depth + 1):
        if current_synset_num in synsets_by_depth[depth]:
            # print('found depth!')
            current_synset_depth = depth
            break
    return current_synset_depth




lowest_index = 9999
best_sdev_mu = 9999
for _ in range(10):

    this_game_data = game(wordnet_data, analysis_depth, start_depth)
    i_synsets_by_depth = this_game_data[0]
    i_start_synset_num = this_game_data[1]

    # print(f'start_synset_num = {start_synset_num}')
    # synsets_by_depth = [{7001}, {1882, 106826}, {6661, 35349, 6181, 7029, 7030, 6190, 92721, 6194, 6196, 4680, 6226, 6227, 6230, 6231, 6232, 6236, 91505, 6253, 6254, 6255, 6256, 6259, 6268, 6269, 5247, 6274, 4740, 6277, 6278, 73350, 4747, 2188, 104845, 4753, 117395, 6292, 6296, 5789, 6302, 6306, 103607, 6340, 6345, 4301, 4302, 6388, 4343, 3321, 3322, 6405, 2830, 6419, 113428, 113429, 2857, 4395, 2357, 1854, 106824, 106834, 106835, 106836, 106837, 6998, 6999, 7000, 106838, 7002, 7003, 7004, 7005, 7006, 7007, 7008, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017, 7018, 4971, 7019, 7020, 7021, 7022, 7023, 7024, 7025, 7026, 7027, 7028, 4982, 7031, 7032, 7033, 7034, 7035, 7036, 7037, 7038, 7039, 7040, 7041, 7042, 7043, 7044, 7045, 2435, 7046, 7047, 7048, 7049, 7050, 2444, 7051, 7054, 7052, 7053, 7055, 7056, 7057, 7058, 7059, 7060, 7061, 7062, 7063, 7064, 7065, 7066, 7067, 7068, 7069, 7070, 7071, 7072, 7073, 7074, 2473, 1917, 6082, 2523, 2531, 2540, 3055, 6132, 6134, 6137, 6138, 3582}, {6159, 36882, 6182, 6183, 6184, 24615, 6186, 41003, 108582, 108588, 6191, 6192, 6193, 34864, 77876, 6197, 6198, 6199, 6200, 6201, 6202, 6203, 6204, 6205, 6206, 4150, 6214, 4169, 6223, 57424, 6229, 6233, 6234, 6235, 6238, 10337, 6243, 10340, 4202, 6252, 4208, 6257, 6258, 6260, 6270, 6271, 6272, 6273, 24705, 6279, 6280, 6281, 6282, 6283, 4237, 6293, 6297, 6298, 6299, 6300, 6301, 32923, 2207, 2208, 2209, 2210, 2211, 6303, 6304, 4263, 73895, 28845, 4285, 4289, 57538, 6342, 4295, 4298, 90315, 4300, 6358, 6367, 4337, 24829, 6398, 24832, 6402, 4355, 6403, 6404, 6406, 6407, 6418, 2341, 4389, 4391, 2345, 24885, 2358, 2373, 4423, 6473, 51530, 106827, 106828, 106829, 106830, 24911, 4432, 4433, 4434, 24912, 24913, 106831, 106832, 106833, 108884, 12649, 2417, 6516, 110965, 110966, 110967, 110968, 110969, 2433, 6532, 6537, 2443, 4149, 6549, 6550, 12706, 2474, 4529, 6590, 6599, 41419, 6618, 2522, 6620, 23008, 2530, 6630, 27112, 2536, 23018, 2539, 2541, 2546, 6648, 513, 88581, 35338, 104972, 6676, 6677, 4629, 37406, 6689, 35363, 4674, 8772, 8773, 8774, 8775, 8776, 8777, 8778, 8779, 8780, 8781, 8782, 8783, 8784, 8785, 8786, 78411, 39504, 4738, 4741, 4742, 4746, 8861, 92843, 4782, 6832, 6833, 6834, 6835, 25268, 117424, 107217, 31466, 31468, 2813, 4862, 74505, 74506, 74507, 74508, 58125, 74509, 76571, 2856, 25387, 56108, 2869, 64072, 13146, 4962, 4966, 4973, 106825, 45952, 72578, 58268, 58280, 58281, 23465, 23466, 58284, 58302, 23504, 3038, 3044, 70632, 76784, 1009, 3061, 115725, 33846, 72768, 11335, 3166, 25695, 5228, 9345, 103555, 78984, 76966, 76970, 7342, 1216, 103620, 103621, 11473, 34009, 34011, 74979, 7398, 7399, 7400, 7401, 7402, 72941, 3318, 34076, 1348, 91504, 1393, 79224, 79235, 23950, 101797, 1457, 1458, 36275, 1460, 7605, 36274, 36280, 34235, 32209, 26084, 26086, 9722, 1532, 1533, 1552, 1556, 77332, 99866, 99867, 1565, 3648, 63043, 34381, 5717, 75359, 63081, 63082, 79468, 34416, 79473, 40582, 79495, 34441, 73356, 73365, 73366, 73367, 5801, 5803, 1741, 71389, 71396, 1794, 32922, 12049, 73495, 12069, 75565, 73544, 73552, 3948, 1908, 12152, 102265, 102269, 6015, 6016, 6017, 6018, 6019, 6020, 6021, 6022, 6023, 6024, 6025, 6026, 6027, 6028, 73617, 73618, 10140, 6047, 71617, 4050, 34781, 6133, 6135, 6136, 6139, 6140, 6141, 6142, 6143}]
    # start_synset_num = 4208

    game_tree_result = get_game_tree(wordnet_data, i_synsets_by_depth, i_start_synset_num, start_depth, hp)
    i_game_tree = game_tree_result[0]
    i_synsets_by_depth = game_tree_result[1]  # todo changing to new index
    i_start_synset_num = game_tree_result[2]  # todo changing to new index
    i_new_index_by_wordnet_index = game_tree_result[3]
    i_dead_ends = game_tree_result[4]
    # print(f'game_tree = {i_game_tree}')
    # print(f'size of tree: {len(i_game_tree)}')

    i_deepest_depth = len(i_synsets_by_depth) - 1
    # print(f'deepest_depth: {i_deepest_depth}')
    # start_synset_num = random.choice(list(synsets_by_depth[deepest_depth]))

    # Analyze
    one_decoys = 0
    decoy_index = 0  # todo smaller desired.
    one_decoy_depths = []
    zero_decoy_depths = []
    syn_num = -1
    for synset_data in i_game_tree:
        syn_num += 1

        if syn_num in i_dead_ends:
            continue

        depth = get_depth(syn_num, i_synsets_by_depth, i_deepest_depth)
        if depth < 2:
            continue

        decoys = synset_data[1]
        if len(decoys) > 1:
            continue  # Index_contribution is 0.
        elif len(decoys) < 1:
            # No decoys!
            index_contribution = 3
            # 1 synset with no decoys is equivalent to having 3 synsets at depth 1 with only one decoy.
            zero_decoy_depths.append(depth)
        else:
            # len(decoys) == 1:
            index_contribution = 1 / max(depth, 1)
            one_decoys += 1
            one_decoy_depths.append(depth)

        decoy_index += index_contribution

    decoy_index /= len(i_game_tree)  # todo divide index by number of synsets in tree.

    # ratio = round(one_decoys / len(i_game_tree), 2)

    # print(f'\none_decoys: {one_decoys}')
    # print(f'one_decoys ratio: {ratio}')
    # print(f'one_decoy_depths: {one_decoy_depths}')
    # print(f'zero_decoy_depths: {zero_decoy_depths}')
    print(f'decoy_index: {decoy_index}')

    if decoy_index > lowest_index:
        continue

    # Break ties of equal decoy index.
    # todo don't need this if decoy_index > lowest_index.
    num_synsets_all_depths = 0
    num_nodes_each_depth = []
    for synsets_at_depth in i_synsets_by_depth[1:]:  # Ignore target depth with always one synset.
        num_synsets_this_depth = len(synsets_at_depth)
        num_synsets_all_depths += num_synsets_this_depth
        num_nodes_each_depth.append(num_synsets_this_depth)
    mean_synsets_per_depth = num_synsets_all_depths / len(i_synsets_by_depth[1:])
    sdev_depth = statistics.pstdev(num_nodes_each_depth, mean_synsets_per_depth)
    sdev_depth_in_mean_units = sdev_depth / mean_synsets_per_depth
    print(f'    {sdev_depth_in_mean_units}')

    # decoy_index <= lowest_index
    if decoy_index < lowest_index or sdev_depth_in_mean_units < best_sdev_mu:
        game_tree = i_game_tree
        synsets_by_depth = i_synsets_by_depth
        start_synset_num = i_start_synset_num
        new_index_by_wordnet_index = i_new_index_by_wordnet_index
        dead_ends = i_dead_ends
        deepest_depth = i_deepest_depth
        lowest_index = decoy_index
        best_sdev_mu = sdev_depth_in_mean_units



print('')
print(f'game_tree = {game_tree}')
print(f'size of tree: {len(game_tree)}')
print(f'deepest_depth: {deepest_depth}')
print(f'lowest_index: {lowest_index}')
print(f'best_sdev_mu: {best_sdev_mu}')
print(f'synsets_by_depth: {synsets_by_depth}')
print(f'start_synset_num: {start_synset_num}')
print(f'new_index_by_wordnet_index: {new_index_by_wordnet_index}')
print(f'dead_ends: {dead_ends}')




wn_index_by_new_index = {}
for wn_index in new_index_by_wordnet_index:
    new_index = new_index_by_wordnet_index[wn_index]
    wn_index_by_new_index[new_index] = wn_index

target_synset_num = list(synsets_by_depth[0])[0]  # The only synset contained within the first set in synsets_by_depth.
# print(f'target_synset_num: {target_synset_num}')



# print(wordnet_data[12031])






def print_synset_info(synset_num, synsets_by_depth, deepest_depth, prefix=''):
    # i.e. 2 | throw, chuck | To toss

    # wn_synset_num = new_index_by_wordnet_index[synset_num]

    # print(wordnet_data[synset_num])

    # todo getting depth twice
    current_synset_depth = get_depth(synset_num, synsets_by_depth, deepest_depth)
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
    current_synset_depth = get_depth(current_synset_num, synsets_by_depth, deepest_depth)
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














