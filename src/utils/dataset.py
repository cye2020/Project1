# 표준 라이브러리
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

# 서드파티 라이브러리  
import pandas as pd
import numpy as np

# 로컬 모듈
from config import DATA_DIR


def convert_minute(val):
    if pd.isna(val) or val == '':          # NaN 값 처리
        return 0
    if isinstance(val, str) and ':' in val:   # "MM:SS" 형식
        m, s = val.split(':')
        return int(float(m)) + int(s)/60
    else:
        return int(float(val))     # 이미 숫자인 경우


# dataset을 읽을 때 넣는 키워드
PANDAS_KWARGS = {
    'games_details': {
        'dtype': {'NICKNAME': str},
        'memory_map': True,
        'converters': {'MIN': convert_minute},
    },
    'ranking': {
        'parse_dates': ['STANDINGSDATE'],
        'date_format': '%Y-%m-%d',
        'memory_map': True,
        'dtype': {'SEASON_ID': str}
    },
    'games': {
        'parse_dates': ['GAME_DATE_EST'],
        'date_format': '%Y-%m-%d',
        # 메모리 절약
        # 'usecols': ['필요한', '컬럼만'],
        # 메모리 효율적 읽기
        'memory_map': True,
    },
    'players': {
        
    },
    'teams': {
        
    },
    'games_details_pre': {
        'dtype': {'START_POSITION': 'category', 'TEAM': 'category', 'TEAM_LVL': 'category', 'PLAYER_ID': str},
        'memory_map': True,
        'index_col': 'DATE'
    },
    'games_details_regular': {
        'dtype': {'START_POSITION': 'category', 'TEAM': 'category', 'TEAM_LVL': 'category', 'PLAYER_ID': str},
        'memory_map': True,
        'index_col': 'DATE'
    },
    'games_pre': {
        'dtype': {'HOME_TEAM': 'category', 'HOME_TEAM_LVL': 'category', 'VISITOR_TEAM': 'category', 'VISITOR_TEAM_LVL': 'category'},
        'memory_map': True,
        'index_col': 'DATE'
    },
    'games_regular': {
        'dtype': {'HOME_TEAM': 'category', 'HOME_TEAM_LVL': 'category', 'VISITOR_TEAM': 'category', 'VISITOR_TEAM_LVL': 'category'},
        'memory_map': True,
        'index_col': 'DATE'
    },
    'ranking_pre': {
        'dtype': {'CONFERENCE': 'category', 'TEAM': 'category', 'TEAM_LVL': 'category'},
        'memory_map': True,
        'index_col': 'DATE'
    },
    'ranking_regular': {
        'dtype': {'CONFERENCE': 'category', 'TEAM': 'category', 'TEAM_LVL': 'category'},
        'memory_map': True,
        'index_col': 'DATE'
    }
}


def load_dataset(name:str, season: int=None, test:bool=False) -> pd.DataFrame:
    kwargs = PANDAS_KWARGS[name].copy()
    dir = DATA_DIR
    # 테스트용 일부만 읽기
    if test:
        kwargs['nrows'] = 10000
    if season:
        dir = dir / f'{season}'
    data = pd.read_csv(dir / f'{name}.csv', **kwargs)
    return data