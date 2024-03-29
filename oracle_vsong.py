import math,os,cx_Oracle,requests,datetime,collections,urllib.parse,json,random,jaconv,shutil,itertools,MySQLdb,sys,copy,webbrowser,pytube,xmljson,regex,re
import subprocess
from pykakasi import kakasi
import get_youtube_data as gy
import music_data as md
import ev
import xml.etree.ElementTree as ET
import pytube_search_channel as psc

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
header = """<div id="yt_pl_idel" class="yt_viewpl dis_none"><group id="radio-sidebar" class="inline-radio" onchange="sidebar_info()"><div class="radio-page-div"><input id="radio-side-pl" class="radio-page-select" type="radio" name="vs-sidebar" checked><label class="radio-page-label">プレイリスト</label></div><div class="radio-page-div"><input id="radio-side-wh" class="radio-page-select" type="radio" name="vs-sidebar"><label class="radio-page-label">視聴履歴</label></div></group><div id="yt_playlist_view_p" class="yt_viewpl_list"></div></div><header><h2 class="Top"><a href="/" onClick='page_ajax_load("/");return false'>VtuberSing</a></h2><nav class="header-nav"><ul><li><a href="/search/" onClick='page_ajax_load("/search/");return false'>検索</a><li><a href="/today/" onClick='page_ajax_load("/today/");return false'>今日の人気</a></ul></nav></header>"""
music_control_html = """<hr><div class="sticky_c_yt pos-none" id="ytembed"><div id="youtube-iframe"></div></div><span class="sticky_c dis_none" id="control_panel"><progress class="yt-progress" id="yt-player-time" max="100" value="0"></progress><div class="flex_box"><div class="beside_gr"><div class="beside_gr_in" id="music_name_display"></div></div><div class="play_center"><button id="yt-playbt" onclick="yt_playorstop()" class="bt_noborder" title="再生"><img class="control_icon" src="/util/playbtn.svg"></button><button onclick="yt_skip()" title="スキップ" class="bt_noborder"><img class="control_icon" src="/util/skipbt.svg"></button><input title="音量を調節" type="range" id="yt_sound_volume" min="0" max="100" value="100" onchange="yt_volume_change()"><button id="yt_display" onclick="yt_display()">表示</button><button id="yt_ch_dismode" onclick='yt_watchmode_ch()' title="大画面で表示" class="bt_noborder"><img class="control_icon" src="/util/bigwindow.svg"></button><input id="autoload_check" type="checkbox"><button type="button" class="bt_noborder shuffle" onclick="yt_pl_shuffle()"><img class="control_icon" src="/util/shafulbt.svg"></button><button type="button" class="bt_noborder" onclick="open_playlist()"><img id="imgupdown_bt" class="control_icon" src="/util/updownbt.svg"></button></div></div></span>"""
html_import_lib = '<link rel="stylesheet" href="/library/main.css"><script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script><script defer src="https://www.youtube.com/iframe_api"></script><script defer src="https://cdn.jsdelivr.net/npm/instant.page@5.1.0/instantpage.min.js"></script><script src="https://cdn.jsdelivr.net/npm/ismobilejs@1.1.1/dist/isMobile.min.js"></script><script src="https://cdn.jsdelivr.net/npm/dexie@3.2.2/dist/dexie.min.js"></script>'
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
    shutil.copy2("jslibrary/vdata.cpp",cgi_bin_dir + "/cgi-bin/vdata.cpp")
    shutil.copy2("jslibrary/vdata_query_post.cpp",cgi_bin_dir + "/cgi-bin/vdata_query_post.cpp")

def ps_lib():#ライブラリのデータを本番環境から移す
    shutil.copy2(folder_path + siteurl + "/library/main.js","jslibrary/main.js")
    shutil.copy2(folder_path + siteurl + "/library/main.css","jslibrary/main.css")
    shutil.copy2(folder_path + siteurl + "/cgi-bin/search.cpp","jslibrary/search.cpp")
    shutil.copy2(folder_path + siteurl + "/cgi-bin/vdata.cpp","jslibrary/vdata.cpp")
    shutil.copy2(folder_path + siteurl + "/cgi-bin/vdata_query_post.cpp","jslibrary/vdata_query_post.cpp")

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
    #変形
    v_id_l = [e[0] for e in cur.fetchall()]
    v_st = gy.ExtremeVideoToStatics(v_id_l)
    dt_now = datetime.datetime.now()
    dt_str = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day) + " " + str(dt_now.hour) + ":" + str(dt_now.minute) + ":" + str(dt_now.second)
    for x in range(len(v_st)):
        #cur.execute("INSERT INTO VIDEO_V_DATA (VIDEO_ID,RELOAD_TIME,VIEW_C,LIKE_C,COMMENT_C) VALUES(:vid,:ndt,:vc,:lc,:cc)",vid=v_st[x[0]],ndt=dt_str,vc=str(v_st[x[1]]),lc=str(v_st[x][2]),cc=str(v_st[x][3]))
        cur.execute("INSERT INTO VIDEO_V_DATA (VIDEO_ID,RELOAD_TIME,VIEW_C,LIKE_C,COMMENT_C) VALUES('" + v_st[x][0] + "','" + dt_str + "','" + str(v_st[x][1]) + "','" + str(v_st[x][2]) + "','" + str(v_st[x][3]) + "')")
    con.commit()

def get_song_title(raw_title: str) -> str:
    title = ""
    # 「作品名」より【楽曲タイトル】 というパターンがあるので、その場合は【】の中身をタイトルとする
    if "より【" in raw_title:
        title = raw_title[raw_title.find("【") + 1: raw_title.find("】")+1]
    else:
        title = raw_title

    # ヘッダー的に記号がついていたら削除する
    if title[0] == '★':
        title = title[1:]

    # ()（）[]【】を除外する。左が半角で右が全角だったりすることもある
    title = regex.sub(r"[【（《\(\[].+?[】）》\)\]]", "", title)

    # 「作品名」主題歌 などのパターンの場合は、その部分を消す
    keywords = ["主題歌", "OP", "CMソング"]
    for keyword in keywords:
        if "」" + keyword in title:
            end_index = title.find("」" + keyword)+1
            for start_index in range(end_index, -1, -1):
                if title[start_index] == '「':
                    title = title[:start_index] + title[end_index + len(keyword) + 1:]
                    break

    for keyword in keywords:
        if "』" + keyword in title:
            end_index = title.find("』" + keyword)+1
            for start_index in range(end_index, -1, -1):
                if title[start_index] == '『':
                    title = title[:start_index] + title[end_index + len(keyword) + 1:]
                    break

    # 「」と『』がある場合、その中の文字列を取り出す
    # ただし、稀に「」の中に自分の名前を入れている場合がある。その場合は無視する
    if "「" in title and "」" in title:
        temp_title = title[title.find("「") + 1: title.find("」")+1]
        keyword_status = True
        for keyword in keywords:
            if keyword in temp_title:
                keyword_status = False
                break
        if keyword_status and "cover" not in temp_title:
            title = temp_title

    if "『" in title and "』" in title:
        temp_title = title[title.find("『") + 1: title.find("』")+1]
        keyword_status = True
        for keyword in keywords:
            if keyword in temp_title:
                keyword_status = False
                break
        if keyword_status and "cover" not in temp_title:
            title = temp_title

    # 歌ってみた以降の文字列を消す
    title = regex.sub(r"多重人格で歌ってみた.*", "", title)
    title = regex.sub(r"コラボ歌ってみた.*", "", title)
    title = regex.sub(r"歌って踊ってみた.*", "", title)
    title = regex.sub(r"を歌ってみた.*", "", title)
    title = regex.sub(r"歌ってみた.*", "", title)

    # cover, covered, covered by 以降の文字列を消す
    title = regex.sub(r"[cC]over(ed)?( by)?.*", "", title)
    title = regex.sub(r"[fF]eat.*", "", title)  # featがある場合がある

    # 描いて歌ってみた系対策
    title = regex.sub(r"描いて.*", "", title)

    # /以降は削除する
    if "/" in title:
        title = title[:title.find("/")+1]
    if "／" in title:
        title = title[:title.find("／")+1]

    # - があったらその後ろを消す
    title = title[:title.find("-")+1]

    if title.startswith("MV") and len(title) >= 2:
        title = title[2:]
    else:
        # MV平置き対策
        title = regex.sub(r"MV.*", "", title)

    title = regex.sub(r"music\s*video", "", title, flags=regex.IGNORECASE)
    title = title.strip()  # 前後空白対策

    if title == "" and len(raw_title) <= 10:
        # 曲名の中央値は8 対してタイトルの中央値は35この文字数でポカする確率は約10/7000で0.14%と非常に低いので一般的に曲名と同じであると考えられる
        title = raw_title

    return title

def correct_video_list(fetchall=False):
    #先にプレミア関係をすることで処理量を削減
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 3")#プレミア用一次処理したのを抽出
    kalist = cur.fetchall()
    if len(kalist)!=0:#プレミア用の何かがあった->ステータス取得
        now_list = [x[0] for x in kalist]
        v_data = gy.videoid_lToMInfo(now_list)
        for r in v_data:
            if r[6]==False:
                cur.execute("UPDATE VIDEO_ID SET IG = 2 WHERE VIDEO_ID = :nvidid",nvidid=r[0])
                con.commit()
    pid_l = diff_playlistid(fetchall=fetchall)
    if len(pid_l)==0:
        print("プレイリスト取得スキップ")
    else:
        print("プレイリスト取得中")
        cur.execute("SELECT VIDEO_ID FROM VIDEO_ID")
        v_id_l = [e[0] for e in cur.fetchall()]
        v_data = gy.videoid_lToMInfo(gy.highper_vidFromPlaylist(pid_l,v_id_l))
        kvar = 0
        if len(v_data) > 0:
            cur.execute("SELECT KEY_MUSIC_NAME FROM MUSIC_SONG_DB WHERE LENGTH(KEY_MUSIC_NAME) > 2")#3文字以上の文字だけ
            musiclist = [t[0] for t in cur.fetchall()]
            for x in range(len(v_data)):
                musicpt = []
                for n in musiclist:
                    if n in v_data[x][3]:
                        musicpt.append(n)
                musicpt.append(get_song_title(v_data[x][3]))
                musicpt.sort(key=len,reverse=True)#長いのを優先的に充てる
                if len(musicpt) > 0:
                    nowmusicpredict = musicpt[0]
                else:
                    nowmusicpredict = ""
                if v_data[x][0] not in v_id_l:#万が一の重複に備え更なる重複チェックをする
                    kvar += 1
                    #cur.execute(f"INSERT INTO VIDEO_ID (VIDEO_ID,CHANNEL_ID,UPLOAD_TIME,VIDEO_NAME,MOVIE_TIME) VALUES('{v_data[x][0]}','{v_data[x][1]}','{str(v_data[x][2])[:-1].replace('T',' ')}','{str(v_data[x][3]).replace('\'','\'\'')}','{v_data[x][5]}')")
                    if v_data[x][6]:
                        ig = 3
                    else:
                        ig = 2
                    cur.execute("INSERT INTO VIDEO_ID (VIDEO_ID,CHANNEL_ID,UPLOAD_TIME,VIDEO_NAME,MOVIE_TIME,IG,MUSIC_NAME) VALUES(:vid,:chid,:ut,:vname,:mt,:ign,:mn)",vid=v_data[x][0],chid=v_data[x][1],ut=str(v_data[x][2])[:-1].replace('T',' '),vname=v_data[x][3],mt=v_data[x][5],ign=ig,mn=nowmusicpredict)
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
    cur.execute("INSERT INTO PAIR_LIST_SECOND(GROUPE_NAME) SELECT distinct NVL(GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) FROM VIDEO_ID vid WHERE NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) IS NOT NULL AND NOT EXISTS (SELECT 'X' FROM PAIR_LIST_SECOND pls WHERE pls.GROUPE_NAME = NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)))")
    con.commit()

