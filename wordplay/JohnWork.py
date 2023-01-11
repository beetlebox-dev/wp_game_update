import pickle
import random
from wordplay.manage_database import POINTER_TYPES_TO_IGNORE, POINTER_SEQUENCES_TO_IGNORE, POINTER_SYMBOL_KEY
from game import game, get_game_tree


with open('wordnet-data-0.pkl', 'rb') as file:
    wordnet_data = pickle.load(file)



# todo: don't need pointers away from target. Don't need pointers after last breadth, or beyond certain depth.

# todo: Make analysis look at in-pointers, and execution look at out-pointers.

# todo: Make synsets_by_depth a tuple.


# start_synset_num = 12941
# synsets_by_depth = [{63805}, {55217, 7235, 63804, 63815}, {5792, 74371, 63813, 114982, 55017, 62666, 7275, 22988, 55821, 62745, 57596, 7230}, {78861, 72720, 72725, 72730, 61980, 53788, 7198, 7199, 7200, 7201, 7202, 7203, 7204, 7205, 7206, 7207, 7208, 7209, 7210, 7211, 7212, 72749, 7213, 7214, 7215, 7216, 7217, 72755, 7218, 7219, 7220, 7221, 7222, 7223, 7224, 7225, 7226, 7227, 7228, 7229, 7231, 7232, 7233, 7234, 7236, 7237, 7238, 7239, 7240, 7241, 7242, 7243, 74828, 7244, 7245, 7246, 7247, 7248, 7249, 7251, 7255, 7256, 42073, 2140, 2151, 77934, 64111, 64112, 64113, 7278, 2160, 2158, 7281, 78973, 56964, 53429, 33983, 74432, 1216, 72932, 76522, 22255, 55550, 102152, 63753, 102153, 13585, 62740, 55578, 13596, 13598, 103200, 103201, 42279, 1321, 64303, 64304, 64305, 64306, 64307, 64308, 64309, 63802, 74557, 41277, 63807, 63806, 55105, 6980, 63814, 76110, 55121, 79194, 79195, 79196, 79197, 79198, 79199, 79200, 79201, 79202, 79203, 79204, 79205, 79206, 79207, 79208, 79209, 79210, 79211, 79212, 79213, 79214, 79215, 79216, 79217, 57716, 73602, 74123, 73623, 50601, 74155, 55218, 55229, 72637, 74685, 39268, 77250, 22987, 76749, 74704, 72661, 74587, 55784}]
# lateral_connections = {35620: {41257}, 935: {41257}, 41280: {41257}, 41257: {41280, 35620, 935}, 973: {35632}, 35632: {973}, 40886: {41256, 115338, 40884}, 40884: {40886}, 41282: {43830, 35951}, 41256: {43830, 115338, 40886, 35951}, 35951: {41256, 41282}, 41259: {41258}, 41258: {41259}, 43830: {41256, 41282, 43771}, 115338: {41256, 40886}, 927: {936}, 936: {927}, 43771: {43830}}
# # Example above shows target synset number 0 at depth/index 0.
# # The sets after that show synset numbers at the depth that corresponds to the set's index.


analysis_depth = 5  # start_depth + hp
start_depth = 3  # DISTANCE BETWEEN start and target, or index of depth that is zero-indexed at target.
hp = 2  # Gameplay continues until hp is NEGATIVE.


this_game_data = game(wordnet_data, analysis_depth, start_depth)
lateral_connections = this_game_data[1]
non_lateral_connections = this_game_data[2]
start_synset_num = this_game_data[3]
synsets_by_depth = this_game_data[0]

