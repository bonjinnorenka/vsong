import librosa
import numpy as np
import pytube
import subprocess
import os
import sys
import math
import ruptures
import resampy
import copy
import json
#spleeter使用　要ffmpegとspleeterのPATH通し

#_だけの変数はごみ箱です

def youtube_music_analyze(videoid,sampling_rate_change = 5,overwrite = False,length_plus = 2):

    #length_plus=2は認識のミスで大体2秒短く算出されるため

    #option

    #videoid = "sq7rVi5wX5E"
    before_path = ""
    sampling_rate_change = 5#推奨5 10でもいいけど高音が特徴なのがうまくいかなくなる
    spleeter_tmpfolder = "tmp"

    if before_path == "":
        before_path = os.getcwd()

    #pytubeでダウンロード
    #一応最高音質で 別にファイル形式はほぼ全部ffmpegで行けるので考えない

    ytnvid = pytube.YouTube(f"https://www.youtube.com/watch?v={videoid}")
    ytnvid_stf = ytnvid.streams.filter(only_audio=True)#音楽に絞る
    max_bitrate = -1
    for x in ytnvid_stf:
        now_bitrate = int(str(x.abr)[:-4])
        if now_bitrate > max_bitrate:
            max_bitrate = now_bitrate
    dl_itag = -1
    for x in ytnvid_stf:
        if int(str(x.abr)[:-4])==max_bitrate:
            dl_itag = x.itag
            break
    if dl_itag != -1:
        stream = ytnvid.streams.get_by_itag(dl_itag)
        dl_path = stream.download()
        ffmpeg_option = ""

        if overwrite:
            ffmpeg_option += "-y"

        #ffmpeg で　ダウンロードしたのをwavに変換(mp3でもopusでも可) 要ffmpegのpath&dl,130秒まで出力させる(負荷軽減)
        subprocess.run(f"ffmpeg {ffmpeg_option} -i \"{dl_path}\" -t 130 -f wav \"{os.path.join(before_path,videoid)}.wav\"")
        #元のファイルを削除
        os.remove(dl_path)
        nowsppath = spleeter_tmpfolder
        if nowsppath == "":
            nowsppath = before_path

        #声とその他を分離
        #subprocess.run(f"spleeter separate {os.path.join(before_path,videoid)}.wav -o {nowsppath}")
        #y_inst,sr_vocal = librosa.load(nowsppath + "/" + videoid + "/accompaniment.wav")

    #声の処理

    #音痴度測定

    """ base_sound_hz = [32.703,34.648,36.708,38.891,41.203,43.654,46.249,48.999,51.913,55.000,58.270,61.735]#C1~B1
    hzx = [x**2 for x in range(1,7,1)]
    soundhz = [n*x for n in base_sound_hz for x in hzx]
    soundhz.sort() """
    #http://www.cs.t-kougei.ac.jp/av-media/lectures/sinxalongsong/5/page020.html https://tomari.org/main/java/oto.html 参考
    """key_hz = 55#A1
    soundhz = [key_hz*2**(x/12) for x in range(65)]#A1~B6までのhzが入ってる

    soundhz = np.round(soundhz)

    nowsppath = spleeter_tmpfolder
    if nowsppath == "":
        nowsppath = before_path

    #声とその他を分離
    subprocess.run(f"spleeter separate {os.path.join(before_path,videoid)}.wav -o {nowsppath}")

    #いらなくなった元wav音声のファイルを削除
    #os.remove(os.path.join(before_path,videoid) + ".wav")

    #os.path.join(before_path,videoid)/vocals.wavがボーカル分離したやつ
    y_vocal,sr_vocal = librosa.load(nowsppath + "/" + videoid + "/vocals.wav")
    """#1024ごとにフーリエ変換
    """vocal_stft = librosa.stft(y=y_vocal,n_fft=2048,hop_length=2048)
    S, phase = librosa.magphase(vocal_stft)  # 複素数を強度と位相へ変換
    vocal_stft_res = librosa.amplitude_to_db(S)  # 強度をdb単位へ変換"""
    """rms_volume = librosa.feature.rms(y=y_vocal,frame_length=1024,hop_length=1024)#dbではない
    vocal_volume = 20*np.log10(rms_volume)
    #-30db以下はカット

    fft_max:list[int] = []

    _index = 0

    for nfftstartindex in range(0,len(y_vocal),2048):
        fftdata = np.fft.fft(y_vocal[nfftstartindex:nfftstartindex+2048])
        fft_max.append([np.argmax(fftdata),vocal_volume[0][_index]])
        _index += 1
    
    #print(fft_max)

    result_box:list[float] = []

    for x in fft_max:
        if x[1] > -30:#-30dbよりも小さい->無視
            idx = np.abs(np.asarray(soundhz) - x[0]).argmin()#idxはindex
            near_hz = soundhz[idx]
            difference:float = 0.0
            if x[0] == near_hz:
                result_box.append(0.0)
            elif x[0] < near_hz:#実際よりも低いときのパターン
                #差を計算
                difference = soundhz[idx] - soundhz[idx -1]
                result_box.append((near_hz - float(x[0]))/ difference)
            else:#実際より高い
                difference = soundhz[idx + 1] - soundhz[idx]
                result_box.append((float(x[0]) - near_hz) / difference)

    #20%

    print(np.average(np.abs(result_box)))"""

    """def fix_chorus(vocal_y,vocal_sr,chorus_start,chorus_end):#ボーカルのデータを参考に長さを必要があれば修正start,endは単位floatの秒
        fmin, fmax = 55, 2093
        #前後10秒拡張
        n_vocaldata = vocal_y[(chorus_start-10)*vocal_sr:(chorus_end+10)*vocal_sr]
        _, voiced_flag, _ = librosa.pyin(y=n_vocaldata, fmin=fmin, fmax=fmax, sr=vocal_sr, frame_length=2048)#こいつ時間制限しないと処理重い
        del _
        #前の時間を調整
        print(len(voiced_flag))

        basestart = copy.copy(chorus_start) - 10
        estimate_fix_chorus_start = copy.copy(chorus_start)
        estimate_fix_chorus_end = copy.copy(chorus_end)

        #配列を反転させる

        start_endindex = math.floor(13*(vocal_sr/512))

        e_count = 0

        for x in np.fliplr(voiced_flag[:math.floor(13*(vocal_sr/512))]):
            if x == 0.0:
                #e_count+=1
                #if e_count > 4:
                    break
                #else:
                    #e_count+=-1
                    #if e_count < 0:
                        #e_count = 0
            start_endindex += -1
        
        if start_endindex!=0:

            pass
        
        end_startindex = len(voiced_flag) - math.floor(13*(vocal_sr/512)) -1
        for x in voiced_flag[len(voiced_flag) - math.floor(13*(vocal_sr/512)):]:
            if x == 0.0:
                #e_count+=1
                #if e_count > 4:
                    break
                #else:
                    #e_count+=-1
                    #if e_count < 0:
                        #e_count = 0
            end_startindex += -1
        if end_startindex!=0:#最後まで声がなかったわけではない
            pass"""

    #こっから認識

    if os.path.isfile(os.path.join(before_path,videoid) + ".wav")==False:
        print("error code2 file not found")
        sys.exit()

    #ファイルをロード
    y,sr = librosa.load(os.path.join(before_path,videoid) + ".wav")

    #この後いらないので削除
    os.remove(os.path.join(before_path,videoid) + ".wav")

    #無音検知

    small_volume = 0.01#閾値

    #y_square = np.square([x[0] + x[1] for x in y])

    really_starttime = 0.0

    for x in range(math.floor(len(y)/2)):#始点
        if y[x] > small_volume:
            really_starttime = x/sr
            break

    really_endtime = (len(y)-1)/sr

    y_length = len(y) - 1

    for x in range(math.floor(len(y)/2)):
        if y[y_length - x] > small_volume:
            really_endtime = (y_length - x)/sr
            break

    sound_length = really_endtime - really_starttime#float

    max_dulation = 120

    if (sound_length/2) < max_dulation:
        max_dulation = math.floor(sound_length/2)
    if sound_length <= 100:
        max_dulation = sound_length

    #音声の長さを調整 120秒以上で半分
    if sound_length >= max_dulation:
        y = y[math.floor(sr*really_starttime):math.floor(sr*max_dulation)]
        #y = y[math.floor(really_starttime):sr*max_dulation]
    else:
        y = y[math.floor(really_starttime):math.floor(really_endtime*sr)]

    n_fft      = 512
    hop_length = n_fft // 2

    #最大値取得

    frame_length_m = sr
    hop_length_m = math.floor(sr/2)

    sc    = librosa.feature.spectral_centroid(y=y, n_fft=frame_length_m, hop_length=hop_length_m)[0]
    rms   = librosa.feature.rms(y=y, frame_length=frame_length_m, hop_length=hop_length_m)[0]
    sc_max = np.amax(sc)
    rms_max = np.amax(rms)

    #あとで使うので値を分岐

    y_origin = copy.deepcopy(y)
    sampling_rate_origin = copy.copy(sr)

    #打楽器抑制

    """x_stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    x_stft_harm, _ = librosa.decompose.hpss(x_stft, margin=1.2)
    y = librosa.util.fix_length(librosa.istft(x_stft_harm, hop_length=hop_length), size=len(y))
    """
    #ダウンサンプリング

    y = resampy.resample(y,sr,int(math.floor(sr/sampling_rate_change)))
    sr = math.floor(sr/sampling_rate_change)

    #特徴量の値を返す関数
    def rms_sc(y,sr):
        frame_length = sr
        hop_length = math.floor(sr/2)

        #fmin, fmax = 256, 2048

        if len(y) > sr*7:#7秒以上のみ
            #打楽器抑制
            #x_stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
            #x_stft_harm, _ = librosa.decompose.hpss(x_stft, margin=1.2)
            #y_hpss = librosa.util.fix_length(librosa.istft(x_stft_harm, hop_length=hop_length), size=len(y))
            
            #fo_pyin, voiced_flag, voiced_prob = librosa.pyin(y=y,sr=sr,fmin=fmin, fmax=fmax,frame_length = 6615)#打楽器抑制使うと動かない!
            sc    = librosa.feature.spectral_centroid(y=y, n_fft=frame_length, hop_length=hop_length)[0]
            sc = np.append(sc,sc_max)
            sc    /= np.max(sc) # [0.0. 1.0]に正規化\
            sc = sc[:-1]

            rms   = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            rms = np.append(rms,rms_max)
            rms   /= np.max(rms) # [0.0. 1.0]に正規化
            rms = rms[:-1]

            #voiced_flag_as = voiced_flag.astype(dtype=np.int8)#false->0 true->1

            #avg_voicefrag = np.average(voiced_flag_as)
            score = 0.0

            score = np.average(sc + rms)*1.2
            score += np.amax(sc + rms)
            if len(y)/sr > 16:#15秒以上で増量
                score += 0.4

            #if avg_voicefrag < 0.14:#ボイスフラグが4割以下なら無効
                #score = 0
            return score,0
        else:
            return 0,0

    #短期フーリエ

    stft_p = 1024

    D = librosa.stft(y,n_fft=1024,hop_length=math.floor(stft_p/4))  # STFT
    #D = librosa.stft(y_inst,n_fft=1024,hop_length=math.floor(stft_p/4))  # STFT
    S, phase = librosa.magphase(D)  # 複素数を強度と位相へ変換
    stft_res = librosa.amplitude_to_db(S)  # 強度をdb単位へ変換

    #区間予測

    algo = ruptures.KernelCPD(kernel="linear").fit(stft_res.T)

    n_bkps_max = 20  # K_max

    _ = algo.predict(n_bkps_max)

    array_of_n_bkps = np.arange(1, n_bkps_max + 1)


    n_bkps = 10 #標準区切り数

    if len(y)/sr < 80:
        n_bkps = 8
    if len(y)/sr < 60:
        n_bkps = 6

    bkps = algo.predict(n_bkps=n_bkps)
    # Convert the estimated change points (frame counts) to actual timestamps
    bkps_times = librosa.frames_to_time(bkps, sr=sr, hop_length=math.floor(stft_p/4))
    bkps_time_indexes = (sr * bkps_times).astype(int).tolist()

    #サビ評価値取得

    chorus_point_max_index = 0
    chorus_point_max = 0
    for (segment_number, (start, end)) in enumerate(ruptures.utils.pairwise([0] + bkps_time_indexes), start=1):
        if start/sr>len(y)/sr/5:
            #now_y = y_origin[start*sampling_rate_change:end*sampling_rate_change]
            now_y = y_origin[start*sampling_rate_change:end*sampling_rate_change]
            #now_y = y_origin[start:end]
            n_score,bf = rms_sc(now_y,sampling_rate_origin)
            if n_score > chorus_point_max:
                chorus_point_max = n_score
                chorus_point_max_index = segment_number
            #print("now_score " + str(n_score) + "\t voice_flag" + str(bf) + "\t nowindex:" + str(segment_number))
    chorus_start = -1
    chorus_end = -1
    chorus_length = 0
    for (segment_number, (start, end)) in enumerate(ruptures.utils.pairwise([0] + bkps_time_indexes), start=1):
        try:
            #segment = signal_origin[start*sampling_rate_change:end*sampling_rate_change]
            #if start*sampling_rate_change<nindex_chrous and nindex_chrous<end*sampling_rate_change:
                #print("This is chorous" + str(times[indices[0]]))
            if segment_number == chorus_point_max_index:
                #print("This in chorus!")
                chorus_start = start/sr
                chorus_end = end/sr
                chorus_length = (end - start)/sr
                
            #print(f"Segment n°{segment_number} (duration: {str((end - start)/sr)} s) start at{str(start/sr)} s")
            #display(Audio(data=segment, rate=math.floor(sampling_rate*sampling_rate_change)))
        except:
            pass
    #重い使わない配列を開放
    del y
    del y_origin
    del D
    del S
    del stft_res

    return videoid,[really_starttime,really_endtime],[chorus_start,chorus_end + length_plus,chorus_length]#,np.average(np.abs(result_box))

if __name__=="__main__":
    try:
        if sys.argv[1].lower()=="file":
            jsfilepass:str = sys.argv[2]
            jsfilepass = os.path.abspath(jsfilepass)
            return_json_dict:dict = {}
            with open(jsfilepass,"r") as f:
                jsf:dict = json.load(f)
            load_vid:list[str] = jsf["videoid"]
            for r in load_vid:
                try:
                    print("start:\t" + r)
                    nvid,timedata,chorusdata = youtube_music_analyze(r)
                    return_json_dict[nvid] = {"timedata":timedata,"chorusdata":chorusdata}
                except:
                    pass
            #filename_path = os.path.basename(jsfilepass)
            with open(jsfilepass[:-5] + "_return.json","w") as f:
                json.dump(return_json_dict,f)
        elif sys.argv[1]!=None:
            print(youtube_music_analyze(sys.argv[1]))
    except:
        vid = input("videoid_input:\t")
        print(youtube_music_analyze(vid))
