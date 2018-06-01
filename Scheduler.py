# -*- coding: utf-8 -*-
from tool.tools import Tools
from Download.Download import Download
from lxml import etree
from spider import GetProduct
import csv

class GetTag():
    def __init__(self):
        self.Tools = Tools()
        #self.Download = Download()
        self.failed_urls = []
    def pro_list(self, TagName, url, pages):
        url_list = []
        for i in range(1, pages):
            page_urls = url + "&page=" + str(i)
           #c = super(GetTag, self).parse(page_urls)
            c = Download.parse(page_urls)
            html = c[0]
            status = c[1]

            if status == 200:
                tree = etree.HTML(html)
                products = tree.xpath("//div[@class='gds-li-ratiowrap']/a/@href")
                # print(products)
                url_list.append(products)
        url_list = [y for x in url_list for y in x]
        self.getData(url_list, TagName)

    def getData(self, url_list, TagName):
        for each in url_list:
            each = each + ' '
            TagName = str(TagName)
            TagName = "".join(TagName).strip()

            pid = Tools.get_id(self, each)[0]
            pid = int(pid)
            #fsaad = Tools.add_url(self, each)
            # 判断产品表中是否存在tag的产品，如果不存在，就将其写入products
            # 如果存在, 判断是否存在parent_id = 0
            Tools.ProductCheckPid(self,pid)
            ProductCheckPid = Tools.ProductCheckPid(self,pid)
            if ProductCheckPid == False:
                pro_spider = GetProduct()
                pro_spider.resolution(url)
            elif ProductCheckPid != 0:
                pid = str(ProductCheckPid)
                url = Tools.relace_pid(pid, url)

            if Tools.TagNameCheck(TagName, pid) == True:
                self.saveData(TagName, pid, url)
                # print("kaishi")
            else:
                print('---tag----repetition---')
        print(TagName + 'cate---over')

    def saveData(self, TagName, pid, url):
        table = "m2b_tags"
        db = Tools.connect_mysql()
        cursor = db.cursor()

        sql = 'INSERT INTO {table} ' \
              'VALUES ("%s", "%s", "%s")'.format(table=table) % (TagName, pid, url)

        try:
            cursor.execute(sql)
            db.commit()
            print("tag---------ok")
        except Exception as e:
            db.rollback()
            print("----MYSQL--failed-------" + url, e)
            self.failed_urls.append(url)
            print(self.failed_urls)

        db.close()

    def getTag(self, pages, tag):
        with open(tag + '.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                TagName = row[0]
                cate_url = row[1]
                self.pro_list(TagName, cate_url, pages)
                # print(row)

            print("all over")

c = GetTag()
c.getTag(pages=2, tag='tag')