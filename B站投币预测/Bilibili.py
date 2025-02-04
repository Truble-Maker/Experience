import datetime
import time

import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 "
                  "Safari/537.36 Edg/132.0.0.0",
    "referer": "https://www.bilibili.com/",
}


def parse_cookie_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if line.strip().startswith("cookie:"):
            cookie_str = line.strip().split("cookie:", 1)[1].strip()
            return {"cookie": cookie_str}

    return None


# 解析 Cookie
cookies = parse_cookie_file("cookie.text")


# 获取全部json数据    在这个url中包含了比赛信息以及预测信息，更全---->获取不到数据了现在
def check_race(date=time.strftime("%Y-%m-%d", time.localtime())):
    """
    :param date: 传入日期
    :return: 返回当天的全部赛事预测
    """
    schedule_url = 'https://api.bilibili.com/x/esports/guess/collection/question'
    schedule_params = \
        {
            'pn': 1,
            'ps': 50,
            'stime': f'{date}' + ' 00:00:00',
            'etime': f'{date}' + ' 23:59:59'
        }
    return requests.get(schedule_url, headers=headers, cookies=cookies, params=schedule_params).json()


# 提取json数据并转化为列表
def parse_json(json_data):
    match_list = []

    # 确保数据格式正确
    matches = json_data.get("data", {}).get("list", [])

    for match in matches:
        contest = match.get("contest", {})  # 兼容新格式
        match_id = contest.get("id", "N/A")  # 赛事 ID
        title = contest.get("season", {}).get("title", "未知赛事")  # 赛事名称
        start_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                   time.localtime(contest["stime"])) if "stime" in contest else "未知"
        end_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(contest["etime"])) if "etime" in contest else "未知"
        home_team = contest.get("home_team", {}).get("title", "未知队伍")  # 主队
        away_team = contest.get("away_team", {}).get("title", "未知队伍")  # 客队

        # 追加到列表（每场比赛作为一行数据）
        match_list.append([match_id, title, start_time, end_time, home_team, away_team])
    return match_list


"""
    被注释掉的check_race()以及parse_json()是调用的另一个api
    该api只会返回比赛的信息，cid
    而新的api会返回cid以及每场比赛每支队伍的赔率以及队伍的detail_id
    为什么不只换url？ -> 两个url得到的json格式有细微的差别，所以提取json数据的parse_json()函数需要更改一下
"""


# 输出比赛信息------后续应该加上该比赛的赔率
def print_race(matches):
    """
    格式化打印比赛信息。

    参数：
        matches (list[list]): 包含比赛数据的二维列表，
                              每行格式为 [id, title, start_time, end_time, home_team, away_team]
    """
    print("{:<8} {:<20} {:<20} {:<20} {:<15} {:<15}".format(
        "比赛ID", "赛事名称", "开始时间", "结束时间", "主队", "客队"
    ))
    print("=" * 100)

    for match in matches:
        print("{:<8} {:<20} {:<20} {:<26} {:<16} {:<15}".format(
            match[0], match[1], match[2], match[3], match[4], match[5]
        ))
    coin_url = 'https://account.bilibili.com/site/getCoin'
    coin = requests.get(coin_url, headers=headers, cookies=cookies).json()
    print("硬币余额: " + str(coin["data"]["money"]))


# 将解析的json数据提取其中的比赛信息 main_id, detail_id 换url之后就不用再去race_massage_url = 'https://api.bilibili.com/x/esports/guess'请求全部数据了
# 并返回要预测的赛事的信息，oid, main_id, detail_id
def print_guess(json_data):
    match_list = []

    matches = json_data.get("data", {}).get("list", [])

    print("{:<20} {:<30} {:<40} {:<20} {:<10}".format(
        "比赛时间", "比赛名称", "参赛队伍", "赔率最低队伍", "赔率"
    ))
    print("=" * 130)

    for match in matches:
        contest = match.get("contest", {})
        questions = match.get("questions", [])

        if not contest or not questions:
            continue

        # 提取比赛ID和比赛名称
        match_id = contest.get("id", "N/A")
        match_name = contest.get("season", {}).get("title", "未知赛事")
        start_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                   time.localtime(contest["stime"])) if "stime" in contest else "未知"

        for question in questions:
            question_id = question.get("id", "N/A")
            team_matchup = question.get("title", "未知对战")

            # 找到赔率最低的队伍
            min_odds = float("inf")
            lowest_team_name = "未知队伍"
            lowest_detail_id = "N/A"

            for detail in question.get("details", []):
                odds = detail.get("odds", float("inf"))
                if odds < min_odds:
                    min_odds = odds
                    lowest_team_name = detail.get("option", "未知队伍")
                    lowest_detail_id = detail.get("detail_id", "N/A")

            # 格式化输出
            print("{:<20} {:<30} {:<40} {:<20} {:<10}".format(
                start_time, match_name, team_matchup, lowest_team_name, min_odds
            ))

            # 追加到返回列表
            match_list.append([match_id, question_id, lowest_detail_id])

    return match_list


