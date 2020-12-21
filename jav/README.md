# JAV爬虫

## 女优

爬取所有女优，存入数据库中

```bash
scrapy crawl actor
```

## 作品

爬取可下载作品

```bash
scrapy crawl film -a actor='波多野結衣'
```

## 磁力链接

爬取可下载作品的磁力链接

```bash
scrapy crawl magnet -a actor='波多野結衣'
```

## 输出磁力链接

输出磁力链接到文件，比如2020-04-19之后逢見リカ的影片：
```bash
python3 115.py 逢見リカ 2020-04-19
```
