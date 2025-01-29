import requests
import tkinter
from bs4 import BeautifulSoup

def get_html(url):
    try:
        response = requests.get(url)
        return BeautifulSoup(response.text, 'html.parser')
       
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

def get_all_article_links(parsedHTML):
    article = parsedHTML.find('div', id='mw-content-text')
    links = article.find_all('a', href=True)

    relevant_links = []
    for link in links:
        reference = link['href']
        if reference.startswith('/wiki/') and not find_blacklisted_parents(link) :
            relevant_links.append(handle_relative_url(reference))

    return relevant_links

def handle_relative_url(url):
    if not url.startswith('http'):
        return "https://en.wikipedia.org/" + url
    return url

def find_blacklisted_parents(element, 
blacklisted_classes = ('infobox', 'vcard', 'reflist', 'hatnote', 'navigation-not-searchable', 'mw-content-subtitle', 'mw-file-description', 'metadata', 'ombox'),
blacklisted_tags = ('i')):
    
    if element.has_attr('class') and any(cls in blacklisted_classes for cls in element['class']):
        return True
    
    if element.name in blacklisted_tags:
        return True

    if element.parent:
        return find_blacklisted_parents(element.parent)
    return False

def game(url : str, pages : list):
    print(url)
    if url in pages:
        return
    
    pages.append(url)

    try:
        result = get_all_article_links(get_html(url))
    except Exception as e:
        print((e))
        return

    if len(result) >= 5:
        game(result[4], pages)

def main():
    starting_page = input()
    visited_pages = []
    game(starting_page, visited_pages)


if __name__ == "__main__":
    main()