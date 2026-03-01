import requests
import xml.etree.ElementTree as ET

def get_news(uri="https://www.n-tv.de/rss"):

    response = requests.get(uri)
    response.encoding = 'utf-8'
    root = ET.fromstring(response.text)

    channel = root.find('channel')

    news = []

    for item in channel.findall('item'):
        title = item.find('title').text
        description = item.find('description').text
        news.append((title, description))


    return news