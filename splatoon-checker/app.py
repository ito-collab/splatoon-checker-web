import streamlit as st
import requests
from datetime import datetime, timedelta, timezone

# 日本語名とAPI（英語）名の対応表
RULE_MAP = {
    "ガチエリア": "Splat Zones",
    "ガチヤグラ": "Tower Control",
    "ガチホコバトル": "Rainmaker",
    "ガチアサリ": "Clam Blitz"
}

# 主要なステージ（必要に応じて追加・変更してください）
STAGE_MAP = {
    "ユノハナ大渓谷": "Scorch Gorge",
    "ゴンズイ地区": "Eeltail Alley",
    "ヤガラ市場": "Hagglefish Market",
    "マテガイ放水路": "Undertow Spillway",
    "ナメロウ金属": "Mincemeat Metalworks",
    "マサバ海峡大橋": "Hammerhead Bridge",
    "マヒマヒリゾート＆スパ": "Mahi-Mahi Resort",
    "海女美術大学": "Inkblot Art Academy",
    "チョウザメ造船": "Sturgeon Shipyard",
    "ザトウマーケット": "MakoMart",
    "スメーシーワールド": "Wahoo World",
    "ヒラメが丘団地": "Flounder Heights",
    "クサヤ温泉": "Brinewater Springs",
    "マンタマリア号": "Manta Maria",
    "タラポートショッピングパーク": "Taraport Shopping Park",
    "コンブトラック": "Kelp Dome",
    "タカアシ経済特区": "Crableg Capital",
    "オヒョウ海運": "Shipshape Cargo Co."
}

# 画面の設定
st.set_page_config(page_title="スプラ3 Xマッチチェッカー", page_icon="🦑", layout="centered")

st.title("🦑 スプラ3 Xマッチチェッカー")
st.write("好きなルールとステージを選ぶと、直近のスケジュールから条件に合うXマッチを検索します！")

# ユーザー入力UI（複数選択）
selected_rules = st.multiselect("👑 遊びたいルールを選んでください", list(RULE_MAP.keys()), default=["ガチエリア"])
selected_stages = st.multiselect("🗺️ 遊びたいステージを選んでください", list(STAGE_MAP.keys()), default=["ナメロウ金属", "マテガイ放水路"])

if st.button("スケジュールを検索🔍"):
    if not selected_rules or not selected_stages:
        st.warning("ルールとステージをそれぞれ1つ以上選択してください。")
    else:
        with st.spinner('イカリングの裏側からスケジュールを取得中...'):
            url = "https://splatoon3.ink/data/schedules.json"
            try:
                res = requests.get(url)
                res.raise_for_status()
                data = res.json()
                
                # Xマッチのスケジュール取得
                x_nodes = data['data']['xSchedules']['nodes']
                
                # 検索用に英語名に変換
                target_rules_en = [RULE_MAP[r] for r in selected_rules]
                target_stages_en = [STAGE_MAP[s] for s in selected_stages]
                
                found_match = False
                
                for schedule in x_nodes:
                    if not schedule.get('xmatchSetting'): continue
                    
                    rule_en = schedule['xmatchSetting']['vsRule']['name']
                    stages_en = [s['name'] for s in schedule['xmatchSetting']['vsStages']]
                    
                    # ルールが一致し、かつステージのいずれかが一致するか判定
                    if rule_en in target_rules_en:
                        if set(stages_en) & set(target_stages_en):
                            found_match = True
                            
                            # 時間の変換 (UTC -> JST)
                            start_dt = datetime.strptime(schedule['startTime'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                            end_dt = datetime.strptime(schedule['endTime'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                            jst_start = start_dt + timedelta(hours=9)
                            jst_end = end_dt + timedelta(hours=9)
                            
                            # 日本語名に戻す
                            inv_rule = {v:k for k,v in RULE_MAP.items()}
                            inv_stage = {v:k for k,v in STAGE_MAP.items()}
                            rule_jp = inv_rule.get(rule_en, rule_en)
                            stages_jp = [inv_stage.get(s, s) for s in stages_en]
                            
                            # 画面に結果を表示
                            st.success(f"⏰ **{jst_start.strftime('%m/%d %H:%M')} 〜 {jst_end.strftime('%H:%M')}**")
                            st.write(f"👑 **{rule_jp}**")
                            st.write(f"🗺️ {' / '.join(stages_jp)}")
                            st.write("---")
                            
                if not found_match:
                    st.info("現在公開されているスケジュール（約24時間先まで）の中に、条件に合うXマッチはありませんでした😭 時間を空けてまたチェックしてみてください。")
                    
            except Exception as e:
                st.error(f"データの取得に失敗しました: {e}")
