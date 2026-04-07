import requests
from datetime import datetime, timedelta, timezone

# ====== 通知設定（ここを自分の好みに書き換える） ======
TARGET_RULES = ["ガチエリア"]
TARGET_STAGES = ["ナメロウ金属", "マヒマヒリゾート＆スパ"]
NOTIFY_HOURS_BEFORE = 10 # 何時間前のタイミングで通知するか

# Discord設定（ステップ1でコピーしたURLを貼る）
DISCORD_WEBHOOK_URL = "ここにDiscordのWebhook_URLを貼り付ける"
# ======================================================

RULE_MAP = {"ガチエリア": "Splat Zones", "ガチヤグラ": "Tower Control", "ガチホコバトル": "Rainmaker", "ガチアサリ": "Clam Blitz"}
STAGE_MAP = {"ユノハナ大渓谷": "Scorch Gorge", "ゴンズイ地区": "Eeltail Alley", "ヤガラ市場": "Hagglefish Market", "マテガイ放水路": "Undertow Spillway", "ナメロウ金属": "Mincemeat Metalworks", "マサバ海峡大橋": "Hammerhead Bridge", "マヒマヒリゾート＆スパ": "Mahi-Mahi Resort", "キンメダイ美術館": "Museum d'Alfonsino", "海女美術大学": "Inkblot Art Academy", "チョウザメ造船": "Sturgeon Shipyard", "ザトウマーケット": "MakoMart", "スメーシーワールド": "Wahoo World", "ヒラメが丘団地": "Flounder Heights", "クサヤ温泉": "Brinewater Springs", "マンタマリア号": "Manta Maria", "ナンプラー遺跡": "Um'ami Ruins", "タラポートショッピングパーク": "Barnacle & Dime", "コンブトラック": "Humpback Pump Track", "タカアシ経済特区": "Crableg Capital", "オヒョウ海運": "Shipshape Cargo Co.", "バイガイ亭": "Robo ROM-en", "ネギトロ炭鉱": "Bluefin Depot", "カジキ空港": "Marlin Airport", "リュウグウターミナル": "Lemuria Hub"}

def send_discord(message):
    """Discordにメッセージを送信する関数"""
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Discordへの送信に失敗しました: {e}")

def check_and_notify():
    res = requests.get("https://splatoon3.ink/data/schedules.json")
    data = res.json()
    x_nodes = data.get('data', {}).get('xSchedules', {}).get('nodes', [])
    
    now = datetime.now(timezone.utc)
    
    for schedule in x_nodes:
        setting = schedule.get('xMatchSetting')
        if not setting: continue
        
        start_time = datetime.strptime(schedule['startTime'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        time_diff = start_time - now
        
        # 1時間に1回の実行で重複通知を防ぐための条件式
        if timedelta(hours=NOTIFY_HOURS_BEFORE - 1) < time_diff <= timedelta(hours=NOTIFY_HOURS_BEFORE):
            rule_en = setting['vsRule']['name']
            stages_en = [s['name'] for s in setting['vsStages']]
            
            # 自分が設定したルールとステージが含まれているかチェック
            if rule_en in [RULE_MAP[r] for r in TARGET_RULES]:
                if set(stages_en) & set([STAGE_MAP[s] for s in TARGET_STAGES]):
                    rule_jp = [k for k, v in RULE_MAP.items() if v == rule_en][0]
                    stages_jp = [k for k, v in STAGE_MAP.items() if v in stages_en]
                    jst_start = start_time + timedelta(hours=9)
                    
                    # Discord用の見やすいメッセージ
                    msg = (
                        f"🦑 **【Xマッチ通知】** 🦑\n"
                        f"もうすぐ好きな条件のXマッチが始まります！\n\n"
                        f"⏰ **時間**: {jst_start.strftime('%m/%d %H:%M')} ~\n"
                        f"👑 **ルール**: {rule_jp}\n"
                        f"🗺️ **ステージ**: {' / '.join(stages_jp)}"
                    )
                    send_discord(msg)

if __name__ == "__main__":
    check_and_notify()
