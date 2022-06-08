function load_chart(){
    if (window.matchMedia('(prefers-color-scheme: dark)').matches === !0) {
        Chart.defaults.color = '#c0c0c0';
    } else {
        Chart.defaults.color = '#3f4551';
    }
}

function dt(video_id) {
    if (window.matchMedia('(min-width:768px)').matches) {
        document.getElementById(video_id + '_td').innerHTML = document.getElementById(video_id + '_dt').innerHTML;
    }
    else{
        document.getElementById(video_id + "_sum").innerHTML = document.getElementById(video_id + "_music_a").innerHTML;
    }
};

const shuffle = ([...array]) => {
    for (let i = array.length - 1; i >= 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

let chart_instance = {};

function Chart_cleater_v2(id_c, label, vc, lc, cc) {
    chart_instance[id_c] = new Chart(document.getElementById(id_c), {
        type: 'line',
        data: {
            labels: label,
            datasets: [{
                label: '視聴回数',
                data: vc,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgb(255, 99, 132)',
            }, {
                label: '高評価数',
                data: lc,
                hidden: !0,
                borderColor: 'rgb(58,180,139)',
                backgroundColor: 'rgb(58,180,139)',
            }, {
                label: 'コメント数',
                data: cc,
                hidden: !0,
                borderColor: 'rgb(137, 195, 235)',
                backgroundColor: 'rgb(137, 195, 235)',
            }]
        },
        options: {
            animation: !1,
            responsive: !0
        }
    })
}

function Chart_cleater_single_v1(id_c,label,content,content_name){
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
            animation: !1,
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
    window.removeEventListener("scroll", music_scroll_ev);
    window.removeEventListener("scroll",ch_scroll_ev);
    chart_instance = {};
    try{
        document.getElementById('lib_search').removeEventListener("input",search_index);
        document.getElementById('lib_search').removeEventListener("change",search_index_finish);
    }
    catch{}
}

function recommend_music_scroll(kind=0){
    let maindoc = document.getElementById("music_recommend");
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

function change_graph_music(g_name){
    chart_instance[g_name].destroy(); 
    let elements = document.getElementsByName(g_name+"_ra");
    var nown = 0;
    for (let x = 0;x<elements.length;x++){
        if (elements.item(x).checked){
            nown = x;
        }
    }
    let kind = ["視聴回数","高評価","コメント数"];
    if(g_name=="sum-yt"){
        Chart_cleater_single_v1(g_name, statistics_data["music"][0], statistics_data["music"][nown+1],kind[nown]);
    }
    else{
        Chart_cleater_single_v1(g_name, statistics_data[g_name][1],statistics_data[g_name][nown+2],kind[nown]);
    }
}

function change_graph_ch(g_name){
    //キャンバス初期化
    chart_instance[g_name].destroy(); 
    let elements = document.getElementsByName(g_name+"_ra");
    var nown = 0;
    for (let x = 0;x<elements.length;x++){
        if (elements.item(x).checked){
            nown = x;
        }
    }
    let kind = ["視聴回数","高評価","コメント数"];
    if(g_name=="sum-yt"){
        Chart_cleater_single_v1(g_name, statistics_data["channel"][0], statistics_data["channel"][nown+1],kind[nown]);
    }
    else{
        Chart_cleater_single_v1(g_name, statistics_data[g_name][1],statistics_data[g_name][nown+2],kind[nown]);
    }
}

function ch_page_load(){
    now_nick_name = "";
    counter_up = 0;
    counter_down = 0;
    load_max = 0;
    maxlength = -1;
    let now_data_xhr = new XMLHttpRequest();
    now_data_xhr.open("GET","data.json");//今のページのjsonを取り寄せる
    now_data_xhr.responseType = "json";
    now_data_xhr.send();
    now_data_xhr.onload = function() {//ファイルが来たら実行
        const ndr = now_data_xhr.response;
        now_nick_name = ndr["nick_name"];
        nowvid = ndr["videoidlist"];
        counter_up = ndr["pageid"];
        counter_down = ndr["pageid"];
        maxlength = ndr["max-length"];
        let statistics_xhr = new XMLHttpRequest();
        statistics_xhr.open("GET","/ch/" + now_nick_name + "/statistics.json");
        statistics_xhr.responseType = "json";
        statistics_xhr.send();
        statistics_xhr.onload = function(){
            statistics_data = statistics_xhr.response;
            if (ndr["pageid"]===0){
                //Chart_cleater_v2("sum-yt",statistics_data["channel"][0],statistics_data["channel"][1],statistics_data["channel"][2],statistics_data["channel"][3]);
                Chart_cleater_single_v1("sum-yt",statistics_data["channel"][0],statistics_data["channel"][1],"視聴回数");
            }
            for(var k=0;k<nowvid.length;k++){
                dt(nowvid[k]);
                //Chart_cleater_v2(nowvid[k],statistics_data[nowvid[k]][1],statistics_data[nowvid[k]][2],statistics_data[nowvid[k]][3],statistics_data[nowvid[k]][4]);
                Chart_cleater_single_v1(nowvid[k],statistics_data[nowvid[k]][1],statistics_data[nowvid[k]][2],"視聴回数");
            }
        }
    }
}

function ch_scroll_do(mes) {
    let sc_xhr = new XMLHttpRequest();
    if (mes=="down"&&maxlength>counter_down+1){
        sc_xhr.open("GET","/ch/" + now_nick_name + "/page" + String(counter_down+2) + "/data.json");
        counter_down++;
    }
    else if(mes=="up"&&0<counter_up){
        if(counter_up==1){
            sc_xhr.open("GET","/ch/" + now_nick_name + "/data.json");
        }
        else{
            sc_xhr.open("GET","/ch/" + now_nick_name + "/page" + String(counter_up) + "/data.json");
        }
        counter_up += -1;
    }
    else{
        recommend();
        return//処理強制終了
    }
    sc_xhr.responseType = "json";
    sc_xhr.send();
    sc_xhr.onload = function(){
        const njdata = sc_xhr.response;
        if(njdata["pageid"]==0){
            document.getElementById("sum-viewer").innerHTML = njdata["first"] + document.getElementById("sum-viewer").innerHTML;
            Chart_cleater_v2("sum-yt",statistics_data["channel"][0],statistics_data["channel"][1],statistics_data["channel"][2],statistics_data["channel"][3]);
        }
        let tbody_el = document.getElementById("tbd-" + String(njdata["pageid"]));
        for (let g=0;g<njdata["videoidlist"].length;g++){
            tbody_el.innerHTML = tbody_el.innerHTML + njdata[g];
        }
        for (let g=0;g<njdata["videoidlist"].length;g++){
            dt(njdata["videoidlist"][g]);
            //Chart_cleater_v2(njdata["videoidlist"][g],statistics_data[njdata["videoidlist"][g]][1],statistics_data[njdata["videoidlist"][g]][2],statistics_data[njdata["videoidlist"][g]][3],statistics_data[njdata["videoidlist"][g]][4]);
            Chart_cleater_single_v1(njdata["videoidlist"][g],statistics_data[njdata["videoidlist"][g]][1],statistics_data[njdata["videoidlist"][g]][2],"視聴回数");
        }
        if(mes=="up"){
            if(njdata["pageid"]==0){
                window.scrollBy(0,document.getElementById("sum-viewer").clientHeight+document.getElementById("tbd-" + String(njdata["pageid"])).clientHeight);
            }
            else{
                window.scrollBy(0,document.getElementById("tbd-" + String(njdata["pageid"])).clientHeight);
            }
        }
    }
}

function ch_scroll_ev() {
    const currentPos = window.pageYOffset;
    var bottomPoint = document.body.clientHeight - window.innerHeight - 600;
    if (bottomPoint <= currentPos) {//下にスクロールされた場合
        ch_scroll_do("down")
    }
    if (currentPos < 500){
        ch_scroll_do("up")
    }
    replace_urlst("ch");
}

function music_page_load(){
    now_music_name = "";
    counter_up = 0;
    counter_down = 0;
    load_max = 0;
    maxlength = -1;
    let now_data_xhr = new XMLHttpRequest();
    now_data_xhr.open("GET","data.json");//今のページのjsonを取り寄せる
    now_data_xhr.responseType = "json";
    now_data_xhr.send();
    now_data_xhr.onload = function() {//ファイルが来たら実行
        const ndr = now_data_xhr.response;
        now_music_name = ndr["music_name"];
        nowvid = ndr["videoidlist"];
        counter_up = ndr["pageid"];
        counter_down = ndr["pageid"];
        maxlength = ndr["max-length"];
        let statistics_xhr = new XMLHttpRequest();
        statistics_xhr.open("GET","/music/" + now_music_name + "/statistics.json");
        statistics_xhr.responseType = "json";
        statistics_xhr.send();
        statistics_xhr.onload = function(){
            statistics_data = statistics_xhr.response;
            if (ndr["pageid"]===0){
                //Chart_cleater_v2("sum-yt",statistics_data["music"][0],statistics_data["music"][1],statistics_data["music"][2],statistics_data["music"][3]);
                Chart_cleater_single_v1("sum-yt",statistics_data["music"][0],statistics_data["music"][1],"視聴回数");
            }
            for(var k=0;k<nowvid.length;k++){
                dt(nowvid[k]);
                //Chart_cleater_v2(nowvid[k],statistics_data[nowvid[k]][1],statistics_data[nowvid[k]][2],statistics_data[nowvid[k]][3],statistics_data[nowvid[k]][4]);
                Chart_cleater_single_v1(nowvid[k],statistics_data[nowvid[k]][1],statistics_data[nowvid[k]][2],"視聴回数");
            }
        }
    }
}

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
    let now_stalist = Object.keys(statistics_data);
    now_stalist.shift();
    now_playlist = [];
    for(let y = 0;y<now_stalist.length;y++){
        now_playlist.push(now_stalist[y]);
    }
    yt_skip();
}

function music_scroll_do(mes) {
    let sc_xhr = new XMLHttpRequest();
    if (mes=="down"&&maxlength>counter_down+1){
        sc_xhr.open("GET","/music/" + now_music_name + "/page" + String(counter_down+2) + "/data.json");
        counter_down++;
    }
    else if(mes=="up"&&0<counter_up){
        if(counter_up==1){
            sc_xhr.open("GET","/music/" + now_music_name + "/data.json");
        }
        else{
            sc_xhr.open("GET","/music/" + now_music_name + "/page" + String(counter_up) + "/data.json");
        }
        counter_up += -1;
    }
    else{
        recommend();
        return//処理強制終了
    }
    sc_xhr.responseType = "json";
    sc_xhr.send();
    sc_xhr.onload = function(){
        const njdata = sc_xhr.response;
        if(njdata["pageid"]==0){
            document.getElementById("sum-viewer").innerHTML = njdata["first"] + document.getElementById("sum-viewer").innerHTML;
            //Chart_cleater_v2("sum-yt",statistics_data["music"][0],statistics_data["music"][1],statistics_data["music"][2],statistics_data["music"][3]);
            Chart_cleater_single_v1("sum-yt",statistics_data["music"][0],statistics_data["music"][1],"視聴回数");
        }
        let tbody_el = document.getElementById("tbd-" + String(njdata["pageid"]));
        for (let g=0;g<njdata["videoidlist"].length;g++){
            tbody_el.innerHTML = tbody_el.innerHTML + njdata[g];
        }
        for (let g=0;g<njdata["videoidlist"].length;g++){
            dt(njdata["videoidlist"][g]);
            //Chart_cleater_v2(njdata["videoidlist"][g],statistics_data[njdata["videoidlist"][g]][1],statistics_data[njdata["videoidlist"][g]][2],statistics_data[njdata["videoidlist"][g]][3],statistics_data[njdata["videoidlist"][g]][4]);
            Chart_cleater_single_v1(njdata["videoidlist"][g],statistics_data[njdata["videoidlist"][g]][1],statistics_data[njdata["videoidlist"][g]][2],"視聴回数");
        }
        if(mes=="up"){
            if(njdata["pageid"]==0){
                window.scrollBy(0,document.getElementById("sum-viewer").clientHeight+document.getElementById("tbd-" + String(njdata["pageid"])).clientHeight);
            }
            else{
                window.scrollBy(0,document.getElementById("tbd-" + String(njdata["pageid"])).clientHeight);
            }
        }
    }
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
            divm.innerHTML = '<button type="button" class="musicbt musicundo" onclick="recommend_music_scroll(1)"><img class="music-bt" src="/util/undo.svg"></button><button type="button" class="musicbt musicnext" onclick="recommend_music_scroll(0)"><img class="music-bt" src="/util/nextbt.svg"></button>'
            if (kind===""){
                document.getElementById("descm").innerHTML = '<hr><p class="other_music">他のおすすめの曲</p>';
            }
            for (let i = 0; i < 20; i++) {
                divm.innerHTML = divm.innerHTML + "<a href='/music/" + res_mr[i][1] +
                    "/' onclick='page_ajax_load(\"/music/" + res_mr[i][1] + "/\");return false' title='" + res_mr[i][0] + "'>" + res_mr[i][0] + "<img class='fit-cut' src='https://i.ytimg.com/vi_webp/" +
                    res_mr[i][2] + "/hqdefault.webp' alt='" + res_mr[i][0] + "' width='320' height='180'></a>";
            }
        };
        let request_cr = new XMLHttpRequest();
        request_cr.open("GET", "/ajax/ch/cr-" + String(now_ran) + ".json");
        request_cr.responseType = "json";
        request_cr.send();
        request_cr.onload = function () {//チャンネルのほう
            const res_cr = request_cr.response;
            let divc = document.getElementById("ch_recommend");
            divc.innerHTML = '<button type="button" class="chbt chundo" onclick="recommend_ch_scroll(1)"><img class="ch-bt" src="/util/undo.svg"></button><button type="button" class="chbt chnext" onclick="recommend_ch_scroll(0)"><img class="ch-bt" src="/util/nextbt.svg"></button>';
            if (kind===""){
                document.getElementById("descc").innerHTML = '<hr><p class="other_music">他のおすすめのVtuber</p>';
            }
            for (let i = 0; i < 20; i++) {
                divc.innerHTML = divc.innerHTML + "<a href='/ch/" + res_cr[i][1] +
                    "/' onclick='page_ajax_load(\"/ch/" + res_cr[i][1] + "/\");return false' title='" + res_cr[i][0] + "'><span class='ofoverflow'>" + res_cr[i][0] +
                    "</span><img class='recommend-ch' src='" + res_cr[i][2] + "' alt='" + res_cr[i][0] +
                    "' width='120' height='120'></a>";
            }
        }
    }
}

