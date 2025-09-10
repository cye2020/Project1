import pandas as pd
import numpy as np


def sum_team_stats(
        details: pd.DataFrame, 
        stats: list = ['FGM', 'FGA', 'FTA', 'OREB', 'TO', 'MIN']
    ) -> pd.DataFrame:
    """팀 선수 총합 스탯 계산

    Args:
        details (pd.DataFrame): 경기 상세 내역
        stats (list, optional): 합산하려 하는 스탯. 기본값 = ['FGM', 'FGA', 'FTA', 'OREB', 'TO', 'MIN'].

    Returns:
        pd.DataFrame: 팀 스탯
    """
    team_stats = (
        details
        .groupby(['TEAM', 'GAME_ID'])[stats]
        .sum()
        .reset_index()
    )
    return team_stats


def create_team_stats(details: pd.DataFrame) -> pd.DataFrame:
    """팀별 경기별 집계 통계를 생성"""
    team_stats = sum_team_stats(details)
    
    # 팀 포제션 계산
    team_stats['TEAM_POSS'] = (
        team_stats['FGA'] + 
        (0.44 * team_stats['FTA']) - 
        team_stats['OREB'] + 
        team_stats['TO']
    ).round(2)
    
    # 컬럼명 변경
    team_stats = team_stats.rename(columns={
        'MIN': 'TEAM_MIN',
        'FGM': 'TEAM_FGM'
    }).round(2)
    
    
    return team_stats


def calculate_FG_PCT(details: pd.DataFrame) -> pd.Series:
    pct = (
        details['FGM']
        .div(details['FGA'])
        .mask(details['FGA'] >= 0)
        * 100
    ).round(2)
    return pct


def calculate_3p_pct(details: pd.DataFrame) -> pd.Series:
    pct = pd.Series(
        np.where(
            details['FG3A'] > 0,
            (details['FG3M'] / details['FG3A'] * 100).round(2),
            0
        )
    )
    return pct


def calculate_ft_pct(details: pd.DataFrame) -> pd.Series:
    pct = pd.Series(
        np.where(
            details['FTA'] > 0,
            (details['FTM'] / details['FTA'] * 100).round(2),
            0
        )
    )
    return pct


def calculate_efg_pct(details: pd.DataFrame) -> pd.Series:
    pct = pd.Series(
        np.where(
            details['FGA'] > 0,
            (
                details['FGM'] +
                0.5 * details['FG3M']
            ) / details['FGA'] * 100
        )
    )
    return pct


def calculate_tsa(details: pd.DataFrame) -> pd.Series:
    tsa = details['FGA'] + 0.44 * details['FTA']
    return tsa


def calculate_ts_pct(details: pd.DataFrame) -> pd.Series:
    tsa = calculate_tsa(details)
    pct = (
        details['PTS']
        .div(2 * tsa)
        .mask(tsa <= 9) * 100
    ).round(2),
    return pct


def calculate_to_pct(details: pd.DataFrame) -> pd.Series:
    tsa = calculate_tsa(details)
    den = tsa + details['TO']
    pct = (
        details['TO']
        .div(den)
        .mask(den <= 0)
    ).round(2)
    return pct


def calculate_ast_pct(details: pd.DataFrame, team_stats: pd.DataFrame = None) -> pd.Series:
    if team_stats:
        details = details.merge(
            team_stats[['GAME_ID', 'TEAM', 'TEAM_MIN', 'TEAM_FGM']],
            on=['GAME_ID', 'TEAM'],
            how='left'
        )
    den = (
            (
                details['MIN'] / (details['TEAM_MIN'] / 5.0)
            ) * details['TEAM_FGM']
        ) - details['FGM']
    
    pct = (
        100.0 * details['AST']
        .div(den.replace(0, np.nan))
        .mask(den <= 0)
    ).clip(0, 100).round(2)
    
    return pct
    


def calculate_advanced_stats(details: pd.DataFrame) -> pd.DataFrame:
    """고급 통계 지표들을 계산"""
    # 1. 기본 데이터 준비
    details['MIN'] = details['MIN'].round(2)
    
    # 2. 팀 통계 생성 및 병합
    team_stats = create_team_stats(details)
    details = details.merge(
        team_stats[['GAME_ID', 'TEAM', 'TEAM_POSS', 'TEAM_MIN', 'TEAM_FGM']],
        on=['GAME_ID', 'TEAM'],
        how='left'
    )
    
    # 3. 개인 포제션 계산
    details['PLAYER_POSS'] = (
        details['FGA'] + 
        (0.44 * details['FTA']) + 
        details['TO']
    )
    
    # 4. 사용률 (Usage Rate) 계산
    details['USG%'] = (
        100 * (
            (details['FGA'] + (0.44 * details['FTA']) + details['TO']) * details['TEAM_MIN']
        ) / (details['MIN'] * details['TEAM_POSS'])
        ).round(2)
    
    # 5. 포제션당 득점 계산
    details['PPP'] = (
        details['PTS'] / details['PLAYER_POSS']
    ).round(2)
    
    # 6. True Shooting % 계산
    details['TS%'] = details['PTS'] / (
        2 * (details['FGA'] + 0.44 * details['FTA'])
    )
    details['TS%'] = details['TS%'].round(2)
    
    # 7. Turnover % 계산
    details['TO%'] = details['TO'] / (
        details['FGA'] + 0.44 * details['FTA'] + details['TO']
    )
    details['TO%'] = details['TO%'].round(2)
    
    # 8. Assist % 계산 (Basketball Reference 공식)
    den = (
        (details['MIN'] / (details['TEAM_MIN'] / 5.0)) * 
        details['TEAM_FGM']
    ) - details['FGM']
    
    details['AST%'] = (
        100.0 * details['AST'] / den.replace(0, np.nan)
    ).clip(0, 100).round(2)
    
    return details