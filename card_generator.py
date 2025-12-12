# card_generator.py
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import os

def create_player_card(nickname, roblox_avatar_url, metrics, badges, season_score):
    """
    플레이어 리캡 카드를 생성하여 PIL Image 객체로 반환합니다.
    (1824x2336 해상도, 다크 네온 템플릿 bg3.png 맞춤형)
    """
    W, H = 1824, 2336

    # 1. 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    font_dir = os.path.join(assets_dir, "font")
    
    # 폰트 파일 경로
    font_main_path = os.path.join(font_dir, "PartialSansKR.otf")
    font_sub_path = os.path.join(font_dir, "GowunDodum.ttf")

    # 배경 이미지 로드 (bg.png 파일이 bg3 스타일이어야 함)
    bg_path = os.path.join(assets_dir, "bg.png")
    if os.path.exists(bg_path):
        card = Image.open(bg_path).convert("RGBA")
        card = card.resize((W, H))
    else:
        # 배경 없으면 어두운 남색
        card = Image.new("RGBA", (W, H), (10, 15, 30))

    draw = ImageDraw.Draw(card)

    # 폰트 로드 헬퍼
    def get_font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

    # 텍스트 색상 (다크 모드)
    COLOR_WHITE = (255, 255, 255)
    COLOR_GRAY = (200, 200, 200) # 설명 텍스트
    COLOR_SCORE = (255, 255, 255) # 점수
    
    # 폰트 사이즈 설정
    font_nick = get_font(font_main_path, 85)
    font_score = get_font(font_main_path, 70)
    
    # 메인 뱃지
    font_badge_main_title = get_font(font_main_path, 65)
    font_badge_main_desc = get_font(font_sub_path, 38)
    
    # 서브 뱃지
    font_badge_sub = get_font(font_main_path, 35)
    
    # 스탯
    font_stat_val = get_font(font_main_path, 60)
    font_stat_label = get_font(font_sub_path, 40)

    # =================================================================
    # [1] 상단 좌측: 원형 아바타 (Avatar)
    # =================================================================
    
    # 배경의 원형 프레임 중심점 추정 (눈대중 보정)
    # x=375, y=415 지점이 원의 중심
    avatar_center_x, avatar_center_y = 327, 605
    avatar_radius = 165 # 프레임 안쪽 반지름
    avatar_size = avatar_radius * 2

    if roblox_avatar_url:
        try:
            response = requests.get(roblox_avatar_url)
            img_raw = Image.open(BytesIO(response.content)).convert("RGBA")
            img_raw = img_raw.resize((avatar_size, avatar_size))
            
            # 원형 마스크
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            avatar_circular = ImageOps.fit(img_raw, mask.size, centering=(0.5, 0.5))
            avatar_circular.putalpha(mask)
            
            # 합성 (중심 기준 좌상단 좌표 계산)
            paste_x = avatar_center_x - avatar_radius
            paste_y = avatar_center_y - avatar_radius
            card.paste(avatar_circular, (paste_x, paste_y), avatar_circular)
        except:
            pass

    # =================================================================
    # [2] 상단 우측: 닉네임 & 점수 (Nickname & Score)
    # =================================================================
    
    # 닉네임 위치 (원 우측 상단)
    nick_x = 650
    nick_y = 500
    draw.text((nick_x, nick_y), nickname, font=font_nick, fill=COLOR_WHITE)

    # 시즌 점수 (닉네임 아래)
    score_text = f"💎 {season_score:,}"
    draw.text((nick_x + 50, nick_y + 150), score_text, font=font_score, fill=COLOR_SCORE)


    # =================================================================
    # [3] 중단: 메인 하이라이트 (Main Badge)
    # =================================================================
    
    # 긴 직사각형 박스 영역 (약 y=690 ~ 1070)
    main_box_x = 140
    main_box_y = 950 
    
    if badges:
        main_badge = badges[0] # 1순위 뱃지
        
        # (1) 뱃지 이미지 (박스 좌측)
        b_path = main_badge.get('image', '')
        b_abs_path = os.path.join(base_dir, b_path) if b_path else ""
        
        img_size = 400
        if os.path.exists(b_abs_path):
            try:
                b_img = Image.open(b_abs_path).convert("RGBA")
                b_img = b_img.resize((img_size, img_size))
                card.paste(b_img, (main_box_x + 40, main_box_y), b_img)
            except:
                pass
        else:
            # 이미지 없을 때 디버깅용 박스 (실제론 안 그림)
            # draw.rectangle([main_box_x + 40, main_box_y, main_box_x + 40 + img_size, main_box_y + img_size], outline="white")
            pass
        
        # (2) 텍스트 (이미지 우측)
        text_x = main_box_x + 380
        text_y = main_box_y + 20
        
        draw.text((text_x, text_y), main_badge['name'], font=font_badge_main_title, fill=COLOR_WHITE)
        
        # 설명 (줄바꿈 처리)
        desc = main_badge['desc']
        # 한 줄에 약 28자 정도
        lines = [desc[i:i+28] for i in range(0, len(desc), 28)]
        desc_formatted = "\n".join(lines)
        
        draw.text((text_x, text_y + 90), desc_formatted, font=font_badge_main_desc, fill=COLOR_GRAY, spacing=15)


    # =================================================================
    # [4] 하단 좌측: 서브 뱃지 (2x2 Grid)
    # =================================================================
    
    sub_badges = badges[1:5] # 2~5순위
    
    # 2x2 그리드 설정
    # 박스 1 시작점: (140, 1150)
    grid_start_x = 115
    grid_start_y = 1440
    
    # 박스 크기 및 간격 (배경 프레임 기준)
    box_w = 360
    box_h = 360
    gap_x = 50  # 좌우 간격
    gap_y = 50  # 상하 간격

    for i in range(4):
        row = i // 2
        col = i % 2
        
        # 현재 박스의 좌상단 좌표
        bx = grid_start_x + (col * (box_w + gap_x))
        by = grid_start_y + (row * (box_h + gap_y))
        
        if i < len(sub_badges):
            badge = sub_badges[i]
            
            # (1) 이미지 (박스 중앙보다 약간 위)
            b_path = badge.get('image', '')
            b_abs_path = os.path.join(base_dir, b_path) if b_path else ""
            
            icon_size = 280
            if os.path.exists(b_abs_path):
                try:
                    b_img = Image.open(b_abs_path).convert("RGBA")
                    b_img = b_img.resize((icon_size, icon_size))
                    
                    # 박스 내 중앙 정렬
                    paste_x = bx + (box_w - icon_size) // 2
                    paste_y = by + 50 # 상단 여백
                    card.paste(b_img, (paste_x, paste_y), b_img)
                except:
                    pass
            
            # (2) 뱃지 이름 (이미지 아래 중앙)
            b_name = badge['name']
            
            # 텍스트 중앙 정렬 계산
            name_bbox = draw.textbbox((0, 0), b_name, font=font_badge_sub)
            name_w = name_bbox[2] - name_bbox[0]
            
            # 이름이 박스보다 넓으면 자르기 (간단 처리)
            # if name_w > box_w - 20: ...
            
            draw.text((bx + (box_w - name_w) // 2, by + 280), b_name, font=font_badge_sub, fill=COLOR_WHITE)


    # =================================================================
    # [5] 하단 우측: 스탯 리스트 (5 Rows)
    # =================================================================
    
    # 주요 스탯 5개
    stats_data = [
        ("K/D Ratio", f"{metrics['kd']}"),
        ("Win Rate", f"{metrics['wr_pub']}%"),
        ("Ranked WR", f"{metrics['wr_rank']}%"),
        ("Total Kills", f"{metrics.get('total_kills', 0):,}"),
        ("Playtime", f"{metrics.get('playtime', 0):.1f}h")
    ]

    # 리스트 영역 시작점
    list_x_start = 980
    list_y_start = 1500
    row_height = 155 # 각 줄의 높이 (배경 프레임 간격)

    for idx, (label, val) in enumerate(stats_data):
        ly = list_y_start + (idx * row_height)
        
        # (1) 라벨 (왼쪽 정렬)
        # 아이콘이 들어갈 공간(약 100px) 띄우고 텍스트 시작
        draw.text((list_x_start + 40, ly), label, font=font_stat_label, fill=COLOR_GRAY)
        
        # (2) 값 (오른쪽 정렬)
        # 영역 끝(x=1780) 기준으로 텍스트 너비만큼 빼서 x좌표 계산
        val_bbox = draw.textbbox((0, 0), val, font=font_stat_val)
        val_w = val_bbox[2] - val_bbox[0]
        val_h = val_bbox[3] - val_bbox[1]
        
        # y좌표 미세 조정 (라벨과 베이스라인 맞추기)
        draw.text((1650 - val_w, ly - 5), val, font=font_stat_val, fill=COLOR_WHITE)

    # 푸터 (우측 하단 구석)
    draw.text((W-400, H-80), "RIVALS RECAP.GG", font=font_stat_label, fill=(150, 150, 150))

    return card