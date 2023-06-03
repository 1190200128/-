import re
import time
from pybloom_live import ScalableBloomFilter, BloomFilter
import scrapy
from scrapy import signals
from selenium import webdriver
from ..items import text_Item
from selenium.webdriver import EdgeOptions


class xinHuaWangSpider(scrapy.Spider):
    name = 'xinhuawang'
    allowed_domains = ['http://so.news.cn/']

    # start_urls = ['https://www.bbc.co.uk/search?q=china+covid+virus&d=news_gnl']

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.key_words = text
        # 可自动扩容的布隆过滤器
        self.bloom = ScalableBloomFilter(initial_capacity=100, error_rate=0.001)
        self.time_start = time.time()

    @classmethod
    def from_crawler(cls, crawler, text=None, *args, **kwargs):
        spider = super(xinHuaWangSpider, cls).from_crawler(crawler, text, *args, **kwargs)
        spider.key_words = text
        # print(key_words)
        option = EdgeOptions()
        option.headless = False
        spider.driver = webdriver.Edge(options=option)
        spider.name = 'xinhuawang'
        # crawler.signals.connect(spider.start_requests, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
        return spider

    # 动态生成初始 URL
    def start_requests(self):
        print(self.key_words)
        self.list = self.key_words.split()
        if len(self.list) == 1:
            self.start_url = 'http://so.news.cn/#search/0/%s/1/' % self.list[0]  # 通过关键词拼接url
            self.model = 'http://so.news.cn/#search/0/%s/{}/' % self.list[0]
            yield scrapy.Request(url=self.start_url, callback=self.parse)
        else:
            self.start_url = self.list[0]
            for i in self.list[1:]:
                self.start_url = self.start_url + '%20' + i
            self.start_url = 'http://so.news.cn/#search/0/%s/1' % self.start_url
            self.model = 'http://so.news.cn/#search/0/%s/{}' % self.start_url
            yield scrapy.Request(url=self.start_url, callback=self.parse)

    def spider_closed(self, spider):
        spider.driver.quit()
        self.time_end = time.time()
        print('新华网花费时间', self.time_end - self.time_start, 's')
        print("爬虫结束了")
        print('*' * 60)

    # 数据解析
    def parse(self, response):
        try:
            result_text = int(response.xpath(
                '//*[@id="newsCount"]/text()').extract_first())
            page=int(result_text/10)
            urls = []
            for i in range(1,5):
                url = self.model.format(i + 1)  # 解析有多少页面
                urls.append(url)
            for url in urls[:5]:
                yield scrapy.Request(url=url, callback=self.sub_parse, dont_filter=True)
                time.sleep(2)
        except:
            print('无搜索结果')
        li_list = response.xpath("//*[@id='newsCon']/div[@class='newsList']/div")  # 获取每一个新闻所在板块
        for li in li_list:
            item = text_Item()
            desc_ = li.xpath("./h2/a").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item["title"]=desc.replace('\n', '').replace('\t', '')
            item["brief"] = li.xpath(".//p[@class='newstext']/text()").extract_first().replace('\n', '').replace('\t', '')#新华网里可能有些新闻没有简要
            item['herf'] = li.xpath("./h2/a/@href").extract_first()
            item['publish_date'] = li.xpath(
                ".//p[@class='newstime']/span/text()").extract_first()
            item['key_words'] = self.key_words  # 关键词

            # 布隆过滤器
            if item["herf"] in self.bloom:
                continue
            else:
                self.bloom.add(item["herf"])

            # 新华网不用筛选
            # # 对要爬取的内容做一个简单的筛选，提高相关度
            # count1 = 0
            # for i in self.list:
            #     if re.search(i, item["title"]) is None and re.search(i, item["brief"]) is None:
            #         count1 = count1 + 1
            # if count1 == len(self.list) :
            #     continue
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
            desc_ = li.xpath("./h2/a").xpath('string(.)').extract()
            desc = ""
            for description in desc_:
                description_ = description.strip()
                desc = desc + description_
            item["title"] = desc.replace('\n', '').replace('\t', '')
            item["brief"] = li.xpath(".//p[@class='newstext']/text()").extract_first().replace('\n', '').replace('\t',
                                                                                                                 '')  # 新华网里可能有些新闻没有简要
            item['herf'] = li.xpath("./h2/a/@href").extract_first()
            item['publish_date'] = li.xpath(
                ".//p[@class='newstime']/span/text()").extract_first()
            item['key_words'] = self.key_words  # 关键词
            # 布隆过滤器
            if item["herf"] in self.bloom:
                continue
            else:
                self.bloom.add(item["herf"])
            # 对要爬取的内容做一个简单的筛选，提高相关度
            # count1 = 0
            # for i in self.list:
            #     if re.search(i, item["title"]) is None and re.search(i, item["brief"]) is None:
            #         count1 = count1 + 1
            # if count1 == len(self.list):
            #     continue
            yield scrapy.Request(
                item['herf'],
                callback=self.parse_detail,
                meta={"item": item},
                dont_filter=True
            )

    def parse_detail(self, response):
        item = response.meta['item']
        desc_ = response.xpath("//p").xpath(
            'string(.)').extract()
        desc = ""
        for description in desc_:
            description_ = description.strip()
            desc = desc + description_
        # item['content'] = "".join(item["content"])
        item['content'] = desc.replace('\t','').replace('\n','')
        # print('结果是'+item)
        yield (item)
