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
};

function Chart_cleater_v2(id_c, label, vc, lc, cc) {
    new Chart(document.getElementById(id_c), {
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
    window.removeEventListener("scroll", music_scroll_ev);
    window.removeEventListener("scroll",ch_scroll_ev);
    try{
        document.getElementById('search').removeEventListener("input",search_index);
    }
    catch{}
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
                Chart_cleater_v2("sum-yt",statistics_data["channel"][0],statistics_data["channel"][1],statistics_data["channel"][2],statistics_data["channel"][3]);
            }
            for(var k=0;k<nowvid.length;k++){
                dt(nowvid[k]);
                Chart_cleater_v2(nowvid[k],statistics_data[nowvid[k]][1],statistics_data[nowvid[k]][2],statistics_data[nowvid[k]][3],statistics_data[nowvid[k]][4]);
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
            Chart_cleater_v2(njdata["videoidlist"][g],statistics_data[njdata["videoidlist"][g]][1],statistics_data[njdata["videoidlist"][g]][2],statistics_data[njdata["videoidlist"][g]][3],statistics_data[njdata["videoidlist"][g]][4]);
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

function ch_replace_urlst(){
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
                history.replaceState(null,null,"/ch/" + now_nick_name + "/page" + String(k+1) + "/" + location.search)
            }
            else{
                history.replaceState(null,null,"/ch/" + now_nick_name + "/" + location.search)
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
    ch_replace_urlst();
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
                Chart_cleater_v2("sum-yt",statistics_data["music"][0],statistics_data["music"][1],statistics_data["music"][2],statistics_data["music"][3]);
            }
            for(var k=0;k<nowvid.length;k++){
                dt(nowvid[k]);
                Chart_cleater_v2(nowvid[k],statistics_data[nowvid[k]][1],statistics_data[nowvid[k]][2],statistics_data[nowvid[k]][3],statistics_data[nowvid[k]][4]);
            }
        }
    }
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
            Chart_cleater_v2("sum-yt",statistics_data["music"][0],statistics_data["music"][1],statistics_data["music"][2],statistics_data["music"][3]);
        }
        let tbody_el = document.getElementById("tbd-" + String(njdata["pageid"]));
        for (let g=0;g<njdata["videoidlist"].length;g++){
            tbody_el.innerHTML = tbody_el.innerHTML + njdata[g];
        }
        for (let g=0;g<njdata["videoidlist"].length;g++){
            dt(njdata["videoidlist"][g]);
            Chart_cleater_v2(njdata["videoidlist"][g],statistics_data[njdata["videoidlist"][g]][1],statistics_data[njdata["videoidlist"][g]][2],statistics_data[njdata["videoidlist"][g]][3],statistics_data[njdata["videoidlist"][g]][4]);
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

function recommend(){
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
            history.replaceState(null, null, "?" + urp.toString())
        }
        let request_mr = new XMLHttpRequest();
        request_mr.open("GET", "/ajax/music/mr-" + String(now_ran) + ".json");
        request_mr.responseType = "json";
        request_mr.send();
        request_mr.onload = function () {
            const res_mr = request_mr.response;
            let divm = document.getElementById("music_recommend");
            document.getElementById("descm").innerHTML = '<hr><p class="other_music">他のおすすめの曲</p>';
            for (let i = 0; i < 20; i++) {
                divm.innerHTML = divm.innerHTML + "<a href='/music/" + res_mr[i][0] +
                    "/' onclick='rec_c()'>" + res_mr[i][0] + "<img src='https://i.ytimg.com/vi/" +
                    res_mr[i][1] + "/mqdefault.jpg' alt='" + res_mr[i][0] + "'></a>"
            }
        };
        let request_cr = new XMLHttpRequest();
        request_cr.open("GET", "/ajax/ch/cr-" + String(now_ran) + ".json");
        request_cr.responseType = "json";
        request_cr.send();
        request_cr.onload = function () {
            const res_cr = request_cr.response;
            let divc = document.getElementById("ch_recommend");
            document.getElementById("descc").innerHTML = '<hr><p class="other_music">他のおすすめのVtuber</p>';
            for (let i = 0; i < 20; i++) {
                divc.innerHTML = divc.innerHTML + "<a href='/ch/" + res_cr[i][0] +
                    "/' onclick='rec_c()'><span class='ofoverflow'>" + res_cr[i][0] +
                    "</span><img class='recommend-ch' src='" + res_cr[i][1] + "' alt='" + res_cr[i][0] +
                    "' title='" + res_cr[i][0] + "'></a>"
            }
        }
    }
}

