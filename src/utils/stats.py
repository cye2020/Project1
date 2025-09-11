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
            'eFG%': self._efg_pct,
            'TS%': self._ts_pct,
            'USG%': self._usg_pct,
            'TO%': self._to_pct,
            'AST%': self._ast_pct,
            'PPP': self._ppp,
            'POSS': self._poss
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

    def aggregate_player_stats(self, 
                            group_cols: Optional[List[str]] = None,
                            weight_stats: Optional[List[str]] = None) -> pd.DataFrame:
        """선수별 통계 집계 (가중평균 포함)
        
        Args:
            group_cols: 그룹화할 컬럼들 (기본: ['PLAYER_ID', 'PLAYER_NAME'])
            weight_stats: 가중평균을 계산할 통계들 (기본: 모든 퍼센트 통계)
            
        Returns:
            선수별 집계된 통계 (가중평균 포함)
        """
        if group_cols is None:
            group_cols = ['PLAYER_ID', 'PLAYER_NAME']
            # 포지션 정보가 있으면 추가
            if 'START_POSITION' in self.data.columns:
                group_cols.append('START_POSITION')
        
        if weight_stats is None:
            weight_stats = ['FG%', '3P%', 'FT%', 'eFG%', 'TS%', 'USG%', 'TO%', 'AST%']
        
        # 가중평균을 위한 가중치 컬럼 생성 (USG% × MIN)
        for stat in weight_stats:
            if stat in self.data.columns:
                weight_col = f"{stat.replace('%', '')}_MIN"
                self.data[weight_col] = self.data[stat] * self.data['MIN']
        
        # 집계 딕셔너리 구성
        agg_dict = {
            'MIN': ['sum', 'mean'],
            'GAME_ID': 'nunique'
        }
        
        # 가중치 컬럼들 합계
        for stat in weight_stats:
            if stat in self.data.columns:
                weight_col = f"{stat.replace('%', '')}_MIN"
                if weight_col in self.data.columns:
                    agg_dict[weight_col] = 'sum'
        
        # 그룹화 및 집계
        grouped = (
            self.data
            .groupby(group_cols, observed=True)
            .agg(agg_dict)
            .reset_index()
        )
        
        
        # 컬럼명 정리 (멀티레벨 컬럼을 플랫하게)
        new_columns = []
        for col in grouped.columns:
            if isinstance(col, tuple):
                if col[1] == '':
                    new_columns.append(col[0])
                else:
                    new_columns.append(f"{col[0]}_{col[1]}")
            else:
                new_columns.append(col)
        grouped.columns = new_columns
        
        # 가중평균 계산
        for stat in weight_stats:
            if stat in self.data.columns:
                weight_col = f"{stat.replace('%', '')}_MIN_sum"
                min_col = 'MIN_sum'
                wavg_col = f"{stat.replace('%', '')}_WAVG"
                
                if weight_col in grouped.columns and min_col in grouped.columns:
                    wavg = (grouped[weight_col] / grouped[min_col]).mask(grouped[min_col] <= 0)
                    grouped[wavg_col] = wavg.round(2)
        
        # 컬럼명 정리
        rename_dict = {
            'MIN_mean': 'MIN_AVG',
            'GAME_ID_nunique': 'G'
        }
        grouped = grouped.rename(columns=rename_dict)
        grouped.columns = grouped.columns.str.upper()
        
        return grouped
        
    def _prepare_team_stats(self):
        """팀 파생 변수 준비"""
        if self.team_stats is None:
            # 팀별 집계
            team_stats = (
                self.data
                .groupby(['TEAM', 'GAME_ID'], observed=True)
                [['FGM', 'FGA', 'FTA', 'OREB', 'TO', 'MIN', 'PTS']]
                .sum()
                .reset_index()
            )
            
            self.team_stats = team_stats
            
            # 팀 포제션 계산
            self.team_stats['TEAM_POSS'] = self._poss(team=True)
            
            # 컬럼명 변경
            self.team_stats = self.team_stats.rename(columns={
                'MIN': 'TEAM_MIN',
                'FGM': 'TEAM_FGM',
                'PTS': 'TEAM_PTS'
            })
            
            
            # 개인 데이터에 팀 정보 병합
            self.data = self.data.merge(
                self.team_stats[['GAME_ID', 'TEAM', 'TEAM_PTS', 'TEAM_POSS', 'TEAM_MIN', 'TEAM_FGM']],
                on=['GAME_ID', 'TEAM'],
                how='left'
            )
    
    # ========== 슈팅 파생 변수 ==========
    def _efg_pct(self) -> pd.Series:
        """효과적인 필드골 성공률"""
        made = self.data['FGM'] + 0.5 * self.data['FG3M']
        attempts = self.data['FGA']
        pct = (made / attempts * 100).mask(attempts <= 0)
        return pct.clip(0, 100).round(2)
    
    def _tsa(self, team: bool = False) -> pd.Series:
        if team:
            data = self.team_stats
        else:
            data = self.data
        tsa = data['FGA'] + 0.44 * data['FTA']
        return tsa
    
    def _ts_pct(self) -> pd.Series:
        """진정한 슈팅 성공률"""
        tsa = self._tsa()
        pct = (self.data['PTS'] / (2 * tsa) * 100).mask(tsa <= 0)
        return pct.clip(0, 100).round(2)
    
    # ========== 고급 파생 변수 ==========
    
    def _poss(self, team: bool = False) -> pd.Series:
        tsa = self._tsa(team)
        if team:
            data = self.team_stats
            poss = tsa - data['TO'] + data['OREB']
        else:
            poss = tsa + self.data['TO']
        return poss
    
    def _usg_pct(self) -> pd.Series:
        """사용률"""
        player_poss = self._poss()
        usg = (
            100 * player_poss * (self.data['TEAM_MIN'] / 5) / 
            (self.data['MIN'] * self.data['TEAM_POSS'])
        ).mask(
            (self.data['MIN'] <= 0) | (self.data['TEAM_POSS'] <= 0)
        )
        return usg.clip(0, 100).round(2)
    
    def _to_pct(self) -> pd.Series:
        """턴오버 비율"""
        player_poss = self._poss()
        pct = (self.data['TO'] / player_poss * 100).mask(player_poss <= 0)
        return pct.clip(0, 100).round(2)
    
    def _ast_pct(self) -> pd.Series:
        """어시스트 비율"""
        den = (
            (self.data['MIN'] / (self.data['TEAM_MIN'] / 5.0)) * 
            self.data['TEAM_FGM']
        ) - self.data['FGM']
        
        pct = (
            100.0 * self.data['AST'] / den.replace(0, np.nan)
        ).mask(den <= 0)
        
        return pct.clip(0, 100).round(2)
    
    def _ppp(self, team=False) -> pd.Series:
        """포제션당 득점"""
        player_poss = self._poss(team)
        if team:
            data = self.team_stats
        else:
            data = self.data
        ppp = (data['PTS'] / player_poss).mask(player_poss <= 0)
        return ppp.round(2)