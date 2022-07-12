#include <fstream>
#include <string>
#include <iostream>
#include <chrono>
#include <filesystem>
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
    std::string now_query_string = getenv("QUERY_STRING");
    std::string now_query_st = url_decode(now_query_string.substr(2));
    auto separator = std::string("|");         // 区切り文字
    auto separator_length = separator.length(); // 区切り文字の長さ

    std::vector<std::string> index_vid;
    string documentroot = getenv("DOCUMENT_ROOT");
    
    if (separator_length == 0) {
    index_vid.push_back(now_query_st);
    } else {
    auto offset = std::string::size_type(0);
    while (1) {
        auto pos = now_query_st.find(separator, offset);
        if (pos == std::string::npos) {
        index_vid.push_back(now_query_st.substr(offset));
        break;
        }
        index_vid.push_back(now_query_st.substr(offset, pos - offset));
        offset = pos + separator_length;
    }
    }

    //ループでデータ取得しres_jsに格納
    for (int x = 0;x<index_vid.size();x++){
        string nowvidid = index_vid[x];
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