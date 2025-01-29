import requests
import tkinter
import webbrowser
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
blacklisted_classes = ('infobox', 'vcard', 'reflist', 'hatnote', 'navigation-not-searchable', 'mw-content-subtitle', 'mw-file-description', 'metadata', 'ombox', 'sidebar'),
blacklisted_tags = ('i', 'figure')):
    
    if element.has_attr('class') and any(cls in blacklisted_classes for cls in element['class']):
        return True
    
    if element.name in blacklisted_tags:
        return True

    if element.parent:
        return find_blacklisted_parents(element.parent)
    return False

def game(url : str, output: tkinter.Frame, next_link_pos = 8, pages = []):
    print(url)

    link_label = tkinter.Label(output, text=url.split("/wiki/")[1])
    link_label.bind("<Button-1>", lambda e: open_url(url))
    link_label.pack(side="top", fill="x")
    output.update_idletasks()

    if url not in pages:
        pages.append(url)

        try:
            result = get_body_links(get_html(url), next_link_pos)
            if len(result) >= next_link_pos:
                game(result[next_link_pos -1], output, pages=pages)

        except Exception as e:
            print((e))


def main():
    root = tkinter.Tk()
    root.title("Wikipedia Game")
    root.geometry("500x700")
    root.resizable(False, False)

    frame = tkinter.Frame(root)
    frame.pack(side="bottom", fill="x")

    output_box = tkinter.Canvas(root, bg="#000000", height=550)
    scrollbar = tkinter.Scrollbar(root, orient="vertical", command=output_box.yview)
    output_box.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = tkinter.Frame(output_box, bg="#000000", width=output_box.winfo_width())
    output_box.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        output_box.configure(scrollregion=output_box.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)

    scrollbar.pack(side="right", fill="y")
    output_box.pack(side="left", fill="both", expand=True)

    link_input = tkinter.Entry(frame, width=40)
    link_input.pack(pady=0)

    button = tkinter.Button(frame, text="Start Game", command=lambda: game(link_input.get(), scrollable_frame))
    button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
