import pymysql
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from konlpy.tag import Okt
import time

okt = Okt()

# db 접근
conn = pymysql.connect(host='223.194.46.68', user='guest', password='1q2w3e4r!', db='my_db', charset='utf8mb4')

contents = []
labels = []

# 전자기기 정보 수집
with conn.cursor() as cursor:
    sql = 'SELECT * FROM my_db.adtext'
    cursor.execute(sql)
    temp1 = cursor.fetchall()

# 내용과 레이블
for doc in temp1:
    contents.append(doc[1])
    labels.append(doc[2])


class Doc2VecCorpus:
    def __iter__(self):
        for i in range(0, len(contents)):
            # print(i)
            yield TaggedDocument(
                words=okt.nouns(contents[i]),
                tags=labels[i])


doc2vec_corpus = Doc2VecCorpus()

start = time.time()
doc2vec_model = Doc2Vec(doc2vec_corpus, vector_size=1000, window=5, workers=8, dbow_words=1, dm=0, seed=1234, min_alpha=0.025, negative=10)
end = time.time()
print("During Time: {}".format(end-start))

model_name = 'Devices_s1000_w5_w8.model'
doc2vec_model.save(model_name)
