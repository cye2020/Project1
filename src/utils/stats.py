import pandas as pd
import numpy as np
from typing import List, Optional


class BasketballStatsCalculator:
    """농구 파생 변수 계산기"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.team_stats = None
        
        # 사용 가능한 파생 변수 매핑
        self.stats_map = {
            'FG%': self._fg_pct,
            '3P%': self._3p_pct,
            'FT%': self._ft_pct,
            'eFG%': self._efg_pct,
            'TS%': self._ts_pct,
            'USG%': self._usg_pct,
            'TO%': self._to_pct,
            'AST%': self._ast_pct,
            'PPP': self._ppp,
        }
    
    def calculate_stats(self, stats_list: Optional[List[str]] = None) -> pd.DataFrame:
        """선택된 파생 변수 계산"""
        
        # 없다면 모든 파생 변수
        if stats_list is None:
            stats_list = list(self.stats_map.keys())
        
        # 기본 준비
        self.data['MIN'] = self.data['MIN'].round(2)
        
        # 팀 파생 변수가 필요하면 팀 파생 변수 준비
        advanced_stats = ['USG%', 'AST%']
        if any(stat in advanced_stats for stat in stats_list):
            self._prepare_team_stats()
        
        # 파생 변수 계산
        for stat in stats_list:
            if stat in self.stats_map:
                self.data[stat] = self.stats_map[stat]()
            else:
                print(f"알 수 없는 파생 변수: {stat}")
        
        return self.data
    
    def get_available_stats(self) -> List[str]:
        """사용 가능한 파생 변수 목록"""
        return list(self.stats_map.keys())
    
    def _prepare_team_stats(self):
        """팀 파생 변수 준비"""
        if self.team_stats is None:
            # 팀별 집계
            team_stats = (
                self.data
                .groupby(['TEAM', 'GAME_ID'], observed=True)
                [['FGM', 'FGA', 'FTA', 'OREB', 'TO', 'MIN']]
                .sum()
                .reset_index()
            )
            
            # 팀 포제션 계산
            team_stats['TEAM_POSS'] = self._poss(team=True)
            
            
            # 컬럼명 변경
            team_stats = team_stats.rename(columns={
                'MIN': 'TEAM_MIN',
                'FGM': 'TEAM_FGM'
            })
            
            self.team_stats = team_stats
            
            # 개인 데이터에 팀 정보 병합
            self.data = self.data.merge(
                team_stats[['GAME_ID', 'TEAM', 'TEAM_POSS', 'TEAM_MIN', 'TEAM_FGM']],
                on=['GAME_ID', 'TEAM'],
                how='left'
            )
    
    # ========== 슈팅 파생 변수 ==========
    
    def _fg_pct(self) -> pd.Series:
        """필드골 성공률"""
        return self._calc_pct('FGM', 'FGA')
    
    def _3p_pct(self) -> pd.Series:
        """3점슛 성공률"""
        return self._calc_pct('FG3M', 'FG3A')
    
    def _ft_pct(self) -> pd.Series:
        """자유투 성공률"""
        return self._calc_pct('FTM', 'FTA')
    
    def _efg_pct(self) -> pd.Series:
        """효과적인 필드골 성공률"""
        made = self.data['FGM'] + 0.5 * self.data['FG3M']
        attempts = self.data['FGA']
        pct = (made / attempts * 100).mask(attempts <= 0)
        return pct.clip(0, 100).round(1)
    
    def _tsa(self) -> pd.Series:
        tsa = self.data['FGA'] + 0.44 * self.data['FTA']
        return tsa
    
    def _ts_pct(self) -> pd.Series:
        """진정한 슈팅 성공률"""
        tsa = self._tsa()
        pct = (self.data['PTS'] / (2 * tsa) * 100).mask(tsa <= 0)
        return pct.clip(0, 100).round(1)
    
    # ========== 고급 파생 변수 ==========
    
    def _poss(self, team: bool = False) -> pd.Series:
        tsa = self._tsa()
        poss = tsa + self.data['TO']
        if team:
            poss = poss - self.data['OREB']
        return poss
    
    def _usg_pct(self) -> pd.Series:
        """사용률"""
        player_poss = self._poss()
        usg = (
            100 * player_poss * self.data['TEAM_MIN'] / 
            (self.data['MIN'] * self.data['TEAM_POSS'])
        ).mask(
            (self.data['MIN'] <= 0) | (self.data['TEAM_POSS'] <= 0)
        )
        return usg.clip(0, 100).round(1)
    
    def _to_pct(self) -> pd.Series:
        """턴오버 비율"""
        player_poss = self._poss()
        pct = (self.data['TO'] / player_poss * 100).mask(player_poss <= 0)
        return pct.clip(0, 100).round(1)
    
    def _ast_pct(self) -> pd.Series:
        """어시스트 비율"""
        den = (
            (self.data['MIN'] / (self.data['TEAM_MIN'] / 5.0)) * 
            self.data['TEAM_FGM']
        ) - self.data['FGM']
        
        pct = (
            100.0 * self.data['AST'] / den.replace(0, np.nan)
        ).mask(den <= 0)
        
        return pct.clip(0, 100).round(1)
    
    def _ppp(self) -> pd.Series:
        """포제션당 득점"""
        player_poss = self._poss()
        ppp = (self.data['PTS'] / player_poss).mask(player_poss <= 0)
        return ppp.round(2)
    
    # ========== 헬퍼 함수 ==========
    
    def _calc_pct(self, made_col: str, attempt_col: str) -> pd.Series:
        """기본 퍼센트 비율 계산"""
        pct = (
            self.data[made_col] / self.data[attempt_col] * 100
        ).mask(self.data[attempt_col] <= 0)
        return pct.round(1)