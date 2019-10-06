# -*- coding: utf-8 -*-

# _*_ coding:utf-8 _*_
import pymysql
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from konlpy.tag import Okt
okt = Okt()
'''
# db 접근
conn = pymysql.connect(host='223.194.46.68', user='guest', password='1q2w3e4r!', db='my_db', charset='utf8mb4')

labels = []

# 전자기기 정보 수집
with conn.cursor() as cursor:
    sql = 'SELECT * FROM my_db.adtext'
    cursor.execute(sql)
    temp1 = cursor.fetchall()

# 내용과 레이블
for doc in temp1:
    labels.append(doc[2])

'''
def module2(blog):
    model_name = 'Devices_s1000_w5_w8_3.model'
    doc2vec_model = Doc2Vec.load(model_name)
    doc2vec_corpus = TaggedDocument(words=okt.nouns(blog[2]), tags='input')
    doc2vec_model.train([doc2vec_corpus], total_examples=doc2vec_model.corpus_count, epochs=doc2vec_model.epochs)

    inferred_vector = doc2vec_model.infer_vector(doc2vec_corpus.words)
    sims = doc2vec_model.docvecs.most_similar([inferred_vector], topn=1)

    for sim in sims:
        if sim[0] == 'NA':
            perc = 0
        else:
            perc = int(sim[1] * 100)
    
    result = [blog[0], blog[1], perc]
    print(result)
    return result