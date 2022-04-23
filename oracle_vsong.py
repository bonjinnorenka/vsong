import math
import os
import cx_Oracle
from requests import request
import requests
import get_youtube_data as gy
import music_data as md
import datetime
import collections
import urllib.parse
import json
import random
import ev

con = cx_Oracle.connect(ev.oracle_user, ev.oracle_ps, ev.oracle_connect_string)
print("Database version:", con.version + "\tデータベースに正常に接続できました。")
cur = con.cursor()
cur.execute("alter session set nls_date_format='YYYY-MM-DD HH24:MI:SS'")

#webサイト用変数設定
siteurl = "vsong.fans"
header = """<style>.Top{font-size:40px;text-align:center}nav ul{display:flex;justify-content:center;list-style:none;padding:0;margin:0}nav ul li{width:120px}.header-nav a{font-size:20px}</style><header><h2 class="Top"><a href="/">VtuberSing</a></h2><nav class="header-nav"><ul><li><a href="/search">検索</a><li><a href="/today">今日の人気</a></ul></nav></header>"""

def conect_close():#接続切るよう
    con.close()
    print("接続を切りました")

def update_videodata():
    cur.execute("alter session set nls_date_format='YYYY-MM-DD HH24:MI:SS'")
    cur.execute("SELECT DISTINCT video_id FROM VIDEO_ID")
    v_id_kl = cur.fetchall()
    #変形
    v_id_l = []
    v_id_a = v_id_l.append
    for x in range(len(v_id_kl)):
        v_id_a(str(v_id_kl[x])[2:-3])
    v_st = gy.ExtremeVideoToStatics(v_id_l)
    dt_now = datetime.datetime.now()
    dt_str = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day) + " " + str(dt_now.hour) + ":" + str(dt_now.minute) + ":" + str(dt_now.second)
    for x in range(len(v_st)):
        cur.execute("INSERT INTO VIDEO_V_DATA (VIDEO_ID,RELOAD_TIME,VIEW_C,LIKE_C,COMMENT_C) VALUES('" + v_st[x][0] + "','" + dt_str + "','" + str(v_st[x][1]) + "','" + str(v_st[x][2]) + "','" + str(v_st[x][3]) + "')")
    con.commit()

def correct_video_list():
    cur.execute("alter session set nls_date_format='YYYY-MM-DD HH24:MI:SS'")
    cur.execute("SELECT DISTINCT PLAYLIST_ID FROM CRAWLER_PLAYLIST")
    pid_kl = cur.fetchall()
    pid_l = []
    pid_l_a = pid_l.append
    for x in range(len(pid_kl)):
        pid_l_a(str(pid_kl[x])[2:-3])
    cur.execute("SELECT DISTINCT video_id FROM VIDEO_ID")
    v_id_kl = cur.fetchall()
    v_id_l = []
    v_id_a = v_id_l.append
    for x in range(len(v_id_kl)):
        v_id_a(str(v_id_kl[x])[2:-3])
    print("プレイリスト取得中")
    v_data = gy.videoid_lToMInfo(gy.highper_vidFromPlaylist(pid_l,v_id_l))
    kvar = 0
    for x in range(len(v_data)):
        if v_data[x][0] not in v_id_l:#万が一の重複に備え更なる重複チェックをする
            kvar += 1
            cur.execute("INSERT INTO VIDEO_ID (VIDEO_ID,CHANNEL_ID,UPLOAD_TIME,VIDEO_NAME,VIDEO_DESCRIPTION) VALUES('" + v_data[x][0] + "','" + v_data[x][1] + "','" + str(v_data[x][2])[:-1].replace("T"," ") + "','" + str(v_data[x][3]).replace("'","''") + "','" + str(v_data[x][4]).replace("'","''") + "')")
    con.commit()
    print(str(kvar) + "個のデータを追加しています")

def add_ch_data():
    cur.execute("SELECT DISTINCT CHANNEL_ID FROM VIDEO_ID")
    chid_kl = cur.fetchall()
    cur.execute("SELECT DISTINCT CH_ID FROM CH_ID WHERE CH_ID IS NOT NULL")
    al_chid = cur.fetchall()
    k_rec_chlist = list((set(chid_kl) ^ set(al_chid)) - set(al_chid))
    if len(k_rec_chlist)==0:
        return#処理終了
    r_chid_l = []
    r_chid_l_a = r_chid_l.append
    for x in range(len(k_rec_chlist)):
        r_chid_l_a(str(k_rec_chlist[x])[2:-3])
    rt_ch = gy.ExtremeChidToInfo(r_chid_l)
    for x in range(len(rt_ch)):
        cur.execute("INSERT INTO CH_ID (CH_ID,NAM,PICTURE_URL) VALUES ('" + rt_ch[x][0] + "','" + str(rt_ch[x][1]).replace("'","''") + "','" + rt_ch[x][2] + "')")
    con.commit()

def add_ch_data_self(chid_list):#めんどいので一つずつ
    st_chidlist = str(chid_list).replace("[","").replace("]","")
    cur.execute("select distinct ch_id from ch_id where ch_id in (" + st_chidlist + ")")
    if cur.fetchone()!=None:
        print("もうすでにある可能性があります")
        return#処理終了
    else:
        rt_ch = gy.ExtremeChidToInfo(chid_list)
        for x in range(len(rt_ch)):
            cur.execute("INSERT INTO CH_ID (CH_ID,NAM,PICTURE_URL) VALUES ('" + rt_ch[x][0] + "','" + str(rt_ch[x][1]).replace("'","''") + "','" + rt_ch[x][2] + "')")
        con.commit()
        print("データ追加完了")

def add_groupe_name():
    #テーブルA=ペアリスト テーブルB=動画IDリスト　参考https://www.projectgroup.info/tips/Oracle/SQL/SQL000001.html
    cur.execute("INSERT INTO PAIR_LIST_SECOND (GROUPE_NAME) SELECT distinct GROUPE_NAME FROM VIDEO_ID TAB_B WHERE GROUPE_NAME IS NOT NULL AND NOT EXISTS (SELECT 'X' FROM PAIR_LIST_SECOND TAB_A WHERE TAB_A.GROUPE_NAME = TAB_B.GROUPE_NAME)")
    con.commit()

def video2data(video_id):
    cur.execute("SELECT VIDEO_ID,CHANNEL_ID,VIDEO_NAME,MUSIC_NAME,GROUPE_NAME FROM VIDEO_ID WHERE VIDEO_ID = '" + video_id + "'")
    video_info = cur.fetchone()
    song_info = [video_info[0],search_musicdata(video_info[3])]
    if video_info[4]==None:#投稿者が一人で歌っている場合
        song_info.append(1)
        cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL FROM CH_ID ci WHERE CH_ID = '" + video_info[1] + "'")
        song_info.append(list(cur.fetchone()))
    else:#グループで歌っているパターン
        menlist = groupe_name2men_name(video_info[4])
        m_menlist = []
        for x in range(len(menlist)):
            m_menlist.append(search_chdata(menlist[x]))
        song_info.extend([len(menlist),m_menlist])
    return song_info

