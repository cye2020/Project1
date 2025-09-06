# 표준 라이브러리
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

# 서드파티 라이브러리  
import pandas as pd

# 로컬 모듈
from config import DATA_DIR


# dataset을 읽을 때 넣는 키워드
PANDAS_KWARGS = {
    'games_details': {
        'dtype': {'NICKNAME': str},
        'memory_map': True,
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
    }
}


def load_dataset(name:str, test:bool=False) -> pd.DataFrame:
    kwargs = PANDAS_KWARGS[name]
    # 테스트용 일부만 읽기
    if test:
        kwargs['nrows'] = 10000
    data = pd.read_csv(DATA_DIR / f'{name}.csv', **kwargs)
    return data