from flask import render_template, request, url_for, redirect
from threading import Thread
import pickle
import wordplay.find_connection as find_connection
import wordplay.find_opposite as find_opposite
from admin import admin_alert_thread


# Copyright 2021 Johnathan Pennington | All rights reserved.


wordnet_index = None
wordnet_data = None
group_map = None
groups_without_opposites = None

wordnet_index_thread = None
wordnet_data_thread = None
group_map_thread = None
groups_without_opposites_thread = None


def tab_classes(active_tab=''):
    tab_class_dict = {'connect': '', 'opposite': '', 'about': ''}
    if active_tab in tab_class_dict:
        tab_class_dict[active_tab] = 'active-tab'
    else:
        'Passed invalid tab name to tab_classes()!'
    return tab_class_dict


def load_index():
    global wordnet_index
    with open('wordplay/wordnet-index.pkl', 'rb') as file:
        wordnet_index = pickle.load(file)


def load_data():
    global wordnet_data
    with open('wordplay/wordnet-data-0.pkl', 'rb') as file:
        wordnet_data = pickle.load(file)


def load_group_map():
    global group_map
    with open('wordplay/group-map.pkl', 'rb') as file:
        group_map = pickle.load(file)


def load_groups_without_opposites():
    global groups_without_opposites
    with open('wordplay/groups-without-opposites.pkl', 'rb') as file:
        groups_without_opposites = pickle.load(file)


def start_load_database_thread():
    global wordnet_data_thread
    global wordnet_index_thread
    global group_map_thread
    global groups_without_opposites_thread
    if wordnet_data_thread is None and wordnet_data is None:
        print('Start load_data thread.')
        wordnet_data_thread = Thread(target=load_data)
        wordnet_data_thread.start()
    if wordnet_index_thread is None and wordnet_index is None:
        print('Start load_index thread.')
        wordnet_index_thread = Thread(target=load_index)
        wordnet_index_thread.start()
    if group_map_thread is None and group_map is None:
        print('Start load_group_map thread.')
        group_map_thread = Thread(target=load_group_map)
        group_map_thread.start()
    if groups_without_opposites_thread is None and groups_without_opposites is None:
        print('Start load_groups_without_opposites thread.')
        groups_without_opposites_thread = Thread(target=load_groups_without_opposites)
        groups_without_opposites_thread.start()


def join_thread(thread):
    if thread is not None:
        if thread.is_alive():
            thread.join(timeout=10.0)


def about():
    start_load_database_thread()
    tab_class = tab_classes('about')
    return render_template('wordplay/about.html', tab_classes=tab_class)


def opposite(word, error=''):
    start_load_database_thread()
    tab_class = tab_classes('opposite')
    return render_template('wordplay/opposite.html', source=word, error=error, tab_classes=tab_class)


def opposite_random():
    global wordnet_data_thread
    global wordnet_data
    start_load_database_thread()
    join_thread(wordnet_data_thread)
    word = find_connection.random_main_group_word(wordnet_data)
    destination = url_for('opposite', word=word)
    admin_alert_thread('Web App - Log', f'WORDPLAY\nOpposite page random button click.\n'
                                        f'Request: {request.url}\nRedirect to: {request.url_root}{destination[1:]}\n'
                                        f'WORD: {word}')
    return redirect(destination)


def opposite_result(synset, word):

    global wordnet_index_thread
    global wordnet_index
    global wordnet_data_thread
    global wordnet_data
    global group_map_thread
    global group_map
    global groups_without_opposites_thread
    global groups_without_opposites

    start_load_database_thread()
    join_thread(groups_without_opposites_thread)
    join_thread(wordnet_index_thread)
    join_thread(wordnet_data_thread)
    data = find_opposite.web_app_inquiry(wordnet_data, wordnet_index, groups_without_opposites, word, synset)

    if data['status'] == 'error':
        tab_class = tab_classes('opposite')
        admin_alert_thread('Web App - ERROR',
                           f'WORDPLAY\n{request.url}\nWORD: {word}\nSYNSET: {synset}\n{data["message"]}')
        return render_template('wordplay/opposite.html', source=word, error=data['message'], tab_classes=tab_class)
    else:
        tab_class = tab_classes('opposite')
        cleaned_word = find_connection.remove_non_wordnet_chars(word)
        if data['status'] == 'choose_synset':
            admin_alert_thread('Web App - Log',
                               f'WORDPLAY\n{request.url}\nRendered opposite choose-synset page.\nWORD: {word}\nSYNSET: {synset}')
            return render_template('wordplay/choose_synset.html', source=cleaned_word, synsets=data['data'],
                                   message=data['message'], tab_classes=tab_class)
        else:
            admin_alert_thread('Web App - Log',
                               f'WORDPLAY\n{request.url}\nRendered opposite result page.\nWORD: {word}\nSYNSET: {synset}')
            return render_template('wordplay/opposite_result.html', source=cleaned_word, info=data['message'],
                                   paths=data['data'], tab_classes=tab_class)


def connect(source, target, error=''):
    start_load_database_thread()
    tab_class = tab_classes('connect')
    return render_template('wordplay/connect.html', source=source, target=target, error=error, tab_classes=tab_class)


def connect_random():
    global wordnet_data_thread
    global wordnet_data
    start_load_database_thread()
    join_thread(wordnet_data_thread)
    source = find_connection.random_main_group_word(wordnet_data)
    target = find_connection.random_main_group_word(wordnet_data)
    destination = url_for('connect', source=source, target=target)
    admin_alert_thread('Web App - Log', f'WORDPLAY\nConnect page random button click.\n'
                                        f'Request: {request.url}\nRedirect to: {request.url_root}{destination[1:]}\n'
                                        f'START: {source}\nTARGET: {target}')
    return redirect(destination)


def connect_result(source, target):

    global wordnet_index_thread
    global wordnet_index
    global wordnet_data_thread
    global wordnet_data
    global group_map_thread
    global group_map

    start_load_database_thread()
    join_thread(group_map_thread)
    join_thread(wordnet_index_thread)
    join_thread(wordnet_data_thread)
    data = find_connection.web_app_inquiry(wordnet_data, wordnet_index, group_map, source, target)

    if data['status'] == 'error':
        admin_alert_thread('Web App - ERROR',
                           f'WORDPLAY\n{request.url}\nSTART: {source}\nTARGET: {target}\n{data["message"]}')
        tab_class = tab_classes('connect')
        return render_template('wordplay/connect.html', source=source, target=target,
                               error=data['message'], tab_classes=tab_class)
    else:
        admin_alert_thread('Web App - Log',
                           f'WORDPLAY\n{request.url}\nRendered connect result page.\nSTART: {source}\nTARGET: {target}')
        tab_class = tab_classes('connect')
        return render_template('wordplay/connect_result.html', source=source, target=target,
                               info=data['message'], paths=data['data'], tab_classes=tab_class)
