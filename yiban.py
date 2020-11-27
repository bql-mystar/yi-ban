import requests
from lxml import etree
import time
import re
import json


class YibanSpider:
    def __init__(self, Cookie, start_vote_url, student_list):
        '''
        :param Cookie: 需要先登录易班，然后按F12，获取对应的Cookir传入
        :param start_vote_url: 打开易班网页班，进入投票页面，点开更多，复制对应的网页即可
        '''
        self.url_prefix = 'https://www.yiban.cn'
        self.start_url = start_vote_url
        self.student_list = student_list
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            'Cookie': Cookie
        }

    def parse_url(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def get_voptions_id(self, params_dict):
        getVoptionsIdUrl = 'https://www.yiban.cn/vote/vote/getVoteDetail'
        getVoptionsData = {
            'vote_id': params_dict.get('vote_id'),
            'uid': params_dict.get('uid'),
            'puid': params_dict.get('puid'),
            'pagetype': params_dict.get('pagetype'),
            'group_id': params_dict.get('group_id'),
            'actor_id': params_dict.get('actor_id'),
            'top_power': params_dict.get('top_power'),
            'edit_power': params_dict.get('edit_power'),
            'end_power': params_dict.get('end_power'),
            'del_power': params_dict.get('del_power'),
            'block_power': params_dict.get('block_power'),
            'isSchoolVerify': params_dict.get('isSchoolVerify'),
            'is_public': params_dict.get('is_public'),
            'is_anonymous': params_dict.get('is_anonymous'),
            'token':params_dict.get('token'),
            'out_power': 'f',
            'isMember':'',
            'url[getVoteDetail]': 'vote/vote/getVoteDetail',
            'url[output]': '/vote/Expand/output',
            'url[getCommentDetail]': 'vote/vote/getCommentDetail',
            'url[addComment]': 'vote/vote/addComment',
            'url[editLove]': 'vote/vote/editLove',
            'url[vote]': 'vote/vote/act',
            'url[setIsTop]': 'vote/Expand/setIsTop',
            'url[setManualEndVote]': 'vote/Expand/setManualEndVote',
            'url[delVote]': 'vote/Expand/delVote',
            'url[delComment]': 'vote/vote/delComment',
            'url[shieldVote]': 'vote/Expand/shieldVote',
            'url[getAnonymous]': 'vote/Expand/getAnonymous',
            'url[userInfo]': 'user/index/index',
            'isLogin': '1',
            'isOrganization': '0',
            'ispublic': '0'
        }
        response = requests.post(getVoptionsIdUrl, headers=self.headers, data=getVoptionsData)
        ret = response.content.decode()
        ret = json.loads(ret)
        voptions_id_list = []
        option_id_list = ret.get('data').get('option_list')
        for option_id_dict in option_id_list:
            voptions_id_list.append(option_id_dict.get('id'))

        return voptions_id_list

    def get_total_params(self, detail_url):
        response = requests.get(detail_url, headers=self.headers)
        html_str = response.content.decode()
        ret = re.findall(r'<script>(.*?)</script>', html_str, re.S)[0] if len(re.findall(r'<script>(.*?)</script>', html_str, re.S)) > 0 else None
        ret = ret.split('g_config')[1]
        ret = ret.replace(' ', '')
        ret = ret[1:]
        ret = ret.split('out_power:')[0].replace(' ', '')
        ret = ret[1:-4]
        ret = ret.split(',')
        params_dict = {}
        params_dict['vote_id'] = ret[0].split(':')[1].replace('"','')
        params_dict['uid'] = ret[1].split(':')[1].replace('"','')
        params_dict['puid'] = ret[2].split(':')[1].replace('"','')
        params_dict['pagetype'] = ret[3].split(':')[1].replace('"','')
        params_dict['group_id'] = ret[4].split(':')[1].replace('"','')
        params_dict['actor_id'] = ret[5].split(':')[1].replace('"','')
        params_dict['top_power'] = ret[6].split(':')[1].replace('"','')
        params_dict['edit_power'] = ret[7].split(':')[1].replace('"','')
        params_dict['end_power'] = ret[8].split(':')[1].replace('"','')
        params_dict['del_power'] = ret[9].split(':')[1].replace('"','')
        params_dict['block_power'] = ret[10].split(':')[1].replace('"','')
        params_dict['isSchoolVerify'] = ret[11].split(':')[1].replace('"','')
        params_dict['is_public'] = ret[12].split(':')[1].replace('"','')
        params_dict['is_anonymous'] = ret[13].split(':')[1].replace('"','')
        params_dict['token'] = ret[14].split(':')[1].replace("'",'')

        return params_dict

    def distinguish_no_vote(self, vote_people_list):
        vote_people_list = set(vote_people_list)
        student_list = set(self.student_list)
        return list(student_list - vote_people_list)

    def run(self):
        while True:

            with open('no_vote_people.txt', 'w', encoding='utf-8') as f:
                for i in range(16):
                    request_url = self.start_url % (i+1)
                    # 发送请求，获取相应
                    html_str = self.parse_url(request_url)
                    # 获取本页对应的投票
                    html = etree.HTML(html_str)
                    # 获取每一条的投票
                    vote_list = html.xpath('//li[@class="topic-frame"]')
                    for vote in vote_list:
                        # 获取每个投票的详细信息
                        item = {}
                        title = vote.xpath('.//a[@target="_blank"]/text()')[0] if len(vote.xpath('.//a[@target="_blank"]/text()'))>0 else None
                        title = title.replace(' ', '')
                        title = title.replace('\r\n', '')
                        item['title'] = title
                        vote_detail_url = self .url_prefix + vote.xpath('.//a[@target="_blank"]/@href')[0] if len(vote.xpath('.//a[@target="_blank"]/@href'))>0 else None
                        params_dict = self.get_total_params(vote_detail_url)
                        voptions_id_list = self.get_voptions_id(params_dict)
                        vote_people_list = []
                        for voptions_id in voptions_id_list:
                            data = {
                               ' puid': params_dict.get('puid') ,
                                'vote_id': params_dict.get('vote_id'),
                                'group_id': params_dict.get('group_id'),
                                'voptions_id':voptions_id,
                                'actor_id': params_dict.get('actor_id'),
                                'page': 1,
                                'size': 40
                            }
                            response = requests.post('https://www.yiban.cn/vote/Expand/getAnonymous',headers=self.headers, data=data )
                            author_name_list = json.loads(response.content.decode()).get('data').get('list')
                            for author_name in author_name_list:
                                if author_name in vote_people_list:
                                    continue
                                vote_people_list.append(author_name.get('author_name'))

                            
                        # 返回未投票的人员名单
                        no_vote_people_list = self.distinguish_no_vote(vote_people_list)
                        # no_vote_people_list = [student for student in self.student_list if student not in vote_people_list]

                        item['no_vote_people_list'] = no_vote_people_list
                        
                        print(item)
                        f.write(json.dumps(item, ensure_ascii=False))
                        f.write('\n')
            print('已经检测完一次，先休眠！！')
            time.sleep(900)

if __name__ == '__main__':
    start_url = 'http://www.yiban.cn/Newgroup/showMorePub/group_id/1197189/puid/1674209/type/3/page/%s'
    Cookie = ''
    student_list = []
    yiban = YibanSpider(Cookie, start_url, student_list)
    yiban.run()
   