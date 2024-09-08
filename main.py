import feedparser
import re

with open('rss_file.xml', 'r') as file:
    file_content = file.read()

feed = feedparser.parse(file_content)

for entry in feed.entries:
    
    print(entry.title)

    entry_content = str(entry.content[0].value)
    #clean paragraphs
    entry_content = entry_content.replace('<!-- wp:paragraph -->', '')
    entry_content = entry_content.replace('<!-- /wp:paragraph -->', '')
    entry_content = entry_content.replace('</p>', '')
    entry_content = entry_content.replace('<p>', '')

    # fix numbered lists
    entry_content = re.sub(r'(\n)(\.)(\d\.)', r'\1\3', entry_content)


    #convert lists
    entry_content = entry_content.replace('<li>', '- ')
    entry_content = entry_content.replace('</li>', '')
    entry_content = entry_content.replace('<!-- wp:list-item -->', '')
    entry_content = entry_content.replace('<!-- /wp:list-item -->', '')
    entry_content = re.sub('<!-- wp:list .* -->', '', entry_content)
    entry_content = re.sub('<!-- /wp:list -->', '', entry_content)

    entry_content = re.sub('<ol.*>', '', entry_content)
    entry_content = re.sub('</ol>', '', entry_content)
    entry_content = re.sub(r'((?:- |\d*\. ).*)([\n]{4})((?:-|\d*\.))', r'\1\n\3', entry_content)

    # headings
    heading_replacement = lambda m: '#' * int(m.group('h')) + ' ' + m.group('title')
    entry_content = re.sub('<!-- wp:heading.*\n<h(?P<h>\d).*?>(?P<title>.*?)<.*\n<!-- /wp:heading -->', heading_replacement, entry_content)


    # images
    

    print(entry_content)



