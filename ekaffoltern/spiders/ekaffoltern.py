import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from ekaffoltern.items import Article


class EkaffolternSpider(scrapy.Spider):
    name = 'ekaffoltern'
    start_urls = ['https://www.ekaffoltern.ch/de/aktuelles/']

    def parse(self, response):
        links = response.xpath('//h2[@class="listEntryTitle"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="pageNaviNextLink"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="subline"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="elementStandard elementContent elementText elementText_var0"]'
                                 '//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
