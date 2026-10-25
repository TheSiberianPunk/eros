import scrapy
from parsel import Selector

class ExtractPageLiterotica(scrapy.Spider):
    name = "crawl_literotica"

    #start_urls = ['https://www.literotica.com/s/the-pleasures-of-hell-01-001']

    def __init__(self, start_url=None, *args, **kwargs):
        super(ExtractPageLiterotica, self).__init__(*args, **kwargs)
        
        self.start_urls = [start_url]

        return self.start_urls

    # точка входа: проверяем является ли это серией. если да то парсим ссылку на серию и парсим каждую ссылку там
    def parse(self, response):
        link_to_series = response.css("body header p a::attr(href)").getall()
        try:
            link_to_series = link_to_series[-1]
            yield response.follow(link_to_series, callback=self.parse_series)
        except:
            yield from self.parse_story(response)

    # в случае обнаруженной серии парсим каждую главу в серии
    def parse_series(self, response):
        print("Parsing as series")
        story_links = response.css("section ul li a::attr(href)").getall()

        for link in story_links:
            yield response.follow(link, callback=self.parse_story)

    # парс одной главы/рассказа
    def parse_story(self, response):
        # получаем текст одной страницы
        text = response.css('body div.panel.article[class *= "_article_"]').get() # ::text
        title = response.css('article h1 ::text').get()
        
        # добавляем текст
        #big_text = '\n'.join(text)
        
        yield {
                'url': response.url,
                'status': response.status,
                'title': title,
                'content': self.clean_article(text)
                }
            
        # follow pages
        for href in response.css('nav[class *= "_pages_"] a::attr(href)').getall():
            print(href)
            yield response.follow(href, callback=self.parse_story)

    # очистка от кнопок report
    def clean_article(self, raw):
        if not raw:
            return ""
        sel = Selector(text=raw)

        for el in sel.xpath('.//*[contains(@class, "_report_")]'):
            el.root.getparent().remove(el.root)
            
        return ''.join(
            child.get() for child in sel.xpath('./*')
        )
    

        