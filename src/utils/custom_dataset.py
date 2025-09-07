from typing import List, Dict

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


USELESS_COLUMNS = {
    'games_details': ['TEAM_ABBREVIATION', 'TEAM_CITY', 'NICKNAME'],
    'ranking': {
    },
    'games': {
    }
}


class CustomDataset:
    def __init__(self, name):
        self.name = name
        self.data: pd.DataFrame = None
        self.version: Dict[str, pd.DataFrame] = {}
        self.version_msg: List[str] = []
        self.count = {'drop': 0}
    
    def load(self, test=False) -> pd.DataFrame:
        kwargs = PANDAS_KWARGS[self.name].copy()
        # 테스트용 일부만 읽기
        if test:
            kwargs['nrows'] = 10000
        data = pd.read_csv(DATA_DIR / f'{self.name}.csv', **kwargs)
        self.data = data
        self.version_msg.append('raw')
        self.version['raw'] = self.data.copy()
        
        return self.data
    
    def preprocess(self, drop=True) -> pd.DataFrame:
        if drop:
            drop_cols = USELESS_COLUMNS[self.name]
            self.data = self.data.drop(columns=drop_cols)
            cnt = self.count['drop']
            msg = f'drop_v{cnt}'
            self.version_msg.append(msg)
            self.version[msg] = self.data.copy()
            self.count['drop'] += 1
        
        return self.data
            