def video2data_v2(video_id):
    cur.execute("SELECT VIDEO_ID,CHANNEL_ID,VIDEO_NAME,MUSIC_NAME,GROUPE_NAME FROM VIDEO_ID WHERE VIDEO_ID = '" + video_id + "'")
    video_info = cur.fetchone()
    song_info = [video_info[0],search_musicdata(video_info[3])]
    if video_info[4]==None:#投稿者が一人で歌っている場合
        song_info.append(1)
        cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,BELONG_OFFICE FROM CH_ID ci WHERE CH_ID = '" + video_info[1] + "'")
        song_info.append(list(cur.fetchone()))
    else:#グループで歌っているパターン
        menlist = groupe_name2men_namev2(video_info[4])
        if len(menlist)==1:
            song_info.append(1)
            cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,BELONG_OFFICE FROM CH_ID WHERE (NICK_NAME_1 in ('" + menlist[0] + "') OR NICK_NAME_2 in ('" + menlist[0] + "')) and ig = 0")
            song_info.append(list(cur.fetchone()))
        else:
            song_info.extend([len(menlist),search_chdata_list_bf(menlist)])
    song_info.append(video_info)
    return song_info

def groupe_name2men_namev2(groupe_name):#v2のテーブルにアクセス
    songer_list = []
    songer_list_a = songer_list.append
    cur.execute("select MN_1,MN_2,MN_3,MN_4,MN_5,MN_6,MN_7,MN_8,MN_9,MN_10,MN_11,MN_12,MN_13,MN_14,MN_15,MN_16,MN_17,MN_18,MN_19,MN_20,MN_21,MN_22,MN_23,MN_24,MN_25,MN_26,MN_27,MN_28,MN_29,MN_30,MN_31,MN_32,MN_33,MN_34,MN_35,MN_36,MN_37,MN_38,MN_39 from PAIR_LIST_SECOND where groupe_name = '" + groupe_name.replace("'","''") + "'")
    k_gndata = cur.fetchone()
    for r in k_gndata:
        if r!=None:#データあり
            songer_list_a(r)
        else:
            break
    return songer_list

def groupe_name2men_name(groupe_name):#過去の遺産低速
    songer_list = []
    songer_list_a = songer_list.append
    cur.execute("SELECT GROUPE_NAME,REDIRECT,MN_1,MN_2,MN_3,MN_4,MN_5,MN_6,OVER_MN FROM PAIR_LIST WHERE GROUPE_NAME = '" + groupe_name.replace("'","''") +"'")
    k_gdata = cur.fetchone()
    while k_gdata[1]!=None:#リダイレクトがあればなくなるまで処理続行
        cur.execute("SELECT GROUPE_NAME,REDIRECT,MN_1,MN_2,MN_3,MN_4,MN_5,MN_6,OVER_MN FROM PAIR_LIST WHERE GROUPE_NAME = '" + k_gdata[1].replace("'","''") +"'")
        k_gdata = cur.fetchone()
    while True:
        for x in range(6):
            if k_gdata[x+2]!=None:
                songer_list_a(k_gdata[x+2])
            else:
                break
        if k_gdata[8]==None:
            break
        cur.execute("SELECT GROUPE_NAME,REDIRECT,MN_1,MN_2,MN_3,MN_4,MN_5,MN_6,OVER_MN FROM PAIR_LIST WHERE GROUPE_NAME = '" + k_gdata[8].replace("'","''") +"'")
        k_gdata = cur.fetchone()
    return songer_list

def add_music_data():
    cur.execute("select distinct music_name from video_id where music_name is not null and music_name not in (select key_music_name from MUSIC_SONG_DB where Key_music_name is not null)")
    k_rec_mlist = cur.fetchall()
    if len(k_rec_mlist)==0:
        return
    for x in range(len(k_rec_mlist)):
        nx = str(k_rec_mlist[x])[2:-3]
        n_music_reslist = md.search_music(nx)#検索
        cur.execute("INSERT INTO MUSIC_SONG_DB (KEY_MUSIC_NAME,MUSIC_NAME_SP,MUSIC_NAME_YT,ARTIST_NAME,SP_ID,YT_ID) VALUES('" + nx.replace("'","''") + "','" + n_music_reslist[0].replace("'","''") + "','" + n_music_reslist[1].replace("'","''") + "','" + n_music_reslist[2].replace("'","''") + "','" + n_music_reslist[3] + "','" + n_music_reslist[4] + "')")
    con.commit()

def true_check():
    _faul = 0
    #chidのニックネームの重複チェック
    cur.execute("select nick_name_1 from ch_id where NICK_NAME_1 is not null and ig = 0 group by nick_name_1 having COUNT(nick_name_1) > 1")
    nmlist_1 = cur.fetchall()
    for x in nmlist_1:
        print(str(x)[2:-3] + "\tは文字列が重複しています at CH_ID nick_name1")
    _faul += len(nmlist_1)
    cur.execute("select nick_name_2 from ch_id where NICK_NAME_2 is not null and ig = 0 group by nick_name_2 having COUNT(nick_name_2) > 1")
    nm_list_2 = cur.fetchall()
    for x in nm_list_2:
        print(str(x) + "\tは文字列が重複しています at CH_ID nick_name2")
    _faul += len(nm_list_2)
    cur.execute("select nick_name_1 from ch_id where nick_name_1 is not null and nick_name_1 in (select nick_name_2 from ch_id where nick_name_2 is not null) UNION select nick_name_2 from ch_id where nick_name_2 is not null and  nick_name_2 in (select nick_name_1 from ch_id where nick_name_1 is not null)")
    kb_nmlist = cur.fetchall()
    for x in kb_nmlist:
        print(str(x) + "\tは文字列が重複しています at CH_ID nick_name")
    _faul += len(kb_nmlist)
    cur.execute("select distinct groupe_name from video_id where not exists ( select GROUPE_NAME from PAIR_LIST_SECOND where video_id.GROUPE_NAME=PAIR_LIST_SECOND.groupe_name) and groupe_name is not null")
    n_glist = cur.fetchall()
    for x in n_glist:
        print(str(x)[2:-3] + "の情報がありません at pair_list_second.groupe_name")
    #pair_listの登録されていないニックネームを検出と同じグループ名内でのニックネームの重複チェック
    cur.execute("SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE IG = 0")
    groupe_list = cur.fetchall()
    cur.execute("select nick_name_1 from ch_id where nick_name_1 is not null union all select nick_name_2 from ch_id where nick_name_2 is not null")
    k_nlist = []
    k_nlist_a = k_nlist.append
    for t in cur.fetchall():
        k_nlist_a(str(t)[2:-3])
    s_nickname_list = set(k_nlist)
    for x in range(len(groupe_list)):
        n_glist = groupe_name2men_namev2(str(groupe_list[x])[2:-3])
        kari = [k for k, v in collections.Counter(n_glist).items() if v > 1]
        for x in range(len(kari)):#重複チェック
            _faul += 1
            print(str(kari[x]) + "\tは文字列が重複しています at pair_list")
        er = list(set(n_glist) - s_nickname_list)
        if len(er)!=0:#データベースに登録なし
            for r in range(len(er)):
                _faul += 1
                print(er[r] + "\tはデータベースに登録されていません at pair_list")
    #動画の投稿者が存在するか確認
    cur.execute("select distinct channel_id from VIDEO_ID vid where not exists ( select 1 from ch_id ch where vid.CHANNEL_ID = ch.ch_id ) and channel_id is not null")
    ch_list = cur.fetchall()
    for x in ch_list:
        print(str(x)[2:-3] + "\tの情報がデータベースにありません at ch_id ch_id")
    _faul += len(ch_list)
    #音楽データが存在するか検索
    cur.execute("SELECT DISTINCT MUSIC_NAME FROM VIDEO_ID vid where ig = 0 and not exists ( select 1 from MUSIC_SONG_DB md where vid.MUSIC_NAME = md.KEY_MUSIC_NAME) and MUSIC_NAME IS NOT NULL")
    m_name = cur.fetchall()
    for x in m_name:
        print(str(x)[2:-3] + "\tの情報がデータベースにありません at music_db")
    _faul += len(m_name)
    #CHIDのLINK先が存在するか確認
    cur.execute("select distinct LINK from ch_id where link != CH_ID")
    link_er = cur.fetchall()
    for x in link_er:
        print(str(x)[2:-3] + "\tの情報がデータベースにありません at ch_id link")
    _faul += len(link_er)
    if _faul==0:
        print("すべてのチェックを通過しました。")
    else:
        print(str(_faul) + "件のエラーが発生しています")

