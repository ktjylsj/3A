# -*- coding: utf-8 -*-

import urllib.request
import json
from selenium import webdriver as wd
import pymysql
from lawcrawl.module2 import module2

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
'''
# db 접근
conn = pymysql.connect(host='223.194.46.68', user='guest', password='1q2w3e4r!', db='my_db', charset='utf8mb4')

'''
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
    file_name = os.path.join(os.path.dirname(__file__), path)
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

'''


# ------------------------------------------------------------------------------
def module1(keyword):

    print(keyword)
    # 네이버 검색 API를 이용하여 keyword에 대한 블로그 포스트 url 가져오기
    driver = wd.Chrome(executable_path='chromedriver.exe', options=options)
    client_id = "N2Zyz2JpfmOreXybO7bZ"
    client_secret = "gddzJjJd5a"
    encText = urllib.parse.quote(keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText + "&display=20"  # json 결과
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


    for i in range(0, 10):
        post_list = []
        post_list.append(contents[i])
        post_list.append(titles[i])
        post_list.append(text[i])
        module2(list)

    driver.close()  # 크롬 창 닫기
