# sshs

[绅士会所](https://sshs.xyz)爬虫。

## 使用方法

先安装依赖：
```bash
pip install -r requirements.txt
```

在项目的根目录运行：
```bash
scrapy crawl monthly_collection
```

## 存储

默认将链接存储到本机的mongodb数据库中。详情请见[配置文件](./sshs/settings.py)。
