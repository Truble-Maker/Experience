import json
import time

import requests


class CS:
    def __init__(self, uid, season = ''):
        self.steam64 = uid
        pvp_url = 'https://api.wmpvp.com/api/v2/csgo/pvpDetailDataStats'
        header = \
            {
                'User-Agent': 'okhttp/4.11.0',
                'Content-Type': 'application/json',
                't': str(int(time.time() * 1000))
            }
        data = \
            {
                'steamId64': self.steam64,
                'csgoSeasonId': f'{season}'
            }
        resp = requests.post(url=pvp_url, headers=header, json=data).text
        self.resp_json = json.loads(resp)
        print("用户: " + self.resp_json['data']['name'])
        print("赛季场次: " + str(self.resp_json['data']['cnt']))
        print("赛季kd: " + str(self.resp_json['data']['kd']))
        print("赛季胜率: " + str(self.resp_json['data']['winRate'] * 100) + '%')
        print("赛季ratingPro: " + str(self.resp_json['data']['pwRating']))
        print("赛季击杀: " + str(self.resp_json['data']['kills']))
        print("赛季死亡: " + str(self.resp_json['data']['deaths']))
        print("赛季助攻: " + str(self.resp_json['data']['assists']))
        print("mvp次数: " + str(self.resp_json['data']['mvpCount']))
        print("ADR: " + str(self.resp_json['data']['adr']))
        print("RWS: " + str(self.resp_json['data']['rws']))
        print("爆头率: " + str(self.resp_json['data']['headShotRatio'] * 100) + '%')
        print("击杀比: " + str(self.resp_json['data']['entryKillRatio'] * 100) + '%')
        print   \
                (
                    f"双杀: {self.resp_json['data']['k2']}, "
                    f"三杀: {self.resp_json['data']['k3']}, "
                    f"四杀: {self.resp_json['data']['k4']}, "
                    f"五杀: {self.resp_json['data']['k5']}, "
                    f"多杀次数: {self.resp_json['data']['multiKill']}"
                )
        print   \
                (
                    f"1v1 获胜: {self.resp_json['data']['vs1']}, "
                    f"1v2 获胜: {self.resp_json['data']['vs2']}, "
                    f"1v3 获胜: {self.resp_json['data']['vs3']}, "
                    f"1v4 获胜: {self.resp_json['data']['vs4']}, "
                    f"1v5 获胜: {self.resp_json['data']['vs5']}, "
                    f"残局获胜: {self.resp_json['data']['endingWin']}"
                )

    def map_information(self):
        if 'hotMaps' not in self.resp_json['data']:
            print("Error: 'hotMaps'字段未找到")
            return

        # 遍历每张地图的信息
        for idx, map_info in enumerate(self.resp_json['data']['hotMaps'], start=1):
            # 提取字段
            map_name = map_info.get('mapName', '未知')
            total_match = map_info.get('totalMatch', 0)
            win_count = map_info.get('winCount', 0)
            total_kill = map_info.get('totalKill', 0)
            death_num = map_info.get('deathNum', 0)
            first_kill = map_info.get('firstKillNum', 0)
            first_death = map_info.get('firstDeathNum', 0)

            # 计算胜率
            if total_match != 0:
                win_rate = (win_count / total_match) * 100
            else:
                win_rate = 0  # 如果总场数为0，胜率为0

            # 打印信息
            print(f"地图TOP {idx}: {map_name}")
            print(f"          赛季总场数: {total_match}")
            print(f"          赛季胜率: {win_rate:.2f}%")
            print(f"          总击杀: {total_kill}")
            print(f"          总死亡: {death_num}")
            print(f"          首杀: {first_kill}")
            print(f"          首死: {first_death}")
            print('-' * 40)

    def check_rating(self):
        # 检查 resp_json 是否包含所需的数据
        if 'data' not in self.resp_json or 'historyPwRatings' not in self.resp_json['data']:
            print("Error: 数据中缺少 'historyPwRatings' 字段")
            return

        # 获取历史评分
        history_ratings = self.resp_json['data']['historyPwRatings']

        # 定义评级区间
        rating_intervals = [
            {'name': '<0.5', 'lower': -float('inf'), 'upper': 0.5},
            {'name': '0.5 - 0.6', 'lower': 0.5, 'upper': 0.6},
            {'name': '0.6 - 0.7', 'lower': 0.6, 'upper': 0.7},
            {'name': '0.7 - 0.8', 'lower': 0.7, 'upper': 0.8},
            {'name': '0.8 - 0.9', 'lower': 0.8, 'upper': 0.9},
            {'name': '0.9 - 1.0', 'lower': 0.9, 'upper': 1.0},
            {'name': '1.0 - 1.3', 'lower': 1.0, 'upper': 1.3},
            {'name': '1.3 - 1.5', 'lower': 1.3, 'upper': 1.5},
            {'name': '1.5 - 1.8', 'lower': 1.5, 'upper': 1.8},
            {'name': '1.8 - 2.0', 'lower': 1.8, 'upper': 2.0},
            {'name': '>=2.0', 'lower': 2.0, 'upper': float('inf')}
        ]

        # 统计每个区间的出现次数
        interval_counts = {interval['name']: 0 for interval in rating_intervals}

        # 遍历历史评分并进行区间分类
        for rating in history_ratings:
            for interval in rating_intervals:
                if interval['lower'] <= rating < interval['upper']:
                    interval_counts[interval['name']] += 1
                    break

        # 打印结果
        print("Rating Intervals:")
        for interval_name, count in interval_counts.items():
            print(f"{interval_name}: {count}")

    def check_inventory(self):
        inventory_url = 'https://gwapi.pwesports.cn/appdecoration/steamcn/csgo/decoration/getSteamInventoryPreview'
        inventory_param = \
            {
                'steamId': self.steam64,
                'previewSize': '19'
            }
        inventory_header = \
            {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'
            }
        resp = requests.get(inventory_url, headers=inventory_header, params=inventory_param).json()
        # 检查接口返回的 code
        if resp.get("code") == 0:
            result = resp["result"]
            total_price = result.get("totalPrice", 0)  # 总价值（分）
            total_value_yuan = total_price / 100  # 转换为元
            items = result.get("previewItem", [])  # 物品列表
            print(f"\n库存总价值（CNY）：\n  {total_value_yuan:.2f} 元")
            print("库存物品名称（marketName）：")
            for index, item in enumerate(items, start=1):
                market_name = item.get("marketName", "未知")
                print(f"  {index}. {market_name}")


if __name__ == "__main__":
    # 初始化 SteamID
    steam_id = input("请输入您的 SteamID: ")

    # 初始化 CS 对象
    qz = CS(steam_id)

    while True:
        print("\n=== CS:GO 数据查询工具 ===")
        print("1. 查看地图信息")
        print("2. 查看 Rating 分析")
        print("3. 查看库存信息")
        print("4. 退出程序")
        print("==========================")

        choice = input("请输入选项编号 (1-4): ")

        if choice == '1':
            print("\n=== 地图信息 ===")
            qz.map_information()
            input("\n按 Enter 键返回主菜单...")
        elif choice == '2':
            print("\n=== Rating 分析 ===")
            qz.check_rating()
            input("\n按 Enter 键返回主菜单...")
        elif choice == '3':
            print("\n=== 库存信息 ===")
            qz.check_inventory()
            input("\n按 Enter 键返回主菜单...")
        elif choice == '4':
            print("\n退出程序...")
            break
        else:
            print("\n无效的选项，请重新输入。")