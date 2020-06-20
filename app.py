from flask import Flask, render_template, request

app = Flask(__name__)


import os
import re
from datetime import timedelta
from googleapiclient.discovery import build

pl_id = "enter any playlist id to check without youtube api (for testing purpose only)"
api_key = 'ENTER_YOUR_API_KEY_HERE'

youtube = build('youtube', 'v3', developerKey=api_key)

hours_pattern = re.compile(r'(\d+)H')
minutes_pattern = re.compile(r'(\d+)M')
seconds_pattern = re.compile(r'(\d+)S')


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/", methods=['POST'])
def process_time():
    newid = request.form['plinput']
    error = "Wrong Url Entered"

    def get_id(playlist_link):
        p = re.compile('^([\S]+list=)?([\w_-]+)[\S]*$')
        m = p.match(playlist_link)
        if m:
            return m.group(2)
        else:
            return render_template("index.html", h=hours, m=minutes, s=seconds, errormessage=error)

    pl_id = get_id(newid)
    nextPageToken = None
    total_seconds = 0
    while True:
        pl_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=pl_id,
            maxResults=50,
            pageToken=nextPageToken
        )

        pl_response = pl_request.execute()

        vid_ids = []
        for item in pl_response['items']:
            vid_ids.append(item['contentDetails']['videoId'])

        vid_request = youtube.videos().list(
            part="contentDetails",
            id=','.join(vid_ids)
        )

        vid_response = vid_request.execute()

        for item in vid_response['items']:
            duration = item['contentDetails']['duration']

            hours = hours_pattern.search(duration)
            minutes = minutes_pattern.search(duration)
            seconds = seconds_pattern.search(duration)

            hours = int(hours.group(1)) if hours else 0
            minutes = int(minutes.group(1)) if minutes else 0
            seconds = int(seconds.group(1)) if seconds else 0

            video_seconds = timedelta(
                hours=hours,
                minutes=minutes,
                seconds=seconds
            ).total_seconds()

            total_seconds += video_seconds

        nextPageToken = pl_response.get('nextPageToken')

        if not nextPageToken:
            break

    total_seconds = int(total_seconds)

    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours or minutes or seconds:
        return render_template("index.html", h=hours, m=minutes, s=seconds)


if __name__ == "__main__":
    print("Executed when invoked directly")
    app.run()
