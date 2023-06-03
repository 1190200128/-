# import re
#
# import scrapy
# from scrapy import signals
# from selenium import webdriver
# from ..items import text_Item
# from selenium.webdriver import EdgeOptions
#
#
# class CbcSpider(scrapy.Spider):
#     name = 'cbc'
#     allowed_domains = ['https://www.cbc.ca/']
#     # start_urls = ['https://www.cbc.ca/search?q=china%20covid%20virus&section=news']
#
#     def __init__(self, text, **kwargs):
#         super().__init__(**kwargs)
#         self.key_words = text
#
#     @classmethod
#     def from_crawler(cls, crawler, text=None, *args, **kwargs):
#         spider = super(CbcSpider, cls).from_crawler(crawler, text, *args, **kwargs)
#         spider.key_words = text
#         option = EdgeOptions()
#         option.headless = False
#         spider.driver = webdriver.Edge(options=option)
#         spider.name = 'cbc'
#         list = text.split()
#         if len(list) == 1:
#             spider.start_url = 'https://www.cbc.ca/search?q=%s&section=news' % list[0]  # 通过关键词拼接url
#         else:
#             start_url = list[0]
#             for i in list[1:]:
#                 start_url = start_url + '%20' + i
#             spider.start_url = 'https://www.cbc.ca/search?q=%s&section=news' % start_url
#         crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
#         return spider
#
#     def start_requests(self):
#         print(self.key_words)
#         self.list = self.key_words.split()
#         if len(self.list) == 1:
#             start_url = 'https://www.cbc.ca/search?q=%s&section=news' % self.list[0]  # 通过关键词拼接url
#             yield scrapy.Request(url=start_url, callback=self.parse)
#         else:
#             start_url = self.list[0]
#             for i in self.list[1:]:
#                 print(i)
#                 start_url = start_url + '%20' + i
#             start_url = 'https://www.cbc.ca/search?q=%s&section=news' % start_url
#             yield scrapy.Request(url=start_url, callback=self.parse)
#
#     def spider_closed(self, spider):
#         spider.driver.quit()
#         print("爬虫结束了")
#         print('*' * 60)
#
#     # 数据解析
#     def parse(self, response):
#         tr_list = response.xpath("//div[@class='contentListCards']/a")  # 获取每一个新闻所在板块
#         # i=0
#         # tr = tr_list[2]
#         for tr in tr_list:
#             item = text_Item()
#             href = tr.xpath("./@href").extract_first()
#             time = tr.xpath(
#                 "./div/div/div[@class='card-content-bottom']/div/div/time/@datetime").extract_first()
#             year = time[:4]
#             month = time[5:7]
#             print(year, month)
#             if int(month) >= 1 and int(year) >= 2019 and href[1:5] == 'news':
#                 # print('111111')
#                 # print(i-1)
#                 item["title"] = tr.xpath("./div/div/div[@class='card-content-top']/h3/text()").extract_first()
#                 # print('结果是1' + item["title"])
#                 item["brief"] = tr.xpath(
#                     "./div/div/div[@class='card-content-top']/div[@id='d-card-']/text()").extract_first()
#                 # print('结果是2' + item["brief"])
#                 item['herf'] = 'https://www.cbc.ca' + href
#                 # print('结果是3' + item['herf'])
#                 item['publish_date'] = tr.xpath(
#                     "./div/div/div[@class='card-content-bottom']/div/div/time/@datetime").extract_first()
#                 # print('结果是4' + item['publish_date'])
#                 item['key_words'] = self.key_words  # 关键词# 对要爬取的内容做一个简单的筛选
#                 # 对要爬取的内容做一个简单的筛选
#                 count1 = 0
#                 for i in self.list:
#                     if re.search(i, item["title"]) is None and re.search(i, item["brief"]) is None:
#                         count1 = count1 + 1
#                 count2 = 0
#                 for i in self.list:
#                     demo = i.upper()
#                     if re.search(demo, item["title"]) is None and re.search(demo, item["brief"]) is None:
#                         count2 = count2 + 1
#                 count3 = 0
#                 for i in self.list:
#                     demo = i.capitalize()
#                     if re.search(demo, item["title"]) is None and re.search(demo, item["brief"]) is None:
#                         count3 = count3 + 1
#                 if count1 == len(self.list) and count2 == len(self.list) and count3 == len(self.list):
#                     continue
#
#                 # if re.search(r'[Cc]ovid', item["title"]) is None and re.search(r'COVID',
#                 #                                                                item["title"]) is None and re.search(
#                 #         r'virus', item["title"]) is None \
#                 #         and re.search(r'[Cc]ovid', item["brief"]) is None and re.search(r'COVID', item[
#                 #     "brief"]) is None and re.search(r'virus', item["brief"]) is None:
#                 #     continue
#                 else:
#                     yield scrapy.Request(
#                         item['herf'],
#                         callback=self.parse_detail,
#                         meta={"item": item},
#                         dont_filter=True
#                     )
#
#     def parse_detail(self, response):
#         item = response.meta['item']
#         desc_info = response.xpath(
#             "//*[@id='detailContent']/div[@class='storyWrapper']/div[@class='story']/p/text()").extract()
#         # desc_ = desc_info.xpath('string(.)').extract()
#         desc = ""
#         for description in desc_info:
#             description_ = description.strip()
#             desc = desc + description_
#         # item['content'] = "".join(item["content"])
#         print(desc)
#         item['content'] = desc
#         # print('结果是'+item)
#         yield (item)
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/2 21:29
# @Author  : zxy
# @File    : bloomberg.py
# !/usr/bin/env python
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


