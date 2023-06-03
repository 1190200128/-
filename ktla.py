import re

import scrapy
from scrapy import signals
from selenium import webdriver
from ..items import text_Item
from selenium.webdriver import EdgeOptions


class KTLASpider(scrapy.Spider):
    name = 'ktla'
    allowed_domains = ['https://ktla.com/']

    # start_urls = ['https://www.bbc.co.uk/search?q=china+covid+virus&d=news_gnl']

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.key_words = text

    @classmethod
    def from_crawler(cls, crawler, text=None, *args, **kwargs):
        spider = super(KTLASpider, cls).from_crawler(crawler, text, *args, **kwargs)
        spider.key_words = text
        # print(key_words)
        option = EdgeOptions()
        option.headless = False
        spider.driver = webdriver.Edge(options=option)
        spider.name = 'ktla'
        # crawler.signals.connect(spider.start_requests, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
        return spider

    # 动态生成初始 URL
    def start_requests(self):
        print(self.key_words)
        self.list = self.key_words.split()
        if len(self.list) == 1:
            self.start_url = 'https://ktla.com/?submit=&s=%s' % self.list[0]  # 通过关键词拼接url
            self.model = 'https://ktla.com/page/{}/?submit&s=%s' % self.list[0]
            yield scrapy.Request(url=self.start_url, callback=self.parse)
        else:
            self.start_url = self.list[0]
            for i in self.list[1:]:
                self.start_url = self.start_url + '+' + i
            self.start_url = 'https://ktla.com/?submit=&s=%s' % self.start_url
            self.model = 'https://ktla.com/page/{}/?submit&s=%s' % self.start_url
            yield scrapy.Request(url=self.start_url, callback=self.parse)

    def spider_closed(self, spider):
        spider.driver.quit()
        print("爬虫结束了")
        print('*' * 60)

    # 数据解析
    def parse(self, response):
        try:
            result_text = response.xpath('//*[@id="main"]/header/form/div[2]/span/text()').extract_first()
            print('sssss')
            num = int(re.findall("\d+", result_text)[1])
            page = int(num / 60)
            urls = []
            for i in range(1,page):
                url = self.model.format(i + 1)
                urls.append(url)
            # for url in urls:
            #     yield scrapy.Request(url=url, callback=self.sub_parse, dont_filter=True)
        except:
            print('无搜索结果')
        li_list = response.xpath("//*[@id='main']/section/div/article")  # 获取每一个新闻所在板块
        for li in li_list[:1]:
            item = text_Item()
            item["title"] = li.xpath("./div/h2/a/text()").extract_first().replace('\t','').replace('\n','')
            item["brief"] = li.xpath('./div/div/a/p/text()').extract_first().replace('\t','')
            item['herf'] = li.xpath("./div/h2/a/@href").extract_first().replace('\t','')
            # item['publish_date'] = li.xpath("./div/footer/time/@datetime").extract_first()
            item['key_words'] = self.key_words  # 关键词
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

    def sub_parse(self, response):
        li_list = response.xpath("//*[@id='main-content']/div[3]/div/div/ul/li")  # 获取每一个新闻所在板块
        for li in li_list:
            item = text_Item()
            item["title"] = li.xpath("./div/h2/a/text()").extract_first().replace('\t', '').replace('\n', '')
            item["brief"] = li.xpath('./div/div/a/p/text()').extract_first().replace('\t', '')
            item['herf'] = li.xpath("./div/h2/a/@href").extract_first().replace('\t', '')
            # item['publish_date'] = li.xpath("./div/footer/time/text()").extract()
            item['key_words'] = self.key_words  # 关键词
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
        item['publish_date']=response.xpath("//*[@id='main']/article/div[1]/p[2]/time").xpath('string(.)').extract_first()
        desc_ = response.xpath("//*[@id='main']/article/div[3]").xpath('string(.)').extract()
        desc = ""
        for description in desc_:
            description_ = description.strip()
            desc = desc + description_
        # item['content'] = "".join(item["content"])
        item['content'] = desc.replace('\t','').replace('\n','')
        print(item)
        yield (item)
