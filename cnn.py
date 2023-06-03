import re
from itertools import groupby

import scrapy
from scrapy import signals
from selenium import webdriver
from ..items import text_Item
from selenium.webdriver import EdgeOptions


class CNNSpider(scrapy.Spider):
    name = 'cnn'
    allowed_domains = ['https://edition.cnn.com/']

    # start_urls = ['https://www.bbc.co.uk/search?q=china+covid+virus&d=news_gnl']

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.key_words = text


    @classmethod
    def from_crawler(cls, crawler, text=None, *args, **kwargs):
        spider = super(CNNSpider, cls).from_crawler(crawler, text, *args, **kwargs)
        spider.key_words = text
        # print(key_words)
        option = EdgeOptions()
        option.headless = False
        spider.driver = webdriver.Edge(options=option)
        spider.name = 'cnn'
        # crawler.signals.connect(spider.start_requests, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)  # 爬虫结束信号
        return spider

    # 动态生成初始 URL
    def start_requests(self):
        print(self.key_words)
        self.list = self.key_words.split()
        if len(self.list) == 1:
            start_url = 'https://edition.cnn.com/search?q=%s&from=0&size=10&page=1&sort=newest&types=article&section=' % self.list[0]  # 通过关键词拼接url
            self.model='https://edition.cnn.com/search?q=%s&from=0&size=10&page={}&sort=newest&types=article&section=' % self.list[0]
            yield scrapy.Request(url=start_url, callback=self.parse)
        else:
            start_url = self.list[0]
            for i in self.list[1:]:
                print(i)
                start_url = start_url + '+' + i
            start_url = 'https://edition.cnn.com/search?q=%s&from=0&size=10&page=1&sort=newest&types=article&section=' % start_url
            self.model = 'https://edition.cnn.com/search?q=%s&from=0&size=10&page={}&sort=newest&types=article&section=' % self.list[0]
            yield scrapy.Request(url=start_url, callback=self.parse)

    def spider_closed(self, spider):
        spider.driver.quit()
        print("爬虫结束了")
        print('*' * 60)

    # 数据解析
    def parse(self, response):
        try:
            results_text = response.xpath('//*[@id="search"]/div[2]/div/div[2]/div[1]/a/div[2]/div[1]/@data-zjs-traits-search_results_number').extract_first()
            num=int([k for k, g in groupby(results_text)][2])
            page=int(num/10)
            urls = []
            for i in range(1,page):
                url = self.model.format(i + 1)
                urls.append(url)
            for url in urls:
                yield scrapy.Request(url=url, callback=self.sub_parse, dont_filter=True)
        except:
            print('无搜索结果')
        li_list = response.xpath("//*[@id='search']//div[@class='search__results-list']/div")  # 获取每一个新闻所在板块
        for li in li_list:
            item = text_Item()
            item["title"] = (li.xpath("./a/div[2]/div[1]").xpath('string(.)').extract_first()).replace('\n','')
            item["brief"] = li.xpath('./a/div[2]/div[3]').xpath('string(.)').extract_first().replace('\n','')
            if 'programmes' in item["brief"]:
                continue
            item['herf'] = li.xpath("./a/@href").extract_first()
            item['publish_date'] = li.xpath("./a/div[2]/div[2]").xpath('string(.)').extract_first().replace('\n','')
            item['key_words'] = self.key_words  # 关键词

            # if re.search(r'[Cc]ovid', item["title"]) == None and re.search(r'COVID',
            #                                                                item["title"]) == None and re.search(
            #     r'virus', item["title"]) == None \
            #         and re.search(r'[Cc]ovid', item["brief"]) == None and re.search(r'COVID', item[
            #     "brief"]) == None and re.search(r'virus', item["brief"]) == None:
            #     continue
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
        # i=0
        # tr = tr_list[2]
        for li in li_list:
            item = text_Item()
            item["title"] = (li.xpath("./a/div[2]/div[1]").xpath('string(.)').extract_first()).replace('\n', '')
            item["brief"] = li.xpath('./a/div[2]/div[3]').xpath('string(.)').extract_first().replace('\n', '')
            if 'programmes' in item["brief"]:
                continue
            item['herf'] = li.xpath("./a/@href").extract_first()
            item['publish_date'] = li.xpath("./a/div[2]/div[2]").xpath('string(.)').extract_first().replace('\n', '')
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

    def parse_detail(self, response):
        item = response.meta['item']
        # desc_ = response.xpath("/html/body//article//div[@class='article__content']").xpath(
        #     'string(.)').extract()
        # desc = ""
        # for description in desc_:
        #     description_ = description.strip()
        #     desc = desc + description_
        # # item['content'] = "".join(item["content"])
        #brief和content完全相同
        item['content'] = item['brief']
        item['brief']=item['content'][0:100]
        print(item)
        # print('结果是'+item)
        yield (item)
