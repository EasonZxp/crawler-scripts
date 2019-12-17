#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import urllib
import pandas as pd
import time


def request_url(url, headers, timeout):
    req = urllib.request.Request(url=url, headers=headers) # 伪装浏览器用户
    try:
        res = urllib.request.urlopen(req, timeout=timeout) # 执行请求获取响应信息
    except urllib.error.HTTPError as e:
        print(e.code)
        err_code = e.code
        return None, err_code
    err_code = 0    
    html = res.read().decode('utf-8') # 从响应对象中读取信息并解码
    return html, err_code


def parse_single_html(html):
    pattern = r'.*&quot;url&quot;:&quot;(.*)&quot;}'
    repo_list = re.findall(pattern, html)
    for repo in repo_list:
        author_name = re.findall(r'.*/.*/(.*)/.*', repo)[0]
        repo_name = re.findall(r'.*/.*/.*/(.*)', repo)[0]
        data_list.append([author_name, repo_name, repo]) 


def write_to_csv(data_list):
    csv_header = ['作者名字', '仓库名字', '仓库地址']
    pd.DataFrame(columns = csv_header,data = data_list).to_csv('fall_detect_repolist.csv', encoding='gb2312')


data_list = []


def request_all_pages():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'}
    number = 1
    retry_number = 0
    
    while True:
        url = 'https://github.com/search?p=' + str(number) + '&q=fall+detect&type=Repositories'
        html, err_code = request_url(url, headers, 15)
        if html != None:
            parse_single_html(html)
            print('have parsed %d pages...' % number)
            number += 1
            time.sleep(5)
        elif err_code == 429: # too many http requests
            time.sleep(30)
            retry_number += 1
            continue
        elif retry_number > 10:
            break
        else:
            break


request_all_pages()
write_to_csv(data_list)