function toppage_recommend(){
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
            history.replaceState(null, null, "?" + urp.toString())
        }
        let request_mr = new XMLHttpRequest();
        request_mr.open("GET", "/ajax/music/mr-" + String(now_ran) + ".json");
        request_mr.responseType = "json";
        request_mr.send();
        request_mr.onload = function () {
            const res_mr = request_mr.response;
            let divm = document.getElementById("music_recommend");
            document.getElementById("descm").innerHTML = '<hr><p class="other_music">おすすめの曲(ランダム表示)</p>';
            for (let i = 0; i < 20; i++) {
                divm.innerHTML = divm.innerHTML + "<a href='/music/" + res_mr[i][0] +
                    "/' onclick='rec_c()'>" + res_mr[i][0] + "<img src='https://i.ytimg.com/vi/" +
                    res_mr[i][1] + "/mqdefault.jpg' alt='" + res_mr[i][0] + "'></a>"
            }
        };
        let request_cr = new XMLHttpRequest();
        request_cr.open("GET", "/ajax/ch/cr-" + String(now_ran) + ".json");
        request_cr.responseType = "json";
        request_cr.send();
        request_cr.onload = function () {
            const res_cr = request_cr.response;
            let divc = document.getElementById("ch_recommend");
            document.getElementById("descc").innerHTML = '<hr><p class="other_music">おすすめのVtuber(ランダム表示)</p>';
            for (let i = 0; i < 20; i++) {
                divc.innerHTML = divc.innerHTML + "<a href='/ch/" + res_cr[i][0] +
                    "/' onclick='rec_c()'><span class='ofoverflow'>" + res_cr[i][0] +
                    "</span><img class='recommend-ch' src='" + res_cr[i][1] + "' alt='" + res_cr[i][0] +
                    "' title='" + res_cr[i][0] + "'></a>"
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

function music_replace_urlst(){
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
                history.replaceState(null,null,"/music/" + now_music_name + "/page" + String(k+1) + "/" + location.search)
            }
            else{
                history.replaceState(null,null,"/music/" + now_music_name + "/" + location.search)
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
    music_replace_urlst();
}

function search_index_finish(){
    search_index();
    if (top_result.length==1){
        console.log("success");
        window.location.href = top_result[0][2];
    }
    else if (sub_result.length==1){
        window.location.href = sub_result[0][2];
    }
    else if (sub_result.length==0){
        document.getElementById("search_result").innerText = "すみません1件も見つかりませんでした.";
    }
}

function search_index(){
    top_result = [];
    sub_result = [];
    let now_svalue = document.getElementById("lib_search").value.toLowerCase();
    now_svalue = now_svalue.replace(/[ァ-ン]/g, function(s) {return String.fromCharCode(s.charCodeAt(0) - 0x60);});//内部処理用にカタカナを平仮名に変換
    for(var nint=0;nint<search_index_data.length;nint++){
        let nowst = search_index_data[nint];
        for(var aint=0;aint<nowst[0].length;aint++){
            let mega_nowst = nowst[0][aint]
            if (mega_nowst===now_svalue){//完全一致
                top_result.push(nowst);
                sub_result.push(nowst);
                break;
            }
            else if (mega_nowst.indexOf(now_svalue)!=-1&&sub_result.indexOf(nowst)==-1){
                sub_result.push(nowst);
            }
        }
    }
    let result_area = document.getElementById("search_result")
    let k_strin = "";
    if (top_result.length==1){
        k_strin = "<a href='" + top_result[0][2] + "'>" + top_result[0][1] + "</a><br>"
    }
    for(var nint=0;nint<sub_result.length;nint++){
        if (top_result.length!=1){
            k_strin = k_strin + "<a href='" + sub_result[nint][2] + "'>" + sub_result[nint][1] + "</a><br>";
        }
        else if(sub_result[nint]!==top_result[0]){
            k_strin = k_strin + "<a href='" + sub_result[nint][2] + "'>" + sub_result[nint][1] + "</a><br>";
        }
    }
    if (search_index_data.length!=sub_result.length){
        result_area.innerHTML = k_strin;
    }
    else{
        result_area.innerHTML = "";
    }
}

function search_index_load(){
    let index_xhr = new XMLHttpRequest();
    index_xhr.open("GET","/search_index.json");
    index_xhr.responseType = "json";
    index_xhr.send();
    index_xhr.onload = function(){
        search_index_data = index_xhr.response["index"];
        document.getElementById('lib_search').addEventListener("input",search_index);
        document.getElementById('lib_search').addEventListener("change",search_index_finish);
        document.getElementById('lib_search').focus();
        search_index();
    }
}

function page_load(){//ページロード時の処理
    page_transition();//変数削除
    if (location.pathname.indexOf("/music/")!==-1){//音楽ページ
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
        toppage_recommend();
    }
    else if (location.pathname==="/search/"){
        search_index_load();
    }
}
page_load();