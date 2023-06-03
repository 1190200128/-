import re

import scrapy
from scrapy import signals
from selenium import webdriver
from ..items import text_Item
from selenium.webdriver import EdgeOptions


class FOXNEWSSpider(scrapy.Spider):
    name = 'foxnews'
    allowed_domains = ['https://www.foxnews.com/']
    # start_urls = ['https://www.cbc.ca/search?q=china%20covid%20virus&section=news']

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.key_words = text

    @classmethod
    def from_crawler(cls, crawler, text=None, *args, **kwargs):
        spider = super(FOXNEWSSpider, cls).from_crawler(crawler, text, *args, **kwargs)
        spider.key_words = text
        option = EdgeOptions()
        option.headless = False
        spider.driver = webdriver.Edge(options=option)
        spider.name = 'foxnews'
        list = text.split()
        if len(list) == 1:
            spider.start_url = 'https://www.foxnews.com/search-results/search?q=%s' % list[0]  # 通过关键词拼接url
        else:
            start_url = list[0]
            for i in list[1:]:
                start_url = start_url + '%20' + i
            spider.start_url = 'https://www.foxnews.com/search-results/search?q=%s' % start_url
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
        return spider

    def start_requests(self):
        self.list = self.key_words.split()
        if len(self.list) == 1:
            start_url = 'https://www.foxnews.com/search-results/search?q=%s' % self.list[0]  # 通过关键词拼接url
            yield scrapy.Request(url=start_url, callback=self.parse)
        else:
            start_url = self.list[0]
            for i in self.list[1:]:
                start_url = start_url + '%20' + i
            start_url = 'https://www.foxnews.com/search-results/search?q=%s' % start_url
            yield scrapy.Request(url=start_url, callback=self.parse)

    def spider_closed(self, spider):
        spider.driver.quit()
        print("爬虫结束了")
        print('*' * 59)

    # 数据解析
    def parse(self, response):
        try:
            tr_list = response.xpath("//*[@id='wrapper']/div[2]/div[2]/div/div[3]/div[1]/article")  # 获取每一个新闻所在板块
            for tr in tr_list:
                item = text_Item()
                href = tr.xpath("./div[1]/a/@href").extract_first()

                item["title"] = tr.xpath("./div[2]/header/h2/a/text()").extract_first()
                item["brief"] = tr.xpath("./div[2]/div/p/a/text()").extract_first()
                item['herf'] = href
                if 'video' in item['herf']:
                    continue
                item['publish_date'] = tr.xpath(
                    "./div[2]/header/div/span[2]").xpath('string(.)').extract_first()
                item['key_words'] = self.key_words  # 关键词# 对要爬取的内容做一个简单的筛选
                # 对要爬取的内容做一个简单的筛选
                count1 = 0
                for i in self.list:
                    if re.search(i, item["title"]) is None and re.search(i, item["brief"]) is None:
                        count1 = count1 + 1
                count2 = 0
                for i in self.list:
                    demo = i.upper()
                    if re.search(demo, item["title"]) is None and re.search(demo, item["brief"]) is None:
                        count2 = count2 + 1
                count3 = 0
                for i in self.list:
                    demo = i.capitalize()
                    if re.search(demo, item["title"]) is None and re.search(demo, item["brief"]) is None:
                        count3 = count3 + 1
                if count1 == len(self.list) and count2 == len(self.list) and count3 == len(self.list):
                    continue
                else:
                    yield scrapy.Request(
                        item['herf'],
                        callback=self.parse_detail,
                        meta={"item": item},
                        dont_filter=True
                    )
        except Exception as e:
            print('出现错误：',e)

    def parse_detail(self, response):
        item = response.meta['item']
        desc_info = response.xpath("//*[@id='wrapper']//main//p").xpath('string(.)').extract()
        # desc_ = desc_info.xpath('string(.)').extract()
        desc = ""
        for description in desc_info:
            description_ = description.strip()
            desc = desc + description_
        # item['content'] = "".join(item["content"])
        item['content'] = desc
        print(item)
        # print('结果是'+item)
        yield (item)