def music_list(music_name):
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID WHERE MUSIC_NAME = '" + music_name.replace("'","''") + "' and ig = 0 ORDER BY UPLOAD_TIME DESC")#登校が新しい順に並び変え
    m_vid = cur.fetchall()
    mlist = []
    mlist_a = mlist.append
    for x in range(len(m_vid)):
        mlist_a(str(m_vid[x])[2:-3])
    return mlist

def oracle_time(datetime_obj):
    return str(datetime_obj.year) + "-" + str(datetime_obj.month) + "-" + str(datetime_obj.day) + " " + str(datetime_obj.hour) + ":" + str(datetime_obj.minute) + ":" + str(datetime_obj.second)

def nomsec_time(datetime_obj):
    return str(datetime_obj.year) + "-" + str(datetime_obj.month) + "-" + str(datetime_obj.day) + "T" + str(datetime_obj.hour) + ":" + str(datetime_obj.minute) + ":" + str(datetime_obj.second) + "+09:00"

def search_musicdata(music_name):
    cur.execute("SELECT KEY_MUSIC_NAME,ARTIST_NAME,SP_ID,YT_ID,CLEATE_PAGE_DATE FROM MUSIC_SONG_DB msd WHERE KEY_MUSIC_NAME = '" + music_name.replace("'","''") + "'")
    s_music_data = list(cur.fetchone())
    if s_music_data[4]==None:
        nowdate = datetime.datetime.now()
        cur.execute("UPDATE MUSIC_SONG_DB SET CLEATE_PAGE_DATE = '" + oracle_time(nowdate) + "' where KEY_MUSIC_NAME = '" + music_name.replace("'","''") + "'")
        con.commit()
        s_music_data[4] = nomsec_time(nowdate)
    else:
        s_music_data[4] = nomsec_time(s_music_data[4])
    return s_music_data

def search_chdata(nick_name):
    nick_name = nick_name.replace("'","''")
    cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,NICK_NAME_2 FROM CH_ID WHERE NICK_NAME_1 ='" + nick_name + "' OR NICK_NAME_2 = '" + nick_name + "'")
    ch_data = list(cur.fetchone())
    if ch_data[1]==None and ch_data[4]!=None:
        ch_data[1] = ch_data[4]
    elif ch_data[1]==None and ch_data[4]==None:
        ch_data[1] = "er"
    return ch_data

def search_chdata_list(nick_name_list):
    pnick_name_list = str(nick_name_list).replace("[","").replace("]","")
    cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,NICK_NAME_2 FROM CH_ID WHERE (NICK_NAME_1 in (" + pnick_name_list + ") OR NICK_NAME_2 in (" + pnick_name_list + ")) and ig = 0")
    ch_dlist = []
    kvar = 0
    for y in cur.fetchall():
        ch_dlist.append(list(y))
        if ch_dlist[kvar][4]==None:
            if ch_dlist[kvar][1]==None:
                ch_dlist[kvar][1] = "er"
        elif ch_dlist[kvar][1]==None:
            ch_dlist[kvar][1] = ch_dlist[kvar][4]
        kvar += 1
    return ch_dlist

def search_chdata_list_bf(nick_name_list):
    pnick_name_list = str(nick_name_list).replace("[","").replace("]","")
    cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,BELONG_OFFICE FROM CH_ID WHERE (NICK_NAME_1 in (" + pnick_name_list + ") OR NICK_NAME_2 in (" + pnick_name_list + ")) and ig = 0")
    ch_dlist = []
    kvar = 0
    for y in cur.fetchall():
        ch_dlist.append(list(y))
        if ch_dlist[kvar][4]==None:
            if ch_dlist[kvar][1]==None:
                ch_dlist[kvar][1] = "er"
        elif ch_dlist[kvar][1]==None:
            ch_dlist[kvar][1] = ch_dlist[kvar][4]
        kvar += 1
    return ch_dlist

def video_name_db(video_id):
    cur.execute("SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID='" + video_id + "'")
    return cur.fetchone()

def youtube_embedded(video_id):
    return '<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/' + video_id + '" title="YouTube video player" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'

def look_up_v_history(video_id,scope=7):#scopeでデータ取得　jstタイムゾーンがJSTなことを確認!!
    cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'),VIEW_C,LIKE_C,COMMENT_C FROM VIDEO_V_DATA WHERE VIDEO_ID = '" + video_id + "' and RELOAD_TIME >= (current_date - " + str(scope) + ") ORDER BY RELOAD_TIME ASC")
    return cur.fetchall()

def view_music_graph(music_name,scope=7):
    music_name = music_name.replace("'","''")
    cur.execute("select TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'),sum(view_c),sum(LIKE_C),sum(COMMENT_C) from VIDEO_V_DATA where VIDEO_ID in (select VIDEO_ID from VIDEO_ID where MUSIC_NAME='" + music_name + "') and RELOAD_TIME >= (current_date - " + str(scope) + ") group by RELOAD_TIME order by RELOAD_TIME asc")
    mgd = cur.fetchall()
    label = []
    data_v = []
    data_l = []
    data_c = []
    for x in range(len(mgd)):
        label.append(mgd[x][0])
        data_v.append(mgd[x][1])
        data_l.append(mgd[x][2])
        data_c.append(mgd[x][3])
    html_data = "<canvas id='sum-yt' class='yt-view-sum inline'></canvas><script>Chart_cleater_v2('sum-yt'," + str(label) + "," + str(data_v) + "," + str(data_l) + "," + str(data_c) + ");</script>"
    return html_data

