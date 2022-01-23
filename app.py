import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.preprocessing import StandardScaler
import PySimpleGUI as sg
import configparser

RECOMMEND = ['Recommend', 'Refresh']
CREATE_PLAYLIST = 'Create Playlist'
ADD_PLAYLIST = 'Add Playlist'
EXIT = 'Exit'
CANCEL = 'Cancel'
OK = 'Ok'


def playlist_window(spotify_instance, user_id, results, reccoid):
    save_prompt_layout = [
        [sg.Text("Input a playlist name to add the tracks to your Spotify account", size=(45, 1))],
        [sg.Text("Playlist Name", size=(10, 1)), sg.Input(size=(30, 1), key='Name')],
        [sg.Column([[sg.Button(ADD_PLAYLIST, disabled_button_color='gray'), sg.Button(CANCEL)]],
                   justification='center')],
        [sg.StatusBar("", size=(0, 1), key='-STATUS-')]
    ]
    save_prompt = sg.Window('Add Playlist to Spotify', save_prompt_layout, finalize=True)

    while True:
        event, values = save_prompt.read()
        if event in (sg.WINDOW_CLOSED, CANCEL, OK):
            break
        elif event == ADD_PLAYLIST:
            playlist_name = values['Name']
            if playlist_name:
                # state = "Login OK" if login(username, password) else "Login failed"
                playlist_description = 'This playlist was constructed from these top 5 tracks: '
                playlist_description += ', '.join([f"{item['name']} by {item['artists'][0]['name']}"
                                                   for i, item in enumerate(results['items'])])
                create_playlist_result = spotify_instance.user_playlist_create(user_id, playlist_name, public=True,
                                                                 collaborative=False, description=playlist_description)
                playlist_id = create_playlist_result['id']

                # add the songs to the playlist
                spotify_instance.playlist_add_items(playlist_id, reccoid, position=None)

                state = playlist_name + " was added to your Spotify Account"
                save_prompt[ADD_PLAYLIST](disabled=True)
                save_prompt[CANCEL](OK)
            else:
                state = "Playlist name required"
            # playlist creation confirmation
            save_prompt['-STATUS-'].update(state)

    save_prompt.close()


def main():
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
    main_window_layout = [[sg.Text('Welcome to our Music Recommendation Program', size=(40, 1),
                                   font=("Helvetica", 15))],
                          [sg.Text('Your Top Tracks', size=(40, 1), font=("Helvetica", 12))],
                          [sg.MLine(key='-ML1-' + sg.WRITE_ONLY_KEY, size=(40, 8))],
                          [sg.Text('Recommended Tracks', size=(40, 1), font=("Helvetica", 12))],
                          [sg.MLine(key='-ML2-' + sg.WRITE_ONLY_KEY, size=(40, 8))],
                          [sg.Button(RECOMMEND[0]),
                           sg.Button(CREATE_PLAYLIST, disabled=True, disabled_button_color='gray'),
                           sg.Button(EXIT)]]

    # Create the Window
    main_window = sg.Window('Music Recommender', main_window_layout)
    top_songs_loaded = False

    # Event Loop to process events and get input
    while True:

        event, values = main_window.read()
        if event in (sg.WIN_CLOSED, EXIT):  # if user closes window or clicks exit
            break
        elif event == RECOMMEND[0]:
            if not top_songs_loaded:
                # user sign in
                sp = spotipy.Spotify(
                    auth_manager=SpotifyOAuth(scope=scope, client_id=cid, client_secret=secret, redirect_uri=uri))

                # get user info
                user_info = sp.current_user()
                user_id = user_info['id']
                user_name = user_info['display_name']
                main_window['-ML1-' + sg.WRITE_ONLY_KEY].print(f'Welcome, {user_name}.\n')

                # get the users top 5 songs
                track_ids = []  # list that stores the track ids of the user's top tracks
                top_tracks = sp.current_user_top_tracks()[:5]
                for i, item in enumerate(top_tracks['items']):
                    main_window['-ML1-' + sg.WRITE_ONLY_KEY].print(
                        f"{i + 1}) {item['name']} by {item['artists'][0]['name']}")
                    track_ids.append(item['id'])

                # get audio features for a series of tracks
                top_songs_features = sp.audio_features(track_ids)
                # results has a list of dictionaries, which contain each song's features

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
                clustering = kmeans.fit_predict(
                    dataframe[['acousticness', 'valence', 'danceability', 'energy', 'instrumentalness',
                               'liveness', 'loudness', 'speechiness', 'tempo', 'key', 'duration_ms',
                               'mode']])

                # adding the predicted clusterings to the dataframe graph as a column
                dataframe["cluster"] = clustering

                # make a dataframe with the features as columns of the top5 songs of the user
                top5user = pd.DataFrame(data=top_songs_features)

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

                top_songs_loaded = True
                main_window[CREATE_PLAYLIST].update(disabled=False)
                main_window[RECOMMEND[0]](RECOMMEND[1])

            # predict which clusters the top5 songs belong to using the k-means cluster that we built
            recommended_songs = kmeans.predict(
                top5user[['acousticness', 'valence', 'danceability', 'energy', 'instrumentalness',
                          'liveness', 'loudness', 'speechiness', 'tempo', 'key', 'duration_ms',
                          'mode']])

            """
            Making the recommendations
            """

            finalreccoid = []
            # list of song names
            finalrecconame = []

            for x in recommended_songs:
                filtereddf = dataframe.loc[dataframe['cluster'] == x]
                filtereddf = filtereddf.sample(n=5)
                recommendedsongidlist = filtereddf['id'].tolist()
                recommendedsongnamelist = filtereddf['name'].tolist()
                finalreccoid.extend(recommendedsongidlist)
                finalrecconame.extend(recommendedsongnamelist)

            main_window['-ML2-' + sg.WRITE_ONLY_KEY]('')
            for i, song in enumerate(finalrecconame):
                main_window['-ML2-' + sg.WRITE_ONLY_KEY].print(f"{i + 1}) {song}")

        elif event == CREATE_PLAYLIST:
            playlist_window(sp, user_id, top_tracks, finalreccoid)

    main_window.close()


if __name__ == '__main__':
    main()
