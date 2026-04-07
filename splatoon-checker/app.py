import streamlit as st
import requests
from datetime import datetime, timedelta, timezone

# スプラトゥーン3の全24ステージ完全網羅
STAGE_MAP = {
    "ユノハナ大渓谷": "Scorch Gorge",
    "ゴンズイ地区": "Eeltail Alley",
    "ヤガラ市場": "Hagglefish Market",
    "マテガイ放水路": "Undertow Spillway",
    "ナメロウ金属": "Mincemeat Metalworks",
    "マサバ海峡大橋": "Hammerhead Bridge",
    "マヒマヒリゾート＆スパ": "Mahi-Mahi Resort",
    "キンメダイ美術館": "Museum d'Alfonsino",
    "海女美術大学": "Inkblot Art Academy",
    "チョウザメ造船": "Sturgeon Shipyard",
    "ザトウマーケット": "MakoMart",
    "スメーシーワールド": "Wahoo World",
    "ヒラメが丘団地": "Flounder Heights",
    "クサヤ温泉": "Brinewater Springs",
    "マンタマリア号": "Manta Maria",
    "ナンプラー遺跡": "Um'ami Ruins",
    "タラポートショッピングパーク": "Barnacle & Dime",
    "コンブトラック": "Humpback Pump Track",
    "タカアシ経済特区": "Crableg Capital",
    "オヒョウ海運": "Shipshape Cargo Co.",
    "バイガイ亭": "Robo ROM-en",
    "ネギトロ炭鉱": "Bluefin Depot",
    "カジキ空港": "Marlin Airport",
    "リュウグウターミナル": "Lemuria Hub"
}

# ルール
RULE_MAP = {
    "ガチエリア": "Splat Zones",
    "ガチヤグラ": "Tower Control",
    "ガチホコバトル": "Rainmaker",
    "ガチアサリ": "Clam Blitz"
}

# 英語→日本語の逆引き用辞書
INV_RULE_MAP = {v: k for k, v in RULE_MAP.items()}
INV_STAGE_MAP = {v: k for k, v in STAGE_MAP.items()}

st.set_page_config(page_title="スプラ3 Xマッチチェッカー", page_icon="🦑", layout="centered")

st.title("🦑 スプラ3 Xマッチチェッカー")
st.write("好きなルールとステージを選ぶと、直近のスケジュールから条件に合うXマッチを検索します！")

# UI: 複数選択
selected_rules = st.multiselect("👑 遊びたいルール", list(RULE_MAP.keys()), default=["ガチエリア"])
selected_stages = st.multiselect("🗺️ 遊びたいステージ", list(STAGE_MAP.keys()), default=["ナメロウ金属"])

if st.button("スケジュールを検索🔍"):
    if not selected_rules or not selected_stages:
        st.warning("ルールとステージをそれぞれ1つ以上選択してください。")
    else:
        with st.spinner('スケジュールを取得中...'):
            url = "https://splatoon3.ink/data/schedules.json"
            try:
                res = requests.get(url)
                res.raise_for_status()
                data = res.json()
                
                # エラー回避のため、データ構造を安全に取得
                x_nodes = data.get('data', {}).get('xSchedules', {}).get('nodes', [])
                
                target_rules_en = [RULE_MAP[r] for r in selected_rules]
                target_stages_en = [STAGE_MAP[s] for s in selected_stages]
                
                found_match = False
                
                st.subheader("🎯 検索結果")
                
                for schedule in x_nodes:
                    # Xマッチのデータが存在しない時間帯（フェス等）をスキップ
                    setting = schedule.get('xMatchSetting')
                    if not setting: 
                        continue
                    
                    rule_en = setting['vsRule']['name']
                    stages_en = [s['name'] for s in setting['vsStages']]
                    
                    # 条件判定
                    if rule_en in target_rules_en:
                        if set(stages_en) & set(target_stages_en):
                            found_match = True
                            
                            # 時間の変換
                            start_dt = datetime.strptime(schedule['startTime'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                            end_dt = datetime.strptime(schedule['endTime'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                            jst_start = start_dt + timedelta(hours=9)
                            jst_end = end_dt + timedelta(hours=9)
                            
                            rule_jp = INV_RULE_MAP.get(rule_en, rule_en)
                            stages_jp = [INV_STAGE_MAP.get(s, s) for s in stages_en]
                            
                            st.success(f"⏰ **{jst_start.strftime('%m/%d %H:%M')} 〜 {jst_end.strftime('%H:%M')}**")
                            st.write(f"👑 **{rule_jp}**")
                            st.write(f"🗺️ {' / '.join(stages_jp)}")
                            st.write("---")
                            
                if not found_match:
                    st.info("現在公開されている約24時間先までのスケジュールに、条件に合うXマッチはありませんでした😭")
                
                # ---------------------------------------------
                # 【新機能】現在公開されているすべての予定を折りたたみ表示
                # ---------------------------------------------
                st.write("")
                with st.expander("📝 参考：現在の全Xマッチスケジュールを確認する"):
                    for schedule in x_nodes:
                        setting = schedule.get('xMatchSetting')
                        if not setting: 
                            continue
                        
                        start_dt = datetime.strptime(schedule['startTime'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                        jst_start = start_dt + timedelta(hours=9)
                        
                        rule_en = setting['vsRule']['name']
                        stages_en = [s['name'] for s in setting['vsStages']]
                        
                        rule_jp = INV_RULE_MAP.get(rule_en, rule_en)
                        stages_jp = [INV_STAGE_MAP.get(s, s) for s in stages_en]
                        
                        st.markdown(f"**{jst_start.strftime('%m/%d %H:%M')}〜** | {rule_jp} | {'・'.join(stages_jp)}")
                        
            except Exception as e:
                st.error(f"データの取得に失敗しました: {e}")
