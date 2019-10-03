import bs4
import requests
import subprocess
from app import app
from flask import jsonify, request

"""
    INPUT: {'url':<url>}
    OUTPUT: [directUrl, likes, dislikes, date-uploaded,
             views, channel, subscriber-count]
"""
@app.route('/api/v1/urlinfo', methods=['POST'])
def urlinfo():
    data = request.json
    url = data['url']
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    title_soup = soup.findAll('span', {'class':'watch-title'})
    viewCount_soup= soup.findAll('span', {'class':'view-count'})
    subCount_soup= soup.findAll('span', {'class':'yt-subscriber-count'})
    channel_soup = soup.findAll('a', {'class':'yt-uix-sessionlink spf-link'})
    date_soup = soup.findAll('strong', {'class':'watch-time-text'})
    likes_soup = soup.findAll('button', {'class':'like-button-renderer-like-button'})
    dislikes_soup = soup.findAll('button', {'class':'like-button-renderer-dislike-button'})

    title = title_soup[0].text
    views = viewCount_soup[0].text
    subCount = subCount_soup[0]['aria-label']
    channelName = channel_soup[0].text
    channelLink = 'https://youtube.com' + channel_soup[0]['href']
    date = date_soup[0].text
    likes = likes_soup[0].text
    dislikes = dislikes_soup[0].text
    directUrl = subprocess.check_output(['youtube-dl','-f','best','--get-url',url])

    ans = {
            'title':title,
            'views':views,
            'subCount':subCount,
            'channelName':channelName,
            'channelLink':channelLink,
            'date':date,
            'likes':likes,
            'dislikes':dislikes,
            'directUrl': directUrl.split(b'\n')[0].decode('utf-8')
        }
    return jsonify(ans)

"""
    INPUT: {'url':<url>}
    OUTPUT: [videoUrl, duration, title, thumbnail, views]
"""
@app.route('/api/v1/channelinfo', methods=['POST'])
def channelinfo():
    ans = {'views':'1'}
    return jsonify(ans)

"""
    INPUT: {'query':<search_query>}
    OUTPUT: [videoUrl, duration, title, thumbnail, views]
"""
@app.route('/api/v1/search', methods=['POST'])
def search():
    ans = {'views':'1'}
    return jsonify(ans)

"""
    OUTPUT: [videoUrl, duration, title, thumbnail, views]
"""
@app.route('/api/v1/hot', methods=['GET'])
def hot():
    ans = {'views':'1'}
    return jsonify(ans)
