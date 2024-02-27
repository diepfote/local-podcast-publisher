#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Original script nicked from https://gist.github.com/xlexi/78f8483fa992f2ed544d

from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator, FeedEntry
from urllib import request
from urllib.parse import unquote, quote
import datetime
import re
import subprocess
import sys


import urllib
host = sys.argv[1]
path = sys.argv[2]
base_url = f'http://{host.rstrip("/")}/{urllib.parse.quote(path.rstrip("/") + "/")}'
podcast_name = sys.argv[3]

raw_html = subprocess.check_output(['curl', '-Ls', base_url])
parsed_html = BeautifulSoup(raw_html)


fg = FeedGenerator()
fg.load_extension('podcast')

fg.id(base_url)
fg.link( href=base_url, rel='alternate' )

fg.title(podcast_name)

image_location = 'http://' + host + '/' + quote(podcast_name) + '.jpg'
fg.image(image_location)

show_description = podcast_name
fg.subtitle(show_description)
fg.description(show_description)
fg.podcast.itunes_summary(show_description)
fg.podcast.itunes_subtitle(show_description)

fg.author(
    {'name':'None'},
)

fg.language('en-GB')

fg.podcast.itunes_category('Games & Hobbies', 'Video Games')
fg.podcast.itunes_author('None')
fg.podcast.itunes_explicit('yes')

fg.podcast.itunes_owner('BLUB', 'some@other.co.uk')

links = parsed_html.body.find_all('a')
links = links[1:]

basic_ffprobe_command = ['ffprobe', '-v', 'quiet', '-of',
                         'csv=p=0', '-show_entries',
                         'format_tags=']

for link in links:
    filename = unquote(link['href'])
    if filename.endswith('.mp4'):
        continue
    # Set the download link as the result.
    item_url = f'{base_url.rstrip("/")}/{link["href"]}'

    # Podcast clients expcept the description to be in HTML so we have to format it as such. We will wrap all links in an html anchor tag.
    get_description_ffprobe = basic_ffprobe_command[:-1]
    get_description_ffprobe.append(basic_ffprobe_command[-1] + 'description')
    get_description_ffprobe.append(f'{path.rstrip("/")}/{filename}')


    formatted_description = subprocess.check_output(get_description_ffprobe).decode('utf-8')
    # Replace all linebreak characters with an HTML linebreak tag.
    regex = '(^"|"\n$)'
    regexp_quotes = re.compile(regex, (re.M|re.DOTALL))
    formatted_description = regexp_quotes.sub('', formatted_description)
    formatted_description = formatted_description.replace('\n', '<br />')


    entry = FeedEntry()
    entry.load_extension('podcast')

    # Set the title of this podcast episode.
    get_title_ffprobe = basic_ffprobe_command[:-1]
    get_title_ffprobe.append(basic_ffprobe_command[-1] + 'title')
    get_title_ffprobe.append(f'{path.rstrip("/")}/{filename}')
    title = subprocess.check_output(get_title_ffprobe).decode('utf-8')
    title = regexp_quotes.sub('', title)
    regex = '^\\s*$'
    regex_ws = re.compile(regex, (re.M|re.DOTALL))
    if regex_ws.match(title):
        title = filename
    entry.title(title)

    # Set the id and home link for this episode as the YouTube video.
    entry.id(item_url)
    entry.link(href=item_url, rel='alternate')

    # Set the description of the podcast episode to the formatted version we created earlier.
    entry.description(formatted_description)

    # Set the duration/length of the podcast, converting it from number of seconds to H:m:s
    duration = subprocess.check_output(['ffprobe-get-duration',
                                       f'{path.rstrip("/")}/{filename}'])


    duration = duration.split(b'.')[0].decode('utf-8')
    duration = int(duration)
    entry.podcast.itunes_duration(duration)

    # Set the published date of the podcast.
    date = subprocess.check_output(['ffprobe-get-date',
                                   f'{path.rstrip("/")}/{filename}'])
    entry.pubDate('{} 00:00 +0000'.format(date.decode('utf-8')))

    # For some reason many podcast clients use the artwork from the episodes instead of the show itself, set the same image here.
    entry.podcast.itunes_image(image_location)

    # They swear a fair bit so we will set the explicit tag in case it may be useful to someone.
    entry.podcast.itunes_explicit('yes')

    episode_summary = formatted_description[0]
    entry.podcast.itunes_summary(episode_summary)
    entry.podcast.itunes_subtitle(episode_summary)

    # Connect to the episode download link without downloading and grab the HTTP headers.
    # extracts Content-Length and Content-Type
    site = request.urlopen(item_url)
    meta = site.info()

    # Set the download link in the RSS item, providing the file length and file size from the HTTP headers.
    entry.enclosure(item_url, meta['Content-Length'], meta['Content-Type'])

    # Add the entry to the feed.
    fg.add_entry(entry)

# Export the feed.
fg.rss_str(pretty=True)
fg.rss_file(podcast_name + '.xml')
