#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/2 21:29
# @Author  : zxy
# @File    : bloomberg.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 17:35
# @Author  : zxy
# @File    : 中国日报网.py
import time
from datetime import datetime
import json
import re

import scrapy
from pybloom_live import ScalableBloomFilter
from scrapy import signals
from selenium import webdriver
from ..items import text_Item
from selenium.webdriver import EdgeOptions


class bloomBergSpider(scrapy.Spider):
    name = 'bloomberg'
    allowed_domains = ['https://www.bloomberg.com/']

    # start_urls = ['https://www.bbc.co.uk/search?q=china+covid+virus&d=news_gnl']

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.key_words = text
        self.bloom = ScalableBloomFilter(initial_capacity=100, error_rate=0.001)

    @classmethod
    def from_crawler(cls, crawler, text=None, *args, **kwargs):
        spider = super(bloomBergSpider, cls).from_crawler(crawler, text, *args, **kwargs)
        spider.key_words = text
        # print(key_words)
        option = EdgeOptions()
        option.headless = False
        spider.driver = webdriver.Edge(options=option)
        spider.name = 'bloomberg'
        # crawler.signals.connect(spider.start_requests, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
        return spider

    # 动态生成初始 URL
    def start_requests(self):
        print(self.key_words)
        self.list = self.key_words.split()
        if len(self.list) == 1:
            self.start_url = 'https://www.bloomberg.com/markets2/api/search?query=%s&page=0&sort=relevance' % self.list[0]  # 通过关键词拼接url
            self.model = 'https://www.bloomberg.com/markets2/api/search?query=%s&page={}&sort=relevance' % self.list[0]
            yield scrapy.Request(url=self.start_url, callback=self.parse)
        else:
            self.url = self.list[0]
            for i in self.list[1:]:
                self.url = self.url + '%20' + i
            self.start_url = 'https://www.bloomberg.com/markets2/api/search?query=%s&page=0&sort=relevance' % self.url
            self.model = 'https://www.bloomberg.com/markets2/api/search?query=%s&page={}&sort=relevance' % self.url
            yield scrapy.Request(url=self.start_url, callback=self.parse)

    def spider_closed(self, spider):
        spider.driver.quit()
        print("爬虫结束了")
        print('*' * 60)

    # 数据解析
    def parse(self, response):
        try:
            self.result_text = response.xpath(
                '/html/body/pre').xpath('string(.)').extract()[0]# 获取页面所有json数据
            pages=int(json.loads(self.result_text)['total'])/10
            if pages>1000:
                pages=1000
            urls = []
            for i in range(1,pages):
                url = self.model.format(i)
                urls.append(url)
            for url in urls:
                time.sleep(3)
                yield scrapy.Request(url=url, callback=self.sub_parse, dont_filter=True)
        except:
            print('页面出现错误')


    def sub_parse(self, response):
        articles = json.loads(self.result_text)['results']
        for i in articles:
            item = text_Item()
            item["title"]=i['headline']
            item['herf']=i['url']
            item['content']=i['summary']
            item['brief']=i['summary'][0:50]
            item['publish_date']=i['publishedAt']
            item['key_words'] = self.key_words
            # yield scrapy.Request(
            #     item['herf'],
            #     callback=self.parse_detail,
            #     meta={"item": item},
            #     dont_filter=True
            # )
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

            yield item




