#! C:\Users\ryo\AppData\Local\Programs\Python\Python310\python
import json
import os
import cgi
import sys

def return_json(resjson):
    print("Content-Type: application/json\n\n" + json.dumps(resjson))
    sys.exit()

res_js = {}
now_mode = cgi.FieldStorage().keys()
#now_mode = "m"
if len(now_mode)!=1:
    res_js = {"status":"error","erms":"too many query string"}
    return_json(res_js)
now_mode = now_mode[0]
now_query = os.path.basename(cgi.FieldStorage().getfirst(now_mode))
#now_query = "KING"
documentroot = os.getenv("DOCUMENT_ROOT")
now_fp = ""
now_query += ".json"
if now_mode=="m":
    now_fp = documentroot + "/api/v4/music/" + now_query
elif now_mode=="c":
    now_fp = documentroot + "/api/v4/ch/" + now_query
else:
    res_js = {"status":"error","erms":"invalid query string"}
    return_json(res_js)
nowj = {}
try:
    with open(now_fp,"r",encoding="utf-8") as f:
        nowj = json.load(f)
except:
    res_js = {"status":"error","erms":"file not found","nowquery":now_fp}
    return_json(res_js)
nowvidlist = nowj["videolist"]
for r in nowvidlist:
    try:
        with open(documentroot + "/api/v4/videoid/" + r + ".json","r",encoding="utf-8") as f:
            nowj = json.load(f)
        res_js[r] = nowj
    except:
        res_js[r] = "er"
res_js["status"] = "success"
return_json(res_js)