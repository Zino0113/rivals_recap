# roblox_api.py
# 로블록스 공식 API를 사용하여 유저 정보와 아바타 이미지를 가져옵니다.

import requests

def get_user_id(username):
    """
    닉네임(String)을 입력받아 로블록스 고유 유저 ID(Integer)를 반환합니다.
    API: https://users.roblox.com/v1/usernames/users
    """
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {
        "usernames": [username],
        "excludeBannedUsers": True
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get('data'):
            return data['data'][0]['id']
        else:
            return None # 유저를 찾을 수 없음
    except Exception as e:
        print(f"Roblox API Error (Get ID): {e}")
        return None

def get_avatar_url(user_id):
    """
    유저 ID를 입력받아 아바타 썸네일(Headshot) URL을 반환합니다.
    API: https://thumbnails.roblox.com/v1/users/avatar-headshot
    """
    # size 옵션: 48x48, 150x150, 420x420 등
    url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('data') and data['data'][0]['state'] == 'Completed':
            return data['data'][0]['imageUrl']
        else:
            return None
    except Exception as e:
        print(f"Roblox API Error (Get Image): {e}")
        return None

def get_roblox_profile(username):
    """
    닉네임 -> ID -> 이미지 URL 과정을 한 번에 처리하는 래퍼 함수
    """
    user_id = get_user_id(username)
    if user_id:
        image_url = get_avatar_url(user_id)
        return {
            "user_id": user_id,
            "avatar_url": image_url
        }
    return None