###--------------
### 处理比较不同阶段LDAtopic的情感变化
###--------------
from tools.Mysql_Process import mysqlHelper
from tools.Mysql_Process import get_db
import pandas as pd


###比较不同阶段LDAtopic的情感变化
def stage_LDAtopic_emo_comp():
    ##连接mysql数据库
    try:
        mh = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
        # mh.open()
    except Exception as e:
        print(e)
    # 时间段
    date_list=['2021年06月22日 00:00', '2021年07月22日 00:00', '2021年08月03日 00:00', '2021年08月17日 00:00','2021年09月09日 23:59']
    # 建立字典存放四个阶段七个话题的三个感情统计
    caldict1 = {'0':{'0':0,'1':0,'2':0}, '1':{'0':0,'1':0,'2':0},'2':{'0':0,'1':0,'2':0},
               '3':{'0':0,'1':0,'2':0},'4':{'0':0,'1':0,'2':0},
               '5':{'0':0,'1':0,'2':0},'6':{'0':0,'1':0,'2':0},'7':{'0':0,'1':0,'2':0}}
    caldict2 = {'0': {'0': 0, '1': 0, '2': 0}, '1': {'0': 0, '1': 0, '2': 0}, '2': {'0': 0, '1': 0, '2': 0},
               '3': {'0': 0, '1': 0, '2': 0}, '4': {'0': 0, '1': 0, '2': 0},
               '5': {'0': 0, '1': 0, '2': 0}, '6': {'0': 0, '1': 0, '2': 0}, '7': {'0': 0, '1': 0, '2': 0}}
    caldict3 = {'0': {'0': 0, '1': 0, '2': 0}, '1': {'0': 0, '1': 0, '2': 0}, '2': {'0': 0, '1': 0, '2': 0},
               '3': {'0': 0, '1': 0, '2': 0}, '4': {'0': 0, '1': 0, '2': 0},
               '5': {'0': 0, '1': 0, '2': 0}, '6': {'0': 0, '1': 0, '2': 0}, '7': {'0': 0, '1': 0, '2': 0}}
    caldict4 = {'0': {'0': 0, '1': 0, '2': 0}, '1': {'0': 0, '1': 0, '2': 0}, '2': {'0': 0, '1': 0, '2': 0},
               '3': {'0': 0, '1': 0, '2': 0}, '4': {'0': 0, '1': 0, '2': 0},
               '5': {'0': 0, '1': 0, '2': 0}, '6': {'0': 0, '1': 0, '2': 0}, '7': {'0': 0, '1': 0, '2': 0}}
    stage_callist=[caldict1,caldict2,caldict3,caldict4]

    max_dict={'0':'0','1':'0','2':'0','3':'0','4':'0','5':'0','6':'0','7':'0'}
    max_lis =[]
    max_list=[max_lis,max_lis,max_lis,max_lis]

    ## 循环查询四个阶段
    for i in range(0,4):
        select_sql = "SELECT * FROM weibo.weibo_ldatopic where str_to_date(time,'%%Y年%%m月%%d日 %%H:%%i') " \
                 "between str_to_date(%s,'%%Y年%%m月%%d日 %%H:%%i') " \
                 "and str_to_date(%s,'%%Y年%%m月%%d日 %%H:%%i');"
        weibo_list = list(mh.findAll(select_sql,(date_list[i],date_list[i+1])))

        for w in weibo_list:
            topic=w[26]
            emo=w[17]
            stage_callist[i][topic][emo]=stage_callist[i][topic][emo]+1

        for t in stage_callist[i].keys():
            max_t = max(stage_callist[i][t], key=stage_callist[i][t].get)
            max_list[i].append(max_t)
            stage_callist[i][t]['max']=max_t
            n_p=stage_callist[i][t]['2']/(stage_callist[i][t]['0']+stage_callist[i][t]['1']+stage_callist[i][t]['2'])
            stage_callist[i][t]['n_p'] = n_p


    # for j in range(0,8):
    #     for i in range(0, 4):
    #         print('第'+str(i)+'阶段第'+str(j)+'个主题：')
    #         print(stage_callist[i][str(j)])
    #
    # for i in range(0, 4):
    #     print('第'+str(i)+'阶段：')
    #     print(max_list[i])

    file_save = '各阶段各主题情绪统计.xlsx'
    write_toxlsx(stage_callist,file_save)


## 导出为xlsx
def write_toxlsx(results,filename):

    dt = pd.DataFrame(results)
    dt.to_excel(filename, index=0)


def main():
    stage_LDAtopic_emo_comp()


main()