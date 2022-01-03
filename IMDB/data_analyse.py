import pandas as pd
import numpy as np
import jieba
import matplotlib.pyplot as plt
import collections
from wordcloud import WordCloud
import string
import re
import spacy
import pytextrank
from summa import keywords
import sys
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
nltk.download('wordnet')
nltk.download('omw-1.4')

class DataAnalyse:
    def __init__(self, path):
        self.path = path
        self.res = None
        self.rate2comment = None
        self.rate2count = None
        self._get_comment_info()
        self.all_keywords = []
        # self.stop_words = []
        # self._load_stop_words()
        
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
                rate = 0
            res.append((time, rate, content.strip()))
        self.res = sorted(res, key=lambda x: x[1], reverse=True)
        return
    
    def _parse_comments(self):
        for time, rate, comment in self.res:
            keys = keywords.keywords(comment).split('\n')
            self.all_keywords += keys
     
    def analyse(self, topk):
        self._parse_comments()
        self._draw_wordcloud(topk)

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
        
    def _draw_wordcloud(self, topk=30):
        
        def _generate_wc(d, file_name):
            greater_wordcloud = WordCloud(background_color="white",width=1000, height=860, margin=2, font_path="/System/Library/fonts/PingFang.ttc").fit_words(d)
            greater_wordcloud.to_file(file_name)
        
        # stemmer = nltk.stem.porter.PorterStemmer()
        # stemmer = nltk.stem.SnowballStemmer("english")
        # self.all_keywords = [stemmer.stem(word) for word in self.all_keywords]
        all_syn_words = []
        for word in self.all_keywords:
            for syn in wordnet.synsets(word):
                for lm in syn.lemmas():
                    all_syn_words.append(lm.name())
        for word in all_syn_words:
            if word in self.all_keywords:
                self.all_keywords.remove(word)

        key_wf = dict(collections.Counter(self.all_keywords).most_common(topk))
        _generate_wc(key_wf, 'figures/%s_top_%d.png' % (self.path.split('.')[0], topk))

if __name__ == "__main__":
    file_name = sys.argv[1]
    topk = int(sys.argv[2])
    DA = DataAnalyse(file_name)
    DA.analyse(100)