print(f'synsets_by_depth = {synsets_by_depth}\nstart_synset_num = {start_synset_num}')
# synsets_by_depth = [{7001}, {1882, 106826}, {6661, 35349, 6181, 7029, 7030, 6190, 92721, 6194, 6196, 4680, 6226, 6227, 6230, 6231, 6232, 6236, 91505, 6253, 6254, 6255, 6256, 6259, 6268, 6269, 5247, 6274, 4740, 6277, 6278, 73350, 4747, 2188, 104845, 4753, 117395, 6292, 6296, 5789, 6302, 6306, 103607, 6340, 6345, 4301, 4302, 6388, 4343, 3321, 3322, 6405, 2830, 6419, 113428, 113429, 2857, 4395, 2357, 1854, 106824, 106834, 106835, 106836, 106837, 6998, 6999, 7000, 106838, 7002, 7003, 7004, 7005, 7006, 7007, 7008, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017, 7018, 4971, 7019, 7020, 7021, 7022, 7023, 7024, 7025, 7026, 7027, 7028, 4982, 7031, 7032, 7033, 7034, 7035, 7036, 7037, 7038, 7039, 7040, 7041, 7042, 7043, 7044, 7045, 2435, 7046, 7047, 7048, 7049, 7050, 2444, 7051, 7054, 7052, 7053, 7055, 7056, 7057, 7058, 7059, 7060, 7061, 7062, 7063, 7064, 7065, 7066, 7067, 7068, 7069, 7070, 7071, 7072, 7073, 7074, 2473, 1917, 6082, 2523, 2531, 2540, 3055, 6132, 6134, 6137, 6138, 3582}, {6159, 36882, 6182, 6183, 6184, 24615, 6186, 41003, 108582, 108588, 6191, 6192, 6193, 34864, 77876, 6197, 6198, 6199, 6200, 6201, 6202, 6203, 6204, 6205, 6206, 4150, 6214, 4169, 6223, 57424, 6229, 6233, 6234, 6235, 6238, 10337, 6243, 10340, 4202, 6252, 4208, 6257, 6258, 6260, 6270, 6271, 6272, 6273, 24705, 6279, 6280, 6281, 6282, 6283, 4237, 6293, 6297, 6298, 6299, 6300, 6301, 32923, 2207, 2208, 2209, 2210, 2211, 6303, 6304, 4263, 73895, 28845, 4285, 4289, 57538, 6342, 4295, 4298, 90315, 4300, 6358, 6367, 4337, 24829, 6398, 24832, 6402, 4355, 6403, 6404, 6406, 6407, 6418, 2341, 4389, 4391, 2345, 24885, 2358, 2373, 4423, 6473, 51530, 106827, 106828, 106829, 106830, 24911, 4432, 4433, 4434, 24912, 24913, 106831, 106832, 106833, 108884, 12649, 2417, 6516, 110965, 110966, 110967, 110968, 110969, 2433, 6532, 6537, 2443, 4149, 6549, 6550, 12706, 2474, 4529, 6590, 6599, 41419, 6618, 2522, 6620, 23008, 2530, 6630, 27112, 2536, 23018, 2539, 2541, 2546, 6648, 513, 88581, 35338, 104972, 6676, 6677, 4629, 37406, 6689, 35363, 4674, 8772, 8773, 8774, 8775, 8776, 8777, 8778, 8779, 8780, 8781, 8782, 8783, 8784, 8785, 8786, 78411, 39504, 4738, 4741, 4742, 4746, 8861, 92843, 4782, 6832, 6833, 6834, 6835, 25268, 117424, 107217, 31466, 31468, 2813, 4862, 74505, 74506, 74507, 74508, 58125, 74509, 76571, 2856, 25387, 56108, 2869, 64072, 13146, 4962, 4966, 4973, 106825, 45952, 72578, 58268, 58280, 58281, 23465, 23466, 58284, 58302, 23504, 3038, 3044, 70632, 76784, 1009, 3061, 115725, 33846, 72768, 11335, 3166, 25695, 5228, 9345, 103555, 78984, 76966, 76970, 7342, 1216, 103620, 103621, 11473, 34009, 34011, 74979, 7398, 7399, 7400, 7401, 7402, 72941, 3318, 34076, 1348, 91504, 1393, 79224, 79235, 23950, 101797, 1457, 1458, 36275, 1460, 7605, 36274, 36280, 34235, 32209, 26084, 26086, 9722, 1532, 1533, 1552, 1556, 77332, 99866, 99867, 1565, 3648, 63043, 34381, 5717, 75359, 63081, 63082, 79468, 34416, 79473, 40582, 79495, 34441, 73356, 73365, 73366, 73367, 5801, 5803, 1741, 71389, 71396, 1794, 32922, 12049, 73495, 12069, 75565, 73544, 73552, 3948, 1908, 12152, 102265, 102269, 6015, 6016, 6017, 6018, 6019, 6020, 6021, 6022, 6023, 6024, 6025, 6026, 6027, 6028, 73617, 73618, 10140, 6047, 71617, 4050, 34781, 6133, 6135, 6136, 6139, 6140, 6141, 6142, 6143}]
# start_synset_num = 4208

game_tree_result = get_game_tree(wordnet_data, synsets_by_depth, start_synset_num, start_depth, hp)
game_tree = game_tree_result[0]
synsets_by_depth = game_tree_result[1]  # todo changing to new index
start_synset_num = game_tree_result[2]  # todo changing to new index
print(f'reindexed synsets_by_depth = {synsets_by_depth}')
print(f'game_tree = {game_tree}')
print(f'size of tree: {len(game_tree)}')


deepest_depth = len(synsets_by_depth) - 1
print(deepest_depth)
# start_synset_num = random.choice(list(synsets_by_depth[deepest_depth]))

