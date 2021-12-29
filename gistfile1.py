#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Original script nicked from https://gist.github.com/xlexi/78f8483fa992f2ed544d

from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator, FeedEntry
from urllib import request
from urllib.parse import unquote
import datetime
import re
import subprocess
import sys


# Search YouTube for all queries starting with "The Nerd³ Podcast - Episode" made by the account officiallynerdcubed,
# yt_service = gdata.youtube.service.YouTubeService()
# query = gdata.youtube.service.YouTubeVideoQuery()
# query.vq = '\"The Nerd³ Podcast - Episode\"'
# query.author = 'officiallynerdcubed'

# Order the results by the time they were published, newest to oldest.
# query.orderby = 'published'

path = sys.argv[2]
base_url = 'http://' + sys.argv[1] + '/' + path
podcast_name = sys.argv[3]

# feed = yt_service.YouTubeQuery(query)
raw_html = subprocess.check_output(['curl', '-Ls', base_url])
parsed_html = BeautifulSoup(raw_html)


# Create a new RSS feed list.
fg = FeedGenerator()
fg.load_extension('podcast')

# Set the id and "home link" of this feed as the officiallynerdcubed YouTube channel
fg.id(base_url)
fg.link( href=base_url, rel='alternate' )

# Set the title and description of the podcast. I was not able to find a good description so I used the one from the first podcast
# let me know if anyone has ideas for a better description
fg.title(podcast_name)

show_description = podcast_name
fg.subtitle(show_description)
fg.description(show_description)
fg.podcast.itunes_summary(show_description)
fg.podcast.itunes_subtitle(show_description)

# Set the author of the podcast
# TODO from vid
fg.author(
    {'name':'None'},
)

# Set the language of the podcast as Traditional English.
fg.language('en-GB')

# While we are not on iTunes many podcast clients depend on iTunes specific information like categories to sort the podcasts
# So I include this information anyway.
fg.podcast.itunes_category('Games & Hobbies', 'Video Games')
# TODO from vid
fg.podcast.itunes_author('None')
fg.podcast.itunes_explicit('yes')

# Set the display image of the podcast.
# fg.podcast.itunes_image('http://alientube.co/artwork.jpg')

# The RSS library requires me to put an Email address for some reason so I made one up, don't bother trying this address.
fg.podcast.itunes_owner('BLUB', 'some@other.co.uk')


links = parsed_html.body.find_all('a')
links = links[1:]

basic_ffprobe_command = ['ffprobe', '-v', 'quiet', '-of',
                         'csv=p=0', '-show_entries',
                         'format_tags=']

for link in links:
    filename = unquote(link['href'])
    # Set the download link as the result.
    item_url = base_url + '/' + link['href']

    # Podcast clients expcept the description to be in HTML so we have to format it as such. We will wrap all links in an html anchor tag.
    get_description_ffprobe = basic_ffprobe_command[:-1]
    get_description_ffprobe.append(basic_ffprobe_command[-1] + 'description')
    get_description_ffprobe.append(path + '/' + filename)


    formatted_description = subprocess.check_output(get_description_ffprobe).decode('utf-8')
    # formatted_description = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))').sub(r'<a href="\1">\1</a>', formatted_description)
    # Replace all linebreak characters with an HTML linebreak tag.
    regex = '(^"|"\n$)'
    regexp_quotes = re.compile(regex, (re.M|re.DOTALL))
    # import ipdb; ipdb.set_trace()
    formatted_description = regexp_quotes.sub('', formatted_description)
    formatted_description = formatted_description.replace('\n', '<br />')


    # Create the RSS entry for this podcast item.
    entry = FeedEntry()
    entry.load_extension('podcast')

    # Set the title of this podcast episode.
    get_title_ffprobe = basic_ffprobe_command[:-1]
    get_title_ffprobe.append(basic_ffprobe_command[-1] + 'title')
    get_title_ffprobe.append(path + '/' + filename)
    title = subprocess.check_output(get_title_ffprobe).decode('utf-8')
    title = regexp_quotes.sub('', title)
    entry.title(title)

    # Set the id and home link for this episode as the YouTube video.
    entry.id(item_url)
    entry.link(href=item_url, rel='alternate')

    # Set the description of the podcast episode to the formatted version we created earlier.
    entry.description(formatted_description)

    # Set the duration/length of the podcast, converting it from number of seconds to H:m:s
    duration = subprocess.check_output(['ffprobe-get-duration',
                                        path + '/' + filename])

    duration = duration.split(b'.')[0].decode('utf-8')
    duration = int(duration)
    entry.podcast.itunes_duration(duration)

    # Set the published date of the podcast.
    date = subprocess.check_output(['ffprobe-get-date',
                                    path + '/' + filename])
    entry.pubdate('{} 00:00 +0000'.format(date.decode('utf-8')))

    # For some reason many podcast clients use the artwork from the episodes instead of the show itself, set the same image here.
    entry.podcast.itunes_image('http://alientube.co/artwork.jpg')

    # They swear a fair bit so we will set the explicit tag in case it may be useful to someone.
    entry.podcast.itunes_explicit('yes')

    # Set podcast episode author
    entry.podcast.itunes_author('Daniel Hardcastle & Wot Fanar')

    # Set the episode summary as the first line of the YouTube description.
    episode_summary = formatted_description[0]
    entry.podcast.itunes_summary(episode_summary)
    entry.podcast.itunes_subtitle(episode_summary)

    # Connect to the episode download link without downloading and grab the HTTP headers.
    site = request.urlopen(item_url)
    meta = site.info()

    # Set the download link in the RSS item, providing the file length and file size from the HTTP headers.
    entry.enclosure(item_url, meta['Content-Length'], meta['Content-Type'])

    # Add the entry to the feed.
    fg.add_entry(entry)

# Export the feed.
fg.rss_str(pretty=True)
fg.rss_file(podcast_name + '.xml')
