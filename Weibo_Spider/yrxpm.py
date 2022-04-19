import requests
from lxml import etree
from urllib import parse
import re
import configparser
import json
import pymysql.cursors
import re
from tools.Mysql_Process import mysqlHelper
from tools.Mysql_Process import get_db
import time
import random
import xlrd
from bs4 import BeautifulSoup

def clean_commenttext(text):
    # text = re.sub(r"\[\S+\]", "", text)      # 去除表情符号
    emotinlist=re.findall(r'\[\S+?\]',text)    #抓取表情
    if len(emotinlist)!=0:
        text = re.sub(r'\<span.\S*.alt=','',text)    #去除html元素，保留表情
        text = re.sub(r'.src\S*.\S*.\S*./></span>','',text)    #去除html元素，保留表情
    # text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
    # text = re.sub(r"#\S+#", "", text)      # 保留话题内容
    URL_REGEX = re.compile(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
        re.IGNORECASE)
    text = re.sub(URL_REGEX, "", text)       # 去除网址
    text = text.replace("转发微博", "")       # 去除无意义的词语
    text = re.sub(r"\s+", " ", text) # 合并正文中过多的空格
    return text.strip()

def get_data(id,page,headers):
    global all_comment_count
    ##-------手机端获取评论--------
    proxies = {
        "http": "http://27.159.191.144:4245",
        "https": "https://59.58.87.109:4213",
    }
    headers = headers
    #这里是手机端

    params = {
        'id':'1474005522114437',
        'page':'1',
    }
    params['id']=id
    params['page']=page
    response2 = requests.get('https://m.weibo.cn/api/comments/show', headers=headers,params=params)
    print("________________________________________________")
    # print(response2)
    ramdonnumber = random.randint(1, 2)
    time.sleep(ramdonnumber)
    print("________________________________________________")
    # if response2.status_code!=200:
    #     proxies=get_ip()
    #     response2 = requests.get('https://m.weibo.cn/api/comments/show', headers=headers, proxies=proxies,
    #                              params=params)

    print(len(response2.text))
    idcount = 0     ##用于存储评论id
    if(len(response2.text)!=3187 and page<5): ##TODO:更改每一个微博的评论页数限制
        html=json.loads(response2.text)
        ##-----wm修改
        mh = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
        mh.open()
        # db = pymysql.connect(host='127.0.0.1', user='root', password='3306', port=3306, db='weibo')
        # cursor = db.cursor()

        item2={}

        for i in html['data']['data']:
            # print(html['data']['data'])
            try:
              item2['weibo_id']=id
              # print('微博id')
              # print(id)
            except:
                item2['weibo_id'] = ''
            try:
              # print('时间')
              item2['created_at'] = i['created_at']
            except:
                item2['created_at'] = ''
            try:
              # print('评论用户id')
              item2['user_id'] = i['user']['id']
            except:
                item2['user_id'] = ''
            try:
              # print('点赞数')
              item2['like_counts'] = i['like_counts']
            except:
                item2['like_counts'] = ''
            try:
              # print('评论')
              item2['text'] = clean_commenttext(i['text'])
              # item2['text'] = i['text']
            except:
                item2['text'] = ''
            try:
              # print('名字')
              item2['name'] = i['user']['screen_name']
            except:
                item2['name'] = ''
            try:
                idcount=idcount+1
                item2['comment_id']=id + 'c' + str(idcount)
            except:
                item2['comment_id']=''
            # print(item2)
            print('---评论---')
            item2['emotion']=''
            #item2['text'] = clean_commenttext(item2['text'])
            sql=f"INSERT INTO `weibo`.`weibo_comment`(`weibo_id`,`created_at`,`user_id`,`like_counts`,`text`,`name`,`comment_id`,`emotion`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s' )"%(item2['weibo_id'],item2['created_at'],item2['user_id'],item2['like_counts'],item2['text'],item2['name'],item2['comment_id'],item2['emotion'])
            # print(sql)

            try :
                mh.open()
                mh.cud_withno_params(sql)
                mh.tijiao()
                print("---评论插入成功---！")
                all_comment_count = all_comment_count + 1
            except:
                print("----评论插入失败---"+sql)

            #cur.commit()
        mh.close()
        #         like_counts 喜欢 id 用户id
        get_data(id,page+1,headers)

