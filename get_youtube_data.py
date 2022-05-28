import subprocess
import requests
import json
import math
from pytube import Playlist
import MySQLdb
import ev

#基本情報取得
ypath = "youtube-dl"#yt-dlpでも動くはず
api_key = ev.youtubev3_apikey

def evolution_VideoidFromPlaylist(playlist_id_list,iglist=[]):#pytubeとappendをキャッシュして高速化
    k_vid = []
    k_v_a = k_vid.append
    for x in range(len(playlist_id_list)):
        playlist = Playlist("https://www.youtube.com/playlist?list=" + playlist_id_list[x])
        for n in range(len(playlist)):
            k_v_a(str(playlist[n])[32:])
    n_vid_l = list(set(k_vid) ^ set(iglist))#かぶりを排除かつ新しいののみ抽出
    return n_vid_l

def highper_vidFromPlaylist(playlist_id,iglist=[]):#subprocessを利用し無理やり並列実行化 mysqlを経由してデータをやり取り
    connection = MySQLdb.connect(host=ev.mysql_host,user=ev.mysql_user,passwd=ev.mysql_ps,db="vsong")
    cur = connection.cursor()
    cur.execute("delete from vsong.tmp_vid")
    connection.commit()
    proc_list = []
    loop_num = len(playlist_id)
    for n in range(loop_num):
        proc = subprocess.Popen([ev.python_call,'get_youtube_playlist.py',str(playlist_id[n])])
        proc_list.append(proc)
    for subproc in proc_list:
        subproc.wait()
    proc_list = []
    cur.execute("SELECT DISTINCT videoid FROM vsong.tmp_vid")
    kk_vid = cur.fetchall()
    k_vid = []
    k_a = k_vid.append
    for w in range(len(kk_vid)):
        k_a(str(kk_vid[w])[2:-3])
    cur.close()
    connection.close()
    n_vid_l = list(set(k_vid) - set(iglist))
    return n_vid_l

def VideoidFromPlaylist(playlist_id):#無制限
    all_path = ypath + " -j --flat-playlist https://www.youtube.com/playlist?list=" + playlist_id
    jsong = subprocess.check_output(all_path)
    #変換
    jsonu = jsong.decode("utf-8").splitlines()
    vid_list = []
    for n in range(len(jsonu)):
        json_one = json.loads(jsonu[n])
        vid_list.append(json_one["url"])
    return vid_list

def VideoidToTitle(Video_id):#無制限
    all_path = ypath + " --get-title " + "https://www.youtube.com/watch?v=" + Video_id
    title = subprocess.check_output(all_path)
    title = title.decode("utf-8")
    return title

def VideoidToSamune(Video_id,save_path):
    url = "https://i.ytimg.com/vi/" + Video_id + "/maxresdefault.jpg"
    pic = requests.get(url)
    f_path = save_path + Video_id + ".jpg"
    f = open(f_path, "wb")
    f.write(pic.content)
    f.close()
    return f_path

def videoid_lToMInfo(videoid_list):
    n_n = math.ceil(float(len(videoid_list)/50))
    info_v = []
    info_v_a = info_v.append
    for n in range(n_n):
        k_vlist = []
        k_vlist_a = k_vlist.append
        if n_n==n+1:
            length = len(videoid_list) - (50 * n)
        else:
            length = 50
        for x in range(length):
            k_vlist_a(videoid_list[x+50*n])
        n_list = str(k_vlist).replace("'","").replace(" ","").replace("[","").replace("]","")
        jsong = requests.get("https://www.googleapis.com/youtube/v3/videos?id=" + n_list + "&key=" + api_key + "&part=snippet")
        new_json = jsong.json()
        for r in range(new_json["pageInfo"]["totalResults"]):
            n_j = new_json["items"][r]["snippet"]
            info_v_a([new_json["items"][r]["id"],n_j["channelId"],n_j["publishedAt"],n_j["title"],n_j["description"]])
    return info_v
        
def VideoidToManyInfo(Video_id):#api使用1日1万回まで
    #url作り
    url = "https://www.googleapis.com/youtube/v3/videos?id=" + Video_id + "&key=" + api_key + "&part=snippet"
    jsong = requests.get(url)
    new_json = jsong.json()
    ti = new_json["items"][0]["snippet"]["publishedAt"]
    title = new_json["items"][0]["snippet"]["title"]
    description = new_json["items"][0]["snippet"]["description"]
    ch_id = new_json["items"][0]["snippet"]["channelId"]
    return title,ti,ch_id,description

