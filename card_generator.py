# card_generator.py
# Pillow 라이브러리를 사용하여 분석 결과를 이미지 카드로 생성합니다.

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

def create_player_card(nickname, roblox_avatar_url, metrics, badges, season_score):
    """
    플레이어 리캡 카드를 생성하여 PIL Image 객체로 반환합니다.
    """
    # 1. 캔버스 설정 (1200x630 - SNS 공유 최적화 사이즈)
    W, H = 1200, 630
    # 배경색 (진한 남색/보라 계열)
    bg_color = (20, 24, 40) 
    card = Image.new("RGBA", (W, H), bg_color)
    draw = ImageDraw.Draw(card)

    # 폰트 로드 (폰트 파일이 없으면 기본 폰트 사용 - 한글 깨짐 주의)
    # 실제 사용시에는 'assets/font/NanumGothicBold.ttf' 경로에 폰트를 넣어주세요.
    try:
        font_title = ImageFont.truetype("assets/font/PartialSansKR-Regular.ttf", 60)
        font_subtitle = ImageFont.truetype("assets/font/PartialSansKR-Regularr.ttf", 30)
        font_stat = ImageFont.truetype("assets/font/GowunDodum-Regular.ttf", 24)
        font_badge = ImageFont.truetype("assets/font/GowunDodum-Regular.ttf", 20)
    except:
        # 폰트 파일이 없으면 기본 로드 (한글이 안나올 수 있음)
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_stat = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # ---------------------------------------------------------
    # [좌측 영역] 아바타 & 기본 정보
    # ---------------------------------------------------------
    
    # 2. 로블록스 아바타 로드 & 붙여넣기
    if roblox_avatar_url:
        try:
            response = requests.get(roblox_avatar_url)
            avatar_img = Image.open(BytesIO(response.content)).convert("RGBA")
            avatar_img = avatar_img.resize((350, 350))
            # 좌측 중앙 배치
            card.paste(avatar_img, (50, 80), avatar_img)
        except:
            pass # 이미지 로드 실패시 패스

    # 3. 닉네임 & 시즌 점수 (좌측 하단)
    draw.text((60, 450), nickname, font=font_title, fill="white")
    draw.text((60, 520), f"SEASON 1 SCORE: {season_score}", font=font_subtitle, fill=(255, 215, 0)) # Gold color

    # ---------------------------------------------------------
    # [우측 영역] 뱃지 & 상세 스탯
    # ---------------------------------------------------------

    # 4. 대표 칭호 (Top 3 Badges)
    draw.text((450, 50), "🏆 SEASON HIGHLIGHTS", font=font_subtitle, fill=(200, 200, 200))
    
    badge_start_y = 100
    for i, badge in enumerate(badges[:3]): # 상위 3개만
        y_pos = badge_start_y + (i * 110)
        
        # 뱃지 이미지 로드 (없으면 네모 박스)
        if os.path.exists(badge.get('image', '')):
            try:
                b_img = Image.open(badge['image']).convert("RGBA")
                b_img = b_img.resize((80, 80))
                card.paste(b_img, (450, y_pos), b_img)
            except:
                draw.rectangle([450, y_pos, 530, y_pos+80], fill=(50, 50, 50))
        else:
             # 이미지 없으면 임시 박스
             draw.rectangle([450, y_pos, 530, y_pos+80], fill=(60, 60, 80), outline="white")

        # 뱃지 이름 & 설명
        draw.text((550, y_pos + 10), badge['name'], font=font_subtitle, fill="white")
        draw.text((550, y_pos + 50), badge['desc'], font=font_badge, fill=(180, 180, 180))

    # 5. 주요 지표 6개 (Grid 형태)
    draw.text((450, 450), "📊 KEY STATS", font=font_subtitle, fill=(200, 200, 200))
    
    stats = [
        ("K/D Ratio", f"{metrics['kd']}"),
        ("Win Rate", f"{metrics['wr_pub']}%"),
        ("Ranked WR", f"{metrics['wr_rank']}%"),
        ("Gap", f"{metrics['gap']}"),
        ("Total Kills", f"{metrics.get('total_kills', 0):,}"), # logic.py에서 넘겨줘야 함
        ("Playtime", f"{metrics.get('playtime', 0):.1f}h")
    ]
    
    # 2행 3열 배치
    grid_start_x = 450
    grid_start_y = 500
    col_width = 230
    row_height = 60
    
    for idx, (label, value) in enumerate(stats):
        row = idx // 3
        col = idx % 3
        x = grid_start_x + (col * col_width)
        y = grid_start_y + (row * row_height)
        
        draw.text((x, y), label, font=font_badge, fill=(150, 150, 150))
        draw.text((x, y+25), value, font=font_stat, fill="white")

    # 6. 하단 푸터 (서비스명)
    draw.text((W-200, H-40), "RIVALS RECAP.GG", font=font_badge, fill=(100, 100, 100))

    return card