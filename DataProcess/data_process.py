# -*- coding: utf-8 -*-
from tool import tool
import pymysql
def get_data(pid, cid, url, title, price, orig_price, description, size_fits, sku, review, img_urls, color_urls, color_imgs, sizes):
	#print(len(img_urls))
	pid = int(pid)
	cid = int(cid)
	# price = int(price)
	# orig_price = int(orig_price)
	review = int(review)
	mysql(pid, cid, url, title, price, orig_price, description, size_fits, sku, review, img_urls, color_urls, color_imgs, sizes)
	# for img_url in img_urls:
	#     img_url = tool.re_img_url(img_url)


def mysql(pid, cid, url, title, price, orig_price, description, size_fits, sku, review, img_urls, color_urls, color_imgs, sizes):

	table= "m2b_products"
	db = tool.tools.connect_mysql()
	cursor = db.cursor()
	img_num = 1
	color_num = 1
	size_num = 1
	c_img_num = 1

	failed_urls = []

	img_keys =[]
	color_keys = []
	size_keys =[]
	c_img_keys =[]

	re_img_urls = []
	re_color_urls = []
	re_size =[]
	re_c_img = []
	#图片链接
	for img_url in img_urls:
		img_url = tool.tools.re_img_url(img_url)
		img_key = "img_url_"+str(img_num)
		img_keys.append(img_key)
		re_img_urls.append('"'+img_url+'"')
		img_num += 1

	img_keys = ','.join(img_keys)
	re_img_urls = ",".join(re_img_urls)
	img_values = re_img_urls

	#颜色链接
	if len(color_urls) !=0:
		for color_url in  color_urls:
			color_url = tool.tools.add_url(color_url)
			color_key = "color_url_"+str(color_num)
			color_keys.append(color_key)
			re_color_urls.append('"'+color_url+'"')
			color_num += 1
		color_keys = ','.join(color_keys)
		re_color_urls = ",".join(re_color_urls)
		color_values = re_color_urls

		for color_img in color_imgs:
			color_img = str(color_img.encode('utf-8'))
			color_img_url = tool.tools.cut_url(color_img)
			c_img_key = "color_img_" + str(c_img_num)
			c_img_keys.append(c_img_key)
			re_c_img.append('"'+color_img_url+'"')
			c_img_num += 1
		c_img_keys = ",".join(c_img_keys)
		re_c_img = ",".join(re_c_img)
		c_img_values = re_c_img
	else:
		color_keys = "".join('color_url_1')
		color_values = '"'+"none"+'"'

		c_img_keys = "".join('color_img_1')
		c_img_values = '"'+"none"+'"'


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


	sql = 'INSERT INTO {table}({img_keys},{color_keys},{size_keys},{c_img_keys}, pid, cid, url, title, price, orig_price, description, size_fit, sku, review) ' \
		  'VALUES ({img_values},{color_values},{size_values},{c_img_values},"%d","%d","%s","%s","%s","%s","%s","%s","%s","%d")'\
		  .format(table=table,c_img_keys =c_img_keys ,c_img_values = c_img_values, img_keys=img_keys, img_values=img_values,color_keys = color_keys,color_values = color_values,size_keys = size_keys,size_values = size_values) \
		  %(pid, cid, url, title, price, orig_price, description, size_fits, sku, review)

	try:
		cursor.execute(sql)
		db.commit()
		print("ok")
	except Exception as e:
		db.rollback()
		print("----MYSQL--failed-------"+url,e)
		failed_urls.append(url)
		print(failed_urls)

	db.close()