function getClosestNum(num, ar){
    //近似値を保持しておく変数
    var closest;
    //配列かどうか、要素があるか判定
    if(Object.prototype.toString.call(ar) ==='[object Array]' && ar.length>0){
      //まず配列の最初の要素を近似値として保持する
      closest = ar[0];
      //配列の要素を順次比較していく
      for(var i=0;i<ar.length;i++){ 
         //この時点での近似値と、指定値の差異を絶対値で保持しておく
         var closestDiff = Math.abs(num - closest);
         //読み込んだ値と比較し、差異を絶対値で保持しておく
         var currentDiff = Math.abs(num - ar[i]);
         //新しく比較した値のほうが近かったら、近似値として保持しておく
         if(currentDiff < closestDiff){
             closest = ar[i];
         }
       }
      //ループが終わったら、近似値を返す
       return closest;
     }
  //配列じゃなかったらfalse
  return false;
}

function replace_urlst(kind=""){
    let k_place_array = [];
    for(var k=0;k<maxlength;k++){
        let ndt = document.getElementById("tbd-" + String(k));
        if (ndt.innerHTML!=""){//内容があるのだけ追加
            k_place_array.push(ndt.getBoundingClientRect()["y"]);
        }
    }
    if (window.matchMedia('(min-width:600px)').matches) {
        var get_put = -1700
    }
    else{
        var get_put = -1000
    }
    const ans = getClosestNum(get_put,k_place_array);
    for(var k=0;k<maxlength;k++){
        if(document.getElementById("tbd-" + String(k)).getBoundingClientRect()["y"]===ans&&String(location).match("/page" + String(k+1) + "/")==null){
            if (k!=0){
                if(kind==="music"){
                    history.replaceState(null,null,"/music/" + now_music_name + "/page" + String(k+1) + "/" + location.search)
                }
                else if(kind==="ch"){
                    history.replaceState(null,null,"/ch/" + now_nick_name + "/page" + String(k+1) + "/" + location.search)
                }
            }
            else{
                if(kind==="music"){
                    history.replaceState(null,null,"/music/" + now_music_name + "/" + location.search)
                }
                else if(kind==="ch"){
                    history.replaceState(null,null,"/ch/" + now_nick_name + "/" + location.search)
                }
            }
        }
    }
    
}

