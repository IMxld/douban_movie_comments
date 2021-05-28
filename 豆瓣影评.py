import random as r
import time as t
import urllib.request
import urllib.error
import re
import zlib
import csv
import os
import sys

time_start = t.time()#计时器
time_temp = t.time()#计时器2

try:
    cookie_now = open('cookie.txt', encoding = 'utf-8').read()#读取cookie
except FileNotFoundError:
    print('缺少必要文件cookie.txt！')
    os.system('pause')
    sys.exit(0)
try:
    user_agent = open('user_agent.txt', encoding = 'utf-8').read()#读取user_agent
except FileNotFoundError:
    print('缺少必要文件user_agent.txt！')
    os.system('pause')
    sys.exit(0)
try:
    url_list = open('url_list.txt', encoding = 'utf-8').read().splitlines()#网页链接列表
except FileNotFoundError:
    print('缺少必要文件url_list.txt')
    os.system('pause')
    sys.exit(0)

#方便从出问题的地方开始抓取
while True:
    try:
        beginning = int(input('想要从第几部电影开始抓取？'))
    except ValueError:
        print('\n请输入一个整数！\n')
        continue
    
    if 0 < beginning <= len(url_list):
        break
    else:
        print('\n请输入在电影总部数范围内的一个整数！\n')
print('\n')
while True:
    try:
        beginning_page = int(input('想要从第几页开始抓取？'))
    except ValueError:
        print('\n请输入一个整数！\n')
        continue
    
    if 0 < beginning_page:
        break
    else:
        print('\n请输入一个正数！\n')
print('\n')

#创建或直接打开datas.csv
files_exist = 1
try:
    datas = open('datas.csv', encoding = 'utf-8-sig', newline = '')
except IOError:
    files_exist = 0
try:
    datas = open('datas.csv', 'a', encoding = 'utf-8-sig', newline = '')
except PermissionError:
    print('请关掉datas.csv后再运行！')
    os.system('pause')
    sys.exit(0)
bloumn_name = ['页面网址', 'id', '用户LINK', 'time',  '星级', '星级评价', '有用', '没用', '回应', '单篇页面网址', '页面标题', '剧透', '内容']
pen = csv.DictWriter(datas, fieldnames = bloumn_name)
if files_exist == 0:
    pen.writeheader()

err = 0#异常状态检测值
goto_page_time = 1#跳转页码功能使用次数
header = {'User-Agent':user_agent,
          'Accept-Encoding': 'gzip, deflate',
          'Cookie':cookie_now
          }#建议后台挂一个浏览器，保持登陆状态并更新cookie

#打开网页函数
def html_get(url):
    global header, err
    try:
        res = urllib.request.Request(url, headers = header)
        res = urllib.request.urlopen(res)
        res.encoding = 'utf-8'
        html = res.read()
        html = zlib.decompress(html, 16+zlib.MAX_WBITS).decode('utf-8')
    except urllib.error.HTTPError or urllib.error.URLError:
        html = 'ERROR!'
        print('请求打开网页时出错！有可能被豆瓣发现我们是爬虫程序了，也有可能是网址出错，请检查后重试！')
        err += 1
    return html

