# song-recommendation-system

This project will allow you to create a spotify album from your favorite songs.

## Preparation

Since this project is in active development, submit your spotify username
in advance to be added to the list of developers using the product.

In addition to cloning this repository, you'll find a `config.ini` file
in the Google Drive folder. Please download that and save it in the project directory.

## Environment set-up

You need a few libraries to run this code. To maintain a sanitary python
work environment, we recommend one of these two options.

To run this code with `conda`, create an environment with
```
conda create -n ai-songs -c conda-forge spotipy scikit-learn pandas numpy matplotlib
```
With this system, use `conda activate ai-songs` and `conda deactivate` to enter and exit this environment.


To use a combination of `venv` and `pip`, in the project directory, you could run
```
python -m venv ai-songs
source ai-songs/bin/activate
pip install spotipy scikit-learn pandas numpy matplotlib
```
With this system, use `source ai-songs/bin/activate` and `deactivate` to enter and exit this environment.

## Usage

Upon opening the program, the window will appear blank. 

1. Run `python app.py`
2. Start the process by clicking `Recommend`
3. Log in if you haven't already
4. Once that has processed, you may review the songs listed and decide whether
you'd like to keep the playlist. Hit refresh as many times as you'd like.
4. Once you like the playlist that has been produced, press `Create Playlist` and choose a name.

You can follow this process as many times as you like. Since your top songs won't change rapidly, it is faster
to click `Refresh` several times than to restart the program.
