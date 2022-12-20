import random
from wordplay.manage_database import POINTER_TYPES_TO_IGNORE, POINTER_SEQUENCES_TO_IGNORE, POINTER_SYMBOL_KEY



# todo: Make analysis look at in-pointers, and execution look at out-pointers.

# todo: Make synsets_by_depth a tuple.

synsets_by_depth = [{95605}, {108288, 108289, 92330, 92331, 36044, 95629, 70475, 95604, 92247, 92248, 92922, 108285, 108286, 108287}, {95608, 39687, 95624, 95625, 95609, 95626, 95627, 43541, 55447, 38777, 70298, 56815, 70076, 103745, 117444, 36037, 111957, 92246, 983, 94042, 92252, 26083, 1012, 50024, 70121, 108268, 108269, 108270, 108271, 108272, 108273, 108274, 108275, 108276, 108277, 108278, 108279, 108280, 108281, 108282, 108283, 108284, 95606, 95607}, {48152, 48153, 9876, 9877, 39496, 36040, 23931, 47193, 47194, 36042, 92249, 92251, 36043, 1119, 36045, 58048, 36046, 48241, 34935, 1667, 92294, 92295, 92296, 92297, 92298, 92299, 92300, 92301, 92302, 92303, 92304, 92305, 92306, 92307, 92308, 92309, 92310, 92311, 92312, 92313, 92314, 92315, 92316, 92317, 92318, 92319, 92320, 92321, 92322, 92323, 92324, 92325, 92326, 92327, 92328, 92329, 3242, 92332, 92333, 92334, 92335, 92336, 92337, 92338, 92339, 92340, 92341, 92342, 92343, 92344, 92345, 92346, 92347, 92348, 92349, 92350, 92351, 92352, 92353, 92354, 92355, 92356, 92357, 92358, 92359, 92360, 92361, 92362, 92363, 92364, 92365, 92366, 92367, 92368, 92369, 92370, 92371, 92372, 92373, 44246, 92374, 92375, 92376, 92377, 92378, 36572, 92379, 92380, 92381, 92382, 92383, 92384, 92385, 92386, 92387, 92388, 92389, 92390, 92391, 92392, 92393, 92394, 92395, 92923, 92924, 92925, 92926, 39681, 108290, 41743, 47390, 70430, 44324, 68389, 38708, 94021, 69958, 70476, 94029, 70477, 70478, 70479, 111956, 94041, 94043, 94044, 51554, 62658, 95610, 95611, 95612, 95613, 95614, 95615, 95616, 95617, 8066, 95618, 95619, 10627, 95116, 95628, 70297, 56217, 3489, 70075, 959, 47559, 70099, 26082, 88552, 35824, 1011}]
# synsets_by_depth = ({0,}, {1, 2}, {3, 4, 5})
# Example above shows target synset number 0 at depth/index 0.
# The sets after that show synset numbers at the depth that corresponds to the set's index.




deepest_depth = len(synsets_by_depth) - 1
start_synset_num = random.choice(list(synsets_by_depth[deepest_depth]))

target_synset_num = list(synsets_by_depth[0])[0]  # The only synset contained within the first set in synsets_by_depth.




import pickle
with open('wordnet-data-0.pkl', 'rb') as file:
    wordnet_data = pickle.load(file)



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
    print_string = f'{prefix}| dist-{synset_depth} | '

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














