"""
    又有新函数迭代了....那旧的呢...
"""

import datetime
import time

import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 "
                  "Safari/537.36 Edg/132.0.0.0",
    "referer": "https://www.bilibili.com/",
}
cookies = {
}


def guess_massage(date=time.strftime("%Y-%m-%d", time.localtime())):
    """
    :param date: 传入时间，默认是当天
    :return: 返回赔率最低的组的cid，detail_id
    """
    guess_massage_url = 'https://api.bilibili.com/x/esports/guess/collection/question'
    guess_param = \
        {
            'pn': 1,
            'ps': 50,
            'stime': f'{date}' + ' 00:00:00',
            'etime': f'{date}' + ' 23:59:59'
        }
    guess_massage_json = requests.get(guess_massage_url, headers=headers, cookies=cookies, params=guess_param).json()
    if not guess_massage_json["data"]["list"]:
        print(
            "现在无赛事可预测" + f'\n您可以查询明天的，在guess_massgae()函数中传入{(datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")}')
    else:
        print(guess_massage_json)


# 暂时没用 将解析到的matches数据提取出来，需要提取oid 以及赔率较低的队伍的id
def guess_race(matches):
    for match in matches:
        # guess_data = \
        #     {
        #         'oid': f'{match[0]}',
        #         'count': '5',
        #         'is_fav': 0,
        #         'csrf': ''
        #     }
        # resp = requests.post(guess_url, headers=headers, cookies=cookies, data=guess_data)
        url = f'https://api.bilibili.com/x/esports/match/detail?match_id={match[0]}'
        resp = requests.post(url, headers=headers, cookies=cookies)
        print(resp.text)
        break


# 获取全部json数据
def check_race(date=time.strftime("%Y-%m-%d", time.localtime())):
    schedule_url = 'https://api.bilibili.com/x/esports/matchs/list'
    schedule_params = \
        {
            "mid": 0,
            "gid": 0,
            "tid": 0,
            "pn": 1,
            "ps": 10,
            "contest_status": "",
            "etime": f"{date}",
            "stime": f"{date}"
        }
    return requests.get(schedule_url, headers=headers, cookies=cookies, params=schedule_params).json()


# 返回请求到的数据并转化为列表，方便后续读取
def parse_json(json_data):
    match_list = []

    # 确保数据格式正确
    matches = json_data["data"]['list']

    for match in matches:
        match_id = match.get("id", "N/A")  # 比赛 ID也就是cid
        title = match.get("season", {}).get("title", "未知赛事")  # 赛事名称
        start_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                   time.localtime(match["stime"])) if "stime" in match else "未知"
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(match["etime"])) if "etime" in match else "未知"
        home_team = match.get("home_team", {}).get("title", "未知队伍")  # 主队
        away_team = match.get("away_team", {}).get("title", "未知队伍")  # 客队

        # 追加到列表（每场比赛作为一行数据）
        match_list.append([match_id, title, start_time, end_time, home_team, away_team])

    return match_list