function music_scroll_ev() {
    const currentPos = window.pageYOffset;
    var bottomPoint = document.body.clientHeight - window.innerHeight - 600;
    if (bottomPoint <= currentPos) {//下にスクロールされた場合
        music_scroll_do("down")
    }
    if (currentPos < 500){
        music_scroll_do("up")
    }
    replace_urlst("music");
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
        load_youtubeapi_player(this.videoId);
    }
}
customElements.define('lite-youtube', LiteYTEmbed);
// End of the lite-youtube-embed

let now_player = "";
let before_playing = "";

function youtube_embed_preload(){
    let ytembed_el = document.getElementById("ytembed");
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
            videoId: "Snqom63tY_4",
            host: 'https://www.youtube-nocookie.com',
            events: {
                'onStateChange': yt_state_change
            }
        })
        ytembed_el.classList.add("float_right");
    }
}

function load_youtubeapi_player(now_video_id){
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
                'onReady': yt_sm_play
            }
        })
        ytembed_el.classList.add("float_right");
    }
    else{
        now_player.loadVideoById({videoId:now_video_id,startSeconds:0});
        if (navigator.userAgent.match(/iPhone|Android.+Mobile|Mobile/)||(navigator.userAgent.match(/Macintosh/)&&'ontouchend' in document)) {
            yt_display();
        }
        now_player.playVideo();
        if (navigator.userAgent.match(/iPhone|Android.+Mobile|Mobile/)||(navigator.userAgent.match(/Macintosh/)&&'ontouchend' in document)) {
            yt_display();
        }
        yt_music_display();
    }
}

