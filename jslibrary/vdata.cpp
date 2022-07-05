#include <fstream>
#include <string>
#include <iostream>
#include <chrono>
#include <filesystem>
#include <regex>
#include "json.hpp"

using json = nlohmann::json;
using namespace std;

std::string url_decode(std::string src){
    std::string ret;
    char ch;
    int i,ii;
    for(i=0; i<src.length(); i++){
        if(int(src[i]) == 37){
        sscanf(src.substr(i+1,2).c_str(), "%x", &ii);
        ch = static_cast<char>(ii);
        ret += ch;
        i = i+2;
        }else{
            ret += src[i];
        }
    }
    return (ret);
}

int main(){
    json res_js;//返信用jsonを定義
    res_js["plang"] = "c++";
    //クエリ文字を受け取り
    std::string now_query_string = getenv("QUERY_STRING");
    std::string now_query = url_decode(now_query_string.substr(2));
    string now_mode = now_query_string.substr(0,1);

    //簡易セキュリティ対策
    if (now_query.find(".") != std::string::npos || now_query.find("/") != std::string::npos){
        std::cout << "Content-Type: application/json";
        std::cout << "\n\n";
        std::cout << "{\"status\":\"error\",\"erms\":\"security error\"}" << std::endl;
        return -1;
    }

    now_query += ".json";

    //string now_query = "Alice in NY";

    string documentroot = getenv("DOCUMENT_ROOT");

    string now_fp = "";
    if (now_mode=="m"){
        now_fp = documentroot + "/api/v4/music/" + now_query;
    }
    else if (now_mode=="c"){
        now_fp = documentroot + "/api/v4/ch/" + now_query;
    }
    else{
        std::cout << "Content-Type: application/json";
        std::cout << "\n\n";
        std::cout << "{\"status\":\"error\",\"erms\":\"invalid query string\"}" << std::endl;
        return -1;
    }
    ifstream ifs(std::filesystem::path(now_fp).make_preferred());
    if (ifs.fail())//読めなければエラーを出す
    {
        std::cout << "Content-Type: application/json";
        std::cout << "\n\n";
        std::cout << "{\"status\":\"error\",\"erms\":\"file not found\",\"query\":\"" + now_query + "\"}" << std::endl;
        return -1;
    }
    //一気に読んで格納
    std::istreambuf_iterator<char> it(ifs);
    std::istreambuf_iterator<char> last;
    std::string string_n(it, last);
    //jsonをパース
    auto musicjson = json::parse(string_n);
    //musicvideolistにvideoidを格納
    vector<std::string> musicvideolist = musicjson["videolist"];
    //ループでデータ取得しres_jsに格納
    for (int x = 0;x<musicvideolist.size();x++){
        string nowvidid = musicvideolist[x];
        //ファイル読み出し
        std::filesystem::path np = documentroot + "/api/v4/videoid/" + nowvidid + ".json";
        ifstream ifs(np.make_preferred());//videodata
        if (ifs.fail()){//エラーの時データはerにする
            res_js[nowvidid] = "er";
        }
        else{
            std::istreambuf_iterator<char> it(ifs);
            std::istreambuf_iterator<char> last;
            std::string string_n(it, last);
            auto k_json = json::parse(string_n);
            k_json["statisticsdata"] = k_json["statisticsdata"][0];
            res_js[nowvidid] = k_json;
        }
    }
    //jsonを出力
    res_js["status"] = "success";
    std::cout << "Content-Type: application/json";
    std::cout << "\n\n";
    std::cout << res_js.dump() << std::endl;
}