import feedparser
import re
import requests
import os

IMG_DIR = 'img'
CONTENT_DIR = 'content'
MY_URL = 'karljohannisson.com'

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

if not os.path.exists(CONTENT_DIR):
    os.makedirs(CONTENT_DIR)

with open('rss_file.xml', 'r') as file:
    file_content = file.read()

feed = feedparser.parse(file_content)

def download_images(urls):
    for url in urls:
        download_image(url)

def download_image(url):
    filename = os.path.join(IMG_DIR , re.findall(r'.*\/(.+)', url)[0])
    if not os.path.exists(filename):
        response=requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f'image downloaded successfully: {filename}')
        else:
            print(f'failed to download {filename}')
    else:
        print(f'skipping download, file already exists: {filename}')

def write_md_to_file(entry_filename, entry_content):
    filename = os.path.join(CONTENT_DIR, entry_filename)
    with open(filename, 'w') as file:
        file.write(entry_content)

def table_to_markdown(match):
    table = match.group(1)
    rows = re.findall(r'<tr>(.*?)</tr>', table, re.DOTALL)
    md_rows = []
    for i, row in enumerate(rows):
        cells = re.findall(r'<t[hd]>(.*?)</t[hd]>', row)
        cells = [re.sub(r'</?em>', '*', cell) for cell in cells]  # Handle emphasis
        md_rows.append("| " + " | ".join(cells) + " |")
        if i == 0:  # After header row
            md_rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return "\n\n" + "\n".join(md_rows) + "\n\n"

for entry in feed.entries:
    
    print(entry)
    print(entry.wp_post_date)

    entry_filename = re.sub(r'.*?/.*?/.*?/(.*?)/', r'\1', entry.link) + '.md'
    if MY_URL in entry_filename or entry.wp_status != 'publish' or entry.wp_post_type != 'post':
        continue
    
    metadata_string = f"""---
    'title': {entry.title}
    'date': {re.sub(r'(\d{4}-\d{2}-\d{2}).*', r'\1', entry.wp_post_date)}
    'url_name': {re.sub(r'.*?/.*?/.*?/(.*?)/', r'\1', entry.link)}
---"""

    
    #entry_filename = entry.title
    #entry_filename = entry_filename.lower()
    #entry_filename = re.sub(r'[\s\W]', '-', entry_filename)
    #entry_filename = entry_filename + '.md'

    #if entry_filename != 'quitting-alcohol-and-its-benefits.md':
    #    continue


    entry_content = str(entry.content[0].value)
    #clean paragraphs
    entry_content = entry_content.replace('<!-- wp:paragraph -->', '')
    entry_content = entry_content.replace('<!-- /wp:paragraph -->', '')
    entry_content = entry_content.replace('</p>', '')
    entry_content = entry_content.replace('<p>', '')

    # fix numbered lists
    entry_content = re.sub(r'(\n)(\.)(\d\.)', r'\1\3', entry_content)


    #convert lists
    entry_content = entry_content.replace(r'<li>', r'- ')
    entry_content = entry_content.replace(r'</li>', r'')
    entry_content = entry_content.replace(r'<!-- wp:list-item -->', r'')
    entry_content = entry_content.replace(r'<!-- /wp:list-item -->', r'')
    entry_content = re.sub(r'<!-- wp:list.*-->', r'', entry_content)
    entry_content = re.sub(r'<!-- /wp:list -->', r'', entry_content)

    entry_content = re.sub(r'<[ou]l.*>', r'', entry_content)
    entry_content = re.sub(r'</[ou]l>', r'', entry_content)
    entry_content = re.sub(r'((?:- |\d*\. ).*)([\n]{4})((?:-|\d*\.))', r'\1\n\3', entry_content)

    # headings
    heading_replacement = lambda m: '#' * int(m.group('h')) + ' ' + m.group('title')
    entry_content = re.sub(r'<!-- wp:heading.*\n<h(?P<h>\d).*?>(?P<title>.*?)<.*\n<!-- /wp:heading -->', heading_replacement, entry_content)

    #bold
    entry_content = re.sub(r'<strong>(.*)</strong>', r'**\1**', entry_content)

    # links
    entry_content = re.sub(r'<a .*?href=".*?/.*?/.*?' + MY_URL + r'.*?/(.*?)".*?>(.*?)<.*?/a>', r'[\2](\1)', entry_content)
    entry_content = re.sub(r'<a .*?href="(.*?)".*?>(.*?)<.*?/a>', r'[\2](\1)', entry_content)

    # images
    entry_content = re.sub(r'<!-- (?:|\/)wp:image.*?-->', r'', entry_content)
    entry_content = re.sub(r'<figure.*<img.*?src="(.*?)".*?<figcaption.*?>(.*?)<.*', r'![\2](\1)', entry_content)
    entry_content = re.sub(r'<figure.*<img.*?src="(.*?)".*', r'![](\1)', entry_content)
    
    #download all images
    all_images = re.findall(r'\!\[.*?\]\((.+)\)', entry_content)
    download_images(all_images)
    
    #change path of images to local:
    entry_content = re.sub(r'\!\[(.*?)\]\((.+\/)(.+)\)', r'![\1](img/\3)', entry_content)
    
    #tables
    entry_content = re.sub(r'<!-- wp:table -->.*?<table>(.*?)</table>.*?<!-- /wp:table -->', table_to_markdown, entry_content, flags=re.DOTALL)

    entry_content = metadata_string + entry_content
    write_md_to_file(entry_filename, entry_content)

    print(entry_content)