function yt_sm_play(){//スマホ自動開始用
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
    document.getElementById("ytembed").classList.toggle("dis_none");
    let button_el = document.getElementById("yt_display")
    if(button_el.innerText=="表示"){
        button_el.innerText = "非表示";
    }
    else{
        button_el.innerText = "表示";
    }
}

let seek_interval;
window.addEventListener("keyup", (e)=>{keybord_yt(e)});

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
        if(document.getElementById("autoload_check").checked&&Math.floor(now_player.getDuration())<Math.floor(now_player.getCurrentTime())+5){//自動再生あり
            yt_skip();
        }
    }
}

function yt_music_display(){
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

let now_playlist = [];

function yt_skip(){
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
            if(now_player!=""){
                now_player.loadVideoById({'videoId': nowvid});
            }
            else{
                load_youtubeapi_player(nowvid);
            }
            before_playing = nowvid;
            yt_music_display();
        } 
    }
    else{
        console.log("normal_next");
        nowvid = now_playlist.shift();
        console.log("start_playing(skip):\t" + nowvid);
        if(now_player!=""){
            now_player.loadVideoById({'videoId': nowvid});
        }
        else{
            load_youtubeapi_player(nowvid);
        }
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
    }
}

function youtube_seekbar(){//バーを変えるやつ
    try{
        document.getElementById("yt-player-time").value = (now_player.getCurrentTime()/now_player.getDuration())*100;
    }
    catch{}
}

