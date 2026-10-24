from ebooklib import epub
from natsort import natsorted
import uuid
import json

# сортировка json по ссылкам к главе/истории. использует natsort
def sort_links_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sorted_data = natsorted(data, key=lambda page: page['url'])

    with open("sorted.json", 'w') as f:
        json.dump(sorted_data, f, indent=2)

    return sorted_data

def create_epub(story_title, author, scraped_json):
    id = uuid.uuid4()
    book = epub.EpubBook()

    book.set_identifier(f"scraped-book-{id}")
    book.set_title(story_title)
    book.add_author(author)
    chapters = []

    with open(scraped_json, 'r', encoding='utf-8') as f:
        scraped_json = json.load(f)

    last_title = None

    for idx, item in enumerate(scraped_json, start=1):
        if item['content'] == "":
            continue
        
        title = item['title']

        ch = epub.EpubHtml(
            title=f'{title}. {idx}',
            file_name=f'page_{idx:03d}.xhtml'
        )

        content = item.get('content', '')
        if isinstance(content, list):
            content = ''.join(content)
        content = content.strip()

        ch.content = f'<html><body><h1>{title}</h1><h3>Page {idx}</h3>{content}</body></html>'
        book.add_item(ch)
        chapters.append(ch)


    book.toc = tuple(
        epub.Link(ch.file_name, ch.title, ch.id) for ch in chapters
    )
    book.spine = ['nav'] + chapters

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(f'{story_title} story-{id}.epub', book)
    return f"book created with {len(chapters)} chapters"
