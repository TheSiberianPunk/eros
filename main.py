from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from book_prep import sort_links_json, create_epub
from eros.eros.spiders.literoticafetch import ExtractPageLiterotica
from eros.eros.spiders.ficbookfetch import ExtractPageFicbook

def run_spider(user_url):
    settings = get_project_settings()
    settings['FEEDS'] = {
    './eros/response.json': {
        'format': 'json',
        'overwrite': True,
        }
    }
    settings.set('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0', priority='cmdline')
    settings.set('AUTOTHROTTLE_ENABLED', True)
    settings.set('AUTOTHROTTLE_START_DELAY', 5)
    settings.set('AUTOTHROTTLE_MAX_DELAY', 60)
    settings.set('AUTOTHROTTLE_TARGET_CONCURRENCY', 1.0)
    settings.set('CONCURRENT_REQUESTS_PER_DOMAIN', 1)
    settings.set('DOWNLOAD_DELAY', 5)
    settings.set('RETRY_HTTP_CODES', [429])
    process = CrawlerProcess(settings=settings)

    try:
        if "literotica" in user_url:
            process.crawl(ExtractPageLiterotica, start_url=user_url)
        elif "ficbook" in user_url:
            process.crawl(ExtractPageFicbook, start_url=user_url)

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