let watch_page_st = 0;

function watch_page_load(){
    document.getElementById("yt_ch_dismode").title = "小さな画面で表示";
    try{
        document.getElementById("youtube-iframe").classList.add("watch_yt_center");
        document.getElementById("ytembed").classList.remove("float_right");
        document.getElementById("ytembed").classList.remove("dis_none");
        document.getElementById("control_panel").classList.remove("dis_none");
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
        p_yt_el.classList.remove("dis_none");
        p_yt_el.classList.remove("float_right");
        let nowvid = new URL(now_player.getVideoUrl()).searchParams.get("v");
        urp.set("v",nowvid);
        history.replaceState(null,null,location.pathname + urp.toString());
    }
    else if (now_demand.length==11){//動画プレイヤーを作成し指定された動画idで読み込む
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
                    'onReady': yt_sm_play
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
            now_player.loadVideoById({'videoId': now_demand});
            yt_music_display();
        }
    }
    watch_page_st = 1;
}

function yt_watchmode_ch(){
    let ytch_el = document.getElementById("yt_ch_dismode");
    if(watch_page_st===0){//通常時->動画ページに遷移
        page_ajax_load("/watch?v=normal");
        ytch_el.title = "元のページに戻る";
    }
    else if(watch_page_st===1){
        history.back();
        ytch_el.title = "大画面で表示";
    }
}