for i in url_list:
    #跳转到问题部分
    if (url_list.index(i) + 1) < beginning:
        continue
    if goto_page_time != 1:
        page = 0
    else:
        goto_page_time = 0
        page = (beginning_page - 1) * 20

    one_time_variable = 1#每次打开新的电影影评时的一次性变量

    while True:
        #提示当前进程所在位置
        print('现在在第 ' + str((url_list.index(i) + 1)) + ' 部电影处。')
        print('现在在第 ' + str((int(page/20) + 1)) + ' 页。')

        #构建url，打开网页并读取网页源代码
        page = str(page)
        url = i + 'reviews?start=' + page#构建url
        html = html_get(url)
        if err != 0:
            break

        #一次性变量
        if one_time_variable == 1:
            title_temp = re.search(r'<title>[\s\S]*?</title>', html).group()
            comment_num = int(re.search(r'(?<=\()\d+(?=\))', title_temp).group())#获取影评总数
            movie_name = re.search(r'(?<=).*?(?=的影评)', title_temp).group().strip()#获取电影名
            one_time_variable = 0
            if comment_num == 0:
                print('这部电影还没有影评！\n')
                break

        all_information = re.findall(r'<div data-cid="[\s\S]*?回应</a>', html)#获取除了影评正文的所有信息

        #检测是否漏掉数据
        if int(int(page) / 20) < int(comment_num / 20):
            if len(all_information) != 20:
                print('本次获取信息不是20条！有可能被豆瓣发现我们是爬虫程序了，请检查后重试！')
                err += 1
                break
        elif int(int(page) / 20) == int(comment_num / 20):
            if (comment_num % 20) != len(all_information):
                print('本次获取信息不是20条！有可能被豆瓣发现我们是爬虫程序了，请检查后重试！')
                err += 1
                break
        else:
            print('已完成：100.00%\n')
            break

        print('已完成：{:.2f}%\n'.format(2000 * (int(page)/20) / comment_num))#提示当前进程所在位置

        user_id, user_adress, comment_time, star, star_discribe, use, useless, responses, comment_adress, comment_title, if_spoiler, comments = [], [], [], [], [], [], [], [], [], [], [], []

        for m in all_information:
            user_id.append(re.search(r'(?<=class="name">)[\s\S]*?(?=</a>)', m).group())#遍历all_information，分离出用户名，并装进一个list
            user_adress.append(re.search(r'(?<=<a href=")[\s\S]*?(?=" class="avator")', m).group())#遍历all_information，分离出用户链接，并装进一个list
            comment_time.append(re.search(r'(?<=class="main-meta">)[\s\S]*?(?=</span>)', m).group())#遍历all_information，分离出评论时间，并装进一个list
            try:
                star.append(re.search(r'(?<=<span class="allstar)\d(?=0 main-title-rating")', m).group() + '星')#遍历all_information，分离出星级，并装进一个list
                star_discribe.append(re.search(r'(?<=0 main-title-rating" title=")..(?=")', m).group())#遍历all_information，分离出星级评价，并装进一个list
            except AttributeError:
                star.append('')
                star_discribe.append('')
            try:
                use.append('有用 ' + re.search(r'\d+(?=\n)', re.search(r'(?<=<span id="r-useful_count-)[\s\S]+?(?=</span>)', m).group()).group())#遍历all_information，分离出有用数，并装进一个list
            except AttributeError:
                use.append('有用 0')
            try:
                useless.append('没用 ' + re.search(r'\d+(?=\n)', re.search(r'(?<=<span id="r-useless_count-)[\s\S]+?(?=</span>)', m).group()).group())#遍历all_information，分离出没用数，并装进一个list
            except AttributeError:
                useless.append('没用 0')
            responses.append(re.search(r'\d+(?=回应)', m).group())#遍历all_information，分离出回应数，并装进一个list
            title = re.search(r'(?<=<h2>)[\s\S]*?(?=</h2>)', m).group()#遍历all_information，分离出标题和标题链接
            comment_adress.append(re.search(r'(?<=<a href=").*?(?=">)', title).group())#从title中分离出评论链接，并装进一个list
            comment_title.append(re.search(r'(?<=">)[\s\S]*?(?=</a>)', title).group() + '（' + movie_name + '）' + '剧评')#从title中分离出评论标题，并装进一个list
            try:
                if_spoiler.append(re.search(r'(?<=<p class="spoiler-tip">)[\s\S]*?(?=</p>)', m).group())#在title中查找是否含有剧透提示
            except AttributeError:
                if_spoiler.append('')
            full_comment_html = html_get('https://movie.douban.com/j/review/' + re.search(r'(?<=<div data-cid=")\d*?(?=">)', m).group() + '/full')
            if err != 0:
                break
            comments_temp = re.search(r'(?<="html":")[\s\S]*?(?="})', full_comment_html).group()
            comments.append(re.sub(r'(<[\s\S]*?>)|(\\n)|(&nbsp;)|(\n)', ' ', comments_temp))

        #写入数据
        for b in range(len(all_information)):
            pen.writerow({'页面网址':url,
                          'id':user_id[b],
                          '用户LINK':user_adress[b],
                          'time':comment_time[b],
                          '星级':star[b],
                          '星级评价':star_discribe[b],
                          '有用':use[b],
                          '没用':useless[b],
                          '回应':responses[b],
                          '单篇页面网址':comment_adress[b],
                          '页面标题':comment_title[b],
                          '剧透':if_spoiler[b],
                          '内容':comments[b]
                          })

        page = int(page)
        page += 20#翻页
    
    #异常判断
    if err != 0:
        break

    #爬取状态提示
    time_temp = t.time()
    print('现在已完成 ' + str((url_list.index(i)+1)) + ' 部电影影评的抓取。')
    print('用时：{:.2f}s。'.format(time_temp - time_start))
    print('\n')

print('已完成本次任务！正在写入数据。')
t.sleep(10)#保证前面的写入任务全部完成
datas.close()
print('用时：{:.2f}s。'.format(time_temp - time_start))
os.system('pause')