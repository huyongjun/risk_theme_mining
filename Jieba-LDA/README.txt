##### Task Description #####
This model is an LDA subject classification model based on the data of Sina Weibo in China.

##### Operating Instructions #####
---- Environment ----
pycharm 2018
python 3.6

----Word segmentation----
Word segmentation by Jieba.

----LDA theme extraction----
Based on the jieba word segmentation in the second step, 
the files after word segmentation can be obtained. 
The LDA theme extraction is carried out below.
In the LDA model fitting step, the parameters to be modified are mainly num_topic and alpha. 
The former num_topic, namely the number of themes,
Keep trying by calling the perplexity function, picking the least confusing theme number as input,
The latter is generally taken as the reciprocal of the number of thmes, such as the number of 10, 0.1, generally smaller is better.

----Output----
Vocabulary and probability for each theme