function today_load(kind=-1,doc_kind="index"){
    let url_parm = new URL(window.location.href).searchParams;
    let urp = new URLSearchParams(new URL(window.location.href));
    let now_demand = url_parm.get("m");
    let nowidlist = ["radio-todayhot","radio-todayhotter","radio-weekhot","radio-monthhot","radio-wholehot"];
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
    if(kind==0){
        today_xhr.open("GET",doc_kind + "_diff.json");
    }
    else if(kind==1){
        today_xhr.open("GET",doc_kind + "_daydiff.json");
    }
    else if(kind==2){
        today_xhr.open("GET",doc_kind + "_weekdiff.json");
    }
    else if(kind==3){
        today_xhr.open("GET",doc_kind + "_monthdiff.json");
    }
    else if(kind==4){
        today_xhr.open("GET",doc_kind + "_wholediff.json")
    }
    today_xhr.responseType = "json";
    today_xhr.send();
    today_xhr.onload = function(){
        let now_j_g = today_xhr.response;
        let now_j = now_j_g["index"];
        let h1_tag = document.querySelector("h1");
        if (now_j_g["kind"]=="diff"||now_j_g["kind"]=="daydiff"){
            h1_tag.innerHTML = "今日の人気曲"
        }
        else if (now_j_g["kind"]=="weekdiff"){
            h1_tag.innerHTML = "今週の人気曲"
        }
        else if (now_j_g["kind"]=="monthdiff"){
            h1_tag.innerHTML = "今月の人気曲"
        }
        else if (now_j_g["kind"]=="wholediff"){
            h1_tag.innerHTML = "全期間人気曲"
        }
        if (doc_kind!="index"){
            h1_tag.innerHTML = h1_tag.innerHTML + "\t" + doc_kind;
        }
        let p_doc = document.getElementById("today_hot");
        p_doc.innerHTML = "";
        let object_length = 50;
        if (Object.keys(now_j).length < object_length){
            object_length = Object.keys(now_j).length;
        }
        for(let r = 0;r<object_length;r++){
            var now_el = document.createElement("div");
            now_el.classList.add("today_hot_space");
            if (now_j_g["kind"]=="diff"){
                now_el.innerHTML = '<span class="ofoverflow_320" title="' + now_j[r][1] +'">' + now_j[r][1] + '<br>' + now_j[r][2].toLocaleString() + '%増</span><br><lite-youtube videoid="' + now_j[r][0] +'" width="320" height="180"></lite-youtube>';
            }
            else if(now_j_g["kind"]=="daydiff"||now_j_g["kind"]=="weekdiff"||now_j_g["kind"]=="monthdiff"||now_j_g["kind"]=="wholediff"){
                now_el.innerHTML = '<span class="ofoverflow_320" title="' + now_j[r][1] +'">' + now_j[r][1] + '<br>' + now_j[r][2].toLocaleString() + '回増</span><br><lite-youtube videoid="' + now_j[r][0] +'" width="320" height="180"></lite-youtube>';
            }
            p_doc.appendChild(now_el);
        }
    }
    document.getElementById("radio-range").addEventListener("change",hotchange);
}

function hot_change_office(){
    let nowidlist = ["radio-todayhot","radio-todayhotter","radio-weekhot","radio-monthhot","radio-wholehot"];
    for (let nown = 0;nown<nowidlist.length;nown++){
        if(document.getElementById(nowidlist[nown]).checked){
            today_load(kind=nown,document.getElementById("select-office").value);
        }
    }
}

function hotchange(){
    let nowidlist = ["radio-todayhot","radio-todayhotter","radio-weekhot","radio-monthhot","radio-wholehot"];
    for (let nown = 0;nown<nowidlist.length;nown++){
        if(document.getElementById(nowidlist[nown]).checked){
            today_load(kind=nown);
        }
    }
}

function hot_chose_load(){
    var today_select_xhr = new XMLHttpRequest();
    today_select_xhr.open("GET","index_list.json");
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

function dir_replace(n_str){
    let n_rep_st = String(n_str).replaceAll("\\","").replaceAll(",","").replaceAll(".","").replaceAll(":","").replaceAll(";","").replaceAll("?","").replaceAll("/","").replaceAll("<","").replaceAll(">","").replaceAll("*","").replaceAll("|","").replaceAll("+","").replaceAll("=","").replaceAll("[","").replaceAll("]","").replaceAll('"',"").replaceAll("(","").replaceAll(")","").replaceAll("^","").replaceAll("!","").replaceAll("$","").replaceAll("'","").replaceAll("%","").replaceAll("&","").replaceAll("～","").replaceAll("#","")
    return n_rep_st
}

function yt_pl_shuffle(){
    now_playlist = shuffle(now_playlist);
}

function page_load(){//ページロード時の処理
    page_transition();//変数削除
    if(location.pathname=="/music/"){
        musittop_load();
    }
    else if (location.pathname.indexOf("/music/")!==-1){//音楽ページ
        load_chart();
        music_page_load();
        window.addEventListener("scroll", music_scroll_ev);
        music_scroll_do();
    }
    else if (location.pathname.indexOf("/ch/")!==-1){//チャンネルページ
        load_chart();
        ch_page_load();
        window.addEventListener("scroll", ch_scroll_ev);
        ch_scroll_do();
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
    else if (location.pathname==="/watch"){//動画視聴
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
youtube_embed_preload();