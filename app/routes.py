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
    OUTPUT: [videoUrl, duration, title, thumbnail, views, date]
"""
@app.route('/api/v1/channelinfo', methods=['POST'])
def channelinfo():
    data = request.json
    channelUrl = data['url'] + '/videos'
    response = requests.get(channelUrl)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    titleSoups = soup.findAll('h3', {'class':'yt-lockup-title'})
    thumbSoups = soup.findAll('img', {'aria-hidden':'true', 'width':'196'})
    viewsSoups = soup.findAll('ul', {'class':'yt-lockup-meta-info'})
    urlSoups = soup.findAll('a', {'class':'yt-uix-sessionlink yt-uix-tile-link spf-link yt-ui-ellipsis yt-ui-ellipsis-2'})

    videos = []
    vidCount = len(titleSoups)
    for i in range(vidCount):
        video = {}

        title_duration = titleSoups[i].text.split('Duration')
        video['title'] = title_duration[0][:-3]
        video['duration'] = title_duration[1][2:-1]
        video['thumbnail'] = thumbSoups[i]['src'].split('?')[0]
        views_date = viewsSoups[i].text.split('views')
        video['views'] = views_date[0] + 'views'
        video['date'] = views_date[1]
        video['url'] = 'https://youtube.com' + urlSoups[i]['href']

        videos.append(video)

    ans = {}
    ans['videos'] = videos
    return jsonify(ans)

"""
    INPUT: {'query':<search_query>}
    OUTPUT: [videoUrl, duration, title, thumbnail, views]
"""
@app.route('/api/v1/search', methods=['POST'])
def search():
    data = request.json
    query = data['query']
    finalQuery = '+'.join(query.split(' '))
    search_url = "https://www.youtube.com/results?search_query=" + finalQuery
    ans = {'views':'1'}
    return jsonify(ans)

"""
    OUTPUT: [videoUrl, duration, title, thumbnail, views]
"""
@app.route('/api/v1/hot', methods=['GET'])
def hot():
    ans = {'views':'1'}
    return jsonify(ans)
