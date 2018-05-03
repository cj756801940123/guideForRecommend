#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import jieba
import jieba.analyse
import re
from gensim.models import Word2Vec,word2vec
from gensim import corpora, models, similarities
from Recommender.handler import database_util
from Recommender.handler import file_util

file_path = (os.path.dirname(os.path.abspath("similarity_util.py")) + '/Recommender/data/').replace('\\', '/')

#根据topK words 找出跟这些词最接近的词汇
def get_similar_type(keywords):
    tables = ['眼','唇','口','香水','底妆']
    # sentences = word2vec.Text8Corpus(file_path+"train_files/descriptions.txt")
    # model = Word2Vec(sentences, size=1000)
    # model.save(file_path+"train_files/trained.model")
    model = Word2Vec.load(file_path+"train_files/trained.model")
    max = 0
    type = ''
    try:
        for i in tables:
            similarity = model.similarity(i,keywords)
            if similarity>max:
                type = i
                max = similarity
        print(type,max)
    except Exception as err:
        return ['product_lipstick','product_eye','product_perfume', 'product_baseMakeup','product_other_perfume']

    if type=='眼':
        return ['product_eye']
    elif type=='唇' or  type=='口':
        return ['product_lipstick']
    elif type=='香水':
        return ['product_perfume', 'product_other_perfume']
    else:
        return ['product_baseMakeup']

def get_words(relative_path):
    # 把停用词做成字典
    stop_words = {}
    file = open(file_path+relative_path, 'r',encoding='utf-8')
    for each_word in file:
        stop_words[each_word.strip()] = each_word.strip()
    file.close()
    return stop_words

def get_descriptions():
    # tables = ['product_lipstick']
    tables = ['product_lipstick', 'product_eye', 'product_perfume', 'product_baseMakeup', 'product_other_perfume']
    file_name = file_path + 'train_files/descriptions.txt'
    file = open(file_name, "w", encoding='utf-8')
    words_file = open(file_path+'train_files/description_words.txt', "w", encoding='utf-8')
    jieba.load_userdict(file_path+'train_files/dictionary.txt')
    jieba.analyse.set_stop_words(file_path + 'train_files/stop_words.txt')  # 去除停用词
    stop_words = get_words('train_files/stop_words.txt')
    dictionary = get_words('train_files/dictionary.txt')

    try:
        for i in tables:
            sql = 'select description from ' + i
            result = list(database_util.search_sql(sql, None))
            for desciprtin in result:
                if len(desciprtin[0])==0:
                    continue
                line = desciprtin[0].strip()
                cut_str = ' '.join(jieba.cut(line))
                file.write(cut_str + '\n')
                # print(desciprtin[0])
                # print(cut_str)

                line = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", "", line)
                word_List = list(jieba.cut(line))  # 用结巴分词，对每行内容进行分词
                outStr = ''
                for word in word_List:
                    if word not in stop_words and word not in dictionary:
                        outStr += word
                        outStr += ' '
                        words_file.write(word+ '\n')  # 将分词好的结果写入到输出文件
                print(outStr)

    except Exception as e:
        print("fail in get_description,err:" + str(e))
    finally:
        file.close()
        words_file.close()
    file_util.del_duplicate('train_files/descriptions.txt')
    file_util.del_duplicate('train_files/description_words.txt')

def get_brands():
    tables = ['product_lipstick', 'product_eye', 'product_perfume', 'product_baseMakeup', 'product_other_perfume']
    file = open(file_path+'train_files/brands.txt', "w", encoding='utf-8')
    brand1 = ''
    brand2 = ''
    try:
        for i in tables:
            sql = 'select brand from ' + i
            result = list(database_util.search_sql(sql, None))
            for j in result:
                if len(j[0]) == 0:
                    continue
                line = j[0].strip()
                if line.find('（')>=0:
                    brand1 = line.split('（')[0]
                    brand2 = line.split('（')[1]
                    brand2 = brand2.split('）')[0]
                file.write(brand1+ '\n'+brand2 + '\n')
                print(brand1,brand2)
    except Exception as e:
        print(e)
    finally:
        file.close()
    file_util.del_duplicate('train_files/brands.txt')
    add_to_dictionary( 'train_files/brands.txt', 'train_files/dictionary.txt')


def add_to_dictionary(in_file,out_file):
    in_file = open(file_path + in_file, "r", encoding='utf-8')
    out_file = open(file_path + out_file, "a", encoding='utf-8')
    try:
        for i in in_file:
                line = i.strip('\n')
                out_file.write(line + '\n')
    except Exception as e:
        print(e)
    in_file.close()
    out_file.close()

if __name__ == '__main__':
    keyword = '美宝莲'
    # keyword = '卡姿兰气垫'
    # file_util.del_duplicate(file_path+'train_files/description_words.txt')
    # add_to_dictionary('train_files/description_words.txt', 'train_files/dictionary.txt')
    # get_brands()
    file_util.del_duplicate('train_files/dictionary.txt')
    get_descriptions()
    get_similar_type(file_path, keyword)


# D:\ComputerScience\ProgramsOfPython\guideForRecommend\Recommender\data\train_files


