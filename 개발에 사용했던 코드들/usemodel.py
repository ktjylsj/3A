# -*- coding: utf-8 -*-

#_*_ coding:utf-8 _*_
import pymysql
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from konlpy.tag import Okt

okt = Okt()

# db 접근
conn = pymysql.connect(host='223.194.46.68', user='guest', password='1q2w3e4r!', db='my_db', charset='utf8mb4')

text = "지난번 발표소식을 전해드렸던 애플 아이폰11이 드디어 1차 출시국에 출시가 되었습니다. 사실 기존 X시리즈에서 XS시리즈로 넘어가며 변화가 그렇게 많지 않아 아쉬웠었는데요. 이번 11 또한 그렇습니다. 그렇다고 완전변화가 없는 것은 아닙니다. 아이폰11 같은경우에는 기존XR의 포지션을 그대로 물려받았습니다. 특히 가장 눈에 띄는 부분이 컬러풀한 색상입니다. 컬러는 블랙, 그린, 옐로, 퍼플, 레드, 화이트 이렇게 6가지 컬러를 가지고 있는데 그중에 오늘은 아이폰11 그린 컬러를 만나보도록 하겠습니다.  먼저 용량은 64GB 부터 시작을 합니다. 이전에도 용량에 대한 부분은 유저들의 큰 불만중에 하나였는데, 역시 동일합니다. 아이폰11의 경우 64GB, 128GB, 256GB의 용량을 선택할 수 있으며, 프로의 경우에는 64GB, 256GB, 512GB 용량을 선택할 수 있습니다. 제거 선택한 용량은 64GB입니다.  그럼 바로 개봉을 해봅니다. 개봉을 하니 바로 아이폰11 그린의 후면이 모습을 드러냅니다. 그린컬러는, 일반적인 그린컬러가 아닌 밝은 민트 컬러라고 생각을 하면되는데, 밝으면서도 아주 산뜻한 느낌을 줍니다.  사실 출시전부터 디자인에 대해 상당히 이슈였었는데요. 루머 그대로 나오는것을 보고는 상당히 놀랐습니다. 아직 케이스가 오지 않아서, 케이스를 장착했을때 모습이 궁금합니다. 오늘 아이폰11 그린 컬러 언박싱과 함께 간단하게 그 특징들 살펴보았는데요. 이번 아이폰11 스펙의 포인트가 카메라 인만큼~! 카메라 성능이 중요하고, 초광각사진이 아쉬웠던 분들은 이번 11시리즈는 아주 좋은 선택이 될것 같습니다. 감사합니다. "

contents = []
labels = []

# 전자기기 정보 수집
with conn.cursor() as cursor:
    sql = 'SELECT * FROM my_db.adtext'
    cursor.execute(sql)
    temp1 = cursor.fetchall()

# 내용과 레이블
for doc in temp1:
    labels.append(doc[2])

def find_sim():
    model_name = 'Devices_s1000_w5_w8_3.model'
    doc2vec_model = Doc2Vec.load(model_name)
    doc2vec_corpus = TaggedDocument(words=okt.nouns(text), tags='input')
    doc2vec_model.train([doc2vec_corpus], total_examples=doc2vec_model.corpus_count, epochs=doc2vec_model.epochs)
    
    inferred_vector = doc2vec_model.infer_vector(doc2vec_corpus.words)
    sims = doc2vec_model.docvecs.most_similar([inferred_vector], topn=5)
    # print(sims)
    for sim in sims:
        print(labels[int(sim[0])] + ', ' + str(sim[1]))
    print("*******************************************************************************************************")


find_sim()