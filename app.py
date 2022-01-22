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
from matplotlib import pyplot as plt
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

#user sign in
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=cid, client_secret=secret, redirect_uri=uri))

#get the users top 5 songs 
track_id = [] #list that stores the track ids of the user's top tracks
results = sp.current_user_top_tracks() 
for i, item in enumerate(results['items'][:5]):
   print(f"{i+1}) track: {item['name']}, artist: {item['artists'][0]['name']}, track ID: {item['id']}")
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
clustering=kmeans.fit_predict(dataframe[['acousticness','valence','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','key','duration_ms','mode']])


#adding the predicted clusterings to the dataframe graph as a column
dataframe['cluster']=clustering

#make a dataframe with the features as columns of the top5 songs of the user
top5user=pd.DataFrame(data=results2)


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

print('These songs are in the generated playlist:')
for songid in finalreccoid:
    print(songid) # TODO convert these to song names
print()

#create a playlist for the user
playlist_name = input('What do you want to call your playlist? (Press Enter to cancel)\n')
if playlist_name != '':
    playlist_description = 'This playlist was constructed from these top 5 tracks: '
    playlist_description += ', '.join([f"{item['name']} by {item['artists'][0]['name']}gq"
                                       for i, item in enumerate(results['items'][:5])])
    results3 = sp.user_playlist_create(user_id, playlist_name, public=True, collaborative=False, description=playlist_description)
    playlist_id = results3['id']

    #add the songs to the playlist
    results3 = sp.playlist_add_items(playlist_id, finalreccoid, position=None)
