import pandas as pd

filename=open('E:\研究生\项目\群组行为突发事件主题发现模型\风险+心智图谱\爬数据\标签数据\\3labels\data_labels.csv',encoding='utf-8')
all_data = pd.read_csv(filename, dtype=str,usecols = [0,5])

# 删除评论前后空格
all_data = all_data.applymap(lambda x: str(x).strip())

#随机抽取n条数据
# all_data=all_data.sample(n=800, random_state=1, axis=0)

# 打乱数据-shuffle
all_data = all_data.sample(frac=1).reset_index(drop=True)

# 划分数据集 可以计算一下8:1:1是
#训练集&&验证集-----训练使用
trainlen=int((len(all_data))*0.8)

train_data = all_data.iloc[:trainlen]
dev_data = all_data.iloc[trainlen+1:]
#测试集----预测使用
#test_data = all_data.iloc[720:]

# 对于训练模型时，BERT内部数据处理时，要求数据集不要表头
train_data.to_csv('./data/train.tsv', sep='\t', header=False, index=False)
dev_data.to_csv('./data/dev.tsv', sep='\t', header=False, index=False)

filename1=open('E:\研究生\项目\群组行为突发事件主题发现模型\风险+心智图谱\爬数据\标签数据\\3labels\\test.csv',encoding='utf-8')
test_data = pd.read_csv(filename1, dtype=str,usecols = [0,5])

# 删除评论前后空格
test_data = test_data.applymap(lambda x: str(x).strip())
test_data.to_csv('./data/test.tsv', sep='\t', header=False, index=False)