target_synset_num = list(synsets_by_depth[0])[0]  # The only synset contained within the first set in synsets_by_depth.
print(f'target_synset_num: {target_synset_num}')



# print(wordnet_data[12031])


def get_depth(current_synset_num):
    # todo getting depth twice
    # current_synset_depth = deepest_depth + 1
    current_synset_depth = 9999
    for depth in range(deepest_depth + 1):
        if current_synset_num in synsets_by_depth[depth]:
            # print('found depth!')
            current_synset_depth = depth
            break
    return current_synset_depth




def print_synset_info(synset_num, prefix=''):
    # i.e. 2 | throw, chuck | To toss

    # print(wordnet_data[synset_num])

    # todo getting depth twice
    current_synset_depth = get_depth(synset_num)
    # current_synset_depth = deepest_depth + 1
    # for depth in range(deepest_depth + 1):
    #     if synset_num in synsets_by_depth[depth]:
    #         # print('found depth!')
    #         current_synset_depth = depth
    #         break

    # Add depth.
    print_string = f'{prefix}{synset_num} | dist-{current_synset_depth} '

    # Add lateral connections.
    if synset_num in lateral_connections:
        print_string += f'| lat-{len(lateral_connections[synset_num])} | '
    else:
        print_string += f'| lat-XXX | '

    # Add all words.
    for word in wordnet_data[synset_num][3]:
        print_string += f'{word}, '

    # Set words/gloss separator.
    print_string = print_string[:-2]  # Delete final ', '.
    # todo: Error if no words and length is 0???
    print_string += ' | '

    # Add gloss.
    print_string += wordnet_data[synset_num][2]

    print(print_string)
    

print('')
print_synset_info(target_synset_num, 'TARGET: | ')
print('')

current_synset_num = start_synset_num
last_pointer_symbol = None

visit_order = {}
visit_number = 0

# todo if both synsets haven't been visited, go to the one that hasn't been shown as a pointer yet.

while True:

    visit_number += 1

    visit_order[current_synset_num] = visit_number

    # # First item is the pointer, and the second is the number of connections.
    # decoy_synsets = [[None, -1], [None, -1], [None, -1]]  # [lateral, ==1_away, >1_away]
    # toward_synset = [None, -1]

    # todo getting depth twice
    current_synset_depth = get_depth(current_synset_num)
    # print(f'current depth: {current_synset_depth}')
    # current_synset_depth = deepest_depth + 1
    # for depth in range(deepest_depth + 1):
    #     if current_synset_num in synsets_by_depth[depth]:
    #         # print('found depth!')
    #         current_synset_depth = depth
    #         break

    print_synset_info(current_synset_num, 'CURRENT: | ')
    print('')

    pointer_num = 1
    for pointer in wordnet_data[current_synset_num][4]:
        # todo: If not pointer ignore type/sequence:
        # todo: Check pointer types.

        pointer_prefix = '    '

        pointer_synset_id = pointer[1]

        # connections = len(wordnet_data[pointer_synset_id][4])  # Number of OUT-pointers.

        child_pointer_symbol = pointer[0]
        if child_pointer_symbol in POINTER_TYPES_TO_IGNORE or child_pointer_symbol == '?p':
            pointer_prefix += 'IGNORED '
        pointer_prefix += f'{pointer_num}) {POINTER_SYMBOL_KEY[child_pointer_symbol]["phrase"]} | '
        print_synset_info(pointer_synset_id, pointer_prefix)
        pointer_num += 1

    print('')
    print_synset_info(target_synset_num, 'TARGET: | ')
    print_synset_info(current_synset_num, 'CURRENT: | ')
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
            print(f'No {pointers_group} pointers!')
        else:
            print(f'Visit number: {visit_number} | Oldest order: {oldest_order} | Chosen id: {chosen_pointer_id}')
            pointer_symbol = ptr_grp[chosen_pointer_id]
            # pointer = ptr_grp[chosen_pointer_id]
            # pointer_symbol = pointer['symbol']
            prefix = f'    {pointers_group}: {POINTER_SYMBOL_KEY[pointer_symbol]["phrase"]} | '
            print_synset_info(chosen_pointer_id, prefix)

        for option_pointer_id in ptr_grp:
            pointer_symbol = ptr_grp[option_pointer_id]
            # pointer = ptr_grp[option_pointer_id]
            # pointer_symbol = pointer['symbol']
            prefix = f'    {pointers_group}opt: {POINTER_SYMBOL_KEY[pointer_symbol]["phrase"]} | '
            print_synset_info(option_pointer_id, prefix)

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