def groupe_name2men_namev2(groupe_name):#v2のテーブルにアクセス
    try:
        cur.execute("select MN from (select TO_CHAR(MN_1) AS MN from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_2) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_3) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_4) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_5) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_6) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_7) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_8) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_9) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_10) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_11) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_12) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_13) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_14) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_15) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_16) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_17) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_18) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_19) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_20) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_21) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_22) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_23) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_24) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_25) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_26) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_27) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_28) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select TO_CHAR(MN_29) from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_30 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_31 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_32 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_33 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_34 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_35 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_36 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_37 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_38 from PAIR_LIST_SECOND where groupe_name = :group_name UNION ALL select MN_39 from PAIR_LIST_SECOND where groupe_name = :group_name) mt where exists(select * from ch_id chi where chi.ig = 0 and mt.MN in (chi.NICK_NAME_1,chi.NICK_NAME_2))",group_name=groupe_name)
        songer_list = [r[0] for r in cur.fetchall()]
        return songer_list
    except:
        pro_log("error","groupe_name2men_namev2",groupe_name,"unknown error->continue")

def add_music_data():
    cur.execute("SELECT DISTINCT MUSIC_NAME FROM VIDEO_ID WHERE MUSIC_NAME IS NOT NULL AND MUSIC_NAME NOT IN (SELECT KEY_MUSIC_NAME FROM MUSIC_SONG_DB WHERE KEY_MUSIC_NAME IS NOT NULL)")
    k_rec_mlist = cur.fetchall()
    if len(k_rec_mlist)==0:
        return
    for x in range(len(k_rec_mlist)):
        nx = str(k_rec_mlist[x])[2:-3]
        cur.execute("select 1 from MUSIC_SONG_DB where KEY_MUSIC_NAME = :nmn",nmn=nx)
        if cur.fetchone()==None:
            n_music_reslist = md.search_music(nx)#検索
            cur.execute("INSERT INTO MUSIC_SONG_DB (KEY_MUSIC_NAME,MUSIC_NAME_SP,MUSIC_NAME_YT,ARTIST_NAME,SP_ID,YT_ID) VALUES(:nkmn,:spmn,:ytmn,:artname,:spid,:ytid)",nkmn=nx,spmn=n_music_reslist[0],ytmn=n_music_reslist[1],artname=n_music_reslist[2],spid=n_music_reslist[3],ytid=n_music_reslist[4])
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
        cur.execute("SELECT DISTINCT NVL(vid.GROUPE_NAME,(SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) FROM VIDEO_ID vid WHERE NOT EXISTS ( SELECT GROUPE_NAME FROM PAIR_LIST_SECOND pls WHERE NVL(vid.GROUPE_NAME,(SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID))=pls.GROUPE_NAME) AND GROUPE_NAME IS NOT NULL")
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
        cur.execute("SELECT DISTINCT MN FROM FLAT_PAIRLIST_SECOND fps WHERE NOT EXISTS(SELECT 1 FROM CH_ID chi WHERE (fps.MN = chi.NICK_NAME_1 OR fps.MN = chi.NICK_NAME_2))")
        not_submit_nickname_list = [y[0] for y in cur.fetchall()]
        for t in not_submit_nickname_list:
            print(t + "はデータベースに登録されていません at pairlist or ch_id")
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
    elif data==2:
        k_array = [None,label,data_v,data_l,data_c]
        return k_array

def view_ch_graph(nick_name):
    cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'), SUM(VIEW_C), SUM(LIKE_C), SUM(COMMENT_C) FROM VIDEO_V_DATA WHERE VIDEO_ID IN (select video_id from video_id where video_id in (select video_id from video_id where IG = 0 AND CHANNEL_ID = (SELECT CHANNEL_ID FROM CH_ID WHERE (NICK_NAME_1 = :menl OR NICK_NAME_2 = :menl) AND IG = 0) UNION ALL SELECT VIDEO_ID FROM VIDEO_ID vid WHERE IG = 0 AND NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) in (SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 in (:menl) OR MN_2 in (:menl) OR MN_3 in (:menl) OR MN_4 in (:menl) OR MN_5 in (:menl) OR MN_6 in (:menl) OR MN_7 in (:menl) OR MN_8 in (:menl) OR MN_9 in (:menl) OR MN_10 in (:menl) OR MN_11 in (:menl) OR MN_12 in (:menl) OR MN_13 in (:menl) OR MN_14 in (:menl) OR MN_15 in (:menl) OR MN_16 in (:menl) OR MN_17 in (:menl) OR MN_18 in (:menl) OR MN_19 in (:menl) OR MN_20 in (:menl) OR MN_21 in (:menl) OR MN_22 in (:menl) OR MN_23 in (:menl) OR MN_24 in (:menl) OR MN_25 in (:menl) OR MN_26 in (:menl) OR MN_27 in (:menl) OR MN_28 in (:menl) OR MN_29 in (:menl) OR MN_30 in (:menl) OR MN_31 in (:menl) OR MN_32 in (:menl) OR MN_33 in (:menl) OR MN_34 in (:menl) OR MN_35 in (:menl) OR MN_36 in (:menl) OR MN_37 in (:menl) OR MN_38 in (:menl) OR MN_39 in (:menl)) UNION ALL select video_id from video_id where channel_id in (select CH_ID from CH_ID where LINK = (SELECT CHANNEL_ID FROM CH_ID WHERE (NICK_NAME_1 = :menl OR NICK_NAME_2 = :menl) AND IG = 0))) and music_name is not null AND STATUS = 0) AND RELOAD_TIME >= (CURRENT_DATE - 7) GROUP BY RELOAD_TIME ORDER BY RELOAD_TIME ASC",menl=nick_name)
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
    try:
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
    except:
        for x in tnlist:
            try:
                xml = requests.get("https://rsshub.app/twitter/user/" + x + "?limit=1")
                xml_parse = ET.fromstring(xml.text)
                pic_url = xmljson.yahoo.data(xml_parse)["rss"]["channel"]["image"]["url"]
                cur.execute("update CH_ID set PICTURE_URL='" + pic_url + "' where TWITTER_NAME='" + x + "'")
                con.commit()
            except:
                pass

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

def beta_add_videotime():
    cur.execute("select VIDEO_ID from VIDEO_ID where MOVIE_TIME is null and STATUS = 0")#必要なカラムを取得
    nowls = [x[0] for x in cur.fetchall()]
    kalist = gy.videoid_lToMInfo(nowls)
    for x in kalist:
        cur.execute("UPDATE VIDEO_ID SET MOVIE_TIME = :mtlong WHERE VIDEO_ID = :nvid",nvid=x[0],mtlong=x[5])
        con.commit()

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
    cur.execute("SELECT CH_ID,NICK_NAME_1 FROM CH_ID WHERE ig = 0 and nick_name_1 is not null and NAM not like '%Topic%' and EXISTS (SELECT DISTINCT CHANNEL_ID FROM VIDEO_ID WHERE IG = 0 AND STATUS = 0 AND GROUPE_NAME IS NULL and CH_ID.CH_ID = CHANNEL_ID)")#一人で歌っているチャンネルを取得
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
    cur.execute("SELECT DISTINCT NVL(vid.GROUPE_NAME,(SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) FROM VIDEO_ID vid WHERE IG = 0 AND STATUS = 0 AND NVL(vid.GROUPE_NAME,(SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) IS NOT NULL")#使われているgroupe name抽出
    gname_v = cur.fetchall()
    for n_gn in gname_v:
        now_gname = str(n_gn)[2:-3]
        now_g_list = groupe_name2men_namev2(now_gname)
        cur.execute("SELECT VIDEO_ID,MUSIC_NAME FROM VIDEO_ID vid WHERE NVL(vid.GROUPE_NAME,(SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) = :gname AND IG = 0 AND STATUS = 0",gname=now_gname)
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
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID WHERE STATUS = 0 AND IG IN (0,2)")
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
    con.commit()
    #数が変わったところに最新の日時(utc+9)を追加
    cur.execute("UPDATE MUSIC_SONG_DB msd SET LAST_MODIFIED = SYSDATE + 9/24 WHERE msd.CONTENT_COUNT != (SELECT COUNT(1) FROM VIDEO_ID vid WHERE vid.MUSIC_NAME = msd.KEY_MUSIC_NAME AND ig = 0)")
    con.commit()
    #その後にカウントの値を更新
    cur.execute("UPDATE MUSIC_SONG_DB msd SET CONTENT_COUNT = (SELECT COUNT(1) FROM VIDEO_ID vid WHERE msd.KEY_MUSIC_NAME = vid.music_name and ig = 0)")
    con.commit()#変更を保存

def ch_modify_update():
    cur.execute("UPDATE CH_ID SET CLEATE_PAGE_DATE = SYSDATE + 9/24 WHERE CLEATE_PAGE_DATE is null and ig = 0")
    con.commit()
    #実行時間長すぎ　効率化したプルリクエスト待ってます
    cur.execute("UPDATE CH_ID chi SET LAST_MODIFIED = SYSDATE + 9 / 24 WHERE chi.CONTENT_COUNT != (select count(1) from video_id vid where video_id in (select video_id from video_id where IG = 0 AND CHANNEL_ID = chi.ch_id UNION SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 0 AND NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) in (SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0))) UNION (select video_id from video_id where channel_id = chi.LINK)) and music_name is not null)")
    con.commit()
    cur.execute("UPDATE CH_ID chi SET CONTENT_COUNT = (select count(1) from video_id vid where video_id in (select video_id from video_id where IG = 0 AND CHANNEL_ID = chi.ch_id UNION SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 0 AND NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) in (SELECT GROUPE_NAME FROM PAIR_LIST_SECOND WHERE MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) OR MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0))) UNION (select video_id from video_id where channel_id = chi.LINK)) and music_name is not null)")
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
    con.commit()
    cur.execute("UPDATE VIDEO_ID vid SET STATUS = 0 WHERE EXISTS(SELECT 1 FROM VIDEO_V_DATA vvd WHERE vvd.RELOAD_TIME > SYSDATE-1 AND vvd.VIDEO_ID = vid.VIDEO_ID)")
    con.commit()

