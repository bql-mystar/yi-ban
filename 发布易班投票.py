import requests
import json
import re
from lxml import etree
import time

class Yiban:
    def __init__(self, Cookie ,request_url_temp, comment_content):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4298.4 Safari/537.36',
            'Cookie': Cookie
        }
        self.url_prefix = 'https://www.yiban.cn'
        self.request_url_temp = request_url_temp
        self.comment_content = comment_content
        pass

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

        mount_id = ret.get('data').get('vote_list').get('Mount_id')
        author_id = ret.get('data').get('vote_list').get('User_id')

        return voptions_id_list, mount_id, author_id

    # 投票部分
    def vote_post(self, params_dict, voption_id_list):
        post_url = 'https://www.yiban.cn/vote/vote/act'

        data = {
            'puid': params_dict['puid'],
            'group_id': params_dict['group_id'],
            'vote_id': params_dict['vote_id'],
            'actor_id': params_dict['actor_id'],
            'voptions_id': voption_id_list[0],
            'minimum': 1,
            'scopeMax': 1
        }
        response = requests.post(post_url, headers=self.headers, data=data)
        return response.content.decode()

    # 评论部分
    def add_comment(self, params_dict, mount_id, author_id):
        post_url = 'https://www.yiban.cn/vote/vote/addComment'
        data = {
            'mountid': mount_id,
            'msg': self.comment_content,
            'group_id': params_dict['group_id'],
            'actor_id': params_dict['actor_id'],
            'vote_id': params_dict['vote_id'],
            'author_id': author_id,
            'puid': params_dict['puid'],
            'reply_comment_id': 0,
            'reply_user_id': 0
            }
        response = requests.post(post_url, headers=self.headers, data=data)
        return response.content.decode()

    # 发表投票部分
    def add_vote(self, puid, group_id, vote_title):
        post_url = 'http://www.yiban.cn/vote/vote/add'
        data = {
            'puid': puid,
            'scope_ids': group_id,
            'title': vote_title,
            'subjectTxt': '',
            'subjectPic': '',
            'options_num': 3,
            'scopeMin': 1,
            'scopeMax': 1,
            'minimum': 1,
            'voteValue': '2022-06-30 23:55',
            'voteKey': 2,
            'public_type': 0,
            'isAnonymous': 1,
            'voteIsCaptcha': 0,
            'istop': 1,
            'sysnotice': 2,
            'isshare': 1,
            'rsa': 1,
            'dom':'.js-submit',
            'group_id': group_id,
            'subjectTxt_1': 'good',
            'subjectTxt_2': 'nice',
            'subjectTxt_3': 'well'
            }

        response = requests.post(post_url, headers=self.headers, data=data)
        return response.content.decode()

    def run(self, vote_title):
        puid = ''
        group_id = ''
        post_response = self.add_vote(puid, group_id, vote_title)
        dict_response = json.loads(post_response)
        print(dict_response)
        if dict_response.get('code') == 200:
            print('发表成功')

       


if __name__ == '__main__':
    # 获取自己的cookie值
    Cookie = ''
    request_url_temp = 'http://www.yiban.cn/Newgroup/showMorePub/group_id/686510/puid/1531874/type/3/page/%s'
    yiban = Yiban(Cookie, request_url_temp, comment_content)
    vote_title = ''
    yiban.run(vote_title)

