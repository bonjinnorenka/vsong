import oracle_vsong as ov
while True:
    nowcommand = input("vsong_maneger: ")
    if nowcommand=="exit":
        ov.conect_close()
        break
    elif nowcommand=="update_vdata":
        ov.update_videodata()
    elif nowcommand=="update_vlist":
        ov.correct_video_list()
    elif nowcommand=="add_chdata":
        ov.add_ch_data()
    elif nowcommand=="add_gname":
        ov.add_groupe_name()
    elif nowcommand=="add_mdata":
        ov.add_music_data()
    elif nowcommand=="true_check":
        ov.true_check()
    elif nowcommand=="make_page":
        ov.make_all_musicpage()
        ov.make_all_chpage()
    elif nowcommand=="re_pic":
        ov.reloadpeople_picture()
    elif nowcommand=="se_index":
        ov.make_search_index()
    elif nowcommand=="random_gen":
        ov.music_recommend_page()
        ov.channel_recommend_page()
    elif nowcommand=="hot":
        ov.todays_hot()
    elif nowcommand=="always_do":
        ov.correct_video_list()
        input("準備が完了したらキーを押してください")
        print("視聴回数データを追加しています")
        ov.update_videodata()
        print("メタデータを追加しています")
        ov.add_ch_data()
        ov.add_groupe_name()
        ov.add_music_data()
        print("データの整合性をチェックしています")
        ov.true_check()
    elif nowcommand=="cplib":
        inpst = input("本当にライブラリデータを本番環境に反映してよろしいですか?(y/n)")
        if inpst=="y":
            ov.cp_lib()
            print("別途search.cppをg++等でコンパイルしてください")
    elif nowcommand=="pslib":
        inpst = input("本当に本番環境のライブラリデータを配布用ディレクトリに反映してよろしいですか?(y/n)")
        if inpst=="y":
            ov.ps_lib()
    elif nowcommand=="cphtml":
        inpst = input("本当に固定HTMLデータを本番環境に反映してよろしいですか?(y/n)")
        if inpst=="y":
            ov.cp_htm()
    elif nowcommand=="pshtml":
        inpst = input("本当に本番環境の固定HTMLデータを配布用ディレクトリに反映してよろしいですか?(y/n)")
        if inpst=="y":
            ov.ps_htm()
    else:
        print("exit:終了\nhelp:今のコマンド\nupdate_vdata:動画の統計情報を更新します\nupdate_vlist:プレイリストから最新の動画idを取得します\nadd_chdata:足りないチャンネルを取得します\
        \nadd_gname:足りないグループ名を追加します\nadd_mdata:足りない音楽データを追加します\ntrue_check:データが正常に登録されているか確認します\nmake_page:ページを生成します\
        \nre_pic:チャンネルの顔画像を更新します\nse_index:検索用索引を生成\nrandom_gen:おすすめデータ生成\nhot:人気動画ランキング生成\nalways_do:定期的に実行するコマンドをまとめたもの")
