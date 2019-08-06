import requests
import sys
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from itertools import count
from collections import OrderedDict
import os



All_list_url = 'http://comic.naver.com/webtoon/creation.nhn'
html = requests.get(All_list_url).text
soup = BeautifulSoup(html, 'html.parser')
webtoon_dict = {}

for thumbnail_tag in soup.select('div.thumb a'):
    url = thumbnail_tag['href']
    title = thumbnail_tag['title']
    match = re.search(r'\d+', url)
    if match:
        url_id = match.group()
    else:
        url_id = None

    webtoon_dict[title] = url_id


def get_naver_webtoon_url(title_id):

        url = 'http://comic.naver.com/webtoon/list.nhn'

        ep_dict = OrderedDict()

        for page in count(1):

            params = {
                'titleId': title_id,
                'page': page,
            }
            # print('try {}'.format(params))

            html = requests.get(url, params=params).text
            soup = BeautifulSoup(html, 'html.parser')

            for tag in soup.select('.viewList tr'):
                try:
                    a_tag = tag.select('a[href*=/webtoon/detail.nhn]')[0]
                except IndexError:
                    continue

                is_up = bool(tag.select('img[src*=ico_toonup]'))
                img_tag = a_tag.find('img')

                ep_url = urljoin(url, a_tag['href'])
                ep_name = img_tag['title']
                img_url = img_tag['src']

                if ep_url in ep_dict:
                    return ep_dict

                ep = {
                    'url': ep_url,
                    'name': ep_name,
                    'img_url': img_url,
                    'is_up': is_up,
                }
                ep_dict[ep_url] = ep


def ep_download(ep_url):
    img_path_list = []

    html = requests.get(ep_url).text
    soup = BeautifulSoup(html, 'html.parser')
    webtoon_name = ' '.join(soup.select('.comicinfo .detail h2')[0].text.split())
    ep_title = soup.select('.tit_area h3')[0].text

    for tag in soup.select('.wt_viewer img'):
        img_url = tag['src']

        headers = {
            'Referer': 'http://comic.naver.com/webtoon/list.nhn?titleId=697656&weekday=sun&page=4',
        }

        img_name = os.path.basename(img_url)
        img_path = os.path.join(webtoon_name, ep_title, img_name)
        img_path_list.append(img_path)

        # 부모의 경로
        dir_path = os.path.dirname(img_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        if not os.path.exists(img_path):
            img_data = requests.get(img_url, headers=headers).content
            print(img_path)
            with open(img_path, 'wb') as f:
                f.write(img_data)
        else:
            # print('SKIP')
            continue

    return img_path_list





#img_path_list = []


if __name__ == "__main__":
    line = sys.argv[1:]
    line = " ".join(line)
    print(line)
    if line == 'list':
        webtoon_list = list(webtoon_dict.keys())

        webtoon_list.sort()

        for webtoon in webtoon_list:
            print(webtoon)
        print('..총 {}작품'.format(len(webtoon_dict)))

    else:
        webtoon_url_list = get_naver_webtoon_url(webtoon_dict[line])
        print('download...{} episodes'.format(len(webtoon_url_list)))

        for url_list in webtoon_url_list:
            ep_download(url_list)

#검색 기능까지 구현해볼것
#이미지를 합치는 기능을 옵션으로 구현한다
#pip install을 집어넣고 실행 파일로 배포