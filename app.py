import streamlit as st
import streamlit.components.v1 as components
import os

# 1. 페이지 설정 (디자인을 꽉 채우기 위해 wide 모드 권장)
st.set_page_config(page_title="반민특위 인물 행적 정리", layout="wide")

# 2. 데이터 파일 존재 여부 확인
data_file = "people_data.js"
html_file = "banmin_people.html"

if not os.path.exists(data_file):
    st.error(f"⚠️ {data_file} 파일이 없습니다. 데이터를 먼저 생성해주세요.")
else:
    # 3. HTML 파일 읽기
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 4. JavaScript 데이터 읽기
    with open(data_file, "r", encoding="utf-8") as f:
        js_data = f.read()

    # 5. HTML 내의 <script src="./people_data.js"></script> 부분을 실제 데이터로 교체
    # 이렇게 해야 깃허브 배포 시 경로 문제가 발생하지 않습니다.
    html_content = html_content.replace(
        '<script src="./people_data.js"></script>',
        f'<script>{js_data}</script>'
    )

    # 6. 전체 화면으로 HTML 표시
    # 스트림릿의 기본 여백을 제거하고 HTML 앱을 띄웁니다.
    st.markdown("""
        <style>
        .main .block-container {
            padding: 0;
            max-width: 100%;
        }
        iframe {
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)

    components.html(html_content, height=1200, scrolling=True)

# 7. 배포 팁 안내 (앱 하단)
with st.sidebar:
    st.info("💡 **배포 팁**\n\nGitHub에 업로드할 때 `banmin_people.html`과 `people_data.js`가 같은 경로에 있는지 꼭 확인하세요.")
