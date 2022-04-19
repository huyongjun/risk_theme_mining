import numpy as np
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from gensim import corpora, models
import matplotlib.pyplot as plt
import math
import pandas as pd
import time


## 读取数据源
def get_data():
    data_list = []
    ##TODO:修改输入文件
    filename='fencioutput.txt'
    for line in open(filename, 'r', encoding='utf-8').readlines():
        # print(line)
        line=line.replace(' \u200b','')
        line = [word.strip() for word in line.split(' ')]
        data_list.append(line)  # list of list 格式
    print(data_list)
    return data_list

## 生成LDA模型
def creat_LDA(data_list,num_topics):
    # 把文章转换成list
    dictionary = Dictionary(data_list)
    # print(type(common_texts))
    # print(common_texts[0])
    # 把文本转换成词袋的形式  id：freq
    corpus = [dictionary.doc2bow(text) for text in data_list]
    corpora.MmCorpus.serialize('corpus.mm', corpus)
    # 控制主题数
    lda = LdaModel(corpus, id2word=dictionary, random_state=1,num_topics=num_topics)
    # # 预测：
    # bow_sample = [(370, 1)]  # 随便找一个样本
    # lda.get_document_topics(bow_sample)  # 预测
    # 预测结果：[(0, 0.2056313), (1, 0.2160506), (2, 0.5783181)]
    print("---LDA模型生成成功！---")
    ## 输出主题关键词xlsx
    topic_list = lda.print_topics(num_topics, 200)
    print(topic_list)
    write_toxlsx(topic_list, "topic_keyword"+str(int(time.time()))+".xlsx")
    # print(dictionary)
    return lda,dictionary


##计算困惑度perplexity，确定主题数量
def perplexity(ldamodel, testset, dictionary, size_dictionary, num_topics):
    print('the info of this ldamodel: \n')
    print('num of topics: %s' % num_topics)
    prep = 0.0
    prob_doc_sum = 0.0
    topic_word_list = []
    for topic_id in range(num_topics):
        topic_word = ldamodel.show_topic(topic_id, size_dictionary)
        # print('------------')
        # print(topic_word)
        dic = {}
        for word, probability in topic_word:
            dic[word] = probability
        topic_word_list.append(dic)
        # print('====================')
        # print(topic_word_list)

    doc_topics_ist = []
    for doc in testset:
        doc_topics_ist.append(ldamodel.get_document_topics(doc, minimum_probability=0))
    # print('****************')
    # print(doc_topics_ist)

    testset_word_num = 0
    for i in range(len(testset)):
        prob_doc = 0.0  # the probablity of the doc
        doc = testset[i]
        doc_word_num = 0
        for word_id, num in dict(doc).items():
            prob_word = 0.0
            doc_word_num += num
            word = dictionary[word_id]
            for topic_id in range(num_topics):
                # cal p(w) : p(w) = sumz(p(z)*p(w|z))
                prob_topic = doc_topics_ist[i][topic_id][1]
                prob_topic_word = topic_word_list[topic_id][word]
                prob_word += prob_topic * prob_topic_word
            prob_doc += math.log(prob_word)  # p(d) = sum(log(p(w)))
        prob_doc_sum += prob_doc
        testset_word_num += doc_word_num
    prep = math.exp(-prob_doc_sum / testset_word_num)  # perplexity = exp(-sum(p(d)/sum(Nd))
    print("模型困惑度的值为 : %s" % prep)
    return prep

## 画图
def graph_draw(topic, perplexity):  # 作主题数与困惑度的折线图
    x = topic
    y = perplexity
    plt.plot(x, y, color="red", linewidth=2)
    plt.xlabel("Number of Topic")
    plt.ylabel("Perplexity")
    plt.savefig("perplexity.png", dpi=300)
    plt.show()



##用困惑度确定主题数量
def main():
    data_list=get_data()
    a = range(1, 20, 1)  # 主题个数
    p = []
    for num_topics in a:
        lda, dictionary = creat_LDA(data_list,num_topics)
        corpus = corpora.MmCorpus('corpus.mm')
        testset = []
        for i in range(0,corpus.num_docs):
            testset.append(corpus[i])
        prep = perplexity(lda, testset, dictionary, len(dictionary.keys()), num_topics)
        p.append(prep)

    graph_draw(a, p)

##生成LDA模型并对现有weibo分类
def topic_predict(data_list,lda, dictionary,num_topics):

    # 把文章转换成list
    dictionary = Dictionary(data_list)
    # 把文本转换成词袋的形式  id：freq
    corpus = [dictionary.doc2bow(text) for text in data_list]
    # 预测：
    # 预测并打印结果
    topic_results=[]
    for i, item in enumerate(corpus):
        topic = lda.get_document_topics(item)
        topic_dic=dict(topic)
        topic_num=[0,1,2,3,4,5,6,7]
        ##插入p为0的话题
        for j in topic_num:
            if j not in topic_dic.keys():
                topic.insert(j,(j,0))
        ##找最大p值对应的话题编号
        max_p=max(topic_dic,key=topic_dic.get)
        # keys = target.keys()
        # print('================')
        # print('第', i + 1, '条记录:',data_list[i])
        # print('第', i + 1, '条记录分类结果:', topic)
        topic.append(str(max_p))
        topic_results.append(topic)

    write_toxlsx(topic_results,"topic_predict"+str(int(time.time()))+".xlsx")

## 导出为xlsx
def write_toxlsx(results,filename):

    dt = pd.DataFrame(results)
    dt.to_excel(filename, index=0)


##以最佳主题数生成LDA模型，并对文本进行分类，并输出到xlsx&&csv，（包含各类概率p，以及最高p的主题编号）
def main2():
    data_list = get_data()
    num_topics=8
    lda, dictionary = creat_LDA(data_list, num_topics)
    topic_predict(data_list,lda, dictionary,num_topics)



main()
# main2()