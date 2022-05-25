#include <fstream>
#include <string>
#include <iostream>
#include <chrono>
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

int main()
{
    json res_js;//返信用jsonを定義
    res_js["st_time"] = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    
    auto start = std::chrono::system_clock::now();

    
    ifstream ifs("search_index_a.rcsv");
    if (ifs.fail())
    {
        std::cout << "Content-Type: application/json";
        std::cout << "\n\n";
        std::cout << "{status:\"error\"}";
        return -1;
    }
    std::istreambuf_iterator<char> it(ifs);
    std::istreambuf_iterator<char> last;
    std::string string_n(it, last);
    auto separator = std::string("@");         // 区切り文字
    auto separator_length = separator.length(); // 区切り文字の長さ
    

    std::vector<std::string> obj_index_search;

    
    if (separator_length == 0) {
    obj_index_search.push_back(string_n);
    } else {
    auto offset = std::string::size_type(0);
    while (1) {
        auto pos = string_n.find(separator, offset);
        if (pos == std::string::npos) {
        obj_index_search.push_back(string_n.substr(offset));
        break;
        }
        obj_index_search.push_back(string_n.substr(offset, pos - offset));
        offset = pos + separator_length;
    }
    }
    

    /*
    FILE* fp = fopen("search_index_a.json","r");
    json search_index_parse = json::parse(fp);
    fclose(fp);
    std::vector<std::string> obj_index_search = search_index_parse["index"];
    */
    
    std::string now_query_string = getenv("QUERY_STRING");
    std::string now_query = url_decode(now_query_string.substr(2));
    
    //std::string now_query = "ときのそら";

    auto end = std::chrono::system_clock::now();   
    auto dur = end - start;// 要した時間を計算
    auto msec_f = std::chrono::duration_cast<std::chrono::milliseconds>(dur).count();

    //一時格納用配列定義
    std::vector<std::string> top_hit;
    std::vector<std::string> sub_hit;

    for (int x = 0;x<obj_index_search.size()/3;x++){
        std::string now_key = obj_index_search[3*x];
        if(now_key==now_query){//キーワード完全一致
            top_hit.push_back(obj_index_search[3*x+1]);
            top_hit.push_back(obj_index_search[3*x+2]);
        }
        else if(now_key.find(now_query) != std::string::npos){//部分一致
            if(sub_hit.size()<100&&std::find(sub_hit.begin(),sub_hit.end(),obj_index_search[3*x+2])==sub_hit.end()){
                sub_hit.push_back(obj_index_search[3*x+1]);
                sub_hit.push_back(obj_index_search[3*x+2]);
            }
        }
    }
    
    //jsonに格納
    res_js["top_hit"] = top_hit;
    res_js["sub_hit"] = sub_hit;
    res_js["query"] = now_query;
    res_js["jsonloadtime"] = msec_f;
    std::cout << "Content-Type: application/json";
    std::cout << "\n\n";
    std::cout << res_js.dump() << std::endl;
}