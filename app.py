# app.py
import streamlit as st
import api_client
import logic
import roblox_api
import card_generator
from io import BytesIO
import pandas as pd
import os
import base64

st.set_page_config(page_title="RIVALS Season 1 Recap", layout="wide", page_icon="🏆")

# [폰트 로드 함수]
def load_custom_fonts():
    fonts = {
        "TitleFont": "assets/font/Jalnan2TTF.ttf",
        "BodyFont": "assets/font/GmarketSansTTFMedium.ttf",
        "BoldFont": "assets/font/GmarketSansTTFBold.ttf"
    }
    font_css = "<style>"
    for font_name, font_path in fonts.items():
        if os.path.exists(font_path):
            with open(font_path, "rb") as f:
                data = f.read()
            b64_data = base64.b64encode(data).decode()
            font_css += f"""
                @font-face {{
                    font-family: '{font_name}';
                    src: url(data:font/ttf;base64,{b64_data}) format('truetype');
                }}
            """
    font_css += """
        html, body, [class*="css"] { font-family: 'BodyFont', sans-serif; }
        h1, h2, h3 { font-family: 'TitleFont', sans-serif !important; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2); }
        div[data-testid="stMetricValue"] { font-family: 'TitleFont', sans-serif; color: #ffffff; }
        div[data-testid="stMetricLabel"] { font-family: 'BoldFont', sans-serif; color: #aaaaaa; }
        .stButton>button { width: 100%; border-radius: 12px; font-family: 'TitleFont', sans-serif; font-size: 18px; }
    </style>
    """
    st.markdown(font_css, unsafe_allow_html=True)

load_custom_fonts()

# --- [무기 매핑 데이터] ---
# 표시 이름 : 파일명 (assets/weapons/ 아래)
WEAPON_MAP = {
    "Assault Rifle": "AssaultRifle.webp",
    "Bow": "Bow.webp",
    "Burst Rifle": "Burstrifle.webp",
    "Crossbow": "Crossbow.webp",
    "Distortion": "Distortion.webp",
    "Energy Rifle": "Energy_Rifle.webp",
    "Flamethrower": "Flamethrower.webp",
    "Grenade Launcher": "Grenadelaunncher.webp", # 파일명 오타 유지 (nn)
    "Gun Blade": "Gun_Blade.webp",
    "Minigun": "Minigun.webp",
    "Paintball Gun": "Paintballgun.webp",
    "RPG": "Rpg.webp",
    "Shotgun": "Shotgun.webp",
    "Sniper": "Sniper.webp",
    # 파일 목록에 없는 경우 대비 (기본값 설정 가능)
    "Katana": "Katana.webp", 
    "Ice Gun": "IceGun.webp",
    "Scythe": "Scythe.webp",
    "Pistol": "Pistol.webp"
}

def get_weapon_img_path(weapon_name):
    filename = WEAPON_MAP.get(weapon_name)
    if filename:
        path = os.path.join("assets", "weapons", filename)
        if os.path.exists(path):
            return path
    return None

if 'data' not in st.session_state: st.session_state['data'] = None
if 'weapon_files' not in st.session_state: st.session_state['weapon_files'] = []
if 'final_weapons_data' not in st.session_state: st.session_state['final_weapons_data'] = []
if 'nickname' not in st.session_state: st.session_state['nickname'] = ""
if 'level' not in st.session_state: st.session_state['level'] = 1
if 'score' not in st.session_state: st.session_state['score'] = 0
if 'roblox_profile' not in st.session_state: st.session_state['roblox_profile'] = None
if 'generated_card' not in st.session_state: st.session_state['generated_card'] = None

with st.sidebar:
    st.header("🏆 Season 1 Recap")
    st.info("API 키는 내부 설정값을 사용합니다.")

