import requests
import tkinter
import webbrowser
import threading
from bs4 import BeautifulSoup

def open_url(url):
    webbrowser.open_new(url)

def get_html(url):
    try:
        response = requests.get(url)
        return BeautifulSoup(response.text, 'html.parser')
       
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

def get_body_links(parsedHTML, amount):
    article = parsedHTML.find('div', id='mw-content-text')
    links = article.find_all('a', href=True)

    relevant_links = []
    for link in links:
        reference = link['href']
        if reference.startswith('/wiki/') and not reference.startswith('/wiki/Help:') and not find_blacklisted_parents(link):
            relevant_links.append(handle_relative_url(reference))
            if len(relevant_links) == amount:
                return relevant_links

    return relevant_links

def handle_relative_url(url):
    if not url.startswith('http'):
        return "https://en.wikipedia.org" + url
    return url

def find_blacklisted_parents(element, 
blacklisted_classes = ('infobox', 'vcard', 'reflist', 'hatnote', 'navigation-not-searchable', 'mw-content-subtitle', 'mw-file-description', 'metadata', 'ombox', 'sidebar', 'navbox'),
blacklisted_tags = ('i', 'figure')):
    
    if element.has_attr('class') and any(cls in blacklisted_classes for cls in element['class']):
        return True
    
    if element.name in blacklisted_tags:
        return True

    if element.parent:
        return find_blacklisted_parents(element.parent)
    return False

def url_for_display(text):
    title = text.split("/wiki/")[-1]
    return " ".join(title.split("_"))

def game(url, output, nth_link, link_input, pages):
    print(url)
    
    output.tag_config(f"{url}", foreground="blue", underline=True)
    output.tag_bind(f"{url}", "<Button-1>", lambda _: open_url(url))
    output.insert(tkinter.END, url_for_display(url) + '\n', (f"{url}",))
    output.update_idletasks()

    if url not in pages:
        pages.append(url)

        try:
            result = get_body_links(get_html(url), nth_link)
            if len(result) >= nth_link:
                print(result)
                game(result[nth_link -1], output, nth_link, link_input, pages)
            else:
                output.insert(tkinter.END, f'\nNOT ENOUGH LINKS TO FOLLOW!\nPAGES TRAVELLED: {len(pages)}')

        except Exception as e:
            output.insert(tkinter.END, f'\nError: {str(e)}')
    else:
        output.insert(tkinter.END, f'\nLOOP ENCOUNTERED!\nPAGES TRAVELLED: {len(pages)}')
    
    link_input.config(state=tkinter.NORMAL)

def init_game(url, output, nth_input, link_input):
    if not url: return
    output.delete(1.0, tkinter.END)
    link_input.delete(0, tkinter.END)
    link_input.config(state=tkinter.DISABLED)

    nth_link = nth_input.get()
    if nth_link.isdigit():
        nth_link = int(nth_link)
        if nth_link <= 0:
            nth_link = 8
    else:
        nth_link = 8

    thread = threading.Thread(target=game, args=(url, output, nth_link, link_input, []))
    thread.start()

def main():
    root = tkinter.Tk()
    root.title("Wikipedia Game")
    root.geometry("700x700")
    root.resizable(False, False)
    root.iconbitmap("root.ico")

    # Output
    scrollbar = tkinter.Scrollbar(root)
    scrollbar.pack(side='right', fill='y')
    text_output = tkinter.Text(root,  yscrollcommand = scrollbar.set, height=25)
    text_output.pack(side='top', fill='x', pady= 10)

    # Input field for wikipedia link
    link_label = tkinter.Label(root, text="STARTING WIKIPEDIA URL")
    link_label.pack()
    link_input = tkinter.Entry(root, width=40)
    link_input.pack()

    # Link position
    pos_label = tkinter.Label(root, text="FOLLOW NTH LINK IN PAGE (DEFAULT: 8TH)")
    pos_label.pack()
    nth_pos_input = tkinter.Spinbox(root, from_=0, to=float('inf'), increment=1, width=5)
    nth_pos_input.pack(pady=5)

    # Button for submitting link
    button = tkinter.Button(root, text="Start Game", command=lambda: init_game(link_input.get(), text_output, nth_pos_input, link_input))
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
