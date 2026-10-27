from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import json

from book_prep import sort_links_json, create_epub
from eros.eros.spiders.literoticafetch import ExtractPageLiterotica
from eros.eros.spiders.ficbookfetch import ExtractPageFicbook

# установка настроек
def set_settings(settings_json=None):
    # в случае отсутствия кастомных настроек, фолбэк на настройки по умолчанию
    if not settings_json:
        settings_json = "./settings/default_settings.json"
    
    with open(settings_json,'r', encoding='utf-8') as f:
        settings_json = json.load(f)

    settings = get_project_settings()

    settings['FEEDS'] = {
        './eros/response.json': {
            'format': 'json',
            'overwrite': True,
            }
    }
    settings.set('USER_AGENT', settings_json['USER_AGENT'], priority='cmdline')
    settings.set('AUTOTHROTTLE_ENABLED', settings_json['AUTOTHROTTLE_ENABLED'])
    settings.set('AUTOTHROTTLE_START_DELAY', settings_json['AUTOTHROTTLE_START_DELAY'])
    settings.set('AUTOTHROTTLE_MAX_DELAY', settings_json['AUTOTHROTTLE_MAX_DELAY'])
    settings.set('AUTOTHROTTLE_TARGET_CONCURRENCY', settings_json['AUTOTHROTTLE_TARGET_CONCURRENCY'])
    settings.set('CONCURRENT_REQUESTS_PER_DOMAIN', settings_json['CONCURRENT_REQUESTS_PER_DOMAIN'])
    settings.set('DOWNLOAD_DELAY', settings_json['DOWNLOAD_DELAY'])
    settings.set('RETRY_HTTP_CODES', settings_json['RETRY_HTTP_CODES'])

    return settings
    


def run_spider(user_url,  settings_json=None):
    crawler_settings = set_settings(settings_json)
    process = CrawlerProcess(settings=crawler_settings)

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