st.markdown("<h1 style='text-align: center;'>🏆 RIVALS SEASON 1 RECAP</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["1️⃣ 데이터 입력", "2️⃣ 상세 정밀 분석", "3️⃣ 나만의 리캡 카드"])

# 1. 데이터 입력
with tab1:
    col_input, col_preview = st.columns([1.5, 1])
    with col_input:
        st.subheader("1. 플레이어 정보")
        c1, c2 = st.columns([2, 1])
        with c1:
            nick_input = st.text_input("닉네임", value=st.session_state['nickname'])
            if nick_input: st.session_state['nickname'] = nick_input
        with c2:
            st.session_state['level'] = st.number_input("레벨", min_value=1, value=st.session_state['level'])

        st.markdown("---")
        st.subheader("2. 스탯 사진 업로드")
        rank_file = st.file_uploader("랭크 사진 1장 (Final ELO 포함)", type=['jpg', 'png'], key="rank_up")
        general_files = st.file_uploader("전체 통계 사진 (2~3장)", type=['jpg', 'png'], accept_multiple_files=True, key="gen_up")
        
        st.markdown("#### ③ 무기 스탯 추가 (선택)")
        with st.expander("🔫 무기 사진 추가하기", expanded=True):
            w_col1, w_col2 = st.columns([1, 2])
            
            # 무기 선택 (매핑된 키들로 리스트 구성)
            w_name_sel = w_col1.selectbox("무기 선택", list(WEAPON_MAP.keys()))
            
            # 선택된 무기 이미지 미리보기
            w_img_path = get_weapon_img_path(w_name_sel)
            if w_img_path:
                w_col1.image(w_img_path, use_container_width=True)
            else:
                w_col1.caption("이미지 없음")

            w_file = w_col2.file_uploader("해당 무기 스탯 사진", type=['jpg', 'png'], key="w_up")
            
            if st.button("➕ 무기 목록에 추가"):
                if w_file:
                    existing_idx = next((i for i, item in enumerate(st.session_state['weapon_files']) if item['name'] == w_name_sel), -1)
                    new_item = {"name": w_name_sel, "file": w_file}
                    if existing_idx != -1:
                        st.session_state['weapon_files'][existing_idx] = new_item
                        st.success(f"{w_name_sel} 업데이트됨!")
                    else:
                        st.session_state['weapon_files'].append(new_item)
                        st.success(f"{w_name_sel} 추가됨!")
                else:
                    st.error("사진을 선택해주세요.")

        if st.session_state['weapon_files']:
            st.write(f"📋 **추가된 무기 ({len(st.session_state['weapon_files'])}개):**")
            for i, item in enumerate(st.session_state['weapon_files']):
                cols = st.columns([4, 1])
                cols[0].text(f"{i+1}. {item['name']}")
                if cols[1].button("🗑️", key=f"del_{i}"):
                    st.session_state['weapon_files'].pop(i)
                    st.rerun()

        st.markdown("---")
        
        if st.button("🚀 전체 분석 시작 (Analyze)", type="primary"):
            if not st.session_state['nickname']:
                st.error("닉네임을 입력해주세요!")
            elif not rank_file and not general_files:
                st.error("랭크 사진 또는 전체 스탯 사진을 최소 1장은 올려주세요.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("📊 메인 스탯(랭크/일반) 분석 중...")
                main_data = api_client.get_main_stats(rank_file, general_files)
                progress_bar.progress(50)
                
                weapons_data = []
                if st.session_state['weapon_files']:
                    total_w = len(st.session_state['weapon_files'])
                    for i, w_item in enumerate(st.session_state['weapon_files']):
                        status_text.text(f"🔫 무기 분석 중: {w_item['name']} ({i+1}/{total_w})")
                        w_res = api_client.get_weapon_stats(w_item['name'], w_item['file'])
                        if w_res:
                            w_res['weapon_name'] = w_item['name']
                            weapons_data.append(w_res)
                        progress_bar.progress(50 + int(40 * (i+1)/total_w))
                
                progress_bar.progress(90)
                
                if main_data:
                    main_data['nickname'] = st.session_state['nickname']
                    st.session_state['data'] = main_data
                    st.session_state['final_weapons_data'] = weapons_data
                    
                    final_elo = main_data.get('season_1_rank_stats', {}).get('final_elo', 0)
                    st.session_state['score'] = final_elo
                    
                    status_text.text("👤 로블록스 프로필 불러오는 중...")
                    profile = roblox_api.get_roblox_profile(st.session_state['nickname'])
                    st.session_state['roblox_profile'] = profile
                    
                    progress_bar.progress(100)
                    st.success("✅ 분석 완료! '상세 정밀 분석' 탭을 확인하세요.")
                    st.balloons()
                else:
                    st.error("분석 실패. 사진을 확인해주세요.")

    with col_preview:
        if st.session_state['data']:
            st.info("데이터가 준비되었습니다. 상단 탭을 눌러 이동하세요.")

# 2. 상세 정밀 분석
with tab2:
    if st.session_state['data']:
        data = st.session_state['data']
        weapons = st.session_state['final_weapons_data']
        metrics = logic.calculate_basic_metrics(data, weapons)
        score = st.session_state['score']
        
        tier_name, tier_img_file = logic.get_tier_info(score)
        badges = logic.get_acquired_badges(data, metrics)

        # [헤더]
        with st.container(border=True):
            hc1, hc2, hc3 = st.columns([1, 2, 1])
            with hc1:
                if st.session_state['roblox_profile']:
                    st.image(st.session_state['roblox_profile']['avatar_url'], width=150)
            with hc2:
                st.markdown(f"## {st.session_state['nickname']}")
                st.markdown(f"##### Lv. {st.session_state['level']}")
                st.markdown(f"#### 💎 Season Score: {score:,}")
            with hc3:
                st.markdown(f"**{tier_name}**")
                tier_img_path = f"assets/ranks/{tier_img_file}"
                if os.path.exists(tier_img_path):
                    st.image(tier_img_path, width=100)
                else:
                    st.caption(f"No Image")

        # [주요 스탯]
        st.markdown("### 📊 주요 스탯 (Key Stats)")
        with st.container(border=True):
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("플레이 타임", f"{metrics['playtime']:.1f}h")
            k2.metric("선호 맵", metrics['favorite_map'])
            k3.metric("총 피해량", f"{metrics['damage_dealt']:,}")
            k4.metric("K/D 비율", metrics['kd'])
            
            st.divider()
            k5, k6, k7, k8 = st.columns(4)
            k5.metric("전체 매치 수", f"{metrics['total_duels']}")
            k6.metric("승률", f"{metrics['wr_pub']}%")
            k7.metric("라운드 승률", f"{metrics['rnd_win_rate']}%")
            k8.metric("급사 승률", f"{metrics['sd_win_rate']}%")
            
            st.divider()
            k9, k10 = st.columns(2)
            k9.metric("최고 연승", f"{metrics['best_streak']}연승")
            k10.metric("저지한 연승", f"{metrics['streak_ended']}연승 저지")

        # [랭크 스탯]
        st.markdown("### 🏆 랭크 스탯 (Ranked Stats)")
        with st.container(border=True):
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("랭크 매치 수", f"{metrics['total_ranked']}")
            r2.metric("랭크 승률", f"{metrics['wr_rank']}%")
            r3.metric("최고 점수", f"{metrics['highest_elo']:,}")
            r4.metric("최저 점수", f"{metrics['lowest_elo']:,}")

        # [무기 별 스탯] (이미지 표시)
        st.markdown("### 🔫 무기 별 상세 스탯")
        if weapons:
            total_ranked_rounds = metrics.get('total_ranked_rounds', 1) 
            if total_ranked_rounds == 0: total_ranked_rounds = 1
            
            w_insights = logic.calculate_weapon_insights(weapons, total_ranked_rounds)
            
            for w in w_insights:
                with st.container(border=True):
                    # 헤더: 이미지 + 이름
                    wc_head1, wc_head2 = st.columns([1, 6])
                    with wc_head1:
                        w_img_path = get_weapon_img_path(w['name'])
                        if w_img_path:
                            st.image(w_img_path, use_container_width=True)
                        else:
                            st.write("🔫")
                    with wc_head2:
                        st.markdown(f"#### {w['name']}") # 이모지 제거됨

                    wc1, wc2, wc3, wc4 = st.columns(4)
                    wc1.metric("총 라운드 (승률)", f"{w['total_rounds']} ({w['round_win_rate']}%)")
                    wc2.metric("총 킬", f"{w['total_kills']}")
                    wc3.metric("KPR", f"{w['kpr']}")
                    wc4.metric("명중률 / 치명타율", f"{w['hit_rate']}% / {w['crit_rate']}%")
                    
                    st.divider()
                    wc5, wc6 = st.columns(2)
                    
                    tier_colors = {"S": "#FFD700", "A": "#FF4500", "B": "#1E90FF", "C": "#32CD32", "D": "#808080"}
                    t_color = tier_colors.get(w['tier'], "#FFFFFF")
                    
                    wc5.markdown(
                        f"""
                        <div style="font-family:'CustomFont'; color:#aaaaaa; font-weight:bold; margin-bottom:5px;">
                            무기 숙련도 (승률)
                        </div>
                        <div style="font-size:32px; font-weight:bold; color:{t_color};">
                            {w['tier']} <span style="font-size:24px; color:white;">({w['ranked_win_rate']}%)</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                    wc6.metric("사용률 (랭크 라운드 기준)", f"{w['pick_rate']}%", f"{w['ranked_rounds']} Rounds")
        else:
            st.info("등록된 무기 데이터가 없습니다.")

        # [획득 칭호]
        st.markdown("### 🎖️ 획득 칭호 목록")
        if badges:
            for i in range(0, len(badges), 3):
                cols = st.columns(3)
                batch = badges[i:i+3]
                for j, b in enumerate(batch):
                    with cols[j]:
                        with st.container(border=True):
                            ic, tc = st.columns([1, 3])
                            with ic:
                                img_path = b.get('image', '')
                                if os.path.exists(img_path):
                                    st.image(img_path, use_container_width=True)
                                else:
                                    st.write("🏅")
                            with tc:
                                st.markdown(f"**{b['name']}**")
                                st.caption(b['desc'])
        else:
            st.info("획득한 칭호가 없습니다.")

        # [종합 분석]
        st.markdown("### 🧠 종합 분석 (Season Highlight)")
        if badges:
            main_badge = badges[0]
            with st.container(border=True):
                ac1, ac2 = st.columns([1, 3])
                with ac1:
                    mb_path = main_badge.get('image', '')
                    if os.path.exists(mb_path):
                        st.image(mb_path, use_container_width=True)
                with ac2:
                    st.markdown(f"## 당신의 플레이 스타일: {main_badge['name']}")
                    st.info(f"**분석 결과:** {main_badge['desc']}")
                    st.write("이 칭호는 시즌 1 동안 당신이 보여준 가장 뛰어난 퍼포먼스를 나타냅니다.")
        else:
            st.write("데이터 부족으로 분석할 수 없습니다.")

# 3. 리캡 카드
with tab3:
    if st.session_state['data'] and st.session_state['roblox_profile']:
        st.subheader("✨ 리캡 카드 확인")
        
        data = st.session_state['data']
        weapons = st.session_state['final_weapons_data']
        metrics = logic.calculate_basic_metrics(data, weapons)
        score = st.session_state['score']
        
        badges = logic.get_acquired_badges(data, metrics)
        avatar_url = st.session_state['roblox_profile']['avatar_url']
        nickname = st.session_state['nickname']
        level = st.session_state['level']
        
        _, tier_image_name = logic.get_tier_info(score)
        
        if st.button("🎨 카드 생성 (새로고침)", key="card_gen"):
            card_img = card_generator.create_player_card(
                nickname, avatar_url, metrics, badges, score, level, tier_image_name
            )
            st.session_state['generated_card'] = card_img
        
        if st.session_state['generated_card']:
            st.image(st.session_state['generated_card'], caption="Season 1 Recap")
            
            buf = BytesIO()
            st.session_state['generated_card'].save(buf, format="PNG")
            st.download_button("💾 카드 저장", buf.getvalue(), f"{nickname}_recap.png", "image/png")
    else:
        st.warning("분석을 먼저 진행해주세요.")