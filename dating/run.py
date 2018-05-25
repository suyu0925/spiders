import os
import requests
from bs4 import BeautifulSoup


base_url = 'http://www.xiangtw.com'
html_file = './data/index.html'


def main():
  for page in range(1, 11):
    girls = []
    # if not os.path.exists(html_file):
    if True:
      get = requests.get(base_url + '/Recommend/index.html?p={}'.format(page))
      with open(html_file, 'w') as f:
        f.write(str(get.content, 'utf-8', errors='ignore'))
      html = get.content
    else:
      with open(html_file, 'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'lxml')
    lis = soup.select('.searchm3 > ul > li')
    for li in lis:
      avatar_url = li.select('.searchm2left > a > img')[0].get('src')
      name = li.select('.searchm2right > .searchm2info > a')[0].get_text()
      gender = li.select('.searchm2right > .searchm2info')[
          1].get_text().replace('性别：', '')

      # 只要女性
      if gender == '女':
        girls.append({
            'avatar': base_url + avatar_url,
            'name': name,
            'gender': gender
        })

  # save girls
  with open('./data/girls.js', 'w') as f:
    f.write(str(girls))


if __name__ == "__main__":
  main()
