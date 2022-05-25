import MySQLdb
import sys
from pytube import Playlist
import ev
connection = MySQLdb.connect(host=ev.mysql_host,user=ev.mysql_user,passwd=ev.mysql_ps,db="vsong")
cur = connection.cursor()
playlist_id = str(sys.argv[1])
playlist = Playlist("https://www.youtube.com/playlist?list=" + playlist_id)
for n in range(len(playlist)):
    cur.execute("INSERT INTO vsong.tmp_vid (videoid) VALUES ('" + (str(playlist[n])[32:]) + "')")
connection.commit()
cur.close()
connection.close()