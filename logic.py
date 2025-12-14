# logic.py
import badges_data

def calculate_basic_metrics(data, weapons=[]):
    """기본 승률, K/D, 갭 차이 및 상세 분석용 모든 지표 계산"""
    
    gen = data.get('general_stats', {})
    rank = data.get('season_1_rank_stats', {})
    
    kills = gen.get('eliminations', 0)
    deaths = gen.get('deaths', 0)
    kd = kills / deaths if deaths > 0 else kills
    damage_dealt = gen.get('damage_dealt', 0)
    playtime = gen.get('playtime_hours', 0)
    favorite_map = gen.get('favorite_map', "-")

    duels = gen.get('duels_played', {})
    d_wins = duels.get('wins', 0)
    d_losses = duels.get('losses', 0)
    total_duels = d_wins + d_losses
    wr_pub = (d_wins / total_duels * 100) if total_duels > 0 else 0.0
    
    best_streak = duels.get('best_streak', 0)
    streak_ended = duels.get('streak_ended', 0)

    sd_wins = duels.get('sudden_death_wins', 0)
    sd_losses = duels.get('sudden_death_losses', 0)
    sd_total = sd_wins + sd_losses
    sd_win_rate = (sd_wins / sd_total * 100) if sd_total > 0 else 0.0

    rounds = gen.get('rounds_played', {})
    rnd_wins = rounds.get('wins', 0)
    rnd_losses = rounds.get('losses', 0)
    rnd_total = rnd_wins + rnd_losses
    rnd_wr = (rnd_wins / rnd_total * 100) if rnd_total > 0 else 0.0

    r_wins = rank.get('duels_won', 0)
    r_losses = rank.get('duels_lost', 0)
    total_ranked = rank.get('duels_played', r_wins + r_losses)
    
    # 랭크 총 라운드 수 (무기 사용 비율 계산용)
    total_ranked_rounds = rank.get('ranked_rounds_played', 0)
    
    wr_rank = rank.get('win_rate', 0.0)
    if wr_rank == 0 and total_ranked > 0:
        wr_rank = (r_wins / total_ranked * 100)

    final_elo = rank.get('final_elo', 0)
    highest_elo = rank.get('highest_elo', 0)
    lowest_elo = rank.get('lowest_elo', 0)

    gap = wr_rank - wr_pub

    # 무기 마스터리 (A등급 이상 개수) - KPH 70 이상
    weapon_mastery_a_count = 0
    for w in weapons:
        w_hours = w.get('playtime_hours', 0)
        w_kills = w.get('eliminations', 0)
        kph = (w_kills / w_hours) if w_hours > 0 else 0
        if kph >= 70:
            weapon_mastery_a_count += 1

    return {
        "kd": round(kd, 2),
        "damage_dealt": damage_dealt,
        "playtime": playtime,
        "favorite_map": favorite_map,
        "total_duels": total_duels,
        "wr_pub": round(wr_pub, 1),
        "total_kills": kills,
        "best_streak": best_streak,
        "streak_ended": streak_ended,
        "sd_total": sd_total,
        "sd_win_rate": round(sd_win_rate, 1),
        "rnd_win_rate": round(rnd_wr, 1),
        "total_ranked": total_ranked,
        "total_ranked_rounds": total_ranked_rounds,
        "wr_rank": round(wr_rank, 1),
        "final_elo": final_elo,
        "highest_elo": highest_elo,
        "lowest_elo": lowest_elo,
        "gap": round(gap, 1),
        "weapon_mastery_a_count": weapon_mastery_a_count,
        "weapons": weapons
    }

def calculate_season_score(data, metrics):
    if metrics.get('final_elo', 0) > 0:
        return metrics['final_elo']
    gen = data.get('general_stats', {})
    score = 0
    score += gen.get('eliminations', 0) * 1
    score += gen.get('duels_played', {}).get('wins', 0) * 10
    score += int(gen.get('playtime_hours', 0) * 50)
    score += gen.get('duels_played', {}).get('flawless_wins', 0) * 20
    return score

def get_tier_info(score):
    if score >= 4200: return "아크 네메시스", "arch.webp"
    if score >= 3600: return "네메시스", "neme.webp"
    
    tiers = [
        ("오닉스", 3000, "o3.webp"),
        ("다이아몬드", 2400, "d3.webp"),
        ("플래티넘", 1800, "p3.webp"),
        ("골드", 1200, "g3.webp"),
        ("실버", 600, "s3.webp"),
        ("브론즈", 0, "b3.webp")
    ]
    
    for name, base_score, img in tiers:
        if score >= base_score:
            diff = score - base_score
            if diff < 200: sub = 1
            elif diff < 400: sub = 2
            else: sub = 3
            return f"{name} {sub}", img
            
    return "언랭크", "b3.webp"

def get_acquired_badges(data, metrics):
    acquired = []
    flat_data = data.get('general_stats', {}).copy()
    
    for badge in badges_data.BADGE_LIST:
        try:
            condition = badge['condition']
            if callable(condition):
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
        except:
            continue
    
    acquired.sort(key=lambda x: x['priority'], reverse=True)
    return acquired

def calculate_weapon_insights(weapons, total_ranked_rounds=0):
    insights = []
    
    # Usage Rate 분모: 등록된 모든 무기의 '총 라운드' 합계
    total_uploaded_rounds = 0
    for w in weapons:
        rp = w.get('rounds_played', {})
        total_uploaded_rounds += rp.get('total', rp.get('wins', 0) + rp.get('losses', 0))

    for w in weapons:
        rp = w.get('rounds_played', {})
        rrp = w.get('ranked_rounds_played', {})
        acc = w.get('accuracy_stats', {})
        
        # 무기별 총 라운드
        weapon_total_rounds = rp.get('total', rp.get('wins', 0) + rp.get('losses', 0))
        kills = w.get('eliminations', 0)
        
        # KPR (Kill Per Round)
        kpr = (kills / weapon_total_rounds) if weapon_total_rounds > 0 else 0
        
        # Hit/Crit % 보정
        hit_rate = acc.get('hit_percentage', 0)
        if hit_rate <= 1.0 and hit_rate > 0: hit_rate *= 100
            
        crit_rate = acc.get('critical_hit_percentage', 0)
        if crit_rate <= 1.0 and crit_rate > 0: crit_rate *= 100

        # 랭크 라운드 스탯
        ranked_rounds = rrp.get('total', rrp.get('wins', 0) + rrp.get('losses', 0))
        ranked_win_rate = rrp.get('win_rate', 0)
        
        # 티어 산정 (랭크 승률 기준)
        if ranked_win_rate >= 70: tier = "S"
        elif ranked_win_rate >= 60: tier = "A"
        elif ranked_win_rate >= 50: tier = "B"
        elif ranked_win_rate >= 40: tier = "C"
        else: tier = "D"
        
        # 픽률 (전체 업로드된 무기 라운드 중 이 무기 비율)
        pick_rate = (weapon_total_rounds / total_uploaded_rounds * 100) if total_uploaded_rounds > 0 else 0.0
        
        insights.append({
            "name": w.get('weapon_name', 'Unknown'),
            "total_rounds": weapon_total_rounds,
            "round_win_rate": rp.get('win_rate', 0),
            "total_kills": kills,
            "kpr": round(kpr, 2),
            "hit_rate": round(hit_rate, 1),
            "crit_rate": round(crit_rate, 1),
            "ranked_rounds": ranked_rounds,
            "ranked_win_rate": ranked_win_rate,
            "tier": tier,
            "pick_rate": round(pick_rate, 1)
        })
    return insights