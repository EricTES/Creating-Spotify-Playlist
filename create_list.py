"""
Step 1: Log onto Youtube
Step 2: Grab Liked Video
Step 3: Create a New Playlist
Step 4: Search for the Song
Step 5: Add this song into the new Spotify playlist
"""
import json
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests

import youtube_dl


from secrets import id, token


class CreatePlaylist:

    def __init__(self):
        self.youtube_client = self.log_in_youtube()
        self.song_list={}

    def log_in_youtube(self):
        """ Log Into Youtube, Copied from Youtube Data API """
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client

    def get_liked_videos(self):
        """Grab Our Liked Videos & Create A Dictionary Of Important Song Information"""
        request = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like"
        )
        response = request.execute()

        # collect each video and get important information
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"])

            # use youtube_dl to collect the song name & artist name
            video = youtube_dl.YoutubeDL({}).extract_info(
                youtube_url, download=False)
            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:
                # save all important info and skip any missing song and artist
                self.song_list[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,

                    # add the uri, easy to get song to put into playlist
                    "spotify_uri": self.get_spotify_song(song_name, artist)

                }


    def create_playlist(self):
        request_body = json.dumps({
            "name": "New Playlist",
            "description": "New playlist description",
            "public": False})

        url = "https://api.spotify.com/v1/users/{}/playlists".format(id)

        r = requests.post(
            url,
            data = request_body,
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer {}".format(token)}
        )

        response = r.json()
        return response["id"]

    def get_spotify_song(self, song,artist):
        url = "https://api.spotify.com/v1/search?q=track:{}%20artist:{}&type=track&limit=20".format(song, artist)

        r = requests.get(
            url,
            headers={"Authorization": "Bearer {}".format(token)}
        )

        response = r.json()
        uri = response["tracks"]["items"][0]["uri"]

        return uri

    def add_to_playlist(self):
        """Add all liked songs into a new Spotify playlist"""
        # populate dictionary with our liked songs
        self.get_liked_videos()

        # collect all of uri
        uris = [info["spotify_uri"]
                for song, info in self.all_song_info.items()]

        # create a new playlist
        playlist_id = self.create_playlist()

        # add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )



c = CreatePlaylist()
