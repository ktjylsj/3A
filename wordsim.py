# -*- coding: utf-8 -*-

import urllib.request
import json
from selenium import webdriver as wd
import re
import os
import pymysql
from PIL import Image  # pip install pillow
import pytesseract  # pip install pytesseract
import time

# ------------------------------------------------------------------------------
# 정규표현식 컴파일
jpg = re.compile(".png|.jpg")
ad = re.compile("저작권료|지원금|협찬")

# db 접근, 각 사용자마다 password와 db명 다름 주의
conn = pymysql.connect(host='localhost', user='root', password='20150303jj', db='mydb', charset='utf8mb4')


# ------------------------------------------------------------------------------
def make_directory(main_dir):  # 결과파일 저장할 디렉토리 생성
    main_dir = './' + main_dir
    if not os.path.isdir(main_dir):  # 폴더가 존재하는지 확인
        os.mkdir(main_dir)  # 없으면 파일을 저장할 폴더 생성
    return main_dir


# ------------------------------------------------------------------------------
def ocrToStr(fullPath, lang='eng'):  # 이미지에서 문자 추출
    img = Image.open(fullPath)  # 이미지 경로

    # 추출(이미지파일, 추출언어, 옵션)
    # preserve_interword_spaces : 단어 간격 옵션을 조절하면서 추출 정확도를 확인한다.
    # psm(페이지 세그먼트 모드 : 이미지 영역안에서 텍스트 추출 범위 모드)
    # psm 모드 : https://github.com/tesseract-ocr/tesseract/wiki/Command-Line-Usage
    outText = pytesseract.image_to_string(img, lang=lang, config='--psm 1 -c preserve_interword_spaces=1')

    if ad.search(outText):
        return True
    else:
        return False


# ------------------------------------------------------------------------------
def findwordsim(keyword):
    # 해당 keyword를 이름으로 하는 디렉토리 생성
    dirname = make_directory(l)

    # 네이버 검색 API를 이용하여 keyword에 대한 블로그 포스트 url 가져오기
    driver = wd.Chrome(executable_path='chromedriver.exe')
    client_id = "N2Zyz2JpfmOreXybO7bZ"
    client_secret = "gddzJjJd5a"
    encText = urllib.parse.quote(keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText + "&display=10"  # json 결과
    # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText + "&display=5"  # xml 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        # print(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)

    # 각 post의 제목과 url을 각각 list에 저장
    titles = []
    contents = []
    json_data = response_body.decode("utf-8")  # ["bloggername"]
    # print(json_data)
    json_parsing = json.loads(json_data)['items']

    for data in json_parsing:
        titles.append(data['title'].replace("&quot;", ""))
        contents.append(data['link'])
        print(data['title'].replace("&quot;", ""))
        print(data['link'])

    # 각 url에 접속
    link = []
    text = []
    AON = []

    for url in contents:
        # url의 이미지파일 가져오기
        driver.get(url)
        driver.get(driver.find_element_by_id('mainFrame').get_attribute('src'))
        ls = driver.find_elements_by_css_selector('img')

        # .jpg파일애서 문자를 추출하여 광고 유무 확인
        idx = 0
        adimg = False  # 광고이미지 유무
        for li in ls:
            if jpg.search(li.get_attribute('src')):
                idx += 1
                u = li.get_attribute('src')
                save = dirname + '/' + str(idx) + '.jpg'
                urllib.request.urlretrieve(u, save)
                adimg = ocrToStr(save, 'kor+eng')  # 이미지가 광고인지아닌지 확인 결과 저장
                if (adimg == True):  # 광고이미지 발견
                    break  # 빼박 광고이므로 해당 url에서 더 볼거 없음

        # url 링크와 본문내용, 광고유무 저장(광고이미지가 없는 경우 본문에서 광고키워드가 있는지 확인 후 저장)
        link.append(url)  # 블로그 링크 저장

        driver.get(url)
        driver.get(driver.find_element_by_id('mainFrame').get_attribute('src'))

        # url에서 본문텍스트만 추출하여 text[]에 저장
        try:
            txt = driver.find_element_by_class_name('se-main-container').text
        except:
            txt = driver.find_element_by_id('postViewArea').text

        text.append(txt)  # 블로그 내용 저장

        # 광고이미지 유무에 따라 본문에서도 광고 키워드 확인
        if (adimg == True):  # 광고이미지가 있음
            AON.append('A')  # 광고

        else:  # 광고이미지가 없음
            if ad.search(txt):
                AON.append('A')  # 광고
            else:
                AON.append('NA')  # 광고 아님

    driver.close()  # 크롬 창 닫기

    # 모든 링크, 본문, 광고유무를 데이터베이스에 저장. 각 사용자마다 데이터베이스명 다름 주의
    for i in range(len(AON)):
        with conn.cursor() as cursor:
            sql = 'INSERT INTO mydb.adtext (name, contents, AON, keyword) VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (link[i], text[i], AON[i], keyword))
        conn.commit()


# ------------------------------------------------------------------------------
if __name__ == "__main__":  # main함수
    li = ['노트10', '아이폰XS']  # 검색 keyword list

    for l in li:
        start = time.time()
        findwordsim(l)
        end = time.time()
        print("%.2f초\n" % (end - start))
