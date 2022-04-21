import spotipy
from ytmusicapi import YTMusic

client_id = "8e4edddd261847c49cdba295af2f890e"
client_secret = "8d01f1f550f84b2aab392a5460dc8ad9"
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
ytmusic = YTMusic()
def search_music(music_name):
    sp_result = spotify.search(q=music_name, type='track')
    yt_result = ytmusic.search(query=music_name,limit=1)[0]
    try:
        song_name_sp = sp_result["tracks"]["items"][0]["name"]
    except:
        song_name_sp = "faul"
    try:
        song_name_yt = yt_result["title"]
    except:
        song_name_yt = "faul"
    try:
        at_name = yt_result["artists"][0]["name"]
    except:
        at_name = "faul"
    try:
        spid = sp_result["tracks"]["items"][0]["id"]
    except:
        spid = "faul"
    try:
        ytid = yt_result["videoId"]
    except:
        ytid = "faul"
    music_data = [song_name_sp,song_name_yt,at_name,spid,ytid]
    return music_data