def VideoidToStatics(video_id):
    vid_l = str(video_id).replace("'","").replace(" ","").replace("[","").replace("]","")
    url = "https://www.googleapis.com/youtube/v3/videos?id=" + vid_l + "&key=" + api_key + "&part=statistics"
    jsong = requests.get(url)
    new_json = jsong.json()
    result_list = []
    result_list_a = result_list.append
    for i in range(new_json["pageInfo"]["totalResults"]):
        #エラーの時はとりあえず-1を出力
        _id = new_json["items"][i]["id"]
        try:
            view_count = new_json["items"][i]["statistics"]["viewCount"]
        except:
            view_count = -1
        try:
            like_count = new_json["items"][i]["statistics"]["likeCount"]
        except:
            like_count = -1
        try:
            comment_count = new_json["items"][i]["statistics"]["commentCount"]
        except:
            comment_count = -1
        result_list_a([_id,view_count,like_count,comment_count])
    return result_list

def ExtremeVideoToStatics(videoid_list):
    n_n = math.ceil(float(len(videoid_list)/50))
    sta_v = []
    sta_v_a = sta_v.append
    for n in range(n_n):
        k_vidl = []
        if n_n==n+1:
            length = len(videoid_list) - (50 * n)
        else:
            length = 50
        k_ap = k_vidl.append
        for x in range(length):
            k_ap(videoid_list[x+50*n])
        n_list = str(k_vidl).replace("'","").replace(" ","").replace("[","").replace("]","")
        jsong = requests.get("https://www.googleapis.com/youtube/v3/videos?id=" + n_list + "&key=" + api_key + "&part=statistics")
        new_json = jsong.json()
        for i in range(new_json["pageInfo"]["totalResults"]):
            #エラーの時はとりあえず-1を出力
            _id = new_json["items"][i]["id"]
            try:
                view_count = new_json["items"][i]["statistics"]["viewCount"]
            except:
                view_count = -1
            try:
                like_count = new_json["items"][i]["statistics"]["likeCount"]
            except:
                like_count = -1
            try:
                comment_count = new_json["items"][i]["statistics"]["commentCount"]
            except:
                comment_count = -1
            sta_v_a([_id,view_count,like_count,comment_count])
    return sta_v

def ChannnelidToInfo(ch_id):
    url = "https://www.googleapis.com/youtube/v3/channels?id=" + ch_id + "&key=" + api_key + "&part=snippet"
    jsong = requests.get(url)
    new_json = jsong.json()
    ch_name = new_json["items"][0]["snippet"]["title"]
    pic_url_k = new_json["items"][0]["snippet"]["thumbnails"]["default"]["url"]
    pic_url = pic_url_k[0:pic_url_k.find("=")]
    return ch_name,pic_url

def ExtremeChidToInfo(chid_list):
    n_n = math.ceil(float(len(chid_list)/50))
    sta_c = []
    sta_c_a = sta_c.append
    for r in range(n_n):
        if n_n-1==r:
            n_loop = len(chid_list) - (50 * r)
        else:
            n_loop = 50
        k_chlist = []
        k_chlist_a = k_chlist.append
        for x in range(n_loop):
            k_chlist_a(chid_list[x+50*r])
        n_list = str(k_chlist).replace("'","").replace(" ","").replace("[","").replace("]","")
        jsong = requests.get("https://www.googleapis.com/youtube/v3/channels?id=" + n_list + "&key=" + api_key + "&part=snippet")
        new_json = jsong.json()
        for i in range(new_json["pageInfo"]["totalResults"]):
            _ch_id = new_json["items"][i]["id"]
            ch_name = new_json["items"][i]["snippet"]["title"]
            pic_url_k = new_json["items"][i]["snippet"]["thumbnails"]["default"]["url"]
            pic_url = pic_url_k[0:pic_url_k.find("=")]
            sta_c_a([_ch_id,ch_name,pic_url])
    return sta_c

def Channnelid_listToInfo(ch_id):
    chid_l = str(ch_id).replace("'","").replace(" ","").replace("[","").replace("]","")
    #url = "https://www.googleapis.com/youtube/v3/channels?id=" + chid_l + "&key=" + api_key + "&part=snippet"
    jsong = requests.get("https://www.googleapis.com/youtube/v3/channels?id=" + chid_l + "&key=" + api_key + "&part=snippet")
    new_json = jsong.json()
    ch_list = []
    for i in range(new_json["pageInfo"]["totalResults"]):
        _ch_id = new_json["items"][i]["id"]
        ch_name = new_json["items"][i]["snippet"]["title"]
        pic_url_k = new_json["items"][i]["snippet"]["thumbnails"]["default"]["url"]
        pic_url = pic_url_k[0:pic_url_k.find("=")]
        ch_list.append([_ch_id,ch_name,pic_url])
    return ch_list
#print(timeit.timeit('VideoidFromPlaylist("PL_0A0t0-Y0AMGFPCuKDZ3o8PMVpKcNvOQ")', number=1, globals=globals()))#19.2414402 youtube-dl
#print(timeit.timeit('VideoidFromPlaylist("PL_0A0t0-Y0AMGFPCuKDZ3o8PMVpKcNvOQ")', number=1, globals=globals()))#25.480206
#print(timeit.timeit("evolution_VideoidFromPlaylist(['PL_0A0t0-Y0AMGFPCuKDZ3o8PMVpKcNvOQ'])", number=1, globals=globals()))#8.508521