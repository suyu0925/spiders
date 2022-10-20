# JAV爬虫

## 爬取排名前50的女优以及作品

```bash
python main.py
```

## 指定爬取某个排行靠后的女优作品

```bash
scrapy crawl portfolio -a actress=宍戸翠蘭
scrapy crawl movie -a actress=宍戸翠蘭
scrapy crawl magnet
```

## 输出磁力链接

输出磁力链接到文件

```bash
python 115.py 宍戸翠蘭
```

可以指定时间起点，比如2021-04-19之后逢見リカ的影片：
```bash
python 115.py 宍戸翠蘭 2020-12-22
```

也可以直接输出具体某个番号
```bash
python 115.py SSIS-116
```