def office_hot():
    #まずは箱リスト作成
    cur.execute("SELECT BELONG_OFFICE FROM CH_ID WHERE IG = 0 AND BELONG_OFFICE IS NOT NULL GROUP BY BELONG_OFFICE ORDER BY SUM(CONTENT_COUNT) DESC")#順番を動画数の多い順に
    video_office_list = [x[0] for x in cur.fetchall()]
    video_office_list.insert(0,"全体")
    with open(folder_path + siteurl + "/api/today/index_list.json","w") as f:
        json.dump({"index":video_office_list},f)
    #箱リストをもとに本番実装
    video_office_list.remove("全体")
    nowday_d = datetime.date.today()
    for r in video_office_list:
        #なんかこのSQL動作遅いんです　プルリクエスト待ってます でもなんかexists->inにしたら100倍早くなった なんで？
        #前日比上昇率
        cur.execute("SELECT VIDEO_ID, (SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID) video_name, RELOAD_TIME, NVL(NULLIF((VIEW_C - lag(VIEW_C, 1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0) / NULLIF((lag(VIEW_C, 1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME) - lag(VIEW_C, 2) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0), - 1000) - 1 DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE - 3 AND exists (select * from VIDEO_ID vid where ig = 0 and vvd.VIDEO_ID = vid.VIDEO_ID) AND vvd.VIDEO_ID in (select VIDEO_ID from video_id vid where exists (select * from ch_id chi where vid.CHANNEL_ID = chi.CH_ID and chi.BELONG_OFFICE = :office_name) or exists (select * from PAIR_LIST_SECOND pls where NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) = pls.GROUPE_NAME and (exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and (pls.MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)))))) or exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and vid.CHANNEL_ID = chi.LINK)) ORDER BY RELOAD_TIME DESC, DIFF DESC FETCH FIRST 100 ROWS ONLY",office_name=r)
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
            cur.execute("SELECT VIDEO_ID, (SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID), RELOAD_TIME, NVL(NULLIF((VIEW_C - lag(VIEW_C, :day_diff) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0), - 1) AS DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE - :day_diff_p AND exists (select * from VIDEO_ID vid where ig = 0 and vvd.VIDEO_ID = vid.VIDEO_ID) AND vvd.VIDEO_ID in (select VIDEO_ID from video_id vid where exists (select * from ch_id chi where vid.CHANNEL_ID = chi.CH_ID and chi.BELONG_OFFICE = :office_name) or exists (select * from PAIR_LIST_SECOND pls where NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) = pls.GROUPE_NAME and (exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and (pls.MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)))))) or exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and vid.CHANNEL_ID = chi.LINK)) ORDER BY RELOAD_TIME DESC, DIFF DESC FETCH FIRST 100 ROWS ONLY",office_name=r,day_diff=n[0],day_diff_p=n[0]+1)
            kalist = cur.fetchall()
            rank_list = []
            vidlist_s = []
            for i in kalist:
                if i[2].date()==nowday_d and i[3] > 0:
                    rank_list.append([i[0],i[1],i[3]])
                    vidlist_s.append(i[0])
            sub_rankilist.append(rank_list)
            sub_vidlist.append(vidlist_s)
        #全期間
        cur.execute("SELECT VIDEO_ID, (SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID), RELOAD_TIME, VIEW_C FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE - 1 AND exists (select * from VIDEO_ID vid where ig = 0 and vvd.VIDEO_ID = vid.VIDEO_ID) AND vvd.VIDEO_ID in (select VIDEO_ID from video_id vid where exists (select * from ch_id chi where vid.CHANNEL_ID = chi.CH_ID and chi.BELONG_OFFICE = :office_name) or exists (select * from PAIR_LIST_SECOND pls where NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) = pls.GROUPE_NAME and (exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and (pls.MN_1 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_2 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_3 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_4 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_5 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_6 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_7 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_8 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_9 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_10 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_11 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_12 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_13 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_14 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_15 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_16 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_17 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_18 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_19 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_20 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_21 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_22 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_23 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_24 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_25 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_26 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_27 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_28 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_29 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_30 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_31 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_32 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_33 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_34 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_35 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_36 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_37 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_38 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)) or pls.MN_39 in (chi.NICK_NAME_1, NVL(chi.NICK_NAME_2, 0)))))) or exists (select * from CH_ID chi where chi.BELONG_OFFICE = :office_name and vid.CHANNEL_ID = chi.LINK)) ORDER BY RELOAD_TIME DESC, VIEW_C DESC FETCH FIRST 100 ROWS ONLY",office_name=r)
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
    slashlist = ["/","、"]
    for n_slash in slashlist:
        cur.execute(f"select GROUPE_NAME from PAIR_LIST_SECOND where GROUPE_NAME LIKE '%{n_slash}%' and MN_1 is null and ig = 0")#まだ入力がなされていないスラッシュ付きのやつを抽出
        k_now_slasher_list = cur.fetchall()
        if k_now_slasher_list==[]:
            print("no-srash")
            return
        now_slasher_list = [t[0] for t in k_now_slasher_list]
        for r in now_slasher_list:
            slash_list = str(r).split(n_slash)
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
    cur.execute("UPDATE VIDEO_ID VID SET IG = 2 WHERE EXISTS(SELECT * FROM CH_ID CHI WHERE IG = 1 AND CHI.CH_ID=VID.CHANNEL_ID) AND VID.GROUPE_NAME IS NULL AND IG = 0")
    con.commit()
    cur.execute("UPDATE VIDEO_ID VID SET IG = 0 WHERE EXISTS(SELECT * FROM CH_ID CHI WHERE IG = 1 AND CHI.CH_ID=VID.CHANNEL_ID) AND NVL(VID.GROUPE_NAME,(SELECT DEFAULT_GROUPE_NAME FROM CH_ID CHI WHERE CHI.CH_ID = VID.CHANNEL_ID)) IS NOT NULL AND IG = 2 AND VID.MUSIC_NAME IS NOT NULL")
    con.commit()
    cur.execute("UPDATE VIDEO_ID VID SET IG = 0 WHERE NOT EXISTS(SELECT * FROM CH_ID CHI WHERE IG = 1 AND CHI.CH_ID=VID.CHANNEL_ID) AND IG = 2 AND VID.MUSIC_NAME IS NOT NULL")
    con.commit()
    cur.execute("update VIDEO_ID set ig = 0 where MUSIC_NAME is not null and GROUPE_NAME is null and ig = 4")
    con.commit()

def make_api_latestmovie():
    cur.execute("SELECT VIDEO_ID,VIDEO_NAME FROM VIDEO_ID WHERE IG = 0 OR IG = 2 ORDER BY UPLOAD_TIME DESC FETCH FIRST 20 ROWS ONLY")
    kalist = [[x[0],x[1]] for x in cur.fetchall()]
    with open(folder_path + siteurl + "/api/latest.json","w") as f:
        json.dump({"index":kalist},f)

def playlist_ignore_auto():
    cur.execute("update CRAWLER_PLAYLIST set ig = 1 where PLAYLIST_ID like 'OL%'")
    con.commit()

def diff_playlistid(force=False,fetchall=False):
    if force:
        cur.execute("SELECT PLAYLIST_ID,CONTENT_LENGTH FROM CRAWLER_PLAYLIST")
    else:
        cur.execute("SELECT PLAYLIST_ID,CONTENT_LENGTH FROM CRAWLER_PLAYLIST WHERE IG = 0")
    curcache = cur.fetchall()
    nowls = [x[0] for x in curcache]
    if fetchall==False:
        pldict = {}
        for r in curcache:
            pldict[r[0]] = r[1]
        nowdata = gy.playlist_count(nowls)
        difflist = []
        for r in nowdata:
            if r[1] != pldict[r[0]]:#値が違う!
                difflist.append(r[0])
                cur.execute("UPDATE CRAWLER_PLAYLIST SET CONTENT_LENGTH = :ncl WHERE PLAYLIST_ID = :npl",ncl=r[1],npl=r[0])
                con.commit()
    else:
        difflist = nowls
    return difflist

def get_song_title(raw_title):

    # 「作品名」より【楽曲タイトル】 というパターンがあるので、その場合は【】の中身をタイトルとする
    if "より【" in raw_title:
        title = raw_title.split("【")[1].split("】")[0]
    else:
        title = raw_title

    # ヘッダー的に記号がついていたら削除する
    if title[0] == "★":
        title = title[1:]

    # ()（）[]【】を除外する。左が半角で右が全角だったりすることもある
    title = re.sub("[<【（《\(\[].+?[】）》〉\)\]>]"," ",title)

    # 「作品名」主題歌 などのパターンの場合は、その部分を消す
    for keyword in ["主題歌", "OP", "CMソング","オリジナル曲"]:
        if "」{}".format(keyword) in title:
            end_index = title.index("」{}".format(keyword))
            for start_index in range(end_index, -1, -1):
                if title[start_index] == "「":
                    title = title[:start_index] + title[end_index + len(keyword) + 1:]
                    break

    for keyword in ["主題歌", "OP", "CMソング","オリジナル曲"]:
        if "』{}".format(keyword) in title:
            end_index = title.index("』{}".format(keyword))
            for start_index in range(end_index, -1, -1):
                if title[start_index] == "『":
                    title = title[:start_index] + title[end_index + len(keyword) + 1:]
                    break

    # 「」と『』がある場合、その中の文字列を取り出す
    # ただし、稀に「」の中に自分の名前を入れている場合がある。その場合は無視する
    if "「" in title and "」" in title:
        temp_title = title = title.split("「")[1].split("」")[0]
        if "cover" not in temp_title.lower():
            title = temp_title

    if "『" in title and "』" in title:
        temp_title = title.split("『")[1].split("』")[0]
        if "cover" not in temp_title.lower():
            title = temp_title

    # 歌ってみた以降の文字列を消す
    title = re.sub("を歌ってみた.*"," ", title)
    title = re.sub("歌ってみた.*"," ", title)

    title = re.sub("描いて.*"," ", title)

    # cover, covered, covered by 以降の文字列を消す
    title = re.sub("[cC]over(ed)?( by)?.*", "", title)
    title = re.sub("[Ff]eat.*", "", title)

    title = re.sub("[Mm]usic[ 　s][Vv]ideo","",title)

    # /以降は削除する
    if "/" in title:
        title = title.split("/")[0]

    if "／" in title:
        title =  title.split("／")[0]

    # - があったらその後ろを消す
    title = title.split("-")[0]

    # コラボメンバーを×で表現している部分を消す
    # #012 的な表現を消す
    title_part_list = []
    for title_part in title.split(" "):
        if "×" not in title_part and not re.fullmatch("#[0-9]+", title_part):
            title_part_list.append(title_part)
    title = " ".join(title_part_list)

    if(title.find("MV")==0):
        title = title[2:]
    else:
        title = re.sub("MV.*","",title)

    # 前後の空白を削除
    title = title.strip()

    return title