# 查询并打印预测收益
def check_earnings(date=None):
    """
    :param date: 格式 "YYYY-MM-DD" 的日期字符串。传入时只显示该日期前一天的记录，如果为 None，则打印所有记录。
    :return: 无返回
    """
    earnings_url = "https://api.bilibili.com/x/esports/guess/collection/record?type=2&pn=1&ps=50"
    response = requests.get(earnings_url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        print("check_earnings函数请求失败，状态码:", response.status_code)
        return

    data = response.json()
    if data.get("code") != 0:
        print("API 返回错误:", data.get("message"))
        return

    records = data["data"]["record"]

    # 定义宽度
    header_fmt = "{:<12} {:<30} {:<30} {:<20} {:<20} {:<20}"
    row_fmt = "{:<12} {:<30} {:<30} {:<20} {:<20} {:<20}"

    # 打印表头
    header_line = header_fmt.format("比赛时间", "赛事名称", "比赛队伍", "押注队伍", "押注金额", "收益金额")
    print(header_line)
    print("=" * len(header_line))
    total_stake = 0
    total_income = 0
    # 遍历记录并打印数据行
    for record in records:
        contest = record.get("contest", {})
        guess_list = record.get("guess", [])
        if not guess_list:
            continue
        guess_json = guess_list[0]

        # 将比赛开始时间戳转换为日期
        contest_date = datetime.datetime.fromtimestamp(contest.get("stime", 0)).date()

        # 如果传入了日期参数，则只保留比赛日期为 (date - 1 天) 的记录
        if date:
            current_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            # 计算前一天的日期
            target_date = current_date - datetime.timedelta(days=1)
            if contest_date != target_date:
                continue

        event_name = contest.get("season", {}).get("title", "")
        home_team = contest.get("home_team", {}).get("title", "")
        away_team = contest.get("away_team", {}).get("title", "")
        teams = f"{home_team} vs {away_team}"
        bet_team = guess_json.get("option", "")
        stake = guess_json.get("stake", 0)
        income = guess_json.get("income", 0)

        total_stake += stake  # 计算总押注
        total_income += income  # 计算总收益
        print(row_fmt.format(
            contest_date.strftime("%Y-%m-%d"), event_name, teams, bet_team, stake, income))

    # 获取硬币余额
    coin_url = 'https://account.bilibili.com/site/getCoin'
    coin_response = requests.get(coin_url, headers=headers, cookies=cookies)
    if coin_response.status_code == 200:
        coin_data = coin_response.json()
        money = coin_data.get("data", {}).get("money", "未知")
        print("\n硬币余额: " + str(money))
    else:
        print("\n获取硬币余额失败，状态码:", coin_response.status_code)
    print(
        f"{'总投资'} {'{:<20}'.format(total_stake)}\n{'总收益'} {'{:<20}'.format(total_income)}\n{'盈亏'} {float(total_income - total_stake)}")


# 提取cookie中的csrf也就是bili_jct
def get_csrf(cookie):
    for part in cookie.split('; '):
        if part.startswith("bili_jct="):
            return part.split("=")[1]
    return None


# 发送预测申请
def post_guess(matches, count=5):
    csrf = get_csrf(cookies['cookie'])
    guess_url = 'https://api.bilibili.com/x/esports/guess/add'
    if csrf:
        for match in matches:
            guess_data = \
                {
                    'oid': f'{match[0]}',
                    'main_id': f'{match[1]}',
                    'detail_id': f'{match[2]}',
                    'count': f'{count}',
                    'is_fav': 1,
                    'csrf': f'{csrf}'
                }
            result = requests.post(guess_url, headers=headers, cookies=cookies, data=guess_data)
            print(result.text)

    else:
        print("csrf校验错误，检查cookie中是否含有bili_jct, 或cookie已过期, 请获取最新cookie")


"""
    首先调用check_race()函数，获取到比赛信息
    然后用parse_json()解析数据，得到列表，然后调用print_race()来显示比赛
    示例
    print_race(parse_json(check_race()))
    比赛ID     赛事名称                 开始时间                 结束时间                 主队              客队             
    ====================================================================================================
    30397    2025IEM卡托维兹          2025-02-03 20:30:00  2025-02-04 08:30:00        MOUZ             Liquid         
    30398    2025IEM卡托维兹          2025-02-03 20:30:00  2025-02-04 08:30:00        FURIA            Astralis       
    30399    2025IEM卡托维兹          2025-02-03 23:00:00  2025-02-04 11:00:00        GL               Mongolz        
    30400    2025IEM卡托维兹          2025-02-03 23:00:00  2025-02-04 11:00:00        NAVI             Spirit         
    硬币余额: 293.4
    
    
    check_earnings()用来查看收益，如果不传参就默认查看历史预测收益，如果传参就会查看你传参数据的前一天的收益
    示例      用time.strftime("%Y-%m-%d", time.localtime())来生成今天的日期，这样传参可以快速知道昨天的预测收益
    check_earnings(time.strftime("%Y-%m-%d", time.localtime()))
    比赛时间         赛事名称                           比赛队伍                           押注队伍                 押注金额                 收益金额                
    =========================================================================================================================================
    2025-02-02   2025IEM卡托维兹                    NAVI vs FURIA                  NAVI                 1                    1.3                 
    
    硬币余额: 293.4
    总投资 1                   
    总收益 1.3                 
    盈亏 0.30000000000000004
    
    用print_guess()来打印今天可以预测的比赛，他有个返回值，返回值就是需要预测的比赛队伍
    示例
    print_guess(check_race())
    比赛时间                 比赛名称                           参赛队伍                                     赔率最低队伍               赔率        
    ==================================================================================================================================
    2025-02-03 20:30:00  2025IEM卡托维兹                    MOUZ vs Liquid 的胜者是？                     Liquid               1.45      
    2025-02-03 20:30:00  2025IEM卡托维兹                    FURIA vs Astralis 的胜者是？                  Astralis             1.59      
    2025-02-03 23:00:00  2025IEM卡托维兹                    GL vs Mongolz 的胜者是？                      Mongolz              1.36      
    2025-02-03 23:00:00  2025IEM卡托维兹                    NAVI vs Spirit 的胜者是？                     Spirit               1.38      
    也可以打印返回值看一下
    print(print_guess(check_race()))
    [[30397, 9024, 18641], [30398, 9023, 18639], [30399, 9022, 18637], [30400, 9021, 18635]]
    返回的是二维列表，这个列表也就是post_guess()所需要的参数
    
    post_guess()用于预测
    示例
    post_guess(print_guess(check_race()))
    比赛时间                 比赛名称                           参赛队伍                                     赔率最低队伍               赔率        
    ==================================================================================================================================
    2025-02-03 20:30:00  2025IEM卡托维兹                    MOUZ vs Liquid 的胜者是？                     Liquid               1.45      
    2025-02-03 20:30:00  2025IEM卡托维兹                    FURIA vs Astralis 的胜者是？                  Astralis             1.6       
    2025-02-03 23:00:00  2025IEM卡托维兹                    GL vs Mongolz 的胜者是？                      Mongolz              1.35      
    2025-02-03 23:00:00  2025IEM卡托维兹                    NAVI vs Spirit 的胜者是？                     Spirit               1.38      
    {"code":75207,"message":"您已经投注了哦~","ttl":1}
    {"code":75207,"message":"您已经投注了哦~","ttl":1}
    {"code":75207,"message":"您已经投注了哦~","ttl":1}
    {"code":75207,"message":"您已经投注了哦~","ttl":1}
    
    post_guess(print_guess(check_race()), count=1)可以给post_guess()的参数count赋值，默认为5
"""
# check_earnings(time.strftime("%Y-%m-%d", time.localtime()))
# post_guess(print_guess(check_race()))
# print_race(parse_json(check_race()))dwd
# idwjiwdj