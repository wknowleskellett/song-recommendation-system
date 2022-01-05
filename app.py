import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

cid = '5afdc63179404ae299ca0fe6ea3f42f6'
secret = '150228edfc42438fb2e627ac0127b412'
uri = 'http://localhost:8888/callback'
scope = "user-top-read,user-library-read,user-follow-read,user-read-currently-playing,user-read-recently-played,playlist-modify-private"
birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'

#user sign in
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=cid, client_secret=secret, redirect_uri=uri))

#get the users top 5 songs 
track_id = [] #list that stores the track ids of the user's top tracks
results = sp.current_user_top_tracks() 
for i, item in enumerate(results['items'][:5]): 
   print(i+1, ") track: ", item['name'], ", artist: ", item['artists'][0]['name'], ", track ID: ", item['id']) 
   track_id.append(item['id'])

#get audio features for a series of tracks
results = sp.audio_features(track_id) #results has a list of dictionaries, which contain each song's features
pprint(results)


