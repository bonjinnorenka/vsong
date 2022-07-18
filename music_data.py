import math
import spotipy
from ytmusicapi import YTMusic
import ev

client_id = ev.spotify_clientid
client_secret = ev.spotify_secret
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
ytmusic = YTMusic()
def search_music(music_name:str):
    sp_result = spotify.search(q="track:"+music_name, type='track',market="jp")
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

def spotyfy_analyze(spidlist:list[str]):
    spidlist_length:int = len(spidlist)
    spid_loop_length:int = math.ceil(len(spidlist) / 100)
    maindata:list = []
    for x in range(spid_loop_length):
        spidlength_nowloop:int = 100
        if x == spid_loop_length - 1:
            spidlength_nowloop = spidlist_length - (100 * x)
        now_spidlist:list[str] = []
        for e in range(spidlength_nowloop):
            now_spidlist.append(spidlist[e+(100*x)])
        audioanlyze_result = spotify.audio_features(now_spidlist)
        maindata.extend([r for r in audioanlyze_result])
    #データ抽出
    resdata = []
    for r in range(len(maindata)):
        try:
            x = maindata[r]
            nowresdata = {}
            nowresdata["id"] = x["id"]
            nowresdata["acousticness"] = x["acousticness"]
            nowresdata["danceability"] = x["danceability"]
            nowresdata["energy"] = x["energy"]
            nowresdata["key"] = x["key"]
            nowresdata["liveness"] = x["liveness"]
            nowresdata["mode"] = x["mode"]
            nowresdata["tempo"] = x["tempo"]
            nowresdata["time_signature"] = x["time_signature"]
            nowresdata["valence"] = x["valence"]
            resdata.append(nowresdata)
        except:
            pass
    return resdata

def spotify_trackdata(spidlist:list[str]):
    spidlist_length:int = len(spidlist)
    spid_loop_length:int = math.ceil(len(spidlist) / 50)
    maindata:list = []
    for x in range(spid_loop_length):
        spidlength_nowloop:int = 50
        if x == spid_loop_length - 1:
            spidlength_nowloop = spidlist_length - (50 * x)
        now_spidlist:list[str] = []
        for e in range(spidlength_nowloop):
            now_spidlist.append(spidlist[e+(50*x)])
        audioanlyze_result = spotify.tracks(now_spidlist,market="jp")
        maindata.extend([r for r in audioanlyze_result["tracks"]])
    resdata = []
    for r in range(len(maindata)):
        try:
            x = maindata[r]
            nowresdata = {}
            nowresdata["id"] = x["id"]
            nowresdata["popularity"] = x["popularity"]
            nowresdata["artist_id"] = x["artists"][0]["id"]
            resdata.append(nowresdata)
        except:
            pass
    return resdata

