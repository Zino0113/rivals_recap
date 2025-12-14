# api_client.py
import google.generativeai as genai
import json
import prompt_data
import streamlit as st

# [설정] API 키 하드코딩 (배포 시 주의)
HARDCODED_API_KEY = "AIzaSyCjnuFL2p50jF0BQ7TgYCf2euweFWgss_Y"

def _configure_genai():
    genai.configure(api_key=HARDCODED_API_KEY)
    return genai.GenerativeModel('models/gemini-2.5-flash')

def get_main_stats(rank_img, general_imgs):
    """랭크 사진(1장) + 일반 스탯 사진(여러 장)을 통합 분석"""
    if not rank_img and not general_imgs:
        return None
        
    model = _configure_genai()
    img_parts = []
    
    # 랭크 이미지
    if rank_img:
        img_parts.append({"mime_type": rank_img.type, "data": rank_img.getvalue()})
    
    # 일반 이미지들
    for img in general_imgs:
        img_parts.append({"mime_type": img.type, "data": img.getvalue()})
        
    try:
        response = model.generate_content(img_parts + [prompt_data.MAIN_STATS_PROMPT])
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"메인 스탯 분석 오류: {e}")
        return None

def get_weapon_stats(weapon_name, weapon_img):
    """개별 무기 스탯 이미지 분석"""
    model = _configure_genai()
    
    img_part = {"mime_type": weapon_img.type, "data": weapon_img.getvalue()}
    
    # 무기 이름을 프롬프트에 주입
    formatted_prompt = prompt_data.WEAPON_STATS_PROMPT.format(weapon_name=weapon_name)
    
    try:
        response = model.generate_content([img_part, formatted_prompt])
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"무기({weapon_name}) 분석 오류: {e}")
        return None