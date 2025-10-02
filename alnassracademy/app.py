import streamlit as st
import pandas as pd
import base64
from PIL import Image
import io
from datetime import date

# Page configuration
st.set_page_config(
    page_title="Al Nassr Academy - Scouting Department",
    page_icon="alnassracademy.png",
    layout="wide"
)

# Custom CSS for the dashboard
def apply_custom_css():
    st.markdown("""
    <style>
        /* Main container */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Header styling */
        .header {
            background-color: #002B5B;
            color: #F9D342;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .logo {
            max-width: 150px;
            margin: 0 auto 1rem;
            display: block;
        }
        
        .title {
            color: #F9D342;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0.5rem 0;
        }
        
        .subtitle {
            color: white;
            font-size: 1.2rem;
            margin: 0;
        }
        
        /* Dashboard grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        /* Dashboard cards */
        .dashboard-card {
            background: white;
            border-radius: 10px;
            padding: 2rem 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            border: 1px solid #e0e0e0;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        
        .card-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #002B5B;
        }
        
        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin: 0.5rem 0;
            color: #002B5B;
        }
        
        /* Leagues section */
        .leagues-section {
            margin-top: 2rem;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        /* Responsive design */
        @media (max-width: 900px) {
            .dashboard-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 600px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            padding: 0.5rem;
            background: #f8f9fa;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            color: #002B5B;
            transition: all 0.2s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: #002B5B;
            color: #F9D342 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'category' not in st.session_state:
    st.session_state.category = None

# -----------------------------
# CATEGORIES
# -----------------------------
CATEGORIES = {
    'NATIONAL TEAMS': 'NATIONAL TEAMS',
    'SENIOR 1 DIV': 'SENIOR 1 DIV',
    'SENIOR 2 DIV': 'SENIOR 2 DIV',
    'U21': 'U21',
    'U18': 'U18',
    'U17': 'U17',
    'U16': 'U16',
    'U15': 'U15'
}

# Mapping categories to Excel files
CATEGORY_FILES = {
    'U21': 'SaudiLeagueU21.xlsx',
    'U18': 'SaudiLeagueU18.xlsx',
    'U17': 'SaudiLeagueU17.xlsx',
    'U16': 'SaudiLeagueU16.xlsx',
    'U15': 'SaudiLeagueU15.xlsx'
}

POSITIONS = [
    "GK", "RB", "RWB", "CB", "LB", "LWB",
    "DM/6", "CM/8", "AM/10",
    "RW/WF", "LW/WF", "ST/9", "SS/9.5"
]

FOOT = ["Right", "Left", "Both"]
CONCLUSION = ["SIGN (التوقيع معه)", "MONITOR CLOSELY (متابعة دقيقة)", "DISCARD (الاستبعاد)"]

# Load data functions
@st.cache_data
def load_teams_data():
    try:
        return pd.read_excel("Saudi_Youth_Leagues.xlsx")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_countries():
    try:
        df = pd.read_excel("countries.xlsx")
        # Assuming the countries are in the first column
        countries = df.iloc[:, 0].dropna().tolist()
        return sorted(countries)
    except Exception as e:
        st.error(f"Error loading countries: {e}")
        return ["Saudi Arabia"]  # Default fallback

@st.cache_data
def load_league_data(category):
    """Load league and team data for a specific category (combines Premier and Division 1)"""
    try:
        dfs = []
        
        if category in CATEGORY_FILES:
            # Load Premier League file
            df_premier = pd.read_excel(CATEGORY_FILES[category])
            # Standardize column name to 'Team'
            if 'Equipos' in df_premier.columns:
                df_premier = df_premier.rename(columns={'Equipos': 'Team'})
            dfs.append(df_premier)
            
            # Try to load Division 1 file if it exists
            div1_file = CATEGORY_FILES[category].replace('.xlsx', 'Div1.xlsx')
            try:
                df_div1 = pd.read_excel(div1_file)
                # Standardize column name to 'Team'
                if 'Equipos' in df_div1.columns:
                    df_div1 = df_div1.rename(columns={'Equipos': 'Team'})
                dfs.append(df_div1)
            except FileNotFoundError:
                pass  # Division 1 file doesn't exist, that's ok
            
            # Combine all dataframes
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                return combined_df
            else:
                return pd.DataFrame()
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading league data for {category}: {e}")
        return pd.DataFrame()

def save_report_to_excel(report_data):
    """Save scout report to Excel file"""
    try:
        # Try to load existing reports
        try:
            df = pd.read_excel("scouts_reports.xlsx")
        except FileNotFoundError:
            # Create new DataFrame if file doesn't exist
            df = pd.DataFrame()
        
        # Append new report
        new_report = pd.DataFrame([report_data])
        df = pd.concat([df, new_report], ignore_index=True)
        
        # Save to Excel
        df.to_excel("scouts_reports.xlsx", index=False)
        return True
    except Exception as e:
        st.error(f"Error saving report: {e}")
        return False

@st.cache_data
def load_reports():
    """Load all scout reports from Excel"""
    try:
        df = pd.read_excel("scouts_reports.xlsx")
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading reports: {e}")
        return pd.DataFrame()

def show_leagues_section():
    st.markdown("## Leagues & Teams")
    df = load_teams_data()
    
    if not df.empty:
        # League filter
        league_filter = st.selectbox("Select League:", df['League'].unique())
        filtered_teams = df[df['League'] == league_filter]
        
        # Display teams in a table
        st.dataframe(filtered_teams, use_container_width=True)
    else:
        st.warning("No data available. Please check the Excel file.")

# -----------------------------
# LANGUAGE FUNCTIONS
# -----------------------------
def toggle_language():
    if st.session_state.language == 'en':
        st.session_state.language = 'ar'
    else:
        st.session_state.language = 'en'

def get_league_name(league_key):
    league_names = {
        'en': {
            "Saudi U-18 Premier League": "Saudi U-18 Premier League",
            "Saudi U-17 Premier League": "Saudi U-17 Premier League", 
            "Saudi U-16 Premier League": "Saudi U-16 Premier League",
            "Saudi U-15 Premier League": "Saudi U-15 Premier League",
            "Saudi Elite League U-21": "Saudi Elite League U-21"
        },
        'ar': {
            "Saudi U-18 Premier League": "الدوري السعودي الممتاز تحت 18",
            "Saudi U-17 Premier League": "الدوري السعودي الممتاز تحت 17",
            "Saudi U-16 Premier League": "الدوري السعودي الممتاز تحت 16", 
            "Saudi U-15 Premier League": "الدوري السعودي الممتاز تحت 15",
            "Saudi Elite League U-21": "الدوري السعودي النخبة تحت 21"
        }
    }
    return league_names[st.session_state.language].get(league_key, league_key)

# -----------------------------
# HOME PAGE - MAIN MENU
# -----------------------------
def show_home_page():
    # Header section
    st.markdown(
        f"""
        <div class="header">
            <img src="data:image/png;base64,{base64.b64encode(open('alnassracademy.png', 'rb').read()).decode()}" class="logo">
            <h1 class="title">AL NASSR ACADEMY</h1>
            <p class="subtitle">{'Scouting Department' if st.session_state.language == 'en' else 'قسم الكشافة'}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Main menu button
    st.markdown(f"<h2 style='text-align: center; color: #002B5B; margin: 2rem 0;'>{'Select an Option' if st.session_state.language == 'en' else 'اختر خياراً'}</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🏆\n\nCATEGORY\n\nالفئات", key="btn_category", use_container_width=True):
            st.session_state.page = 'categories'
            st.rerun()

# -----------------------------
# CATEGORIES PAGE
# -----------------------------
def show_categories_page():
    # Header
    st.markdown(f"<h2 style='text-align: center; color: #002B5B;'>{'Select Category' if st.session_state.language == 'en' else 'اختر الفئة'}</h2>", unsafe_allow_html=True)
    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
    
    # Create cards for each category
    col1, col2, col3, col4 = st.columns(4)
    
    categories_list = list(CATEGORIES.keys())
    
    for idx, category in enumerate(categories_list):
        col_idx = idx % 4
        with [col1, col2, col3, col4][col_idx]:
            if st.button(f"⚽\n\n{category}", key=f"cat_{category}", use_container_width=True):
                st.session_state.category = category
                st.session_state.page = 'category_view'
                st.rerun()
    
    # Add spacing for remaining categories
    if len(categories_list) < 8:
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

# -----------------------------
# CATEGORY VIEW (with tabs)
# -----------------------------
def show_category_view():
    category = st.session_state.category
    
    if not category:
        st.session_state.page = 'categories'
        st.rerun()
        return
    
    # Header
    st.markdown(f"<h2 style='text-align: center; color: #002B5B;'>{category}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Tabs
    if st.session_state.language == 'en':
        tabs = st.tabs(["📝 CREATE REPORT", "📊 VIEW REPORTS", "🗄️ VIEW DATABASE", "📈 ANALYTICS"])
    else:
        tabs = st.tabs(["📝 إنشاء تقرير", "📊 عرض التقارير", "🗄️ قاعدة البيانات", "📈 التحليلات"])
    
    with tabs[0]:
        show_create_report_form(category)
    
    with tabs[1]:
        show_category_reports(category)
    
    with tabs[2]:
        if st.session_state.language == 'en':
            st.info("📊 Database view will be implemented soon.")
        else:
            st.info("📊 سيتم تنفيذ عرض قاعدة البيانات قريباً.")
    
    with tabs[3]:
        if st.session_state.language == 'en':
            st.info("📈 Analytics will be implemented soon.")
        else:
            st.info("📈 سيتم تنفيذ التحليلات قريباً.")

# -----------------------------
# MAIN APPLICATION
# -----------------------------
def main():
    # Apply styling
    apply_custom_css()
    
    # Language toggle button in sidebar
    with st.sidebar:
        st.markdown("### Settings / الإعدادات")
        if st.button("🇸🇦 عربي" if st.session_state.language == 'en' else "🇬🇧 English",
                    key="lang_toggle",
                    help="Toggle Language",
                    use_container_width=True):
            toggle_language()
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        if st.session_state.page != 'home':
            if st.button("🏠 " + ("Home" if st.session_state.language == 'en' else "الرئيسية"), 
                        key="btn_home",
                        use_container_width=True):
                st.session_state.page = 'home'
                st.rerun()
    
    # Show appropriate page based on session state
    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'categories':
        show_categories_page()
    elif st.session_state.page == 'category_view':
        show_category_view()

# -----------------------------
# CREATE REPORT FORM (by category)
# -----------------------------
def show_create_report_form(category):
    """Create report form customized for each category"""
    
    # Load league data for this category
    league_df = load_league_data(category)
    
    # Competition & Team section OUTSIDE the form for dynamic filtering
    if st.session_state.language == 'en':
        st.markdown('<div class="section-header">🏆 Competition & Team</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-header">🏆 المسابقة والفريق</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # League selection
        if not league_df.empty and 'League' in league_df.columns:
            leagues = sorted(league_df['League'].unique().tolist())
            if st.session_state.language == 'en':
                league = st.selectbox("League - Category *", options=[""] + leagues, key=f"league_{category}")
            else:
                league = st.selectbox("الدوري - الفئة *", options=[""] + leagues, key=f"league_{category}")
        else:
            if st.session_state.language == 'en':
                league = st.text_input("League - Category *", placeholder="Enter league name", key=f"league_{category}")
            else:
                league = st.text_input("الدوري - الفئة *", placeholder="أدخل اسم الدوري", key=f"league_{category}")
    
    with col2:
        # Team selection - filter teams by selected league
        if not league_df.empty and 'Team' in league_df.columns:
            if league and 'League' in league_df.columns:
                # Filter teams by the selected league
                filtered_teams = league_df[league_df['League'] == league]['Team'].unique().tolist()
                teams = sorted(filtered_teams) if filtered_teams else []
            else:
                # If no league selected, show all teams
                teams = sorted(league_df['Team'].unique().tolist())
            
            if st.session_state.language == 'en':
                team = st.selectbox("Player Team *", options=[""] + teams, 
                                   help="Select a league first to see teams" if not league else None,
                                   key=f"team_{category}")
            else:
                team = st.selectbox("فريق اللاعب *", options=[""] + teams,
                                   help="اختر الدوري أولاً لرؤية الفرق" if not league else None,
                                   key=f"team_{category}")
        else:
            if st.session_state.language == 'en':
                team = st.text_input("Player Team *", placeholder="Enter team name", key=f"team_{category}")
            else:
                team = st.text_input("فريق اللاعب *", placeholder="أدخل اسم الفريق", key=f"team_{category}")
    
    # Now start the form for the rest of the fields
    with st.form("scout_report_form", clear_on_submit=True):
        
        # Basic Information
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">📝 Basic Information</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-header">📝 المعلومات الأساسية</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.language == 'en':
                scout_name = st.text_input("Scout Name *", placeholder="Your name")
                player_name = st.text_input("Player Name *", placeholder="Full player name")
                report_date = st.date_input("Report Date *", value=date.today())
                number = st.number_input("Number *", min_value=0, max_value=99, value=0, help="Jersey number")
            else:
                scout_name = st.text_input("اسم الكشاف *", placeholder="اسمك")
                player_name = st.text_input("اسم اللاعب *", placeholder="الاسم الكامل للاعب")
                report_date = st.date_input("تاريخ التقرير *", value=date.today())
                number = st.number_input("الرقم *", min_value=0, max_value=99, value=0, help="رقم القميص")
        
        with col2:
            # Load countries list
            countries_list = load_countries()
            
            if st.session_state.language == 'en':
                birth_year = st.number_input("Birth Year *", min_value=1990, max_value=2015, value=2006)
                nationality = st.selectbox("Nationality *", options=[""] + countries_list)
                match_date = st.date_input("Match Date *", value=date.today())
            else:
                birth_year = st.number_input("سنة الميلاد *", min_value=1990, max_value=2015, value=2006)
                nationality = st.selectbox("الجنسية *", options=[""] + countries_list)
                match_date = st.date_input("تاريخ المباراة *", value=date.today())
        
        # Match field
        if st.session_state.language == 'en':
            match = st.text_input("Match *", placeholder="e.g., Team A vs Team B")
        else:
            match = st.text_input("المباراة *", placeholder="مثال: الفريق أ ضد الفريق ب")
        
        # Player photo upload (optional)
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">📸 Player Photo (Optional)</div>', unsafe_allow_html=True)
            player_photo = st.file_uploader("Upload player photo", type=["jpg", "jpeg", "png"], help="Optional: Upload a photo of the player")
        else:
            st.markdown('<div class="section-header">📸 صورة اللاعب (اختياري)</div>', unsafe_allow_html=True)
            player_photo = st.file_uploader("تحميل صورة اللاعب", type=["jpg", "jpeg", "png"], help="اختياري: قم بتحميل صورة اللاعب")
        
        # Display uploaded photo preview
        if player_photo is not None:
            col_photo1, col_photo2, col_photo3 = st.columns([1, 2, 1])
            with col_photo2:
                image = Image.open(player_photo)
                st.image(image, caption="Player Photo Preview" if st.session_state.language == 'en' else "معاينة صورة اللاعب", use_container_width=True)
        
        # Player Details
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">⚽ Player Details</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-header">⚽ تفاصيل اللاعب</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.language == 'en':
                position = st.selectbox("Position *", [""] + POSITIONS)
            else:
                position_ar = {
                    "GK": "حارس مرمى", "RB": "مدافع أيمن", "RWB": "مدافع جناح أيمن",
                    "CB": "مدافع وسط", "LB": "مدافع أيسر", "LWB": "مدافع جناح أيسر",
                    "DM/6": "متوسط دفاعي", "CM/8": "متوسط ميدان", "AM/10": "متوسط مهاجم",
                    "RW/WF": "جناح أيمن", "LW/WF": "جناح أيسر", "ST/9": "مهاجم صريح", "SS/9.5": "مهاجم ثاني"
                }
                position = st.selectbox("المركز *", [""] + POSITIONS,
                                      format_func=lambda x: position_ar.get(x, x) if x else "")
        
        with col2:
            if st.session_state.language == 'en':
                foot = st.selectbox("Dominant Foot *", [""] + FOOT)
            else:
                foot_ar = {"Right": "أيمن", "Left": "أيسر", "Both": "كلاهما"}
                foot = st.selectbox("القدم المفضلة *", [""] + FOOT,
                                  format_func=lambda x: foot_ar.get(x, x) if x else "")
        
        # Contract and Agent (optional)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.language == 'en':
                contract = st.text_input("Contract (Optional)", placeholder="Contract details if available")
            else:
                contract = st.text_input("العقد (اختياري)", placeholder="تفاصيل العقد إن وجدت")
        
        with col2:
            if st.session_state.language == 'en':
                agent = st.text_input("Agent (Optional)", placeholder="Agent name if available")
            else:
                agent = st.text_input("الوكيل (اختياري)", placeholder="اسم الوكيل إن وجد")
        
        # Smart Evaluation
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">💭 Smart Evaluation</div>', unsafe_allow_html=True)
            smart_eval = st.text_area("Smart Evaluation *",
                                    placeholder="Clear bullets: behavior, impacts, key data, tactical context...",
                                    height=140)
        else:
            st.markdown('<div class="section-header">💭 التقييم الذكي</div>', unsafe_allow_html=True)
            smart_eval = st.text_area("التقييم الذكي *",
                                    placeholder="نقاط واضحة: السلوك، التأثيرات، البيانات الرئيسية، السياق التكتيكي...",
                                    height=140)
        
        # Ratings
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">📊 Ratings</div>', unsafe_allow_html=True)
            st.caption("""
            **Performance (الأداء):**
            1 – Below average: Performance below team standard.
            2 – Good performance: Solid contribution, equal or slightly above team standard.
            3 – Excellent: Strong impact, one of the best players.  
            4 – Outstanding (MVP): Dominant, decisive, best player on the pitch.
            
            **Potential (الإمكانات):**
            Compared to age/position/proximity to first team:
            1 – Limited potential: Unlikely to progress beyond current level.
            2 – Able to maintain steady and reliable performance at team level.
            3 – Shows clear expectations to impact at higher levels, strong margin for development.
            4 – Exceptional talent with conditions to become decisive at elite level.
            """)
        else:
            st.markdown('<div class="section-header">📊 التقييمات</div>', unsafe_allow_html=True)
            st.caption("""
            **الأداء (Performance):**
            1 – أقل من المتوسط: أداء أقل من مستوى الفريق.
            2 – أداء جيد: مساهمة قوية، مساوية أو أعلى قليلاً من مستوى الفريق.
            3 – ممتاز: تأثير قوي، واحد من أفضل اللاعبين.
            4 – متميز (أفضل لاعب): مهيمن، حاسم، أفضل لاعب في الملعب.
            
            **الإمكانات (Potential):**
            بالمقارنة مع العمر/المركز/قربه للفريق الأول:
            1 – إمكانات محدودة: من غير المرجح أن يتقدم بعد المستوى الحالي.
            2 – قادر على الحفاظ على أداء ثابت وموثوق بمستوى الفريق.
            3 – يُظهر توقعات واضحة للتأثير بمستويات أعلى، هامش قوي للتطور.
            4 – موهبة استثنائية مع شروط ليصبح حاسماً على مستوى النخبة.
            """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.language == 'en':
                performance = st.radio("Performance (الأداء) *", options=[1, 2, 3, 4], horizontal=True)
            else:
                performance = st.radio("الأداء (Performance) *", options=[1, 2, 3, 4], horizontal=True)
        
        with col2:
            if st.session_state.language == 'en':
                potential = st.radio("Potential (الإمكانات) *", options=[1, 2, 3, 4], horizontal=True)
            else:
                potential = st.radio("الإمكانات (Potential) *", options=[1, 2, 3, 4], horizontal=True)
        
        # Conclusion
        if st.session_state.language == 'en':
            conclusion = st.selectbox("Conclusion *", [""] + CONCLUSION)
        else:
            conclusion_ar = {
                "SIGN (التوقيع معه)": "التوقيع معه",
                "MONITOR CLOSELY (متابعة دقيقة)": "متابعة دقيقة", 
                "DISCARD (الاستبعاد)": "الاستبعاد"
            }
            conclusion = st.selectbox("الخلاصة *", [""] + CONCLUSION,
                                    format_func=lambda x: conclusion_ar.get(x, x) if x else "")
        
        # Submit button
        if st.session_state.language == 'en':
            submitted = st.form_submit_button("🔘 Submit / إرسال", use_container_width=True)
        else:
            submitted = st.form_submit_button("🔘 إرسال / Submit", use_container_width=True)
        
        # Handle form submission
        if submitted:
            # Validation
            errors = []
            
            if not scout_name.strip():
                errors.append("Scout Name" if st.session_state.language == 'en' else "اسم الكشاف")
            if not player_name.strip():
                errors.append("Player Name" if st.session_state.language == 'en' else "اسم اللاعب")
            if not league:
                errors.append("League" if st.session_state.language == 'en' else "الدوري")
            if not team:
                errors.append("Team" if st.session_state.language == 'en' else "الفريق")
            if not position:
                errors.append("Position" if st.session_state.language == 'en' else "المركز")
            if not foot:
                errors.append("Dominant Foot" if st.session_state.language == 'en' else "القدم المفضلة")
            if not smart_eval.strip():
                errors.append("Smart Evaluation" if st.session_state.language == 'en' else "التقييم الذكي")
            if not conclusion:
                errors.append("Conclusion" if st.session_state.language == 'en' else "الخلاصة")
            if not nationality:
                errors.append("Nationality" if st.session_state.language == 'en' else "الجنسية")
            if not match.strip():
                errors.append("Match" if st.session_state.language == 'en' else "المباراة")
            
            if errors:
                if st.session_state.language == 'en':
                    st.error(f"Please complete all required fields: {', '.join(errors)}")
                else:
                    st.error(f"يرجى إكمال الحقول المطلوبة: {', '.join(errors)}")
                return
            
            # Prepare report data
            report_data = {
                'Category': category,
                'Scout Name': scout_name,
                'Player Name': player_name,
                'Birth Year': birth_year,
                'Nationality': nationality,
                'Number': number,
                'Position': position,
                'Dominant Foot': foot,
                'League': league,
                'Team': team,
                'Match': match,
                'Match Date': match_date.strftime('%Y-%m-%d'),
                'Report Date': report_date.strftime('%Y-%m-%d'),
                'Performance': performance,
                'Potential': potential,
                'Smart Evaluation': smart_eval,
                'Conclusion': conclusion,
                'Contract': contract if contract else '',
                'Agent': agent if agent else ''
            }
            
            # Save report to Excel
            if save_report_to_excel(report_data):
                # Clear cache to reload reports
                load_reports.clear()
                
                # Show success message
                if st.session_state.language == 'en':
                    st.success("✅ Report saved successfully!")
                else:
                    st.success("✅ تم حفظ التقرير بنجاح!")
                
                # Display submitted data
                st.subheader("📄 Report Summary" if st.session_state.language == 'en' else "📄 ملخص التقرير")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Performance" if st.session_state.language == 'en' else "الأداء", 
                             f"{performance}/4")
                with col2:
                    st.metric("Potential" if st.session_state.language == 'en' else "الإمكانات", 
                             f"{potential}/4")
                with col3:
                    st.metric("Player" if st.session_state.language == 'en' else "اللاعب", 
                             player_name)
                with col4:
                    st.metric("Team" if st.session_state.language == 'en' else "الفريق", 
                             team if team else "N/A")

# -----------------------------
# CATEGORY REPORTS VIEW
# -----------------------------
def show_category_reports(category):
    """Show reports filtered by category"""
    df = load_reports()
    
    if df.empty:
        if st.session_state.language == 'en':
            st.info("📝 No reports available yet. Create your first report!")
        else:
            st.info("📝 لا توجد تقارير متاحة بعد. قم بإنشاء تقريرك الأول!")
        return
    
    # Filter by category
    if 'Category' in df.columns:
        df = df[df['Category'] == category]
    
    if df.empty:
        if st.session_state.language == 'en':
            st.info(f"📝 No reports for {category} yet.")
        else:
            st.info(f"📝 لا توجد تقارير لـ {category} بعد.")
        return
    
    # Display count
    if st.session_state.language == 'en':
        st.markdown(f"### 📊 Reports for {category} ({len(df)} found)")
    else:
        st.markdown(f"### 📊 تقارير {category} ({len(df)} تم العثور عليها)")
    
    # Display reports in expandable cards
    for idx, row in df.iterrows():
        with st.expander(f"⚽ {row['Player Name']} - {row['Team']} ({row['Position']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**{'Scout' if st.session_state.language == 'en' else 'الكشاف'}:** {row['Scout Name']}")
                st.markdown(f"**{'Birth Year' if st.session_state.language == 'en' else 'سنة الميلاد'}:** {row['Birth Year']}")
                st.markdown(f"**{'Nationality' if st.session_state.language == 'en' else 'الجنسية'}:** {row['Nationality']}")
                st.markdown(f"**{'Number' if st.session_state.language == 'en' else 'الرقم'}:** {row.get('Number', 'N/A')}")
            
            with col2:
                st.markdown(f"**{'League' if st.session_state.language == 'en' else 'الدوري'}:** {row['League']}")
                st.markdown(f"**{'Team' if st.session_state.language == 'en' else 'الفريق'}:** {row['Team']}")
                st.markdown(f"**{'Match' if st.session_state.language == 'en' else 'المباراة'}:** {row['Match']}")
                st.markdown(f"**{'Match Date' if st.session_state.language == 'en' else 'تاريخ المباراة'}:** {row['Match Date']}")
            
            with col3:
                st.markdown(f"**{'Performance' if st.session_state.language == 'en' else 'الأداء'}:** {row['Performance']}/4")
                st.markdown(f"**{'Potential' if st.session_state.language == 'en' else 'الإمكانات'}:** {row['Potential']}/4")
                st.markdown(f"**{'Foot' if st.session_state.language == 'en' else 'القدم'}:** {row['Dominant Foot']}")
                st.markdown(f"**{'Conclusion' if st.session_state.language == 'en' else 'الخلاصة'}:** {row['Conclusion']}")
            
            st.markdown("---")
            st.markdown(f"**{'Smart Evaluation' if st.session_state.language == 'en' else 'التقييم الذكي'}:**")
            st.write(row['Smart Evaluation'])

# -----------------------------
# OLD SCOUT FORM (kept for compatibility)
# -----------------------------
def show_scout_form():
    if st.session_state.language == 'en':
        st.header("🔍 New Player Assessment")
        st.markdown("Fill out the form below to create a new scouting report")
    else:
        st.header("🔍 تقييم لاعب جديد")
        st.markdown("املأ النموذج أدناه لإنشاء تقرير كشفي جديد")
    
    with st.form("scout_report_form", clear_on_submit=True):
        # Competition & Team section inside the form
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">⚽ Competition & Team</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-header">⚽ المسابقة والفريق</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # League selection
            if st.session_state.language == 'en':
                league = st.selectbox(
                    "League - Category *",
                    options=list(LEAGUE_TEAMS.keys()),
                    key="league_selector"
                )
            else:
                league = st.selectbox(
                    "الدوري - الفئة *",
                    options=list(LEAGUE_TEAMS.keys()),
                    format_func=get_league_name,
                    key="league_selector_ar"
                )
        
        with col2:
            # Get team options based on selected league
            team_options = sorted(LEAGUE_TEAMS[league]) if league in LEAGUE_TEAMS else []
            
            if st.session_state.language == 'en':
                team = st.selectbox(
                    "Player Team *",
                    options=team_options,
                    key=f"team_select_{league}",
                    disabled=not team_options,
                    placeholder="Select a league first" if not team_options else "Select a team"
                )
            else:
                team = st.selectbox(
                    "فريق اللاعب *",
                    options=team_options,
                    key=f"team_select_ar_{league}",
                    disabled=not team_options,
                    placeholder="اختر الدوري أولاً" if not team_options else "اختر الفريق"
                )
        
        # Basic Information
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">📝 Basic Information</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-header">📝 المعلومات الأساسية</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.language == 'en':
                scout_name = st.text_input("Scout Name *", placeholder="Your name")
                player_name = st.text_input("Player Name *", placeholder="Full player name")
                report_date = st.date_input("Report Date *", value=date.today())
            else:
                scout_name = st.text_input("اسم الكشاف *", placeholder="اسمك")
                player_name = st.text_input("اسم اللاعب *", placeholder="الاسم الكامل للاعب")
                report_date = st.date_input("تاريخ التقرير *", value=date.today())
        
        with col2:
            # Load countries list
            countries_list = load_countries()
            
            if st.session_state.language == 'en':
                birth_year = st.number_input("Birth Year *", min_value=2000, max_value=2015, value=2006)
                nationality = st.selectbox("Nationality *", options=[""] + countries_list)
                match_date = st.date_input("Match Date *", value=date.today())
            else:
                birth_year = st.number_input("سنة الميلاد *", min_value=2000, max_value=2015, value=2006)
                nationality = st.selectbox("الجنسية *", options=[""] + countries_list)
                match_date = st.date_input("تاريخ المباراة *", value=date.today())
        
        # Match field
        if st.session_state.language == 'en':
            match = st.text_input("Match *", placeholder="e.g., Team A vs Team B")
        else:
            match = st.text_input("المباراة *", placeholder="مثال: الفريق أ ضد الفريق ب")
        
        # Player photo upload (optional)
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">📸 Player Photo (Optional)</div>', unsafe_allow_html=True)
            player_photo = st.file_uploader("Upload player photo", type=["jpg", "jpeg", "png"], help="Optional: Upload a photo of the player")
        else:
            st.markdown('<div class="section-header">📸 صورة اللاعب (اختياري)</div>', unsafe_allow_html=True)
            player_photo = st.file_uploader("تحميل صورة اللاعب", type=["jpg", "jpeg", "png"], help="اختياري: قم بتحميل صورة اللاعب")
        
        # Display uploaded photo preview
        if player_photo is not None:
            col_photo1, col_photo2, col_photo3 = st.columns([1, 2, 1])
            with col_photo2:
                image = Image.open(player_photo)
                st.image(image, caption="Player Photo Preview" if st.session_state.language == 'en' else "معاينة صورة اللاعب", use_container_width=True)
        
        # Position selection
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.language == 'en':
                position = st.selectbox("Position *", [""] + POSITIONS)
            else:
                position_ar = {
                    "GK": "حارس مرمى", "RB": "مدافع أيمن", "RWB": "مدافع جناح أيمن",
                    "CB": "مدافع وسط", "LB": "مدافع أيسر", "LWB": "مدافع جناح أيسر",
                    "DM/6": "متوسط دفاعي", "CM/8": "متوسط ميدان", "AM/10": "متوسط مهاجم",
                    "RW/WF": "جناح أيمن", "LW/WF": "جناح أيسر", "ST/9": "مهاجم صريح", "SS/9.5": "مهاجم ثاني"
                }
                position = st.selectbox("المركز *", [""] + POSITIONS,
                                      format_func=lambda x: position_ar.get(x, x) if x else "")
        
        with col2:
            if st.session_state.language == 'en':
                foot = st.selectbox("Dominant Foot *", [""] + FOOT)
            else:
                foot_ar = {"Right": "أيمن", "Left": "أيسر", "Both": "كلاهما"}
                foot = st.selectbox("القدم المفضلة *", [""] + FOOT,
                                  format_func=lambda x: foot_ar.get(x, x) if x else "")
        
        # Additional Information
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.language == 'en':
                contract = st.text_input("Contract (if available)")
            else:
                contract = st.text_input("العقد (إذا وجد)")
        
        with col2:
            if st.session_state.language == 'en':
                agent = st.text_input("Agent (if available)")
            else:
                agent = st.text_input("الوكيل (إذا وجد)")
        
        # Smart Evaluation
        if st.session_state.language == 'en':
            smart_eval = st.text_area("Smart Evaluation *",
                                    placeholder="Clear bullets: behavior, impacts, key data, tactical context...",
                                    height=140)
        else:
            smart_eval = st.text_area("التقييم الذكي *",
                                    placeholder="نقاط واضحة: السلوك، التأثيرات، البيانات الرئيسية، السياق التكتيكي...",
                                    height=140)
        
        # Ratings
        if st.session_state.language == 'en':
            st.markdown('<div class="section-header">📊 Ratings</div>', unsafe_allow_html=True)
            st.caption("""
            **Performance (الأداء):**
            1 – Below average: Performance below team standard.
            2 – Good performance: Solid contribution, equal or slightly above team standard.
            3 – Excellent: Strong impact, one of the best players.  
            4 – Outstanding (MVP): Dominant, decisive, best player on the pitch.
            
            **Potential (الإمكانات):**
            Compared to age/position/proximity to first team:
            1 – Limited potential: Unlikely to progress beyond current level.
            2 – Able to maintain steady and reliable performance at team level.
            3 – Shows clear expectations to impact at higher levels, strong margin for development.
            4 – Exceptional talent with conditions to become decisive at elite level.
            """)
        else:
            st.markdown('<div class="section-header">📊 التقييمات</div>', unsafe_allow_html=True)
            st.caption("""
            **الأداء (Performance):**
            1 – أقل من المتوسط: أداء أقل من مستوى الفريق.
            2 – أداء جيد: مساهمة قوية، مساوية أو أعلى قليلاً من مستوى الفريق.
            3 – ممتاز: تأثير قوي، واحد من أفضل اللاعبين.
            4 – متميز (أفضل لاعب): مهيمن، حاسم، أفضل لاعب في الملعب.
            
            **الإمكانات (Potential):**
            بالمقارنة مع العمر/المركز/قربه للفريق الأول:
            1 – إمكانات محدودة: من غير المرجح أن يتقدم بعد المستوى الحالي.
            2 – قادر على الحفاظ على أداء ثابت وموثوق بمستوى الفريق.
            3 – يُظهر توقعات واضحة للتأثير بمستويات أعلى، هامش قوي للتطور.
            4 – موهبة استثنائية مع شروط ليصبح حاسماً على مستوى النخبة.
            3 – موهبة استثنائية بشروط ليصبح حاسمًا على المستوى النخبوي.
            """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.language == 'en':
                performance = st.radio("Performance (الأداء) *", options=[1, 2, 3, 4], horizontal=True)
            else:
                performance = st.radio("الأداء (Performance) *", options=[1, 2, 3, 4], horizontal=True)
        
        with col2:
            if st.session_state.language == 'en':
                potential = st.radio("Potential (الإمكانات) *", options=[1, 2, 3, 4], horizontal=True)
            else:
                potential = st.radio("الإمكانات (Potential) *", options=[1, 2, 3, 4], horizontal=True)
        
        # Conclusion
        if st.session_state.language == 'en':
            conclusion = st.selectbox("Conclusion *", [""] + CONCLUSION)
        else:
            conclusion_ar = {
                "SIGN (التوقيع معه)": "التوقيع معه",
                "MONITOR CLOSELY (متابعة دقيقة)": "متابعة دقيقة", 
                "DISCARD (الاستبعاد)": "الاستبعاد"
            }
            conclusion = st.selectbox("الخلاصة *", [""] + CONCLUSION,
                                    format_func=lambda x: conclusion_ar.get(x, x) if x else "")
        
        # Submit button
        if st.session_state.language == 'en':
            submitted = st.form_submit_button("Submit / إرسال")
        else:
            submitted = st.form_submit_button("إرسال / Submit")
        
        # Handle form submission
        if submitted:
            # Validation
            errors = []
            
            # Get the selected team from session state if available
            selected_team = st.session_state.get('selected_team')
            
            # Check required fields
            if not scout_name.strip():
                errors.append("Scout Name" if st.session_state.language == 'en' else "اسم الكشاف")
            if not player_name.strip():
                errors.append("Player Name" if st.session_state.language == 'en' else "اسم اللاعب")
            if not st.session_state.get('selected_league'):
                errors.append("League" if st.session_state.language == 'en' else "الدوري")
            if not selected_team:
                errors.append("Team" if st.session_state.language == 'en' else "الفريق")
            if not position:
                errors.append("Position" if st.session_state.language == 'en' else "المركز")
            if not foot:
                errors.append("Dominant Foot" if st.session_state.language == 'en' else "القدم المفضلة")
            if not smart_eval.strip():
                errors.append("Smart Evaluation" if st.session_state.language == 'en' else "التقييم الذكي")
            if not conclusion:
                errors.append("Conclusion" if st.session_state.language == 'en' else "الخلاصة")
            
            if errors:
                if st.session_state.language == 'en':
                    st.error(f"Please complete all required fields: {', '.join(errors)}")
                else:
                    st.error(f"يرجى إكمال الحقول المطلوبة: {', '.join(errors)}")
                return
            
            # Prepare report data
            report_data = {
                'Scout Name': scout_name,
                'Player Name': player_name,
                'Birth Year': birth_year,
                'Nationality': nationality,
                'Position': position,
                'Dominant Foot': foot,
                'League': league,
                'Team': team,
                'Match': match,
                'Match Date': match_date.strftime('%Y-%m-%d'),
                'Report Date': report_date.strftime('%Y-%m-%d'),
                'Performance': performance,
                'Potential': potential,
                'Smart Evaluation': smart_eval,
                'Conclusion': conclusion
            }
            
            # Save report to Excel
            if save_report_to_excel(report_data):
                # Clear cache to reload reports
                load_reports.clear()
                
                # Show success message
                if st.session_state.language == 'en':
                    st.success("✅ Report saved successfully!")
                else:
                    st.success("✅ تم حفظ التقرير بنجاح!")
                
                # Display submitted data
                st.subheader("📄 Report Summary" if st.session_state.language == 'en' else "📄 ملخص التقرير")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Performance" if st.session_state.language == 'en' else "الأداء", 
                             f"{performance}/4")
                with col2:
                    st.metric("Potential" if st.session_state.language == 'en' else "الإمكانات", 
                             f"{potential}/4")
                with col3:
                    st.metric("Player" if st.session_state.language == 'en' else "اللاعب", 
                             player_name)
                with col4:
                    st.metric("Team" if st.session_state.language == 'en' else "الفريق", 
                             team if team else "N/A")

# -----------------------------
# REPORTS VIEW
# -----------------------------
def show_reports_view():
    # Load reports
    df = load_reports()
    
    if df.empty:
        if st.session_state.language == 'en':
            st.info("📝 No reports available yet. Create your first report!")
        else:
            st.info("📝 لا توجد تقارير متاحة بعد. قم بإنشاء تقريرك الأول!")
        return
    
    # Filters section
    if st.session_state.language == 'en':
        st.markdown("### 🔍 Filters")
    else:
        st.markdown("### 🔍 الفلاتر")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Player Name filter
        if st.session_state.language == 'en':
            player_names = ['All'] + sorted(df['Player Name'].unique().tolist())
            selected_player = st.selectbox("Player Name", player_names)
        else:
            player_names = ['الكل'] + sorted(df['Player Name'].unique().tolist())
            selected_player = st.selectbox("اسم اللاعب", player_names)
        
        # Position filter
        if st.session_state.language == 'en':
            positions = ['All'] + sorted(df['Position'].unique().tolist())
            selected_position = st.selectbox("Position", positions)
        else:
            positions = ['الكل'] + sorted(df['Position'].unique().tolist())
            selected_position = st.selectbox("المركز", positions)
    
    with col2:
        # Scout filter
        if st.session_state.language == 'en':
            scouts = ['All'] + sorted(df['Scout Name'].unique().tolist())
            selected_scout = st.selectbox("Scout", scouts)
        else:
            scouts = ['الكل'] + sorted(df['Scout Name'].unique().tolist())
            selected_scout = st.selectbox("الكشاف", scouts)
        
        # Team filter
        if st.session_state.language == 'en':
            teams = ['All'] + sorted(df['Team'].unique().tolist())
            selected_team = st.selectbox("Team", teams)
        else:
            teams = ['الكل'] + sorted(df['Team'].unique().tolist())
            selected_team = st.selectbox("الفريق", teams)
    
    with col3:
        # League filter
        if st.session_state.language == 'en':
            leagues = ['All'] + sorted(df['League'].unique().tolist())
            selected_league = st.selectbox("League", leagues)
        else:
            leagues = ['الكل'] + sorted(df['League'].unique().tolist())
            selected_league = st.selectbox("الدوري", leagues)
        
        # Performance filter
        if st.session_state.language == 'en':
            performance_options = ['All', '1', '2', '3', '4']
            selected_performance = st.selectbox("Performance", performance_options)
        else:
            performance_options = ['الكل', '1', '2', '3', '4']
            selected_performance = st.selectbox("الأداء", performance_options)
    
    # Potential filter (below the columns)
    if st.session_state.language == 'en':
        potential_options = ['All', '1', '2', '3', '4']
        selected_potential = st.selectbox("Potential", potential_options)
    else:
        potential_options = ['الكل', '1', '2', '3', '4']
        selected_potential = st.selectbox("الإمكانات", potential_options)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_player not in ['All', 'الكل']:
        filtered_df = filtered_df[filtered_df['Player Name'] == selected_player]
    
    if selected_position not in ['All', 'الكل']:
        filtered_df = filtered_df[filtered_df['Position'] == selected_position]
    
    if selected_scout not in ['All', 'الكل']:
        filtered_df = filtered_df[filtered_df['Scout Name'] == selected_scout]
    
    if selected_team not in ['All', 'الكل']:
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]
    
    if selected_league not in ['All', 'الكل']:
        filtered_df = filtered_df[filtered_df['League'] == selected_league]
    
    if selected_performance not in ['All', 'الكل']:
        filtered_df = filtered_df[filtered_df['Performance'] == int(selected_performance)]
    
    if selected_potential not in ['All', 'الكل']:
        filtered_df = filtered_df[filtered_df['Potential'] == int(selected_potential)]
    
    # Display results
    st.markdown("---")
    if st.session_state.language == 'en':
        st.markdown(f"### 📊 Reports ({len(filtered_df)} found)")
    else:
        st.markdown(f"### 📊 التقارير ({len(filtered_df)} تم العثور عليها)")
    
    if filtered_df.empty:
        if st.session_state.language == 'en':
            st.warning("No reports match the selected filters.")
        else:
            st.warning("لا توجد تقارير تطابق الفلاتر المحددة.")
    else:
        # Display reports in expandable cards
        for idx, row in filtered_df.iterrows():
            with st.expander(f"⚽ {row['Player Name']} - {row['Team']} ({row['Position']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**{'Scout' if st.session_state.language == 'en' else 'الكشاف'}:** {row['Scout Name']}")
                    st.markdown(f"**{'Birth Year' if st.session_state.language == 'en' else 'سنة الميلاد'}:** {row['Birth Year']}")
                    st.markdown(f"**{'Nationality' if st.session_state.language == 'en' else 'الجنسية'}:** {row['Nationality']}")
                    st.markdown(f"**{'Position' if st.session_state.language == 'en' else 'المركز'}:** {row['Position']}")
                
                with col2:
                    st.markdown(f"**{'League' if st.session_state.language == 'en' else 'الدوري'}:** {row['League']}")
                    st.markdown(f"**{'Team' if st.session_state.language == 'en' else 'الفريق'}:** {row['Team']}")
                    st.markdown(f"**{'Match' if st.session_state.language == 'en' else 'المباراة'}:** {row['Match']}")
                    st.markdown(f"**{'Match Date' if st.session_state.language == 'en' else 'تاريخ المباراة'}:** {row['Match Date']}")
                
                with col3:
                    st.markdown(f"**{'Performance' if st.session_state.language == 'en' else 'الأداء'}:** {row['Performance']}/4")
                    st.markdown(f"**{'Potential' if st.session_state.language == 'en' else 'الإمكانات'}:** {row['Potential']}/4")
                    st.markdown(f"**{'Foot' if st.session_state.language == 'en' else 'القدم'}:** {row['Dominant Foot']}")
                    st.markdown(f"**{'Conclusion' if st.session_state.language == 'en' else 'الخلاصة'}:** {row['Conclusion']}")
                
                st.markdown("---")
                st.markdown(f"**{'Smart Evaluation' if st.session_state.language == 'en' else 'التقييم الذكي'}:**")
                st.write(row['Smart Evaluation'])

# -----------------------------
# ANALYTICS
# -----------------------------
def show_analytics():
    if st.session_state.language == 'en':
        st.header("📈 Analytics Dashboard")
        st.info("📊 Analytics dashboard functionality will be implemented next.")
    else:
        st.header("📈 لوحة التحليلات")
        st.info("📊 سيتم تنفيذ وظائف لوحة التحليلات في المرحلة التالية.")

# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":
    main()
