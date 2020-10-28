import spotipy, requests, json, re, os
from dotenv import load_dotenv; load_dotenv()
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup

SCOPE = os.getenv('SCOPE')
USERNAME = "SvAlpha"
WITR_LIST_ID = "5oZHtALZHNjUTxUg6eavaq"
BANNED_WORDS = [word for word in open('banned_words.txt')]

token = util.prompt_for_user_token(USERNAME, SCOPE)

sp = spotipy.Spotify(auth=util.prompt_for_user_token(USERNAME, SCOPE))

results = sp.user_playlist_tracks(USERNAME,WITR_LIST_ID)
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

def prRed(skk):
    print("\033[91m{}\033[00m".format(skk))

def prYellow(skk):
    print("\033[93m{}\033[00m".format(skk)) 

def prGreen(skk):
    print("\033[92m{}\033[00m".format(skk)) 

def request_song_info(song_title, artist_name):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + 'nUVDo5c_QK3BAaHaxYWcyJ3O6jY-Sfbf80VhgkEg08o1ifa0f2xvldCpPy4dT788'}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response

track_list = list()
for elem in tracks:
    track_list += [(elem['track']['name'] + " || " + elem['track']['artists'][0]['name'])]

not_found_lst = list()

for elem in track_list:
    lst = elem.split(" || ")
    title_orig = lst[0]
    title = title_orig.split()
    if len(title) == 2:
        if title[1] == "(Remastered)":
            title = [title[0]]
    elif len(title) > 2:
        title = title[0:2]
    title = ' '.join(title)
    artist = lst[1]
    website = request_song_info(title, artist)
    json = website.json()
    remote_song_info = None

    for hit in json['response']['hits']:
        if artist.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break

    song_url = None
    if remote_song_info:
        song_url = remote_song_info['result']['url']
    else:
        not_found_lst += [artist + " || " + title_orig]
        continue
    
    if song_url:
        page = requests.get(song_url)
        html = BeautifulSoup(page.text, 'html.parser')
        lyrics = html.find('div', class_='lyrics').get_text()
        if lyrics.strip() == "[Instrumental]":
            print("Instrumental: ", end='')
    else:
        print("No URL returned for " + artist + "'s \"" + title + "\"")
        continue

    bad_count = 0;
    for word in BANNED_WORDS:
        bad_count += len(re.findall(word, lyrics.lower()))

    if bad_count == 1 or bad_count == 2:
        prYellow(artist + "'s \"" + title_orig + "\" contains " + str(bad_count) + " banned words.")
    elif bad_count > 2:
        prRed(artist + "'s \"" + title_orig + "\" contains " + str(bad_count) + " banned words.")
    else:
        prGreen(artist + "'s \"" + title_orig + "\" contains " + str(bad_count) + " banned words.")

print("Searches not found for: ")
for elem in not_found_lst:
    print("\t" + elem)