def music_helper():#曲名が長いやつに引っ張られるようになってる　ぽとかだと簡単に引っかかっちゃう
    igch_tig()
    cur.execute("SELECT KEY_MUSIC_NAME FROM MUSIC_SONG_DB")
    musiclist = [str(x[0]) for x in cur.fetchall()]
    cur.execute("SELECT VIDEO_ID,VIDEO_NAME FROM VIDEO_ID WHERE IG = 2 AND MUSIC_NAME IS NULL")
    nowvideolist = [[x[0],str(x[1])] for x in cur.fetchall()]
    if len(nowvideolist)!=0:
        print(str(len(nowvideolist)) + "\t回分あるから頑張れ!")
        for r in range(len(nowvideolist)):
            nvidname = nowvideolist[r][1]
            nvidid = nowvideolist[r][0]
            musicpt = []
            #for n in musiclist:
                #if n in nvidname:
                    #musicpt.append(n)
            musicpt.append(get_song_title(nvidname))
            musicpt.sort(key=len,reverse=True)
            if len(musicpt)>0:
                print("動画id: " + nvidid + "\n動画名: " + nvidname + "\n推測される音楽名: " + musicpt[0] + "\n\nOK->y or 空白\tNo->n\tig->ii\tコラボカツ入力良し->c\tまちがい->音楽名を入力\n\n")
            else:
                print("動画id: " + nvidid + "\n動画名: " + nvidname + "\n\n音楽名を入力\n\n")
            invalue = input("condition: ")
            invalue = invalue.lower()
            if invalue == "y" or invalue == "":
                cur.execute("UPDATE VIDEO_ID SET MUSIC_NAME = :nmn WHERE VIDEO_ID = :nvid",nmn = musicpt[0],nvid=nvidid)
                con.commit()
            elif invalue == "ii":
                cur.execute("UPDATE VIDEO_ID SET IG = 1 WHERE VIDEO_ID = :nvid",nvid=nvidid)
                con.commit()
            elif invalue == "n":
                pass
            elif invalue == "c":
                cur.execute("UPDATE VIDEO_ID SET IG = 4,MUSIC_NAME = :nmn WHERE VIDEO_ID = :nvid",nvid=nvidid,nmn = musicpt[0])
                con.commit()
            else:
                cur.execute("UPDATE VIDEO_ID SET MUSIC_NAME = :nmn WHERE VIDEO_ID = :nvid",nmn=invalue,nvid=nvidid)
                con.commit()
            con.commit()
    else:
        print("対象はありません")

def open_not_entered():
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 2 ORDER BY VIDEO_ID ASC")
    vidlist = [x[0] for x in cur.fetchall()]
    ret = input("本当に" + str(len(vidlist)) + "個のタブを開きますか？ Y/n")
    ret = ret.lower()
    if ret == "y":
        for x in vidlist:
            webbrowser.open_new_tab("https://www.youtube.com/watch?v=" + x)

def unknown_channel_search():
    cur.execute("SELECT DISTINCT MN FROM FLAT_PAIRLIST_SECOND fps WHERE NOT EXISTS(SELECT 1 FROM CH_ID chi WHERE (fps.MN = chi.NICK_NAME_1 OR fps.MN = chi.NICK_NAME_2))")
    not_submit_nickname_list = [y[0] for y in cur.fetchall()]
    chidlist = []
    for x in not_submit_nickname_list:
        s = psc.Search_channel(x)
        if s.results==None:
            s.get_next_results()
        if s.results !=None and len(s.results) > 0:
            chidlist.append(s.results[0])
    if len(chidlist) > 0:
        add_ch_data_self(chidlist)

def open_not_entered_ch(mode=0):
    if mode==0:
        cur.execute("SELECT CH_ID FROM CH_ID WHERE IG = 0 AND NICK_NAME_1 IS NULL ORDER BY CH_ID ASC")
    elif mode==1:
        cur.execute("SELECT CH_ID FROM CH_ID WHERE IG = 1 AND DEFAULT_GROUPE_NAME IS NULL AND NAM like '%Topic%' AND NAM NOT LIKE '%Various Artists%' ORDER BY CH_ID ASC")
    chidlist = [c[0] for c in cur.fetchall()]
    ret = input("本当に" + str(len(chidlist)) + "個のタブを開きますか？ Y/n :")
    ret = ret.lower()
    if ret == "y":
        for x in chidlist:
            webbrowser.open_new_tab("https://www.youtube.com/channel/" + x + "/about")

def beta_spotify_reload():
    cur.execute("select KEY_MUSIC_NAME from MUSIC_SONG_DB where SP_ID = 'faul' and CONTENT_COUNT > 0")
    fetchcache = cur.fetchall()
    for r in fetchcache:
        rn = r[0]
        res = md.search_music(rn)
        cur.execute("update MUSIC_SONG_DB set MUSIC_NAME_SP = :mnsp,SP_ID = :spid,ARTIST_NAME = :nan where KEY_MUSIC_NAME = :nkmn",nkmn=rn,mnsp=res[0],spid=res[3],nan=res[2])
        con.commit()

def music_analyze():
    cur.execute("SELECT SP_ID FROM MUSIC_SONG_DB msd WHERE SP_ID != 'faul' AND CONTENT_COUNT > 0 AND NOT EXISTS(SELECT 1 FROM MUSICINFO sd WHERE sd.SP_ID = msd.SP_ID)")
    spid_list = [x[0] for x in cur.fetchall()]
    if len(spid_list)>0:
        nowres = md.spotyfy_analyze(spid_list)
        for x in nowres:
            cur.execute("INSERT INTO MUSICINFO (SP_ID,ACOUSTICNESS,DANCEABILITY,ENERGY,PITCH_CLASS,MNMJ,TEMPO,TIME_SIGNATURE,VALENCE) VALUES (:spid,:ac,:dance,:enerrgy,:pitch,:mnmj,:tempo,:tisi,:valence)",spid=x["id"],ac=x["acousticness"],dance=x["danceability"],enerrgy=x["energy"],pitch=x["key"],mnmj=x["mode"],tempo=x["tempo"],tisi=x["time_signature"],valence=x["valence"])
        con.commit()
        nowres = md.spotify_trackdata(spid_list)
        cur.execute("SELECT SP_ID FROM MUSICINFO")
        nidlis = [r[0] for r in cur.fetchall()]
        for x in nowres:
            if x["id"] in nidlis:
                cur.execute("UPDATE MUSICINFO SET POPULARITY = :np,ARTIST_ID = :nai WHERE SP_ID = :nspid",np=x["popularity"],nai=x["artist_id"],nspid=x["id"])
                con.commit()

def ownerplaylist_recommend():
    nowpl = pytube.Playlist("https://www.youtube.com/playlist?list=" + ev.owplid)
    ins_playlist = [str(nowpl[x])[32:] for x in range(len(nowpl))]#idが入ったリスト
    save_jsondata = []
    for r in ins_playlist:
        try:
            with open(folder_path + siteurl + "/api/v4/videoid/" + r + ".json","r") as f:
                nowjson = json.load(f)
            vidname = nowjson["videoname"]
        except:
            cur.execute("SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = :nvidid FETCH FIRST 1 ROWS ONLY",nvidid=r)
            vidname = cur.fetchone()[0]
        save_jsondata.append([r,vidname])
    with open(folder_path + siteurl + "/api/recommend.json","w") as f:
        json.dump({"index":save_jsondata},f)

#ここから新バージョン用コード

class Diffdata:
    datelabel = []
    viewcount = []
    likecount = []
    commentcount = []
    igdata = None

    def __init__(self) -> None:
        self.datelabel = []
        self.viewcount = []
        self.likecount = []
        self.commentcount = []
        self.igdata = None

    def _import(self,datalabel,viewcount,likecount,commentcount):
        self.datelabel = datalabel
        self.viewcount = viewcount
        self.likecount = likecount
        self.commentcount = commentcount

    def output(self):
        return [self.igdata,self.datelabel,self.viewcount,self.likecount,self.commentcount]

class Videodata:
    videoid = ""
    channelid = ""
    uploadtime = datetime.datetime
    videoname = ""
    musicname = ""
    groupname = ""
    status = ""
    movietime = ""
    member = []
    diffdata = ""
    channelname = ""
    songstart:float = 0.0
    songend:float = 0.0
    chorusstart:float = 0.0
    chorusend:float = 0.0

    def __init__(self):
        self.videoid = ""
        self.channelid = ""
        self.uploadtime = datetime.datetime
        self.videoname = ""
        self.musicname = ""
        self.groupname = ""
        self.status = ""
        self.movietime = ""
        self.member = []
        self.diffdata = ""
        self.channelname = ""
        self.songstart:float = 0.0
        self.songend:float = 0.0
        self.chorusstart:float = 0.0
        self.chorusend:float = 0.0
    
    def generate_videodata(self):
        self = video2data_v4(self.videoid)

    def generate_member(self):
        if self.groupname==None:
            cur.execute("SELECT NICK_NAME_1,NICK_NAME_2,PICTURE_URL,BELONG_OFFICE FROM CH_ID WHERE CH_ID = :nchid",nchid=self.channelid)
            fetchcache = cur.fetchone()
            nowmemberdata = Memberdata()
            nowmemberdata.nickname = fetchcache[0]
            nowmemberdata.subnickname = fetchcache[1]
            nowmemberdata.pictureurl = fetchcache[2]
            nowmemberdata.belongoffice = fetchcache[3]
            self.member = [nowmemberdata]
        else:
            self.member = groupname2memdata_v4(self.groupname)

    def generate_diffdata(self):
        cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'), NVL(NULLIF((VIEW_C - lag(VIEW_C, 1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0), 0) AS DIFF, LIKE_C, COMMENT_C FROM VIDEO_V_DATA vvd WHERE VIDEO_ID = :nvid AND RELOAD_TIME > SYSDATE - 8 ORDER BY RELOAD_TIME ASC OFFSET 1 ROWS FETCH FIRST 7 ROWS ONLY",nvid=self.videoid)
        fetchcache = cur.fetchall()
        self.diffdata = Diffdata()
        self.diffdata._import([x[0] for x in fetchcache],[x[1] for x in fetchcache],[x[2] for x in fetchcache],[x[3] for x in fetchcache])

    def dictlist_mendata(self):
        if self.member == []:
            self.generate_member()
        mainlist = []
        for x in range(len(self.member)):
            try:
                mainlist.append(self.member[x].output())
            except:
                mainlist.append(self.member[x].output(self.member[x]))
        return mainlist

    def apidata(self,mode=0):
        if self.videoname == "":
            self.generate_videodata()
        if self.member == []:
            self.generate_member()
        if self.diffdata == "":
            self.generate_diffdata()
        if mode==1 and self.channelname=="":
            cur.execute("SELECT NAM FROM CH_ID WHERE NICK_NAME_1 = :nnc OR NICK_NAME_2 = :nnc")
            self.channelname = cur.fetchone()[0]
        if mode==0:
            nowdic = {"videoid":self.videoid,"videoname":self.videoname,"musicname":self.musicname,"statisticsdata":self.diffdata.output(),"memberdata":self.dictlist_mendata(),"movietime":self.movietime}
        if mode==1:
            nowdic = {"videoid":self.videoid,"videoname":self.videoname,"musicname":self.musicname,"statisticsdata":self.diffdata.output(),"memberdata":self.dictlist_mendata(),"movietime":self.movietime,"channelname":self.channelname,"songtime":[self.songstart,self.songend],"chorusdata":[self.chorusstart,self.chorusend]}
        return nowdic

