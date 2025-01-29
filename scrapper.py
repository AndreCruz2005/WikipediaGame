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
        if reference.startswith('/wiki/') and not reference.startswith('/wiki/Help:') and not find_blacklisted_parents(link):
            relevant_links.append(handle_relative_url(reference))

    return relevant_links

def handle_relative_url(url):
    if not url.startswith('http'):
        return "https://en.wikipedia.org" + url
    return url

def find_blacklisted_parents(element, 
blacklisted_classes = ('infobox', 'vcard', 'reflist', 'hatnote', 'navigation-not-searchable', 'mw-content-subtitle', 'mw-file-description', 'metadata', 'ombox', 'sidebar'),
blacklisted_tags = ('i')):
    
    if element.has_attr('class') and any(cls in blacklisted_classes for cls in element['class']):
        return True
    
    if element.name in blacklisted_tags:
        return True

    if element.parent:
        return find_blacklisted_parents(element.parent)
    return False

def game(url : str, pages : list, text: tkinter.Text, next_link_pos = 8):
    print(url)
    if url in pages:
        return
    pages.append(url)

    text.insert(tkinter.END, url + '\n')

    try:
        result = get_all_article_links(get_html(url))
    except Exception as e:
        print((e))
        return

    if len(result) >= next_link_pos:
        game(result[next_link_pos -1], pages, text, next_link_pos)

def main():
    root = tkinter.Tk()
    root.title("Wikipedia Game")
    root.geometry("500x700")
    root.resizable(False, False)

    frame = tkinter.Frame(root)
    frame.pack(side="bottom", fill="x")

    output_box = tkinter.Text(root, yscrollcommand=True, xscrollcommand=True)
    output_box.pack(side="top", fill="x")

    link_input = tkinter.Entry(frame, width=40)
    link_input.pack(pady=0)

    results = []
    button = tkinter.Button(frame, text="Start Game", command=lambda: game(link_input.get(), results, output_box))
    button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
