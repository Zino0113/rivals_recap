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

if 'data' not in st.session_state: st.session_state['data'] = None
if 'weapons' not in st.session_state: st.session_state['weapons'] = []
if 'nickname' not in st.session_state: st.session_state['nickname'] = ""
if 'roblox_profile' not in st.session_state: st.session_state['roblox_profile'] = None
if 'generated_card' not in st.session_state: st.session_state['generated_card'] = None

with st.sidebar:
    st.header("⚙️ Recap 설정")
    user_api_key = st.text_input("API Key (옵션)", type="password")

st.markdown("<h1 style='text-align: center;'>🏆 RIVALS SEASON 1 RECAP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>당신의 시즌 1 기록을 화려한 카드로 만들어 자랑하세요!</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["1️⃣ 데이터 입력 & 분석", "2️⃣ 나만의 플레이어 카드"])

# ==========================================
# 1. 데이터 입력 (Input)
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("닉네임 입력 -> 스크린샷 업로드 -> 무기 정보 추가(선택) -> 분석 시작")
        nick_input = st.text_input("Roblox 닉네임", value=st.session_state['nickname'])
        if nick_input: st.session_state['nickname'] = nick_input
        
        uploaded_files = st.file_uploader("스탯 스크린샷 (다중 선택)", accept_multiple_files=True, type=['jpg', 'png'])
        
        with st.expander("🔫 무기 데이터 추가 (중요: 웨폰마스터 칭호)", expanded=False):
            c_w1, c_w2, c_w3 = st.columns([2, 1, 1])
            w_name = c_w1.selectbox("무기", ["Sniper", "Assault Rifle", "Shotgun", "Pistol", "Katana", "Bow", "Flamethrower", "Ice Gun"])
            w_kills = c_w2.number_input("킬", step=10)
            w_hours = c_w3.number_input("시간(h)", step=0.5)
            if st.button("무기 추가"):
                st.session_state['weapons'].append({"name": w_name, "kills": w_kills, "hours": w_hours})
                st.success(f"{w_name} 추가됨")
        
        if st.session_state['weapons']:
            st.caption(f"등록된 무기: {len(st.session_state['weapons'])}개")

        if st.button("🚀 분석 시작 (Recap 생성)", type="primary"):
            if not st.session_state['nickname']:
                st.error("닉네임을 입력해주세요!")
            elif not uploaded_files:
                st.error("스크린샷을 업로드해주세요!")
            else:
                with st.spinner("AI가 시즌 데이터를 분석 중입니다..."):
                    result = api_client.get_gemini_response(uploaded_files, user_api_key)
                    if result:
                        st.session_state['data'] = result
                        # 데이터에 닉네임이 없거나 비어있으면 수동 입력값 사용
                        if not st.session_state['data'].get('nickname'):
                            st.session_state['data']['nickname'] = st.session_state['nickname']
                        
                        profile = roblox_api.get_roblox_profile(st.session_state['nickname'])
                        st.session_state['roblox_profile'] = profile
                        
                        st.success("분석 완료! '나만의 플레이어 카드' 탭으로 이동하세요.")
                        st.balloons()

    with col2:
        st.write("📊 **분석 미리보기**")
        if st.session_state['data']:
            data = st.session_state['data']
            metrics = logic.calculate_basic_metrics(data, st.session_state['weapons'])
            season_score = logic.calculate_season_score(data, metrics)
            badges = logic.get_acquired_badges(data, metrics)
            
            st.metric("Season Score", f"{season_score:,} pts")
            
            # [수정] Playtime 키 변경 반영
            playtime = data.get('playtime', 0)
            st.write(f"**Playtime:** {playtime:.1f}h")
            
            st.write(f"**획득 뱃지:** {len(badges)}개")
            for b in badges[:3]:
                st.caption(f"🏅 {b['name']} (점수: {int(b.get('priority', 0))})")
        else:
            st.markdown("데이터가 없습니다.")

# ==========================================
# 2. 플레이어 카드 (Output)
# ==========================================
with tab2:
    if st.session_state['data'] and st.session_state['roblox_profile']:
        st.subheader("✨ Your Season 1 Player Card")
        
        data = st.session_state['data']
        metrics = logic.calculate_basic_metrics(data, st.session_state['weapons'])
        season_score = logic.calculate_season_score(data, metrics)
        badges = logic.get_acquired_badges(data, metrics)
        
        avatar_url = st.session_state['roblox_profile']['avatar_url']
        nickname = st.session_state['nickname']
        
        if st.button("🎨 카드 생성하기 (새로고침)", key="gen_btn"):
            card_img = card_generator.create_player_card(nickname, avatar_url, metrics, badges, season_score)
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
            
        st.markdown("---")
        st.subheader("🏅 획득한 칭호 목록")
        cols = st.columns(3)
        for idx, badge in enumerate(badges):
            with cols[idx % 3]:
                st.info(f"**{badge['name']}**\n\n{badge['desc']}")

    else:
        st.warning("먼저 '데이터 입력' 탭에서 분석을 완료해주세요.")    