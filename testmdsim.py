#_*_ coding:utf-8 _*_
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from konlpy.tag import Okt


def find_sim():
    model_name = 'Devices_s1000_w5_w8.model'
    doc2vec_model = Doc2Vec.load(model_name)

    doc2vec_corpus = TaggedDocument(Okt().nouns(), 'input')
    doc2vec_model.train(doc2vec_corpus, total_examples=doc2vec_model.corpus_count, epochs=doc2vec_model.epochs)

    inferred_vector = doc2vec_model.infer_vector(doc2vec_corpus[doc_id].words)
    sims = doc2vec_model.docvecs.most_similar([inferred_vector], topn=4)
    for sim in sims:
        print(sim)
    print("*******************************************************************************************************")

