## 1024爬虫

自动下载1024上“新时代的我们”子版块下的帖子中的图片。下载完成后放在data目录下。

使用语言为node或python。

### 网络环境

需要翻墙，默认使用ss。代理设置详见run.py中的proxies。

### 运行

**node**

首先需要安装node和yarn。

```bash
yarn
yarn start
```

**python**

依赖requests库和requests[socks]库。

```bash
pip install requests
pip install -U requests[socks]
```

```bash
python run.py
```