class Memberdata:
    nickname = ""
    subnickname = ""
    pictureurl = ""
    belongoffice = ""
    createtime = datetime
    modifytime = datetime
    video = []
    diffdata = ""

    def __init__(self):
        self.nickname = ""
        self.subnickname = ""
        self.pictureurl = ""
        self.belongoffice = ""
        self.createtime = datetime
        self.modifytime = datetime
        self.video = []
        self.diffdata = ""

    def generate_memberdata(self):
        cur.execute("SELECT NICK_NAME_1,NICK_NAME_2,PICTURE_URL,NVL(BELONG_OFFICE,'個人勢'),CLEATE_PAGE_DATE,LAST_MODIFIED FROM CH_ID WHERE NICK_NAME_1 = :nmn OR NICK_NAME_2 = :nmn",nmn=self.nickname)
        fetchcache = cur.fetchone()
        self.nickname = fetchcache[0]
        self.subnickname = fetchcache[1]
        self.pictureurl = fetchcache[2]
        self.belongoffice = fetchcache[3]
        self.createtime = fetchcache[4]
        self.modifytime = fetchcache[5]

    def generate_videolist(self):
        self.video = nickname2allvideodata_v4(self.nickname).video
    
    def generate_diffdata(self):
        if self.video==[]:
            self.generate_videolist(self)
        videoidlist = [x.videoid for x in self.video]
        retlist = view_vlist_graph(video_idlist=videoidlist)
        self.diffdata = Diffdata()
        self.diffdata._import(retlist[0],retlist[1],retlist[2],retlist[3])

    def output(self):
        return {"nickname":self.nickname,"pictureurl":self.pictureurl,"office":self.belongoffice}

class Musicdata:
    musicname = ""
    artistname = ""
    spotifyid = ""
    youtubeid = ""
    createtime = datetime
    modifytime = datetime
    video = []
    diffdata = ""

    def __init__(self):
        self.musicname = ""
        self.artistname = ""
        self.spotifyid = ""
        self.youtubeid = ""
        self.createtime = datetime
        self.modifytime = datetime
        self.video = []
        self.diffdata = ""
    
    def generate_musidata(self):
        cur.execute("SELECT KEY_MUSIC_NAME,ARTIST_NAME,SP_ID,YT_ID,CLEATE_PAGE_DATE,LAST_MODIFIED FROM MUSIC_SONG_DB WHERE KEY_MUSIC_NAME = :nmn",nmn=self.musicname)
        fetchcache = cur.fetchone()
        self.artistname = fetchcache[1]
        self.spotifyid = fetchcache[2]
        self.youtubeid = fetchcache[3]
        self.createtime = fetchcache[4]
        self.modifytime = fetchcache[5]
        if self.artistname==None:
            self.artistname = "不明"

    def generate_videolist(self):
        self.video = music2allvideodata_v4(self.musicname).video
    
    def generate_diffdata(self):
        cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'), SUM(VIEW_C), SUM(LIKE_C), SUM(COMMENT_C) FROM VIDEO_V_DATA vvd WHERE exists (SELECT * FROM VIDEO_ID vid WHERE MUSIC_NAME = :nmn AND vvd.VIDEO_ID = vid.VIDEO_ID) and vvd.RELOAD_TIME > sysdate - 8 group by vvd.RELOAD_TIME order by vvd.RELOAD_TIME asc",nmn=self.musicname)
        fetchcache = cur.fetchall()
        self.diffdata = Diffdata()
        self.diffdata._import([x[0] for x in fetchcache],[x[1] for x in fetchcache],[x[2] for x in fetchcache],[x[3] for x in fetchcache])

    def apidata(self):
        if self.video == []:
            self.generate_videolist()
        if self.artistname == "":
            self.generate_musidata()
        if self.diffdata == "":
            self.generate_diffdata()
        nowdic = {"musicname":self.musicname,"sp":self.spotifyid,"yt":self.youtubeid,"statisticsdata":self.diffdata.output(),"artistname":self.artistname,"videolist":[x.videoid for x in self.video]}
        return nowdic

def video2data_v4(videoid):
    nowvideodata = Videodata()
    cur.execute("SELECT VIDEO_ID,CHANNEL_ID,UPLOAD_TIME,VIDEO_NAME,MUSIC_NAME,GROUPE_NAME,STATUS,MOVIE_TIME,(SELECT NICK_NAME_1 FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT NICK_NAME_2 FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT PICTURE_URL FROM CH_ID WHERE CH_ID=CHANNEL_ID),NVL((SELECT BELONG_OFFICE FROM CH_ID WHERE CH_ID=CHANNEL_ID),'個人勢'),(SELECT CLEATE_PAGE_DATE FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT LAST_MODIFIED FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT NAM FROM CH_ID WHERE CH_ID=CHANNEL_ID) FROM VIDEO_ID WHERE VIDEO_ID = :nvid",nvid=videoid)
    fetchcache = cur.fetchone()

    nowvideodata.videoid = fetchcache[0]
    nowvideodata.channelid = fetchcache[1]
    nowvideodata.uploadtime = fetchcache[2]
    nowvideodata.videoname = fetchcache[3]
    nowvideodata.musicname = fetchcache[4]
    nowvideodata.groupname = fetchcache[5]
    nowvideodata.status = fetchcache[6]
    nowvideodata.movietime = fetchcache[7]
    nowvideodata.channelname = fetchcache[14]

    if nowvideodata.groupname==None:#グループ名なし
        nowmemberdata = Memberdata()

        nowmemberdata.nickname = fetchcache[8]
        nowmemberdata.subnickname = fetchcache[9]
        nowmemberdata.pictureurl = fetchcache[10]
        nowmemberdata.belongoffice = fetchcache[11]
        nowmemberdata.createtime = fetchcache[12]
        nowmemberdata.modifytime = fetchcache[13]

        nowvideodata.member.append(nowmemberdata)
    else:
        nowvideodata.generate_member()
    return nowvideodata
    
def groupname2memdata_v4(groupname):
    cur.execute("SELECT (SELECT NICK_NAME_1 FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), (SELECT NICK_NAME_2 FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), (SELECT PICTURE_URL FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), NVL((SELECT BELONG_OFFICE FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), '個人勢'), (SELECT CLEATE_PAGE_DATE FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), (SELECT LAST_MODIFIED FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0) from FLAT_PAIRLIST_SECOND where GROUPE_NAME = :group_name",group_name=groupname)
    fetchcache = cur.fetchall()
    allmemberlist = []
    for r in fetchcache:
        nowmemberdata = Memberdata()
        nowmemberdata.nickname = r[0]
        nowmemberdata.subnickname = r[1]
        nowmemberdata.pictureurl = r[2]
        nowmemberdata.belongoffice = r[3]
        nowmemberdata.createtime = r[4]
        nowmemberdata.modifytime = r[5]
        allmemberlist.append(nowmemberdata)
    return allmemberlist

def music2allvideodata_v4(musicname):
    cur.execute("SELECT VIDEO_ID,CHANNEL_ID,UPLOAD_TIME,VIDEO_NAME,MUSIC_NAME,GROUPE_NAME,STATUS,MOVIE_TIME,(SELECT NICK_NAME_1 FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT NICK_NAME_2 FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT PICTURE_URL FROM CH_ID WHERE CH_ID=CHANNEL_ID),NVL((SELECT BELONG_OFFICE FROM CH_ID WHERE CH_ID=CHANNEL_ID),'個人勢'),(SELECT CLEATE_PAGE_DATE FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT LAST_MODIFIED FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT NAM FROM CH_ID WHERE CH_ID=CHANNEL_ID) FROM VIDEO_ID WHERE MUSIC_NAME = :nmn AND STATUS = 0 AND (IG = 0 OR IG = 2) ORDER BY UPLOAD_TIME DESC",nmn=musicname)
    fetchcache = cur.fetchall()

    nowmusicdata = Musicdata()
    nowmusicdata.musicname = musicname

    for x in fetchcache:
        nowvideodata = Videodata()

        nowvideodata.videoid = x[0]
        nowvideodata.channelid = x[1]
        nowvideodata.uploadtime = x[2]
        nowvideodata.videoname = x[3]
        nowvideodata.musicname = x[4]
        nowvideodata.groupname = x[5]
        nowvideodata.status = x[6]
        nowvideodata.movietime = x[7]
        nowvideodata.channelname = x[14]

        if nowvideodata.groupname==None:#グループ名なし
            nowmemberdata = Memberdata()

            nowmemberdata.nickname = x[8]
            nowmemberdata.subnickname = x[9]
            nowmemberdata.pictureurl = x[10]
            nowmemberdata.belongoffice = x[11]
            nowmemberdata.createtime = x[12]
            nowmemberdata.modifytime = x[13]

            nowvideodata.member.append(nowmemberdata)
        else:
            nowvideodata.generate_member()
        nowmusicdata.video.append(nowvideodata)

    return nowmusicdata

def create_pairlist_materialized():
    cur.execute("CREATE MATERIALIZED VIEW FLAT_PAIRLIST_SECOND AS SELECT GROUPE_NAME, TO_CHAR(MN_1) MN from PAIR_LIST_SECOND WHERE MN_1 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_2) MN from PAIR_LIST_SECOND WHERE MN_2 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_3) MN from PAIR_LIST_SECOND WHERE MN_3 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_4) MN from PAIR_LIST_SECOND WHERE MN_4 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_5) MN from PAIR_LIST_SECOND WHERE MN_5 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_6) MN from PAIR_LIST_SECOND WHERE MN_6 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_7) MN from PAIR_LIST_SECOND WHERE MN_7 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_8) MN from PAIR_LIST_SECOND WHERE MN_8 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_9) MN from PAIR_LIST_SECOND WHERE MN_9 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_10) MN from PAIR_LIST_SECOND WHERE MN_10 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_11) MN from PAIR_LIST_SECOND WHERE MN_11 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_12) MN from PAIR_LIST_SECOND WHERE MN_12 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_13) MN from PAIR_LIST_SECOND WHERE MN_13 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_14) MN from PAIR_LIST_SECOND WHERE MN_14 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_15) MN from PAIR_LIST_SECOND WHERE MN_15 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_16) MN from PAIR_LIST_SECOND WHERE MN_16 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_17) MN from PAIR_LIST_SECOND WHERE MN_17 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_18) MN from PAIR_LIST_SECOND WHERE MN_18 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_19) MN from PAIR_LIST_SECOND WHERE MN_19 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_20) MN from PAIR_LIST_SECOND WHERE MN_20 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_21) MN from PAIR_LIST_SECOND WHERE MN_21 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_22) MN from PAIR_LIST_SECOND WHERE MN_22 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_23) MN from PAIR_LIST_SECOND WHERE MN_23 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_24) MN from PAIR_LIST_SECOND WHERE MN_24 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_25) MN from PAIR_LIST_SECOND WHERE MN_25 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_26) MN from PAIR_LIST_SECOND WHERE MN_26 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_27) MN from PAIR_LIST_SECOND WHERE MN_27 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_28) MN from PAIR_LIST_SECOND WHERE MN_28 IS NOT NULL UNION ALL SELECT GROUPE_NAME, TO_CHAR(MN_29) MN from PAIR_LIST_SECOND WHERE MN_29 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_30 MN from PAIR_LIST_SECOND WHERE MN_30 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_31 MN from PAIR_LIST_SECOND WHERE MN_31 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_32 MN from PAIR_LIST_SECOND WHERE MN_32 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_33 MN from PAIR_LIST_SECOND WHERE MN_33 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_34 MN from PAIR_LIST_SECOND WHERE MN_34 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_35 MN from PAIR_LIST_SECOND WHERE MN_35 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_36 MN from PAIR_LIST_SECOND WHERE MN_36 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_37 MN from PAIR_LIST_SECOND WHERE MN_37 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_38 MN from PAIR_LIST_SECOND WHERE MN_38 IS NOT NULL UNION ALL SELECT GROUPE_NAME, MN_39 MN from PAIR_LIST_SECOND WHERE MN_39 IS NOT NULL")
    con.commit()
    #インデックス作成
    cur.execute("CREATE INDEX INDEX_FPS_GROUPE_NAME ON FLAT_PAIRLIST_SECOND(GROUPE_NAME)")
    cur.execute("CREATE INDEX INDEX_FPS_MN ON FLAT_PAIRLIST_SECOND(MN)")
    cur.execute("CREATE INDEX INDEX_FPS_GROUPE_NAME_AND_MN ON FLAT_PAIRLIST_SECOND(GROUPE_NAME,MN)")
    con.commit()

