import re

import scrapy
from pybloom_live import ScalableBloomFilter
from scrapy import signals
from selenium import webdriver
from ..items import text_Item
from selenium.webdriver import EdgeOptions


class BBCSpider(scrapy.Spider):
    name = 'bbc'
    allowed_domains = ['https://www.bbc.co.uk/search?q=&d=news_gnl']

    # start_urls = ['https://www.bbc.co.uk/search?q=china+covid+virus&d=news_gnl']

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.key_words = text
        self.bloom = ScalableBloomFilter(initial_capacity=100, error_rate=0.001)

    @classmethod
    def from_crawler(cls, crawler, text=None, *args, **kwargs):
        spider = super(BBCSpider, cls).from_crawler(crawler, text, *args, **kwargs)
        spider.key_words = text
        # print(key_words)
        option = EdgeOptions()
        option.headless = False
        spider.driver = webdriver.Edge(options=option)
        spider.name = 'bbc'
        # crawler.signals.connect(spider.start_requests, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
        return spider

    # 动态生成初始 URL
    def start_requests(self):
        print(self.key_words)
        self.list = self.key_words.split()
        if len(self.list) == 1:
            self.start_url = 'https://www.bbc.co.uk/search?q=%s&d=news_gnl' % self.list[0]  # 通过关键词拼接url
            self.model = 'https://www.bbc.co.uk/search?q=%s&d=news_gnl&page={}' % self.list[0]
            yield scrapy.Request(url=self.start_url, callback=self.parse)
        else:
            self.url = self.list[0]
            for i in self.list[1:]:
                self.url = self.url + '+' + i
            self.start_url = 'https://www.bbc.co.uk/search?q=%s&d=news_gnl' % self.url
            self.model = 'https://www.bbc.co.uk/search?q=%s&d=news_gnl&page={}' % self.url
            yield scrapy.Request(url=self.start_url, callback=self.parse)

    def spider_closed(self, spider):
        spider.driver.quit()
        print("爬虫结束了")
        print('*' * 60)

    # 数据解析
    def parse(self, response):
        try:
            page = int(response.xpath(
                '//*[@id="main-content"]/div[4]/div/div/nav/div/div/div[3]/div/ol/li[14]/div/a/div/text()').extract_first())
            urls = []
            for i in range(page):
                url = self.model.format(i + 1)
                urls.append(url)
            for url in urls:
                yield scrapy.Request(url=url, callback=self.sub_parse, dont_filter=True)
        except:
            print('无搜索结果')
        li_list = response.xpath("//*[@id='main-content']/div[3]/div/div/ul/li")  # 获取每一个新闻所在板块
        for li in li_list:
            item = text_Item()
            item["title"] = li.xpath("./div/div/div[1]/div[1]/a/span/p/span/text()").extract_first()
            item["brief"] = li.xpath('./div/div/div[1]/div[1]/p/text()').extract_first()
            if 'programmes' in item["brief"]:
                continue
            item['herf'] = li.xpath("./div/div/div[1]/div[1]/a/@href").extract_first()
            item['publish_date'] = li.xpath(
                "./div/div/div[1]/div[2]/div/ul/div/li[1]/div[2]/span/span/text()").extract_first()
            item['key_words'] = self.key_words  # 关键词
            # 布隆过滤器
            if item["herf"] in self.bloom:
                continue
            else:
                self.bloom.add(item["herf"])
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
            # if re.search(r'[Cc]ovid', item["title"]) == None and re.search(r'COVID',
            #                                                                item["title"]) == None and re.search(
            #     r'virus', item["title"]) == None \
            #         and re.search(r'[Cc]ovid', item["brief"]) == None and re.search(r'COVID', item[
            #     "brief"]) == None and re.search(r'virus', item["brief"]) == None:
            #     continue
            else:
                yield scrapy.Request(
                    item['herf'],
                    callback=self.parse_detail,
                    meta={"item": item},
                    dont_filter=True
                )

    def sub_parse(self, response):
        li_list = response.xpath("//*[@id='main-content']/div[3]/div/div/ul/li")  # 获取每一个新闻所在板块
        # i=0
        # tr = tr_list[2]
        for li in li_list:
            item = text_Item()
            # print('111111')
            # print(i-1)
            item["title"] = li.xpath("./div/div/div[1]/div[1]/a/span/p/span/text()").extract_first()
            # print('结果是1' + item["title"])
            item["brief"] = li.xpath('./div/div/div[1]/div[1]/p/text()').extract_first()
            # print('结果是2' + item["brief"])
            item['herf'] = li.xpath("./div/div/div[1]/div[1]/a/@href").extract_first()
            if 'programmes' in item["brief"]:  # 跳过特殊网站
                continue
            # print('结果是3' + item['herf'])
            item['publish_date'] = li.xpath(
                "./div/div/div[1]/div[2]/div/ul/div/li[1]/div[2]/span/span/text()").extract_first()
            # print('结果是4' + item['publish_date'])
            item['key_words'] = self.key_words  # 关键词
            # 布隆过滤器
            if item["herf"] in self.bloom:
                continue
            else:
                self.bloom.add(item["herf"])
            # 对要爬取的内容做一个简单的筛选
            count1 = 0
            for i in self.list:
                if re.search(i, item["title"]) is None and re.search(i, item["brief"]) is None:
                    count1 = count1 + 1
            count2=0
            for i in self.list:
                demo=i.upper()
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

    def parse_detail(self, response):
        item = response.meta['item']
        desc_ = response.xpath("//*[@id='main-content']/article/div[@data-component='text-block']").xpath(
            'string(.)').extract()
        desc = ""
        for description in desc_:
            description_ = description.strip()
            desc = desc + description_
        # item['content'] = "".join(item["content"])
        item['content'] = desc
        # print('结果是'+item)
        yield (item)
