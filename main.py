from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import requests

chosen_date = input("Which year would you like to travel back to?\n"
                    "Type the date in the format YYYY-MM-DD:\n")
url = f"https://www.billboard.com/charts/hot-100/{chosen_date}"

# REQUESTS
response = requests.get(url=url)
data = response.text

# BEAUTIFULSOUP
page = BeautifulSoup(data, features='html.parser')
ranking_data = page.findAll(
    'span',
    attrs={
        'class',
        'chart-element__rank__number'
    }
)
artist_data = page.findAll(
    'span',
    attrs={
        'class',
        'chart-element__information__artist'
    }
)
title_data = page.findAll(
    'span',
    attrs={
        'class',
        'chart-element__information__song'
    }
)

rankings, artists, titles = [], [], []
[rankings.append(ranking.string) for ranking in ranking_data]
[artists.append(artist.string) for artist in artist_data]
[titles.append(title.string) for title in title_data]

playlist = list(zip(rankings, artists, titles))
# print(playlist)

# WRITE TO FILE
with open(f"hot-100_playlist_{chosen_date}.txt", mode="w") as file:
    file.write(f"Billboard Hot-100 ({chosen_date})\n"
               f"-------------------------------\n")
    for track_info in playlist:
        file.write(f"{int(track_info[0]), track_info[1], track_info[2]}\n")

# SPOTIFY
SPOTIFY_CLIENT_ID = "**********"
SPOTIFY_CLIENT_SECRET = "**********"
SPOTIFY_REDIRECT_URI = "http://example.com"
PLAYLIST_URL = f"https://api.spotify.com/v1/users/{SPOTIFY_CLIENT_ID}/playlists"

# SPOTIFY - AUTHORIZATION
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="playlist-modify-private",
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

# SPOTIFY - FETCH URI
uri_list = []
for song in playlist:
    search_results = sp.search(q=f"track:{song[2]} year:{chosen_date[:4]}", type="track")
    try:
        uri = search_results['tracks']['items'][0]['uri']
        uri_list.append(uri)
    except IndexError:
        print(f"{song[2]} by {song[1]} doesn't exist on Spotify. Skipped.")
        with open("songs_skipped.txt", mode="a") as file:
            file.write(f"{song[2]} by {song[1]}\n")

with open("uri_results.txt", mode="w") as file:
    for uri in uri_list:
        file.write(f"{uri}\n")

# SPOTIFY - CREATE PLAYLIST
new_playlist = sp.user_playlist_create(
    user=user_id,
    name=f"Billboard Hot-100 ({chosen_date})",
    public=False
)

# SPOTIFY - ADD SONGS
sp.playlist_add_items(playlist_id=new_playlist["id"], items=uri_list)
