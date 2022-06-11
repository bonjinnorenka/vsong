import MySQLdb
import sys
from pytube import Playlist
import ev
playlist_id = str(sys.argv[1])
playlist = Playlist("https://www.youtube.com/playlist?list=" + playlist_id)
ins_playlist = [str(playlist[x])[32:] for x in range(len(playlist))]
connection = MySQLdb.connect(host=ev.mysql_host,user=ev.mysql_user,passwd=ev.mysql_ps,db="vsong")
cur = connection.cursor()
cur.executemany("INSERT INTO vsong.tmp_vid (videoid) VALUES (%s)",ins_playlist)
connection.commit()
cur.close()
connection.close()