# card_generator.py
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import os

def create_player_card(nickname, roblox_avatar_url, metrics, badges, score, level, tier_image_name):
    """
    플레이어 리캡 카드를 생성합니다.
    """
    W, H = 1824, 2336

    # 1. 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    font_dir = os.path.join(assets_dir, "font")
    ranks_dir = os.path.join(assets_dir, "ranks") # [수정] 랭크 이미지 폴더 경로 추가
    
    # 폰트 파일 경로
    font_main_path = os.path.join(font_dir, "PartialSansKR.otf")
    font_sub_path = os.path.join(font_dir, "GowunDodum.ttf")

    # 배경 이미지 로드
    bg_path = os.path.join(assets_dir, "bg.png")
    if os.path.exists(bg_path):
        card = Image.open(bg_path).convert("RGBA")
        card = card.resize((W, H))
    else:
        card = Image.new("RGBA", (W, H), (10, 15, 30))

    draw = ImageDraw.Draw(card)

    def get_font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

    # 색상
    COLOR_WHITE = (255, 255, 255)
    COLOR_GRAY = (200, 200, 200)
    COLOR_SCORE = (255, 215, 0)
    COLOR_STROKE = (0, 0, 0)

    # 폰트
    font_nick = get_font(font_main_path, 85)
    font_level = get_font(font_main_path, 35)
    font_score_label = get_font(font_sub_path, 45)
    font_score_val = get_font(font_main_path, 55)
    
    font_badge_main_title = get_font(font_main_path, 65)
    font_badge_main_desc = get_font(font_sub_path, 38)
    font_badge_sub = get_font(font_main_path, 25)
    
    font_stat_val = get_font(font_main_path, 60)
    font_stat_label = get_font(font_sub_path, 40)

    # =================================================================
    # [1] 아바타
    # =================================================================
    avatar_center_x, avatar_center_y = 327, 605
    avatar_radius = 165
    avatar_size = avatar_radius * 2

    if roblox_avatar_url:
        try:
            response = requests.get(roblox_avatar_url)
            img_raw = Image.open(BytesIO(response.content)).convert("RGBA")
            img_raw = img_raw.resize((avatar_size, avatar_size))
            
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            avatar_circular = ImageOps.fit(img_raw, mask.size, centering=(0.5, 0.5))
            avatar_circular.putalpha(mask)
            
            card.paste(avatar_circular, (avatar_center_x - avatar_radius, avatar_center_y - avatar_radius), avatar_circular)
        except:
            pass

    # =================================================================
    # [2] 닉네임 & 레벨(Star)
    # =================================================================
    nick_x = 650
    nick_y = 500
    
    # 닉네임
    draw.text((nick_x, nick_y), nickname, font=font_nick, fill=COLOR_WHITE, stroke_width=6, stroke_fill=COLOR_STROKE)
    
    # 닉네임 길이 계산
    nick_bbox = draw.textbbox((0, 0), nickname, font=font_nick)
    nick_w = nick_bbox[2] - nick_bbox[0]
    
    # 별 아이콘 + 레벨
    star_path = os.path.join(assets_dir, "star.png")
    star_size = 80
    star_x = nick_x + nick_w + 30
    star_y = nick_y + 10

    if os.path.exists(star_path):
        try:
            star_img = Image.open(star_path).convert("RGBA")
            star_img = star_img.resize((star_size, star_size))
            card.paste(star_img, (int(star_x), int(star_y)), star_img)
            
            # 레벨 숫자
            level_str = str(level)
            lv_bbox = draw.textbbox((0, 0), level_str, font=font_level)
            lv_w = lv_bbox[2] - lv_bbox[0]
            lv_h = lv_bbox[3] - lv_bbox[1]
            
            star_center_x = star_x + (star_size / 2)
            star_center_y = star_y + (star_size / 2)
            
            draw.text((star_center_x - (lv_w / 2), star_center_y - (lv_h / 2) - 5), level_str, font=font_level, fill=COLOR_WHITE, stroke_width=2, stroke_fill=COLOR_STROKE)
            
        except Exception as e:
            pass

    # =================================================================
    # [3] 점수 영역 (2줄: 최종 / 최고)
    # =================================================================
    score_start_x = nick_x
    score_start_y = nick_y + 140
    line_gap = 80
    
    # [수정] 티어 아이콘 로드 (ranks 폴더에서 로드)
    # tier_image_name은 logic.py에서 "g3.webp" 등으로 옴
    tier_path = os.path.join(ranks_dir, tier_image_name) 
    
    tier_img = None
    if os.path.exists(tier_path):
        try:
            t_img = Image.open(tier_path).convert("RGBA")
            tier_img = t_img.resize((70, 70))
        except: 
            print(f"티어 이미지 로드 실패: {tier_path}")
    else:
        print(f"티어 이미지를 찾을 수 없음: {tier_path}")

    def draw_score_line(y, label, val):
        draw.text((score_start_x, y), label, font=font_score_label, fill=COLOR_GRAY)
        l_bbox = draw.textbbox((0, 0), label, font=font_score_label)
        l_w = l_bbox[2] - l_bbox[0]
        
        icon_x = score_start_x + l_w
        val_x = icon_x + 20
        
        if tier_img:
            card.paste(tier_img, (int(icon_x), int(y - 5)), tier_img)
            val_x += 60
        else:
            # 이미지 없으면 다이아 이모지
            draw.text((icon_x, y), "💎", font=font_score_val, fill=COLOR_WHITE)
            val_x += 50
            
        draw.text((val_x, y), f"{val:,} 점", font=font_score_val, fill=COLOR_SCORE)

    draw_score_line(score_start_y, "최종 점수 : ", score)
    draw_score_line(score_start_y + line_gap, "최고 점수 : ", score)


    # =================================================================
    # [4] 메인 뱃지
    # =================================================================
    main_box_x = 140
    main_box_y = 950 
    
    if badges:
        main_badge = badges[0]
        b_path = main_badge.get('image', '')
        b_abs_path = os.path.join(base_dir, b_path) if b_path else ""
        
        img_size = 400
        if os.path.exists(b_abs_path):
            try:
                b_img = Image.open(b_abs_path).convert("RGBA")
                b_img = b_img.resize((img_size, img_size))
                card.paste(b_img, (main_box_x + 40, main_box_y), b_img)
            except: pass
        
        text_x = main_box_x + 470
        text_y = main_box_y + 20
        draw.text((text_x, text_y), main_badge['name'], font=font_badge_main_title, fill=COLOR_WHITE)
        
        desc = main_badge['desc']
        lines = [desc[i:i+28] for i in range(0, len(desc), 28)]
        draw.text((text_x, text_y + 90), "\n".join(lines), font=font_badge_main_desc, fill=COLOR_GRAY, spacing=15)


    # =================================================================
    # [5] 서브 뱃지
    # =================================================================
    sub_badges = badges[1:5]
    grid_start_x = 125
    grid_start_y = 1407
    box_w, box_h = 360, 360
    gap_x, gap_y = 42, 45

    for i in range(4):
        bx = grid_start_x + ((i % 2) * (box_w + gap_x))
        by = grid_start_y + ((i // 2) * (box_h + gap_y))
        
        if i < len(sub_badges):
            badge = sub_badges[i]
            b_path = badge.get('image', '')
            b_abs_path = os.path.join(base_dir, b_path) if b_path else ""
            icon_size = 346
            
            if os.path.exists(b_abs_path):
                try:
                    b_img = Image.open(b_abs_path).convert("RGBA")
                    b_img = b_img.resize((icon_size, icon_size))
                    paste_x = bx + (box_w - icon_size) // 2
                    paste_y = by + 50
                    card.paste(b_img, (int(paste_x), int(paste_y)), b_img)
                except: pass


    # =================================================================
    # [6] 스탯 리스트
    # =================================================================
    stats_data = [
        ("K/D Ratio", f"{metrics['kd']}"),
        ("Win Rate", f"{metrics['wr_pub']}%"),
        ("Ranked WR", f"{metrics['wr_rank']}%"),
        ("Total Kills", f"{metrics.get('total_kills', 0):,}"),
        ("Playtime", f"{metrics.get('playtime', 0):.1f}h")
    ]

    list_x = 980
    list_y = 1500
    row_h = 155

    for idx, (label, val) in enumerate(stats_data):
        ly = list_y + (idx * row_h)
        draw.text((list_x + 40, ly), label, font=font_stat_label, fill=COLOR_GRAY)
        
        val_bbox = draw.textbbox((0, 0), val, font=font_stat_val)
        val_w = val_bbox[2] - val_bbox[0]
        draw.text((1650 - val_w, ly - 5), val, font=font_stat_val, fill=COLOR_WHITE)

    # 푸터
    draw.text((W-400, H-80), "RIVALS RECAP.GG", font=font_stat_label, fill=(150, 150, 150))

    return card