def reload_pairlist_materialized():
    cur.execute("DROP MATERIALIZED VIEW FLAT_PAIRLIST_SECOND")
    create_pairlist_materialized()
    #cur.execute("EXECUTE dbms_mview.refresh('FLAT_PAIRLIST_SECOND')")

def nickname2allvideodata_v4(nickname):
    cur.execute("SELECT VIDEO_ID, CHANNEL_ID, UPLOAD_TIME, VIDEO_NAME, MUSIC_NAME, GROUPE_NAME, STATUS, MOVIE_TIME, (SELECT NICK_NAME_1 FROM CH_ID WHERE CH_ID = CHANNEL_ID), (SELECT NICK_NAME_2 FROM CH_ID WHERE CH_ID = CHANNEL_ID), (SELECT PICTURE_URL FROM CH_ID WHERE CH_ID = CHANNEL_ID), NVL((SELECT BELONG_OFFICE FROM CH_ID WHERE CH_ID = CHANNEL_ID), '個人勢'), (SELECT CLEATE_PAGE_DATE FROM CH_ID WHERE CH_ID = CHANNEL_ID), (SELECT LAST_MODIFIED FROM CH_ID WHERE CH_ID = CHANNEL_ID), (SELECT NAM FROM CH_ID WHERE CH_ID = CHANNEL_ID) from VIDEO_ID vid where (exists (SELECT * from FLAT_PAIRLIST_SECOND fps where MN in ((select NICK_NAME_1 from CH_ID where NICK_NAME_1 = :nnc or NICK_NAME_2 = :nnc), (select NVL(NICK_NAME_2, 0) from CH_ID where NICK_NAME_1 = :nnc or NICK_NAME_2 = :nnc)) and NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) = fps.GROUPE_NAME) OR vid.CHANNEL_ID = (SELECT CH_ID FROM CH_ID chi WHERE NICK_NAME_1 = :nnc OR NICK_NAME_2 = :nnc)) AND (IG = 0 OR IG = 2) STATUS = 0 ORDER BY UPLOAD_TIME DESC",nnc=nickname)
    fetchcache = cur.fetchall()
    
    nowmainmemberdata = Memberdata()
    nowmainmemberdata.nickname = nickname

    for x in fetchcache:
        nowvideodata = Videodata()

        nowvideodata.videoid = x[0]
        nowvideodata.channelid = x[1]
        nowvideodata.uploadtime = x[2]
        nowvideodata.videoname = x[3]
        nowvideodata.musicname = x[4]
        nowvideodata.groupname = x[5]
        nowvideodata.status = x[6]
        nowvideodata.movietime = x[7]
        nowvideodata.channelname = x[14]

        if nowvideodata.groupname==None:#グループ名なし
            nowmemberdata = Memberdata()

            nowmemberdata.nickname = x[8]
            nowmemberdata.subnickname = x[9]
            nowmemberdata.pictureurl = x[10]
            nowmemberdata.belongoffice = x[11]
            nowmemberdata.createtime = x[12]
            nowmemberdata.modifytime = x[13]

            nowvideodata.member.append(nowmemberdata)
        else:
            nowvideodata.generate_member()
        nowmainmemberdata.video.append(nowvideodata)
    return nowmainmemberdata

