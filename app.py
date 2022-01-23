from pickle import TRUE
from tkinter.tix import Tree
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot  as plt
import PySimpleGUI as sg
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
cid = config['Service']['cid']
secret = config['Service']['secret']
uri = 'http://localhost:8888/callback'
scope = ','.join(['user-top-read',
                  'user-library-read',
                  'user-follow-read',
                  'user-read-currently-playing',
                  'user-read-recently-played',
                  'playlist-modify-private',
                  'playlist-modify-public'])

sg.theme('DarkTeal6')

# window
layout = [[sg.Text('Welcome to our Music Recommendation Program', size=(40, 1), font=("Helvetica", 15))],
          [sg.Text('Your Top Tracks', size=(40, 1), font=("Helvetica", 12))],
          [sg.MLine(key='-ML1-' + sg.WRITE_ONLY_KEY, size=(40, 8))],
          [sg.Text('Recommended Tracks', size=(40, 1), font=("Helvetica", 12))],
          [sg.MLine(key='-ML2-' + sg.WRITE_ONLY_KEY, size=(40, 8))],
          [sg.Button('Recommend'), sg.Button('Exit')]]

def playlist_window(finalreccoid):
        klayout = [
        [sg.Text("Input a playlist name to add the tracks to your Spotify account", size=(45, 1))],
        [sg.Text("Playlist Name", size=(10, 1)), sg.Input(size=(30, 1), key='Name')],
        [sg.Column([[sg.Button("Add Playlist"), sg.Button("Exit")]], justification='center')],
        [sg.StatusBar("", size=(0, 1), key='-STATUS-')]
        ]
        new_window = sg.Window('Add Playlist to Spotify', klayout, finalize=True)

        while True:
            event, values = new_window.read()
            if event in (sg.WINDOW_CLOSED, "Exit"):
                break
            elif event == "Add Playlist":
                playlistname = values['Name']
                if playlistname:
                    # state = "Login OK" if login(username, password) else "Login failed"
                    playlist_description = 'This playlist was constructed from these top 5 tracks: '
                    playlist_description += ', '.join([f"{item['name']} by {item['artists'][0]['name']}gq"
                                                       for i, item in enumerate(results['items'][:5])])
                    results3 = sp.user_playlist_create(user_id, playlistname, public=True, collaborative=False,
                                                       description=playlist_description)
                    playlist_id = results3['id']
                    
                    # add the songs to the playlist
                    results3 = sp.playlist_add_items(playlist_id, finalreccoid, position=None)
                    
                    state = playlistname + " was added to your Spotify Account"
                    # playlist creation confirmation
                    new_window['-STATUS-'].update(state)
                else:
                    state = "Playlist name required"
                new_window['-STATUS-'].update(state)

        new_window.close()


# Create the Window
window = sg.Window('Music Recommender', layout)

# Event Loop to process events and get input
while True:

    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
        break
    
    # user sign in
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=cid, client_secret=secret, redirect_uri=uri))

    # get the users top 5 songs
    track_id = []  # list that stores the track ids of the user's top tracks
    results = sp.current_user_top_tracks()
    for i, item in enumerate(results['items'][:5]):
        window['-ML1-'+sg.WRITE_ONLY_KEY].print(
            i+1, ")", item['name'], "by", item['artists'][0]['name']) 
        track_id.append(item['id'])

    # get user info
    info = sp.current_user()
    user_id = info['id']
    user_name = info['display_name']

    # get audio features for a series of tracks
    results2 = sp.audio_features(track_id)  # results has a list of dictionaries, which contain each song's features
    # pprint(results2)

    dataframe = pd.read_csv('data.csv')

    # defining  KMeans
    kmeans = KMeans(n_clusters=100, init='k-means++', max_iter=100, n_init=1, verbose=0, random_state=3425)

    """
    Normalizing numerical columns of the graph using Standard Scalar to perform k-means clustering
    """

    scaler = StandardScaler()
    numerical_columns = ['loudness',
                         'tempo',
                         'key',
                         'year',
                         'duration_ms',
                         'explicit',
                         'mode',
                         'popularity']
    for label in numerical_columns:
        scaler.fit(dataframe[[label]])
        dataframe[label] = scaler.transform(dataframe[[label]])

    """
    Perform K-Means clustering on N features
    """
    clustering = kmeans.fit_predict(dataframe[['acousticness', 'valence', 'danceability', 'energy', 'instrumentalness',
                                               'liveness', 'loudness', 'speechiness', 'tempo', 'key', 'duration_ms',
                                               'mode']])

    # adding the predicted clusterings to the dataframe graph as a column
    dataframe["cluster"] = clustering

    # make a dataframe with the features as columns of the top5 songs of the user
    top5user = pd.DataFrame(data=results2)

    """
    Normalize the numerical columns for the top5 songs using Standard Scaler
    """
    user_numerical_columns = ['loudness',
                              'tempo',
                              'key',
                              # 'year',
                              'duration_ms',
                              # 'explicit',
                              'mode',
                              # 'popularity'
                              ]
    for label in user_numerical_columns:
        scaler.fit(top5user[[label]])
        top5user[label] = scaler.transform(top5user[[label]])

    # predict which clusters the top5 songs belong to using the k-means cluster that we built
    clustering5songs = kmeans.predict(top5user[['acousticness', 'valence', 'danceability', 'energy', 'instrumentalness',
                                                'liveness', 'loudness', 'speechiness', 'tempo', 'key', 'duration_ms',
                                                'mode']])

    """
    Making the recommendations
    """

    finalreccoid = []
    # list of song names
    finalrecconame = []

    for x in clustering5songs:
        filtereddf = dataframe.loc[dataframe['cluster'] == x]
        filtereddf = filtereddf.sample(n=5)
        recommendedsongidlist = filtereddf['id'].tolist()
        recommendedsongnamelist = filtereddf['name'].tolist()
        finalreccoid.extend(recommendedsongidlist)
        finalrecconame.extend(recommendedsongnamelist)
        
    for i, song in enumerate(finalrecconame):
        window['-ML2-' + sg.WRITE_ONLY_KEY].print(f"{i + 1}) {song}")
    

    playlist_window(finalreccoid)

window.close()


