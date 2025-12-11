# app.py
import streamlit as st
import api_client
import logic
import roblox_api
import card_generator
from io import BytesIO

# --- 페이지 설정 ---
st.set_page_config(page_title="RIVALS Season 1 Recap", layout="wide", page_icon="🏆")

# CSS로 스타일 좀 더 예쁘게 (선택사항)
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .big-font { font-size:30px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
if 'data' not in st.session_state: st.session_state['data'] = None
if 'weapons' not in st.session_state: st.session_state['weapons'] = []
if 'nickname' not in st.session_state: st.session_state['nickname'] = ""
if 'roblox_profile' not in st.session_state: st.session_state['roblox_profile'] = None
if 'generated_card' not in st.session_state: st.session_state['generated_card'] = None

# --- 사이드바 (옵션) ---
with st.sidebar:
    st.header("⚙️ Recap 설정")
    # API 키 입력창은 숨겼지만, 원한다면 오버라이드 가능하게 둠
    user_api_key = st.text_input("API Key (옵션, 미입력시 기본값)", type="password")

# --- 메인 타이틀 ---
st.markdown("<h1 style='text-align: center;'>🏆 RIVALS SEASON 1 RECAP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>당신의 시즌 1 기록을 화려한 카드로 만들어 자랑하세요!</p>", unsafe_allow_html=True)

# 탭 구성: 심플하게 2단계
tab1, tab2 = st.tabs(["1️⃣ 데이터 입력 & 분석", "2️⃣ 나만의 플레이어 카드"])

# ==========================================
# 1. 데이터 입력 (Input)
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("닉네임을 입력하고 스크린샷을 업로드하면 AI가 분석합니다.")
        nick_input = st.text_input("Roblox 닉네임", value=st.session_state['nickname'])
        if nick_input: st.session_state['nickname'] = nick_input
        
        uploaded_files = st.file_uploader("스탯 스크린샷 (다중 선택)", accept_multiple_files=True, type=['jpg', 'png'])
        
        if st.button("🚀 분석 시작 (Recap 생성)", type="primary"):
            if not st.session_state['nickname']:
                st.error("닉네임을 입력해주세요!")
            elif not uploaded_files:
                st.error("스크린샷을 업로드해주세요!")
            else:
                with st.spinner("AI가 시즌 데이터를 분석 중입니다..."):
                    # API 호출 (하드코딩 키 사용)
                    result = api_client.get_gemini_response(uploaded_files, user_api_key)
                    if result:
                        st.session_state['data'] = result
                        st.session_state['data']['nickname'] = st.session_state['nickname']
                        
                        # 로블록스 프사 가져오기
                        profile = roblox_api.get_roblox_profile(st.session_state['nickname'])
                        st.session_state['roblox_profile'] = profile
                        
                        st.success("분석 완료! '나만의 플레이어 카드' 탭으로 이동하세요.")
                        st.balloons()

    with col2:
        st.write("📊 **분석 미리보기**")
        if st.session_state['data']:
            data = st.session_state['data']
            metrics = logic.calculate_basic_metrics(data)
            season_score = logic.calculate_season_score(data, metrics)
            badges = logic.get_acquired_badges(data, metrics)
            
            # 간단 요약
            st.metric("Season Score", f"{season_score:,} pts")
            st.write(f"**획득 뱃지:** {len(badges)}개")
            for b in badges[:3]:
                st.caption(f"🏅 {b['name']}")
        else:
            st.markdown("""
            **이런 분들에게 추천합니다!**
            - 📸 내 전적을 인스타/디코에 자랑하고 싶은 분
            - 🩸 내가 '거인 학살자'인지 궁금한 분
            - 🏆 시즌 1 점수가 궁금한 분
            """)

# ==========================================
# 2. 플레이어 카드 (Output)
# ==========================================
with tab2:
    if st.session_state['data'] and st.session_state['roblox_profile']:
        st.subheader("✨ Your Season 1 Player Card")
        
        # 데이터 준비
        data = st.session_state['data']
        metrics = logic.calculate_basic_metrics(data)
        season_score = logic.calculate_season_score(data, metrics)
        badges = logic.get_acquired_badges(data, metrics)
        avatar_url = st.session_state['roblox_profile']['avatar_url']
        nickname = st.session_state['nickname']
        
        # 카드 생성 (Pillow)
        if st.button("🎨 카드 생성하기 (새로고침)", key="gen_btn"):
            card_img = card_generator.create_player_card(nickname, avatar_url, metrics, badges, season_score)
            st.session_state['generated_card'] = card_img
        
        # 생성된 카드 보여주기 & 다운로드
        if st.session_state['generated_card']:
            st.image(st.session_state['generated_card'], caption="Rivals Season 1 Recap", use_column_width=True)
            
            # 다운로드 버튼
            buf = BytesIO()
            st.session_state['generated_card'].save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="💾 카드 이미지 다운로드",
                data=byte_im,
                file_name=f"{nickname}_season1_recap.png",
                mime="image/png"
            )
            
        # 하단: 칭호 상세 설명
        st.markdown("---")
        st.subheader("🏅 획득한 칭호 목록")
        cols = st.columns(3)
        for idx, badge in enumerate(badges):
            with cols[idx % 3]:
                st.info(f"**{badge['name']}**\n\n{badge['desc']}")

    else:
        st.warning("먼저 '데이터 입력' 탭에서 분석을 완료해주세요.")