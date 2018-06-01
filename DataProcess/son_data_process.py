# -*- coding: utf-8 -*-
from tool.tools import Tools
import pymysql
tools = Tools()
def get_data(parent_id, pid, cid, url, title, price, orig_price, sku, review, img_urls ,sizes):
	#print(len(img_urls))
	pid = int(pid)
	cid = int(cid)
	review = int(review)
	mysql(parent_id, pid, cid, url, title, price, orig_price, sku, review, img_urls ,sizes)


def mysql(parent_id, pid, cid, url, title, price, orig_price, sku, review, img_urls ,sizes):

	table= "m2b_products"
	db = tools.connect_mysql()
	cursor = db.cursor()
	img_num = 1
	size_num = 1

	failed_urls = []

	img_keys =[]
	size_keys =[]

	re_img_urls = []
	re_size =[]
	#图片链接
	for img_url in img_urls:
		img_url = tools.re_img_url(img_url)
		img_key = "img_url_"+str(img_num)
		img_keys.append(img_key)
		re_img_urls.append('"'+img_url+'"')
		img_num += 1

	img_keys = ','.join(img_keys)
	re_img_urls = ",".join(re_img_urls)
	img_values = re_img_urls

	#尺寸
	if len(sizes) != 0:
		for size in  sizes:
			size_key = "size_"+str(size_num)
			size_keys.append(size_key)
			re_size.append('"'+size+'"')
			size_num += 1
		size_keys = ','.join(size_keys)
		re_size = ",".join(re_size)
		size_values = re_size
	else:
		size_keys = "".join('size_1')
		size_values = '"'+"none"+'"'


	sql = 'INSERT INTO {table}({img_keys},{size_keys}, parent_id, pid, cid, url, title, price, orig_price, sku, review) ' \
		  'VALUES ({img_values},{size_values},"%d","%d","%d","%s","%s","%s","%s","%s","%d")'\
		  .format(table=table, img_keys=img_keys, img_values=img_values,size_keys = size_keys,size_values = size_values) \
		  %(parent_id, pid, cid, url, title, price, orig_price, sku, review)
	try:
		cursor.execute(sql)
		db.commit()
		print("son--ok")
	except Exception as e:
		db.rollback()
		print("---son---MYSQL--failed-------",e)
		failed_urls.append(url)
		print(failed_urls)

	db.close()
