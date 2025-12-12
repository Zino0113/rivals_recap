# card_generator.py
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import os

def create_player_card(nickname, roblox_avatar_url, metrics, badges, season_score):
    """
    플레이어 리캡 카드를 생성하여 PIL Image 객체로 반환합니다.
    (밝은 배경 템플릿 전용)
    """
    W, H = 1200, 630 # 캔버스 크기

    # 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    font_dir = os.path.join(assets_dir, "font")
    
    # 1. 배경 이미지 로드
    bg_path = os.path.join(assets_dir, "bg.png") # 파일명을 bg.png로 통일해주세요
    if os.path.exists(bg_path):
        card = Image.open(bg_path).convert("RGBA")
        card = card.resize((W, H))
    else:
        # 배경 없으면 흰색 단색 (디버깅용)
        card = Image.new("RGBA", (W, H), (240, 240, 245))

    draw = ImageDraw.Draw(card)

    # 폰트 경로 (확장자 주의)
    font_main_path = os.path.join(font_dir, "PartialSansKR.otf")
    font_sub_path = os.path.join(font_dir, "GowunDodum.ttf")

    def get_font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            print(f"⚠️ 폰트 로드 실패: {path}")
            return ImageFont.load_default()

    # 폰트 로드 (크기 및 색상 설정)
    # 배경이 밝으므로 글씨는 어두운 색(Dark Navy) 사용
    TEXT_COLOR = (20, 24, 60) 
    HIGHLIGHT_COLOR = (80, 80, 100) # 회색 서브 텍스트
    SCORE_COLOR = (218, 165, 32) # 골드

    font_nick = get_font(font_main_path, 50)
    font_score = get_font(font_main_path, 30)
    font_section = get_font(font_main_path, 28)
    font_badge_name = get_font(font_main_path, 26)
    font_badge_desc = get_font(font_sub_path, 18)
    font_stat_val = get_font(font_main_path, 36)
    font_stat_label = get_font(font_sub_path, 16)

    # ---------------------------------------------------------
    # [좌측 영역] 원형 아바타 & 프로필
    # ---------------------------------------------------------
    
    # 아바타 위치 및 크기 (배경 템플릿의 원 위치에 맞춤)
    avatar_size = 280
    avatar_x, avatar_y = 100, 180 # 원형 프레임 대략적 위치

    if roblox_avatar_url:
        try:
            response = requests.get(roblox_avatar_url)
            img_raw = Image.open(BytesIO(response.content)).convert("RGBA")
            img_raw = img_raw.resize((avatar_size, avatar_size))
            
            # 원형 마스크 생성
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            # 원형으로 자르기
            avatar_circular = ImageOps.fit(img_raw, mask.size, centering=(0.5, 0.5))
            avatar_circular.putalpha(mask)
            
            # 합성
            card.paste(avatar_circular, (avatar_x, avatar_y), avatar_circular)
        except Exception as e:
            print(f"이미지 합성 실패: {e}")

    # 닉네임 (아바타 아래 중앙 정렬)
    # 텍스트 너비 계산하여 중앙 정렬
    nick_bbox = draw.textbbox((0, 0), nickname, font=font_nick)
    nick_w = nick_bbox[2] - nick_bbox[0]
    draw.text((avatar_x + (avatar_size//2) - (nick_w//2), avatar_y + avatar_size + 20), 
              nickname, font=font_nick, fill=TEXT_COLOR)

    # 시즌 점수
    score_text = f"SEASON 1 SCORE: {season_score:,}"
    score_bbox = draw.textbbox((0, 0), score_text, font=font_score)
    score_w = score_bbox[2] - score_bbox[0]
    draw.text((avatar_x + (avatar_size//2) - (score_w//2), avatar_y + avatar_size + 80), 
              score_text, font=font_score, fill=SCORE_COLOR)

    # ---------------------------------------------------------
    # [우측 상단] SEASON HIGHLIGHTS (뱃지)
    # ---------------------------------------------------------
    # 배경 템플릿의 윗쪽 괄호 영역 (x=450~)
    
    start_x = 480
    start_y = 150
    
    # 섹션 타이틀 (이미지에 포함되어 있다면 주석 처리 가능)
    # draw.text((start_x, 110), "SEASON HIGHLIGHTS", font=font_section, fill=HIGHLIGHT_COLOR)

    for i, badge in enumerate(badges[:2]): # 공간상 2개가 적당해보임
        bx = start_x + (i * 350) # 가로로 배치
        by = start_y
        
        # 뱃지 아이콘
        badge_path = badge.get('image', '')
        abs_badge_path = os.path.join(base_dir, badge_path) if badge_path else ""
        
        if os.path.exists(abs_badge_path):
            try:
                b_icon = Image.open(abs_badge_path).convert("RGBA")
                b_icon = b_icon.resize((70, 70))
                card.paste(b_icon, (bx, by), b_icon)
            except:
                draw.rectangle([bx, by, bx+70, by+70], fill=(200, 200, 200))
        else:
             draw.rectangle([bx, by, bx+70, by+70], fill=(200, 200, 200))

        # 뱃지 텍스트
        draw.text((bx + 85, by + 5), badge['name'], font=font_badge_name, fill=TEXT_COLOR)
        # 설명이 길면 줄바꿈 처리 로직이 필요하나, 여기선 간단히 자름
        desc = badge['desc']
        if len(desc) > 15: desc = desc[:15] + "..."
        draw.text((bx + 85, by + 40), desc, font=font_badge_desc, fill=HIGHLIGHT_COLOR)

    # ---------------------------------------------------------
    # [우측 하단] KEY STATS
    # ---------------------------------------------------------
    # 배경 템플릿의 아래쪽 괄호 영역
    
    stats_start_y = 350
    # draw.text((start_x, stats_start_y - 40), "KEY STATS", font=font_section, fill=HIGHLIGHT_COLOR)

    stats_data = [
        ("K/D RATIO", f"{metrics['kd']}"),
        ("WIN RATE", f"{metrics['wr_pub']}%"),
        ("TOTAL KILLS", f"{metrics.get('total_kills', 0):,}"),
        ("RANKED WR", f"{metrics['wr_rank']}%"),
        ("PLAYTIME", f"{metrics.get('playtime', 0):.1f}h"),
        ("GAP", f"{metrics['gap']}")
    ]

    # 2행 3열 그리드 배치
    grid_w = 230
    grid_h = 100
    
    for idx, (label, val) in enumerate(stats_data):
        row = idx // 3
        col = idx % 3
        
        sx = start_x + (col * grid_w)
        sy = stats_start_y + (row * grid_h)
        
        # 수치 (크게)
        draw.text((sx, sy), val, font=font_stat_val, fill=TEXT_COLOR)
        # 라벨 (작게)
        draw.text((sx, sy + 45), label, font=font_stat_label, fill=HIGHLIGHT_COLOR)

    # 푸터
    draw.text((W-220, H-30), "RIVALS RECAP.GG", font=font_stat_label, fill=(150, 150, 150))

    return card