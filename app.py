from pickle import TRUE
from tkinter.tix import Tree
from pprint import pprint
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot  as plt
import PySimpleGUI as sg
import spotipy
from spotipy.oauth2 import SpotifyOAuth

cid = 'b724fb0e25894e9f97220f2a560a3789'
secret = '29d7540a9f1245ac855efd1db30ae5c3'
uri = 'http://localhost:8888/callback'
scope = "user-top-read,user-library-read,user-follow-read,user-read-currently-playing,user-read-recently-played,playlist-modify-private"
birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'

sg.theme('DarkTeal6')

# window 
layout = [  [sg.Text('Welcome to our Music Recommendation Program', size=(40,1), font=("Helvetica", 15))],
            [sg.Text('Your Top Tracks', size=(40,1), font=("Helvetica", 12))],
            [sg.MLine(key='-ML1-'+sg.WRITE_ONLY_KEY, size=(40,8))],
            [sg.Text('Recommended Tracks', size=(40,1), font=("Helvetica", 12))],
            [sg.MLine(key='-ML2-'+sg.WRITE_ONLY_KEY, size=(40,8))],
            [sg.Button('Recommend'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Music Recommender', layout)
# Event Loop to process "events" and get the "values" of the inputs

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    #user sign in
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=cid, client_secret=secret, redirect_uri=uri))
    
    #get the users top 5 songs 
    track_id = [] #list that stores the track ids of the user's top tracks
    results = sp.current_user_top_tracks() 
    for i, item in enumerate(results['items'][:5]):
        window['-ML1-'+sg.WRITE_ONLY_KEY].print(i+1, ")", item['name'], "by", item['artists'][0]['name'])
        track_id.append(item['id'])

    #get user info
    info = sp.current_user()
    user_id = info['id']
    user_name = info['display_name']

    #get audio features for a series of tracks
    results2 = sp.audio_features(track_id) #results has a list of dictionaries, which contain each song's features
    #pprint(results2) 


    dataframe=pd.read_csv('data.csv')

    #defining  KMeans
    kmeans=KMeans(n_clusters=100, init='k-means++', max_iter=100, n_init=1, verbose=0, random_state=3425)

    """
    Normalizing numerical columns of the graph using Standard Scalar to perform k-means clustering
    """

    scaler=StandardScaler()
    scaler.fit(dataframe[['loudness']])
    dataframe['loudness'] = scaler.transform(dataframe[['loudness']])
    scaler.fit(dataframe[['tempo']])
    dataframe['tempo'] = scaler.transform(dataframe[['tempo']])
    scaler.fit(dataframe[['key']])
    dataframe['key'] = scaler.transform(dataframe[['key']])
    scaler.fit(dataframe[['year']])
    dataframe['year'] = scaler.transform(dataframe[['year']])
    scaler.fit(dataframe[['duration_ms']])
    dataframe['duration_ms'] = scaler.transform(dataframe[['duration_ms']])
    scaler.fit(dataframe[['explicit']])
    dataframe['explicit'] = scaler.transform(dataframe[['explicit']])
    scaler.fit(dataframe[['mode']])
    dataframe['mode'] = scaler.transform(dataframe[['mode']])
    scaler.fit(dataframe[['popularity']])
    dataframe['popularity'] = scaler.transform(dataframe[['popularity']])


    """
    Perform K-Means clustering on N features
    """
    clustering=kmeans.fit_predict(dataframe[['acousticness','valence','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','key','duration_ms','mode']])


    #adding the predicted clusterings to the dataframe graph as a column
    dataframe["cluster"]=clustering

    #make a dataframe with the features as columns of the top5 songs of the user
    top5user=pd.DataFrame(data=results2)


    """
    Normalize the numerical columns for the top5 songs usin Standard Scaler
    """
    scaler.fit(top5user[['loudness']])
    top5user['loudness'] = scaler.transform(top5user[['loudness']])
    scaler.fit(top5user[['tempo']])
    top5user['tempo'] = scaler.transform(top5user[['tempo']])
    scaler.fit(top5user[['key']])
    top5user['key'] = scaler.transform(top5user[['key']])
    scaler.fit(top5user[['duration_ms']])
    top5user['duration_ms'] = scaler.transform(top5user[['duration_ms']])
    scaler.fit(top5user[['mode']])
    top5user['mode'] = scaler.transform(top5user[['mode']])


    #predict which clusters the top5 songs belong to using the k-means cluster that we built
    clustering5songs=kmeans.predict(top5user[['acousticness','valence','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','key','duration_ms','mode']])

    """
    Making the recommendations
    """

    finalreccoid=[]
    # list of song names
    finalrecconame=[]

    for x in clustering5songs:
        filtereddf=dataframe.loc[dataframe['cluster']==x]
        filtereddf=filtereddf.sample(n=5)
        recommendedsongidlist=filtereddf['id'].tolist()
        recommendedsongnamelist=filtereddf['name'].tolist()
        finalreccoid.extend(recommendedsongidlist)
        finalrecconame.extend(recommendedsongnamelist)

    #create a playlist for the user
    playlist_name = 'New recommended songs'
    playlist_description = 'Thanks for using the songs recommendation system app. In this playlist, you can find your 25 recommended songs. Here are the top 5 tracks we used to make the playlist: '
    for i, item in enumerate(results['items'][:5]): 
       playlist_description += f"{item['name']} by {item['artists'][0]['name']}, "
    results3 = sp.user_playlist_create(user_id, playlist_name, public=True, collaborative=False, description=playlist_description)
    playlist_id = results3['id']

    #add the songs to the playlist
    items = finalreccoid #list of ids of the songs i want to add to the playlist (get it from Harsha) #TODO
    results3 = sp.playlist_add_items(playlist_id, items, position=None)
    
    i=0
    for song in finalrecconame:   
        window['-ML2-'+sg.WRITE_ONLY_KEY].print(i+1, ")", song)
        i += 1

window.close()


