#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 15:49
# @Author  : zxy
# @File    : 搜狐网.py
import os
import re
import time

import requests
from pybloom_live import ScalableBloomFilter, BloomFilter
import scrapy
from scrapy import signals
from selenium import webdriver
from ..items import text_Item
from selenium.webdriver import EdgeOptions


class souHuSpider(scrapy.Spider):
    name = 'souhuwang'
    allowed_domains = ['http://news.sohu.com/']

    # start_urls = ['https://www.cbc.ca/search?q=china%20covid%20virus&section=news']

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.key_words = text
        # 可自动扩容的布隆过滤器
        self.bloom = ScalableBloomFilter(initial_capacity=100, error_rate=0.001)
        self.name = '搜狐网'
        self.time_start = time.time()

    @classmethod
    def from_crawler(cls, crawler, text=None, *args, **kwargs):
        spider = super(souHuSpider, cls).from_crawler(crawler, text, *args, **kwargs)
        spider.key_words = text
        option = EdgeOptions()
        option.headless = False
        spider.driver = webdriver.Edge(options=option)
        spider.name = 'souhuwang'
        list = text.split()
        if len(list) == 1:
            spider.start_url = 'https://search.sohu.com/?keyword=%s' % list[0]  # 通过关键词拼接url
        else:
            start_url = list[0]
            for i in list[1:]:
                start_url = start_url + '%20' + i
            spider.start_url = 'https://search.sohu.com/?keyword=%s' % start_url
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
        return spider

    def start_requests(self):
        print(self.key_words)
        self.list = self.key_words.split()
        if len(self.list) == 1:
            start_url = 'https://search.sohu.com/?keyword=%s' % self.list[0]  # 通过关键词拼接url
            yield scrapy.Request(url=start_url, callback=self.parse)
        else:
            start_url = self.list[0]
            for i in self.list[1:]:
                print(i)
                start_url = start_url + '%20' + i
            start_url = 'https://search.sohu.com/?keyword=%s' % start_url
            yield scrapy.Request(url=start_url, callback=self.parse)

    def spider_closed(self, spider):
        spider.driver.quit()
        self.time_end = time.time()
        print('搜狐报网花费时间', self.time_end - self.time_start, 's')
        print("爬虫结束了")
        print('*' * 60)

    # 数据解析
    def parse(self, response):
        div_list = response.xpath("//*[@id='news-list']/div[@class='cards-small-plain']")  # 获取cards-small-plain种类新闻所在板块
        for div in div_list:
            item = text_Item()
            item['herf'] = div.xpath("./div/h4/a/@href").extract_first()
            desc_ = div.xpath("./div/h4/a").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item["title"] = desc.replace('\t', '').replace('\n', '')
            desc_ = div.xpath(
                "./div/p[@class='plain-content-desc']/a").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item['brief'] = desc

            desc_ = div.xpath("./div/p[@class='plain-content-comm']").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item['publish_date'] = desc.replace('\t', '').replace('\n', '').replace('\xa0', '').split(' ')[-1]
            item['key_words'] = self.key_words  # 关键词# 对要爬取的内容做一个简单的筛选
            # 布隆过滤器
            if item["herf"] in self.bloom:
                continue
            else:
                self.bloom.add(item["herf"])
            # 对要爬取的内容做一个简单的筛选，提高相关度
            count1 = 0
            for i in self.list:
                if re.search(i, item["title"]) is None and re.search(i, item["brief"]) is None:
                    count1 = count1 + 1
            if count1 == len(self.list):
                continue
            else:
                yield scrapy.Request(
                    item['herf'],
                    callback=self.parse_detail,
                    meta={"item": item},
                    dont_filter=True
                )
        div_list = response.xpath(
            "//*[@id='news-list']/div[@class='cards-small-plain-nobrief']")  # 获取cards-small-plain-nobrief种类新闻所在板块
        for div in div_list:
            item = text_Item()
            item['herf'] = div.xpath("./div/h4/a/@href").extract_first()
            desc_ = div.xpath("./div/h4/a").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item["title"] = desc.replace('\t', '').replace('\n', '')
            item['brief'] = ''  # 这一种没有简要

            desc_ = div.xpath("./div/p").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item['publish_date'] = desc.replace('\t', '').replace('\n', '').replace('\xa0', '').split(' ')[-1]
            item['key_words'] = self.key_words  # 关键词# 对要爬取的内容做一个简单的筛选
            # 布隆过滤器
            if item["herf"] in self.bloom:
                continue
            else:
                self.bloom.add(item["herf"])
            # 对要爬取的内容做一个简单的筛选，提高相关度
            count1 = 0
            for i in self.list:
                if re.search(i, item["title"]) is None and re.search(i, item["brief"]) is None:
                    count1 = count1 + 1
            if count1 == len(self.list):
                continue
            else:
                yield scrapy.Request(
                    item['herf'],
                    callback=self.parse_detail,
                    meta={"item": item},
                    dont_filter=True
                )
        div_list = response.xpath("//*[@id='news-list']/div[@class='cards-small-img']")  # 获取cards-small-img种类新闻所在板块
        for div in div_list:
            item = text_Item()
            item['herf'] = div.xpath(".//div[@class='cards-content-title']/a/@href").extract_first()
            desc_ = div.xpath(".//div[@class='cards-content-title']/a").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item["title"] = desc.replace('\t', '').replace('\n', '')
            desc_ = div.xpath(
                ".//p[@class='cards-content-right-desc']/a").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item['brief'] = desc

            desc_ = div.xpath(".//p[@class='cards-content-right-comm']").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item['publish_date'] = desc.replace('\t', '').replace('\n', '').replace('\xa0', '').split(' ')[-1]
            item['key_words'] = self.key_words  # 关键词# 对要爬取的内容做一个简单的筛选
            # 布隆过滤器
            if item["herf"] in self.bloom:
                continue
            else:
                self.bloom.add(item["herf"])
                # 对要爬取的内容做一个简单的筛选，提高相关度
                count1 = 0
                for i in self.list:
                    if re.search(i, item["title"]) is None and re.search(i, item["brief"]) is None:
                        count1 = count1 + 1
                if count1 == len(self.list):
                    continue
                else:
                    yield scrapy.Request(
                        item['herf'],
                        callback=self.parse_detail,
                        meta={"item": item},
                        dont_filter=True
                    )


    def parse_detail(self, response):
        item = response.meta['item']
        if item['brief'] != '':
            desc_info = response.xpath(
                "//*[@id='mp-editor']/p").xpath('string(.)').extract()
            # desc_ = desc_info.xpath('string(.)').extract()
            desc = ""
            for description in desc_info:
                description_ = description.strip()
                desc = desc + description_
            # item['content'] = "".join(item["content"])
            item['content'] = desc
            # print('结果是'+item)
        else:
            desc = response.xpath(
                "//*[@id='sohuplayer']/div/video/@src").extract_first()
            item['content'] = '视频链接是：' + desc
            file_dir = os.getcwd() + '\\视频' + '\\' + self.name
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            if 'MP4' in desc:  # blob加密的另外处理
                data = requests.get('https:'+desc).content
                with open(f"{file_dir}\\{item['title']}.mp4", 'wb') as fp:
                    fp.write(data)
        yield item

    def parse_video(self, response):
        item = response.meta['item']
        # 创建文件夹
        file_dir = os.getcwd() + '\\视频' + '\\' + self.name
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(f"{file_dir}\\{item['title']}.mp4", 'wb') as fp:
            fp.write(response)
