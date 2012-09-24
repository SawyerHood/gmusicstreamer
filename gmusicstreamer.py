"""
Copyright (C) 2012 Sawyer Hood

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



"""






from gmusicapi.api import Api
from getpass import getpass
import os
import mpd
import time
import threading

os.system("ls -l")

"""This thread constantly watches to make sure that the newest songs from the Google Music playlist are fetched and added to the queue"""
class playlistWatcher(threading.Thread):

    def __init__(self, api, io):
        threading.Thread.__init__(self)
        
        self.api = api
        self.io = io
        


    def run(self):
        while self.io.isrunning:
            songs = self.api.get_playlist_songs(self.io.playlist_id)
            if songs != False:
                for song in songs:

                    self.io.playlist.append(song['id'])
                    self.api.remove_songs_from_playlist(self.io.playlist_id, song['id'])
            time.sleep(5.0)
                

"""This thread sends songs from the queue to MPD """
class musicinterfacer(threading.Thread):

    def __init__(self, api, io):
        threading.Thread.__init__(self)
        self.isPaused = False
        self.i = -1
        self.io = io
        self.api = api
        self.switchingsong = False

    def run(self):
        #print "i = ", self.i
        #print len(self.io.playlist)
        #os.system("mpc clear")
        #os.system("mpc add \"" + self.api.get_stream_url(self.io.playlist[self.i]) + "\"")
        #os.system("mpc play")
           
        #time.sleep(.5)
        while self.io.isrunning:

            while not self.isPaused and not self.switchingsong:
                    if "audio" not  in self.io.client.status():
                        self.next()
                        time.sleep(1.0)

                        

                    
    def pause(self):
        self.isPaused = True
        os.system("mpc stop")

    def next(self):
        if len(self.io.playlist) > 0 and self.i < len(self.io.playlist):
            
            self.switchingsong = True
            self.i += 1
            print "i = ", self.i
            if self.i < len(self.io.playlist) and self.i >= 0 and len(self.io.playlist) > 0:
                os.system("mpc clear")
                os.system("mpc add \"" + self.api.get_stream_url(self.io.playlist[self.i]) + "\"")
                os.system("mpc play")
           
                time.sleep(.5)
            self.switchingsong = False

    def back(self):
        self.switchingsong = True
        self.i -= 1
        if self.i < 0:
            self.i = 0 


        if self.i < len(api.playlist) and self.i >= 0:

            os.system("mpc clear")
            os.system("mpc add \"" + api.get_stream_url(api.playlist[self.i]) + "\"")
            os.system("mpc play")
            
            time.sleep(.5)
            self.switchingsong = False

    def play(self):
        self.isPaused = False
        os.system("mpc play")






"""This thread is responsible for taking userinput and controlling the playlist."""
class iohandler(threading.Thread):

    def __init__(self, api,playlist,playlist_id, client):
        threading.Thread.__init__(self)
        self.isrunning = True
        self.api = api
        self.client = client
        self.playlist = playlist
        self.playlist_id = playlist_id
        self.playlistupdater = playlistWatcher(self.api, self)
        self.playlistupdater.start()
        time.sleep(.5)
        self.musichandler = musicinterfacer(api, self)
        self.musichandler.start()

    def run(self):
        while self.isrunning == True:
            userinput = raw_input('Enter Command: ')
            if "play" in userinput:
                self.musichandler.play()
            elif "next" in userinput:
                #Make music interfacer skip the song
                self.musichandler.next()
            elif "back" in userinput:
                #Make music interfacer play the previous song
                self.musichandler.back()
            elif "pause" in userinput:
                #Make music interfacer pause
                self.musichandler.pause()
            elif "exit" in userinput:
                #Exit the program
                self.musichandler.pause()
                self.isrunning = False

            else:
                print "Sorry command not detected."

        print "Done! Cleaning up..."
        
    
        self.api.logout()




def init():
    """Makes an instance of the api and attempts to login with it.
    Returns the authenticated api.
    """
    
    api = Api() 
    
    logged_in = False
    attempts = 0

    while not logged_in and attempts < 3:
        email = raw_input("Email: ")
        password = getpass()

        logged_in = api.login(email, password)
        attempts += 1

    return api

def main():

    

    #Make a new instance of the api and prompt the user to log in.
    api = init()
    client = mpd.MPDClient()           # create client object
    client.connect("localhost", 6600,  # connect to localhost:6600
                timeout=10)        # optional timeout in seconds (floats allowed), default: None
    

    if not api.is_authenticated():
        print "Sorry, those credentials weren't accepted."
        return

    print "Successfully logged in."
    print

    #Get all of the users songs.
    #library is a big list of dictionaries, each of which contains a single song.
    print "Loading playlists..."
    
    playlist_id = ''
    playlists = api.get_all_playlist_ids(True, True, False)['user']
    if playlists.has_key('Pi queue'):
       playlist_id = playlists['Pi queue']

    else:
        playlist_id = api.create_playlist("Pi queue")
        raw_input("\'Pi queue\' playlist created, add songs to it via google music and press any key to add.")
    songIds = list()
    """songs = api.get_playlist_songs(playlist_id)
    if songs != False:
        for song in songs:
            songIds.append(song['id'])"""

    
    mainthread = iohandler(api, songIds, playlist_id, client)
    mainthread.setDaemon(True)
    mainthread.start() 
    

if __name__ == '__main__':
    main()
	

