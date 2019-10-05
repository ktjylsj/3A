# -*- coding: utf-8 -*-

import urllib.request
import json
from selenium import webdriver as wd
import pymysql
import module2
import time

# ------------------------------------------------------------------------------
# gpuless 옵션
options = wd.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
'''
# ------------------------------------------------------------------------------
# 정규표현식 컴파일
jpg = re.compile(".png|.jpg")
ad = re.compile("저작권료|협찬|원고료|활동비|제공받아|지원받아|지급받아")  # 공시 지원금 때문에 지원금 뺌

# db 접근
conn = pymysql.connect(host='223.194.46.68', user='guest', password='1q2w3e4r!', db='my_db', charset='utf8mb4')
'''
# ------------------------------------------------------------------------------
def module1(keyword):
    start = time.time()
    print(keyword)
    # 네이버 검색 API를 이용하여 keyword에 대한 블로그 포스트 url 가져오기
    driver = wd.Chrome(executable_path='chromedriver.exe', options=options)
    client_id = "N2Zyz2JpfmOreXybO7bZ"
    client_secret = "gddzJjJd5a"
    encText = urllib.parse.quote(keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText + "&display=12"  # json 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
    else:
        print("Error Code:" + rescode)

    # 각 post의 제목과 url을 각각 list에 저장
    titles = []
    contents = []
    json_data = response_body.decode("utf-8")  # ["bloggername"]
    json_parsing = json.loads(json_data)['items']
    i = 0
    for data in json_parsing:
        temp = data['title'].replace("&quot;", "")
        temp = temp.replace("<b>", "")
        temp = temp.replace("</b>", "")
        titles.append(temp)
        contents.append(data['link'])

    # 각 url에 접속
    link = []
    text = []
    result = []
    for url in contents:
        if 'naver' not in url:
            continue
        # url 링크와 본문내용, 광고유무 저장(광고이미지가 없는 경우 본문에서 광고키워드가 있는지 확인 후 저장)
        link.append(url)  # 블로그 링크 저장
        driver.get(url)
        # url에서 본문텍스트만 추출하여 text[]에 저장
        try:
            driver.get(driver.find_element_by_id('mainFrame').get_attribute('src'))
        except:
            print()
        txt = driver.find_element_by_id('postListBody').text
        text.append(txt)


    for i in range(len(text)):
        post_list = []
        post_list.append(contents[i])
        post_list.append(titles[i])
        post_list.append(text[i])
        result.append(module2.module2(post_list))
        print(i)

    driver.close()  # 크롬 창 닫기
    end = time.time()
    print("%.2f초\n" % (end - start))
    return result
