import requests
import threading
import re
import os
import traceback


# 默认使用clash的7890端口
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

# 默认只下载第1页
DownloadPages = 1


class myThread (threading.Thread):  # 继承父类threading.Thread
    def __init__(self, url, dir, filename):
        threading.Thread.__init__(self)
        self.threadID = filename
        self.url = url
        self.dir = dir
        self.filename = filename

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        download_pic(self.url, self.dir, self.filename)


def download_pic(url, dir, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name', 'Referer': 'https://t66y.com'}
    # 下载图片通常无需代理，直连即可
    req = requests.get(url=url, headers=headers)
    if req.status_code == 200:
        with open(str(dir) + '/' + str(filename) + '.jpg', 'wb') as f:
            f.write(req.content)


try:
    flag = 1
    while flag <= DownloadPages:
        base_url = 'https://t66y.com/'
        page_url = 'https://t66y.com/thread0806.php?fid=8&search=&page=' + \
            str(flag)
        # 获取第flag页的html
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name', 'Referer': 'https://t66y.com'}
        get = requests.get(page_url, headers=headers, proxies=proxies)

        # 在第flag页中查找帖子标题的链接
        # <h3><a href="htm_data/8/1805/3152995.html" target="_blank" id="">Ashleigh[27P]</a></h3>
        article_url = re.findall(
            r'<h3><a href="(.*)" target="_blank" id="">(?!<.*>).*</a></h3>', str(get.content, 'gbk', errors='ignore'))

        for url in article_url:
            threads = []
            title = ['default']
            getpage = requests.get(
                str(base_url) + str(url), headers=headers,  proxies=proxies)

            # 获取帖子标题的文字
            title = re.findall(
                r'<h4>(.*)</h4>', str(getpage.content, 'gbk', errors='ignore'))
            # 使用标题当作目录名
            if len(title) == 0:
                print('can not match title in ', url)
                print('the content is ', str(
                    getpage.content, 'gbk', errors='ignore'))
                continue
            file = './data/' + title[0]
            if os.path.exists(file) == False:
                # 找出帖子中的图片地址
                img_url = re.findall(r'<input (data-link=\'(.*?)\' )?data-src=\'(.*?)\'',
                                     str(getpage.content, 'gbk', errors='ignore'))

                if img_url == None or len(img_url) == 0:
                    print(title[0] + '中没有图片，跳过')
                else:
                    os.makedirs(file)
                    filename = 1
                    print('开始下载：{}，共{}P'.format(file, len(img_url)))
                    for (data_link, link_url, download_url) in img_url:
                        # print('开始下载图片：' + download_url)
                        thread = myThread(download_url, file, filename)
                        thread.start()
                        threads.append(thread)
                        filename = filename + 1
                    downloaded = 0
                    for t in threads:
                        # 每张图片给30秒下载时间
                        t.join(30 * len(img_url))
                        downloaded += 1
                        print('下载进度{}/{}'.format(downloaded, len(img_url)))
                    print('下载完成，共' + str(filename) + '张图片')
            else:
                print('{}文件夹已存在，跳过'.format(title[0]))
        print('第' + str(flag) + '页下载完成')
        flag = flag + 1
except Exception as e:
    print('程序错误，退出')
    print(traceback.format_exc())
