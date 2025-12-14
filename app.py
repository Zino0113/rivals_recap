# app.py
import streamlit as st
import api_client
import logic
import roblox_api
import card_generator
from io import BytesIO

st.set_page_config(page_title="RIVALS Season 1 Recap", layout="wide", page_icon="🏆")

st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .big-font { font-size:30px !important; font-weight: bold; }
    img { max-width: 100%; }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'data' not in st.session_state: st.session_state['data'] = None
if 'weapon_files' not in st.session_state: st.session_state['weapon_files'] = [] # 무기 파일 리스트
if 'final_weapons_data' not in st.session_state: st.session_state['final_weapons_data'] = []
if 'nickname' not in st.session_state: st.session_state['nickname'] = ""
if 'level' not in st.session_state: st.session_state['level'] = 1
if 'roblox_profile' not in st.session_state: st.session_state['roblox_profile'] = None
if 'generated_card' not in st.session_state: st.session_state['generated_card'] = None

with st.sidebar:
    st.header("🏆 Season 1 Recap")
    st.info("API 키는 내부 설정값을 사용합니다.")

st.markdown("<h1 style='text-align: center;'>🏆 RIVALS SEASON 1 RECAP</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["1️⃣ 데이터 입력 (사진 업로드)", "2️⃣ 리캡 카드 확인"])

# ==========================================
# 1. 데이터 입력 (Input)
# ==========================================
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
        
        # (1) 랭크 스탯
        st.markdown("#### ① 랭크 스탯 (Season 1)")
        rank_file = st.file_uploader("랭크 사진 1장 (Final ELO 포함)", type=['jpg', 'png'], key="rank_up")
        
        # (2) 전체 스탯
        st.markdown("#### ② 전체 스탯 (Statistics)")
        general_files = st.file_uploader("전체 통계 사진 (2~3장)", type=['jpg', 'png'], accept_multiple_files=True, key="gen_up")
        
        # (3) 무기 스탯
        st.markdown("#### ③ 무기 스탯 추가 (선택)")
        with st.expander("🔫 무기 사진 추가하기", expanded=True):
            w_col1, w_col2 = st.columns([2, 3])
            w_name_sel = w_col1.selectbox("무기 선택", ["Sniper", "Assault Rifle", "Shotgun", "Pistol", "Katana", "Bow", "Flamethrower", "Ice Gun", "Scythe", "Minigun"])
            w_file = w_col2.file_uploader("해당 무기 스탯 사진", type=['jpg', 'png'], key="w_up")
            
            if st.button("➕ 무기 목록에 추가"):
                if w_file:
                    # 세션에 저장 (튜플 형태: 이름, 파일객체)
                    st.session_state['weapon_files'].append({"name": w_name_sel, "file": w_file})
                    st.success(f"{w_name_sel} 사진 추가됨!")
                else:
                    st.error("사진을 선택해주세요.")

        # 추가된 무기 목록 표시
        if st.session_state['weapon_files']:
            st.write(f"📋 **추가된 무기 ({len(st.session_state['weapon_files'])}개):**")
            for idx, item in enumerate(st.session_state['weapon_files']):
                st.caption(f"{idx+1}. {item['name']}")

        st.markdown("---")
        
        # (4) 분석 버튼
        if st.button("🚀 전체 분석 시작 (Analyze)", type="primary"):
            if not st.session_state['nickname']:
                st.error("닉네임을 입력해주세요!")
            elif not rank_file and not general_files:
                st.error("랭크 사진 또는 전체 스탯 사진을 최소 1장은 올려주세요.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 1. 메인 스탯 분석
                status_text.text("📊 메인 스탯(랭크/일반) 분석 중...")
                main_data = api_client.get_main_stats(rank_file, general_files)
                progress_bar.progress(50)
                
                # 2. 무기 스탯 분석
                weapons_data = []
                if st.session_state['weapon_files']:
                    total_w = len(st.session_state['weapon_files'])
                    for i, w_item in enumerate(st.session_state['weapon_files']):
                        status_text.text(f"🔫 무기 분석 중: {w_item['name']} ({i+1}/{total_w})")
                        w_res = api_client.get_weapon_stats(w_item['name'], w_item['file'])
                        if w_res:
                            weapons_data.append(w_res)
                        progress_bar.progress(50 + int(40 * (i+1)/total_w))
                
                progress_bar.progress(90)
                
                # 3. 데이터 통합 및 저장
                if main_data:
                    # 닉네임 강제 적용
                    main_data['nickname'] = st.session_state['nickname']
                    st.session_state['data'] = main_data
                    st.session_state['final_weapons_data'] = weapons_data
                    
                    # 프로필 로드
                    status_text.text("👤 로블록스 프로필 불러오는 중...")
                    profile = roblox_api.get_roblox_profile(st.session_state['nickname'])
                    st.session_state['roblox_profile'] = profile
                    
                    progress_bar.progress(100)
                    st.success("✅ 분석 완료! 오른쪽(또는 아래) 탭에서 카드를 확인하세요.")
                    st.balloons()
                else:
                    st.error("메인 스탯 분석에 실패했습니다. 사진을 확인해주세요.")

    with col_preview:
        if st.session_state['data']:
            st.write("📊 **분석 결과 요약**")
            data = st.session_state['data']
            weapons = st.session_state['final_weapons_data']
            
            metrics = logic.calculate_basic_metrics(data, weapons)
            
            # 랭크 정보 표시
            final_elo = metrics.get('final_elo', 0)
            tier_img = logic.get_tier_image_name(final_elo)
            
            c1, c2 = st.columns(2)
            c1.metric("Final ELO", f"{final_elo:,}")
            c1.caption(f"Tier Image: {tier_img}")
            
            c2.metric("K/D Ratio", metrics['kd'])
            c2.metric("Playtime", f"{metrics['playtime']:.1f}h")
            
            st.markdown("---")
            if weapons:
                st.write("🔫 **무기 분석 결과**")
                w_insights = logic.calculate_weapon_insights(weapons)
                for w in w_insights:
                    st.caption(f"**{w['name']}**: {w['kph']} KPH ({w['tier']})")

# ==========================================
# 2. 플레이어 카드 (Output)
# ==========================================
with tab2:
    if st.session_state['data'] and st.session_state['roblox_profile']:
        st.subheader("✨ Your Season 1 Player Card")
        
        data = st.session_state['data']
        weapons = st.session_state['final_weapons_data']
        
        metrics = logic.calculate_basic_metrics(data, weapons)
        # 점수는 ELO 사용
        score = metrics.get('final_elo', 0) 
        if score == 0: score = logic.calculate_season_score(data, metrics)
            
        badges = logic.get_acquired_badges(data, metrics)
        
        avatar_url = st.session_state['roblox_profile']['avatar_url']
        nickname = st.session_state['nickname']
        level = st.session_state['level']
        tier_image_name = logic.get_tier_image_name(score)
        
        if st.button("🎨 카드 생성하기 (새로고침)", key="gen_btn"):
            card_img = card_generator.create_player_card(
                nickname=nickname, 
                roblox_avatar_url=avatar_url, 
                metrics=metrics, 
                badges=badges, 
                score=score,
                level=level,
                tier_image_name=tier_image_name
            )
            st.session_state['generated_card'] = card_img
        
        if st.session_state['generated_card']:
            st.image(st.session_state['generated_card'], caption="Rivals Season 1 Recap")
            
            buf = BytesIO()
            st.session_state['generated_card'].save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="💾 카드 이미지 다운로드",
                data=byte_im,
                file_name=f"{nickname}_season1_recap.png",
                mime="image/png"
            )
    else:
        st.info("데이터 입력 탭에서 분석을 먼저 진행해주세요.")