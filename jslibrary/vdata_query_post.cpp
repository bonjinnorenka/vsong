#include <fstream>
#include <string>
#include <iostream>
#include <chrono>
#include <filesystem>
#include "json.hpp"

using json = nlohmann::json;

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
    std::vector<std::string> query_videoid_array;

    //リクエスト方法を判別
    
    if ((std::string)std::getenv("REQUEST_METHOD")==(std::string)"POST"){
        //標準入力受け取り
        std::string receive_jsstring;
        std::cin >> receive_jsstring;

        //jsonをパース
        json receive_json = json::parse(receive_jsstring);
        query_videoid_array = (std::vector<std::string>)receive_json["videoid"];
    }
    else if ((std::string)std::getenv("REQUEST_METHOD")==(std::string)"GET"){
        std::string now_query_string = getenv("QUERY_STRING");//querystringを取得
        std::string now_query_st = url_decode(now_query_string.substr(2));

        std::string separator = std::string("|");         // 区切り文字
        int separator_length = separator.length(); // 区切り文字の長さ

        if (separator_length == 0) {
            query_videoid_array.push_back(now_query_st);
            } else {
            auto offset = std::string::size_type(0);
            while (1) {
                auto pos = now_query_st.find(separator, offset);
                if (pos == std::string::npos) {
                query_videoid_array.push_back(now_query_st.substr(offset));
                break;
                }
                query_videoid_array.push_back(now_query_st.substr(offset, pos - offset));
                offset = pos + separator_length;
            }
            }
    }
    else {
        res_js["error"] = "unknown requests";
        res_js["method"] = std::getenv("REQUEST_METHOD");
    }


    //htmlたちがいるところを取得
    std::string documentroot = getenv("DOCUMENT_ROOT");

    //std::string documentroot = "C:\\Users\\ryo\\Documents\\vscode\\vsong\\public\\vsong.fans";

    //ぶん回して情報取得

    for(int x = 0;x<query_videoid_array.size();x++){
        std::string nowvidid = query_videoid_array[x];
        //ファイル読み出し
        std::filesystem::path np = documentroot + "/api/v4/videoid/" + nowvidid + ".json";
        std::ifstream ifs(np.make_preferred());//videodata
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

    //出力
    res_js["status"] = "success";
    std::cout << "Content-Type: application/json";
    std::cout << "\n\n";
    std::cout << res_js.dump() << std::endl;
}