def make_music_page_v4(musicname,useapi=True):
    try:
        musicdata = Musicdata()
        if useapi:
            try:
                with open(folder_path + siteurl + "/api/v4/music/" + dir_name_replace(musicname) + ".json","r") as f:
                    nowjson = json.load(f)
                    musicdata.musicname = musicname
                    musicdata.artistname = nowjson["artist"]
                    musicdata.spotifyid = nowjson["sp"]
                    musicdata.youtubeid = nowjson["yt"]
                    if nowjson["createtime"]!=None:
                        musicdata.createtime = datetime.datetime.strptime(nowjson["createtime"],"%Y-%m-%dT%H:%M:%S")
                    else:
                        musicdata.createtime = None
                    if nowjson["modifytime"]!=None:
                        musicdata.modifytime = datetime.datetime.strptime(nowjson["modifytime"],"%Y-%m-%dT%H:%M:%S")
                    else:
                        musicdata.modifytime = None
                    for x in nowjson["videolist"]:
                        with open(folder_path + siteurl + "/api/v4/videoid/" + x + ".json","r") as vf:
                            vapidata = json.load(vf)
                            nvdata = Videodata()
                            nvdata.videoid = x
                            nvdata.channelname = vapidata["channelname"]
                            nvdata.movietime = vapidata["movietime"]
                            nvdata.musicname = vapidata["musicname"]
                            nvdata.videoname = vapidata["videoname"]
                            musicdata.video.append(nvdata)
            except:
                musicdata = music2allvideodata_v4(musicname=musicname)
                musicdata.generate_musidata()
        else:
            musicdata = music2allvideodata_v4(musicname=musicname)
            musicdata.generate_musidata()
        n_html_path = folder_path + siteurl + "/music/" + dir_name_replace(musicname) + "/"
        if os.path.isdir(n_html_path)==False:
            os.makedirs(n_html_path)
        share_html = []
        share_html_a = share_html.append
        description = f"Vtuberの{musicdata.musicname}の歌ってみた動画をまとめたサイトです。たくさんのvtuberの歌ってみた動画のランキングのサイトです。皆様に沢山のvtuberを知ってもらいたく運営しています。"
        page_title = f"Vtuberの歌う{musicdata.musicname}"
        share_html_a('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/music/" + dir_name_replace(musicdata.musicname) + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + nomsec_time(musicdata.createtime) + '"><meta property="article:modified_time" content="' + nomsec_time(musicdata.modifytime) + '"></head><body>')
        share_html_a(html_import_lib)
        share_html_a(header)
        share_html_a('<main><div class="for_center">')
        if musicdata.spotifyid!=None and musicdata.youtubeid!=None:
            share_html_a("<h1><button class='nbt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + musicdata.musicname + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/watch?v=" + musicdata.youtubeid + "'>YoutubeMusicで聞く</a></td></tr><tr><td><p>" + musicdata.musicname + "</p></td><td><p>" + musicdata.artistname + """</p><td><a href='https://open.spotify.com/track/""" + musicdata.spotifyid + """'>Spotifyで再生</a></td></tr></table>""")
        elif musicdata.spotifyid==None and musicdata.youtubeid!=None:
            share_html_a("<h1><button class='nbt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + musicdata.musicname + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/watch?v=" + musicdata.youtubeid + "'>YoutubeMusicで聞く</a></td></tr><tr><td><p>" + musicdata.musicname + "</p></td><td><p>" + musicdata.artistname + "</p><td><a href='https://open.spotify.com/search/" + urllib.parse.quote(musicdata.musicname) + "'>spotifyで検索(DBに登録されていません)</a></td></tr></table>")
        elif musicdata.spotifyid!=None and musicdata.youtubeid==None:
            share_html_a("<h1><button class='nbt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + musicdata.musicname + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/search?q=" + urllib.parse.quote(musicdata.musicname) + "'>YoutubeMusicで検索(DBにデータがありません)</a></td></tr><tr><td><p>" + musicdata.musicname + "</p></td><td><p>" + musicdata.artistname + """</p><td><a href='https://open.spotify.com/track/""" + musicdata.spotifyid + """'>Spotifyで再生</a></td></tr></table>""")
        elif musicdata.spotifyid==None and musicdata.youtubeid==None:
            share_html_a("<h1><button class='nbt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + musicdata.musicname + "</h1><table border='1' class='table-line inline'><tr><th><p>曲名</p></th><th><p>アーティスト名</p></th><td><a href='https://music.youtube.com/search?q=" + urllib.parse.quote(musicdata.musicname) + "'>YoutubeMusicで検索(DBにデータがありません)</a></td></tr><tr><td><p>" + musicdata.musicname + "</p></td><td><p>" + musicdata.artistname + "</p><td><a href='https://open.spotify.com/search/" + urllib.parse.quote(musicdata.musicname) + "'>spotifyで検索(DBに登録されていません)</a></td></tr></table>")
        share_html_a('<group class="inline-radio-sum yt-view-sum" onchange="change_graph_music(\'sum-yt\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">コメント数</label></div></group>' + "<canvas id='sum-yt' class='yt-view-sum inline'></canvas></div>")
        share_html_a("<div class='pos_re'><select id='page_sort_select' class='sort_select' onchange='music_select_change()'><option value='latest'>新しい順</option><option value='viewcount_desc'>視聴回数(多い順)</option><option value='viewcount_asc'>視聴回数(少ない順)</option><option value='goodcount'>高評価数(多い順)</option><option value='commentcount'>コメント数(多い順)</option><option value='viewcount_rate'>視聴回数上昇率(多い順)</option></select><div class='switch-flex'>")
        share_html_a('</div></div><div id="music_flex">')
        needshort = False
        needtopic = False
        for nowviddata in musicdata.video:
            if nowviddata.movietime != None:
                if nowviddata.movietime <= 60:
                    addclass = " yt_short"
                    needshort = True
                else:
                    addclass = ""
            else:
                addclass = ""
            if nowviddata.channelname!="":
                if "Topic" in nowviddata.channelname:
                    addclass += " inctopic"
                    needtopic = True
            share_html_a(f'<div id="fb_{nowviddata.videoid}" class="music_flex_ly{addclass}"><span class="ofoverflow_320" title="{nowviddata.videoname}">{nowviddata.videoname}</span><lite-youtube videoid="{nowviddata.videoid}"></lite-youtube><button class="ofoverflow_320 minmg" onclick="vdt(\'{nowviddata.videoid}\')">詳細を表示</button></div>')
        if needtopic:
            share_html.insert(7,"<div class='switch'><span>配信楽曲を表示</span><input id='cmn-toggle-ms' class='cmn-toggle cmn-toggle-round'type='checkbox' onchange='ytviewchange()'><label for='cmn-toggle-ms' class='cmn-toggle-label'></label></div>")
        if needshort:
            share_html.insert(7,"<div class='switch'><span>ショート動画を表示</span><input id='cmn-toggle-sh' class='cmn-toggle cmn-toggle-round' type='checkbox' onchange='ytviewchange()'><label for='cmn-toggle-sh' class='cmn-toggle-label' id='cmn-toggle-short'></label></div>")
        share_html_a("""</div></div><div class="pos-re"><div id="descm"></div><div id="music_recommend"></div><div id="descc"></div><div id="ch_recommend"></div></div></main>""" + music_control_html)
        share_html_a("<script src='/library/main.js'></script></body></html>")
        with open(n_html_path + "index.html","wb") as f:
            f.write("".join(list(flatten(share_html))).encode("utf-8"))#windows対策
    except Exception as e:
        pro_log("error","make_musicpage_v4",musicname,"unknown error->continue",str(e))

def make_ch_page_v4(nickname,useapi=True):
    try:
        chdata = Memberdata()
        if useapi:
            try:
                with open(folder_path + siteurl + "/api/v4/ch/" + dir_name_replace(nickname) + ".json","r") as f:
                    njson = json.load(f)
                    chdata.nickname = nickname
                    chdata.belongoffice = njson["belongoffice"]
                    for x in njson["videolist"]:
                        with open(folder_path + siteurl + "/api/v4/videoid/" + x + ".json","r") as vf:
                            vapidata = json.load(vf)
                            nvdata = Videodata()
                            nvdata.videoid = x
                            nvdata.channelname = vapidata["channelname"]
                            nvdata.movietime = vapidata["movietime"]
                            nvdata.musicname = vapidata["musicname"]
                            chdata.video.append(nvdata)
                    if njson["createtime"]!=None:
                        chdata.createtime = datetime.datetime.strptime(njson["createtime"],"%Y-%m-%dT%H:%M:%S")
                    else:
                        chdata.createtime = None
                    if njson["modifytime"]!=None:
                        chdata.modifytime = datetime.datetime.strptime(njson["modifytime"],"%Y-%m-%dT%H:%M:%S")
                    else:
                        chdata.modifytime = None
            except:
                chdata = nickname2allvideodata_v4(nickname)
                chdata.generate_memberdata()
        else:
            chdata = nickname2allvideodata_v4(nickname)
            chdata.generate_memberdata()
        site_nick_name = dir_name_replace(nickname)
        n_html_path = folder_path + siteurl + "/ch/" + site_nick_name + "/"
        if os.path.isdir(n_html_path)==False:#フォルダがなければ生成
            os.mkdir(n_html_path)
        share_html = []
        share_html_a = share_html.append
        description = f"Vtuberの{chdata.nickname}が歌った歌ってみた及びオリジナル曲をまとめたサイトです。たくさんのvtuberの歌ってみた動画のランキングのサイトです。皆様に沢山のvtuberを知ってもらいたく運営しています。"
        page_title = chdata.nickname + "の歌った曲集"
        share_html_a('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + site_nick_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + nomsec_time(chdata.createtime) + '"><meta property="article:modified_time" content="' + nomsec_time(chdata.modifytime) + '"></head><body>')
        share_html_a(html_import_lib)
        share_html_a(header)
        share_html_a('<main><div class="for_center">')
        share_html_a(f'<h1><button class="nbt_noborder" onclick="allplay()"><img class="control_icon" src="/util/cicle_playbtn.svg"></button>{nickname}</h1>')
        share_html_a('<group class="inline-radio-sum yt-view-sum" onchange="change_graph_ch(\'sum-yt\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">コメント数</label></div></group>' + "<canvas id='sum-yt' class='yt-view-sum inline'></canvas></div>")
        share_html_a("<div class='pos_re'><select id='page_sort_select' class='sort_select' onchange='ch_select_change()'><option value='latest'>新しい順</option><option value='viewcount_desc'>視聴回数(多い順)</option><option value='viewcount_asc'>視聴回数(少ない順)</option><option value='goodcount'>高評価数(多い順)</option><option value='commentcount'>コメント数(多い順)</option><option value='viewcount_rate'>視聴回数上昇率(多い順)</option></select><div class='switch-flex'>")
        share_html_a("</div></div><div id='ch_flex'>")
        needshort = False
        needtopic = False
        needcollab = False
        for nowviddata in chdata.video:
            if nowviddata.movietime != None:
                if nowviddata.movietime <= 60:
                    addclass = " yt_short"
                    needshort = True
                else:
                    addclass = ""
            else:
                addclass = ""
            if nowviddata.channelname!="":
                if "Topic" in nowviddata.channelname:
                    addclass += " inctopic"
                    needtopic = True
            membercount = 1
            if useapi:
                try:
                    with open(folder_path + siteurl + "/api/v4/videoid/" + nowviddata.videoid + ".json","r") as f:
                        njson = json.load(f)
                    membercount = len(njson["memberdata"])
                except:
                    nowviddata.generate_member()
                    membercount = len(nowviddata.member)
            else:
                nowviddata.generate_member()
                membercount = len(nowviddata.member)
            if membercount > 1:
                addclass += " collab"
                needcollab = True
            share_html_a(f'<div id="fb_{nowviddata.videoid}" class="music_flex_ly{addclass}"><span class="ofoverflow_320" title="{nowviddata.videoname}"><a href="{"/music/" + dir_name_replace(nowviddata.musicname) + "/"}" onclick="page_ajax_load(\'{"/music/" + dir_name_replace(nowviddata.musicname) + "/"}\');return false">{nowviddata.musicname}</a></span><lite-youtube videoid="{nowviddata.videoid}"></lite-youtube><button class="ofoverflow_320 minmg" onclick="vdt(\'{nowviddata.videoid}\')">詳細を表示</button></div>')
        if needcollab:
            share_html.insert(7,"<div class='switch'><span>コラボを表示</span><input id='cmn-toggle-cb' class='cmn-toggle cmn-toggle-round' type='checkbox' onchange='ytviewchange()' checked><label for='cmn-toggle-cb' class='cmn-toggle-label'></label></div>")
        if needtopic:
            share_html.insert(7,"<div class='switch'><span>配信楽曲を表示</span><input id='cmn-toggle-ms' class='cmn-toggle cmn-toggle-round' type='checkbox' onchange='ytviewchange()'><label for='cmn-toggle-ms' class='cmn-toggle-label'></label></div>")
        if needshort:
            share_html.insert(7,"<div class='switch'><span>ショート動画を表示</span><input id='cmn-toggle-sh' class='cmn-toggle cmn-toggle-round' type='checkbox' onchange='ytviewchange()'><label for='cmn-toggle-sh' class='cmn-toggle-label'></label></div>")
        share_html_a("""</div><div class="pos-re"><div id="descm"></div><div id="music_recommend"></div><div id="descc"></div><div id="ch_recommend"></div></div></main>""" + music_control_html)
        share_html_a("<script src='/library/main.js'></script></body></html>")
        with open(n_html_path + "index.html","wb") as f:
            f.write("".join(list(flatten(share_html))).encode("utf-8"))#windows対策
    except Exception as e:
        pro_log("error","make_chpage_v4",nickname,"unknown error->continue",str(e))

def v4chpage_all():
    cur.execute("SELECT NICK_NAME_1 FROM CH_ID WHERE NICK_NAME_1 IS NOT NULL AND CONTENT_COUNT > 0")
    nicknamelist = [x[0] for x in cur.fetchall()]
    for t in nicknamelist:
        make_ch_page_v4(t)

def v4music_all():
    cur.execute("SELECT KEY_MUSIC_NAME FROM MUSIC_SONG_DB WHERE CONTENT_COUNT > 0")
    musiclist = [x[0] for x in cur.fetchall()]
    for t in musiclist:
        make_music_page_v4(t)

def v4api_video():
    if os.path.isdir(folder_path + siteurl + "/api/v4/videoid/")==False:
        os.makedirs(folder_path + siteurl + "/api/v4/videoid/")
    cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'),VIDEO_ID,VIEW_C,LIKE_C,COMMENT_C FROM VIDEO_V_DATA WHERE TRUNC(RELOAD_TIME,'DD') = (SELECT MAX(TRUNC(RELOAD_TIME,'DD')) FROM VIDEO_V_DATA)")
    latestdata = {}
    for r in cur.fetchall():
        latestdata[r[1]] = [r[0],r[2],r[3],r[4]]
    cur.execute("SELECT VIDEO_ID,TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'), NVL(NULLIF((VIEW_C - lag(VIEW_C, 1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)), 0), 0) AS DIFF, LIKE_C, COMMENT_C FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE - 8 ORDER BY VIDEO_ID ASC,RELOAD_TIME ASC")
    ndiffdata = {}
    for x in cur.fetchall():
        try:
            diffd = ndiffdata[x[0]]#わざとout of rangeさせて判定
            skip = False
        except:
            ndiffdata[x[0]] = Diffdata()
            diffd = ndiffdata[x[0]]
            skip = True
        if skip:
            try:
                diffd.igdata = latestdata[x[0]]
            except:
                pass
        else:
            diffd.datelabel.append(x[1])
            diffd.viewcount.append(x[2])
            diffd.likecount.append(x[3])
            diffd.commentcount.append(x[4])

    cur.execute("SELECT GROUPE_NAME, (SELECT NICK_NAME_1 FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), (SELECT NICK_NAME_2 FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), (SELECT PICTURE_URL FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), NVL((SELECT BELONG_OFFICE FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), '個人勢'), (SELECT CLEATE_PAGE_DATE FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0), (SELECT LAST_MODIFIED FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0) from FLAT_PAIRLIST_SECOND WHERE EXISTS (SELECT 1 FROM CH_ID WHERE (NICK_NAME_1 = MN OR NICK_NAME_2 = MN) AND IG = 0 AND NICK_NAME_1 IS NOT NULL) ORDER BY GROUPE_NAME")
    ngroup_data = {}
    for x in cur.fetchall():
        if x[0] not in ngroup_data.keys():
            ngroup_data[x[0]] = []
        ndata = ngroup_data[x[0]]
        now_mendata = Memberdata()
        now_mendata.nickname = x[1]
        now_mendata.subnickname = x[2]
        now_mendata.pictureurl = x[3]
        now_mendata.belongoffice = x[4]
        now_mendata.createtime = x[5]
        now_mendata.modifytime = x[6]
        ndata.append(now_mendata)
        
    cur.execute("SELECT VIDEO_ID,CHANNEL_ID,UPLOAD_TIME,VIDEO_NAME,MUSIC_NAME,GROUPE_NAME,STATUS,MOVIE_TIME,(SELECT NICK_NAME_1 FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT NICK_NAME_2 FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT PICTURE_URL FROM CH_ID WHERE CH_ID=CHANNEL_ID),NVL((SELECT BELONG_OFFICE FROM CH_ID WHERE CH_ID=CHANNEL_ID),'個人勢'),(SELECT CLEATE_PAGE_DATE FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT LAST_MODIFIED FROM CH_ID WHERE CH_ID=CHANNEL_ID),(SELECT NAM FROM CH_ID WHERE CH_ID=CHANNEL_ID),SOUND_START,SOUND_END,CHORUS_START,CHORUS_END FROM VIDEO_ID WHERE IG != 1")
    fetchcache = cur.fetchall()
    for x in fetchcache:
        nowvideodata = Videodata()

        nowvideodata.videoid = x[0]
        nowvideodata.channelid = x[1]
        nowvideodata.uploadtime = x[2]
        nowvideodata.videoname = x[3]
        nowvideodata.musicname = x[4]
        nowvideodata.groupname = x[5]
        nowvideodata.status = x[6]
        nowvideodata.movietime = x[7]
        nowvideodata.channelname = x[14]
        nowvideodata.songstart = x[15]
        nowvideodata.songend = x[16]
        nowvideodata.chorusstart = x[17]
        nowvideodata.chorusend = x[18]
        try:
            nowvideodata.diffdata = ndiffdata[nowvideodata.videoid]
            nowvideodata.diffdata.igdata.extend([math.floor((nowvideodata.diffdata.viewcount[len(nowvideodata.diffdata.viewcount)-1]/nowvideodata.diffdata.viewcount[len(nowvideodata.diffdata.viewcount)-2])*100),nowvideodata.uploadtime.timestamp()])
        except:
            pass

        if nowvideodata.groupname==None:#グループ名なし
            nowmemberdata = Memberdata()

            nowmemberdata.nickname = x[8]
            nowmemberdata.subnickname = x[9]
            nowmemberdata.pictureurl = x[10]
            nowmemberdata.belongoffice = x[11]
            nowmemberdata.createtime = x[12]
            nowmemberdata.modifytime = x[13]

            nowvideodata.member.append(nowmemberdata)
        else:
            try:
                nowvideodata.member = ngroup_data[x[5]]
            except:
                nowvideodata.generate_member()
        with open(folder_path + siteurl + "/api/v4/videoid/" + nowvideodata.videoid + ".json","w") as f:
            json.dump(nowvideodata.apidata(mode=1),f)

def v4api_ch():
    if os.path.isdir(folder_path + siteurl + "/api/v4/ch/")==False:
        os.makedirs(folder_path + siteurl + "/api/v4/ch/")
    cur.execute("SELECT NICK_NAME_1,NICK_NAME_2,PICTURE_URL,NVL(BELONG_OFFICE,'個人勢'),CLEATE_PAGE_DATE,LAST_MODIFIED FROM CH_ID WHERE IG = 0 AND NICK_NAME_1 IS NOT NULL")
    fetchcache = cur.fetchall()
    for x in range(len(fetchcache)):
        nowmemdata = Memberdata()

        nowmemdata.nickname = fetchcache[x][0]
        nowmemdata.subnickname = fetchcache[x][1]
        nowmemdata.pictureurl = fetchcache[x][2]
        nowmemdata.belongoffice = fetchcache[x][3]
        nowmemdata.createtime = fetchcache[x][4]
        nowmemdata.modifytime = fetchcache[x][5]

        cur.execute("SELECT VIDEO_ID from VIDEO_ID vid where status = 0 and (exists (SELECT * from FLAT_PAIRLIST_SECOND fps where MN in ((select NICK_NAME_1 from CH_ID where NICK_NAME_1 = :nnc or NICK_NAME_2 = :nnc), (select NVL(NICK_NAME_2, 0) from CH_ID where NICK_NAME_1 = :nnc or NICK_NAME_2 = :nnc)) and NVL(vid.GROUPE_NAME, (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE chi.CH_ID = vid.CHANNEL_ID)) = fps.GROUPE_NAME) OR vid.CHANNEL_ID = (SELECT CH_ID FROM CH_ID chi WHERE NICK_NAME_1 = :nnc OR NICK_NAME_2 = :nnc)) AND (IG = 0 OR IG = 2) ORDER BY UPLOAD_TIME DESC",nnc=nowmemdata.nickname)
        videoidlist = [r[0] for r in cur.fetchall()]
        diffarray = view_vlist_graph(video_idlist=videoidlist,data=2)
        with open(folder_path + siteurl + "/api/v4/ch/" + dir_name_replace(nowmemdata.nickname) + ".json","w") as f:
            try:
                json.dump({"channelnickname":nowmemdata.nickname,"statisticsdata":diffarray,"videolist":videoidlist,"pictureurl":nowmemdata.pictureurl,"belongoffice":nowmemdata.belongoffice,"createtime":nowmemdata.createtime.isoformat(),"modifytime":nowmemdata.modifytime.isoformat()},f)
            except:
                json.dump({"channelnickname":nowmemdata.nickname,"statisticsdata":diffarray,"videolist":videoidlist,"pictureurl":nowmemdata.pictureurl,"belongoffice":nowmemdata.belongoffice,"createtime":None,"modifytime":None},f)
                
def v4api_music():
    if os.path.isdir(folder_path + siteurl + "/api/v4/music/")==False:
        os.makedirs(folder_path + siteurl + "/api/v4/music/")
    #先にmusicnameでvideoidを仕分ける
    cur.execute("SELECT VIDEO_ID,MUSIC_NAME FROM VIDEO_ID WHERE MUSIC_NAME IS NOT NULL AND (IG = 0 OR IG = 2)")
    n_music_vid = {}
    for x in cur.fetchall():
        if x[1] not in n_music_vid.keys():
            n_music_vid[x[1]] = []
        n_music_vid[x[1]].append(x[0])
    #次に使うビューを定義
    cur.execute("CREATE OR REPLACE VIEW VVD_MUSIC AS SELECT VIDEO_ID,(SELECT MUSIC_NAME FROM VIDEO_ID vid WHERE vid.VIDEO_ID = vvd.VIDEO_ID) MUSIC_NAME,TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD') CHAR_RELOAD_TIME, VIEW_C, LIKE_C, COMMENT_C FROM VIDEO_V_DATA vvd WHERE vvd.RELOAD_TIME > sysdate - 8")
    cur.execute("SELECT MUSIC_NAME,CHAR_RELOAD_TIME,SUM(VIEW_C),SUM(LIKE_C),SUM(COMMENT_C) FROM VVD_MUSIC GROUP BY MUSIC_NAME,CHAR_RELOAD_TIME ORDER BY MUSIC_NAME ASC, CHAR_RELOAD_TIME ASC")
    n_music_diff = {}
    for x in cur.fetchall():
        if x[0] not in n_music_diff.keys():
            n_music_diff[x[0]] = [None,[],[],[],[]]
        n_music_diff[x[0]][1].append(x[1])
        n_music_diff[x[0]][2].append(x[2])
        n_music_diff[x[0]][3].append(x[3])
        n_music_diff[x[0]][4].append(x[4])
    cur.execute("SELECT KEY_MUSIC_NAME,ARTIST_NAME,SP_ID,YT_ID,CLEATE_PAGE_DATE,LAST_MODIFIED FROM MUSIC_SONG_DB WHERE CONTENT_COUNT > 0")
    fetchcache = cur.fetchall()
    for x in fetchcache:
        try:
            diffarray = n_music_diff[x[0]]
        except:
            cur.execute("SELECT TO_CHAR(RELOAD_TIME, 'YYYY/MM/DD'), SUM(VIEW_C), SUM(LIKE_C), SUM(COMMENT_C) FROM VIDEO_V_DATA vvd WHERE exists (SELECT * FROM VIDEO_ID vid WHERE MUSIC_NAME = :nmn AND vvd.VIDEO_ID = vid.VIDEO_ID) and vvd.RELOAD_TIME > sysdate - 8 group by vvd.RELOAD_TIME order by vvd.RELOAD_TIME asc",nmn=x[0])
            diffcache = cur.fetchall()
            diffarray = [None,[r[0] for r in diffcache],[r[1] for r in diffcache],[r[2] for r in diffcache],[r[3] for r in diffcache]]
        try:
            vididlist = n_music_vid[x[0]]
        except:
            cur.execute("select VIDEO_ID from VIDEO_ID where MUSIC_NAME = :nmn AND (IG = 0 OR IG = 2) AND STATUS = 0",nmn=x[0])
            vididlist = [r[0] for r in cur.fetchall()]
        with open(folder_path + siteurl + "/api/v4/music/" + dir_name_replace(x[0]) + ".json","w") as f:
            try:
                json.dump({"musicname":x[0],"sp":x[2],"yt":x[3],"artist":x[1],"videolist":vididlist,"statisticsdata":diffarray,"createtime":x[4].isoformat(),"modifytime":x[5].isoformat()},f)
            except:
                json.dump({"musicname":x[0],"sp":x[2],"yt":x[3],"artist":x[1],"videolist":vididlist,"statisticsdata":diffarray,"createtime":None,"modifytime":None},f)

def youtube_music_analyze():
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID WHERE IG = 0 AND STATUS = 0 AND ( SOUND_START = 0 OR SOUND_END = 0 OR CHORUS_START = 0 OR CHORUS_END = 0)")
    need_vidlist = [x[0] for x in cur.fetchall()]
    if len(need_vidlist)==0:
        return
    filelist = []
    proc_list = []
    if len(need_vidlist) < ev.multi_max*4:
        with open(ev.tmp_folder + "/vid_0.json","w") as f:
            json.dump({"videoid":need_vidlist},f)
        filelist.append(ev.tmp_folder + "/vid_0_return.json")
        subprocess.run([ev.python_call,os.path.dirname(os.path.abspath(__file__)) + '/youtube_music_analyze.py',"file",ev.tmp_folder + "/vid_0.json"], stdout=subprocess.DEVNULL)
    else:
        #ファイル生成
        content_length = math.ceil(len(need_vidlist)/ev.multi_max)
        for n in range(ev.multi_max):
            vlistjson = {"videoid":need_vidlist[content_length*n:content_length*(n+1)]}
            if n+1==ev.multi_max:
                vlistjson["videoid"] = need_vidlist[content_length*n:]
            with open(ev.tmp_folder + f"/vid_{n+1}.json","w") as f:
                json.dump(vlistjson,f)
            filelist.append(ev.tmp_folder + f"/vid_{n+1}_return.json")
        for n in range(ev.multi_max):
            proc = subprocess.Popen([ev.python_call,os.path.dirname(os.path.abspath(__file__)) + '/youtube_music_analyze.py',"file",ev.tmp_folder + f"/vid_{n+1}.json"], stdout=subprocess.DEVNULL)
            proc_list.append(proc)
        for subproc in proc_list:
            subproc.wait()
    for x in filelist:
        with open(x,"r") as f:
            retj:dict = json.load(f)
        inc_vid = retj.keys()
        for r in inc_vid:
            ndata = retj[r]
            cur.execute("UPDATE VIDEO_ID SET SOUND_START = :ss,SOUND_END = :se,CHORUS_START = :cs,CHORUS_END = :ce WHERE VIDEO_ID = :vid",ss=ndata["timedata"][0],se=ndata["timedata"][1],cs=ndata["chorusdata"][0],ce=ndata["chorusdata"][1],vid=r)
            con.commit()

def groupe_predict():
    cur.execute("UPDATE VIDEO_ID vid SET GROUPE_NAME = (SELECT DEFAULT_GROUPE_NAME FROM CH_ID chi WHERE vid.CHANNEL_ID = chi.CH_ID AND chi.IG = 1) WHERE vid.IG = 2 AND vid.GROUPE_NAME IS NULL AND EXISTS(SELECT 1 FROM CH_ID chi WHERE chi.IG = 1 AND chi.CH_ID=vid.CHANNEL_ID AND chi.DEFAULT_GROUPE_NAME IS NOT NULL)")
    con.commit()

def ig2_musicname():
    cur.execute("select VIDEO_ID,VIDEO_NAME from VIDEO_ID where IG = 2")
    fetchCache = cur.fetchall()
    for x in fetchCache:
        videoname = x[1]
        predict = get_song_title(videoname)
        if(len(predict)>30):
            predict = predict[0:30]
        cur.execute("UPDATE VIDEO_ID SET MUSIC_NAME = :mn WHERE VIDEO_ID = :vid",vid=x[0],mn=predict)
        con.commit()
