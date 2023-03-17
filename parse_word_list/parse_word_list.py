import csv
import pickle


with open("word_set.pkl", "rb") as file:
    word_set = pickle.load(file)
print(list(word_set)[0:40])


# most_common_250 = set()
# with open('vocabulary.com-1000.csv', newline='') as csvfile:  # Ordered by usage frequency.
#     csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
#     word_num = 0
#     for row in csv_reader:
#         word = str(row[0])
#         most_common_250.add(word)
#         word_num += 1
#         if word_num >= 250:
#             break
#
#
# game_word_set = set()
# with open('ef.edu-3000.csv', newline='') as csvfile:  # Alphabetical
#     csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
#     for row in csv_reader:
#         word = str(row[0])
#         if word in most_common_250:
#             continue
#         game_word_set.add(word)
#
#
# with open("word_set.pkl", "wb") as file:
#     pickle.dump(game_word_set, file)
