# -*- coding: utf-8 -*-
from config import setting
from tool.tools import Tools
import requests
from bs4 import BeautifulSoup
import random
import time
from lxml import etree
import json
from Download.Download import Download
from DataProcess import data_process,son_data_process


class GetProduct(Download):

    def detail(self, file):
        pro_num = 1
        urls = self.tools.get_url(file)
        for url in urls:
            self.resolution(url)
            print(">>" + str(pro_num) + "------product-over--------")
            ProductCheck = self.tools.ProductCheck(url)
            if ProductCheck == 0:
                time.sleep(random.choice(range(5, 10)))
            pro_num += 1
            #break
        print('all-products----over')

    def resolution(self, url):
        c = super(GetProduct, self).parse(url)
        html = c[0]
        status = c[1]
        ProductCheck = self.tools.ProductCheck(url)
        if ProductCheck == 0:
            if status == 200:
                tree = etree.HTML(html)
                pid = self.tools.get_id(url)[0]
                cid = self.tools.get_id(url)[1]
                title = tree.xpath("//div[@class='goodsd-right col-sm-5']//h4/text()")
                title = "".join(title).strip()
                price = self.tools.get_price(pid)[0]
                orig_price = self.tools.get_price(pid)[1]
                description = tree.xpath("//div[@class='goodsd-right col-sm-5']//div[@class='kv']/div//text()")
                description = [x.strip() for x in description if x != '\n          ']
                description = [x for x in description if x != '']
                description = "\n".join(description)

                size_fits = tree.xpath("//table[@class='kv']")[0]
                del size_fits.attrib['class']
                for size_fit in size_fits:
                    del size_fit.attrib['class']
                    for i in size_fit:
                        # keys(1)
                        del i.attrib['class']
                        i.set('valign', '321')
                        del i.attrib['valign']
                        i.set('colspan', '321')
                        del i.attrib['colspan']
                    # print(size_fit)
                    # list_size.append(size_fit)

                size_fits = etree.tostring(size_fits)
                size_fits = size_fits.decode().replace('\n', '')
                sku = tree.xpath("//div[@class='summary']/span[@class='sku']/text()")
                sku = "".join(sku).replace(' ', '').replace('\n', '').replace('SKU:', '')
                review = tree.xpath("//div[@class='comments']/a/span/text()")
                review = "".join(review).strip('\n').replace(' ', '')
                sizes = self.tools.get_size(pid)
                if review == '':
                    review = 0

                img_urls = tree.xpath("//div[@class='swiper-wrapper']/div/img/@data-src")

                # img_counts = tree.xpath("//div[@class='vertical-wrap']/img/@data-src")
                color_urls = tree.xpath("//div[@class='opt-color']/a/@href")
                color_imgs = tree.xpath("//div[@class='opt-color']/a/@style")
                # 判断是否有相同的id
                ProductCheckSku = self.tools.ProductCheck(sku)
                if ProductCheckSku == 0:
                    # 判断是否有多个颜色
                    this_url = url
                    if color_urls:
                        color_urls = color_urls[1:]
                        for color_url in color_urls:
                            color_url = color_url + ''
                            # color_url = str(color_url.encode('UTF-8'))
                            self.son_resolution(color_url, pid)
                    data_process.get_data(pid, cid, this_url, title, price, orig_price, description, size_fits, sku,
                                          review, img_urls, color_urls, color_imgs, sizes)

        else:
             print("-----Parent-url-repetition-----")

    def son_resolution(self, color_url, parent_pid):
        url = self.tools.add_url(color_url)
        c = super(GetProduct, self).parse(url)
        html = c[0]
        status = c[1]
        ProductCheck = self.tools.ProductCheck(url)
        if ProductCheck == 0:
            if status == 200:
                tree = etree.HTML(html)
                parent_id = int(parent_pid)
                pid = self.tools.get_id(url)[0]
                cid = self.tools.get_id(url)[1]
                title = tree.xpath("//div[@class='goodsd-right col-sm-5']//h4/text()")
                title = "".join(title).strip()
                price = self.tools.get_price(pid)[0]
                orig_price = self.tools.get_price(pid)[1]
                sku = tree.xpath("//div[@class='summary']/span[@class='sku']/text()")
                sku = "".join(sku).replace(' ', '').replace('\n', '').replace('SKU:', '')
                review = tree.xpath("//div[@class='comments']/a/span/text()")
                review = "".join(review).replace('\n', '').replace(' ', '')
                if review == '':
                    review = 0
                img_urls = tree.xpath("//div[@class='swiper-wrapper']/div/img/@data-src")
                sizes = self.tools.get_size(pid)
                ProductCheckSku = self.tools.ProductCheck(sku)
                if ProductCheckSku == 0:
                    son_data_process.get_data(parent_id, pid, cid, url, title, price, orig_price, sku, review, img_urls,
                                              sizes)
        else:
            print("-----son-url-repetition-----")

