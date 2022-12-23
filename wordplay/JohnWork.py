import pickle
import random
from wordplay.manage_database import POINTER_TYPES_TO_IGNORE, POINTER_SEQUENCES_TO_IGNORE, POINTER_SYMBOL_KEY
from game import game


with open('wordnet-data-0.pkl', 'rb') as file:
    wordnet_data = pickle.load(file)


# todo: Make analysis look at in-pointers, and execution look at out-pointers.

# todo: Make synsets_by_depth a tuple.


# synsets_by_depth = [{41257}, {41280, 35620, 935}, {43776, 43777, 43778, 43779, 43780, 115338, 37776, 927, 35619, 41256, 936, 41258, 41259, 41260, 41261, 41262, 41263, 35632, 41264, 41265, 41266, 40884, 41267, 41268, 43830, 40886, 41282, 40905, 973, 35951, 105841, 43768, 43769, 43770, 43771, 43772, 43773, 43774, 43775}, {36352, 36353, 36354, 36355, 36356, 36357, 36358, 36359, 36360, 36361, 36362, 36363, 12, 36364, 36365, 36366, 36367, 36368, 36369, 36370, 36371, 36372, 36373, 36374, 36375, 36376, 36377, 36378, 36379, 36380, 36381, 36382, 36384, 36385, 36386, 36387, 36388, 36383, 36389, 36390, 36391, 36392, 36393, 36394, 36395, 36396, 36397, 36398, 36399, 36400, 36401, 36402, 36403, 36404, 36405, 36406, 36407, 36408, 36409, 36410, 36411, 36412, 36413, 36414, 36415, 36416, 36417, 36418, 36419, 36420, 36421, 36422, 36423, 36424, 36425, 36426, 36427, 36428, 36429, 36430, 36431, 36432, 36433, 36434, 36435, 36436, 36437, 36438, 36439, 36440, 36441, 36442, 36443, 36444, 36445, 36446, 36447, 36448, 36449, 36450, 36451, 36452, 36453, 36454, 36455, 36456, 36457, 36458, 36459, 36460, 36461, 36462, 36463, 35953, 36464, 36465, 35950, 92728, 12398, 44086, 44087, 92731, 44088, 106570, 44089, 106568, 44090, 115339, 151, 106569, 673, 40895, 43746, 43748, 36071, 234, 36079, 43781, 43782, 43783, 43784, 43785, 43786, 43787, 43788, 43789, 43790, 43791, 43792, 43793, 43794, 36115, 43795, 43796, 43797, 43798, 43799, 11, 41245, 35621, 35622, 35623, 35624, 2854, 43817, 43828, 41269, 41270, 43829, 41272, 41273, 41274, 41275, 43832, 43831, 43833, 41279, 36160, 41281, 43834, 41283, 41284, 36165, 41285, 41286, 41287, 43848, 43850, 43851, 43852, 43853, 43854, 43855, 43856, 43849, 44085, 117074, 113171, 39776, 41319, 41320, 36207, 44035, 105842, 43835, 44039, 43836, 44040, 43837, 36241, 37778, 36243, 37779, 37780, 37781, 36247, 37777, 43926, 43930, 43931, 43932, 43936, 930, 931, 932, 933, 934, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 40885, 949, 40887, 40888, 40889, 40890, 101305, 43846, 43956, 43847, 43961, 43962, 43963, 43964, 43965, 43966, 43967, 43968, 43969, 43970, 43971, 43972, 36299, 43973, 40902, 36302, 36304, 43985, 36306, 35798, 35799, 36312, 36313, 36315, 43999, 43960, 43957, 36334, 36337, 36338, 36339, 36340, 36341, 36342, 36343, 36344, 36345, 36346, 36347, 36348, 36349, 36350, 36351}]
# lateral_connections = {35620: {41257}, 935: {41257}, 41280: {41257}, 41257: {41280, 35620, 935}, 973: {35632}, 35632: {973}, 40886: {41256, 115338, 40884}, 40884: {40886}, 41282: {43830, 35951}, 41256: {43830, 115338, 40886, 35951}, 35951: {41256, 41282}, 41259: {41258}, 41258: {41259}, 43830: {41256, 41282, 43771}, 115338: {41256, 40886}, 927: {936}, 936: {927}, 43771: {43830}}
# # Example above shows target synset number 0 at depth/index 0.
# # The sets after that show synset numbers at the depth that corresponds to the set's index.


this_game_data = game(wordnet_data)
synsets_by_depth = this_game_data[0]
lateral_connections = this_game_data[1]



deepest_depth = len(synsets_by_depth) - 1
start_synset_num = random.choice(list(synsets_by_depth[deepest_depth]))

target_synset_num = list(synsets_by_depth[0])[0]  # The only synset contained within the first set in synsets_by_depth.






def print_synset_info(synset_num, prefix=''):
    # i.e. 2 | throw, chuck | To toss

    # print(wordnet_data[synset_num])
    
    synset_depth = deepest_depth + 1
    for depth in range(deepest_depth + 1):
        if synset_num in synsets_by_depth[depth]:
            # print('found depth!')
            synset_depth = depth
            break

    # Add depth.
    print_string = f'{prefix}| dist-{synset_depth} '

    # Add lateral connections.
    if synset_num in lateral_connections:
        print_string += f'| lat-{len(lateral_connections[synset_num])} '
    else:
        print_string += f'| lat-XXX '

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
print_synset_info(target_synset_num, 'TARGET: ')
print('')

current_synset_num = start_synset_num
last_pointer_symbol = None

while True:

    print_synset_info(current_synset_num)
    print('')

    pointer_num = 1
    for pointer in wordnet_data[current_synset_num][4]:
        # todo: If not pointer ignore type/sequence:
        # todo: Check pointer types.

        pointer_prefix = '    '

        child_pointer_symbol = pointer[0]
        if child_pointer_symbol in POINTER_TYPES_TO_IGNORE or child_pointer_symbol == '?p':
            pointer_prefix += 'IGNORED '
            # continue  # Ignore specified pointers and word pivots.

        if pointer[0] in POINTER_SEQUENCES_TO_IGNORE:
            if POINTER_SEQUENCES_TO_IGNORE[child_pointer_symbol] == pointer[0]:
                pointer_prefix += 'IGNORED '
                # continue  # Ignore specified pointer type sequences.

        pointer_prefix += f'{pointer_num}) {POINTER_SYMBOL_KEY[child_pointer_symbol]["phrase"]} '
        print_synset_info(pointer[1], pointer_prefix)
        pointer_num += 1

    next_pointer_index = int(input('    Which synset next? ')) - 1
    print('')
    
    current_synset_num = wordnet_data[current_synset_num][4][next_pointer_index][1]














