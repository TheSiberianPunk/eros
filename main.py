from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from book_prep import sort_links_json, create_epub
from eros.eros.spiders.literoticafetch import ExtractPageLiterotica
from eros.eros.spiders.ficbookfetch import ExtractPageFicbook

def run_spider(user_url):
    settings = get_project_settings()
    settings['FEEDS'] = {
    '/eros/response.json': {
        'format': 'json',
        'overwrite': True,
    }
}
    process = CrawlerProcess(settings=settings)
    
    try:
        if "literotica" in user_url:
            process.crawl(ExtractPageLiterotica)
        elif "ficbook" in user_url:
            process.crawl(ExtractPageFicbook)

        process.start()
    except Exception as e:
        raise Exception("Ошибка парсинга. Убедитесь, в правильности введенной ссылки.  {e}")
    

if __name__ == "__main__":
    url = input("Введите ссылку для парсинга => ").strip()
    storyname = input("Введите название истории => ")
    storyauthor = input("Введите имя автора => ")

    run_spider(url)
    
    sort_links_json('eros/response.json')
    create_epub(storyname, storyauthor, "sorted.json")