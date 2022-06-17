import math,os,cx_Oracle,requests,datetime,collections,urllib.parse,json,random,copy,jaconv,shutil,itertools,MySQLdb,sys
from pykakasi import kakasi
import get_youtube_data as gy
import music_data as md
import ev
import xml.etree.ElementTree as ET

try:
    con_ms = MySQLdb.connect(host=ev.mysql_host,user=ev.mysql_user,passwd=ev.mysql_ps,db="vsong")
    cur_ms = con_ms.cursor()
except:
    print("エラー記録用データベース(mysql)に接続できませんでした")

try:#引数にあれば登録
    now_origin = sys.argv[1]
except:
    now_origin = "anynomous"

def oracle_time(datetime_obj):
    return str(datetime_obj.year) + "-" + str(datetime_obj.month) + "-" + str(datetime_obj.day) + " " + str(datetime_obj.hour) + ":" + str(datetime_obj.minute) + ":" + str(datetime_obj.second)

def sql_escape(nowst):
    nowst = str(nowst)
    return nowst.replace("'","''").replace('"','""')

def pro_log(lebel,fn_name,argv_data,erdesc,ermessage=""):
    if len(ermessage) > 2800:
        ermessage = ermessage[0:2800] + "\toverflow!"
    else:
        ermessage = sql_escape(ermessage)
    if ermessage=="":
        ermessage = None
    try:
        cur_ms.execute(f"INSERT INTO pro_er_log (log_date,log_author,log_origin,function_name,argv_data,er_name,label,er_message) VALUES ('{oracle_time(datetime.datetime.now())}','{now_origin}','program','{fn_name}','{argv_data}','{sql_escape(erdesc)}','{lebel}','{ermessage}')")
        con_ms.commit()
    except:
        print("unknown error log skipped on MySql error")
    if lebel=="error":
        print(f"{fn_name} エラー発生　{argv_data} 時 エラー状態 {erdesc}")

pro_log("log","mysql-login","","login success")

try:
    con = cx_Oracle.connect(ev.oracle_user, ev.oracle_ps, ev.oracle_connect_string)
    print("Database version:", con.version + "\tデータベースに正常に接続できました。")
    cur = con.cursor()
    cur.execute("alter session set nls_date_format='YYYY-MM-DD HH24:MI:SS'")
except:
    pro_log("error","oracle-login","","failed oracle login->stop program")
    sys.exit("failed oracle login")

#webサイト用変数設定
header = """<header><h2 class="Top"><a href="/" onClick='page_ajax_load("/");return false'>VtuberSing</a></h2><nav class="header-nav"><ul><li><a href="/search/" onClick='page_ajax_load("/search/");return false'>検索</a><li><a href="/today/" onClick='page_ajax_load("/today/");return false'>今日の人気</a></ul></nav></header>"""
music_control_html = """<div class="sticky_c_yt dis_none" id="ytembed"><div id="youtube-iframe"></div></div><span class="sticky_c dis_none" id="control_panel"><progress class="yt-progress" id="yt-player-time" max="100" value="0"></progress><div class="flex_box"><div class="beside_gr"><div class="beside_gr_in" id="music_name_display"></div></div><div class="play_center"><button id="yt-playbt" onclick="yt_playorstop()" class="bt_noborder" title="再生"><img class="control_icon" src="/util/playbtn.svg"></button><button onclick="yt_skip()" title="スキップ" class="bt_noborder"><img class="control_icon" src="/util/skipbt.svg"></button><input title="音量を調節" type="range" id="yt_sound_volume" min="0" max="100" value="100" onchange="yt_volume_change()"><button id="yt_display" onclick="yt_display()">表示</button><button id="yt_ch_dismode" onclick='yt_watchmode_ch()' title="大画面で表示" class="bt_noborder"><img class="control_icon" src="/util/bigwindow.svg"></button><input id="autoload_check" type="checkbox">"""
html_import_lib = '<link rel="stylesheet" href="/library/main.css"><script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script><script src="https://www.youtube-nocookie.com/s/player/7e5c03a3/www-widgetapi.vflset/www-widgetapi.js"></script><script defer src="https://cdn.jsdelivr.net/npm/instant.page@5.1.0/instantpage.min.js"></script>'
siteurl = ""
try:
    siteurl = ev.siteurl
except:
    siteurl = "vsong.fans"
folder_path = ""
try:
    folder_path = ev.folder_path
except:
    folder_path = "public/"
cgi_bin_dir = ""
try:
    cgi_bin_dir = ev.cgi_bin_path
except:
    cgi_bin_dir = "public/vsong.fans"
default_modify_time = "2022-5-31"

def cp_lib():#ライブラリのデータを配置
    shutil.copy2("jslibrary/main.js",folder_path + siteurl + "/library/main.js")
    shutil.copy2("jslibrary/main.css",folder_path + siteurl + "/library/main.css")
    shutil.copy2("jslibrary/search.cpp",cgi_bin_dir + "/cgi-bin/search.cpp")

def ps_lib():#ライブラリのデータを本番環境から移す
    shutil.copy2(folder_path + siteurl + "/library/main.js","jslibrary/main.js")
    shutil.copy2(folder_path + siteurl + "/library/main.css","jslibrary/main.css")
    shutil.copy2(folder_path + siteurl + "/cgi-bin/search.cpp","jslibrary/search.cpp")

def cp_htm():#basic_pageのデータを本番の場所にペースト
    shutil.copy2("basic_page/watch-index.html",folder_path + siteurl + "/watch/index.html")
    shutil.copy2("basic_page/search-index.html",folder_path + siteurl + "/search/index.html")
    shutil.copy2("basic_page/today-index.html",folder_path + siteurl + "/today/index.html")
    shutil.copy2("basic_page/toppage-index.html",folder_path + siteurl + "/index.html")
    shutil.copy2("basic_page/musictop-index.html",folder_path + siteurl + "/music/index.html")

def ps_htm():#本番環境からbasic_pageに配置
    shutil.copy2(folder_path + siteurl + "/watch/index.html","basic_page/watch-index.html")
    shutil.copy2(folder_path + siteurl + "/search/index.html","basic_page/search-index.html")
    shutil.copy2(folder_path + siteurl + "/today/index.html","basic_page/today-index.html")
    shutil.copy2(folder_path + siteurl + "/index.html","basic_page/toppage-index.html")
    shutil.copy2(folder_path + siteurl + "/music/index.html","basic_page/musictop-index.html")

def conect_close():#接続切るよう
    cur.close()
    con.close()
    cur_ms.close()
    con_ms.close()
    print("接続を切りました")

