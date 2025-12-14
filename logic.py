# logic.py
import badges_data

def calculate_basic_metrics(data, weapons=[]):
    """데이터 구조 변경 반영 (general_stats, season_1_rank_stats)"""
    
    gen = data.get('general_stats', {})
    rank = data.get('season_1_rank_stats', {})
    
    kills = gen.get('eliminations', 0)
    deaths = gen.get('deaths', 0)
    kd = kills / deaths if deaths > 0 else kills

    # 일반전
    d_wins = gen.get('duels_played', {}).get('wins', 0)
    d_losses = gen.get('duels_played', {}).get('losses', 0)
    total_duels = d_wins + d_losses
    wr_pub = (d_wins / total_duels * 100) if total_duels > 0 else 0.0

    # 랭크전 (Rank Stats 사진 기반)
    r_wins = rank.get('duels_won', 0)
    r_losses = rank.get('duels_lost', 0)
    # total_ranked = r_wins + r_losses 
    # API가 total played를 주면 그거 쓰고 없으면 합산
    total_ranked = rank.get('duels_played', r_wins + r_losses)
    wr_rank = rank.get('win_rate', 0.0)
    if wr_rank == 0 and total_ranked > 0:
        wr_rank = (r_wins / total_ranked * 100)

    gap = wr_rank - wr_pub

    # 뱃지용 추가 지표
    sd_wins = gen.get('duels_played', {}).get('sudden_death_wins', 0)
    sd_losses = gen.get('duels_played', {}).get('sudden_death_losses', 0)
    sd_total = sd_wins + sd_losses
    sd_win_rate = (sd_wins / sd_total * 100) if sd_total > 0 else 0.0

    weapon_mastery_a_count = 0
    for w in weapons:
        # 무기별 win %가 60% 이상이면 A급으로 간주 (또는 킬수 등 기준 변경 가능)
        # 기존 로직: KPH 70 이상
        kph = (w.get('eliminations', 0) / w.get('playtime_hours', 1)) if w.get('playtime_hours', 0) > 0 else 0
        if kph >= 70:
            weapon_mastery_a_count += 1

    return {
        "kd": round(kd, 2),
        "wr_pub": round(wr_pub, 1),
        "wr_rank": round(wr_rank, 1),
        "gap": round(gap, 1),
        "total_duels": total_duels,
        "total_ranked": total_ranked,
        "total_kills": kills,
        "playtime": gen.get('playtime_hours', 0),
        "sd_total": sd_total,
        "sd_win_rate": sd_win_rate,
        "weapon_mastery_a_count": weapon_mastery_a_count,
        "final_elo": rank.get('final_elo', 0), # 점수
        "weapons": weapons
    }

def calculate_season_score(data, metrics):
    # 점수는 Final ELO를 우선 사용
    if metrics.get('final_elo', 0) > 0:
        return metrics['final_elo']
    
    # ELO가 없으면 계산식 사용 (Fallback)
    gen = data.get('general_stats', {})
    score = 0
    score += gen.get('eliminations', 0) * 1
    score += gen.get('duels_played', {}).get('wins', 0) * 10
    score += int(gen.get('playtime_hours', 0) * 50)
    score += gen.get('duels_played', {}).get('flawless_wins', 0) * 20
    return score

def get_tier_image_name(score):
    if score < 600: return "b3.webp"
    elif score < 1200: return "s3.webp"
    elif score < 1800: return "g3.webp"
    elif score < 2400: return "p3.webp"
    elif score < 3000: return "d3.webp"
    elif score < 3600: return "o3.webp"
    elif score < 4200: return "neme.webp"
    else: return "arch.webp"

def get_acquired_badges(data, metrics):
    acquired = []
    # 데이터 구조 맞추기 (뱃지 로직이 기존 구조를 따를 수 있음)
    # badges_data.py의 lambda 함수들이 data['general_stats']를 참조하도록 수정하거나
    # 여기서 data를 flatten해서 넘겨줄 수도 있음.
    # 가장 깔끔한 건 여기서 data 구조를 badges_data가 좋아하는 형태로 래핑하는 것.
    
    # 래핑 데이터 생성 (기존 badges_data 호환용)
    flat_data = data.get('general_stats', {}).copy()
    # 루트 레벨에 필요한 키들이 있다면 추가
    
    for badge in badges_data.BADGE_LIST:
        try:
            condition = badge['condition']
            if callable(condition):
                # flat_data를 넘겨서 기존 로직 호환성 유지
                is_valid = condition(flat_data, metrics)
            else:
                is_valid = bool(condition)
            
            if is_valid:
                badge_info = badge.copy()
                if 'name_func' in badge: badge_info['name'] = badge['name_func'](flat_data, metrics)
                if 'image_func' in badge: badge_info['image'] = badge['image_func'](flat_data, metrics)
                if 'desc_func' in badge: badge_info['desc'] = badge['desc_func'](flat_data, metrics)
                
                if 'priority_func' in badge: badge_info['priority'] = badge['priority_func'](flat_data, metrics)
                else: badge_info['priority'] = badge.get('priority', 0)
                
                acquired.append(badge_info)
        except Exception as e:
            continue
    
    acquired.sort(key=lambda x: x['priority'], reverse=True)
    return acquired

def calculate_weapon_insights(weapons):
    insights = []
    for w in weapons:
        hours = w.get('playtime_hours', 0)
        kills = w.get('eliminations', 0)
        kph = (kills / hours) if hours > 0 else 0
        
        tier = "B"
        if kph >= 120: tier = "GOD"
        elif kph >= 100: tier = "SSS"
        elif kph >= 70: tier = "A"
        
        insights.append({
            "name": w.get('weapon_name', 'Unknown'),
            "hours": hours,
            "kills": kills,
            "kph": round(kph, 1),
            "tier": tier
        })
    return insights