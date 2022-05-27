import itertools
import math,os,cx_Oracle,requests,datetime,collections,urllib.parse,json,random,copy,jaconv
import MySQLdb
from pykakasi import kakasi
import get_youtube_data as gy
import music_data as md
import ev

con = cx_Oracle.connect(ev.oracle_user, ev.oracle_ps, ev.oracle_connect_string)
print("Database version:", con.version + "\tデータベースに正常に接続できました。")
cur = con.cursor()
cur.execute("alter session set nls_date_format='YYYY-MM-DD HH24:MI:SS'")

#webサイト用変数設定
siteurl = "vsong.fans"
header = """<header><h2 class="Top"><a href="/" onClick='page_ajax_load("/");return false'>VtuberSing</a></h2><nav class="header-nav"><ul><li><a href="/search/" onClick='page_ajax_load("/search/");return false'>検索</a><li><a href="/today/" onClick='page_ajax_load("/today/");return false'>今日の人気</a></ul></nav></header>"""
folder_path = "public/"

def conect_close():#接続切るよう
    con.close()
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

def video2data_v2(video_id):
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

def groupe_name2men_namev2(groupe_name):#v2のテーブルにアクセス
    songer_list = []
    songer_list_a = songer_list.append
    cur.execute("select MN_1,MN_2,MN_3,MN_4,MN_5,MN_6,MN_7,MN_8,MN_9,MN_10,MN_11,MN_12,MN_13,MN_14,MN_15,MN_16,MN_17,MN_18,MN_19,MN_20,MN_21,MN_22,MN_23,MN_24,MN_25,MN_26,MN_27,MN_28,MN_29,MN_30,MN_31,MN_32,MN_33,MN_34,MN_35,MN_36,MN_37,MN_38,MN_39 from PAIR_LIST_SECOND where groupe_name = :group_name",group_name=groupe_name.replace("'","''"))
    k_gndata = cur.fetchone()
    for r in k_gndata:
        if r!=None:#データあり
            songer_list_a(r)
        else:
            break
    return songer_list

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
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID WHERE MUSIC_NAME = :music_name and ig = 0 ORDER BY UPLOAD_TIME DESC",music_name=music_name.replace("'","''"))#登校が新しい順に並び変え
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

def make_all_musicpage():
    cur.execute("SELECT KEY_MUSIC_NAME FROM MUSIC_SONG_DB")
    for x in cur.fetchall():
        make_music_page_v2(str(x)[2:-3])

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

def get_ch_vdata(nickname,mode=0):
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
    elif mode==1:
        for n in vidlist:
            vid_a(str(n)[2:-3])
    if mode==0:
        return vdata,t_page_d,vid_list
    elif mode==1:
        return vid_list

