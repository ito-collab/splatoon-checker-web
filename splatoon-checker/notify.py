import requests
from datetime import datetime, timedelta, timezone
import os

# ====== 設定（テスト時は多めに入れるのがコツです） ======
TARGET_RULES = ["ガチエリア"]
TARGET_STAGES = ["ナメロウ金属", "マヒマヒリゾート＆スパ", "ヤガラ市場", "タカアシ経済特区", "バイガイ亭", "クサヤ温泉"]
NOTIFY_HOURS_BEFORE = 12  # 12時間後までに始まるものなら全部通知する設定に変更

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
# ======================================================

RULE_MAP = {"ガチエリア": "Splat Zones", "ガチヤグラ": "Tower Control", "ガチホコバトル": "Rainmaker", "ガチアサリ": "Clam Blitz"}
STAGE_MAP = {"ユノハナ大渓谷": "Scorch Gorge", "ゴンズイ地区": "Eeltail Alley", "ヤガラ市場": "Hagglefish Market", "マテガイ放水路": "Undertow Spillway", "ナメロウ金属": "Mincemeat Metalworks", "マサバ海峡大橋": "Hammerhead Bridge", "マヒマヒリゾート＆スパ": "Mahi-Mahi Resort", "キンメダイ美術館": "Museum d'Alfonsino", "海女美術大学": "Inkblot Art Academy", "チョウザメ造船": "Sturgeon Shipyard", "ザトウマーケット": "MakoMart", "スメーシーワールド": "Wahoo World", "ヒラメが丘団地": "Flounder Heights", "クサヤ温泉": "Brinewater Springs", "マンタマリア号": "Manta Maria", "ナンプラー遺跡": "Um'ami Ruins", "タラポートショッピングパーク": "Barnacle & Dime", "コンブトラック": "Humpback Pump Track", "タカアシ経済特区": "Crableg Capital", "オヒョウ海運": "Shipshape Cargo Co.", "バイガイ亭": "Robo ROM-en", "ネギトロ炭鉱": "Bluefin Depot", "カジキ空港": "Marlin Airport", "リュウグウターミナル": "Lemuria Hub"}

def check_and_notify():
    # Webhook URLが空じゃないかチェック
    if not DISCORD_WEBHOOK_URL:
        print("❌ エラー: DiscordのWebhook URLが設定されていません。GitHubのSecretsを確認してください。")
        return

    res = requests.get("https://splatoon3.ink/data/schedules.json")
    data = res.json()
    x_nodes = data.get('data', {}).get('xSchedules', {}).get('nodes', [])
    
    now = datetime.now(timezone.utc)
    print(f"⏰ 現在時刻 (UTC): {now.strftime('%H:%M')}")
    
    found_any = False
    for schedule in x_nodes:
        setting = schedule.get('xMatchSetting')
        if not setting: continue
        
        start_time = datetime.strptime(schedule['startTime'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        time_diff = start_time - now
        
        rule_en = setting['vsRule']['name']
        stages_en = [s['name'] for s in setting['vsStages']]
        
        # ログ出力：今チェックしているスケジュールを表示
        diff_mins = int(time_diff.total_seconds() / 60)
        print(f"--- チェック中: {rule_en} ({diff_mins}分後開始) ---")

        # 【修正】0分〜2時間以内に始まるものなら通知対象にする
        if timedelta(hours=0) < time_diff <= timedelta(hours=NOTIFY_HOURS_BEFORE):
            # ルールとステージの判定
            rule_match = rule_en in [RULE_MAP[r] for r in TARGET_RULES if r in RULE_MAP]
            stage_match = any(s in [STAGE_MAP[ts] for ts in TARGET_STAGES if ts in STAGE_MAP] for s in stages_en)
            
            if rule_match and stage_match:
                print("✅ 条件に合致！Discordに送信します。")
                rule_jp = [k for k, v in RULE_MAP.items() if v == rule_en][0]
                stages_jp = [k for k, v in STAGE_MAP.items() if v in stages_en]
                jst_start = start_time + timedelta(hours=9)
                
                msg = f"🦑 **【Xマッチ通知】**\n⏰ {jst_start.strftime('%m/%d %H:%M')}〜\n👑 {rule_jp}\n🗺️ {' / '.join(stages_jp)}"
                requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
                found_any = True
            else:
                print(f"❌ ルールまたはステージが不一致 (RuleMatch:{rule_match}, StageMatch:{stage_match})")
    
    if not found_any:
        print("ℹ️ 条件に合うスケジュールは見つかりませんでした。")

if __name__ == "__main__":
    check_and_notify()
