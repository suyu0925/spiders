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
