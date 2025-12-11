# api_client.py
import google.generativeai as genai
import json
import prompt_data
import streamlit as st

# [주의] 테스트용 하드코딩된 API 키입니다. 실제 배포 시에는 환경변수나 Secret으로 관리해야 합니다.
HARDCODED_API_KEY = ""

def get_gemini_response(uploaded_files, api_key=None):
    """
    Gemini 2.5 Flash 모델 호출. 
    인자로 받은 key가 없으면 하드코딩된 key를 사용합니다.
    """
    # 사용자가 입력한 키가 있으면 그거 쓰고, 없으면 하드코딩 키 사용
    final_key = api_key if api_key else HARDCODED_API_KEY
    
    if not final_key:
        return None
    
    genai.configure(api_key=final_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    img_parts = []
    for uploaded_file in uploaded_files:
        img_parts.append({
            "mime_type": uploaded_file.type,
            "data": uploaded_file.getvalue()
        })
    
    try:
        response = model.generate_content(img_parts + [prompt_data.SYSTEM_PROMPT])
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
        
    except Exception as e:
        st.error(f"AI 분석 중 오류 발생: {e}")
        return None