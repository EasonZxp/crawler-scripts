#!/usr/bin/env python
# coding: utf-8

# # 目标
# - 爬取某个时间内gerrit上merged的代码提交，网页地址: http://172.16.1.12:8080/#/q/status:merged
# - 爬取数据存储在csv文本中
# - 数据统计可视化饼图

# # 步骤
# - 分析待爬取网页
# - 使用requests库download html数据
# - 解析html数据，获取想要的数据(owner，subject，time, branch)
# - 数据存储csv文件
# - 数据读取，饼图展示
import json
import csv
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'GerritAccount=aGuusMdOedjnXPmoaB.HRV7g2WzKLjS',
    'Host': '172.16.1.12:8080',
    'Referer': 'http://172.16.1.12:8080/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.102 Safari/537.36 Vivaldi/2.6.1566.44',
    'X-Gerrit-Auth': 'aGuuWI2Fxqd8nWAa9rdikkUE67QaR6a'
}
all_data = []


def time_cmp(time1, time2):
    return int(time1) > int(time2)


def request_all_htmls(end_timestamp):
    number = 0
    run_condition = True

    while run_condition:
        request_url = 'http://172.16.1.12:8080/changes/?q=status:merged&n=25&O=1' + '&S=' + str(25 * number)
        html = requests.get(request_url, headers=headers, timeout=5)
        if html.status_code == 200:
            data = html.text.replace(')]}\'', '')
            json_data = json.loads(data)
            if len(json_data) <= 0:
                print('not valid json data, break.')
                run_condition = False
                break

            for commit in json_data:
                commit_time = commit['updated'].split('.')[0].replace(' ', '').replace('-', '').replace(':', '')
                commit_author = commit['owner']['name']
                commit_subject = commit['subject']
                commit_branch = commit['branch']
                commit_project = commit['project']
                # print(commit_time, commit_author, commit_subject, commit_branch, commit_project)
                commit_dict = dict(zip(['time', 'project', 'branch', 'owner', 'subject'], [commit_time, commit_project,
                                                                                           commit_branch, commit_author,
                                                                                           commit_subject]))

                if time_cmp(commit_time, end_timestamp):
                    # print(commit_dict)
                    all_data.append(commit_dict)
                else:
                    print('time end, break...')
                    run_condition = False
                    break

            number += 1
            print('have parsed %d pages...' % number)
        else:
            print('request html error : %d' % html.status_code)
            break;
    pass


def func(pct, allvals):
    absolute = int(pct / 100. * np.sum(allvals))
    return "{:.1f}%\n({:d})".format(pct, absolute)


def print_commit_ratio_pie():
    commit_author = []
    commit_number = []
    df = pd.read_csv('commits.csv', encoding="ISO-8859-1")
    for key, group_df in df.groupby('owner'):
        commit_author.append(key)
        commit_number.append(len(group_df))
    print(commit_author, commit_number)

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    fig, ax = plt.subplots(figsize=(10, 20), subplot_kw=dict(aspect="equal"))
    wedges, texts, autotexts = ax.pie(commit_number, autopct=lambda pct: func(pct, commit_number),
                                      textprops=dict(color="w"))
    ax.legend(wedges, commit_author,
              title="commit author",
              loc="upper left",
              bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title("代码提交统计")
    plt.show()


def write_to_csv_file():
    # write to csv
    # time project branch owner subject
    with open("commits.csv", "a", newline='') as file:
        writer = csv.writer(file)
        fieldnames = {'time', 'project', 'branch', 'owner', 'subject'}  # 表头
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for commit_dict in all_data:
            writer.writerow(commit_dict)
        file.close()


request_all_htmls(int('20191201042116'))
write_to_csv_file()
print_commit_ratio_pie()