def make_music_page_v2(music_name,mode=0):
    n_html_path = folder_path + siteurl + "/music/" + dir_name_replace(music_name) + "/"
    if os.path.isdir(n_html_path)==False:
        os.mkdir(n_html_path)
    share_html = []
    share_html_a = share_html.append
    if mode==0:
        music_data = search_musicdata(music_name)
        share_html_a('<link rel="stylesheet" href="/library/main.css"><script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script><script src="https://www.youtube-nocookie.com/s/player/7e5c03a3/www-widgetapi.vflset/www-widgetapi.js"></script>')
        share_html_a(header)
        description = "Vtuberの" + music_name + "の歌ってみた動画をまとめたサイトです。たくさんのvtuberの歌ってみた動画のランキングのサイトです。皆様に沢山のvtuberを知ってもらいたく運営しています。"
        page_title = "Vtuberの歌う" + music_name
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
        share_html_a('<div id="sum-viewer"></div>')
        share_html_a("<table id='video_data_t'>")
        share_html_a("""</table></div><div id="descm"></div><div id="music_recommend"></div><div id="descc"></div><div id="ch_recommend"></div></main><div class="sticky_c_yt dis_none" id="ytembed"><div id="youtube-iframe"></div></div><span class="sticky_c dis_none" id="control_panel"><progress class="yt-progress" id="yt-player-time" max="100" value="0"></progress><div class="flex_box"><div class="beside_gr"><div class="beside_gr_in" id="music_name_display"></div></div><div class="play_center"><button id="yt-playbt" onclick="yt_playorstop()" class="bt_noborder" title="再生"><img class="control_icon" src="/util/playbtn.svg"></button><button onclick="yt_skip()" title="スキップ" class="bt_noborder"><img class="control_icon" src="/util/skipbt.svg"></button><input title="音量を調節" type="range" id="yt_sound_volume" min="0" max="100" value="100" onchange="yt_volume_change()"><button id="yt_display" onclick="yt_display()">表示</button><button id="yt_ch_dismode" onclick='yt_watchmode_ch()' title="大画面で表示" class="bt_noborder"><img class="control_icon" src="/util/bigwindow.svg"></button><input id="autoload_check" type="checkbox"></div></div></span>""")
    music_videos_id = music_list(music_name)
    tbdata = []
    tbdata_ex = tbdata.extend
    for g in range(math.ceil(len(music_videos_id)/10)):
        tbdata_ex(["<tbody id='tbd-" + str(g) + "'>","</tbody>"])
    statistics_data = {}
    v_data = []
    for x in music_videos_id:
        v_data.append(video2data_v2(x))
    for r in range(math.ceil(len(music_videos_id)/10)):
        nowvid = []
        page_html_data_mdata = []
        phdm_a = page_html_data_mdata.append
        json_pagedata = {"music_name":dir_name_replace(music_name),"pageid":r,"max-length":math.ceil(len(music_videos_id)/10)}
        nowpgdata = copy.deepcopy(share_html)
        json_count = 0
        if 10*(r+1) > len(music_videos_id):
            max_len = len(music_videos_id)
        else:
            max_len = 10*(r+1)
        for x in range(10*r,max_len,1):
            x_list = []
            x_list_a = x_list.append
            if r==0 and x==0:
                statistics_data["music"] = view_music_graph(music_name,dt=1)
            if r==0 and x==0 and mode==0:
                #初回分だけ特殊データ登録
                json_pagedata["first"] = '<group class="inline-radio-sum yt-view-sum" onchange="change_graph_music(\'sum-yt\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">コメント数</label></div></group>' + "<canvas id='sum-yt' class='yt-view-sum inline'></canvas>"
                page_html_data_mdata.append('<group class="inline-radio-sum yt-view-sum" onchange="change_graph_music(\'sum-yt\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">コメント数</label></div></group>' + "<canvas id='sum-yt' class='yt-view-sum inline'></canvas>")
            can_d,sclist = view_graph(video_id=v_data[x][0],dt=4,scope=7)#統計情報取得
            statistics_data[v_data[x][0]] = sclist#統計データを辞書に登録
            if mode==0:#この場合HTMLデータも生成
                nowvid.append(v_data[x][0])
                #メンバーリストをエラーが出ないよう訂正そして画像のURLもついでに最適化
                men_of_list = []
                if v_data[x][2]==1:#歌い手が１人
                    if v_data[x][3][5]==None:
                        v_data[x][3][5] = "個人"
                    men_of_list = [str(v_data[x][3][0]).replace(" ",""),v_data[x][3][5]]
                    #url-rewrite
                    if "https://yt" in v_data[x][3][3]:#画像ソースがyoutubeの場合
                        v_data[x][3][3] = v_data[x][3][3] + "=s75-c-k-c0x00ffffff-no-rj"
                    elif "https://pbs.twimg.com" in v_data[x][3][3]:#twitter
                        v_data[x][3][3] = str(v_data[x][3][3])[:-11] + "200x200" + str(v_data[x][3][3])[-4:]
                else:#複数人
                    for w in range(v_data[x][2]):
                        if v_data[x][3][w][0] not in men_of_list:
                            men_of_list.append(str(v_data[x][3][w][0]).replace(" ",""))
                        if v_data[x][3][w][5]==None:
                            v_data[x][3][w][5] = "個人"
                        if v_data[x][3][w][5] not in men_of_list:
                            men_of_list.append(v_data[x][3][w][5])
                        if "https://yt" in v_data[x][3][w][3]:#ソースyoutube
                            v_data[x][3][w][3] = v_data[x][3][w][3] + "=s75-c-k-c0x00ffffff-no-rj"
                        elif "https://pbs.twimg.com" in v_data[x][3][w][3]:
                            v_data[x][3][w][3] = str(v_data[x][3][w][3])[:-11] + "200x200" + str(v_data[x][3][w][3])[-4:]
                #行のデータ
                x_list_a("<tr class='" + " ".join(men_of_list) + "'><td><lite-youtube videoid='" + v_data[x][0] + "' playlabel='Play'></lite-youtube></td><td class='yt-meta' id='" + v_data[x][0] + "_td'><details id='" + v_data[x][0] + "_dt' class='mdata-dt'><summary class='music_title'>" + v_data[x][4][2] + "</summary>" + f'<group class="inline-radio" onchange="change_graph_music(\'{v_data[x][0]}\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="{v_data[x][0]}_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="{v_data[x][0]}_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="{v_data[x][0]}_ra"><label class="radio-page-label">コメント数</label></div></group>' + can_d + "<div class='vtuber_sing'>")
                #人データ追加
                if v_data[x][2]==1:#歌い手が１人
                    x_list_a("<a href='/ch/" + dir_name_replace(v_data[x][3][0]) + "' onclick='page_ajax_load(\"/ch/" + dir_name_replace(v_data[x][3][0]) + "/\");return false'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][3] + "' alt='" + v_data[x][3][0] + "' title='" + v_data[x][3][0] + "'></a>")
                else:#歌い手が複数人
                    for u in range(v_data[x][2]):
                        x_list_a("<a href='/ch/" + dir_name_replace(v_data[x][3][u][0]) + "' onclick='page_ajax_load(\"/ch/" + dir_name_replace(v_data[x][3][u][0]) + "/\");return false'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][u][3] + "' alt='" + v_data[x][3][u][0] + "' title='" + v_data[x][3][u][0] + "'></a>")
                x_list_a("</div></details></td></tr>")
                json_pagedata[json_count] = "".join(x_list)
                json_count += 1
                phdm_a(copy.copy(x_list))
        if mode==0:
            k_tbdata = copy.deepcopy(tbdata)
            k_tbdata.insert((2*r)+1,page_html_data_mdata)
            nowpgdata.insert(6,k_tbdata)
            nowpgdata.append("<script src='/library/main.js'></script>")
            head_data = []
            stapass_preload = "<link rel='preload' href='/music/" + music_name + "/statistics.json' as='fetch'>"
            if r==0 and r!=math.ceil(len(v_data)/10):#初回ページかつ次のページがある
                head_data.append('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + music_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + music_data[4] + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '">')
                head_data.append('<link rel="next" href="/music/' + music_name + '/page2/">')
                head_data.append(stapass_preload + "</head>")#閉じタグちゃん
            elif r==0 and r==math.ceil(len(v_data)/10):#初回ページのみ
                head_data.append('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + music_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + music_data[4] + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '">' + stapass_preload + '</head>')
            elif r==math.ceil(len(v_data)/10):#最後のページ
                head_data.append('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + music_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + music_data[4] + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '">' + stapass_preload)
                if r!=1:
                    head_data.append('<link rel="prev" href="/music/' + music_name + '/page' + str(math.ceil(len(v_data)/10)-1) + '/">')
                else:
                    head_data.append('<link rel="prev" href="/music/' + music_name + '/">')
                head_data.append("</head>")#閉じタグちゃん
            else:
                head_data.append('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + music_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + music_data[4] + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '">' + stapass_preload)
                if r==1:#２ページ目の場合初回ページが前
                    head_data.append('<link rel="prev" href="/music/' + music_name + '/">')
                else:
                    head_data.append('<link rel="prev" href="/music/' + music_name + '/page' + str(r) + '/">')
                head_data.append('<link rel="next" href="/music/' + music_name + '/page' + str(r+2) + '/">')
                head_data.append("</head>")#閉じタグちゃん
            head_data.append("<body>")
            nowpgdata.insert(0,"".join(head_data))
            nowpgdata.append("</body></html>")
            json_pagedata["videoidlist"] = nowvid
            #ファイル保存パッチ            
            if r==0:
                html_fp = ""
            else:
                if os.path.isdir(n_html_path + "page" + str(r+1) + "/")==False:#フォルダがなければ生成
                    os.mkdir(n_html_path + "page" + str(r+1) + "/")
                html_fp = "page" + str(r+1) + "/"
            with open(n_html_path + html_fp + "data.json","w") as f:#テーブルのデータ
                    json.dump(json_pagedata,f,indent=4)
            with open(n_html_path + html_fp + "index.html","wb") as f:
                f.write("".join(list(flatten(nowpgdata))).encode("utf-8"))#windows対策
    with open(n_html_path + "statistics.json","w") as f:
        json.dump(statistics_data,f,indent=4)

def make_chpage_v2(nick_name,mode=0):
    site_nick_name = dir_name_replace(nick_name)
    n_html_path = folder_path + siteurl + "/ch/" + site_nick_name + "/"
    if os.path.isdir(n_html_path)==False:#フォルダがなければ生成
        os.mkdir(n_html_path)
    if mode==0:
        v_data,page_fc_date,videolist_id = get_ch_vdata(nick_name)
    elif mode==1:
        videolist_id = get_ch_vdata(nickname=nick_name,mode=1)
    share_html = []
    share_html_a = share_html.append
    description = "Vtuberの" + nick_name + "が歌った歌ってみた及びオリジナル曲をまとめたサイトです。たくさんのvtuberの歌ってみた動画のランキングのサイトです。皆様に沢山のvtuberを知ってもらいたく運営しています。"
    page_title = nick_name + "の歌った曲集"
    share_html_a('<link rel="stylesheet" href="/library/main.css"><script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script><script src="https://www.youtube-nocookie.com/s/player/7e5c03a3/www-widgetapi.vflset/www-widgetapi.js"></script>')
    share_html_a(header)
    share_html_a('<main><div class="for_center"><div id="sum-viewer"></div>')
    share_html_a("<table id='video_data_t'>")
    #ここの6番目にデータは入れてね
    share_html_a("""</table></div><div id="descm"></div><div id="music_recommend"></div><div id="descc"></div><div id="ch_recommend"></div></main><div class="sticky_c_yt dis_none" id="ytembed"><div id="youtube-iframe"></div></div><span class="sticky_c dis_none" id="control_panel"><progress class="yt-progress" id="yt-player-time" max="100" value="0"></progress><div class="flex_box"><div class="beside_gr"><div class="beside_gr_in" id="music_name_display"></div></div><div class="play_center"><button id="yt-playbt" onclick="yt_playorstop()" class="bt_noborder" title="再生"><img class="control_icon" src="/util/playbtn.svg"></button><button onclick="yt_skip()" title="スキップ" class="bt_noborder"><img class="control_icon" src="/util/skipbt.svg"></button><input title="音量を調節" type="range" id="yt_sound_volume" min="0" max="100" value="100" onchange="yt_volume_change()"><button id="yt_display" onclick="yt_display()">表示</button><button id="yt_ch_dismode" onclick='yt_watchmode_ch()' title="大画面で表示" class="bt_noborder"><img class="control_icon" src="/util/bigwindow.svg"></button><input id="autoload_check" type="checkbox"></div></div></span>""")
    tbdata = []
    tbdata_ex = tbdata.extend
    for g in range(math.ceil(len(videolist_id)/10)):
        tbdata_ex(["<tbody id='tbd-" + str(g) + "'>","</tbody>"])
    statistics_data = {}
    for r in range(math.ceil(len(videolist_id)/10)):#メインデータ生成
        if mode==0:
            nowvid = []
            page_html_data_mdata = []
            phdm_a = page_html_data_mdata.append
            json_pagedata = {"nick_name":dir_name_replace(nick_name),"pageid":r,"max-length":math.ceil(len(v_data)/10)}
            nowpgdata = copy.deepcopy(share_html)
            json_count = 0
        if 10*(r+1) > len(videolist_id):
            max_len = len(videolist_id)
        else:
            max_len = 10*(r+1)
        for x in range(10*r,max_len,1):
            x_list = []
            x_list_a = x_list.append
            if r==0 and x==0:
                statistics_data["channel"] = view_vlist_graph(videolist_id,data=1)
            if r==0 and x==0 and mode==0:
                #初回分だけ特殊データ登録
                json_pagedata["first"] = ("<h1><button class='bt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + nick_name + "</h1>" + '<group class="inline-radio-sum yt-view-sum" onchange="change_graph_ch(\'sum-yt\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">コメント数</label></div></group>' + "<canvas id='sum-yt' class='yt-view-sum inline'></canvas>")
                page_html_data_mdata.append("<h1><button class='bt_noborder' onclick='allplay()'><img class='control_icon' src='/util/cicle_playbtn.svg'></button>" + nick_name + "</h1>"  + '<group class="inline-radio-sum yt-view-sum" onchange="change_graph_ch(\'sum-yt\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="sum-yt_ra"><label class="radio-page-label">コメント数</label></div></group>' + "<canvas id='sum-yt' class='yt-view-sum inline'></canvas>")
            can_d,sclist = view_graph(video_id=videolist_id[x],dt=4,scope=7)#統計情報取得
            statistics_data[videolist_id[x]] = sclist#統計データを辞書に登録
            if mode==0:#この場合HTMLデータも生成
                nowvid.append(v_data[x][0])
                #メンバーリストをエラーが出ないよう訂正そして画像のURLもついでに最適化
                men_of_list = []
                if v_data[x][2]==1:#歌い手が１人
                    if v_data[x][3][5]==None:
                        v_data[x][3][5] = "個人"
                    men_of_list = [str(v_data[x][3][0]).replace(" ",""),v_data[x][3][5]]
                    #url-rewrite
                    if "https://yt" in v_data[x][3][3]:#画像ソースがyoutubeの場合
                        v_data[x][3][3] = v_data[x][3][3] + "=s75-c-k-c0x00ffffff-no-rj"
                    elif "https://pbs.twimg.com" in v_data[x][3][3]:#twitter
                        v_data[x][3][3] = str(v_data[x][3][3])[:-11] + "200x200" + str(v_data[x][3][3])[-4:]
                else:#複数人
                    for w in range(v_data[x][2]):
                        if v_data[x][3][w][0] not in men_of_list:
                            men_of_list.append(str(v_data[x][3][w][0]).replace(" ",""))
                        if v_data[x][3][w][5]==None:
                            v_data[x][3][w][5] = "個人"
                        if v_data[x][3][w][5] not in men_of_list:
                            men_of_list.append(v_data[x][3][w][5])
                        if "https://yt" in v_data[x][3][w][3]:#ソースyoutube
                            v_data[x][3][w][3] = v_data[x][3][w][3] + "=s75-c-k-c0x00ffffff-no-rj"
                        elif "https://pbs.twimg.com" in v_data[x][3][w][3]:
                            v_data[x][3][w][3] = str(v_data[x][3][w][3])[:-11] + "200x200" + str(v_data[x][3][w][3])[-4:]
                #行のデータ
                x_list_a("<tr class='" + " ".join(men_of_list) + "'><td><lite-youtube videoid='" + v_data[x][0] + "' playlabel='Play'></lite-youtube></td><td class='yt-meta' id='" + v_data[x][0] + "_td'><details id='" + v_data[x][0] + "_dt' class='mdata-dt'><summary id='" + v_data[x][0] + "_sum' class='music_title'><a id='" + v_data[x][0] + "_music_a' href='/music/"+ dir_name_replace(v_data[x][1][0]) + "/' onClick='page_ajax_load(\"/music/" + dir_name_replace(v_data[x][1][0]) + "/\");return false'>" + v_data[x][1][0] + "</a></summary>" + f'<group class="inline-radio" onchange="change_graph_ch(\'{v_data[x][0]}\')"><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="{v_data[x][0]}_ra" checked><label class="radio-page-label">視聴回数</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="{v_data[x][0]}_ra"><label class="radio-page-label">高評価</label></div><div class="radio-page-div"><input class="radio-page-select-p" type="radio" name="{v_data[x][0]}_ra"><label class="radio-page-label">コメント数</label></div></group>' + can_d + "<div class='vtuber_sing'>")
                #人データ追加
                if v_data[x][2]==1:#歌い手が１人
                    x_list_a("<a href='/ch/" + dir_name_replace(v_data[x][3][0]) + "' onclick='page_ajax_load(\"/ch/" + dir_name_replace(v_data[x][3][0]) + "/\");return false'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][3] + "' alt='" + v_data[x][3][0] + "' title='" + v_data[x][3][0] + "'></a>")
                else:#歌い手が複数人
                    for u in range(v_data[x][2]):
                        x_list_a("<a href='/ch/" + dir_name_replace(v_data[x][3][u][0]) + "' onclick='page_ajax_load(\"/ch/" + dir_name_replace(v_data[x][3][u][0]) + "/\");return false'><img loading='lazy' width='75' height='75' class='v_face' src='" + v_data[x][3][u][3] + "' alt='" + v_data[x][3][u][0] + "' title='" + v_data[x][3][u][0] + "'></a>")
                x_list_a("</div></details></td></tr>")
                json_pagedata[json_count] = "".join(x_list)
                json_count += 1
                phdm_a(copy.copy(x_list))
        if mode==0:
            k_tbdata = copy.deepcopy(tbdata)
            k_tbdata.insert((2*r)+1,page_html_data_mdata)
            nowpgdata.insert(4,k_tbdata)
            nowpgdata.append("<script src='/library/main.js'></script>")
            head_data = []
            stapass_preload = "<link rel='preload' href='/ch/" + nick_name + "/statistics.json' as='fetch'>"
            if r==0 and r!=math.ceil(len(v_data)/10):#初回ページかつ次のページがある
                head_data.append('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + site_nick_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + page_fc_date + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '">')
                head_data.append('<link rel="next" href="/ch/' + nick_name + '/page2/">')
                head_data.append(stapass_preload + "</head>")#閉じタグちゃん
            elif r==0 and r==math.ceil(len(v_data)/10):#初回ページのみ
                head_data.append('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + site_nick_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + page_fc_date + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '">' + stapass_preload + '</head>')
            elif r==math.ceil(len(v_data)/10):#最後のページ
                head_data.append('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + site_nick_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + page_fc_date + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '">' + stapass_preload)
                if r!=1:
                    head_data.append('<link rel="prev" href="/ch/' + nick_name + '/page' + str(math.ceil(len(v_data)/10)-1) + '/">')
                else:
                    head_data.append('<link rel="prev" href="/ch/' + nick_name + '/">')
                head_data.append("</head>")#閉じタグちゃん
            else:
                head_data.append('<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"><meta name="HandheldFriendly" content="True"><meta name="auther" content="VtuberSongHobbyist"><meta name="description" content="' + description + '"><meta property="og:description" content="' + description + '"><meta name="twitter:description" content="' + description + '"><title>' + page_title + '</title><meta property="og:title" content="' + page_title + '"><meta name="twitter:title" content="' + page_title + '"><meta property="og:url" content="https://' + siteurl + "/ch/" + site_nick_name + '"><meta property="og:image" content=""><meta name="twitter:image" content=""><meta name="twitter:card" content="summary"><meta property="article:published_time" content="' + page_fc_date + '"><meta property="article:modified_time" content="' + nomsec_time(datetime.datetime.now()) + '">' + stapass_preload)
                if r==1:#２ページ目の場合初回ページが前
                    head_data.append('<link rel="prev" href="/ch/' + nick_name + '/">')
                else:
                    head_data.append('<link rel="prev" href="/ch/' + nick_name + '/page' + str(r) + '/">')
                head_data.append('<link rel="next" href="/ch/' + nick_name + '/page' + str(r+2) + '/">')
                head_data.append("</head>")#閉じタグちゃん
            head_data.append("<body>")
            nowpgdata.insert(0,"".join(head_data))
            nowpgdata.append("</body></html>")
            json_pagedata["videoidlist"] = nowvid
            #ファイル保存パッチ            
            if r==0:
                html_fp = ""
            else:
                if os.path.isdir(n_html_path + "page" + str(r+1) + "/")==False:#フォルダがなければ生成
                    os.mkdir(n_html_path + "page" + str(r+1) + "/")
                html_fp = "page" + str(r+1) + "/"
            with open(n_html_path + html_fp + "data.json","w") as f:#テーブルのデータ
                    json.dump(json_pagedata,f,indent=4)
            with open(n_html_path + html_fp + "index.html","wb") as f:
                f.write("".join(list(flatten(nowpgdata))).encode("utf-8"))#windows対策
    with open(n_html_path + "statistics.json","w") as f:
        json.dump(statistics_data,f,indent=4)

def make_all_chpage(mode=0):
    cur.execute("select nick_name_1 from ch_id where ig = 0 and nick_name_1 is not null")
    chid_list = cur.fetchall()
    for i in chid_list:
        make_chpage_v2(str(i)[2:-3],mode=mode)

def music_recommend_page():
    ajax_path = folder_path + siteurl + "/ajax/music/"
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
            cur.execute("select video_id from video_id where music_name = '" + nmusic_name.replace("'","''") + "' order by upload_time desc FETCH FIRST 1 ROWS ONLY")
            n_vid = str(cur.fetchone())[2:-3]
            k_ar = [nmusic_name,dir_name_replace(nmusic_name),n_vid]
            n_dict[x] = k_ar
        with open(ajax_path + "mr-" + str(n) + ".json","w") as f:
            json.dump(n_dict,f,indent=4)

def channel_recommend_page():
    ajax_path = folder_path + siteurl + "/ajax/ch/"
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
            k_ar = [ch_data[k_ranlist[n]][0],dir_name_replace(ch_data[k_ranlist[n]][0]),ch_data[k_ranlist[n]][1]]
            n_dict[n] = k_ar
        with open(ajax_path + "cr-" + str(x) + ".json","w") as f:
            json.dump(n_dict,f,indent=4)

def dir_name_replace(dir_name):
    ret_dn = str(dir_name).replace("\\","").replace(",","").replace(".","").replace(":","").replace(";","").replace("?","").replace("/","").replace("<","").replace(">","").replace("*","").replace("|","").replace("+","").replace("=","").replace("[","").replace("]","").replace('"',"").replace("(","").replace(")","").replace("^","").replace("!","").replace("$","").replace("'","").replace("%","").replace("&","").replace("～","")
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
    cur.execute("SELECT CH_ID,NICK_NAME_1 FROM CH_ID WHERE EXISTS (SELECT DISTINCT CHANNEL_ID FROM VIDEO_ID WHERE IG = 0 AND GROUPE_NAME IS NULL and CH_ID.CH_ID = CHANNEL_ID)")#一人で歌っているチャンネルを取得
    single_ch_list = cur.fetchall()
    for n_chid in single_ch_list:
        cur.execute("SELECT VIDEO_ID,MUSIC_NAME FROM VIDEO_ID WHERE CHANNEL_ID = '" + n_chid[0] + "'AND IG = 0 AND GROUPE_NAME IS NULL AND MUSIC_NAME IS NOT NULL")
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
    cur.execute("SELECT DISTINCT GROUPE_NAME FROM VIDEO_ID WHERE IG = 0 AND GROUPE_NAME IS NOT NULL")#使われているgroupe name抽出
    gname_v = cur.fetchall()
    for n_gn in gname_v:
        now_gname = str(n_gn)[2:-3]
        now_g_list = groupe_name2men_namev2(now_gname)
        cur.execute("SELECT VIDEO_ID,MUSIC_NAME FROM VIDEO_ID WHERE GROUPE_NAME = '" + now_gname + "' AND IG = 0")
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
    with open(folder_path + siteurl + "/cgi-bin/search_index.json","w") as f:
        json.dump({"index":search_index},f,indent=4)
    k_ar = list(itertools.chain.from_iterable(search_index))
    with open(folder_path + siteurl + "/cgi-bin/search_index_a.json","w") as f:
        json.dump({"index":k_ar},f)
    with open(folder_path + siteurl + "/cgi-bin/search_index_a.rcsv","w",encoding="utf-8") as f:
        f.write("@".join(k_ar))
    connection_l = MySQLdb.connect(host="localhost",user="root",passwd="mysqlroot",db="vsong")
    cur_l = connection_l.cursor()
    for r in search_index:
        cur_l.execute("INSERT INTO vsong_search (main_index_key,index_print_name,index_url) VALUES('" + r[0] + "','" + str(r[1]).replace("'","''") + "','" + r[2] + "')")
    connection_l.commit()
    connection_l.close()

def make_video_random():
    cur.execute("SELECT VIDEO_ID FROM VIDEO_ID")
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
            json.dump(k_dict,f,indent=4)

def todays_hot():
    #データベースから前日の伸び率　ただし分母や分子が0になったときは-1000を出力　を最初の100行だけ取得
    cur.execute("SELECT VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,NVL(NULLIF((VIEW_C - lag(VIEW_C,1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0)/NULLIF((lag(VIEW_C,1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME) - lag(VIEW_C,2) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0),-1000)-1 DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE -3 AND EXISTS (SELECT VIDEO_ID FROM VIDEO_ID vid WHERE vid.VIDEO_ID = vvd.VIDEO_ID AND IG = 0) ORDER BY RELOAD_TIME DESC,DIFF DESC FETCH FIRST 100 ROWS ONLY")
    kari_fetch = cur.fetchall()
    rank_list = []
    for r in kari_fetch:#パーセントのようにして配列に保存
        rank_list.append([r[0],r[1],math.floor(r[3]*100)])
    with open(folder_path + siteurl + "/today/index_diff.json","w") as f:
        json.dump({"kind":"diff","index":rank_list},f)
    cur.execute("SELECT VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,NVL(NULLIF((VIEW_C - lag(VIEW_C,1) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0),-1) AS DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE-2 AND EXISTS (SELECT VIDEO_ID FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID AND IG = 0) ORDER BY RELOAD_TIME DESC,DIFF DESC FETCH FIRST 100 ROWS ONLY")
    kari_fetch = cur.fetchall()
    rank_list = []
    for r in kari_fetch:#パーセントのようにして配列に保存
        rank_list.append([r[0],r[1],r[3]])
    with open(folder_path + siteurl + "/today/index_daydiff.json","w") as f:
        json.dump({"kind":"daydiff","index":rank_list},f)
    cur.execute("SELECT VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,NVL(NULLIF((VIEW_C - lag(VIEW_C,7) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0),-1) AS DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE-8 AND EXISTS (SELECT VIDEO_ID FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID AND IG = 0) ORDER BY RELOAD_TIME DESC,DIFF DESC FETCH FIRST 100 ROWS ONLY")
    kari_fetch = cur.fetchall()
    rank_list = []
    for r in kari_fetch:#パーセントのようにして配列に保存
        rank_list.append([r[0],r[1],r[3]])
    with open(folder_path + siteurl + "/today/index_weekdiff.json","w") as f:
        json.dump({"kind":"weekdiff","index":rank_list},f)
    cur.execute("SELECT VIDEO_ID,(SELECT VIDEO_NAME FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID),RELOAD_TIME,NVL(NULLIF((VIEW_C - lag(VIEW_C,30) OVER (PARTITION BY VIDEO_ID ORDER BY RELOAD_TIME)),0),-1) AS DIFF FROM VIDEO_V_DATA vvd WHERE RELOAD_TIME > SYSDATE-31 AND EXISTS (SELECT VIDEO_ID FROM VIDEO_ID WHERE VIDEO_ID = vvd.VIDEO_ID AND IG = 0) ORDER BY RELOAD_TIME DESC,DIFF DESC FETCH FIRST 100 ROWS ONLY")
    kari_fetch = cur.fetchall()
    rank_list = []
    for r in kari_fetch:#パーセントのようにして配列に保存
        rank_list.append([r[0],r[1],r[3]])
    with open(folder_path + siteurl + "/today/index_monthdiff.json","w") as f:
        json.dump({"kind":"monthdiff","index":rank_list},f)

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
    cur.execute("SELECT VIDEO_ID,MUSIC_NAME FROM VIDEO_ID WHERE IG = 0")
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

make_music_top()