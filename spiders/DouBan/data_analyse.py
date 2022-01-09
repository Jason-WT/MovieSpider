import pandas as pd
import numpy as np
import jieba
import matplotlib.pyplot as plt
import collections
from wordcloud import WordCloud
import zhon.hanzi
import string
import re
from snownlp import SnowNLP

jieba.enable_paddle()

class DataAnalyse:
    def __init__(self, path):
        self.path = path
        self.res = None
        self.rate2comment = None
        self.rate2count = None
        self._get_comment_info()
        self.stop_words = []
        self.punctuation = zhon.hanzi.punctuation + string.punctuation
        self._load_stop_words()

    def _load_stop_words(self, path="../utils/all_stopwords.txt"):
        lines = open(path, 'r', encoding='utf-8').readlines()
        for line in lines:
            self.stop_words.append(line.strip())
     
    def _get_comment_info(self):
        df = pd.read_csv(self.path, encoding='utf-8')
        res = []
        for index, row in df.iterrows():
            time, rate, content = row['times'], row['rates'], row['contents']
            try:
                rate = int(rate)
            except Exception as e:
                continue
            res.append((time, rate, content.strip()))
        self.res = sorted(res, key=lambda x: x[1], reverse=True)
        return
    
    def _filter(self, word):
        word = word.strip()
        word = re.sub("[%s]" % "".join(zhon.hanzi.punctuation + string.punctuation), "", word)
        if word in self.stop_words or word in self.punctuation:
            return True
        if word == " " or word == "":
            return True
        return False
    
    def _parse_comments(self):
        rate2comment = {}
        rate2count = {}
        for item in self.res:
            rate = item[1]
            rate2count[rate] = rate2count.get(rate, 0) + 1
            if rate not in rate2comment:
                rate2comment[rate] = []
            comment = list(jieba.cut(item[2], use_paddle=True))
            new_comment = []
            for c in comment:
                if self._filter(c):
                    continue
                new_comment.append(c)
                
            rate2comment[rate] += list(new_comment)
            
        self.rate2comment = rate2comment
        self.rate2count = rate2count
    
    def analyse(self, rate_threshold, topk):
        self._parse_comments()
        self._plot_rate_bar()
        self._parse_sentiments(rate_threshold)
        self._draw_wordcloud(rate_threshold, topk)
    
    def _parse_sentiments(self, rate_threshold):
        ge_thres_sentiment = [0, 0]
        lt_thres_sentiment = [0, 0]
        for rate in range(1, rate_threshold):
            for word in self.rate2comment[rate]:
                word = SnowNLP(word)
                lt_thres_sentiment[0] += word.sentiments
                lt_thres_sentiment[1] += 1
        for rate in range(rate_threshold, 6):
            for word in self.rate2comment[rate]:
                word = SnowNLP(word)
                ge_thres_sentiment[0] += word.sentiments
                ge_thres_sentiment[1] += 1
        print("avg sentiments when rate >= %d is %.4f" % (rate_threshold, ge_thres_sentiment[0] / ge_thres_sentiment[1]))
        print("avg sentiments when rate < %d is %.4f" % (rate_threshold, lt_thres_sentiment[0] / lt_thres_sentiment[1]))
    
    def _plot_rate_bar(self):
        rates = []
        sum_rate = 0.0
        sum_count = 0.0
        for i in range(1, 6):
            rates.append(self.rate2count[i])
            sum_rate += i * self.rate2count[i]
            sum_count += self.rate2count[i]

        plt.title("rate-count distribution")
        plt.xlabel("rate")
        plt.ylabel("count")
        plt.bar(range(1, 6), rates)
        print("The avgerage rate is %.2f" % (sum_rate / sum_count))
        
    def _draw_wordcloud(self, rate_threshold, topk=30):
        
        def _generate_wc(d, file_name):
            greater_wordcloud = WordCloud(background_color="white",width=1000, height=860, margin=2, font_path="/System/Library/fonts/PingFang.ttc").fit_words(d)
            greater_wordcloud.to_file(file_name)

        def _filter_same_content(gt, lt):
            new_gt = {}
            new_lt = {}
            for key in gt.keys():
                if key not in lt.keys():
                    new_gt[key] = gt[key]
            for key in lt.keys():
                if key not in gt.keys():
                    new_lt[key] = lt[key]
            return new_gt, new_lt

        greater = []
        lower = []
        for k, v in self.rate2comment.items():
            if k >= rate_threshold:
                greater += v
            else:
                lower += v
        gt_wf = dict(collections.Counter(greater).most_common(topk))
        lt_wf = dict(collections.Counter(lower).most_common(topk))
        
        gt_wf, lt_wf = _filter_same_content(gt_wf, lt_wf)
#         print("gt", gt_wf)
#         print("lt", lt_wf)
        
        _generate_wc(gt_wf, 'figures/ge_%d_top_%d.png' % (rate_threshold, topk))
        _generate_wc(lt_wf, 'figures/lt_%d_top_%d.png' % (rate_threshold, topk))

if __name__ == "__main__":
    DA = DataAnalyse("data/the_bankers_douban.csv")
    DA.analyse(4, 100)
