# -*- coding: utf-8 -*-
import re
import pymysql
import os
import requests
import json


#获取需要爬取的产品url
class Tools(object):
    def __init__(self):
        self.url = 'https://www.shein.com'
        self.pro_list = []
        self.dirpath = os.path.dirname(os.path.realpath(__file__))
    def get_price(self,pid):
        url = "https://www.shein.com/product/getPrice?goods_id=" + pid
        price_json = requests.get(url)
        price_json = json.loads(price_json.text)
        price = price_json['info']['price'][pid]['salePrice']['amount']
        orig_price = price_json['info']['price'][pid]['retailPrice']['amount']
        return price, orig_price

    # 获取尺寸函数
    def get_size(self,pid):
        sizes = []
        url = "https://www.shein.com/product/attr?id=" + pid
        size_json = requests.get(url)
        size_json = json.loads(size_json.text)
        if size_json['info'] != None:
            for size in size_json['info']['attrSize']:
                size = size['attr_value']
                sizes.append(size)
        else:
            sizes = []
        return sizes

    def get_url(self, file):
        num = 0
        filename = self.dirpath+'\\' + file + '.txt'
        with open(filename, 'r' ,encoding='UTF-8') as file_to_read:
            lines = file_to_read.readlines()
            for line in lines:
                pro_url = self.url + line.strip('\n')
                self.pro_list.append(pro_url)
            return self.pro_list

    #完善残缺的url
    def add_url(self,xurl):
        newurl = self.url +xurl
        return newurl

    #获取url中的pid和cid
    def get_id(self, url):

        pid = re.findall(r'-p-(\d+)*',url, re.S)[0]
        cid = re.findall(r'-cat-(\d+)*',url, re.S)[0]
        return pid, cid


    #去除url多余的英文，然后获取高清大图的url，且判断是否有https前缀
    def re_img_url(self, img_url):
        thumb = re.findall(r'_thumbnail_(\d+[a-z]{1}\d+).',img_url, re.S)
        https = re.findall(r'(https:)',img_url, re.S)
        if thumb :
            s = "_thumbnail_"+thumb[0]
            img_url = "https:"+img_url.replace(s,'')
        elif len(https) == 0:
            img_url = "https:"+ img_url

        return img_url

    #清洗数据中的空格与换行符
    def string(self, values):
        values = values.replace(' ','').replace('\n','')
        return values

    #截取color图
    def cut_url(self, url):
      color_img = re.findall(r'url\((.*)\)', url)
      color_img =  "https:" + color_img[0]
      return color_img
      #pass

    #保存失败url
    def save_fail_url(self, urls):
        with open('failurls.txt', "a") as f:
            f.write(urls+"\n")

    def connect_mysql(self):
        db = pymysql.connect(host="localhost", user="root", password="root9999", port=3306, db='shein3')
        return db

    #当flag等于True时，说明url没有重复
    def ProductCheck(self, pro_url):
        db = self.connect_mysql()
        cursor = db.cursor()
        sql = 'SELECT count(*) FROM m2b_products WHERE url = "%s"' % (pro_url)
        try:
            cursor.execute(sql)
            row = cursor.fetchone()
            row = row[0]
            #print(type(row))
            return row
            #print(all_urls)
        except Exception as e :
            print(e)
        db.close()
    #检测sku重复
    def ProductCheckSku(self, sku):
        db = self.connect_mysql()
        cursor = db.cursor()
        sql = 'SELECT count(*) FROM m2b_products WHERE sku = "%s"' % (sku)
        try:
            cursor.execute(sql)
            row = cursor.fetchone()
            row = row[0]
            return row
        except Exception as e:
            print(e)
        db.close()
    #检测pid的是否重复
    def ProductCheckPid(self, pid):
        db = self.connect_mysql()
        cursor = db.cursor()
        sql = 'SELECT parent_id FROM m2b_products WHERE pid = "%s"' % (pid)
        try:
            cursor.execute(sql)
            row = cursor.fetchone()
            if row == None:
                row = False
                return row
            else:
                row = row[0]
                return row
            # print(all_urls)
        except Exception as e:
            print(e)
        db.close()
    #检测tag的数据是否重复
    def TagNameCheck(self, TagName,pid):
        db = self.connect_mysql()
        cursor = db.cursor()
        sql = 'SELECT * FROM m2b_tags WHERE TagName ="%s" and pid = "%s"' % (TagName, pid)
        try:
            cursor.execute(sql)
            row = cursor.fetchone()
            if row == None:
                row = True
                return row
            else:
                row = False
                return row
            # print(all_urls)
        except Exception as e:
            print(e)
        db.close()

    #修改tag表里面的url，替换pid
    def relace_pid(self, pid, url):
        parent_url = re.sub(r'-p-(\d+)*', '-p-'+pid, url)
        return parent_url

tools  = Tools()
