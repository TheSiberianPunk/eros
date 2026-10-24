import scrapy
from parsel import Selector

class ExtractPageFicbook(scrapy.Spider):
    name = "crawl_ficbook"

    #start_urls = ["https://ficbook.net/readfic/019e704d-a680-76c8-a0e4-9b539f509b52"]

    def __init__(self, start_url=None, *args, **kwargs):
        super(ExtractPageFicbook, self).__init__(*args, **kwargs)
            
        self.start_urls = [start_url] 

    # парсим главы из основной страницы
    def parse(self, response):
        chapter_links = response.css("ul.list-of-fanfic-parts a.part-link ::attr(href)").getall()
        for link in chapter_links:
            if "/assets/" not in link: # обход собранных спрайтов кнопок
                yield response.follow(f'https://ficbook.net{link}', callback=self.parse_chapter)

    # парсим одну главу
    def parse_chapter(self, response):
        title = response.css("h2 ::text").get()
        content = response.css("article div#content").get()

        content = self.add_breaks(content)

        yield {
            "url": response.url,
            "status": response.status,
            "title": title,
            "content": self.clean_promo(content)
        }

    # читаемые переносы строк
    def add_breaks(self, text):
        text = text.replace('\r\n', '\n').replace('\n', '<br/>')
        return text

    # убрать промо страницы
    def clean_promo(self, raw):
        if not raw:
            return ''
        sel = Selector(text=raw)

        for el in sel.xpath("//div[contains(@class, 'fanfic-text-promo')]"):
            parent = el.root.getparent()
            if parent is not None:
                parent.remove(el.root)

        return ''.join(
                    child.get() for child in sel.xpath('./*')
                )