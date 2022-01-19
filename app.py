from pickle import TRUE
from tkinter.tix import Tree
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

cid = '5afdc63179404ae299ca0fe6ea3f42f6'
secret = '150228edfc42438fb2e627ac0127b412'
uri = 'http://localhost:8888/callback'
scope = "user-top-read,user-library-read,user-follow-read,user-read-currently-playing,user-read-recently-played,playlist-modify-private,playlist-modify-public"

#user sign in
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=cid, client_secret=secret, redirect_uri=uri))

#get the users top 5 songs 
track_id = [] #list that stores the track ids of the user's top tracks
results = sp.current_user_top_tracks() 
for i, item in enumerate(results['items'][:5]): 
   print(i+1, ") track: ", item['name'], ", artist: ", item['artists'][0]['name'], ", track ID: ", item['id'])
   track_id.append(item['id'])

#get user info
info = sp.current_user()
user_id = info['id']
user_name = info['display_name']

#get audio features for a series of tracks
results2 = sp.audio_features(track_id) #results has a list of dictionaries, which contain each song's features
pprint(results2) 

#create a playlist for the user
playlist_name = 'New recommended songs'
playlist_description = 'Thanks for using the songs recommendation system app. In this playlist, you can find your 30 recommended songs.'
results3 = sp.user_playlist_create(user_id, playlist_name, public=True, collaborative=False, description=playlist_description)
playlist_id = results3['id']

#add the songs to the playlist
items = [] #list of ids of the songs i want to add to the playlist (get it from Harsha) #TODO
results3 = sp.playlist_add_items(playlist_id, items, position=None) 


