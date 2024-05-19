import os
import sys

import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

scrapy.utils.reactor.install_reactor(
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
)
from twisted.internet import reactor

sys.path.append(os.path.join(os.path.abspath("../")))
from crawler.spiders.promotion_spider import PromotionSpider


def spider_ended(spider, reason):
    print("Spider ended:", spider.name, reason)


def run_crawl():
    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
    settings = get_project_settings()
    runner = CrawlerRunner(settings=settings)

    deferred = runner.crawl(
        PromotionSpider, start_urls="https://vnptpay.vn/web/khuyenmai"
    )
    half_day = 12 * 60 * 60
    deferred.addCallback(lambda _: reactor.callLater(half_day, run_crawl))

    for crawler in runner.crawlers:
        crawler.signals.connect(spider_ended, signal=scrapy.signals.spider_closed)

    return deferred


if __name__ == "__main__":
    run_crawl()
    reactor.run()