def view_graph(video_id,scope=7,dt=0):
    v_his = look_up_v_history(video_id,scope)
    label = []
    w_data = []
    label_a = label.append
    w_data_a = w_data.append
    for x in range(len(v_his)):
        label_a(v_his[x][0])
        w_data_a(v_his[x][1])
    if dt==0:
        html_data = "<canvas id='" + video_id + "' class='yt-view_graph'></canvas><script>Chart_cleater('" + video_id + "'," + str(label) + "," + str(w_data) + ")</script>"
        return html_data
    elif dt==1:
        html_data = "<canvas id='" + video_id + "' class='yt-view_graph'></canvas>"
        script = "<script>dt('" + video_id + "');Chart_cleater('" + video_id + "'," + str(label) + "," + str(w_data) + ");</script>"
        return html_data,script
    elif dt==2:
        html_data = "<canvas id='" + video_id + "' class='yt-view_graph'></canvas>"
        script = [video_id,label,w_data]
        return html_data,script

def make_music_page(music_name):
    n_html_path = "public/" + siteurl + "/music/" + music_name.replace("?","").replace(":","").replace("/","") + "/"
    if os.path.isdir(n_html_path)==False:
        os.mkdir(n_html_path)
    html_body_data = []
    html_body_data_a = html_body_data.append
    html_body_data_a(header)
    music_data = search_musicdata(music_name)
    if music_data[1]==None:#アーティスト名がなければ適当に置き換え
        music_data[1] = "Not Found"
    #jsライブラリ及びそれに付随するCSSを追加
    html_body_data_a('<script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script><script src="https://cdn.jsdelivr.net/npm/lite-youtube-embed@0.2.0/src/lite-yt-embed.min.js"></script><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lite-youtube-embed@0.2.0/src/lite-yt-embed.min.css">')
    #カスタムCSSを追加
    html_body_data_a("<style>.recommend-ch{width:120px;height:120px;aspect-ratio:1/1}.other_music{font-size:25px;text-align:center}.ofoverflow{width:120px;overflow:hidden;white-space:nowrap;text-overflow:clip;display:inline-block}:root{--main-text:#3f4551;--main-bg:#fffffd}@media (prefers-color-scheme:dark){:root{--main-text:silver;--main-bg:#2f3136;color-scheme:dark}}body{color:var(--main-text);background-color:var(--main-bg);font-family:'Meiryo',sans-serif}#video_data_t td{min-width:500px;min-height:300px}.v_face{max-height:75px;max-width:75px;aspect-ratio:1/1;border-radius:50%}.vtuber_sing,#music_recommend,#ch_recommend{overflow-x:auto;display:flex}a{color:#8aa2d3}.table-line{border-collapse:collapse}.yt-meta{max-width:500px}.music_title{font-size:20px;text-align:center}.yt-view_graph{max-width:500px;max-height:250px}.yt-view-sum{max-width:500px;max-height:250px;width:490px}.for_center{margin-left:calc(48vw - 500px);margin-right:calc(48vw - 500px)}h1{text-align:center}.inline{margin-left:auto;margin-right:auto}@media screen and (max-width:1000px){.yt-meta{min-width:75px!important;max-width:calc(97vw - 500px)!important}.yt-view_graph{max-width:calc(98vw - 500px)}.for_center{margin-left:auto!important;margin-right:auto!important}}@media screen and (max-width:600px){#video_data_t td{padding:4px 12px;display:block;min-width:90vw;max-width:90vw;min-height:auto}.yt-meta{max-width:90vw!important}.yt-view_graph{max-width:none!important}.yt-view-sum{width:100%}}</style>")
    #chart.jsのラッパーおよび削除くんを作成
    html_body_data_a("<script>function Chart_cleater(video_id,label_d,dataset_v){new Chart(document.getElementById(video_id),{type:'line',data:{labels:label_d,datasets:[{label:'視聴回数',backgroundColor:'rgb(255, 99, 132)',borderColor:'rgb(255, 99, 132)',data:dataset_v}]},option:{responsive:!0,animation:false}})}if(window.matchMedia('(prefers-color-scheme: dark)').matches===!0){Chart.defaults.color='#c0c0c0'}else{Chart.defaults.color='#3f4551'}function dt(video_id){if(window.matchMedia('(min-width:768px)').matches){document.getElementById(video_id+'_td').innerHTML=document.getElementById(video_id+'_dt').innerHTML}};function Chart_cleater_v2(id_c,label,vc,lc,cc){new Chart(document.getElementById(id_c),{type:'line',data:{labels:label,datasets:[{label:'視聴回数',data:vc,borderColor:'rgb(255, 99, 132)',backgroundColor:'rgb(255, 99, 132)',},{label:'高評価数',data:lc,hidden:!0,borderColor:'rgb(58,180,139)',backgroundColor:'rgb(58,180,139)',},{label:'コメント数',data:cc,hidden:!0,borderColor:'rgb(137, 195, 235)',backgroundColor:'rgb(137, 195, 235)',}]},options:{animation:!1,responsive:!0}})}</script>")
    #音楽データの表を作成
    html_body_data_a('<main><div class="for_center">')
    if music_data[2] and music_data[3]!=None:#spotifyもyoutubeも存在する場合
        html_body_data_a("<h1>" + music_data[0] + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/watch?v=" + music_data[3] + "'>YoutubeMusicで聞く</a></td></tr><tr><td><p>" + music_data[0] + "</p></td><td><p>" + music_data[1] + """</p><td><div id="spotify-embed"></div><script>spotify_id='""" + music_data[2] + """';if(window.matchMedia('(prefers-color-scheme: dark)').matches == true){document.getElementById("spotify-embed").innerHTML='<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/' + spotify_id + '?theme=0" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>';}else{document.getElementById("spotify-embed").innerHTML='<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/' + spotify_id + '" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>';}</script></td></tr></table>""")
    elif music_data[2]==None and music_data[3]!=None:#spotifyにはないがyoutubeにはある場合
        html_body_data_a("<h1>" + music_data[0] + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/watch?v=" + music_data[3] + "'>YoutubeMusicで聞く</a></td></tr><tr><td><p>" + music_data[0] + "</p></td><td><p>" + music_data[1] + "</p><td><a href='https://open.spotify.com/search/" + urllib.parse.quote(music_data[0]) + "'>spotifyで検索(DBに登録されていません)</a></td></tr></table>")
    elif music_data[2]!=None and music_data[3]==None:#spotifyにありyoutubeにないパターン
        html_body_data_a("<h1>" + music_data[0] + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/search?q=" + music_data[0] + "'>YoutubeMusicで検索(DBにデータがありません)</a></td></tr><tr><td><p>" + music_data[0] + "</p></td><td><p>" + music_data[1] + """</p><td><div id="spotify-embed"></div><script>spotify_id='""" + music_data[2] + """';if(window.matchMedia('(prefers-color-scheme: dark)').matches == true){document.getElementById("spotify-embed").innerHTML='<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/' + spotify_id + '?theme=0" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>';}else{document.getElementById("spotify-embed").innerHTML='<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/' + spotify_id + '" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>';}</script></td></tr></table>""")
    else:#spotifyにもyoutubeにもないパターン
        html_body_data_a("<h1>" + music_data[0] + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/search?q=" + music_data[0] + "'>YoutubeMusicで検索(DBにデータがありません)</a></td></tr><tr><td><p>" + music_data[0] + "</p></td><td><p>" + music_data[1] + "</p><td><a href='https://open.spotify.com/search/" + urllib.parse.quote(music_data[0]) + "'>spotifyで検索(DBに登録されていません)</a></td></tr></table>")
    html_body_data_a(view_music_graph(music_name))
    music_videos_id = music_list(music_name)
    v_data = []
    for x in range(len(music_videos_id)):
        v_data.append(video2data_v2(music_videos_id[x]))
    html_body_data_a("<table id='video_data_t'><tbody id='video_data_tbody'>")
    overflow_ajax = {}
    numbering = 0
    for x in range(len(v_data)):
        if x >= 10:#数が増えたとき用10以上になるとAJAX方式に変更
            tmp_datalist = []
            html_body_data_a = tmp_datalist.append
            can_d,sclist = view_graph(video_id=v_data[x][0],dt=2)
            html_body_data_a("<td><lite-youtube videoid='" + v_data[x][0] + "' playlabel='Play'></lite-youtube></td><td class='yt-meta' id='" + v_data[x][0] + "_td'><details id='" + v_data[x][0] + "_dt'><summary class='music_title'>" + v_data[x][4][2] + "</summary>" + can_d)
        else:
            can_d,sc = view_graph(video_id=v_data[x][0],dt=1)
            html_body_data_a("<tr><td><lite-youtube videoid='" + v_data[x][0] + "' playlabel='Play'></lite-youtube></td><td class='yt-meta' id='" + v_data[x][0] + "_td'><details id='" + v_data[x][0] + "_dt'><summary class='music_title'>" + v_data[x][4][2] + "</summary>" + can_d)
        html_body_data_a("<a href='https://vsong.fans/video_data/" + v_data[x][0] + ".html'>詳細データ</a><div class='vtuber_sing'>")
        if v_data[x][2]==1:#歌い手が１人
            if "https://yt" in v_data[x][3][3]:#画像ソースがyoutubeの場合
                html_body_data_a("<a href='/ch/" + v_data[x][3][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][3] + "=s75-c-k-c0x00ffffff-no-rj' alt='" + v_data[x][3][0] + "' title='" + v_data[x][3][0] + "'></a>")
            else:
                html_body_data_a("<a href='/ch/" + v_data[x][3][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][3] + "' alt='" + v_data[x][3][0] + "' title='" + v_data[x][3][0] + "'></a>")
        else:#歌い手が複数人
            for r in range(v_data[x][2]):
                    if "https://yt" in v_data[x][3][r][3]:#画像ソースがyoutubeの場合
                        html_body_data_a("<a href='/ch/" + v_data[x][3][r][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][r][3] + "=s75-c-k-c0x00ffffff-no-rj' alt='" + v_data[x][3][r][0] + "' title='" + v_data[x][3][r][0] + "'></a>")
                    elif "https://pbs.twimg.com" in v_data[x][3][r][3]:#画像ソースがtwitter
                        html_body_data_a("<a href='/ch/" + v_data[x][3][r][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + str(v_data[x][3][r][3])[:-11] + '200x200' + str(v_data[x][3][r][3])[-4:] + "' alt='" + v_data[x][3][r][0] + "' title='" + v_data[x][3][r][0] + "'></a>")
                    else:
                        html_body_data_a("<a href='/ch/" + v_data[x][3][r][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][r][3] + "' alt='" + v_data[x][3][r][0] + "' title='" + v_data[x][3][r][0] + "'></a>")
        if x >= 10:
            html_body_data_a("</div></details></td>")
            kdict = {"mainc":"".join(tmp_datalist),"fnc":sclist}
            overflow_ajax[str(x)[-1]] = kdict
            tmp_datalist = []#処理が終わったら一時データリストを初期化
        else:
            html_body_data_a(sc + "</div></details></td></tr>")
        if x>=10 and len(v_data)-1==x or x in range(20,1000,10):#10以上かつ最後か20以上の10のときにAJAX用ファイルを生成
            if os.path.isdir(n_html_path + "ajax/")==False:#フォルダがなければ生成
                os.mkdir(n_html_path + "ajax/")
            with open(n_html_path + "ajax/tbdata-" + str(numbering) + ".json","w") as f:
                json.dump(overflow_ajax,f,indent=4)
            numbering += 1
            overflow_ajax = {}
    html_body_data_a = html_body_data.append#変更している場合があるのでこのタイミングで元に戻す
    html_body_data_a("""</tbody></table></div><div id="descm"></div><div id="music_recommend"></div><div id="descc"></div><div id="ch_recommend"></div></main>""")
    html_body_data_a("""<script>var numbaring=0;var load_max=0;const html=document.querySelector('html');function scroll_ev(){const currentPos=window.pageYOffset;var bottomPoint=document.body.clientHeight-window.innerHeight-600;if(bottomPoint<=currentPos){let request=new XMLHttpRequest();request.open("GET","ajax/tbdata-"+String(numbaring)+".json");numbaring+=1;request.responseType='json';request.send();request.onload=function(){const res=request.response;for(let i=0;i<10;i++){try{let now_tr=document.createElement("tr");now_tr.innerHTML=res[i].mainc;now_tr.className=res[i].forclass;document.getElementById('video_data_tbody').appendChild(now_tr);dt(res[i].fnc[0]);Chart_cleater(res[i].fnc[0],res[i].fnc[1],res[i].fnc[2]);if(i>8){break}}catch{window.removeEventListener('scroll',scroll_ev);if(load_max<1){load_max++;now_ran=Math.floor(Math.random()*100);let request_mr=new XMLHttpRequest();request_mr.open("GET","/ajax/music/mr-"+String(now_ran)+".json");request_mr.responseType='json';request_mr.send();request_mr.onload=function(){const res_mr=request_mr.response;let divm=document.getElementById('music_recommend');document.getElementById('descm').innerHTML='<hr><p class="other_music">他のおすすめの曲</p>';for(let i=0;i<20;i++){divm.innerHTML =  divm.innerHTML + "<a href='/music/" + res_mr[i][0] + "/'>" + res_mr[i][0] + "<img src='https://i.ytimg.com/vi/" + res_mr[i][1] + "/mqdefault.jpg' alt='" + res_mr[i][0] + "'></a>"}}; let request_cr=new XMLHttpRequest();request_cr.open("GET","/ajax/ch/cr-"+String(now_ran)+".json");request_cr.responseType='json';request_cr.send();request_cr.onload=function(){const res_cr=request_cr.response;let divc=document.getElementById('ch_recommend');document.getElementById('descc').innerHTML='<hr><p class="other_music">他のおすすめのVtuber</p>';for(let i=0;i<20;i++){divc.innerHTML=divc.innerHTML+"<a href='/ch/"+res_cr[i][0]+"/'><span class='ofoverflow'>"+res_cr[i][0]+"</span><img class='recommend-ch' src='"+res_cr[i][1]+"' alt='"+res_cr[i][0]+"' title='"+res_cr[i][0]+"'></a>"}}}}}}}}window.addEventListener('scroll',scroll_ev);scroll_ev()</script>""")
    description = "Vtuberの" + music_name + "の歌ってみた動画をまとめたサイトです。たくさんのvtuberの歌ってみた動画のランキングのサイトです。皆様に沢山のvtuberを知ってもらいたく運営しています。"
    page_title = "Vtuberの歌う" + music_name
    head_data = '<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/music/" + music_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + music_data[4] + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '"></head>'
    html_body_data.insert(0,head_data)
    with open(n_html_path + "index.html","wb") as f:
        f.write("".join(html_body_data).encode("utf-8"))#windows対策

#make_music_page("フォニイ")

def make_all_musicpage():
    cur.execute("SELECT KEY_MUSIC_NAME FROM MUSIC_SONG_DB")
    for x in cur.fetchall():
        make_music_page(str(x)[2:-3])

def reloadpeople_picture():
    #youtubeの場合
    cur.execute("SELECT CH_ID FROM CH_ID WHERE CH_ID is not null and ig = 0")
    chid_list = []
    chid_list_a = chid_list.append
    for x in cur.fetchall():
        chid_list_a(str(x)[2:-3])
    ch_data = gy.ExtremeChidToInfo(chid_list)
    for x in ch_data:
        cur.execute("UPDATE CH_ID SET PICTURE_URL='" + x[2] + "' WHERE CH_ID = '" + x[0] + "'")
    con.commit()
    #twitterの場合
    cur.execute("select distinct twitter_name from ch_id where TWITTER_NAME is not null")
    k_tnlist = cur.fetchall()
    tnlist = [str(i)[2:-3] for i in k_tnlist]
    n_n = math.ceil(float(len(tnlist)/100))
    header_tw = {"Authorization":"Bearer " + ev.tw_apikey}
    for r in range(n_n):
        if n_n==r+1:#最後
            n_length = len(tnlist) - (100*r)
        else:
            n_length = 100
        n_tster = []
        n_tster_a = n_tster.append
        for e in range(n_length):
            n_tster_a(tnlist[e+100*r])
        tster = str(n_tster).replace("'","").replace(" ","").replace("[","").replace("]","")
        jsong = requests.get("https://api.twitter.com/2/users/by?user.fields=profile_image_url&usernames=" + tster,headers=header_tw)
        new_json = jsong.json()
        for i in range(n_length):
            cur.execute("update CH_ID set PICTURE_URL='" + new_json["data"][i]["profile_image_url"].replace("normal","400x400") + "' where TWITTER_NAME='" + new_json["data"][i]["username"] + "'")
    con.commit()

def get_ch_vdata(nickname):
    chdata = search_chdata(nickname)
    if chdata[5]!=None:
        nclist = [str(chdata[0]).replace("'","''"),str(chdata[5]).replace("'","''")]
    else:
        nclist = [str(chdata[0]).replace("'","''")]
    menlist = str(nclist).replace("[","").replace("]","")
    menlist = "(" + menlist + ")"
    cur.execute("select video_id from video_id where video_id in (select video_id from video_id where IG = 0 AND CHANNEL_ID = '" + chdata[1] + "' UNION ALL SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 0 AND GROUPE_NAME in (SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 in " + menlist + " OR MN_2 in " + menlist + "OR MN_3 in " + menlist + "OR MN_4 in " + menlist + "OR MN_5 in " + menlist + "OR MN_6 in " + menlist + "OR MN_7 in " + menlist + "OR MN_8 in " + menlist + "OR MN_9 in " + menlist + "OR MN_10 in " + menlist + "OR MN_11 in " + menlist + "OR MN_12 in " + menlist + "OR MN_13 in " + menlist + "OR MN_14 in " + menlist + "OR MN_15 in " + menlist + "OR MN_16 in " + menlist + "OR MN_17 in " + menlist + "OR MN_18 in " + menlist + "OR MN_19 in " + menlist + "OR MN_20 in " + menlist + "OR MN_21 in " + menlist + "OR MN_22 in " + menlist + "OR MN_23 in " + menlist + "OR MN_24 in " + menlist + "OR MN_25 in " + menlist + "OR MN_26 in " + menlist + "OR MN_27 in " + menlist + "OR MN_28 in " + menlist + "OR MN_29 in " + menlist + "OR MN_30 in " + menlist + "OR MN_31 in " + menlist + "OR MN_32 in " + menlist + "OR MN_33 in " + menlist + "OR MN_34 in " + menlist + "OR MN_35 in " + menlist + "OR MN_36 in " + menlist + "OR MN_37 in " + menlist + "OR MN_38 in " + menlist + "OR MN_39 in " + menlist + ") UNION ALL select video_id from video_id where channel_id in (select CH_ID from CH_ID where LINK='" + chdata[1] + "')) and music_name is not null ORDER BY UPLOAD_TIME DESC")
    vidlist = cur.fetchall()
    vdata = []
    vdata_a = vdata.append
    for n in vidlist:
        vdata_a(video2data_v2(str(n)[2:-3]))
    cur.execute("select CLEATE_PAGE_DATE from ch_id where NICK_NAME_1 in ('" + nickname + "')")
    t_page_d = cur.fetchone()
    if t_page_d[0]==None:
        nowdate = datetime.datetime.now()
        cur.execute("UPDATE CH_ID SET CLEATE_PAGE_DATE = '" + oracle_time(nowdate) + "' where NICK_NAME_1 = '" + nickname.replace("'","''") + "'")
        con.commit()
        t_page_d = nomsec_time(nowdate)
    else:
        t_page_d = nomsec_time(t_page_d[0])
    return vdata,t_page_d

def make_channel_page(nick_name):#チャンネルのページを作成
    site_nick_name = nick_name.replace("?","").replace(":","").replace("/","")
    n_html_path = "public/" + siteurl + "/ch/" + site_nick_name + "/"
    if os.path.isdir(n_html_path)==False:#フォルダがなければ生成
        os.mkdir(n_html_path)
    html_body_data = []
    html_body_data_a = html_body_data.append
    html_body_data_a(header)
    #jsライブラリ及びそれに付随するCSSを追加
    html_body_data_a('<script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script><script src="https://cdn.jsdelivr.net/npm/lite-youtube-embed@0.2.0/src/lite-yt-embed.min.js"></script><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lite-youtube-embed@0.2.0/src/lite-yt-embed.min.css">')
    #カスタムCSSを追加
    html_body_data_a("<style>.other_music{font-size:25px;text-align:center}.ofoverflow{width:120px;overflow:hidden;white-space:nowrap;text-overflow:clip;display:inline-block}h1{text-align:center;font-size:30px}:root{--main-text:#3f4551;--main-bg:#fffffd}@media (prefers-color-scheme:dark){:root{--main-text:silver;--main-bg:#2f3136;color-scheme:dark}}body{color:var(--main-text);background-color:var(--main-bg);font-family:'Meiryo',sans-serif}#video_data_t td{min-width:500px;min-height:300px}.v_face{max-height:75px;max-width:75px;aspect-ratio:1/1;border-radius:50%}.vtuber_sing,#music_recommend,#ch_recommend{overflow-x:auto;display:flex}.recommend-ch{width:120px;height:120px;aspect-ratio:1/1}a{color:#8aa2d3}.table-line{border-collapse:collapse}.yt-meta{max-width:500px}.music_title{font-size:20px;text-align:center}.yt-view_graph{max-width:500px;max-height:250px}h1{text-align:center}.for_center{margin-left:calc(48vw - 500px);margin-right:calc(48vw - 500px)}@media screen and (max-width:1000px){.yt-meta{min-width:75px!important;max-width:calc(97vw - 500px)!important}.yt-view_graph{max-width:calc(98vw - 500px)}.for_center{margin-left:auto!important;margin-right:auto!important}}@media screen and (max-width:600px){#video_data_t td{padding:4px 12px;display:block;min-width:90vw;max-width:90vw;min-height:auto}.yt-meta{max-width:90vw!important}.yt-view_graph{max-width:none!important}}</style>")
    #chart.jsのラッパーおよび削除くんを作成
    html_body_data_a("<script>function Chart_cleater(video_id,label_d,dataset_v){new Chart(document.getElementById(video_id),{type:'line',data:{labels:label_d,datasets:[{label:'視聴回数',backgroundColor:'rgb(255, 99, 132)',borderColor:'rgb(255, 99, 132)',data:dataset_v}]},options:{animation:!1,responsive:!0}})} if(window.matchMedia('(prefers-color-scheme: dark)').matches===!0){Chart.defaults.color='#c0c0c0'}else{Chart.defaults.color='#3f4551'} function dt(video_id){if(window.matchMedia('(min-width:768px)').matches){document.getElementById(video_id+'_td').innerHTML=document.getElementById(video_id+'_dt').innerHTML}}</script>")
    v_data,page_fc_date = get_ch_vdata(nick_name)
    html_body_data_a('<main><div class="for_center">')
    html_body_data_a("<h1>" + nick_name + "</h1>")
    html_body_data_a("<table id='video_data_t'><tbody id='video_data_tbody'>")
    overflow_ajax = {}
    numbering = 0
    numbering_b = 0
    for x in range(len(v_data)):
        men_of_list = []
        if v_data[x][2]==1:#歌い手が１人
            if v_data[x][3][5]==None:
                v_data[x][3][5] = "個人"
            men_of_list = [str(v_data[x][3][0]).replace(" ",""),v_data[x][3][5]]
        else:
            for w in range(v_data[x][2]):
                if v_data[x][3][w][0] not in men_of_list:
                    men_of_list.append(str(v_data[x][3][w][0]).replace(" ",""))
                if v_data[x][3][w][5]==None:
                    v_data[x][3][w][5] = "個人"
                if v_data[x][3][w][5] not in men_of_list:
                    men_of_list.append(v_data[x][3][w][5])
        if x >= 10:#数が増えたとき用10以上になるとAJAX方式に変更
            tmp_datalist = []
            html_body_data_a = tmp_datalist.append
            can_d,sclist = view_graph(video_id=v_data[x][0],dt=2)
            html_body_data_a("<td><lite-youtube videoid='" + v_data[x][0] + "' playlabel='Play'></lite-youtube></td><td class='yt-meta' id='" + v_data[x][0] + "_td'><details id='" + v_data[x][0] + "_dt'><summary class='music_title'>" + v_data[x][1][0] + "</summary>" + can_d)
        else:
            can_d,sc = view_graph(video_id=v_data[x][0],dt=1)
            html_body_data_a("<tr class='" + " ".join(men_of_list) + "'><td><lite-youtube videoid='" + v_data[x][0] + "' playlabel='Play'></lite-youtube></td><td class='yt-meta' id='" + v_data[x][0] + "_td'><details id='" + v_data[x][0] + "_dt'><summary class='music_title'>" + v_data[x][1][0] + "</summary>" + can_d)
        html_body_data_a("<a href='https://vsong.fans/video_data/" + v_data[x][0] + ".html'>詳細データ</a><div class='vtuber_sing'>")
        if v_data[x][2]==1:#歌い手が１人
            if "https://yt" in v_data[x][3][3]:#画像ソースがyoutubeの場合
                html_body_data_a("<a href='/ch/" + v_data[x][3][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][3] + "=s75-c-k-c0x00ffffff-no-rj' alt='" + v_data[x][3][0] + "' title='" + v_data[x][3][0] + "'></a>")
            else:
                html_body_data_a("<a href='/ch/" + v_data[x][3][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][3] + "' alt='" + v_data[x][3][0] + "' title='" + v_data[x][3][0] + "'></a>")
        else:#歌い手が複数人
            for r in range(v_data[x][2]):
                if "https://yt" in v_data[x][3][r][3]:#画像ソースがyoutubeの場合
                    html_body_data_a("<a href='/ch/" + v_data[x][3][r][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][r][3] + "=s75-c-k-c0x00ffffff-no-rj' alt='" + v_data[x][3][r][0] + "' title='" + v_data[x][3][r][0] + "'></a>")
                elif "https://pbs.twimg.com" in v_data[x][3][r][3]:#画像ソースがtwitter
                    html_body_data_a("<a href='/ch/" + v_data[x][3][r][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + str(v_data[x][3][r][3])[:-11] + '200x200' + str(v_data[x][3][r][3])[-4:] + "' alt='" + v_data[x][3][r][0] + "' title='" + v_data[x][3][r][0] + "'></a>")
                else:
                    html_body_data_a("<a href='/ch/" + v_data[x][3][r][0] + "'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][r][3] + "' alt='" + v_data[x][3][r][0] + "' title='" + v_data[x][3][r][0] + "'></a>")
        if x >= 10:
            html_body_data_a("</div></details></td>")
            kdict = {"mainc":"".join(tmp_datalist),"fnc":sclist,"forclass":" ".join(men_of_list)}
            overflow_ajax[int(str(x)[-1])] = kdict
            tmp_datalist = []#処理が終わったら一時データリストを初期化
        else:
            html_body_data_a(sc + "</div></details></td></tr>")
        if x in range(10,1000,10):
            html_body_data.append("</tbody><tbody id='tbd-" + str(numbering_b) + "'>")
            numbering_b += 1
        if x>=10 and len(v_data)-1==x or x in range(20,1000,10):#10以上かつ最後か20以上の10のときにAJAX用ファイルを生成
            if os.path.isdir(n_html_path + "ajax/")==False:#フォルダがなければ生成
                os.mkdir(n_html_path + "ajax/")
            overflow_ajax["now_c"] = numbering
            with open(n_html_path + "ajax/tbdata-" + str(numbering) + ".json","w") as f:
                json.dump(overflow_ajax,f,indent=4)
            numbering += 1
            overflow_ajax = {}
    html_body_data_a = html_body_data.append#変更している場合があるのでこのタイミングで元に戻す
    html_body_data_a("""</tbody></table></div><div id="descm"></div><div id="music_recommend"></div><div id="descc"></div><div id="ch_recommend"></div></main>""")
    html_body_data_a("<script>var max_len=" + str(numbering) + """;var numbaring=0;var load_max=0;var su_numb=0;const html=document.querySelector("html");function scroll_do(){if(numbaring<max_len){document.head.insertAdjacentHTML('beforeEnd','<link rel="preload" href="ajax/tbdata-'+String(numbaring+1)+'.json">');let request=new XMLHttpRequest();request.open("GET","ajax/tbdata-"+String(numbaring)+".json");numbaring++;request.responseType="json";request.send();request.onload=function(){const res=request.response;let url_parm=new URL(window.location.href).searchParams;if(url_parm.get('ran')==null){history.replaceState(null,null,"?tbdid="+String(su_numb))} su_numb++;for(let i=0;i<10;i++){try{let now_tr=document.createElement("tr");now_tr.innerHTML=res[i].mainc;now_tr.className=res[i].forclass;document.getElementById("tbd-"+String(res.now_c)).appendChild(now_tr);dt(res[i].fnc[0]);Chart_cleater(res[i].fnc[0],res[i].fnc[1],res[i].fnc[2])}catch{window.removeEventListener("scroll",scroll_ev);if(load_max==0){load_max++;let url_parm=new URL(window.location.href).searchParams;if(url_parm.get('ran')!=null){now_ran=url_parm.get('ran')}else{now_ran=Math.floor(Math.random()*100);history.replaceState(null,null,"?ran="+String(now_ran))} let request_mr=new XMLHttpRequest();request_mr.open("GET","/ajax/music/mr-"+String(now_ran)+".json");request_mr.responseType="json";request_mr.send();request_mr.onload=function(){const res_mr=request_mr.response;let divm=document.getElementById("music_recommend");document.getElementById("descm").innerHTML='<hr><p class="other_music">他のおすすめの曲</p>';for(let i=0;i<20;i++){divm.innerHTML=divm.innerHTML+"<a href='/music/"+res_mr[i][0]+"/'>"+res_mr[i][0]+"<img src='https://i.ytimg.com/vi/"+res_mr[i][1]+"/mqdefault.jpg' alt='"+res_mr[i][0]+"'></a>"}};let request_cr=new XMLHttpRequest();request_cr.open("GET","/ajax/ch/cr-"+String(now_ran)+".json");request_cr.responseType="json";request_cr.send();request_cr.onload=function(){const res_cr=request_cr.response;let divc=document.getElementById("ch_recommend");document.getElementById("descc").innerHTML='<hr><p class="other_music">他のおすすめのVtuber</p>';for(let i=0;i<20;i++){divc.innerHTML=divc.innerHTML+"<a href='/ch/"+res_cr[i][0]+"/'><span class='ofoverflow'>"+res_cr[i][0]+"</span><img class='recommend-ch' src='"+res_cr[i][1]+"' alt='"+res_cr[i][0]+"' title='"+res_cr[i][0]+"'></a>"}}}}}}}} function scroll_ev(){const currentPos=window.pageYOffset;var bottomPoint=document.body.clientHeight-window.innerHeight-600;if(bottomPoint<=currentPos){scroll_do()}} window.addEventListener("scroll",scroll_ev);scroll_ev();let url_parm=new URL(window.location.href).searchParams;if(url_parm.get('ran')!=null){for(let step=0;step<20;step++){scroll_do()}} if(url_parm.get('tbdid')!=null){for(let step=0;step<1+Number(url_parm.get('tbdid'));step++){scroll_do()}}</script>""")
    description = "Vtuberの" + nick_name + "が歌った歌ってみた及びオリジナル曲をまとめたサイトです。たくさんのvtuberの歌ってみた動画のランキングのサイトです。皆様に沢山のvtuberを知ってもらいたく運営しています。"
    page_title = nick_name + "の歌った曲集"
    head_data = '<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + site_nick_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + page_fc_date + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '"></head><body>'
    html_body_data.insert(0,head_data)
    html_body_data_a("""</body></html>""")
    with open(n_html_path + "index.html","wb") as f:
        f.write("".join(html_body_data).encode("utf-8"))#windows対策

#make_channel_page("ときのそら")

def make_all_chpage():
    cur.execute("select nick_name_1 from ch_id where ig = 0 and nick_name_1 is not null")
    chid_list = cur.fetchall()
    for i in chid_list:
        make_channel_page(str(i)[2:-3])

def music_recommend_page():
    ajax_path = "public/" + siteurl + "/ajax/music/"
    cur.execute("select KEY_MUSIC_NAME from MUSIC_SONG_DB")
    music_list = []
    music_list_a = music_list.append
    for x in cur.fetchall():
        music_list_a(str(x)[2:-3])
    len_mlist = len(music_list)
    for n in range(100):#おすすめを100件生成
        k_ranlist = []
        n_dict = {}
        while len(k_ranlist)<20:
            k = random.randint(0,len_mlist-1)
            if k not in k_ranlist:
                k_ranlist.append(k)
        for x in range(len(k_ranlist)):
            nmusic_name = music_list[k_ranlist[x]]
            cur.execute("select video_id from video_id where music_name = '" + nmusic_name.replace("'","''") + "' order by upload_time desc")
            n_vid = str(cur.fetchone())[2:-3]
            k_ar = [nmusic_name,n_vid]
            n_dict[x] = k_ar
        with open(ajax_path + "mr-" + str(n) + ".json","w") as f:
            json.dump(n_dict,f,indent=4)

def channel_recommend_page():
    ajax_path = "public/" + siteurl + "/ajax/ch/"
    cur.execute("select nick_name_1,picture_url from ch_id where ig = 0")
    ch_data_k = cur.fetchall()
    len_ch_data = len(ch_data_k)
    #chdataを加工
    ch_data = []
    ch_data_a = ch_data.append
    for r in ch_data_k:
        link = r[1]
        if "https://yt" in link:#youtube
            link = link + "=s120-c-k-c0x00ffffff-no-rj"
        elif "https://pbs.twimg.com" in link:#twitter
            link = link[:-11] + "200x200" + link[-4:]
        ch_data_a([r[0],link])
    for x in range(100):
        k_ranlist = []
        n_dict = {}
        while len(k_ranlist)<20:
            k = random.randint(0,len_ch_data-1)
            if k not in k_ranlist:
                k_ranlist.append(k)        
        for n in range(len(k_ranlist)):
            k_ar = [ch_data[k_ranlist[n]][0],ch_data[k_ranlist[n]][1]]
            n_dict[n] = k_ar
        with open(ajax_path + "cr-" + str(x) + ".json","w") as f:
            json.dump(n_dict,f,indent=4)
