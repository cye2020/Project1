from pathlib import Path

# 프로젝트 경로들
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
SRC_DIR = PROJECT_ROOT / 'src'
IMAGES_DIR = PROJECT_ROOT / 'images'
SHARE_DIR = SRC_DIR / 'share'
UTILS_DIR = SRC_DIR / 'utils'



NBA_COLORS = {
    'Atlanta':        '#E03A3E',  # Hawks Red
    'Boston':         '#007A33',  # Celtics Green
    'Brooklyn':       '#000000',  # Black
    'Charlotte':      '#00788C',  # Teal
    'Chicago':        '#CE1141',  # Bulls Red
    'Cleveland':      '#860038',  # Wine
    'Dallas':         '#00538C',  # Mavericks Blue
    'Denver':         '#0E2240',  # Nuggets Navy
    'Detroit':        '#C8102E',  # Pistons Red
    'Golden State':   '#1D428A',  # Warriors Blue
    'Houston':        '#CE1141',  # Rockets Red
    'Indiana':        '#002D62',  # Pacers Navy
    'L.A. Clippers':  '#C8102E',  # Clippers Red
    'L.A. Lakers':    '#552583',  # Lakers Purple
    'Memphis':        '#5D76A9',  # Beale Street Blue
    'Miami':          '#98002E',  # Heat Red
    'Milwaukee':      '#00471B',  # Bucks Green
    'Minnesota':      '#0C2340',  # Timberwolves Navy
    'New Orleans':    '#0C2340',  # Pelicans Navy
    'New York':       '#006BB6',  # Knicks Blue
    'Oklahoma City':  '#007AC1',  # Thunder Blue
    'Orlando':        '#0077C0',  # Magic Blue
    'Philadelphia':   '#006BB6',  # 76ers Blue
    'Phoenix':        '#E56020',  # Suns Orange
    'Portland':       '#E03A3E',  # Blazers Red
    'Sacramento':     '#5A2D81',  # Kings Purple
    'San Antonio':    '#000000',  # Spurs Black
    'Toronto':        '#CE1141',  # Raptors Red
    'Utah':           '#F9A01B',  # Jazz Yellow (current scheme uses black/yellow/white)
    'Washington':     '#002B5C',  # Wizards Navy
}
