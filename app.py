import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="반민특위 인물 행적 정리", layout="wide")

# 2. 커스텀 CSS 주입 (이미지의 디자인 재현)
st.markdown("""
    <style>
    /* 전체 배경색 */
    .stApp {
        background-color: #f5f0e6;
    }
    
    /* 상단 대형 헤더 박스 */
    .header-container {
        background-color: #5d2a1d;
        color: white;
        padding: 40px;
        border-radius: 25px;
        margin-bottom: 30px;
    }
    
    /* 흰색 카드 스타일 */
    .white-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #e0dcd0;
        height: 100%;
    }
    
    /* XML 요약 카드 스타일 */
    .xml-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #5d2a1d;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    
    /* 텍스트 색상 및 폰트 설정 */
    h1, h2, h3 {
        color: #3d1c14 !important;
    }
    .header-container h1 {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 상단 헤더 섹션
st.markdown("""
    <div class="header-container">
        <p style="font-size: 0.9rem; opacity: 0.8; letter-spacing: 1px;">HISTORICAL SOURCE DIGEST</p>
        <h1 style="font-size: 2.5rem; margin-bottom: 15px;">반민족행위특별조사위원회 활동 당시<br>인물 행적 정리</h1>
        <p style="line-height: 1.6; opacity: 0.9;">
            아래 표는 사용자가 제공한 XML 4개를 먼저 분석한 뒤, 반민특위 활동기 전후에 집중적으로 언급된 인물들의 친일 협력 행적, 공판 내용, 체포 정황을 수업용으로 다시 정리한 것입니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

# 4. XML 분석 요약 섹션 (4열 레이아웃)
st.subheader("XML 분석 요약")
xml_cols = st.columns(4)
xml_files = [
    {"name": "pj_001.xml", "desc": "《민족정기의 심판》 계열 자료입니다. 조직 단위의 서술이 많아 배경 자료로 유용합니다."},
    {"name": "pj_002.xml", "desc": "《반민자 대공판기》로, 체포·공판·감방생활 등 인물별 흐름 확인이 좋습니다."},
    {"name": "pj_003.xml", "desc": "《반민자 죄상기》로, 주요 인물의 친일 행적을 기사 형식으로 서술합니다."},
    {"name": "pj_004.xml", "desc": "《친일파 군상》 상권으로, 등장 인물 목록이 담겨 있어 범위 파악에 유리합니다."}
]

for i, col in enumerate(xml_cols):
    with col:
        st.markdown(f"""
            <div class="white-card">
                <b style="color:#5d2a1d;">{xml_files[i]['name']}</b><br>
                <p style="font-size: 0.85rem; color: #555; margin-top:10px;">{xml_files[i]['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. 메인 콘텐츠 (좌: 인물 리스트, 우: 상세 정보)
main_col1, main_col2 = st.columns([3, 2])

with main_col1:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.subheader("인물 표 (2,651명)")
    
    # 검색바 구현
    search_input = st.text_input("인물명, 분야, 핵심어 검색", placeholder="박흥식, 경제 등")
    
    # 샘플 데이터 (실제로는 generate_people_data.py에서 생성된 데이터를 불러와야 함)
    data = {
        "인물": ["朴興植(박흥식)", "이광수", "최남선", "노덕술"],
        "분야": ["경제", "문화", "문화", "경찰"],
        "대표 직위": ["경제·실업 인물", "문인", "사학자", "경찰"],
        "핵심 행적 요약": ["화신백화점 운영, 조선비행기회사 설립 등 친일 협력", "친일 어용단체 활동", "학병 권유 강연", "독립운동가 고문"]
    }
    df = pd.DataFrame(data)
    
    # 스트림릿 테이블 표시
    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with main_col2:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.write("📍 **상세 정보**")
    
    # 선택된 인물 상세 (예시: 박흥식)
    st.markdown("""
        <div style="background-color: #fcfaf5; padding: 15px; border-radius: 10px;">
            <span style="background-color: #eee; padding: 2px 8px; border-radius: 5px; font-size: 0.8rem;">경제</span>
            <h2 style="margin: 10px 0;">朴興植(박흥식)</h2>
            <p style="color: #666; font-size: 0.9rem;">제3부 황민화운동의 선봉 조선임전보국단의 죄악사 / 제4부 국민총력조선연맹의 해부</p>
            <hr>
            <p style="font-size: 0.95rem; line-height: 1.6;">
                화신백화점과 조선비행기회사 운영을 바탕으로 일본의 전시 동원 체제에 적극 협력한 대표적인 친일 실업가로 여러 문헌에서 반복적으로 언급됩니다.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
