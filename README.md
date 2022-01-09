# Toy Project for Recommendation System
# Just for fun;  Don't be serious


## recommend_system
### 基于豆瓣的推荐系统
#### V2 基于协同过滤的推荐系统

##### TBD

#### V1 基于规则random推荐系统

> date: 2022-01-09  
> code: reommendrecommend_by_self_v1.py  
> 说人话：丐中丐版的推荐系统：  

##### 背景
目前豆瓣上的「想看」list，只有简单的按照「收藏时间」、「评分」、「标题」排序的功能，给豆瓣提了需求，豆瓣说收到以后也没有后文了；抱着“求人不如求己”的心态，自己手撸个脚本，根据自己的喜好来过滤筛选，实现充分的定制化（在下自己的代码，想咋折腾咋折腾）
![chat with douban pm](./rec_system/DouBan/figures/chat_log.png)

##### 方案
给定「账号id」和「cookies」，将账号id对应的「想看」list里的电影找出来，然后根据需求选择电影进行推荐
- 主要增加了以下几个过滤策略
  - 打分过滤：过滤小于x分的电影
  - 内容过滤：过滤掉非指定内容种类的电影，e.g.: 剧情，动画片，纪录片
  - 时长过滤：过滤掉时长大于阈值的电影（现在的电影都太长了， 动不动就两三个小时起步。。。）
  - 国家过滤：过滤掉非指定国家的电影

（还有很多乱七八糟的过滤条件其实都可以加入，但是预期后面通过协同过滤来做，不整这些没用的）

##### 使用方法
- 将浏览器中豆瓣的cookies copy出来放到本目录下的cookies文件中；
  - 为什么需要自己拷贝cookies：豆瓣有时候会出现验证码登录，如果采用selenium的爬虫方式，cost比较大，所以copy cookies是一个ROI更高的方式。 
- 执行命令：  
`python run.py --account_id 175455903 --topk 5 --rate 8.0 --duration 120 --country 美国 --content_type 剧情`
  - account_id: 豆瓣上给的id，很早以前的id应该是按照名字来的；后来的id是数字，可以去豆瓣的链接上找找，一般是people/后面的这一串数字
  - topk: 最后给推荐的个数
  - rate: 得分阈值，小于该阈值会被过滤掉
  - duration: 时长阈值，大于该阈值会被过滤掉
  - country: 不是这个country的电影会被过滤掉
  - content_type: 不是这个类型的电影会被过滤掉

##### 示例结果
用张老板的账号做个测2333

![张一鸣的](./rec_system/DouBan/figures/zym.png)


## spiders
这里只是一些爬虫的小脚本~  
For DouBan: python crawl\_comments.py && python data\_analyse.py  
For IMDB: python crawl\_comments.py && python data\_analyse.py ***.csv 100