class cbcSpider(scrapy.Spider):
    name = 'cbc'
    allowed_domains = ['https://www.bloomberg.com/']

    # start_urls = ['https://www.bbc.co.uk/search?q=china+covid+virus&d=news_gnl']

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.key_words = text
        self.bloom = ScalableBloomFilter(initial_capacity=100, error_rate=0.001)

    @classmethod
    def from_crawler(cls, crawler, text=None, *args, **kwargs):
        spider = super(cbcSpider, cls).from_crawler(crawler, text, *args, **kwargs)
        spider.key_words = text
        option = EdgeOptions()
        option.headless = False
        spider.driver = webdriver.Edge(options=option)
        spider.name = 'cbc'
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
        return spider

    # 动态生成初始 URL
    def start_requests(self):
        print(self.key_words)
        self.list = self.key_words.split()
        if len(self.list) == 1:
            self.start_url = 'https://www.cbc.ca/search?q=%s&section=all&sortOrder=relevance&media=all' % self.list[0]  # 通过关键词拼接url
            self.model = 'https://www.cbc.ca/search_api/v1/search?q=%s&sortOrder=relevance&media=all&boost-cbc-keywords=7&boost-cbc-keywordscollections=7&boost-cbc-keywordslocation=4&boost-cbc-keywordsorganization=3&boost-cbc-keywordsperson=5&boost-cbc-keywordssubject=7&boost-cbc-publishedtime=30&page={}&fields=feed' % self.list[0]
            yield scrapy.Request(url=self.start_url, callback=self.parse)
        else:
            self.url = self.list[0]
            for i in self.list[1:]:
                self.url = self.url + '%20' + i
            self.start_url = 'https://www.cbc.ca/search?q=%s&section=all&sortOrder=relevance&media=all' % self.url
            self.model = 'https://www.cbc.ca/search_api/v1/search?q=%s&sortOrder=relevance&media=all&boost-cbc-keywords=7&boost-cbc-keywordscollections=7&boost-cbc-keywordslocation=4&boost-cbc-keywordsorganization=3&boost-cbc-keywordsperson=5&boost-cbc-keywordssubject=7&boost-cbc-publishedtime=30&page={}&fields=feed' % self.url
            yield scrapy.Request(url=self.start_url, callback=self.parse)

    def spider_closed(self, spider):
        spider.driver.quit()
        print("爬虫结束了")
        print('*' * 60)

    # 数据解析
    def parse(self, response):
        try:
            self.result_text = response.xpath(
                '//*[@id="content"]//h2/strong[2]/text()').extract_first()  # 获取总的结果数目
            print(self.result_text)
            pages = int(self.result_text) / 10
            if pages > 1000:
                pages = 1000
            else:
                pages=int(pages)
            urls = []
            for i in range(2, pages):
                url = self.model.format(i)
                urls.append(url)
            for url in urls:
                time.sleep(3)
                yield scrapy.Request(url=url, callback=self.sub_parse, dont_filter=True)
        except:
            print('页面出现错误')

    def sub_parse(self, response):
        articles = json.loads(response.xpath(
                '/html/body/pre').xpath('string(.)').extract()[0])# 获取页面所有json数据)
        for i in articles:
            item = text_Item()
            item["title"] = i['title']
            item['herf'] = 'https://'+i['url']
            item['brief'] = i['description']
            item['publish_date'] = i['publishtime']
            item['key_words'] = self.key_words
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

            yield scrapy.Request(
                item['herf'],
                callback=self.parse_detail,
                meta={"item": item},
                dont_filter=True
            )

    def parse_detail(self, response):
        item = response.meta['item']
        desc_info = response.xpath(
            "//*[@id='detailContent']/div[@class='storyWrapper']/div[@class='story']/p/text()").extract()
        desc = ""
        for description in desc_info:
            description_ = description.strip()
            desc = desc + description_
        # item['content'] = "".join(item["content"])
        print(desc)
        item['content'] = desc
        # print('结果是'+item)
        yield (item)


