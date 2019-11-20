import bs4
import requests
import subprocess
from app import app
from flask import jsonify, request

"""
    INPUT: {'url':<url>}
    OUTPUT: [directUrl, title, likes, dislikes, date-uploaded,
             views, channel-link, channel-name, subscriber-count]
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
    channelLink = channel_soup[0]['href']
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
        video['url'] = urlSoups[i]['href']

        videos.append(video)

    ans = {}
    ans['videos'] = videos
    return jsonify(ans)

"""
    INPUT: {'query':<search_query>}
    OUTPUT: [videoUrl, duration, title, thumbnail, views, date]
"""
@app.route('/api/v1/search', methods=['POST'])
def search():
    page = request.args.get('page', default=1, type=int)
    data = request.json
    query = data['query']
    finalQuery = '+'.join(query.split(' '))
    search_url = "https://www.youtube.com/results?search_query=" + finalQuery + "&page=" + str(page)
    response = requests.get(search_url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    
    titleSoups = soup.findAll('h3', {'class':'yt-lockup-title'})
    thumbSoups = soup.findAll('img', {'height':'138', 'width':'246'})
    urlSoups = soup.findAll('a', {'class':'yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink spf-link'})
    dateViewsSoups = soup.findAll('ul', {'class':'yt-lockup-meta-info'})
    channelSoup_divs = soup.findAll('div', {'class':'yt-lockup-byline'})
    channelSoup = []
    for x in channelSoup_divs:
        tempSoup = x.find_all('a', {'class':'yt-uix-sessionlink spf-link'})
        channelSoup = channelSoup + tempSoup

    videos = []
    vidCount = len(urlSoups)
    for i in range(vidCount):
        video = {}

        try:
            title = urlSoups[i]['title']
            title_duration = titleSoups[i].text.split('Duration: ')
            duration = title_duration[1][:-1]
            video['duration'] = duration
            video['title'] = title
            video['url'] =  urlSoups[i]['href']
            video['thumbnail'] = thumbSoups[i]['data-thumb'].split('?')[0]
            date_views = dateViewsSoups[i].text.split('ago')
            video['date'] = date_views[0] + 'ago'
            video['views'] = date_views[1]
            video['channelTitle'] = channelSoup[i].text
            video['channelUrl'] = channelSoup[i]['href']

            videos.append(video)

        except Exception as e:
            pass

    #channels = []
    ans = {}
    ans['videos'] = videos
    #ans['channels'] = channels
    return jsonify(ans)

"""
    OUTPUT: [videoUrl, duration, title, thumbnail, date, views]
"""
@app.route('/api/v1/explore', methods=['GET'])
def explore():
    url = "https://www.youtube.com"
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, "html.parser")

    titleSoups = soup.findAll('h3', {'class':'yt-lockup-title'})
    thumbSoups = soup.findAll('img', {'height':'110', 'width':'196'})
    urlSoups = soup.findAll('a', {'class':'yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink spf-link'})
    dateViewsSoups = soup.findAll('ul', {'class':'yt-lockup-meta-info'})

    videos = []
    vidCount = len(urlSoups)
    for i in range(vidCount):
        video = {}

        try:
            title = urlSoups[i]['title']
            title_duration = titleSoups[i].text.split('Duration: ')
            duration = title_duration[1][:-1]
            video['duration'] = duration
            video['title'] = title
            video['url'] = urlSoups[i]['href']
            video['thumbnail'] = thumbSoups[i]['data-thumb'].split('?')[0]
            date_views = dateViewsSoups[i].text.split(' views')
            video['date'] = date_views[1]
            video['views'] = date_views[0] + ' views'

            videos.append(video)

        except Exception as e:
            pass

    ans = {'videos':videos}
    return jsonify(ans)
