###--------------
### 处理计算不同阶段不同主题的风险感知
### 指标：1.网媒 ①网媒数量②微博数量③传播速度
###       2.网民 ①关注度 a转发量b评论量c点赞量 ②负面情感占比

###--------------


from tools.Mysql_Process import mysqlHelper
from tools.Mysql_Process import get_db
from openpyxl import load_workbook
import pandas as pd
import time


##计算不同阶段不同主题的风险感知
def cal_stage_topic_index():
    ## 读取weibo 负面情感占比列表
    ## TODO
    file_home = r'E:\研究生\项目\群组行为突发事件主题发现模型\风险+心智图谱\代码\话题微博情感处理py\各阶段各主题情绪统计.xlsx'
    wb = load_workbook(filename=file_home)
    sheet1 = wb.worksheets[0]
    # 获取表格所有行和列，两者都是可迭代的
    rows = sheet1.rows
    # 存储四个阶段七个主题情感列表
    stage_emo_list=[]
    for r in rows:
        if r[0].value=='0':
            continue
        t_list=[]
        for c in r:
            diction=eval(c.value)
            t_list.append(diction['n_p'])
        stage_emo_list.append(t_list)

    print(stage_emo_list)

    ##连接mysql数据库
    try:
        mh = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
        # mh.open()
    except Exception as e:
        print(e)

    # 时间段
    date_list = ['2021年06月22日 00:00', '2021年07月22日 00:00', '2021年08月03日 00:00', '2021年08月17日 00:00',
                 '2021年09月09日 23:59']

    media_num_list=[]
    weibo_num_list=[]
    day_list=[]
    media_rate_list=[]
    search_hot_list=[]
    transmit_num_list=[]
    comment_num_list=[]
    like_num_list=[]
    ## 循环查询四个阶段的微博
    for i in range(0, 4):
        # 网媒数量
        media_num=[0,0,0,0,0,0,0,0]
        # weibo数量
        weibo_num=[0,0,0,0,0,0,0,0]
        # 主题持续天数
        day=[0,0,0,0,0,0,0,0]
        # 传播速度
        media_rate=[0,0,0,0,0,0,0,0]
        # 主题热搜热度指数=weibo所属话题的热度（不重复）
        search_hot=[0,0,0,0,0,0,0,0]
        # 主题热搜
        seach={'0':[],'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[]}
        # 主题下微博转发总数
        transmit_num=[0,0,0,0,0,0,0,0]
        # 主题下微博评论总数
        comment_num=[0,0,0,0,0,0,0,0]
        # 主题下微博点赞总数
        like_num=[0,0,0,0,0,0,0,0]
        # 主题负面情感占比
        n_emo_p_list=stage_emo_list[i]

        ## 查询网媒数量
        for t in range(0,8):
            select_sql="SELECT count(distinct (name)) FROM weibo.weibo_ldatopic where str_to_date(time,'%%Y年%%m月%%d日 %%H:%%i') " \
                     "between str_to_date(%s,'%%Y年%%m月%%d日 %%H:%%i') " \
                     "and str_to_date(%s,'%%Y年%%m月%%d日 %%H:%%i')" \
                       "and topic_maxp=%s" \
                       "and (pro_weibo_label='0' or pro_weibo_label='2');"
            result = mh.findAll(select_sql, (date_list[i], date_list[i + 1],str(t)))
            media_num[t]=result[0][0]

        ## 查询主题持续天数
        for t in range(0,8):
            select_sql="SELECT datediff(max(str_to_date(time, '%%Y年%%m月%%d日 %%H:%%i')), min(str_to_date(time, '%%Y年%%m月%%d日 %%H:%%i')))" \
                       " FROM weibo.weibo_ldatopic where str_to_date(time,'%%Y年%%m月%%d日 %%H:%%i') " \
                     "between str_to_date(%s,'%%Y年%%m月%%d日 %%H:%%i') " \
                     "and str_to_date(%s,'%%Y年%%m月%%d日 %%H:%%i')" \
                       "and topic_maxp=%s" \
                       "and (pro_weibo_label='0' or pro_weibo_label='2');"
            result= mh.findAll(select_sql, (date_list[i], date_list[i + 1],str(t)))
            day[t]=result[0][0]


        ## 查询微博列表（分阶段，不分主题）
        select_sql = "SELECT * FROM weibo.weibo_ldatopic where str_to_date(time,'%%Y年%%m月%%d日 %%H:%%i') " \
                     "between str_to_date(%s,'%%Y年%%m月%%d日 %%H:%%i') " \
                     "and str_to_date(%s,'%%Y年%%m月%%d日 %%H:%%i')" \
                     "and (pro_weibo_label='0' or pro_weibo_label='2');"
        weibo_list = list(mh.findAll(select_sql, (date_list[i], date_list[i + 1])))

        ## 遍历微博列表
        for w in weibo_list:
            topic_no = int(w[26])
            weibo_num[topic_no]=weibo_num[topic_no]+1
            if (w[6]!='') and (w[6]!='转发'):
                transmit_num[topic_no]=transmit_num[topic_no]+int(w[6])
            if (w[2]!='') and (w[2]!=' 评论'):
                comment_num[topic_no]=comment_num[topic_no]+int(w[2])
            if (w[3]!='') and (w[3]!='赞'):
                like_num[topic_no] = like_num[topic_no] + int(w[3])
            if (w[9]!='') and (w[9]!='topic_id'):
                if seach[str(topic_no)].count(w[9])==0:
                    select_sql = "SELECT hot_value FROM weibo.hot_topic where topic_id=%s;"
                    hot_value = mh.findAll(select_sql, str(w[9]))
                    seach[str(topic_no)].append(str(w[9]))
                    search_hot[topic_no]=search_hot[topic_no]+int(hot_value[0][0])

        ## 计算传播速度=转发量/天数
        for t in range(0,8):
            if day[t]!=0:
                media_rate[t]=transmit_num[t]/day[t]
            else:
                print('除数为0')

        media_num_list.append(media_num)
        weibo_num_list.append(weibo_num)
        day_list.append(day)
        media_rate_list.append(media_rate)
        search_hot_list.append(search_hot)
        transmit_num_list.append(transmit_num)
        comment_num_list.append(comment_num)
        like_num_list.append(like_num)

    print(media_num_list)
    print(weibo_num_list)
    print(day_list)
    print(media_rate_list)
    print(search_hot_list)
    print(transmit_num_list)
    print(comment_num_list)
    print(like_num_list)
    print(stage_emo_list)

    ## 指标输出为excel
    ## 风险感知各指标数值导出（7个指标，共4个阶段*8个话题=32行数据），作为spssau输入
    output_list=[]
    for i in range(0,4):
        for j in range(0,8):
            one_list = []
            ## 网媒数量
            one_list.append(media_num_list[i][j])
            ## weibo数量
            one_list .append(weibo_num_list[i][j])
            ## 传播速度
            one_list.append(media_rate_list[i][j])
            ## 热搜热度指数
            one_list.append(search_hot_list[i][j])
            ## 转发量
            # one_list.append(transmit_num_list[i][j])
            ## 评论量
            one_list.append(comment_num_list[i][j])
            ## 点赞量
            one_list.append(like_num_list[i][j])
            ## 负面情感占比
            one_list.append(stage_emo_list[i][j])
            output_list.append(one_list)

    write_toxlsx(output_list,filename='index_output'+str(int(time.time()))+'.xlsx')




    ###-----标准化处理-----
    media_num_list2 = []
    weibo_num_list2 = []
    media_rate_list2 = []
    transmit_num_list2 = []
    comment_num_list2 = []
    like_num_list2 = []
    stage_emo_list2=[]
    media_num_list3 = []
    weibo_num_list3 = []
    media_rate_list3 = []
    transmit_num_list3 = []
    comment_num_list3 = []
    like_num_list3 = []
    stage_emo_list3 = []
    # max_media_num = 0
    # max_weibo_num = 0
    # max_media_rate = 0
    # max_transmit_num = 0
    # max_comment_num = 0
    # max_like_num = 0
    # max_stage_emo = 0
    # min_media_num = 1000
    # min_weibo_num = 1000
    # min_media_rate = 1000
    # min_transmit_num = 1000
    # min_comment_num = 1000
    # min_like_num = 1000
    # min_stage_emo = 1000
    # for i in range(0,5):
    #     if max(media_num_list[i])>max_media_num:
    #         max_media_num=max(media_num_list[i])
    #     if max(weibo_num_list[i]) > max_weibo_num:
    #         max_weibo_num = max(weibo_num_list[i])
    #     if max(media_rate_list[i]) > max_media_rate:
    #         max_media_rate = max(media_rate_list[i])
    #     if max(transmit_num_list[i]) > max_transmit_num:
    #         max_transmit_num = max(transmit_num_list[i])
    #     if max(comment_num_list[i]) > max_comment_num:
    #         max_comment_num = max(comment_num_list[i])
    #     if max(like_num_list[i]) > max_like_num:
    #         max_like_num = max(like_num_list[i])
    #     if max(stage_emo_list[i]) > max_stage_emo:
    #         max_stage_emo = max(stage_emo_list[i])
    #
    #     if min(media_num_list[i])<min_media_num:
    #         min_media_num=min(media_num_list[i])
    #     if min(weibo_num_list[i]) < min_weibo_num:
    #         min_weibo_num = min(weibo_num_list[i])
    #     if min(media_rate_list[i]) < min_media_rate:
    #         min_media_rate = min(media_rate_list[i])
    #     if min(transmit_num_list[i]) < min_transmit_num:
    #         min_transmit_num = min(transmit_num_list[i])
    #     if min(comment_num_list[i]) < min_comment_num:
    #         max_comment_num = max(comment_num_list[i])
    #     if min(like_num_list[i]) < min_like_num:
    #         min_like_num = min(like_num_list[i])
    #     if min(stage_emo_list[i]) < min_stage_emo:
    #         min_stage_emo = min(stage_emo_list[i])

    # for i in range(0,4):
    #     for j in range(0,8):
    #         media_num_list2.append(media_num_list[i][j])
    #         weibo_num_list2 .append(weibo_num_list[i][j])
    #         media_rate_list2.append(media_rate_list[i][j])
    #         transmit_num_list2.append(transmit_num_list[i][j])
    #         comment_num_list2.append(comment_num_list[i][j])
    #         like_num_list2.append(like_num_list[i][j])
    #         stage_emo_list2.append(stage_emo_list[i][j])

    # max_media_num = max(media_num_list2)
    # max_weibo_num = max(weibo_num_list2)
    # max_media_rate = max(media_rate_list2)
    # max_transmit_num = max(transmit_num_list2)
    # max_comment_num = max(comment_num_list2)
    # max_like_num = max(like_num_list2)
    # max_stage_emo = max(stage_emo_list2)
    # min_media_num = min(media_num_list2)
    # min_weibo_num = min(weibo_num_list2)
    # min_media_rate = min(media_rate_list2)
    # min_transmit_num = min(transmit_num_list2)
    # min_comment_num = min(comment_num_list2)
    # min_like_num = min(like_num_list2)
    # min_stage_emo = min(stage_emo_list2)
    #
    # for i in media_num_list2:
    #     media_num_list3.append((max_media_num-i)/(max_media_num-min_media_num))
    # for i in weibo_num_list2:
    #     weibo_num_list3.append((max_weibo_num - i) / (max_weibo_num - min_weibo_num))
    # for i in media_rate_list2:
    #     media_rate_list3.append((max_media_rate-i)/(max_media_rate-min_media_rate))
    # for i in transmit_num_list2:
    #     transmit_num_list3.append((max_transmit_num-i)/(max_transmit_num-min_transmit_num))
    # for i in comment_num_list2:
    #     comment_num_list3.append((max_comment_num-i)/(max_comment_num-min_comment_num))
    # for i in like_num_list2:
    #     like_num_list3.append((max_like_num-i)/(max_like_num-min_like_num))
    # for i in stage_emo_list2:
    #     stage_emo_list3.append((max_stage_emo-i)/(max_stage_emo-min_stage_emo))
    #
    # print(media_num_list3)
    # print(weibo_num_list3)
    # print(media_rate_list3)
    # print(transmit_num_list3)
    # print(comment_num_list3)
    # print(like_num_list3)
    # print(stage_emo_list3)
    #



## 导出为xlsx
def write_toxlsx(results,filename):

    dt = pd.DataFrame(results)
    dt.to_excel(filename, index=0)


def main():
    cal_stage_topic_index()


main()