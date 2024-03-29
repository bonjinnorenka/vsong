function load_chart(){
    if (window.matchMedia('(prefers-color-scheme: dark)').matches === !0) {
        Chart.defaults.color = '#c0c0c0';
    } else {
        Chart.defaults.color = '#3f4551';
    }
}

const shuffle = ([...array]) => {
    for (let i = array.length - 1; i >= 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

let chart_instance = {};

function Chart_cleater_single_v1(id_c,label,content,content_name){
    try{
        chart_instance[id_c].destroy(); 
    }
    catch{}
    chart_instance[id_c] = new Chart(document.getElementById(id_c), {
        type: 'line',
        data: {
            labels: label,
            datasets: [{
                label: content_name,
                data: content,
                borderColor: 'rgb(56, 161, 219)',
                backgroundColor: 'rgb(56, 161, 219)',
            }]
        },
        options: {
            responsive: !0
        }
    })
}

function page_transition(){//ページ移動時万が一あると問題が起こる可能性があるグローバル変数を削除
    delete now_music_name;
    delete counter_down;
    delete counter_up;
    delete load_max;
    delete maxlength;
    delete nowvid;
    delete statistics_data;
    delete now_nick_name;
    delete search_index_data;
    delete top_result;
    delete sub_result;
    chart_instance = {};
    try{
        document.getElementById('lib_search').removeEventListener("input",search_index);
        document.getElementById('lib_search').removeEventListener("change",search_index_finish);
    }
    catch{}
}

let nowpage_allplaylist = [];

function recommend_music_scroll(kind=0){
    let maindoc = document.getElementById("music_recommend");
    if(kind==0){//進
        maindoc.scrollBy(window.innerWidth-100,0);
    }
    else if (kind==1){//戻る
        maindoc.scrollBy(100 - window.innerWidth,0);
    }
}

function latest_music_scroll(kind=0){
    let maindoc = document.getElementById("latest_music");
    if(kind==0){//進
        maindoc.scrollBy(window.innerWidth-100,0);
    }
    else if (kind==1){//戻る
        maindoc.scrollBy(100 - window.innerWidth,0);
    }

}

function recommend_ch_scroll(kind=0){
    let maindoc = document.getElementById("ch_recommend");
    if(kind==0){//進
        maindoc.scrollBy(window.innerWidth-100,0);
    }
    else if (kind==1){//戻る
        maindoc.scrollBy(100 - window.innerWidth,0);
    }
}

function owner_recommend_scroll(kind=0){
    let maindoc = document.getElementById("ownerrecommend_music");
    if(kind==0){//進
        maindoc.scrollBy(window.innerWidth-100,0);
    }
    else if (kind==1){//戻る
        maindoc.scrollBy(100 - window.innerWidth,0);
    }
}

function change_graph_music(g_name){
    let elements = document.getElementsByName(g_name+"_ra");
    var nown = 0;
    for (let x = 0;x<elements.length;x++){
        if (elements.item(x).checked){
            nown = x;
        }
    }
    let kind = ["視聴回数","高評価","コメント数"];
    if(g_name=="sum-yt"){
        let nowmusic_name = decodeURI(String(location.pathname).slice(7,-1));//すでに置き換え済み
        let musicapi_xhr = new XMLHttpRequest();
        musicapi_xhr.open("GET","/api/v4/music/" + dir_replace(nowmusic_name) + ".json");
        musicapi_xhr.responseType = "json";
        musicapi_xhr.send();
        musicapi_xhr.onload = function(){
            let nowjson = musicapi_xhr.response;
            Chart_cleater_single_v1("sum-yt",nowjson["statisticsdata"][1],nowjson["statisticsdata"][nown+2],kind[nown]);
        }
    }
    else{
        let vidapi_xhr = new XMLHttpRequest();
        vidapi_xhr.open("GET","/api/v4/videoid/" + g_name + ".json");
        vidapi_xhr.responseType = "json";
        vidapi_xhr.send();
        vidapi_xhr.onload = function(){
            let nowjson = vidapi_xhr.response;
            Chart_cleater_single_v1(g_name,nowjson["statisticsdata"][1],nowjson["statisticsdata"][nown+2],kind[nown]);
        }
    }
}

function change_graph_ch(g_name){
    //キャンバス初期化
    try{
        chart_instance[g_name].destroy(); 
    }
    catch{}
    let nowchname = decodeURI(String(location.pathname).slice(4,-1));
    let elements = document.getElementsByName(g_name+"_ra");
    var nown = 0;
    for (let x = 0;x<elements.length;x++){
        if (elements.item(x).checked){
            nown = x;
        }
    }
    let kind = ["視聴回数","高評価","コメント数"];
    if(g_name=="sum-yt"){
        let chapi_xhr = new XMLHttpRequest();
        chapi_xhr.open("GET","/api/v4/ch/" + dir_replace(nowchname) + ".json");
        chapi_xhr.responseType = "json";
        chapi_xhr.send();
        chapi_xhr.onload = function(){
            let nowjson = chapi_xhr.response;
            Chart_cleater_single_v1(g_name,nowjson["statisticsdata"][1],nowjson["statisticsdata"][nown+2],kind[nown]);
        }
    }
    else{
        let vidapi_xhr = new XMLHttpRequest();
        vidapi_xhr.open("GET","/api/v4/videoid/" + g_name + ".json");
        vidapi_xhr.responseType = "json";
        vidapi_xhr.send();
        vidapi_xhr.onload = function(){
            let nowjson = vidapi_xhr.response;
            Chart_cleater_single_v1(g_name,nowjson["statisticsdata"][1],nowjson["statisticsdata"][nown+2],kind[nown]);
        }
    }
}

function ch_page_load(){
    let nowchname = decodeURI(String(location.pathname).slice(4,-1));
    let chapi_xhr = new XMLHttpRequest();
    chapi_xhr.open("GET","/api/v4/ch/" + dir_replace(nowchname) + ".json");
    chapi_xhr.responseType = "json";
    chapi_xhr.send();
    chapi_xhr.onload = function(){
        let nowjson = chapi_xhr.response;
        Chart_cleater_single_v1("sum-yt",nowjson["statisticsdata"][1],nowjson["statisticsdata"][2],"視聴回数");
        nowpage_allplaylist = nowjson["videolist"];
    }
    load_max = 0;
    recommend();
    ytviewchange()
}

function music_page_load(){
    let nowmusic_name = decodeURI(String(location.pathname).slice(7,-1));//すでに置き換え済み
    let musicapi_xhr = new XMLHttpRequest();
    musicapi_xhr.open("GET","/api/v4/music/" + nowmusic_name + ".json");
    musicapi_xhr.responseType = "json";
    musicapi_xhr.send();
    musicapi_xhr.onload = function(){
        let nowjson = musicapi_xhr.response;
        Chart_cleater_single_v1("sum-yt",nowjson["statisticsdata"][1],nowjson["statisticsdata"][2],"視聴回数");
        nowpage_allplaylist = nowjson["videolist"];
    }
    load_max = 0;
    recommend();
    ytviewchange()
}

let load_max = 0;

function musittop_load(){
    let url_parm = new URL(window.location.href).searchParams;
    let urp = new URLSearchParams(new URL(window.location.href));
    let now_ran;
    if (url_parm.get('ran') != null) {
        now_ran = url_parm.get('ran');
    } else {
        now_ran = Math.floor(Math.random() * 100);
        urp.delete("tbdid");
        urp.set("ran", String(now_ran));
        history.replaceState(null, null, "?" + urp.toString());
    }
    let musictop_xhr = new XMLHttpRequest();
    musictop_xhr.open("GET","/ajax/music-top/mct-" + String(now_ran) + ".json");
    musictop_xhr.responseType = "json";
    musictop_xhr.send();
    musictop_xhr.onload = function(){
        now_j = musictop_xhr.response;
        now_j = now_j["index"];
        let p_doc = document.getElementById("music_top");
        for(let r = 0;r<50;r++){
            var now_el = document.createElement("div");
            now_el.classList.add("music_top_space");
            now_el.innerHTML = '<a href="' + now_j[r][2] + '" onClick="page_ajax_load(\"' + now_j[r][2] + '\");return false"><span class="ofoverflow_320" title="' + now_j[r][1] +'">' + now_j[r][1] + '</span><br><img src="https://i.ytimg.com/vi_webp/' + now_j[r][0] + '/mqdefault.webp"</a>';
            p_doc.appendChild(now_el);
        }
    }
}

function allplay(){
    now_playlist = nowpage_allplaylist;
    sync_playlist()
    yt_skip();
}

function recommend(kind=""){
    if(load_max===0){
        load_max++;
        let url_parm = new URL(window.location.href).searchParams;
        let urp = new URLSearchParams(new URL(window.location.href));
        if (url_parm.get('ran') != null) {
            now_ran = url_parm.get('ran');
        } else {
            now_ran = Math.floor(Math.random() * 100);
            urp.delete("tbdid");
            urp.set("ran", String(now_ran));
            history.replaceState(null, null, "?" + urp.toString());
        }
        let request_mr = new XMLHttpRequest();
        request_mr.open("GET", "/ajax/music/mr-" + String(now_ran) + ".json");
        request_mr.responseType = "json";
        request_mr.send();
        request_mr.onload = function () {//音楽のほう
            const res_mr = request_mr.response;
            let divm = document.getElementById("music_recommend");
            divm.innerHTML = '<button type="button" class="musicbt musicundo" onclick="recommend_music_scroll(1)"><img class="music-bt inversion_pic" src="/util/nextbt.svg"></button><button type="button" class="musicbt musicnext" onclick="recommend_music_scroll(0)"><img class="music-bt" src="/util/nextbt.svg"></button>'
            if (isMobile.any){
                let nowdoc = document.getElementsByClassName("musicbt");
                for (let x = 0;x<nowdoc.length;x++){
                    nowdoc[x].classList.add("dis_none");
                }
            }
            if (kind===""){
                document.getElementById("descm").innerHTML = '<hr><p class="other_music">他のおすすめの曲</p>';
            }
            let vivm_chache = divm.innerHTML;
            for (let i = 0; i < 20; i++) {
                vivm_chache += "<a href='/music/" + res_mr[i][1] +
                    "/' onclick='page_ajax_load(\"/music/" + res_mr[i][1] + "/\");return false' title='" + res_mr[i][0] + "'>" + res_mr[i][0] + "<img class='fit-cut' src='https://i.ytimg.com/vi_webp/" +
                    res_mr[i][2] + "/hqdefault.webp' alt='" + res_mr[i][0] + "' width='320' height='180'></a>";
            }
            divm.innerHTML = vivm_chache;
        };
        let request_cr = new XMLHttpRequest();
        request_cr.open("GET", "/ajax/ch/cr-" + String(now_ran) + ".json");
        request_cr.responseType = "json";
        request_cr.send();
        request_cr.onload = function () {//チャンネルのほう
            const res_cr = request_cr.response;
            let divc = document.getElementById("ch_recommend");
            divc.innerHTML = '<button type="button" class="chbt chundo" onclick="recommend_ch_scroll(1)"><img class="ch-bt inversion_pic" src="/util/nextbt.svg"></button><button type="button" class="chbt chnext" onclick="recommend_ch_scroll(0)"><img class="ch-bt" src="/util/nextbt.svg"></button>';
            if (isMobile.any){
                let nowdoc = document.getElementsByClassName("chbt");
                for (let x = 0;x<nowdoc.length;x++){
                    nowdoc[x].classList.add("dis_none");
                }
            }
            if (kind===""){
                document.getElementById("descc").innerHTML = '<hr><p class="other_music">他のおすすめのVtuber</p>';
            }
            let divc_cache = divc.innerHTML;
            for (let i = 0; i < 20; i++) {
                divc_cache += "<a href='/ch/" + res_cr[i][1] +
                    "/' onclick='page_ajax_load(\"/ch/" + res_cr[i][1] + "/\");return false' title='" + res_cr[i][0] + "'><span class='ofoverflow'>" + res_cr[i][0] +
                    "</span><img class='recommend-ch' src='" + res_cr[i][2] + "' alt='" + res_cr[i][0] +
                    "' width='120' height='120'></a>";
            }
            divc.innerHTML = divc_cache;
        }
        if (kind=="top"){
            let latestapi_xhr = new XMLHttpRequest();
            latestapi_xhr.open("GET","/api/latest.json");
            latestapi_xhr.responseType = "json";
            latestapi_xhr.send();
            latestapi_xhr.onload = function(){
                let now_j = latestapi_xhr.response;
                let nowlong = now_j["index"].length;
                let nowdoc = document.getElementById("latest_music");
                let nowdoc_cache = nowdoc.innerHTML;
                for (let x = 0;x<nowlong;x++){
                    nowdoc_cache += "<div><span class='ofoverflow_320' title='" + now_j["index"][x][1] + "'>" + now_j["index"][x][1] + "</span><lite-youtube id='iframe-" + now_j["index"][x][0] + "' videoid='" + now_j["index"][x][0] + "' width='320' height='180'></lite-youtube></div>"
                }
                nowdoc_cache += '<button type="button" class="musicbt latestundo" onclick="latest_music_scroll(1)"><img id="vs_latest_movie_undo_pic" class="music-bt inversion_pic" src="/util/nextbt.svg"></button><button type="button" class="musicbt latestnext" onclick="latest_music_scroll(0)"><img id="vs_latest_movie_next_pic" class="music-bt" src="/util/nextbt.svg"></button>';
                nowdoc.innerHTML = nowdoc_cache;
                if (isMobile.any){
                    let nowdoc = document.getElementsByClassName("musicbt");
                    for (let x = 0;x<nowdoc.length;x++){
                        nowdoc[x].classList.add("dis_none");
                    }
                }
            }
            let owreco_music_xhr = new XMLHttpRequest();
            owreco_music_xhr.open("GET","/api/recommend.json");
            owreco_music_xhr.responseType = "json";
            owreco_music_xhr.send();
            owreco_music_xhr.onload = function(){
                let now_j = owreco_music_xhr.response;
                let now_data = now_j["index"];
                now_data = arrayShuffle_second(now_data);
                let nowloop = now_data.length;
                if (nowloop > 20){
                    nowloop = 20;
                }
                let owner_recommend_doc = document.getElementById("ownerrecommend_music");
                let owrec_chache = owner_recommend_doc.innerHTML;
                for (let x = 0;x<nowloop;x++){
                    owrec_chache += "<div><span class='ofoverflow_320' title='" + now_data[x][1] + "'>" + now_data[x][1] + "</span><lite-youtube id='iframe-" + now_data[x][0] + "' videoid='" + now_data[x][0] + "' width='320' height='180'></lite-youtube></div>"
                }
                owrec_chache += '<button type="button" class="musicbt ow_recommendundo" onclick="owner_recommend_scroll(1)"><img id="vs_owner_recommend_undo_pic" class="music-bt inversion_pic" src="/util/nextbt.svg"></button><button type="button" class="musicbt ow_recommendnext" onclick="owner_recommend_scroll(0)"><img id="vs_owner_recommend_next_pic" class="music-bt" src="/util/nextbt.svg"></button>';
                owner_recommend_doc.innerHTML = owrec_chache;
            }
        }
    }
}

function arrayShuffle_second(array) {
    var k, t, len;
    len = array.length;
    if (len < 2) {
        return array;
    }
    while (len) {
        k = Math.floor(Math.random() * len--);
        t = array[k];
        array[k] = array[len];
        array[len] = t;
    }
    return array;
}
  

function getClosestNum(num, ar){
    var closest;
    if(Object.prototype.toString.call(ar) ==='[object Array]' && ar.length>0){
      closest = ar[0];
      for(var i=0;i<ar.length;i++){ 
         var closestDiff = Math.abs(num - closest);
         var currentDiff = Math.abs(num - ar[i]);
         if(currentDiff < closestDiff){
             closest = ar[i];
         }
       }
       return closest;
     }
  return false;
}

function search_index_finish(){
    //search_index();
    if (top_result.length==1){
        page_ajax_load(top_result[0][1]);
    }
    else if (sub_result.length==1){
        page_ajax_load(sub_result[0][1]);
    }
    else if (sub_result.length==0){
        document.getElementById("search_result").innerText = "すみません1件も見つかりませんでした.";
    }
}

function japan_smallToBig(nowst){
    let retst = nowst.replaceAll("ぁ","あ").replaceAll("ぃ","い").replaceAll("ぅ","う").replaceAll("ぇ","え").replaceAll("ぉ","お").replaceAll("っ","つ").replaceAll("ゃ","や").replaceAll("ゅ","ゆ").replaceAll("ょ","よ").replaceAll("ァ","あ").replaceAll("ィ","い").replaceAll("ゥ","う").replaceAll("ェ","え").replaceAll("ォ","お").replaceAll("ッ","つ").replaceAll("ャ","や").replaceAll("ュ","ゆ").replaceAll("ョ","よ")
    return retst
}

let latest_time = 0;

function FdToSd(now_ar){
    if (now_ar.length%2==1){
        return false
    }
    let k_ar = [];
    for (c = 0;c<(now_ar.length/2);c++){
        k_ar.push([now_ar[2*c],now_ar[2*c+1]]);
    }
    return k_ar
}

function search_index_finish(){
    search_index(line="on");
}

function search_index(line="none"){
    top_result = [];
    sub_result = [];
    let now_query_st = document.getElementById("lib_search").value;
    if(now_query_st!=""){
        history.replaceState(null,null,location.pathname + "?q=" + now_query_st);
    }
    else{
        history.replaceState(null,null,location.pathname);
    }
    let now_svalue = now_query_st.toLowerCase();
    now_svalue = japan_smallToBig(now_svalue);
    now_svalue = now_svalue.replaceAll(/[ァ-ン]/g, function(s) {return String.fromCharCode(s.charCodeAt(0) - 0x60);});//内部処理用にカタカナを平仮名に変換
    now_svalue = now_svalue.replaceAll(/[！-～]/g,function(s) {return String.fromCharCode(s.charCodeAt(0) - 0xFEE0);});//内部処理用に全角英数字を半角に変換
    now_svalue = now_svalue.replaceAll(" ","").replaceAll("　","");//半角と全角の空白をなくす
    if(now_svalue==""||(now_svalue[0].match(/^[A-Za-z0-9]+/)==null&&now_svalue[now_svalue.length-1].match(/^[A-Za-z0-9]+/)!=null&&line!="on")){//空か入力途中なら除外か最初が英数字でないかつ最後が英数字の時は検索除外
        if(now_svalue==""){
            document.getElementById("search_result").innerHTML = "";
        }
        return
    }
    let search_xhr = new XMLHttpRequest();
    search_xhr.open("GET","/cgi-bin/search.cgi?q=" + now_svalue);
    search_xhr.responseType = "json";
    search_xhr.send();
    search_xhr.onload = function(){
        let now_search_res = search_xhr.response;
        if (now_search_res["st_time"]<latest_time){//最新の結果ではない
            return
        }
        latest_time = now_search_res["st_time"];
        top_result = FdToSd(now_search_res["top_hit"]);
        sub_result = FdToSd(now_search_res["sub_hit"]);
        let result_area = document.getElementById("search_result")
        let k_strin = "";
        if (top_result.length==1){
            k_strin = "<a href='" + top_result[0][1] + "' onClick='page_ajax_load(\"" + top_result[0][1] + "\");return false'>" + top_result[0][0] + "</a><br>"
        }
        for(var nint=0;nint<sub_result.length;nint++){
            if (top_result.length!=1){
                k_strin = k_strin + "<a href='" + sub_result[nint][1] + "' onClick='page_ajax_load(\"" + sub_result[nint][1] + "\");return false'>" + sub_result[nint][0] + "</a><br>";
            }
            else if(sub_result[nint]!==top_result[0]){
                k_strin = k_strin + "<a href='" + sub_result[nint][1] + "' onClick='page_ajax_load(\"" + sub_result[nint][1] + "\");return false'>" + sub_result[nint][0] + "</a><br>";
            }
        }
        result_area.innerHTML = k_strin;
        if(k_strin==""){
            result_area.innerText = "すみません１件も見つかりませんでした";
        }
    }
}

function page_ajax_load(htmlpass,ig=0){
    //特殊処理
    console.log(location.pathname)
    if(watch_page_st===1){//視聴ページのサイズを元に戻しクラスを振りなおす
        let yt_el = document.getElementById("youtube-iframe");
        let vw = window.innerWidth;
        let yt_window_size;
        if (vw<600){//スマホ向け　全力表示
            yt_window_size = Math.floor(vw*0.98);
        }
        else{//タブレット向け
            yt_window_size = 500;
        }
        yt_el.width = yt_window_size;
        yt_el.height = Math.floor(yt_window_size*0.5625);
        yt_el.classList.remove("watch_yt_center");
        document.getElementById("ytembed").classList.add("float_right");
        watch_page_st = 0;
        document.getElementById("yt_display").classList.remove("dis_none");
    }
    let page_ajax_xhr = new XMLHttpRequest();
    page_ajax_xhr.open("GET",new URL("https://vsong.fans"+htmlpass).pathname);
    page_ajax_xhr.responseType = "document";
    page_ajax_xhr.send();
    page_ajax_xhr.onload = function(){
        const ajax_html = page_ajax_xhr.response;
        let ajax_head = ajax_html.querySelector("head");
        let ajax_main = ajax_html.querySelector("main");
        //書き換え
        document.querySelector("head").innerHTML = ajax_head.innerHTML;
        document.querySelector("main").innerHTML = ajax_main.innerHTML;
        if (ig===0){//次のページに行くとき
            history.pushState(null,null,htmlpass);
            window.scrollTo(0,0);
        }
        if (ig===1){//戻っちゃうとき
            history.replaceState(null,null,htmlpass);
        }
        console.log(htmlpass);
        page_load();
    }
}

function search_index_load(){
    document.getElementById('lib_search').addEventListener("input",search_index);
    document.getElementById('lib_search').addEventListener("change",search_index_finish);
    document.getElementById('lib_search').focus();
    search_index();
}

//lite-youtube-embed https://github.com/paulirish/lite-youtube-embed
class LiteYTEmbed extends HTMLElement {
    connectedCallback() {
        this.videoId = this.getAttribute('videoid');
        let playBtnEl = this.querySelector('.lty-playbtn');
        this.playLabel = (playBtnEl && playBtnEl.textContent.trim()) || this.getAttribute('playlabel') || 'Play';
        this.id = "iframe-" + this.videoId;
        if (!this.style.backgroundImage) {
          this.style.backgroundImage = `url("https://i.ytimg.com/vi_webp/${this.videoId}/hqdefault.webp")`;
        }
        if (!playBtnEl) {
            playBtnEl = document.createElement('button');
            playBtnEl.type = 'button';
            playBtnEl.classList.add('lty-playbtn');
            this.append(playBtnEl);
        }
        if (!playBtnEl.textContent) {
            const playBtnLabelEl = document.createElement('span');
            playBtnLabelEl.className = 'lyt-visually-hidden';
            playBtnLabelEl.textContent = this.playLabel;
            playBtnEl.append(playBtnLabelEl);
        }
        this.addEventListener('pointerover', LiteYTEmbed.warmConnections, {once: true});
        this.addEventListener('click', this.addIframe);
        this.addEventListener('contextmenu', this.addPlaylist);
    }
    static addPrefetch(kind, url, as) {
        const linkEl = document.createElement('link');
        linkEl.rel = kind;
        linkEl.href = url;
        if (as) {
            linkEl.as = as;
        }
        document.head.append(linkEl);
    }
    static warmConnections() {
        if (LiteYTEmbed.preconnected) return;
        LiteYTEmbed.addPrefetch('preconnect', 'https://www.youtube-nocookie.com');
        LiteYTEmbed.addPrefetch('preconnect', 'https://www.google.com');
        LiteYTEmbed.preconnected = false;
    }
    addIframe(e) {
        if (this.classList.contains('lyt-activated')) return;
        e.preventDefault();
        this.classList.add('lyt-activated');
        //load_youtubeapi_player(this.videoId);
        ask_load_youtube(this.videoId);
    }
    addPlaylist(e){
        e.preventDefault();
        now_playlist.push(this.videoId);
        sync_playlist()//プレイリスト同期
        if(document.getElementById("yt_pl_idel").classList.contains("dis_none")==false&&document.getElementById("radio-side-pl").checked){//サイドバーが開かつプレイリストを見てるとき順番を更新
            view_playlist();
        }
    }
}
customElements.define('lite-youtube', LiteYTEmbed);
// End of the lite-youtube-embed

function ask_load_youtube(videoid){
    if (now_playlist.length > 0){
        let res = window.confirm("現在の再生リストを削除し再生しますか？");
        if (res){
            now_playlist = [];
            load_youtubeapi_player(videoid);
        }
        else{
            now_playlist.push(videoid);
        }
        sync_playlist()
    }
    else{
        load_youtubeapi_player(videoid);
    }
}

let now_player = "";
let before_playing = "";

let now_videoid;
let nowseek;
let defaut_videoid = "WF9P_NXHh5M";

function youtube_embed_preload(){
    //最新の情報を得る
    vsongdb.array_list.where("arrayname")
        .equals("latest_playdata")
        .limit(1)
        .toArray()
        .then(function(ndtobj){
            let ndt;
            try{
                ndt = ndtobj[0]["arraydata"];
            }
            catch{}
            try{
                now_videoid = ndt.videoid;
                nowseek = ndt.playtime;
            }
            catch{
                now_videoid = defaut_videoid;
                nowseek = 0;
            }
            if (now_videoid == null){
                now_videoid = defaut_videoid;
            }
            if (nowseek == NaN){
                nowseek = 0;
            }
            let ytembed_el = document.getElementById("ytembed");
            if(ytembed_el.innerHTML=='<div id=\"youtube-iframe\"></div>'||now_player==""){
                if(now_videoid!=defaut_videoid){
                    try{
                        document.getElementById("control_panel").classList.remove("dis_none");
                    }
                    catch{}
                }
                ytembed_el.classList.add("float_right");
                ytembed_el.classList.remove("dis_none");
                let vw = window.innerWidth;
                let yt_window_size;
                if (vw<600){//スマホ向け　全力表示
                    yt_window_size = Math.floor(vw*0.98);
                }
                else{//タブレット向け
                    yt_window_size = 500;
                }
                now_player = new YT.Player("youtube-iframe", {
                    width: yt_window_size,
                    height: Math.floor(yt_window_size * 0.5625),
                    videoId: now_videoid,
                    host: 'https://www.youtube-nocookie.com',
                    playerVars: {start: Math.ceil(nowseek),
                        disablekb: 1,
                        controls: 0},
                    events: {
                        'onError': yt_skip
                    }
                })
                now_player.addEventListener("onStateChange",yt_state_change);
                now_player.addEventListener("onReady",youtube_embed_preload_stop);
            }
        })
    
}

let playtime_data = [0,0,0,0];//本当のスタート,位置表示用のスタート,終わり,位置表示スタートから終わりまでの時間

function youtube_embed_preload_stop(){
    if (now_videoid==defaut_videoid){
        now_player.stopVideo();
    }
    before_playing = now_videoid;
    yt_music_display();
    now_player.removeEventListener('onReady',youtube_embed_preload_stop);
    if (now_videoid!=defaut_videoid){
        try{
            document.getElementById("yt-player-time").value = (nowseek/now_player.getDuration())*100;
        }
        catch{}
        load_youtubeapi_player(now_video_id=now_videoid,startsec=nowseek,mode="cue")
    }
    load_playlist();
}

function load_youtubeapi_player(now_video_id,startsec=0,mode="play"){
    if (before_playing!=""){
        try{
            document.getElementById("iframe-" + before_playing).classList.remove("lyt-activated");
        }
        catch{}
    }
    try{
        document.getElementById("control_panel").classList.remove("dis_none");
    }
    catch{}
    before_playing = now_video_id;
    let ytembed_el = document.getElementById("ytembed");
    if (mode=="play"){
        add_songhistory(now_video_id);
    }
    if(ytembed_el.innerHTML=='<div id=\"youtube-iframe\"></div>'||now_player==""){
        let vw = window.innerWidth;
        let yt_window_size;
        if (vw<600){//スマホ向け　全力表示
            yt_window_size = Math.floor(vw*0.98);
        }
        else{//タブレット向け
            yt_window_size = 500;
        }
        now_player = new YT.Player("youtube-iframe", {
            width: yt_window_size,
            height: Math.floor(yt_window_size * 0.5625),
            videoId: now_video_id,
            host: 'https://www.youtube-nocookie.com',
            playerVars: {'autoplay': 1},
            events: {
                'onStateChange': yt_state_change,
                'onReady': yt_sm_play,
                'onError': yt_skip
            }
        })
        ytembed_el.classList.add("float_right");
        //document.getElementById("ytembed").classList.remove("pos-none");
    }
    else{
        let videoid_api_xhr = new XMLHttpRequest();
        videoid_api_xhr.open("GET","/api/v4/videoid/" + now_video_id + ".json");
        videoid_api_xhr.responseType = "json";
        videoid_api_xhr.send();
        videoid_api_xhr.onload = function(){
            let json_res = videoid_api_xhr.response;
            let start = 0;
            let end = 0;
            if (main_option_data["watch_music_mode"]==0){
                start = 0;
                end = json_res["movietime"];
            }
            else if (main_option_data["watch_music_mode"]==1){
                start = json_res["songtime"][0];
                end = json_res["songtime"][1];
            }
            else if (main_option_data["watch_music_mode"]==2){
                start = json_res["chorusdata"][0];
                end = json_res["chorusdata"][1];
            }

            let datastart = start;

            if (startsec!=0){//開始位置の指定がある場合はそれで上書き
                start = startsec;
            }

            if (mode=="play"){
                now_player.loadVideoById({videoId:now_video_id,startSeconds:start,endSeconds:end});
                console.log("start_playing(load):\t" + now_video_id);
            }
            else if (mode=="cue"){
                now_player.cueVideoById({videoId:now_video_id,startSeconds:start,endSeconds:end})
                console.log("load_playing(cue):\t" + now_video_id);
            }
            playtime_data = [start,datastart,end,end-datastart];
            yt_music_display();
        }
    }
}

function yt_sm_play(){//スマホ自動開始用
    console.log("ready!")
    now_player.playVideo();
    yt_music_display();
    if (navigator.userAgent.match(/iPhone|Android.+Mobile/)) {
        yt_display();
    }
}

function yt_volume_change(){
    try{
        now_player.setVolume(document.getElementById("yt_sound_volume").value);
    }
    catch{}
}

function yt_display(){
    document.getElementById("ytembed").classList.toggle("pos-none");
    let button_el = document.getElementById("yt_display")
    if(document.getElementById("ytembed").classList.contains("pos-none")){
        button_el.innerText = "表示";
    }
    else{
        button_el.innerText = "非表示";
    }
}

let seek_interval;
window.addEventListener("keydown", (e)=>{keybord_yt(e)});
let playlock = false;

function yt_state_change(){//再生の状態に応じてバーを更新するかを選択
    let st = now_player.getPlayerState();
    let ytpbt_el = document.getElementById("yt-playbt");
    if(st==1){//再生開始時
        seek_interval = setInterval(youtube_seekbar, 500);
        ytpbt_el.innerHTML = '<img src="/util/pausebtn.svg" class="control_icon">';
        ytpbt_el.title = "一時停止する";
    }
    else if (st==0||st==2){//再生停止時
        clearInterval(seek_interval);
        ytpbt_el.innerHTML = '<img src="/util/playbtn.svg" class="control_icon">';
        ytpbt_el.title = "再生する";
        let player_gd_er = false;
        if (now_player.getDuration()===0){//うまく取得できていないとき
            player_gd_er = true;
        }
        if((document.getElementById("autoload_check").checked||now_playlist.length>0)&&Math.floor(playtime_data[0]+playtime_data[3])<Math.floor(now_player.getCurrentTime())+5&&playlock==false&&player_gd_er==false){//自動再生あり
            yt_skip();
        }
        else{
            playlock = false;
        }
    }
}

function yt_music_display(){
    let vidapi_xhr = new XMLHttpRequest();
    vidapi_xhr.open("GET","/api/v4/videoid/" + before_playing + ".json");
    vidapi_xhr.responseType = "json";
    vidapi_xhr.send();
    vidapi_xhr.onload = function(){
        if(this.status==404){
            let yt_md_xhr = new XMLHttpRequest();
            yt_md_xhr.open("GET","https://www.youtube-nocookie.com/oembed?url=https://www.youtube.com/watch?v=" + before_playing + "&format=json");
            yt_md_xhr.responseType = "json";
            yt_md_xhr.send();
            yt_md_xhr.onload = function(){
                let yt_md_json = yt_md_xhr.response;
                let now_yt_title = yt_md_json["title"] + "/" + yt_md_json["author_name"];
                console.log(now_yt_title);
                document.getElementById("music_name_display").innerHTML = "<p class='p_kari'>" + now_yt_title + "</p>";
            }
        }
        else{
            let nowjson = vidapi_xhr.response;
            //メンバー名文字列生成
            let menst = "";
            for (let x = 0;x<nowjson["memberdata"].length;x++){
                menst += nowjson["memberdata"][x]["nickname"] + " ";
            }
            if (nowjson["groupname"]==""){
                document.getElementById("music_name_display").innerHTML = "<p class='p_kari'>" + nowjson["musicname"] + " / " + menst + "</p>"
            }
            else{
                document.getElementById("music_name_display").innerHTML = "<p class='p_kari'>" + nowjson["musicname"] + " / " + menst + "</p>"
            }
        }
    }
    
   /*
    let yt_md_xhr = new XMLHttpRequest();
    yt_md_xhr.open("GET","https://www.youtube-nocookie.com/oembed?url=https://www.youtube.com/watch?v=" + before_playing + "&format=json");
    yt_md_xhr.responseType = "json";
    yt_md_xhr.send();
    yt_md_xhr.onload = function(){
        let yt_md_json = yt_md_xhr.response;
        let now_yt_title = yt_md_json["title"] + "/" + yt_md_json["author_name"];
        console.log(now_yt_title);
        document.getElementById("music_name_display").innerHTML = "<p class='p_kari'>" + now_yt_title + "</p>";
    }
    */
}

let now_playlist = [];

function yt_skip(){
    try{
        document.getElementById("control_panel").classList.remove("dis_none");
    }
    catch{}
    let nowvid;
    if(now_playlist.length==0){//プレイリストが空の時
        let now_ran = Math.floor(Math.random() * 100);
        let playlist_xhr = new XMLHttpRequest();
        playlist_xhr.open("GET","/random_pl/ran" + String(now_ran) + ".json");
        playlist_xhr.responseType = "json";
        playlist_xhr.send();
        playlist_xhr.onload = function(){
            now_playlist = playlist_xhr.response[0];
            console.log(now_playlist);
            nowvid = now_playlist.shift();
            console.log("start_playing(skip):\t" + nowvid);
            load_youtubeapi_player(nowvid);
            before_playing = nowvid;
            yt_music_display();
            sync_playlist()
        } 
    }
    else{
        console.log("normal_next");
        nowvid = now_playlist.shift();
        sync_playlist()
        console.log("start_playing(skip):\t" + nowvid);
        load_youtubeapi_player(nowvid);
        before_playing = nowvid;
        yt_music_display();
    }
}

function keybord_yt(element){//キーボードで操作されたときに反応
    if (element.key=="MediaPlayPause"){
        try{
            yt_playorstop();
        }
        catch{}
    }
    else if (element.key=="MediaTrackNext"){
        try{
            yt_skip();
        }
        catch{}
    }
}

function yt_playorstop(){
    try{
        var st = now_player.getPlayerState();
    }
    catch{
        var st = -5
    }
    if(st==-1||st==2||st==3||st==5){
        now_player.playVideo();
    }
    else if (st==1){
        now_player.pauseVideo();
        playlock = true;
    }
}

function youtube_seekbar(){//バーを変えるやつ
    try{
        //document.getElementById("yt-player-time").value = (now_player.getCurrentTime()/now_player.getDuration())*100;
        document.getElementById("yt-player-time").value = ((now_player.getCurrentTime()-playtime_data[1])/playtime_data[3])*100;
    }
    catch{}
}

let watch_page_st = 0;

function watch_page_load(){
    document.getElementById("yt_ch_dismode").title = "小さな画面で表示";
    try{
        document.getElementById("youtube-iframe").classList.add("watch_yt_center");
        document.getElementById("ytembed").classList.remove("float_right","pos-none");
        document.getElementById("control_panel").classList.remove("dis_none");
        document.getElementById("yt_display").classList.add("dis_none");
    }
    catch{}
    let url_parm = new URL(window.location.href).searchParams;
    let urp = new URLSearchParams(new URL(window.location.href));
    let now_demand = url_parm.get("v");
    //widthから計算
    let vw = window.innerWidth;
    let yt_emb_width = 0;
    if (vw<600){
        yt_emb_width = Math.floor(vw * 0.98);
    }
    else if (vw<1000){
        yt_emb_width = Math.floor(vw * 0.75);
    }
    else{
        yt_emb_width = Math.floor(vw * 0.5);
    }

    if(now_demand==null){
        page_ajax_load("/");
        return
    }
    else if (now_demand==="normal"){//プレイヤーを引き継ぐ
        //現在のプレイヤーの情報を取得
        let yt_el = document.getElementById("youtube-iframe");
        yt_el.width = yt_emb_width;
        yt_el.height = Math.floor(yt_emb_width * 0.5625);
        yt_el.classList.add("watch_yt_center");
        let p_yt_el = document.getElementById("ytembed");
        p_yt_el.classList.remove("pos-none");
        p_yt_el.classList.remove("float_right");
        let nowvid = new URL(now_player.getVideoUrl()).searchParams.get("v");
        urp.set("v",nowvid);
        history.replaceState(null,null,location.pathname + urp.toString());
    }
    else if (now_demand.length==11){//動画プレイヤーを作成し指定された動画idで読み込む
        console.log("new youtube player!")
        before_playing = now_demand;
        if(now_player==""){
            now_player = new YT.Player("youtube-iframe", {
                width: yt_emb_width,
                height: Math.floor(yt_emb_width * 0.5625),
                videoId: now_demand,
                host: 'https://www.youtube-nocookie.com',
                playerVars: {'autoplay': 1},
                events: {
                    'onStateChange': yt_state_change,
                    'onReady': yt_sm_play,
                    'onError': yt_skip
                }
            });
            document.getElementById("youtube-iframe").classList.add("watch_yt_center");
            document.getElementById("youtube-iframe").classList.remove("float_right");
            yt_music_display();
        }
        else{
            let yt_el = document.getElementById("youtube-iframe");
            yt_el.width = yt_emb_width;
            yt_el.height = Math.floor(yt_emb_width * 0.5625);
            load_youtubeapi_player(now_demand);
            yt_music_display();
        }
    }
    watch_page_st = 1;
}

function yt_watchmode_ch(){
    let ytch_el = document.getElementById("yt_ch_dismode");
    if(watch_page_st===0){//通常時->動画ページに遷移
        page_ajax_load("/watch/?v=normal");
        ytch_el.title = "元のページに戻る";
    }
    else if(watch_page_st===1){
        history.back();
        ytch_el.title = "大画面で表示";
    }
}

let nowidlist = ["radio-todayhot","radio-todayhotter","radio-weekhot","radio-monthhot","radio-wholehot"];

function today_load(kind=-1,doc_kind="index"){
    let url_parm = new URL(window.location.href).searchParams;
    let urp = new URLSearchParams(new URL(window.location.href));
    let now_demand = url_parm.get("m");
    if (window.innerWidth<600){
        document.getElementById("radio-todayhot-l").innerText = "日刊\n(上昇率)";
        document.getElementById("radio-todayhotter-l").innerText = "日刊\n(再生数)";
        document.getElementById("radio-weekhot-l").innerText = "週刊";
        document.getElementById("radio-monthhot-l").innerText = "月刊";
        document.getElementById("radio-wholehot-l").innerText = "全期間";
    }
    if ((now_demand==null&&kind!=-1)||(now_demand!=kind&&kind!=-1)){
        urp.append("m",kind);
        if(url_parm.get("p")!=null){
            urp.append("p",url_parm.get("p"));
        }
        history.replaceState(null,null,"?"+urp.toString());
        document.getElementById(nowidlist[kind]).checked = true;
    }
    else if(now_demand!=null&&kind==-1){
        kind = now_demand;
        document.getElementById(nowidlist[kind]).checked = true;
    }
    if (kind==-1){
        kind = 0;
        document.getElementById("radio-todayhot").checked = true;
    }
    doc_kind = dir_replace(doc_kind);
    if (doc_kind!="index"){
        urp.append("p",doc_kind);
        if(url_parm.get("m")!=null){
            urp.append("m",url_parm.get("m"));
        }
        history.replaceState(null,null,"?"+urp.toString());
    }
    else if(doc_kind=="index"&&url_parm.get("p")!=null){
        doc_kind = url_parm.get("p");
    }
    if(doc_kind=="inde"){
        doc_kind = "index";
    }
    var today_xhr = new XMLHttpRequest();
    today_xhr.open("GET","/api/today/" + doc_kind + ".json");
    today_xhr.responseType = "json";
    today_xhr.send();
    today_xhr.onload = function(){
        let now_j_g = today_xhr.response;
        let now_j = now_j_g["index"];
        let h1_tag = document.querySelector("h1");
        let hotname_list = ["今日の人気曲","今日の人気曲","今週の人気曲","今月の人気曲","全期間人気曲"];
        nowpage_allplaylist = now_j_g["vidlist"][kind];
        h1_tag.innerHTML = '<button class="nbt_noborder" onclick="allplay()"><img class="control_icon" src="/util/cicle_playbtn.svg"></button>' + hotname_list[kind];
        let p_doc = document.getElementById("today_hot");
        p_doc.innerHTML = "";
        let object_length = 50;
        if (Object.keys(now_j[kind]).length < object_length){
            object_length = Object.keys(now_j[kind]).length;
        }
        now_j = now_j[kind];
        for(let r = 0;r<object_length;r++){
            var now_el = document.createElement("div");
            now_el.classList.add("today_hot_space");
            if (kind==0){
                now_el.innerHTML = '<span class="ofoverflow_320" title="' + now_j[r][1] +'">' + now_j[r][1] + '<br>' + now_j[r][2].toLocaleString() + '%増</span><br><lite-youtube videoid="' + now_j[r][0] +'" width="320" height="180"></lite-youtube>';
            }
            else if (kind==4){
                now_el.innerHTML = '<span class="ofoverflow_320" title="' + now_j[r][1] +'">' + now_j[r][1] + '<br>' + now_j[r][2].toLocaleString() + '回</span><br><lite-youtube videoid="' + now_j[r][0] +'" width="320" height="180"></lite-youtube>';
            }
            else if (kind > 0){
                now_el.innerHTML = '<span class="ofoverflow_320" title="' + now_j[r][1] +'">' + now_j[r][1] + '<br>' + now_j[r][2].toLocaleString() + '回増</span><br><lite-youtube videoid="' + now_j[r][0] +'" width="320" height="180"></lite-youtube>';
            }
            p_doc.appendChild(now_el);
        }
    }
    document.getElementById("radio-range").addEventListener("change",hotchange);
}

function hot_change_office(){
    for (let nown = 0;nown<nowidlist.length;nown++){
        if(document.getElementById(nowidlist[nown]).checked){
            today_load(kind=nown,document.getElementById("select-office").value);
        }
    }
}

function hotchange(){
    for (let nown = 0;nown<nowidlist.length;nown++){
        if(document.getElementById(nowidlist[nown]).checked){
            today_load(kind=nown);
        }
    }
}

function hot_chose_load(){
    var today_select_xhr = new XMLHttpRequest();
    today_select_xhr.open("GET","/api/today/index_list.json");
    today_select_xhr.responseType = "json";
    today_select_xhr.send();
    today_select_xhr.onload = function(){
        //要素を作りh1の次に追加
        let now_js = today_select_xhr.response;
        let select_el = document.getElementById("select-office");
        let nowjs_keys = now_js["index"];
        let url_parm = new URL(window.location.href).searchParams;
        for (let x = 0;x<nowjs_keys.length;x++){
            let now_op_el = document.createElement("option");
            now_op_el.innerText = nowjs_keys[x];
            now_op_el.value = nowjs_keys[x];
            if (nowjs_keys[x]=="全体"){
                now_op_el.value = "inde";
            }
            if(url_parm.get("p")==now_op_el.value){
                now_op_el.selected = true;
            }
            select_el.appendChild(now_op_el);
        }
        select_el.addEventListener("change",hot_change_office);
    }
}

function page_sort(pagekind="c",kind="latest"){
    let nowquery;
    if (pagekind=="c"){
        //チャンネル名取得
        nowquery = decodeURI(String(location.pathname).slice(4,-1));
    }
    else if (pagekind=="m"){
        nowquery = decodeURI(String(location.pathname).slice(7,-1));
    }
    //ファイル取得
    let chsort_xhr = new XMLHttpRequest();
    chsort_xhr.open("GET","/cgi-bin/vdata.cgi?" + pagekind + "=" + nowquery);
    chsort_xhr.responseType = "json";
    chsort_xhr.send();
    chsort_xhr.onload = function(){
        let nowjson = chsort_xhr.response;
        let nowjs_keys = Object.keys(nowjson);
        let key_remove = ["plang","status"];
        nowjs_keys = nowjs_keys.filter(function(v){
            return ! key_remove.includes(v);
        });
        let nowsortlist = [];
        for (let x = 0;x<nowjs_keys.length;x++){
            if (Object.keys(nowjson[nowjs_keys[x]]).indexOf("statisticsdata")!=-1){
                nowsortlist.push(nowjson[nowjs_keys[x]]);
            }
        }
        let retnum = 5;
        if (kind=="latest"){
            retnum = 5;
        }
        else if (kind=="viewcount_desc"){
            retnum = 1;
        }
        else if (kind=="goodcount"){
            retnum = 2;
        }
        else if (kind=="commentcount"){
            retnum = 3;
        }
        else if (kind=="viewcount_rate"){
            retnum = 4;
        }
        if (kind=="viewcount_asc"){
            retnum = 1;
            nowsortlist.sort(function(a,b){return(a["statisticsdata"][retnum] - b["statisticsdata"][retnum]);});//昇順にする
        }
        else{
            nowsortlist.sort(function(a,b){return(b["statisticsdata"][retnum] - a["statisticsdata"][retnum]);});//降順にする
        }
        let flexname = "";
        if (pagekind=="m"){
            flexname = "music_flex";
        }
        else if (pagekind=="c"){
            flexname = "ch_flex";
        }
        let mainflex = document.getElementById(flexname);
        mainflex.innerHTML = "";//全内容削除
        let mfinvalue = "";
        for (let x = 0;x<nowsortlist.length;x++){
            let ns = nowsortlist[x];
            let addclass = "";
            if (ns["movietime"] <= 60){
                addclass = " yt_short";
            }
            try{
                if (ns["channelname"].indexOf("Topic")!=-1){
                    addclass += " inctopic";
                }
            }
            catch{}
            if (ns["memberdata"].length > 1){
                addclass += " collab"
            }
            if (pagekind=="m"){
                mfinvalue += '<div id="fb_' + ns["videoid"] + '" class="music_flex_ly' + addclass + '"><span class="ofoverflow_320" title="' + ns["videoname"] + '">' + ns["videoname"] + '</span><lite-youtube videoid="' + ns["videoid"] + '"></lite-youtube><button class="ofoverflow_320 minmg" onclick="vdt(\'' + ns["videoid"] + '\')">詳細を表示</button></div>';
            }
            else if (pagekind=="c"){
                mfinvalue += '<div id="fb_' + ns["videoid"] + '" class="music_flex_ly' + addclass + '"><span class="ofoverflow_320" title="' + ns["videoname"] + '"><a href="' + "/music/" + dir_replace(ns["musicname"]) + "/" + '" onclick="page_ajax_load(\'' + "/music/" + dir_replace(ns["musicname"]) + "/" + '\');return false">' + ns["musicname"] + '</a></span><lite-youtube videoid="' + ns["videoid"] + '"></lite-youtube><button class="ofoverflow_320 minmg" onclick="vdt(\'' + ns["videoid"] + '\')">詳細を表示</button></div>';
            }
        }
        mainflex.innerHTML = mfinvalue;
        ytviewchange();
    }
}

function ch_select_change(){
    page_sort("c",document.getElementById("page_sort_select").value);
}

function music_select_change(){
    page_sort("m",document.getElementById("page_sort_select").value);
}

function dir_replace(n_str){
    let n_rep_st = String(n_str).replaceAll("\\","").replaceAll(",","").replaceAll(".","").replaceAll(":","").replaceAll(";","").replaceAll("?","").replaceAll("/","").replaceAll("<","").replaceAll(">","").replaceAll("*","").replaceAll("|","").replaceAll("+","").replaceAll("=","").replaceAll("[","").replaceAll("]","").replaceAll('"',"").replaceAll("(","").replaceAll(")","").replaceAll("^","").replaceAll("!","").replaceAll("$","").replaceAll("'","").replaceAll("%","").replaceAll("&","").replaceAll("～","").replaceAll("#","")
    return n_rep_st
}

function yt_pl_shuffle(){
    now_playlist = shuffle(now_playlist);
    sync_playlist()
    if(document.getElementById("yt_pl_idel").classList.contains("dis_none")==false&&document.getElementById("radio-side-pl").checked){//サイドバーが開かつプレイリストを見てるとき順番を更新
        view_playlist();
    }
}

let beforevid = "";

function vdt(videoid){
    try{
        document.getElementById("nvdt").remove();
    }
    catch{}
    if(videoid!=beforevid){
        beforevid = videoid;
        //make element
        let nowdiv = document.createElement("div");
        nowdiv.id = "nvdt";
        document.getElementById("fb_"+videoid).after(nowdiv);
        //操作用のグループを生成
        let nowbg = document.createElement("group");
        nowbg.classList.add("inline-radio");
        for(let y = 0;y<3;y++){
            let maindiv = document.createElement("div");
            maindiv.classList.add("radio-page-div");
            let maininputel = document.createElement("input");
            maininputel.classList.add("radio-page-select-p");
            maininputel.type = "radio";
            maininputel.name = videoid + "_ra";
            if (y==0){
                maininputel.checked = true;
            }
            maindiv.appendChild(maininputel);
            let btlabel = document.createElement("label");
            btlabel.classList.add("radio-page-label");
            let labellist = ["視聴回数","高評価","コメント数"];
            btlabel.innerText = labellist[y];
            maindiv.appendChild(btlabel);
            nowbg.appendChild(maindiv);
        }
        nowbg.addEventListener("change",function(){change_graph_music(videoid);});
        nowdiv.appendChild(nowbg);
        //canvas用要素作成
        let nowcan = document.createElement("canvas");
        nowcan.id = videoid;
        nowcan.classList.add("yt-view_graph");
        nowdiv.appendChild(nowcan);
        let vflexdiv = document.createElement("div");
        vflexdiv.id = "vflex";
        vflexdiv.classList.add("vtuber_sing");
        nowdiv.appendChild(vflexdiv);
        let vdataapi_xhr = new XMLHttpRequest();
        vdataapi_xhr.open("GET","/api/v4/videoid/" + videoid + ".json");
        vdataapi_xhr.responseType = "json";
        vdataapi_xhr.send();
        vdataapi_xhr.onload = function(){
            let nowjson = vdataapi_xhr.response;
            Chart_cleater_single_v1(nowjson["videoid"],nowjson["statisticsdata"][1],nowjson["statisticsdata"][2],"視聴回数");
            for (let u = 0;u<nowjson["memberdata"].length;u++){
                let now_adoc = document.createElement("button");
                now_adoc.classList.add("nbt_noborder")
                now_adoc.addEventListener("click",function(){page_ajax_load("/ch/" + dir_replace(nowjson["memberdata"][u]["nickname"]) + "/");})
                let nowpicel = document.createElement("img");
                nowpicel.src = picurl2fiturl(nowjson["memberdata"][u]["pictureurl"],75);
                nowpicel.classList.add("v_face");
                nowpicel.width = 75;
                nowpicel.height = 75;
                nowpicel.alt = nowjson["memberdata"][u]["nickname"];
                nowpicel.title = nowjson["memberdata"][u]["nickname"];
                now_adoc.appendChild(nowpicel);
                vflexdiv.appendChild(now_adoc);
            }
        }
    }
    else{
        beforevid = "";
    }
}

function picurl2fiturl(nowurl,size=75){
    let returl = nowurl;
    if (nowurl.indexOf("yt3.ggpht.com") != -1||nowurl.indexOf("yt4.ggpht.com") != -1){
        returl = nowurl + "=s" + String(size) + "-c-k-c0x00ffffff-no-rj";
    }
    else if (nowurl.indexOf("pbs.twimg.com") != -1){
        let twurl_base = String(nowurl).slice(0,-11);
        let twurl_ex = String(nowurl).slice(-4);
        if (size <= 48){
            returl = twurl_base + "normal" + twurl_ex;
        }
        else if (size <= 200){
            returl = twurl_base + "200x200" + twurl_ex;
        }
        else{
            returl = twurl_base + "400x400" + twurl_ex;
        }
    }
    return returl
}

function ytviewchange(){
    //今のページ判別
    let nid = "";
    if (location.pathname.indexOf("/music/")!==-1){
        nid = "music_flex";
    }
    else if (location.pathname.indexOf("/ch/")!==-1){
        nid = "ch_flex";
    }
    let doclist = document.getElementById(nid).childNodes;
    let nowshsw = false;
    try{
        nowshsw = document.getElementById("cmn-toggle-sh").checked;
    }
    catch{}
    let nowmssw = false;
    try{
        nowmssw = document.getElementById("cmn-toggle-ms").checked;
    }
    catch{}
    let nowcbsw = false;
    try{
        nowcbsw = document.getElementById("cmn-toggle-cb").checked;
    }
    catch{}
    for (let x = 0;x<doclist.length;x++){
        let nowdoc_cl = doclist[x].classList;
        //全部
        if (nowdoc_cl.contains("yt_short")&&nowdoc_cl.contains("inctopic")&&nowdoc_cl.contains("collab")){
            if (nowshsw||nowmssw||nowcbsw){
                nowdoc_cl.remove("dis_none");
            }
            else{
                nowdoc_cl.add("dis_none");
            }
        }
        //ショートカツ配信
        else if (nowdoc_cl.contains("yt_short")&&nowdoc_cl.contains("inctopic")&&nowdoc_cl.contains("collab")==false){
            if (nowshsw||nowmssw){
                nowdoc_cl.remove("dis_none");
            }
            else{
                nowdoc_cl.add("dis_none");
            }
        }
        //ショートカツコラボ
        else if (nowdoc_cl.contains("yt_short")&&nowdoc_cl.contains("inctopic")==false&&nowdoc_cl.contains("collab")){
            if (nowshsw||nowcbsw){
                nowdoc_cl.remove("dis_none");
            }
            else{
                nowdoc_cl.add("dis_none");
            }
        }
        //配信カツコラボ
        else if (nowdoc_cl.contains("yt_short")==false&&nowdoc_cl.contains("inctopic")&&nowdoc_cl.contains("collab")){
            if (nowcbsw&&nowmssw){
                nowdoc_cl.remove("dis_none");
            }
            else{
                nowdoc_cl.add("dis_none");
            }
        }
        //配信楽曲だけ
        else if (nowdoc_cl.contains("yt_short")==false&&nowdoc_cl.contains("inctopic")&&nowdoc_cl.contains("collab")==false){
            if (nowmssw){
                nowdoc_cl.remove("dis_none");
            }
            else{
                nowdoc_cl.add("dis_none");
            }
        }
        //ショートだけ
        else if (nowdoc_cl.contains("yt_short")&&nowdoc_cl.contains("inctopic")==false&&nowdoc_cl.contains("collab")==false){
            if (nowshsw){
                nowdoc_cl.remove("dis_none");
            }
            else{
                nowdoc_cl.add("dis_none");
            }
        }
        //コラボだけ
        else if (nowdoc_cl.contains("yt_short")==false&&nowdoc_cl.contains("inctopic")==false&&nowdoc_cl.contains("collab")){
            if (nowcbsw){
                nowdoc_cl.remove("dis_none");
            }
            else{
                nowdoc_cl.add("dis_none");
            }
        }
    }
}

let vsongdb = new Dexie("vsong_db");
vsongdb.version(1).stores({//定義
    array_list: "++arrayname, arraydata"
});

function sync_playlist(){
    vsongdb.array_list.put({
        arrayname: "playlist",
        arraydata: now_playlist
    })
}

function load_playlist(){
    vsongdb.array_list.where("arrayname")
        .equals("playlist")
        .limit(1)
        .toArray()
        .then(function (ndt){
            console.log(ndt)
            try{
                now_playlist = ndt[0]["arraydata"];
            }
            catch{console.log("can't get playlist.")}
        });
}

function save_latest_videoinfo(){
    try{
        vsongdb.array_list.put({
            arrayname: "latest_playdata",
            arraydata: {"videoid": now_player.getVideoData()["video_id"],
                        "playtime": now_player.getCurrentTime()}
        })
    }
    catch{}
}

function add_songhistory(videoid){
    if (main_option_data["save_watch_history"]){
        //一度取得してから追加
        vsongdb.array_list.where("arrayname")
        .equals("songhistory")
        .limit(1)
        .toArray()
        .then(function (ndt){
            console.log(ndt);
            try{
                let songhistory = ndt[0]["arraydata"];
                songhistory.unshift([videoid,new Date()]);
                //こっから保存
                vsongdb.array_list.put({
                    arrayname: "songhistory",
                    arraydata: songhistory
                })
            }
            catch{
                vsongdb.array_list.put({
                    arrayname: "songhistory",
                    arraydata: [[videoid,new Date]]
                })
            }
        });
    }
}

function watch_history_all_clear(){
    vsongdb.array_list.put({
        arrayname: "songhistory",
        arraydata: []//空で保存
    })
    view_watchhistory_offset = 0;
    view_watchhistory();
}

function get_songhistory(){
    vsongdb.array_list.where("arrayname")
        .equals("songhistory")
        .limit(1)
        .toArray()
        .then(function (ndt){
            console.log(ndt);
            try{
                let songhistory = ndt[0]["arraydata"];
                return songhistory
            }
            catch{
                return "error"
            }
        })
}

let view_watchhistory_offset = 0;

function watchhistory_down(){
    let nowdoc = document.getElementById("yt_playlist_view_p");
    if (nowdoc.scrollTop > nowdoc.scrollTopMax * 0.95){
        nowdoc.removeEventListener("scroll",watchhistory_down);
        view_watchhistory_offset++;
        view_watchhistory();
    }
}

function view_watchhistory(){
    vsongdb.array_list.where("arrayname")
        .equals("songhistory")
        .limit(1)
        .toArray()
        .then(function (ndt){
            console.log(ndt);
            try{
                let songhistory = ndt[0]["arraydata"];
                let allvid = [];
                let looplength = 50;
                let startnumber = looplength*view_watchhistory_offset;
                if (looplength*view_watchhistory_offset>songhistory.length){//オフセットできないほど履歴がないときはスキップ
                    return
                }
                if (looplength>songhistory.length){
                    looplength = songhistory.length;
                }
                for (let x = startnumber;x<(startnumber + looplength);x++){
                    if (allvid.indexOf(songhistory[x][0])==-1){//ないときだけ追加
                        allvid.push(songhistory[x][0]);
                    }
                }
                //リクエスト送る
                let watch_vid_xhr = new XMLHttpRequest();
                watch_vid_xhr.open("POST","/cgi-bin/vdata_query_post.cgi");
                watch_vid_xhr.setRequestHeader("Content-Type", "application/json");
                watch_vid_xhr.responseType = "json";
                watch_vid_xhr.send(JSON.stringify({"videoid":allvid}));
                watch_vid_xhr.onload = function(){
                    let nowjson = watch_vid_xhr.response;
                    let parentdoc = document.getElementById("yt_playlist_view_p");
                    if (view_watchhistory_offset===0){
                        parentdoc.innerHTML = '<div class="ytpl_inele"><button class="sidebar_history_clear" onclick="watch_history_all_clear()">履歴をすべて削除</button><hr></div>';//リセット
                    }
                    for (let x = startnumber;x<(startnumber + looplength);x++){
                        let nowvid = songhistory[x][0];
                        let nchdoc = document.createElement("div");
                        nchdoc.classList.add("ytpl_inele");
                        /*
                        let nimg = document.createElement("img");
                        nimg.src = "https://i.ytimg.com/vi_webp/" + nowvid +"/mqdefault.webp";
                        nimg.classList.add("fit-cut");
                        nimg.width = 160;
                        nimg.height = 90;
                        */
                        //let now_lite = document.createElement("lite-youtube");
                        //now_lite.videoid = nowvid;
                        //now_lite.width = 160;
                        //now_lite.height = 90;
                        //nchdoc.appendChild(nimg);
                        let nowappend_html = "<lite-youtube videoid='" + nowvid + "' class='for-sidebar-embed'></lite-youtube>"
                        //nchdoc.appendChild(now_lite);
                        nchdoc.innerHTML += nowappend_html;
                        let menst = "";
                        try{
                            for (let r = 0;r<nowjson[nowvid]["memberdata"].length;r++){
                                menst += nowjson[nowvid]["memberdata"][r]["nickname"] + " ";
                            }
                        }
                        catch{}
                        let nowdesdoc = document.createElement("div");
                        nowdesdoc.classList.add("wh_nest");
                        try{
                            nowdesdoc.innerHTML = "再生日時:" + songhistory[x][1].toLocaleString("ja") + "<br><a href='/music/" + dir_replace(nowjson[nowvid]["musicname"]) + "/' onclick='page_ajax_load(\"/music/" + dir_replace(nowjson[nowvid]["musicname"]) + "/\");return false'>" + nowjson[nowvid]["musicname"] + "</a><br>" + menst;
                        }
                        catch{}
                        nchdoc.appendChild(nowdesdoc);
                        if (x+1 != songhistory.length){
                            nchdoc.appendChild(document.createElement("hr"));
                        }
                        parentdoc.appendChild(nchdoc);
                    }
                    parentdoc.addEventListener("scroll",watchhistory_down);
                }
            }
            catch{
                return "error"
            }
        })
}

function view_playlist(){
    if (now_playlist.length > 0){
        //プレイリスト内の動画の情報を取得
        let playlist_data_xhr = new XMLHttpRequest();
        //playlist_data_xhr.open("GET","/cgi-bin/vdata_query.cgi?q=" + now_playlist.join("|"));//wikipedia感ある仕様 件数制限はURLの限界まで
        playlist_data_xhr.open("POST","/cgi-bin/vdata_query_post.cgi");
        playlist_data_xhr.setRequestHeader('Content-Type', 'application/json');
        playlist_data_xhr.responseType = "json";
        //playlist_data_xhr.send();
        playlist_data_xhr.send(JSON.stringify({"videoid":now_playlist}));
        playlist_data_xhr.onload = function(){
            let nowjson = playlist_data_xhr.response;
            let parentdoc = document.getElementById("yt_playlist_view_p");
            parentdoc.innerHTML = "";//リセット
            for (let x = 0;x<now_playlist.length;x++){
                let nowvid = now_playlist[x];
                let nchdoc = document.createElement("div");
                nchdoc.classList.add("ytpl_inele","ytplv_" + nowvid);
                let nimg = document.createElement("img");
                nimg.src = "https://i.ytimg.com/vi_webp/" + nowvid +"/hqdefault.webp";
                nimg.classList.add("fit-cut");
                nimg.width = 160;
                nimg.height = 90;
                nchdoc.appendChild(nimg);
                let menst = "";
                try{
                    for (let r = 0;r<nowjson[nowvid]["memberdata"].length;r++){
                        menst += nowjson[nowvid]["memberdata"][r]["nickname"] + " ";
                    }
                }
                catch{}
                let nowdesdoc = document.createElement("div");
                nowdesdoc.classList.add("pl_nest");
                nowdesdoc.innerHTML = "<a href='/music/" + dir_replace(nowjson[nowvid]["musicname"]) + "/' onclick='page_ajax_load(\"/music/" + dir_replace(nowjson[nowvid]["musicname"]) + "/\");return false'>" + nowjson[nowvid]["musicname"] + "</a><br>" + menst;
                nchdoc.appendChild(nowdesdoc);
                nchdoc.innerHTML += '<button class="pl_trbt bt_noborder" onclick="playlist_remove(\'' + nowvid + '\')"><img src="/util/trash.webp" width="85" height="85"></button>';
                if (x+1 != now_playlist.length){
                    nchdoc.appendChild(document.createElement("hr"));
                }
                parentdoc.appendChild(nchdoc);
            }
        }
    }  
    else{
        document.getElementById("yt_playlist_view_p").innerHTML = "<p class='center-txt'>現在再生リストは空です</p>";
    }
}

let main_option_data = {"watch_music_mode":1,"save_watch_history":true};

function save_option(){
    vsongdb.array_list.put({
        arrayname: "option",
        arraydata: main_option_data
    })
}

function load_option(){
    vsongdb.array_list.where("arrayname")
        .equals("option")
        .limit(1)
        .toArray()
        .then(function (ndt){
            if (ndt===[]){//データがない時撥ねる->保存
                save_option();
                return
            }
            main_option_data = ndt[0]["arraydata"];
        })
}

load_option()
let mps_id = ["radio-side-op-normal","radio-side-op-cut","radio-side-op-chorus"]

function music_play_support_mode_change(){
    for (let x=0;x<mps_id.length;x++){
        if(document.getElementById(mps_id[x]).checked){
            main_option_data["watch_music_mode"] = x;
            break
        }
    }
    save_option();
}

function view_side_option(){
    let add_content = ["","",""]
    try{
        for (let x=0;x<mps_id.length;x++){
            if(document.getElementById(mps_id[x]).checked){
                add_content[x] = "checked";
                break
            }
        }
    }
    catch{
        add_content[main_option_data["watch_music_mode"]] = "checked";
    }
    let watch_history_save_status = "";
    if (main_option_data["save_watch_history"]){
        watch_history_save_status = "checked";
    }
    let parent_doc = document.getElementById("yt_playlist_view_p");
    parent_doc.innerHTML = '<p class="center-txt">音楽再生支援</p><group id="vs-radio-sidebar-option" class="inline-radio" onchange="music_play_support_mode_change()"><div class="radio-page-div"><input id="radio-side-op-normal" class="radio-option-select" type="radio" name="vs-sidebar-option" ' + add_content[0] + '><label class="radio-option-label">通常再生</label></div><div class="radio-page-div"><input id="radio-side-op-cut" class="radio-option-select" type="radio" name="vs-sidebar-option" ' + add_content[1] +'><label class="radio-option-label">無音カット</label></div><div class="radio-page-div"><input id="radio-side-op-chorus" class="radio-option-select" type="radio" name="vs-sidebar-option" ' + add_content[2] + '><label class="radio-option-label">1サビのみ</label></div></group><div class="pos-re mt-15"><span class="option-checkbox-txt">再生履歴を保存</span><div class="switch"><input id="cmn-toggle-save-watch" class="cmn-toggle cmn-toggle-round" type="checkbox" onchange="option_watchhistory_save_change()"' + watch_history_save_status + '><label for="cmn-toggle-save-watch" class="cmn-toggle-label-left"></label></div></div>';
}

function open_playlist(){
    document.getElementById("imgupdown_bt").classList.toggle("inversion_pic");
    document.getElementsByTagName("main")[0].classList.toggle("on_viewpl");
    document.getElementById("yt_pl_idel").classList.toggle("dis_none");
    document.getElementById("ytembed").classList.toggle("ytembed_swift");
    if (document.getElementById("yt_pl_idel").classList.contains("dis_none")==false){
        sidebar_info();
    }
}

function option_watchhistory_save_change(){
    if(document.getElementById("cmn-toggle-save-watch").checked){
        main_option_data["save_watch_history"] = true;
    }
    else{
        main_option_data["save_watch_history"] = false;
    }
    save_option();
}

function sidebar_info(){
    document.getElementById("yt_playlist_view_p").removeEventListener("scroll",watchhistory_down);
    if(document.getElementById("radio-side-pl").checked){
        view_playlist();
    }
    else if (document.getElementById("radio-side-wh").checked){
        view_watchhistory();
        view_watchhistory_offset = 0;
    }
    else if (document.getElementById("radio-side-op").checked){
        view_side_option();
    }
}

function playlist_remove(nvideoid){
    //プレイリストから削除
    now_playlist = now_playlist.filter(item=> item != nvideoid);
    let nowviddoc = document.getElementsByClassName("ytplv_" + nvideoid);
    for (let x = 0;x<nowviddoc.length;x++){
        nowviddoc[x].remove();
        console.log("del")
    }
}

function page_load(){//ページロード時の処理
    page_transition();//変数削除
    if(location.pathname=="/music/"){
        musittop_load();
    }
    else if (location.pathname.indexOf("/music/")!==-1){//音楽ページ
        load_chart();
        music_page_load();
    }
    else if (location.pathname.indexOf("/ch/")!==-1){//チャンネルページ
        load_chart();
        ch_page_load();
    }
    else if (location.pathname==="/"){//トップページ
        load_max = 0;
        recommend("top");
    }
    else if (location.pathname==="/search/"||location.pathname==="/search"){//検索
        let url_parm = new URL(window.location.href).searchParams;
        if(url_parm.get("q")!=null){
            document.getElementById("lib_search").value=url_parm.get("q");
        }
        search_index_load();
    }
    else if (location.pathname==="/watch/"){//動画視聴
        watch_page_load();
    }
    else if (location.pathname==="/today/"){//今日の人気
        today_load();
        hot_chose_load();
    }
}

page_load();

window.addEventListener('popstate', function(e) {//バックボタン対策
    let now_url = String(location.href).replace(location.origin,"");
    page_ajax_load(now_url,1);
});

function onYouTubeIframeAPIReady(){//youtubeプリロード用
    youtube_embed_preload();
}

window.addEventListener('beforeunload',save_latest_videoinfo);//ページ離脱時状況保存

setInterval(save_latest_videoinfo,10000)//10秒ごとに状態を保存