def flatten(l):
    for el in l:
        if isinstance(el, collections.abc.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

def update_videodata():
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID")
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
        #cur.execute("INSERT INTO VIDEO_V_DATA (VIDEO_ID,RELOAD_TIME,VIEW_C,LIKE_C,COMMENT_C) VALUES(:vid,:ndt,:vc,:lc,:cc)",vid=v_st[x[0]],ndt=dt_str,vc=str(v_st[x[1]]),lc=str(v_st[x][2]),cc=str(v_st[x][3]))
        cur.execute("INSERT INTO VIDEO_V_DATA (VIDEO_ID,RELOAD_TIME,VIEW_C,LIKE_C,COMMENT_C) VALUES('" + v_st[x][0] + "','" + dt_str + "','" + str(v_st[x][1]) + "','" + str(v_st[x][2]) + "','" + str(v_st[x][3]) + "')")
    con.commit()

def correct_video_list():
    cur.execute("SELECT DISTINCT PLAYLIST_ID FROM CRAWLER_PLAYLIST")
    pid_kl = cur.fetchall()
    pid_l = []
    pid_l_a = pid_l.append
    for x in range(len(pid_kl)):
        pid_l_a(str(pid_kl[x])[2:-3])
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID")
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
            #cur.execute(f"INSERT INTO VIDEO_ID (VIDEO_ID,CHANNEL_ID,UPLOAD_TIME,VIDEO_NAME,MOVIE_TIME) VALUES('{v_data[x][0]}','{v_data[x][1]}','{str(v_data[x][2])[:-1].replace('T',' ')}','{str(v_data[x][3]).replace('\'','\'\'')}','{v_data[x][5]}')")
            cur.execute("INSERT INTO VIDEO_ID (VIDEO_ID,CHANNEL_ID,UPLOAD_TIME,VIDEO_NAME,MOVIE_TIME,IG) VALUES(:vid,:chid,:ut,:vname,:mt,2)",vid=v_data[x][0],chid=v_data[x][1],ut=str(v_data[x][2])[:-1].replace('T',' '),vname=v_data[x][3],mt=v_data[x][5])
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
    ok_id_list = []
    for x in chid_list:
        cur.execute("select distinct ch_id from ch_id where ch_id = :nid",nid=x)
        n = cur.fetchone()
        if n == None:
            ok_id_list.append(x)
    if len(ok_id_list)==0:
        return
    rt_ch = gy.ExtremeChidToInfo(ok_id_list)
    for x in range(len(rt_ch)):
        cur.execute("INSERT INTO CH_ID (CH_ID,NAM,PICTURE_URL) VALUES ('" + rt_ch[x][0] + "','" + str(rt_ch[x][1]).replace("'","''") + "','" + rt_ch[x][2] + "')")
    con.commit()
    print("データ追加完了")

def add_groupe_name():
    #テーブルA=ペアリスト テーブルB=動画IDリスト　参考https://www.projectgroup.info/tips/Oracle/SQL/SQL000001.html
    cur.execute("INSERT INTO PAIR_LIST_SECOND (GROUPE_NAME) SELECT distinct GROUPE_NAME FROM VIDEO_ID TAB_B WHERE GROUPE_NAME IS NOT NULL AND NOT EXISTS (SELECT 'X' FROM PAIR_LIST_SECOND TAB_A WHERE TAB_A.GROUPE_NAME = TAB_B.GROUPE_NAME)")
    con.commit()

def video2data_v2(video_id):
    try:
        cur.execute("SELECT VIDEO_ID,CHANNEL_ID,VIDEO_NAME,MUSIC_NAME,GROUPE_NAME FROM VIDEO_ID WHERE VIDEO_ID = :video_id",video_id=video_id)
        video_info = cur.fetchone()
        song_info = [video_info[0],search_musicdata(video_info[3])]
        if video_info[4]==None:#投稿者が一人で歌っている場合
            song_info.append(1)
            cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,BELONG_OFFICE FROM CH_ID ci WHERE CH_ID = :ch_id",ch_id=video_info[1])
            song_info.append(list(cur.fetchone()))
        else:#グループで歌っているパターン
            menlist = groupe_name2men_namev2(video_info[4])
            if len(menlist)==1:
                song_info.append(1)
                cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,BELONG_OFFICE FROM CH_ID WHERE (NICK_NAME_1 in (:nick_name) OR NICK_NAME_2 in (:nick_name)) and ig = 0",nick_name=menlist[0])
                song_info.append(list(cur.fetchone()))
            else:
                song_info.extend([len(menlist),search_chdata_list_bf(menlist)])
        song_info.append(video_info)
        return song_info
    except:
        pro_log("error","video2data_v2",video_id,"unknown error->continue")

def groupe_name2men_namev2(groupe_name):#v2のテーブルにアクセス
    try:
        cur.execute("select MN from (select TO_CHAR(MN_1) AS MN from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_2) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_3) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_4) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_5) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_6) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_7) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_8) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_9) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_10) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_11) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_12) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_13) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_14) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_15) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_16) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_17) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_18) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_19) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_20) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_21) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_22) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_23) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_24) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_25) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_26) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_27) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_28) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_29) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_30 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_31 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_32 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_33 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_34 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_35 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_36 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_37 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_38 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_39 from PAIR_LIST_SECOND where groupe_name = :group_name) mt where exists(select * from ch_id chi where chi.ig = 0 and mt.MN in (chi.NICK_NAME_1,chi.NICK_NAME_2))",group_name=groupe_name)
        songer_list = [r[0] for r in cur.fetchall()]
        return songer_list
    except:
        pro_log("error","groupe_name2men_namev2",groupe_name,"unknown error->continue")

def group_name2mendata(group_name):#v2テーブルアクセス
    try:
        cur.execute("SELECT MN,(SELECT PICTURE_URL FROM CH_ID chi WHERE (chi.NICK_NAME_1 = mt.MN OR chi.NICK_NAME_2 = mt.MN) AND IG = 0) from (select TO_CHAR(MN_1) AS MN from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_2) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_3) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_4) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_5) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_6) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_7) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_8) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_9) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_10) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_11) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_12) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_13) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_14) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_15) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_16) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_17) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_18) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_19) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_20) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_21) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_22) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_23) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_24) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_25) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_26) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_27) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_28) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_29) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_30 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_31 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_32 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_33 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_34 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_35 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_36 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_37 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_38 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_39 from PAIR_LIST_SECOND where groupe_name = :group_name) mt where exists(select * from ch_id chi where chi.ig = 0 and mt.MN in (chi.NICK_NAME_1,chi.NICK_NAME_2))",group_name=group_name)
        return [[x[0],x[1]] for x in cur.fetchall()]
    except:
        pro_log("error","group_name2mendata",group_name,"unknown error->continue")

def add_music_data():
    cur.execute("SELECT DISTINCT MUSIC_NAME FROM VIDEO_ID WHERE MUSIC_NAME IS NOT NULL AND MUSIC_NAME NOT IN (SELECT KEY_MUSIC_NAME FROM MUSIC_SONG_DB WHERE KEY_MUSIC_NAME IS NOT NULL)")
    k_rec_mlist = cur.fetchall()
    if len(k_rec_mlist)==0:
        return
    for x in range(len(k_rec_mlist)):
        nx = str(k_rec_mlist[x])[2:-3]
        n_music_reslist = md.search_music(nx)#検索
        cur.execute("INSERT INTO MUSIC_SONG_DB (KEY_MUSIC_NAME,MUSIC_NAME_SP,MUSIC_NAME_YT,ARTIST_NAME,SP_ID,YT_ID) VALUES('" + nx.replace("'","''") + "','" + n_music_reslist[0].replace("'","''") + "','" + n_music_reslist[1].replace("'","''") + "','" + n_music_reslist[2].replace("'","''") + "','" + n_music_reslist[3] + "','" + n_music_reslist[4] + "')")
    con.commit()

def true_check():
    try:
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
            print(x[0] + "の情報がありません at pair_list_second.groupe_name")
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
            n_glist = groupe_name2men_namev2(groupe_list[x][0])
            kari = [k for k, v in collections.Counter(n_glist).items() if v > 1]
            for x in range(len(kari)):#重複チェック
                _faul += 1
                print(str(kari[x]) + "\tは文字列が重複しています at pair_list")
            er = list(set(n_glist) - s_nickname_list)
            if len(er)!=0:#データベースに登録なし
                for r in range(len(er)):
                    _faul += 1
                    print(er[r] + "\tはデータベースに登録されていません at pair_list グループ名:" + groupe_list[x][0])
        #動画の投稿者が存在するか確認
        cur.execute("select distinct channel_id from VIDEO_ID vid where not exists ( select 1 from ch_id ch where vid.CHANNEL_ID = ch.ch_id ) and channel_id is not null")
        ch_list = cur.fetchall()
        for x in ch_list:
            print(x[0] + "\tの情報がデータベースにありません at ch_id ch_id")
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
        cur.execute("SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 is null and ig = 0")
        gn_n1none = cur.fetchall()
        for r in gn_n1none:
            print(r[0] + "\tのメンバーが登録されていません at pairlist")
        if _faul==0:
            print("すべてのチェックを通過しました。")
            pro_log("log","true_check","","異常なし")
        else:
            print(str(_faul) + "件のエラーが発生しています")
            pro_log("log","true_check","",str(_faul) + "件のエラーが発生しています")
    except:
        pro_log("error","true_check","","failed true_check->continue")

def music_list(music_name):
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID WHERE MUSIC_NAME = :music_name and ig = 0 and status = 0 ORDER BY UPLOAD_TIME DESC",music_name=music_name)#投稿が新しい順に並び変え
    return [x[0] for x in cur.fetchall()]

def nomsec_time(datetime_obj):
    return str(datetime_obj.year) + "-" + str(datetime_obj.month) + "-" + str(datetime_obj.day) + "T" + str(datetime_obj.hour) + ":" + str(datetime_obj.minute) + ":" + str(datetime_obj.second) + "+09:00"

def search_musicdata(music_name):
    cur.execute("SELECT KEY_MUSIC_NAME,ARTIST_NAME,SP_ID,YT_ID,CLEATE_PAGE_DATE,LAST_MODIFIED FROM MUSIC_SONG_DB msd WHERE KEY_MUSIC_NAME = :msnm",msnm=music_name)
    s_music_data = list(cur.fetchone())
    if s_music_data[4]==None:
        nowdate = datetime.datetime.now()
        cur.execute("UPDATE MUSIC_SONG_DB SET CLEATE_PAGE_DATE = :oct where KEY_MUSIC_NAME = :msnm",oct=oracle_time(nowdate),msnm=music_name)
        con.commit()
        s_music_data[4] = nomsec_time(nowdate)
    else:
        s_music_data[4] = nomsec_time(s_music_data[4])
    if s_music_data[5]!=None:
        s_music_data[5] = nomsec_time(s_music_data[5])
    return s_music_data

def search_chdata(nick_name):
    nick_name = nick_name.replace("'","''")
    cur.execute("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,NICK_NAME_2 FROM CH_ID WHERE NICK_NAME_1 = :nick_name OR NICK_NAME_2 = :nick_name",nick_name=nick_name)
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
    #print("SELECT NICK_NAME_1,CH_ID,NAM,PICTURE_URL,LINK,BELONG_OFFICE FROM CH_ID WHERE (NICK_NAME_1 in (" + pnick_name_list + ") OR NICK_NAME_2 in (" + pnick_name_list + ")) and ig = 0")
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
    if len(ch_dlist)!=len(nick_name_list):
        print("エラーが発生したかも")   
    return ch_dlist

def video_name_db(video_id):
    cur.execute("SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID='" + video_id + "'")
    return cur.fetchone()

def youtube_embedded(video_id):
    return '<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/' + video_id + '" title="YouTube video player" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'

def look_up_v_history(video_id,scope=7):#scopeでデータ取得　jstタイムゾーンがJSTなことを確認!!
    cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'), NVL(NULLIF((VIEW_C - lag(VIEW_C, 1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0), 0) AS DIFF, LIKE_C, COMMENT_C FROM VIDEO_V_DATA vvd WHERE VIDEO_ID = '" + video_id + "' AND RELOAD_TIME > SYSDATE - " + str(scope + 1) + " ORDER BY RELOAD_TIME ASC OFFSET 1 ROWS FETCH FIRST 7 ROWS ONLY")
    return cur.fetchall()

def view_vlist_graph(video_idlist,scope=7,data=0):
    if video_idlist==[]:
        return ""
    st_vidlist = str(video_idlist).replace("[","").replace("]","").replace(" ","")
    cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'),SUM(VIEW_C),SUM(LIKE_C),SUM(COMMENT_C) FROM VIDEO_V_DATA WHERE VIDEO_ID IN(" + st_vidlist + ") AND RELOAD_TIME >= (CURRENT_DATE - " + str(scope) + ") GROUP BY RELOAD_TIME ORDER BY RELOAD_TIME ASC")
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
    if data==0:
        html_data = "<canvas id='sum-yt' class='yt-view-sum inline'></canvas><script>Chart_cleater_v2('sum-yt'," + str(label) + "," + str(data_v) + "," + str(data_l) + "," + str(data_c) + ");</script>"
        return html_data
    elif data==1:
        k_array = [label,data_v,data_l,data_c]
        return k_array

def view_ch_graph(nick_name):
    cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'), SUM(VIEW_C), SUM(LIKE_C), SUM(COMMENT_C) FROM VIDEO_V_DATA WHERE VIDEO_ID IN (select video_id from video_id where video_id in (select video_id from video_id where IG = 0 AND CHANNEL_ID = (SELECT CHANNEL_ID FROM CH_ID WHERE (NICK_NAME_1 = :menl OR NICK_NAME_2 = :menl) AND IG = 0) UNION ALL SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 0 AND GROUPE_NAME in (SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 in (:menl) OR MN_2 in (:menl) OR MN_3 in (:menl) OR MN_4 in (:menl) OR MN_5 in (:menl) OR MN_6 in (:menl) OR MN_7 in (:menl) OR MN_8 in (:menl) OR MN_9 in (:menl) OR MN_10 in (:menl) OR MN_11 in (:menl) OR MN_12 in (:menl) OR MN_13 in (:menl) OR MN_14 in (:menl) OR MN_15 in (:menl) OR MN_16 in (:menl) OR MN_17 in (:menl) OR MN_18 in (:menl) OR MN_19 in (:menl) OR MN_20 in (:menl) OR MN_21 in (:menl) OR MN_22 in (:menl) OR MN_23 in (:menl) OR MN_24 in (:menl) OR MN_25 in (:menl) OR MN_26 in (:menl) OR MN_27 in (:menl) OR MN_28 in (:menl) OR MN_29 in (:menl) OR MN_30 in (:menl) OR MN_31 in (:menl) OR MN_32 in (:menl) OR MN_33 in (:menl) OR MN_34 in (:menl) OR MN_35 in (:menl) OR MN_36 in (:menl) OR MN_37 in (:menl) OR MN_38 in (:menl) OR MN_39 in (:menl)) UNION ALL select video_id from video_id where channel_id in (select CH_ID from CH_ID where LINK = (SELECT CHANNEL_ID FROM CH_ID WHERE (NICK_NAME_1 = :menl OR NICK_NAME_2 = :menl) AND IG = 0))) and music_name is not null AND STATUS = 0) AND RELOAD_TIME >= (CURRENT_DATE - 7) GROUP BY RELOAD_TIME ORDER BY RELOAD_TIME ASC",menl=nick_name)
    chv = cur.fetchall()
    return [[x[0] for x in chv],[x[1] for x in chv],[x[2] for x in chv],[x[3] for x in chv]]

def view_music_graph(music_name,scope=7,dt=0):
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
    if dt==0:
        html_data = "<canvas id='sum-yt' class='yt-view-sum inline'></canvas><script>Chart_cleater_v2('sum-yt'," + str(label) + "," + str(data_v) + "," + str(data_l) + "," + str(data_c) + ");</script>"
        return html_data
    elif dt==1:
        stadata = [label,data_v,data_l,data_c]
        return stadata

def view_graph(video_id,scope=7,dt=0):
    v_his = look_up_v_history(video_id,scope)
    label = []
    w_data = []
    l_data = []
    c_data = []
    label_a = label.append
    w_data_a = w_data.append
    l_data_a = l_data.append
    c_data_a = c_data.append
    for x in range(len(v_his)):
        label_a(v_his[x][0])
        w_data_a(v_his[x][1])
        l_data_a(v_his[x][2])
        c_data_a(v_his[x][3])
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
    elif dt==3:
        html_data = "<canvas id='" + video_id + "' class='yt-view_graph'></canvas>"
        script = "<script>dt('" + video_id + "');Chart_cleater_v2('" + video_id + "'," + str(label) + "," + str(w_data) + "," + str(l_data) + "," + str(c_data) + ");</script>"
        return html_data,script
    elif dt==4:
        html_data = "<canvas id='" + video_id + "' class='yt-view_graph'></canvas>"
        script = [video_id,label,w_data,l_data,c_data]
        return html_data,script
    elif dt==5:
        script = [video_id,label,w_data,l_data,c_data]
        return script

def musicvlist(musicname):
    cur.execute("select VIDEO_ID from VIDEO_ID WHERE MUSIC_NAME = :msname AND MOVIE_TIME > 60",msname=musicname)
    return [x[0] for x in cur.fetchall()]

def make_all_musicpage():
    cur.execute("SELECT KEY_MUSIC_NAME FROM MUSIC_SONG_DB")
    for x in cur.fetchall():
        make_musicpage_v3(str(x)[2:-3])

def reloadpeople_picture():
    #youtubeの場合
    cur.execute("SELECT CH_ID FROM CH_ID WHERE CH_ID is not null and ig = 0")
    chid_list = []
    chid_list_a = chid_list.append
    for x in cur.fetchall():
        chid_list_a(str(x)[2:-3])
    ch_data = gy.ExtremeChidToInfo(chid_list)
    for x in ch_data:
        cur.execute("UPDATE CH_ID SET PICTURE_URL=:purl WHERE CH_ID = :chid",purl=x[2],chid=x[0])
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

def get_ch_vdata(nickname,mode=0):
    chdata = search_chdata(nickname)
    if chdata[5]!=None:
        nclist = [str(chdata[0]).replace("'","''"),str(chdata[5]).replace("'","''")]
    else:
        nclist = [str(chdata[0]).replace("'","''")]
    menlist = str(nclist).replace("[","").replace("]","")
    cur.execute("select video_id from video_id where video_id in (select video_id from video_id where IG = 0 AND CHANNEL_ID = '" + chdata[1] + "' UNION ALL SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 0 AND GROUPE_NAME in (SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 in (:menl) OR MN_2 in (:menl) OR MN_3 in (:menl) OR MN_4 in (:menl) OR MN_5 in (:menl) OR MN_6 in (:menl) OR MN_7 in (:menl) OR MN_8 in (:menl) OR MN_9 in (:menl) OR MN_10 in (:menl) OR MN_11 in (:menl) OR MN_12 in (:menl) OR MN_13 in (:menl) OR MN_14 in (:menl) OR MN_15 in (:menl) OR MN_16 in (:menl) OR MN_17 in (:menl) OR MN_18 in (:menl) OR MN_19 in (:menl) OR MN_20 in (:menl) OR MN_21 in (:menl) OR MN_22 in (:menl) OR MN_23 in (:menl) OR MN_24 in (:menl) OR MN_25 in (:menl) OR MN_26 in (:menl) OR MN_27 in (:menl) OR MN_28 in (:menl) OR MN_29 in (:menl) OR MN_30 in (:menl) OR MN_31 in (:menl) OR MN_32 in (:menl) OR MN_33 in (:menl) OR MN_34 in (:menl) OR MN_35 in (:menl) OR MN_36 in (:menl) OR MN_37 in (:menl) OR MN_38 in (:menl) OR MN_39 in (:menl) ) UNION ALL select video_id from video_id where channel_id in (select CH_ID from CH_ID where LINK='" + chdata[1] + "')) and music_name is not null AND STATUS = 0 ORDER BY UPLOAD_TIME DESC",menl=menlist)
    vidlist = cur.fetchall()
    vdata = []
    vdata_a = vdata.append
    vid_list = []
    vid_a = vid_list.append
    if mode==0:
        for n in vidlist:
            vdata_a(video2data_v2(str(n)[2:-3]))
            vid_a(str(n)[2:-3])
        cur.execute("select CLEATE_PAGE_DATE from ch_id where NICK_NAME_1 in ('" + nickname + "')")
        t_page_d = cur.fetchone()
        if t_page_d[0]==None:
            nowdate = datetime.datetime.now()
            cur.execute("UPDATE CH_ID SET CLEATE_PAGE_DATE = '" + oracle_time(nowdate) + "' where NICK_NAME_1 = '" + nickname.replace("'","''") + "'")
            con.commit()
            t_page_d = nomsec_time(nowdate)
        else:
            t_page_d = nomsec_time(t_page_d[0])
        cur.execute("select LAST_MODIFIED from ch_id where NICK_NAME_1 in ('" + nickname + "')")
        lmod = cur.fetchone()
        lmod_t = nomsec_time(lmod[0])
    elif mode==1:
        for n in vidlist:
            vid_a(str(n)[2:-3])
    if mode==0:
        return vdata,t_page_d,vid_list,lmod_t
    elif mode==1:
        return vid_list

def make_musicpage_v3(music_name,mode=0):
    try:
        n_html_path = folder_path + siteurl + "/music/" + dir_name_replace(music_name) + "/"
        if os.path.isdir(n_html_path)==False:
            os.makedirs(n_html_path)
        share_html = []
        share_html_a = share_html.append
        if mode==0:
            description = "Vtuberの" + music_name + "の歌ってみた動画をまとめたサイトです。たくさんのvtuberの歌ってみた動画のランキングのサイトです。皆様に沢山のvtuberを知ってもらいたく運営しています。"
            page_title = "Vtuberの歌う" + music_name
            music_data = search_musicdata(music_name)
            share_html_a('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/music/" + music_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + music_data[4] + '"><meta property="article:modified_time" content="' + music_data[5] + '"></head><body>')
            share_html_a(html_import_lib)
            share_html_a(header)
            share_html_a('<main><div class="for_center">')
            if music_data[1]==None:
                music_data[1] = "不明"
            if music_data[2] and music_data[3]!=None:#spotifyもyoutubeも存在する場合
                share_html_a("<h1><button class='bt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + music_data[0] + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/watch?v=" + music_data[3] + "'>YoutubeMusicで聞く</a></td></tr><tr><td><p>" + music_data[0] + "</p></td><td><p>" + music_data[1] + """</p><td><a href='https://open.spotify.com/track/""" + music_data[2] + """'>Spotifyで再生</a></td></tr></table>""")
            elif music_data[2]==None and music_data[3]!=None:#spotifyにはないがyoutubeにはある場合
                share_html_a("<h1><button class='bt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + music_data[0] + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/watch?v=" + music_data[3] + "'>YoutubeMusicで聞く</a></td></tr><tr><td><p>" + music_data[0] + "</p></td><td><p>" + music_data[1] + "</p><td><a href='https://open.spotify.com/search/" + urllib.parse.quote(music_data[0]) + "'>spotifyで検索(DBに登録されていません)</a></td></tr></table>")
            elif music_data[2]!=None and music_data[3]==None:#spotifyにありyoutubeにないパターン
                share_html_a("<h1><button class='bt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + music_data[0] + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/search?q=" + music_data[0] + "'>YoutubeMusicで検索(DBにデータがありません)</a></td></tr><tr><td><p>" + music_data[0] + "</p></td><td><p>" + music_data[1] + """</p><td><a href='https://open.spotify.com/track/""" + music_data[2] + """'>Spotifyで再生</a></td></tr></table>""")
            else:#spotifyにもyoutubeにもないパターン
                share_html_a("<h1><button class='bt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + music_data[0] + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/search?q=" + music_data[0] + "'>YoutubeMusicで検索(DBにデータがありません)</a></td></tr><tr><td><p>" + music_data[0] + "</p></td><td><p>" + music_data[1] + "</p><td><a href='https://open.spotify.com/search/" + urllib.parse.quote(music_data[0]) + "'>spotifyで検索(DBに登録されていません)</a></td></tr></table>")
            share_html_a('<group class="inline-radio-sum yt-view-sum" onchange="change_graph_music(\'sum-yt\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">コメント数</label></div></group>' + "<canvas id='sum-yt' class='yt-view-sum inline'></canvas>")
            share_html_a('</div><div id="music_flex">')
            music_videos = music_list(music_name)#動画IDと動画名取得
            v_data = [video2data_v2(g) for g in music_videos]
            nowdata = []
            for x in range(len(v_data)):
                men_of_list = []
                if v_data[x][2]==1:#歌い手が１人
                    if v_data[x][3][5]==None:
                        v_data[x][3][5] = "個人"
                    men_of_list = [str(v_data[x][3][0]).replace(" ",""),v_data[x][3][5]]
                else:#複数人
                    for w in range(v_data[x][2]):
                        if v_data[x][3][w][0] not in men_of_list:
                            men_of_list.append(str(v_data[x][3][w][0]).replace(" ",""))
                        if v_data[x][3][w][5]==None:
                            v_data[x][3][w][5] = "個人"
                        if v_data[x][3][w][5] not in men_of_list:
                            men_of_list.append(v_data[x][3][w][5])
                nowdata.append(f'<div id="fb_{v_data[x][0]}" class="music_flex_ly {" ".join(men_of_list)}"><span class="ofoverflow_320" title="{v_data[x][4][2]}">{v_data[x][4][2]}</span><lite-youtube videoid="{v_data[x][0]}"></lite-youtube><button class="ofoverflow_320 minmg" onclick="vdt(\'{v_data[x][0]}\')">詳細を表示</button></div>')
            share_html_a(nowdata)
            share_html_a("""</div></div><div class="pos-re"><div id="descm"></div><div id="music_recommend"></div><div id="descc"></div><div id="ch_recommend"></div></div></main>""" + music_control_html)
            share_html_a("<script src='/library/main.js'></script></body></html>")
            with open(n_html_path + "index.html","wb") as f:
                f.write("".join(list(flatten(share_html))).encode("utf-8"))#windows対策
    except Exception as e:
        pro_log("error","make_musicpage_v3",music_name,"unknown error->continue",str(e))

def make_chpage_v3(nick_name):
    try:
        site_nick_name = dir_name_replace(nick_name)
        n_html_path = folder_path + siteurl + "/ch/" + site_nick_name + "/"
        if os.path.isdir(n_html_path)==False:#フォルダがなければ生成
            os.mkdir(n_html_path)
        v_data,page_fc_date,videolist_id,page_lmod = get_ch_vdata(nick_name)
        share_html = []
        share_html_a = share_html.append
        description = "Vtuberの" + nick_name + "が歌った歌ってみた及びオリジナル曲をまとめたサイトです。たくさんのvtuberの歌ってみた動画のランキングのサイトです。皆様に沢山のvtuberを知ってもらいたく運営しています。"
        page_title = nick_name + "の歌った曲集"
        share_html_a('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + site_nick_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + page_fc_date + '"><meta property="article:modified_time" content="' + page_lmod + '"></head><body>')
        share_html_a(html_import_lib)
        share_html_a(header)
        share_html_a('<main><div class="for_center">')
        share_html_a('<group class="inline-radio-sum yt-view-sum" onchange="change_graph_ch(\'sum-yt\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">コメント数</label></div></group>' + "<canvas id='sum-yt' class='yt-view-sum inline'></canvas></div><div id='ch_flex'>")
        nowdata = []
        for x in range(len(v_data)):
            men_of_list = []
            if v_data[x][2]==1:#歌い手が１人
                if v_data[x][3][5]==None:
                    v_data[x][3][5] = "個人"
                men_of_list = [str(v_data[x][3][0]).replace(" ",""),v_data[x][3][5]]
            else:#複数人
                for w in range(v_data[x][2]):
                    if v_data[x][3][w][0] not in men_of_list:
                        men_of_list.append(str(v_data[x][3][w][0]).replace(" ",""))
                    if v_data[x][3][w][5]==None:
                        v_data[x][3][w][5] = "個人"
                    if v_data[x][3][w][5] not in men_of_list:
                        men_of_list.append(v_data[x][3][w][5])
            nowdata.append(f'<div id="fb_{v_data[x][0]}" class="music_flex_ly {" ".join(men_of_list)}"><span class="ofoverflow_320" title="{v_data[x][1][0]}"><a href="{"/music/" + dir_name_replace(v_data[x][1][0]) + "/"}" onclick="page_ajax_load(\'{"/music/" + dir_name_replace(v_data[x][1][0]) + "/"}\');return false">{v_data[x][1][0]}</a></span><lite-youtube videoid="{v_data[x][0]}"></lite-youtube><button class="ofoverflow_320 minmg" onclick="vdt(\'{v_data[x][0]}\')">詳細を表示</button></div>')
        share_html_a(nowdata)
        share_html_a("""</div><div class="pos-re"><div id="descm"></div><div id="music_recommend"></div><div id="descc"></div><div id="ch_recommend"></div></div></main>""" + music_control_html)
        share_html_a("<script src='/library/main.js'></script></body></html>")
        with open(n_html_path + "index.html","wb") as f:
            f.write("".join(list(flatten(share_html))).encode("utf-8"))#windows対策
    except Exception as e:
        pro_log("error","make_chpage_v3",nick_name,"unknown error->continue",str(e))

def make_all_chpage():
    cur.execute("select nick_name_1 from ch_id where ig = 0 and nick_name_1 is not null and content_count > 0")
    chid_list = cur.fetchall()
    for i in chid_list:
        make_chpage_v3(str(i)[2:-3])

def music_recommend_page():
    ajax_path = folder_path + siteurl + "/ajax/music/"
    cur.execute("select key_music_name,(select VIDEO_ID from VIDEO_ID vid where vid.MUSIC_NAME = msd.KEY_MUSIC_NAME AND STATUS = 0 order by upload_time desc FETCH FIRST 1 ROWS ONLY) from MUSIC_SONG_DB msd where exists(select * from VIDEO_ID vid where msd.KEY_MUSIC_NAME = vid.music_name having count(*) > 0)")
    music_list = [[x[0],x[1]] for x in cur.fetchall()]
    len_mlist = len(music_list)
    for n in range(100):#おすすめを100件生成
        k_ranlist = []
        n_dict = {}
        while len(k_ranlist)<20:
            k = random.randint(0,len_mlist-1)
            if k not in k_ranlist:
                k_ranlist.append(k)
        for x in range(len(k_ranlist)):
            nmusic_name = music_list[k_ranlist[x]][0]
            k_ar = [nmusic_name,dir_name_replace(nmusic_name),music_list[k_ranlist[x]][1]]
            n_dict[x] = k_ar
        with open(ajax_path + "mr-" + str(n) + ".json","w") as f:
            json.dump(n_dict,f,indent=4)

def make_api_video_data():
    cur.execute("SELECT VIDEO_ID,(SELECT NICK_NAME_1 FROM CH_ID WHERE CH_ID.CH_ID=VIDEO_ID.CHANNEL_ID),(SELECT PICTURE_URL FROM CH_ID WHERE CH_ID.CH_ID=VIDEO_ID.CHANNEL_ID),VIDEO_NAME,MUSIC_NAME from VIDEO_ID where ig = 0 and STATUS = 0 and GROUPE_NAME IS NULL")
    now_ls = [[x[0],x[1],x[2],x[3],x[4]] for x in cur.fetchall()]
    for r in now_ls:
        with open(folder_path + siteurl + "/api/videoid/" + r[0] + ".json","w") as f:
            json.dump({"videoid":r[0],"nickname":r[1],"chphoto":r[2],"videoname":r[3],"musicname":r[4],"groupname":"","statisticsdata":view_graph(r[0],7,5)},f)
    cur.execute("SELECT VIDEO_ID,VIDEO_NAME,MUSIC_NAME,GROUPE_NAME from VIDEO_ID where ig = 0 and STATUS = 0 and GROUPE_NAME IS NOT NULL")
    nowls = [[x[0],x[1],x[2],x[3]] for x in cur.fetchall()]
    for r in nowls:
        with open(folder_path + siteurl + "/api/videoid/" + r[0] + ".json","w") as f:
            json.dump({"videoid":r[0],"nickname":"","chphoto":"","videoname":r[1],"musicname":r[2],"groupname":dir_name_replace(r[3]),"statisticsdata":view_graph(r[0],7,5)},f)

def make_api_group_data(strict=0):
    #動画があり入力されているのだけを抽出
    cur.execute("SELECT DISTINCT GROUPE_NAME FROM VIDEO_ID vid WHERE EXISTS(SELECT * FROM PAIR_LIST_SECOND pls WHERE pls.GROUPE_NAME = vid.GROUPE_NAME AND MN_1 IS NOT NULL) AND IG = 0 AND STATUS = 0")
    now_ls = [x[0] for x in cur.fetchall()]
    for r in now_ls:
        nfpath = folder_path + siteurl + "/api/groupname/" + dir_name_replace(r) + ".json"
        if os.path.isfile(nfpath) and strict==0:
            pass
        else:
            with open(nfpath,"w") as f:
                json.dump({"groupname":r,"groupmenlist":group_name2mendata(r)},f)

def beta_add_videotime():
    cur.execute("select VIDEO_ID from VIDEO_ID where MOVIE_TIME is null and STATUS = 0")#必要なカラムを取得
    nowls = [x[0] for x in cur.fetchall()]
    kalist = gy.videoid_lToMInfo(nowls)
    for x in kalist:
        cur.execute("UPDATE VIDEO_ID SET MOVIE_TIME = :mtlong WHERE VIDEO_ID = :nvid",nvid=x[0],mtlong=x[5])
    con.commit()

def make_api_music_data():
    cur.execute("SELECT KEY_MUSIC_NAME,SP_ID,YT_ID FROM MUSIC_SONG_DB WHERE CONTENT_COUNT > 0")
    nowls = [[x[0],view_music_graph(x[0],7,1),x[1],x[2],musicvlist(x[0])] for x in cur.fetchall()]
    for r in nowls:
        with open(folder_path + siteurl + "/api/music/" + dir_name_replace(r[0]) + ".json","w") as f:
            json.dump({"musicname":r[0],"statisticsdata":r[1],"sp":r[2],"yt":r[3],"videolist":r[4]},f)

def make_api_ch_data():
    cur.execute("select nick_name_1 from ch_id where ig = 0 and nick_name_1 is not null and content_count > 0")
    nowls = [[x[0],view_vlist_graph(get_ch_vdata(x[0],1),data=1),get_ch_vdata(x[0],1)] for x in cur.fetchall()]
    for r in nowls:
        with open(folder_path + siteurl + "/api/channel/" + dir_name_replace(r[0]) + ".json","w") as f:
            json.dump({"channelnickname":r[0],"statisticsdata":r[1],"videolist":r[2]},f)

def channel_recommend_page():
    ajax_path = folder_path + siteurl + "/ajax/ch/"
    cur.execute("select nick_name_1,picture_url from ch_id where ig = 0 and NICK_NAME_1 is not null")
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
            k_ar = [ch_data[k_ranlist[n]][0],dir_name_replace(ch_data[k_ranlist[n]][0]),ch_data[k_ranlist[n]][1]]
            n_dict[n] = k_ar
        with open(ajax_path + "cr-" + str(x) + ".json","w") as f:
            json.dump(n_dict,f,indent=4)

def dir_name_replace(dir_name):
    ret_dn = str(dir_name).replace("\\","").replace(",","").replace(".","").replace(":","").replace(";","").replace("?","").replace("/","").replace("<","").replace(">","").replace("*","").replace("|","").replace("+","").replace("=","").replace("[","").replace("]","").replace('"',"").replace("(","").replace(")","").replace("^","").replace("!","").replace("$","").replace("'","").replace("%","").replace("&","").replace("～","").replace("#","").replace("＃","")
    return ret_dn

kks = kakasi()#インスタンスは負荷がかかるので事前に呼び出す
moji = str.maketrans("ぁぃぅぇぉっゃゅょ", "あいうえおつやゆよ")#使いまわせるものわしなくては！

def KanjiToKana(kanji_st):
    kanji_st = kanji_st.lower()
    kanji_st.replace(" ","").replace("　","")
    res = kks.convert(kanji_st)
    er_strings = [["博衣こより","はくいこより"],["雪花ラミィ","ゆきはならみぃ"],["大神ミオ","おおかみみお"]]
    k_res_list = []#うまくルビ振りができないのを登録
    for x in res:
        k_res_list.append(x["hira"])
    all_kana_res = "".join(k_res_list)
    for x in er_strings:
        if kanji_st==x[0]:
            all_kana_res = x[1]
    kana_res = dir_name_replace(str(jaconv.kata2hira(kanji_st)).translate(moji))
    all_kana_res = dir_name_replace(all_kana_res.translate(moji))
    if all_kana_res==kana_res:
        return [all_kana_res]
    else:
        return [kana_res,all_kana_res]

def make_search_index():
    cur.execute("select KEY_MUSIC_NAME from MUSIC_SONG_DB where CLEATE_PAGE_DATE is not null")
    search_index = []
    search_index_a = search_index.append
    for x in cur.fetchall():
        nst = str(x)[2:-3]
        nowret = KanjiToKana(nst)
        if len(nowret)==1:
            search_index_a([nowret[0],nst,"/music/" + dir_name_replace(nst) + "/"])
        else:#2使えってくる
            for r in range(2):
                search_index_a([nowret[r],nst,"/music/" + dir_name_replace(nst) + "/"])
    cur.execute("select NICK_NAME_1 from ch_id where CLEATE_PAGE_DATE is not null")
    for x in cur.fetchall():
        nst = str(x)[2:-3]
        nowret = KanjiToKana(nst)
        if len(nowret)==1:
            search_index_a([nowret[0],nst,"/ch/" + dir_name_replace(nst) + "/"])
        else:#2使えってくる
            for r in range(2):
                search_index_a([nowret[r],nst,"/ch/" + dir_name_replace(nst) + "/"])
    cur.execute("SELECT CH_ID,NICK_NAME_1 FROM CH_ID WHERE ig = 0 and NAM not like '%Topic%' and EXISTS (SELECT DISTINCT CHANNEL_ID FROM VIDEO_ID WHERE IG = 0 AND STATUS = 0 AND GROUPE_NAME IS NULL and CH_ID.CH_ID = CHANNEL_ID)")#一人で歌っているチャンネルを取得
    single_ch_list = cur.fetchall()
    for n_chid in single_ch_list:
        cur.execute("SELECT VIDEO_ID,MUSIC_NAME FROM VIDEO_ID WHERE CHANNEL_ID = '" + n_chid[0] + "'AND IG = 0 AND GROUPE_NAME IS NULL AND STATUS = 0 AND MUSIC_NAME IS NOT NULL")
        for n in cur.fetchall():
            nst = n_chid[1] + " " + n[1]
            nowret = KanjiToKana(nst)
            if len(nowret)==1:
                search_index_a([nowret[0].replace(" ",""),nst,"/watch?v=" + n[0]])
            else:#2使えってくる
                for r in range(2):
                    search_index_a([nowret[r].replace(" ",""),nst,"/watch?v=" + n[0]])
            nst = n[1] + " " + n_chid[1]
            nowret = KanjiToKana(nst)
            if len(nowret)==1:
                search_index_a([nowret[0].replace(" ",""),nst,"/watch?v=" + n[0]])
            else:#2使えってくる
                for r in range(2):
                    search_index_a([nowret[r].replace(" ",""),nst,"/watch?v=" + n[0]])
    cur.execute("SELECT DISTINCT GROUPE_NAME FROM VIDEO_ID WHERE IG = 0 AND STATUS = 0 AND GROUPE_NAME IS NOT NULL")#使われているgroupe name抽出
    gname_v = cur.fetchall()
    for n_gn in gname_v:
        now_gname = str(n_gn)[2:-3]
        now_g_list = groupe_name2men_namev2(now_gname)
        cur.execute("SELECT VIDEO_ID,MUSIC_NAME FROM VIDEO_ID WHERE GROUPE_NAME = :gname AND IG = 0 AND STATUS = 0",gname=now_gname)
        for n in cur.fetchall():
            for z in now_g_list:
                nst = z + " " + n[1]
                nowret = KanjiToKana(nst)
                if len(nowret)==1:
                    search_index_a([nowret[0].replace(" ",""),nst,"/watch?v=" + n[0]])
                else:#2使えってくる
                    for r in range(2):
                        search_index_a([nowret[r].replace(" ",""),nst,"/watch?v=" + n[0]])
                nst = n[1] + " " + z
                nowret = KanjiToKana(nst)
                if len(nowret)==1:
                    search_index_a([nowret[0].replace(" ",""),nst,"/watch?v=" + n[0]])
                else:#2使えってくる
                    for r in range(2):
                        search_index_a([nowret[r].replace(" ",""),nst,"/watch?v=" + n[0]])
    k_ar = list(itertools.chain.from_iterable(search_index))
    with open(cgi_bin_dir + "/cgi-bin/search_index_a.json","w") as f:
        json.dump({"index":k_ar},f)
    with open(cgi_bin_dir + "/cgi-bin/search_index_a.rcsv","w",encoding="utf-8") as f:
        f.write("@".join(k_ar))
    """
    connection_l = MySQLdb.connect(host="localhost",user="root",passwd="mysqlroot",db="vsong")
    cur_l = connection_l.cursor()
    for r in search_index:
        cur_l.execute("INSERT INTO vsong_search (main_index_key,index_print_name,index_url) VALUES('" + r[0] + "','" + str(r[1]).replace("'","''") + "','" + r[2] + "')")
    connection_l.commit()
    connection_l.close()
    """

def make_video_random():
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID WHERE STATUS = 0")
    vid_list = []
    vid_list_a = vid_list.append
    for x in cur.fetchall():
        vid_list_a(str(x)[2:-3])
    vidlen = len(vid_list)
    for x in range(100):
        n_vidlist = []
        n_vidlist_a = n_vidlist.append
        n_range_list = []
        n_range_list_a = n_range_list.append
        while len(n_range_list)<100:
            n_range = random.randint(0,vidlen-1)
            if n_range not in n_range_list:
                n_range_list_a(n_range)
        for r in n_range_list:
            n_vidlist_a(vid_list[r])
        k_dict = {0:n_vidlist}
        with open(folder_path + siteurl + "/random_pl/ran" + str(x) + ".json","w") as f:
            json.dump(k_dict,f)

def todays_hot():
    #データベースから前日の伸び率　ただし分母や分子が0になったときは-1000を出力　を最初の100行だけ取得
    cur.execute("SELECT VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,NVL(NULLIF((VIEW_C - lag(VIEW_C,1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0)/NULLIF((lag(VIEW_C,1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME) - lag(VIEW_C,2) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0),-1000)-1 DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE -3 AND EXISTS (SELECT VIDEO_ID FROM VIDEO_ID vid WHERE vid.VIDEO_ID = vvd.VIDEO_ID AND IG = 0) ORDER BY RELOAD_TIME DESC,DIFF DESC FETCH FIRST 100 ROWS ONLY")
    kfetch = cur.fetchall()
    rank_list_a = [[r[0],r[1],math.floor(r[3]*100)] for r in kfetch]
    vidlist_a = [r[0] for r in kfetch]
    cur.execute("SELECT VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,NVL(NULLIF((VIEW_C - lag(VIEW_C,1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0),-1) AS DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE-2 AND EXISTS (SELECT VIDEO_ID FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID AND IG = 0) ORDER BY RELOAD_TIME DESC,DIFF DESC FETCH FIRST 100 ROWS ONLY")
    kfetch = cur.fetchall()
    rank_list_b = [[r[0],r[1],r[3]] for r in kfetch]
    vidlist_b = [r[0] for r in kfetch]
    cur.execute("SELECT VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,NVL(NULLIF((VIEW_C - lag(VIEW_C,7) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0),-1) AS DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE-8 AND EXISTS (SELECT VIDEO_ID FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID AND IG = 0) ORDER BY RELOAD_TIME DESC,DIFF DESC FETCH FIRST 100 ROWS ONLY")
    kfetch = cur.fetchall()
    rank_list_c = [[r[0],r[1],r[3]] for r in kfetch]
    vidlist_c = [r[0] for r in kfetch]
    cur.execute("SELECT VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,NVL(NULLIF((VIEW_C - lag(VIEW_C,30) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0),-1) AS DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE-31 AND EXISTS (SELECT VIDEO_ID FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID AND IG = 0) ORDER BY RELOAD_TIME DESC,DIFF DESC FETCH FIRST 100 ROWS ONLY")
    kfetch = cur.fetchall()
    rank_list_d = [[r[0],r[1],r[3]] for r in kfetch]
    vidlist_d = [r[0] for r in kfetch]
    cur.execute("select VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,VIEW_C from VIDEO_V_DATA vvd where RELOAD_TIME > SYSDATE -1 order by RELOAD_TIME desc,VIEW_C desc FETCH FIRST 100 ROWS ONLY")
    kfetch = cur.fetchall()
    rank_list_e = [[r[0],r[1],r[3]] for r in kfetch]
    vidlist_e = [r[0] for r in kfetch]
    with open(folder_path + siteurl + "/api/today/index.json","w") as f:
        json.dump({"index":[rank_list_a,rank_list_b,rank_list_c,rank_list_d,rank_list_e],"vidlist":[vidlist_a,vidlist_b,vidlist_c,vidlist_d,vidlist_e]},f)

def wikipedia_info(nickname_list):#wikipediapi->自動update 一度にできるの50個まででも名前にカンマ入っていると悲劇が起こるので40で
    #wikipedia apiは順番守らないので注意
    nowlen = len(nickname_list)
    nowloop = math.ceil(float(nowlen/40))
    for x in range(nowloop):
        if x==nowloop-1:
            now_long = nowlen - 40 * (x)
        else:
            now_long = 40
        now_nclist = []
        now_nclist_a = now_nclist.append
        for r in range(now_long):
            now_nclist_a(nickname_list[40*x+r])
        #nclist->nickname(1)|nickname(2)
        now_ncst = str(now_nclist).replace("[","").replace("]","").replace(",","|").replace("'","")
        jsong = requests.get("https://ja.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=" + now_ncst)
        new_json = jsong.json()#パース
        nowkeys = new_json["query"]["pages"].keys()
        for r in nowkeys:
            nowdata = new_json["query"]["pages"][r]
            title = nowdata["title"]
            try:
                exp = nowdata["extract"]
            except:
                exp = ""
            if exp!="":
                cur.execute("UPDATE CH_ID SET DESCRIPTION = '" + exp.replace("'","''").replace(" ","").replace("　","") + "' WHERE NICK_NAME_1 = '" + title.replace("'","''") + "'")
        con.commit()

def wikipedia_all():#没
    cur.execute("SELECT NICK_NAME_1 FROM CH_ID WHERE NICK_NAME_1 IS NOT NULL AND DESCRIPTION IS NULL")
    k_nclist = []
    k_nclist_a = k_nclist.append
    for z in cur.fetchall():
        k_nclist_a(str(z)[2:-3])
    wikipedia_info(k_nclist)

def make_music_top():
    cur.execute("SELECT VIDEO_ID,MUSIC_NAME FROM VIDEO_ID WHERE IG = 0 AND STATUS = 0")
    vlist = []
    vlist_a = vlist.append
    for x in cur.fetchall():
        nowst = dir_name_replace(x[1])
        vlist_a([x[0],x[1],"/music/" + nowst])
    vlist_len_c = len(vlist) - 1
    for r in range(100):
        karilist = []
        karilist_a = karilist.append
        for n in range(50):
            now_ran = random.randint(0,vlist_len_c)
            karilist_a([vlist[now_ran][0],vlist[now_ran][1],vlist[now_ran][2]])
        with open(folder_path + siteurl + "/ajax/music-top/mct-" + str(r) + ".json","w") as f:
            json.dump({"index":karilist},f)

def music_modify_update():
    cur.execute("UPDATE MUSIC_SONG_DB SET CLEATE_PAGE_DATE = SYSDATE + 9/24 WHERE CLEATE_PAGE_DATE is null")
    #数が変わったところに最新の日時(utc+9)を追加
    cur.execute("UPDATE MUSIC_SONG_DB msd SET LAST_MODIFIED = SYSDATE + 9/24 WHERE msd.CONTENT_COUNT != (SELECT COUNT(1) FROM VIDEO_ID vid WHERE vid.MUSIC_NAME = msd.KEY_MUSIC_NAME AND ig = 0)")
    #その後にカウントの値を更新
    cur.execute("UPDATE MUSIC_SONG_DB msd SET CONTENT_COUNT = (SELECT COUNT(1) FROM VIDEO_ID vid WHERE msd.KEY_MUSIC_NAME = vid.music_name and ig = 0)")
    con.commit()#変更を保存

def ch_modify_update():
    cur.execute("UPDATE CH_ID SET CLEATE_PAGE_DATE = SYSDATE + 9/24 WHERE CLEATE_PAGE_DATE is null and ig = 0")
    #実行時間長すぎ　効率化したプルリクエスト待ってます
    cur.execute("UPDATE CH_ID chi SET LAST_MODIFIED = SYSDATE + 9 / 24 WHERE chi.CONTENT_COUNT != (select count(1) from video_id vid where video_id in (select video_id from video_id where IG = 0 AND CHANNEL_ID = chi.ch_id UNION SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 0 AND GROUPE_NAME in (SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0))) UNION (select video_id from video_id where channel_id = chi.LINK)) and music_name is not null)")
    cur.execute("UPDATE CH_ID chi SET CONTENT_COUNT = (select count(1) from video_id vid where video_id in (select video_id from video_id where IG = 0 AND CHANNEL_ID = chi.ch_id UNION SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 0 AND GROUPE_NAME in (SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0))) UNION (select video_id from video_id where channel_id = chi.LINK)) and music_name is not null)")
    con.commit()

def onlydate_time(datetime_obj):
    return str(datetime_obj.year) + "-" + str(datetime_obj.month) + "-" + str(datetime_obj.day)

def makesitemap():#もちろん5万件以上対応
    #urlの配列を作成およびトップページ等の特殊ページも追加
    urllist = [[f"https://{siteurl}/",default_modify_time],[f"https://{siteurl}/today/",onlydate_time(datetime.datetime.now())],[f"https://{siteurl}/search/",default_modify_time]]
    urllist_a = urllist.append

    cur.execute("SELECT NICK_NAME_1,TO_CHAR(LAST_MODIFIED,'YYYY-MM-DD') FROM CH_ID WHERE IG = 0")
    kalist = cur.fetchall()
    for x in kalist:
        urllist_a([f"https://{siteurl}/ch/{dir_name_replace(x[0])}",x[1]])
    cur.execute("SELECT KEY_MUSIC_NAME,TO_CHAR(LAST_MODIFIED,'YYYY-MM-DD') FROM MUSIC_SONG_DB")
    kalist = cur.fetchall()
    for x in kalist:
        urllist_a([f"https://{siteurl}/music/{dir_name_replace(x[0])}",x[1]])
    
    for x in range(math.ceil(float(len(urllist)/50000))):
        urlset = ET.Element('urlset')
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        tree = ET.ElementTree(element=urlset)
        if x+1==math.ceil(float(len(urllist)/50000)):#ループ回数を計算
            nowloop = len(urllist) - 50000*x
        else:
            nowloop = 50000
        for nurlist_c in range(nowloop):
            url_element = ET.SubElement(urlset, 'url')
            loc = ET.SubElement(url_element, 'loc')
            loc.text = urllist[nurlist_c][0]
            lastmod = ET.SubElement(url_element, 'lastmod')
            lastmod.text = urllist[nurlist_c][1]
        tree.write(folder_path + siteurl + f'/sitemap/sitemap{str(x)}.xml', encoding='utf-8', xml_declaration=True)
    
    #sitemap_index作成
    sitemapindex = ET.Element('sitemapindex')
    sitemapindex.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.ElementTree(element=sitemapindex)
    for r in range(x+1):
        sitemap_el = ET.SubElement(sitemapindex,"sitemap")
        loc = ET.SubElement(sitemap_el, "loc")
        loc.text = f"https://{siteurl}/sitemap/sitemap{str(r)}.xml"
    tree.write(folder_path + siteurl + "/sitemap_index.xml",encoding='utf-8', xml_declaration=True)

def yt_status_ex():#0なら見れる1なら見れない
    cur.execute("UPDATE VIDEO_ID vid SET STATUS = 1 WHERE NOT EXISTS(SELECT 1 FROM VIDEO_V_DATA vvd WHERE vvd.RELOAD_TIME > SYSDATE-1 AND vvd.VIDEO_ID = vid.VIDEO_ID)")
    cur.execute("UPDATE VIDEO_ID vid SET STATUS = 0 WHERE EXISTS(SELECT 1 FROM VIDEO_V_DATA vvd WHERE vvd.RELOAD_TIME > SYSDATE-1 AND vvd.VIDEO_ID = vid.VIDEO_ID)")
    con.commit()

def office_hot():
    #まずは箱リスト作成
    cur.execute("select distinct BELONG_OFFICE from CH_ID chi where exists(select 1 from VIDEO_ID vid where vid.CHANNEL_ID = chi.CH_ID) and chi.BELONG_OFFICE IS NOT NULL")
    video_office_list = [x[0] for x in cur.fetchall()]
    video_office_list.insert(0,"全体")
    with open(folder_path + siteurl + "/api/today/index_list.json","w") as f:
        json.dump({"index":video_office_list},f)
    #箱リストをもとに本番実装
    video_office_list.remove("全体")
    nowday_d = datetime.date.today()
    for r in video_office_list:
        #なんかこのSQL動作遅いんです　プルリクエスト待ってます でもなんかexists->inにしたら100倍早くなった なんで？
        cur.execute("SELECT VIDEO_ID, (SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID) video_name, RELOAD_TIME, NVL(NULLIF((VIEW_C - lag(VIEW_C, 1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0) / NULLIF((lag(VIEW_C, 1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME) - lag(VIEW_C, 2) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0), - 1000) - 1 DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE - 3 AND exists(select * from VIDEO_ID vid where ig = 0 and vvd.VIDEO_ID = vid.VIDEO_ID) AND vvd.VIDEO_ID in (select VIDEO_ID from video_id vid where exists (select * from ch_id chi where vid.CHANNEL_ID = chi.CH_ID and chi.BELONG_OFFICE = :office_name) or exists (select * from PAIR_LIST_SECOND pls where vid.GROUPE_NAME = pls.GROUPE_NAME and (exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and (pls.MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)))))) or exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and vid.CHANNEL_ID = chi.LINK)) ORDER BY RELOAD_TIME DESC, DIFF DESC FETCH FIRST 100 ROWS ONLY",office_name=r)
        kalist = cur.fetchall()
        rank_list_a = []
        vidlist_a = []
        for i in kalist:
            if i[2].date()==nowday_d and i[3] > 0:
                rank_list_a.append([i[0],i[1],math.floor(i[3]*100)])
                vidlist_a.append(i[0])
        sub_rankilist = []
        sub_vidlist = []
        diff_list = [[1,"daydiff"],[7,"weekdiff"],[30,"monthdiff"]]
        for n in diff_list:
            cur.execute("SELECT VIDEO_ID, (SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID), RELOAD_TIME, NVL(NULLIF((VIEW_C - lag(VIEW_C, :day_diff) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0), - 1) AS DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE - :day_diff_p AND exists(select * from VIDEO_ID vid where ig = 0 and vvd.VIDEO_ID = vid.VIDEO_ID) AND vvd.VIDEO_ID in (select VIDEO_ID from video_id vid where exists (select * from ch_id chi where vid.CHANNEL_ID = chi.CH_ID and chi.BELONG_OFFICE = :office_name) or exists (select * from PAIR_LIST_SECOND pls where vid.GROUPE_NAME = pls.GROUPE_NAME and (exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and (pls.MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)))))) or exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and vid.CHANNEL_ID = chi.LINK)) ORDER BY RELOAD_TIME DESC, DIFF DESC FETCH FIRST 100 ROWS ONLY",office_name=r,day_diff=n[0],day_diff_p=n[0]+1)
            kalist = cur.fetchall()
            rank_list = []
            vidlist_s = []
            for i in kalist:
                if i[2].date()==nowday_d and i[3] > 0:
                    rank_list.append([i[0],i[1],i[3]])
                    vidlist_s.append(i[0])
            sub_rankilist.append(rank_list)
            sub_vidlist.append(vidlist_s)
        cur.execute("SELECT VIDEO_ID, (SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID), RELOAD_TIME, VIEW_C FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE - 1 AND exists(select * from VIDEO_ID vid where ig = 0 and vvd.VIDEO_ID = vid.VIDEO_ID) AND vvd.VIDEO_ID in (select VIDEO_ID from video_id vid where exists (select * from ch_id chi where vid.CHANNEL_ID = chi.CH_ID and chi.BELONG_OFFICE = :office_name) or exists (select * from PAIR_LIST_SECOND pls where vid.GROUPE_NAME = pls.GROUPE_NAME and (exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and (pls.MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)))))) or exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and vid.CHANNEL_ID = chi.LINK)) ORDER BY RELOAD_TIME DESC, VIEW_C DESC FETCH FIRST 100 ROWS ONLY",office_name=r)
        kalist = cur.fetchall()
        rank_list_b = []
        vidlist_b = []
        for i in kalist:
            if i[2].date()==nowday_d and i[3] > 0:
                rank_list_b.append([i[0],i[1],i[3]])
                vidlist_b.append(i[0])
        with open(folder_path + siteurl + f"/api/today/{dir_name_replace(r)}.json","w") as f:
            json.dump({"index":[rank_list_a,sub_rankilist[0],sub_rankilist[1],sub_rankilist[2],rank_list_b],"vidlist":[vidlist_a,sub_vidlist[0],sub_vidlist[1],sub_vidlist[2],vidlist_b]},f)

def groupname_slash():
    cur.execute("select GROUPE_NAME from PAIR_LIST_SECOND where GROUPE_NAME LIKE '%/%' and MN_1 is null and ig = 0")#まだ入力がなされていないスラッシュ付きのやつを抽出
    k_now_slasher_list = cur.fetchall()
    if k_now_slasher_list==[]:
        print("no-srash")
        return
    now_slasher_list = [t[0] for t in k_now_slasher_list]
    for r in now_slasher_list:
        slash_list = str(r).split("/")
        k_now_mnlist = [["MN_"+str(y+1),"'"+slash_list[y]+"'"] for y in range(len(slash_list))]
        now_mnlist = []
        for q in k_now_mnlist:
            now_mnlist.append("=".join(q))
        cur.execute(f"UPDATE PAIR_LIST_SECOND SET {','.join(now_mnlist)} WHERE GROUPE_NAME = '{r}'")
    con.commit()

def remove_topic():
    cur.execute("UPDATE CH_ID set ig = 1 where NAM like '%Topic%'")
    con.commit()

def igch_tig():#無視するチャンネル上がっていてグループ名が設定されていないものを一時無視に追加
    cur.execute("update VIDEO_ID vid set ig = 2 where exists(select * from CH_ID chi where ig = 1 and chi.CH_ID=vid.CHANNEL_ID) and vid.GROUPE_NAME is null and ig = 0")
    con.commit()

def make_api_latestmovie():
    cur.execute("SELECT VIDEO_ID,VIDEO_NAME FROM VIDEO_ID WHERE IG = 0 OR IG = 2 ORDER BY UPLOAD_TIME DESC FETCH FIRST 20 ROWS ONLY")
    kalist = [[x[0],x[1]] for x in cur.fetchall()]
    with open(folder_path + siteurl + "/api/latest.json","w") as f:
        json.dump({"index":kalist},f)

make_chpage_v3("ときのそら")