if __name__ == '__main__':
    keywords = []  #TODO:话题列表
    ##---wm 读取话题列表
    readxlsx = xlrd.open_workbook(r'E:\研究生\项目\群组行为突发事件主题发现模型\风险+心智图谱\数据\热搜话题表.xlsx')
    sheet = readxlsx.sheet_by_name('Sheet12')  # 名字的方式
    nrows = sheet.nrows  # 行
    ncols = sheet.ncols  # 列
    for r in range(1, nrows):
        keywords.append(sheet.cell(r, 1).value)  # 获取i行2列的表格值

    headerlist = [{
    'authority': 's.weibo.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://s.weibo.com/weibo?q=%E5%86%B0%E5%A2%A9%E5%A2%A9',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'SINAGLOBAL=1125574285936.4727.1646133564409; ALF=1677669838; SUB=_2AkMVQouodcPxrAZXkfwRyW3nboxH-jyml-JeAn7uJhIyOhh77kpSqSVutBF-XCeKCUENlI3fYsBoQlJIjhJBgsR_; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhSfG5qDP4le31-E2WxeUe.5JpX5KzhUgL.Fo-c1KBXSKqfeo22dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMfSo.XSh-cSKzp; _s_tentry=s.weibo.com; Apache=6351148847862.829.1646134431983; ULV=1646134432155:2:2:2:6351148847862.829.1646134431983:1646133564413',
},{
    'authority': 's.weibo.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://s.weibo.com/weibo?q=%E6%96%B0%E5%86%A0%E7%97%85%E6%AF%92%E6%88%962019%E5%B9%B410%E6%9C%88%E5%8D%B3%E5%9C%A8%E6%AC%A7%E6%B4%B2%E4%BC%A0%E6%92%AD&sudaref=s.weibo.com',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'SINAGLOBAL=2073354087824.8147.1605254793719; _s_tentry=-; Apache=7093480315669.58.1646103910513; ULV=1646103910748:37:2:2:7093480315669.58.1646103910513:1646103789478; login_sid_t=efcf0c6dce17e664d8dc8387710d7b97; cross_origin_proto=SSL; appkey=; SSOLoginState=1646121960; UOR=,,login.sina.com.cn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhSfG5qDP4le31-E2WxeUe.5JpX5KMhUgL.Fo-c1KBXSKqfeo22dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMfSo.XSh-cSKzp; ALF=1677927267; SCF=AhcEDMbCHzMCHAPhMSHgBgxsUq7yA28LeA9VSNnhlbA2OBbijmIc6dU9Xadqk5WHtdXDInsoB7BydApuhAdyYLg.; SUB=_2A25PJZ-zDeRhGeNI4lYV9SjJyT2IHXVsUvZ7rDV8PUNbmtAKLRjwkW9NSAFXwYLXConLxBrwY8RxM0KmgWyCoAwT',
},{
    'authority': 's.weibo.com',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 SLBrowser/7.0.0.12151 SLBChan/8',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://s.weibo.com/weibo?q=%E5%86%B0%E5%A2%A9%E5%A2%A9',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'SINAGLOBAL=6025697794357.822.1603625748324; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5Jk2EJPY9xxi0yxieJNOX-5JpX5KMhUgL.Fo24e0qXS0z4ehz2dJLoI7USC-8lK.8W; ALF=1677901692; SSOLoginState=1646365692; SCF=AhIMU_NOJ_Dg02VG7-IkkeUmfdxFBw4El1Z5Px6P0_Rfwrq5y6l77F1UPY5kReVqJoVFHpivdxOzA_NElGbyQFA.; SUB=_2A25PJfutDeRhGedH6FQV9yzFyz6IHXVsU2plrDV8PUNbmtB-LWbMkW9NUL4D5Hl0X_ojqwYCVLX58U7PIBDFwY5t; _s_tentry=weibo.com; Apache=5925944579109.677.1646365706550; ULV=1646365707166:4:3:3:5925944579109.677.1646365706550:1646273107060',
}] #TODO:请求头列表
    ##1gjr；2wm；3ct
    header_index = 1

    all_topic_count = 0
    all_weibo_count = 0
    all_comment_count = 0

    for keyword in keywords: #遍历所有的话题，进行评论获取
        all_topic_count += 1

        print("正在爬取:《",keyword,"》话题信息=========================================================")
        # keyword= '新冠病毒或2019年10月即在欧洲传播'

        #-----------网页端获取热门微博内容-------------

        headers = headerlist[header_index]
        print("正在使用第{}个请求头".format(header_index + 1))
        ## 准备下一次的请求头
        temp_index = random.randint(0,len(headerlist)-1)
        while temp_index == header_index:
            temp_index = random.randint(0, len(headerlist)-1)
        header_index = temp_index


        # 获取话题页数
        params = {
            'q': '\u51B0\u58A9\u58A9',
            'xsort': 'hot',
            'suball':'1',
            'timescope':'custom:2021-06-22-0:2021-09-09-23',
            'Refer':'g',
            'page':'1',
        }#这里是翻页的

        params['q']=keyword
        response = requests.get('https://s.weibo.com/weibo', headers=headers, params=params, allow_redirects=False)
        # print(response.text)
        html=etree.HTML(response.text)
        # print(html.text)
        try:
            pages=html.xpath('//ul[@node-type="feed_list_page_morelist"]')
            # print(pages.find_elements_by_xpath('li'))
            pages_count = len(pages[0])
            print("当前话题有页数：",pages_count) #获取了页数
        except Exception as e :
            print(e)
            pages_count=1

        for page in range(1,pages_count+1): #TODO:遍历一个话题所有页
            # 获取当前页面：
            params['page'] = str(page)
            response = requests.get('https://s.weibo.com/weibo', headers=headers, params=params, allow_redirects=False)
            # print(response.text)
            html = etree.HTML(response.text)

            tree = html.xpath('//div[@action-type="feed_list_item"]')
            ##-----wm修改
            mh = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
            mh.open()
            ##查询话题序号
            # select_sql = "SELECT topic_id FROM hot_topic WHERE topic_name = %s"
            # result=list(mh.findAll(select_sql,keyword))
            # topic_id =result[0]

            # db = pymysql.connect(host='127.0.0.1', user='root', password='mingkemysql..', port=3306, db='positions_wb')
            # cursor = db.cursor()
            print("当前页面的微博数：",len(tree))

            for i in tree: ## TODO:一个话题内微博个数
                try:
                        item={}
                        #print(i.xpath('@mid'))
                        try:
                            item['id']=i.xpath('@mid')[0] #微博id
                        except:
                            item['id']=''
                        #print('名字')
                        try:
                            item['name']=i.xpath('.//a/@nick-name')[0] #用户名
                        except:
                            item['name']=''

                        #print('点赞')
                        try:
                            item['like']=i.xpath('.//span[@class="woo-like-count"]/text()')[0]
                        except:
                            item['like']=''
                        #print('评论数量')
                        try:
                            item['coment']=i.xpath('.//a[@action-data="pageid=weibo&suda-data=key%3Dtblog_search_weibo%26value%3Dweibo_h_1_p_p"]/text()')[0]
                        except:
                            item['coment']=''
                        #print('转发数量')
                        try:
                            item['transmit']=i.xpath('.//a[@action-type="feed_list_forward"]/text()')[1]
                        except:
                            item['transmit']=''

                        #print('微博文本')
                        try:
                            item['text']=''.join(i.xpath('.//p[@node-type="feed_list_content"]/text()'))
                            if (len(i.xpath('.//p[@node-type="feed_list_content_full"]/text()')))!=0:
                                item['text'] = ''.join(i.xpath('.//p[@node-type="feed_list_content_full"]/text()'))
                                ##----wm加上链接的文字
                                # item['text'] = item['text'] + ''.join(
                                #     i.xpath('.//p[@node-type="feed_list_content_full"]//a/text()'))
                            # else:
                            #     item['text'] = item['text'] + ''.join(i.xpath('.//p[@node-type="feed_list_content"]//a/text()'))
                            item['text']=item['text'].strip()
                            # print( item['text'])
                            print('----微博内容----')
                        except:
                            item['text']=''
                        # try:
                        #     item['text']=''.join(i.xpath('.//p[@node-type="feed_list_content"]/text()'))
                        #     try:
                        #         item['text'] = ''.join(i.xpath('.//p[@node-type="feed_list_content_full"]/text()'))
                        #     except:
                        #         pass
                        #     try:
                        #         item['text']= item['text']+''.join(i.xpath('.//p[@node-type="feed_list_content_full"]//a/text()'))
                        #     except:
                        #         pass
                        #     print( item['text'])
                        #     print('************')
                        # except:
                        #     item['text']=''
                        #print('时间')
                        try:
                            item['time']=i.xpath('.//div[@node-type="like"]/p[@class="from"]/a[1]/text()')[0].strip()
                        except:
                            item['time']=''
                        id=i.xpath('@mid')[0]
                        # print(item)
                        # print(i.xpath('.//div[@class="card-top"]//h4[@class="title"]/a[1]/@href'))
                        sql = f"INSERT INTO `weibo`.`hot_weibo`(`word`,`coment`,`like`,`weibo_id`,`text`,`name`,`transmit`,`time`) VALUES ('%s','%s','%s','%s','%s','%s', '%s', '%s')" % (
                            keyword, item['coment'], item['like'], item['id'], item['text'], item['name'], item['transmit'], item['time'])
                        # print(sql)
                        try:
                            mh.open()
                            mh.cud_withno_params(sql)
                            mh.tijiao()
                            print("----微博内容插入成功----！")
                            all_weibo_count = all_weibo_count + 1

                        except:
                            print("----微博内容插入失败----"+sql)
                        ramdonnumber = random.randint(1,2)
                        time.sleep(ramdonnumber)
                        #cur.commit()
                        mh.close()
                        get_data(id, 1,headers)
                        print('---一个微博爬完---')

                except Exception as e :
                    print(e)

        print("爬取的话题总数：",all_topic_count)
        print("爬取的微博总数：",all_weibo_count)
        print("爬取评论总数：",all_comment_count)
