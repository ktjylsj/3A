# -*- coding: utf-8 -*-

import urllib.request
import json
from selenium import webdriver as wd
import re
import os
import io
import pymysql
from PIL import Image  # pip install pillow
import pytesseract  # pip install pytesseract
import time
from urllib.request import HTTPError

jpg = re.compile(".png|.jpg")
ad = re.compile("저작권료|협찬|원고료|활동비|제공받아|지원받아|지급받아")#공시 지원금 때문에 지원금 뺌

# ------------------------------------------------------------------------------
# gpuless 옵션
options = wd.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# ------------------------------------------------------------------------------
# 정규표현식 컴파일
jpg = re.compile(".png|.jpg")
ad = re.compile("저작권료|협찬|원고료|활동비|제공받아|지원받아|지급받아") #공시 지원금 때문에 지원금 뺌

# db 접근
conn = pymysql.connect(host='223.194.46.68', user='guest', password='1q2w3e4r!', db='my_db', charset='utf8mb4')


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

def detect_text(path):
    file_name = os.path.join(os.path.dirname(__file__),path)
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    # print('Texts:')

    txt = ""
    for text in texts:
        txt = text.description
        # print(txt)
        break

    if ad.search(txt):
        return True
    else:
        return False

# ------------------------------------------------------------------------------
def findwordsim(keyword):
    # 해당 keyword를 이름으로 하는 디렉토리 생성
    # dirname = make_directory(l)

    print(keyword)
    # 네이버 검색 API를 이용하여 keyword에 대한 블로그 포스트 url 가져오기
    # driver = wd.Chrome(executable_path='chromedriver.exe')
    driver = wd.Chrome(executable_path='chromedriver.exe', options=options)
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
        # print(data['title'].replace("&quot;", ""))
        # print(data['link'])x
    # print(len(contents))
    # 각 url에 접속
    link = []
    text = []
    AON = []

    for url in contents:
        if 'naver' not in url:
            continue
        adimg = False
        # url의 이미지파일 가져오기
        driver.get(url)
        driver.get(driver.find_element_by_id('mainFrame').get_attribute('src'))
        ls = driver.find_element_by_id('postListBody')
        ls = ls.find_elements_by_css_selector('img')

        # .jpg파일애서 문자를 추출하여 광고 유무 확인
        adimg = False  # 광고이미지 유무
        # print(len(ls))
        # print(ls[len(ls) - 1].get_attribute('src'))
        save = './img.jpg'
        try:
            urllib.request.urlretrieve(ls[len(ls) - 1].get_attribute('src'), save)
        except HTTPError as e:
            print(e)
        except:
            print("")
        else:
            adimg = detect_text('img.jpg')
            # print(adimg)
            os.remove('./img.jpg')

        # url 링크와 본문내용, 광고유무 저장(광고이미지가 없는 경우 본문에서 광고키워드가 있는지 확인 후 저장)
        link.append(url)  # 블로그 링크 저장
        driver.get(url)
        driver.get(driver.find_element_by_id('mainFrame').get_attribute('src'))

        # url에서 본문텍스트만 추출하여 text[]에 저장
        try:
            driver.get(driver.find_element_by_id('mainFrame').get_attribute('src'))
        except:
            print()

            # url에서 본문텍스트만 추출하여 text[]에 저장
        txt = driver.find_element_by_id('postListBody').text
        txt = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '', txt)
        text.append(txt)  # 블로그 내용 저장
        if adimg == False:
            if ad.search(txt):
                AON.append('A')  # 광고
            else:
                AON.append('NA')  # 광고 아님
        else:
            AON.append('A')
            
    # 모든 링크, 본문, 광고유무를 데이터베이스에 저장. 각 사용자마다 데이터베이스명 다름 주의
    for i in range(0, len(text)):
        with conn.cursor() as cursor:
            sql = 'INSERT INTO my_db.adtext (name, contents, AON, keyword) VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (link[i], text[i], AON[i], keyword))
        conn.commit()
        
    driver.close()  # 크롬 창 닫기


# ------------------------------------------------------------------------------
if __name__ == "__main__":  # main함수
    li = ['아이폰XR', '아이폰XS', '아이폰X', '노트10', '노트9', '노트8', 's10', 's9', 's8']  # 검색 keyword list '아이폰XR', '아이폰XS', '아이폰X', '아이폰SE', '아이폰8', '아이폰8 플러스','아이폰6',  , '아이폰5', '아이폰5s' '갤럭시 노트10'

    for l in li:
        start = time.time()
        findwordsim(l)
        end = time.time()
        print("%.2f초\n" % (end - start))

    '''
    start = time.time()
    findwordsim('노트9')
    end = time.time()
    print("%.2f초\n" % (end - start))'''
