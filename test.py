#version.15

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib
# import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# from streamlit_option_menu import option_menu
# from matplotlib.ticker import StrMethodFormatter
import requests
from urllib.request import urlopen
from PIL import Image
import os
import plotly.express as px
import xlrd


#한글깨짐 방지코드 
font_location = 'NanumGothic.ttf'
fm.fontManager.addfont(font_location)
font_name = fm.FontProperties(fname=font_location).get_name()
matplotlib.rc('font', family=font_name)
matplotlib.rc('axes', unicode_minus=False)

#Layout
st.set_page_config(
    page_title="Chemicals Inventory",
    layout="wide",
    initial_sidebar_state="expanded")


# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "Project Overview"
if "df" not in st.session_state:
    st.session_state.df = None
if "df2" not in st.session_state:
    st.session_state.df2 = None
if "df3" not in st.session_state:
    st.session_state.df3 = None
if "df4" not in st.session_state:
    st.session_state.df4 = None
if "pivot_html" not in st.session_state:
    st.session_state.pivot_html = None
if "pivot_html3" not in st.session_state:
    st.session_state.pivot_html3 = None
if "pivot_df" not in st.session_state:
    st.session_state.pivot_df = None
if "pivot_df2" not in st.session_state:
    st.session_state.pivot_df2 = None
if "pivot_df3" not in st.session_state:
    st.session_state.pivot_df3 = None
if "pivot_df4" not in st.session_state:
    st.session_state.pivot_df4 = None
if "pivot_df5" not in st.session_state:
    st.session_state.pivot_df5 = None
if 'uploaded_pdf' not in st.session_state:
    st.session_state['uploaded_pdf'] = None
if 'uploaded_hwp' not in st.session_state:
    st.session_state['uploaded_hwp'] = None
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []
    
# Sidebar buttons for page navigation
# st.title("$\small\color{blue}\mathbf{화학물질Inventory 관리시스템}$")

st.title(":compass: 화학물질Inventory 관리시스템")

def imgF():
    img = Image.open("캡처.jpg")
    new_size = (300, 100)
    img = img.resize(new_size)
#     st.image(img)  
    st.sidebar.image(img)

imgF()

st.sidebar.title("Menu")

with st.sidebar.expander(":clipboard:$\large\sf{Project Overview}$"):
    if st.button(":one: Project Overview"):
        st.session_state.page = "Project Overview"
    if st.button(":two: Government Guidelines"):
        st.session_state.page = "Government Guidelines"


# Expander 생성
with st.sidebar.expander(":bar_chart:$\large\sf{화학물질 통계보고}$"):
#     if st.button(":one:프로젝트 개요"):
#         st.session_state.page = "프로젝트 개요"
    if st.button(":one: Database_1"):
        st.session_state.page = "Database_1"
    if st.button(":two: Data_1 Analysis"):
        st.session_state.page = "Data_1 Analysis"
    if st.button(":three: Trend Graph_1"): 
        st.session_state.page = "Trend Graph_1"
    if st.button(":four: Product Components"): 
        st.session_state.page = "Product Components"

with st.sidebar.expander(":chart_with_upwards_trend:$\large\sf{유해화학물질 실적관리}$"):    
    if st.button(":one: Database_2"): 
        st.session_state.page = "Database_2"
    if st.button(":two: Data_2 Analysis"):
        st.session_state.page = "Data_2 Analysis"
    if st.button(":three: Trend Graph_2"):  
        st.session_state.page = "Trend Graph_2"
    
with st.sidebar.expander(":chart_with_downwards_trend:$\large\sf{화학물질 배출량 보고}$"):
    if st.button(":one: Database_3"): 
        st.session_state.page = "Database_3"
    if st.button(":two: Data_3 Analysis"):
        st.session_state.page = "Data_3 Analysis"
    if st.button(":three: Trend Graph_3"):  
        st.session_state.page = "Trend Graph_3"

# Page1: 프로젝트 개요
if st.session_state.page == "Project Overview":
    st.header("Project Overview")
    st.write('''
      **:pushpin:구축동기**
         
         - 화학물질 통계조사,유해화학물질 실적보고, 화학물질 배출량자료 관리시스템 부재로 데이터의 체계적 관리 미흡  
         - 정부보고자료 회사내 공유 시스템 필요 
      
      **:pushpin:구축목적**
      
         - 화학물질 통계조사 및 실적 보고 자료 체계적 관리 및 ESG 공시 화학물질 데이타 제공 
      
      **:pushpin:구축범위**
      
         - 화학물질 통계조사, 유해화학물질 실적보고, 화학물질 배출량 신고 자료
      
      **:pushpin:주요기능**
      
         - 화학물질 마스터 자료 제공
         
         - 피벗기능 제공으로 다양한 리포트 보고 기능
         
         - Data 자체 오류 검증
         
         - SAP연계 데이타 연계 관리,자료다운로드 가능
        
         
      **:pushpin:기대효과**

         - DB관리시스템 구축으로 효율적인 데이타 관리 가능, 시각화로 Trend 및 이상치 파악 가능,리포트 작성시간 단축
      
      **:pushpin:자료 sourece**
      
         - ROMYS,자재구매팀,Poylymer영업팀,PP생산팀,PE생산팀,Aromatics영업팀,생산조정팀

                                
             ''')
    
if st.session_state.page == "Government Guidelines":
    st.header("화학물질 통계조사 및 실적보고, 배출량 조사 작성 지침")
    
    # 특정 파일 경로를 지정
    file_paths = [
        '★제5차 화학물질 통계조사 지침서_최종본.pdf',
        '2022년도 유해화학물질 실적보고 안내문.pdf',
        '통계조사실적보고 사용자매뉴얼.pdf',
        '[별표 1] 화학물질 배출량 조사대상 업종 (제3조제1항 관련)(화학물질의 배출량조사 및 산정계수에 관한 규정).hwp',
        '[별표 2] 화학물질 배출량 조사대상 화학물질 (제5조제1항 관련)(화학물질의 배출량조사 및 산정계수에 관한 규정).hwp',
        '2023년 화학물질 배출량조사 안내.hwp'
    ]
    
    # 파일 목록을 저장할 곳 초기화
    if 'uploaded_files' not in st.session_state:
        st.session_state['uploaded_files'] = []

    # 이미 업로드된 파일 이름 목록
    uploaded_file_names = [f["name"] for f in st.session_state['uploaded_files']]

    # 파일 경로에서 파일을 읽고 업로드하기
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        if os.path.exists(file_path) and file_name not in uploaded_file_names:
            with open(file_path, "rb") as f:
                file_content = f.read()
                st.session_state['uploaded_files'].append({
                    "name": file_name,
                    "content": file_content
                })

    # 업로드된 파일 목록 및 다운로드 버튼 표시
    if st.session_state['uploaded_files']:
        st.success(f"{len(st.session_state['uploaded_files'])}개의 파일 다운로드 가능합니다.")
        st.subheader("다운로드 파일:")
        
        for index, uploaded_file in enumerate(st.session_state['uploaded_files']):
            with st.container():
                col1, col2 = st.columns([3, 1])
                col1.write(uploaded_file["name"])  # 파일 이름 표시
                with col2:
                    st.download_button(
                        label="다운로드",
                        data=uploaded_file["content"],
                        file_name=uploaded_file["name"],
                        key=f"file_download_{index}"
                    )
#                     if st.button("삭제", key=f"delete_{index}"):
#                         del st.session_state['uploaded_files'][index]
#                         st.experimental_rerun()
        
    
# Page2: 제품별 통계량
elif st.session_state.page == "Database_1":
    st.header("화학물질 제품별 통계량")
    
    df = pd.read_excel('A.xlsx')
    
    st.markdown("<div style='text-align: right'>[단위: kg/년]</div>", unsafe_allow_html=True)
    
    if df is not None:
        df = df.fillna(0)
        if '연도' in df.columns:
            df['연도'] = df['연도'].astype(str)
            
            # '연도' 칼럼에서 고유한 값을 가져와서 multiselect에 사용
            years = df['연도'].unique().tolist()
            selected_years = st.multiselect('연도 선택:', years, default=years)

            # 선택된 연도에 따라 DataFrame을 필터링
            df = df[df['연도'].isin(selected_years)]
            
            # '전년대비 증감율_입고량합계(%)' 컬럼을 위한 슬라이더 추가
            if '전년대비 증감율_입고량합계(%)' in df.columns:
                min_rate = df['전년대비 증감율_입고량합계(%)'].min()
                max_rate = df['전년대비 증감율_입고량합계(%)'].max()
                selected_rate_range = st.slider(
                    '전년 대비 증감율 범위 선택:',
                    min_value=float(min_rate),
                    max_value=float(max_rate),
                    value=(float(min_rate), float(max_rate))
                )
                df = df[df['전년대비 증감율_입고량합계(%)'].between(selected_rate_range[0], selected_rate_range[1])]
                
            # '입고량-합계' 컬럼을 위한 슬라이더 추가
            if '입고량-합계' in df.columns:
                min_rate = df['입고량-합계'].min()
                max_rate = df['입고량-합계'].max()
                selected_rate_range = st.slider(
                    '입고량-합계 범위 선택:',
                    min_value=float(min_rate),
                    max_value=float(max_rate),
                    value=(float(min_rate), float(max_rate))
                )
                df = df[df['입고량-합계'].between(selected_rate_range[0], selected_rate_range[1])]  
                
            # '출고량-합계' 컬럼을 위한 슬라이더 추가
            if '출고량-합계' in df.columns:
                min_rate = df['출고량-합계'].min()
                max_rate = df['출고량-합계'].max()
                selected_rate_range = st.slider(
                    '출고량-합계 범위 선택:',
                    min_value=float(min_rate),
                    max_value=float(max_rate),
                    value=(float(min_rate), float(max_rate))
                )
                df = df[df['출고량-합계'].between(selected_rate_range[0], selected_rate_range[1])]      
                
        # 데이터프레임 출력 (모든 숫자형 컬럼에 대해 포맷 지정)
        st.dataframe(df.style.format(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x))
        st.session_state.df = df  # Save the dataframe in session state
        
    elif st.session_state.df is not None:
        df = st.session_state.df
        if '연도' in df.columns:
            years = df['연도'].unique().tolist()
            selected_years = st.multiselect('연도 선택:', years, default=years)
            df = df[df['연도'].isin(selected_years)]

        # 데이터프레임 출력 (모든 숫자형 컬럼에 대해 포맷 지정)
        st.dataframe(df.style.format(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x))
        
# Page3: 피벗 테이블 생성
elif st.session_state.page == "Data_1 Analysis":
    st.header("화학물질 통계 DB 분석")
    st.markdown("<div style='text-align: right'>[단위: kg/년]</div>", unsafe_allow_html=True)
    # Display saved pivot table HTML if exists
    if st.session_state.pivot_html:
        st.markdown(st.session_state.pivot_html, unsafe_allow_html=True)   
        
    if st.session_state.df is not None:
        df = st.session_state.df
            
        values = st.multiselect("입고량 또는 출고량을 선택하세요.", df.columns, default=st.session_state.get('values', []))
        index = st.multiselect("제품명(상품명)을 선택하세요.", df.columns, default=st.session_state.get('index', []))
        columns = st.multiselect("연도를 선택하세요.", df.columns, default=st.session_state.get('columns', []))

        if '제품명(상품명)' in df.columns:
            selected_products = st.multiselect("제품명(상품명)을 선택하세요.", df['제품명(상품명)'].unique(), default=st.session_state.get('selected_products', []))
        
            
        if st.button("Pivot Table 생성"):
                        # Update the session state for multiselects
            st.session_state.values = values
            st.session_state.index = index
            st.session_state.columns = columns
            st.session_state.selected_products = selected_products
            
            
            try:
                if selected_products:
                    df = df[df['제품명(상품명)'].isin(selected_products)]

                if '연도' in df.columns:
                    df['연도'] = df['연도'].astype(int)
            

                pivot_df = pd.pivot_table(df, values=values, index=index, columns=columns, aggfunc=np.sum)
                pivot_df = pivot_df.fillna(0)
                # Flatten the MultiIndex for columns (if present)
                if isinstance(pivot_df.columns, pd.MultiIndex):
                    pivot_df.columns = [' '.join(map(str, col_tuple)) for col_tuple in pivot_df.columns.values]
                    
                st.session_state.pivot_df = pivot_df
                
                # Generate and store the HTML table in session state
                html_table = pivot_df.to_html(classes="table table-striped", float_format=lambda x: '{:,.0f}'.format(x), border=0)
                st.session_state.pivot_html = html_table
                st.markdown(html_table, unsafe_allow_html=True)   
                
                # Create the HTML table from the pivot_df
                html_table = '<div style="overflow-x: scroll; overflow-y: scroll; height: 400px;">'
                html_table += '<table class="table"><thead><tr><th></th>'
                for col in pivot_df.columns:
                    html_table += f'<th>{col}</th>'
                html_table += '</tr></thead><tbody>'

                for idx, row in pivot_df.iterrows():
                    html_table += '<tr><td>' + str(idx) + '</td>'
                    for col in pivot_df.columns:
                        val = row[col]
                        if isinstance(val, (int, float)):
                            html_table += f'<td>{val:,.0f}</td>'
                        else:
                            html_table += f'<td>{val}</td>'
                    html_table += '</tr>'
                html_table += '</tbody></table></div>'

                custom_css = """
                <style>
                    .table {
                        border-collapse: collapse;
                        width: 120%;
                        table-layout: auto;
                        font-size: 0.9em;
                    }
                    .table th, .table td {
                        border: 1px solid black;
                        padding: 12px;
                        text-align: center;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }
                    .table th {
                        background-color: #f2f2f2;
                        position: sticky;
                        top: 0;
                    }
                </style>
                """
                st.markdown(custom_css, unsafe_allow_html=True)
                st.markdown(html_table, unsafe_allow_html=True)

            except Exception as e:
                st.write("에러가 발생했습니다: ", e)
    else:
        st.warning("먼저 데이터를 업로드 해주세요.")
        
# Page4: 그래프 보기 

elif st.session_state.page == "Trend Graph_1":
    st.header("화학물질별 Trend Graph")
    st.markdown("<div style='text-align: right'>[단위: kg/년]</div>", unsafe_allow_html=True)    
    # If pivot_df exists in session, plot the graph
    if st.session_state.pivot_df is not None:
        df = st.session_state.pivot_df.copy()
        df.reset_index(inplace=True)
        
        # 데이터를 Plotly가 사용할 수 있는 형식으로 변환
        df_melted = df.melt(id_vars=df.columns[0], var_name='연도', value_name='값')

        # Plotly 그래프 생성
        fig = px.line(
            df_melted, 
            x='연도', 
            y='값', 
            color=df.columns[0],
            markers=True,  # 마커 추가
            labels={df.columns[0]: "제품명(상품명)"},
            title='연도별 제품 통계'
        )
       # 마커 크기와 색상 조정
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=10, color='white', line=dict(width=2))
        )
        
        # 그래프 레이아웃 설정
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            legend_title="제품명(상품명)",
            yaxis=dict(
                tickformat=',.0f',
                gridcolor='lightgrey',  # Y축 간격선 색상 설정
                gridwidth=0.5  # Y축 간격선 너비 설정
            ),
            plot_bgcolor='rgba(255,255,255,1)',
            height=700  # 그래프의 세로 크기 조정
        )

        # 그래프 출력
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("먼저 피벗 테이블을 생성해주세요.")
        
        
# Page5: 제품별 구성성분
elif st.session_state.page == "Product Components":
    st.header("제품별 구성성분")
#     uploaded_file2 = st.file_uploader("Product Components", type=["xlsx"])
    df2 = pd.read_excel('구성성분_2016~2022.xlsx')
    if df2 is not None:
#         df2 = pd.read_excel(df2)
        if '연도' in df2.columns:
            df2['연도'] = df2['연도'].astype(str)
            
            # '연도' 칼럼에서 고유한 값을 가져와서 multiselect에 사용
            years = df2['연도'].unique().tolist()
            selected_years = st.multiselect('연도 선택:', years, default=years)

            # 선택된 연도에 따라 DataFrame을 필터링
            df2 = df2[df2['연도'].isin(selected_years)]

        st.dataframe(df2.round(0),use_container_width=True)

        st.session_state.df2 = df2  # Save the dataframe in session state
        
    elif st.session_state.df2 is not None:
        # 세션 상태의 DataFrame을 가져옴
        df2 = st.session_state.df2
        if '연도' in df2.columns:
            years = df2['연도'].unique().tolist()
            selected_years = st.multiselect('연도 선택:', years, default=years)
            df2 = df2[df2['연도'].isin(selected_years)]
        
        st.dataframe(df2.round(0),use_container_width=True)
                 
    else:
        st.warning("먼저 데이터를 업로드 해주세요.")

# Page6: 유해화학물질 실적관리
elif st.session_state.page == "Database_2":
    st.header("유해화학물질 실적 DB")
#     uploaded_file3 = st.file_uploader("Database_2", type=["xlsx"])
    df3 = pd.read_excel('세부실적보고_2019~2022(3).xlsx')
    
    if df3 is not None:
#         df3 = pd.read_excel(uploaded_file3)
        if '조사연도' in df3.columns:
            df3['조사연도'] = df3['조사연도'].astype(str)
            
            # '연도' 칼럼에서 고유한 값을 가져와서 multiselect에 사용
            years = df3['조사연도'].unique().tolist()
            selected_years = st.multiselect('조사연도 선택:', years, default=years)

            # 선택된 연도에 따라 DataFrame을 필터링
            df3 = df3[df3['조사연도'].isin(selected_years)]
            
        if '세부실적보고명' in df3.columns:
            df3['세부실적보고명'] = df3['세부실적보고명'].astype(str)
            
            # '연도' 칼럼에서 고유한 값을 가져와서 multiselect에 사용
            years = df3['세부실적보고명'].unique().tolist()
            selected_years = st.multiselect('세부실적보고명 선택:', years, default=years)

            # 선택된 연도에 따라 DataFrame을 필터링
            df3 = df3[df3['세부실적보고명'].isin(selected_years)]
            
            # '전년대비 증감율_입고량합계(%)' 컬럼을 위한 슬라이더 추가
            if '전년대비 증감율(%)' in df3.columns:
                min_rate = df3['전년대비 증감율(%)'].min()
                max_rate = df3['전년대비 증감율(%)'].max()
                selected_rate_range = st.slider(
                    '전년 대비 증감율 범위 선택:',
                    min_value=float(min_rate),
                    max_value=float(max_rate),
                    value=(float(min_rate), float(max_rate))
                )
                df3 = df3[df3['전년대비 증감율(%)'].between(selected_rate_range[0], selected_rate_range[1])]
                
                
            # '취급량(년)' 컬럼을 위한 슬라이더 추가
            if '취급량(년)' in df3.columns:
                min_rate = df3['취급량(년)'].min()
                max_rate = df3['취급량(년)'].max()
                selected_rate_range = st.slider(
                    ' 취급량 범위 선택:',
                    min_value=float(min_rate),
                    max_value=float(max_rate),
                    value=(float(min_rate), float(max_rate))
                )
                df3 = df3[df3['취급량(년)'].between(selected_rate_range[0], selected_rate_range[1])]
                
        st.markdown("<div style='text-align: right'>[단위: ton/년]</div>", unsafe_allow_html=True)        
        st.dataframe(df3.round(0))

        st.session_state.df3 = df3  # Save the dataframe in session state
        
    elif st.session_state.df3 is not None:
        # 세션 상태의 DataFrame을 가져옴
        df3 = st.session_state.df3
        
        if '조사연도' in df3.columns:
            years = df3['조사연도'].unique().tolist()
            selected_years = st.multiselect('조사연도 선택:', years, default=years)
            df3 = df3[df3['조사연도'].isin(selected_years)]
            
        if '세부실적보고명' in df3.columns:
            years = df3['세부실적보고명'].unique().tolist()
            selected_years = st.multiselect('세부실적보고명 선택:', years, default=years)
            df3 = df3[df3['세부실적보고명'].isin(selected_years)]
        st.dataframe(df3.round(0),use_container_width=True)
                 
    else:
        st.warning("먼저 데이터를 업로드 해주세요.")
        

# Page7: 유해화학물질 데이터 분석

elif st.session_state.page == "Data_2 Analysis":
    st.header("유해화학물질 Data Analysis")
    st.markdown("<div style='text-align: right'>[단위: ton/년]</div>", unsafe_allow_html=True)
    
    # Display saved pivot table HTML if exists
    if st.session_state.pivot_html3:
        st.markdown(st.session_state.pivot_html3, unsafe_allow_html=True)   
        
    if st.session_state.df3 is not None:
        df3 = st.session_state.df3
            
        values = st.multiselect("취급량(년)을 선택하세요.", df3.columns, default=st.session_state.get('values3', []))
        index = st.multiselect("제품명을 선택하세요.", df3.columns, default=st.session_state.get('index3', []))
        columns = st.multiselect("조사연도를 선택하세요.", df3.columns, default=st.session_state.get('columns3', []))

        if '제품명' in df3.columns and '세부실적보고명' in df3.columns:
            selected_products = st.multiselect("보고 싶은 상세 제품명을 선택하세요.", df3['제품명'].unique(), default=st.session_state.get('selected_products3', []))
            selected_reports = st.multiselect("세부실적보고명을 선택하세요.", df3['세부실적보고명'].unique(), default=st.session_state.get('selected_reports', []))
        
        if st.button("Pivot Table 생성"):
            # Update the session state for multiselects
            st.session_state.values3 = values
            st.session_state.index3 = index
            st.session_state.columns3 = columns
            st.session_state.selected_products3= selected_products
            st.session_state.selected_reports = selected_reports
            
            try:
                if selected_products:
                    df3 = df3[df3['제품명'].isin(selected_products)]
                if selected_reports:
                    df3 = df3[df3['세부실적보고명'].isin(selected_reports)]

                if '조사연도' in df3.columns:
                    df3['조사연도'] = df3['조사연도'].astype(int)
                
                pivot_df3 = pd.pivot_table(df3, values=values, index=index, columns=columns, aggfunc=np.sum)
                pivot_df3 = pivot_df3.fillna(0)
                # Flatten the MultiIndex for columns (if present)
                if isinstance(pivot_df3.columns, pd.MultiIndex):
                    pivot_df3.columns = [' '.join(map(str, col_tuple)) for col_tuple in pivot_df3.columns.values]
                    
                st.session_state.pivot_df3 = pivot_df3
                
                # Generate and store the HTML table in session state
                html_table = pivot_df3.to_html(classes="table table-striped", float_format=lambda x: '{:,.0f}'.format(x), border=0)
                st.session_state.pivot_html3 = html_table
                st.markdown(html_table, unsafe_allow_html=True)    
                
                # Create the HTML table from the pivot_df
                html_table = '<div style="overflow-x: scroll; overflow-y: scroll; height: 400px;">'
                html_table += '<table class="table"><thead><tr><th></th>'
                for col in pivot_df3.columns:
                    html_table += f'<th>{col}</th>'
                html_table += '</tr></thead><tbody>'

                for idx, row in pivot_df3.iterrows():
                    html_table += '<tr><td>' + str(idx) + '</td>'
                    for col in pivot_df3.columns:
                        val = row[col]
                        if isinstance(val, (int, float)):
                            html_table += f'<td>{val:,.0f}</td>'
                        else:
                            html_table += f'<td>{val}</td>'
                    html_table += '</tr>'
                html_table += '</tbody></table></div>'

                custom_css = """
                <style>
                    .table {
                        border-collapse: collapse;
                        width: 120%;
                        table-layout: auto;
                        font-size: 0.9em;
                    }
                    .table th, .table td {
                        border: 1px solid black;
                        padding: 12px;
                        text-align: center;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }
                    .table th {
                        background-color: #f2f2f2;
                        position: sticky;
                        top: 0;
                    }
                </style>
                """
                st.markdown(custom_css, unsafe_allow_html=True)
                st.markdown(html_table, unsafe_allow_html=True)

            except Exception as e:
                st.write("에러가 발생했습니다: ", e)
    else:
        st.warning("먼저 데이터를 업로드 해주세요.")


        
# Page8: 유해화학물질 그래프 보기

elif st.session_state.page == "Trend Graph_2":
    st.header("유해화학물질 Trend Graph")
    st.markdown("<div style='text-align: right'>[단위: ton/년]</div>", unsafe_allow_html=True)
    
    # If pivot_df3 exists in session, plot the graph
    if st.session_state.pivot_df3 is not None:
        df3 = st.session_state.pivot_df3.copy()
        df3.reset_index(inplace=True)

        # 데이터를 Plotly가 사용할 수 있는 형식으로 변환
        df3_melted = df3.melt(id_vars=df3.columns[0], var_name='연도', value_name='값')

        # Plotly 그래프 생성
        fig = px.line(
            df3_melted, 
            x='연도', 
            y='값', 
            color=df3.columns[0],
            markers=True,  # 마커 추가
            labels={df3.columns[0]: "제품명(상품명)"},
            title='연도별 유해화학물질 통계'
        )

        # 마커 크기와 색상 조정
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=10, color='white', line=dict(width=2))
        )

        # 그래프 레이아웃 설정
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            legend_title="제품명(상품명)",
            yaxis=dict(
                tickformat=',.0f',
                gridcolor='lightgrey',  # Y축 간격선 색상 설정
                gridwidth=0.5  # Y축 간격선 너비 설정
            ),
            plot_bgcolor='rgba(255,255,255,1)',
            height=700  # 그래프의 세로 크기 조정
        )

        # 그래프 출력
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("먼저 피벗 테이블을 생성해주세요.")
        
             
        
        
# Page9: 화학물질 배출량 보고

elif st.session_state.page == "Database_3":
    st.header("배출량 Database")
    st.markdown("<div style='text-align: right'>[단위: kg/년]</div>", unsafe_allow_html=True)
    
#     uploaded_file4 = st.file_uploader("Database_3", type=["xlsx"])
    df4 = pd.read_excel('배출량_2017~2022(2).xlsx')
    
    if df4 is not None:
#         df4 = pd.read_excel(uploaded_file4)
        df4 = df4.fillna(0)
        st.session_state.df4 = df4
        
        if '연도' in df4.columns:
            df4['연도'] = df4['연도'].astype(str)
            years = df4['연도'].unique().tolist()
            selected_years = st.multiselect('연도 선택:', years, default=years)
            df4 = df4[df4['연도'].isin(selected_years)]
            
        if '대분류' in df4.columns:
            df4['대분류'] = df4['대분류'].astype(str)
            years = df4['대분류'].unique().tolist()
            selected_years = st.multiselect('대분류 선택:', years, default=years)
            df4 = df4[df4['대분류'].isin(selected_years)]
            
        if '중분류' in df4.columns:
            df4['대분류'] = df4['대분류'].astype(str)
            years = df4['중분류'].unique().tolist()
            selected_years = st.multiselect('중분류 선택:', years, default=years)
            df4 = df4[df4['중분류'].isin(selected_years)]
            
        if '소분류' in df4.columns:
            df4['소분류'] = df4['소분류'].astype(str)
            years = df4['소분류'].unique().tolist()
            selected_years = st.multiselect('소분류 선택:', years, default=years)
            df4 = df4[df4['소분류'].isin(selected_years)]
            
            
        #st.dataframe(df.style.format({'전년대비 증감율_입고량합계(%)': '{:.2f}%'})) 
        st.dataframe(df4.round(0))
        st.session_state.df4 = df4  # Save the dataframe in session state
        
    elif st.session_state.df4 is not None:
        df4 = st.session_state.df4
        if '연도' in df4.columns:
            df4['연도'] = df4['연도'].astype(str)
            df4 = df4.fillna(0)

            years = df4['연도'].unique().tolist()
            selected_years = st.multiselect('연도 선택:', years, default=years)
            df4 = df4[df4['연도'].isin(selected_years)]
            
        if '대분류' in df4.columns:
            df4['대분류'] = df4['대분류'].astype(str)
            years = df4['대분류'].unique().tolist()
            selected_years = st.multiselect('대분류 선택:', years, default=years)
            df4 = df4[df4['대분류'].isin(selected_years)]
            
        if '중분류' in df4.columns:
            df4['대분류'] = df4['대분류'].astype(str)
            years = df4['중분류'].unique().tolist()
            selected_years = st.multiselect('중분류 선택:', years, default=years)
            df4 = df4[df4['중분류'].isin(selected_years)]
            
        if '소분류' in df4.columns:
            df4['소분류'] = df4['소분류'].astype(str)
            years = df4['소분류'].unique().tolist()
            selected_years = st.multiselect('소분류 선택:', years, default=years)
            df4 = df4[df4['소분류'].isin(selected_years)]
        
        st.dataframe(df4.round(0))
        st.session_state.df4 = df4  # Save the dataframe in session state


        

# Page10: 배출량 데이터 분석

elif st.session_state.page == "Data_3 Analysis":
    st.header("화학물질 배출량 분석")
    
#     uploaded_file4 = st.file_uploader("화학물질 배출량 분석.", type=["xlsx"])

#     if uploaded_file5 is not None:
#         df4 = pd.read_excel(uploaded_file4)
#         df4 = df5.fillna(0)
    df4 = st.session_state.df4
    st.session_state.df4 = df4.round(0)
    
    if '연도' in df4.columns:
                df4['연도'] = df4['연도'].astype(str)
                years = df4['연도'].unique().tolist()
                selected_years = st.multiselect('해당 연도 선택:', years, default=years)
                df4 = df4[df4['연도'].isin(selected_years)]

    if '대분류' in df4.columns:
        df4['대분류'] = df4['대분류'].astype(str)
        years = df4['대분류'].unique().tolist()
        selected_years = st.multiselect('대분류 선택:', years, default=years)
        df4 = df4[df4['대분류'].isin(selected_years)]

    if '중분류' in df4.columns:
        df4['대분류'] = df4['대분류'].astype(str)
        years = df4['중분류'].unique().tolist()
        selected_years = st.multiselect('중분류 선택:', years, default=years)
        df4 = df4[df4['중분류'].isin(selected_years)]

    if '소분류' in df4.columns:
        df4['소분류'] = df4['소분류'].astype(str)
        years = df4['소분류'].unique().tolist()
        selected_years = st.multiselect('소분류 선택:', years, default=years)
        df4 = df4[df4['소분류'].isin(selected_years)]

    

            #st.dataframe(df.style.format({'전년대비 증감율_입고량합계(%)': '{:.2f}%'})) 
#         st.dataframe(df4.round(0))
#         st.session_state.df4 = df4  # Save the dataframe in session state
        
    elif st.session_state.df4 is not None:
        df4 = st.session_state.df4
        if '연도' in df4.columns:
            df4['연도'] = df4['연도'].astype(str)
            df4 = df4.fillna(0)

            years = df4['연도'].unique().tolist()
            selected_years = st.multiselect('해당 연도 선택:', years, default=years)
            df4 = df4[df4['연도'].isin(selected_years)]
            
        if '대분류' in df4.columns:
            df4['대분류'] = df4['대분류'].astype(str)
            years = df4['대분류'].unique().tolist()
            selected_years = st.multiselect('대분류 선택:', years, default=years)
            df4 = df4[df4['대분류'].isin(selected_years)]
            
        if '중분류' in df4.columns:
            df4['대분류'] = df4['대분류'].astype(str)
            years = df4['중분류'].unique().tolist()
            selected_years = st.multiselect('중분류 선택:', years, default=years)
            df4 = df4[df4['중분류'].isin(selected_years)]
            
        if '소분류' in df4.columns:
            df4['소분류'] = df4['소분류'].astype(str)
            years = df4['소분류'].unique().tolist()
            selected_years = st.multiselect('소분류 선택:', years, default=years)
            df4 = df4[df4['소분류'].isin(selected_years)]
        
        st.dataframe(df4.round(0))
        st.session_state.df4 = df4  # Save the dataframe in session state
        
        # 추가: Column 선택 옵션
    values = st.multiselect("제품을 선택하세요.", df4.columns, default=st.session_state.get('values4', []))
#     index = st.multiselect("Row 인덱스로 사용할 열을 선택하세요.", df4.columns, default=st.session_state.get('index4', []))
    columns = st.multiselect("연도를 선택하세요.", df4.columns, default=st.session_state.get('columns4', []))
    
    st.markdown("<div style='text-align: right'>[단위: kg/년]</div>", unsafe_allow_html=True)
    
    if st.button("Pivot Table 생성"):
        st.session_state.values4 = values
#         st.session_state.index4 = index
        st.session_state.columns4 = columns

        try:
            pivot_df4 = pd.pivot_table(df4, values=values, columns=columns, aggfunc=np.sum)
            pivot_df4 = pivot_df4.fillna(0)
            st.session_state.pivot_df4 = pivot_df4
#             st.write(pivot_df4.round(0),use_container_width=True)
            st.dataframe(st.session_state.pivot_df4.round(0),use_container_width=True)

        except Exception as e:
            st.write("에러가 발생했습니다: ", e)

    elif 'pivot_df4' in st.session_state:
#         st.write(st.session_state.pivot_df4.round(0),use_container_width=True)
        st.dataframe(st.session_state.pivot_df4,use_container_width=True)
        
# Page11: 유해화학물질 그래프 보기

elif st.session_state.page == "Trend Graph_3":
    st.header("화학물질 배출량 Trend Graph")
    st.markdown("<div style='text-align: right'>[단위: kg/년]</div>", unsafe_allow_html=True)

    if st.session_state.pivot_df4 is not None:
        df4 = st.session_state.pivot_df4.copy()
        df4.reset_index(inplace=True)

        # 데이터를 Plotly가 사용할 수 있는 형식으로 변환
        df4_melted = df4.melt(id_vars=df4.columns[0], var_name='연도', value_name='값')

        # Plotly 그래프 생성
        fig = px.line(
            df4_melted, 
            x='연도', 
            y='값', 
            color=df4.columns[0],
            markers=True,  # 마커 추가
            labels={df4.columns[0]: "제품명(상품명)"},
            title='연도별 화학물질 배출량 통계'
        )

        # 마커 크기와 색상 조정
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=10, color='white', line=dict(width=2))
        )

        # 그래프 레이아웃 설정
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            legend_title="제품명(상품명)",
            yaxis=dict(
                tickformat=',.0f',
                gridcolor='lightgrey',  # Y축 간격선 색상 설정
                gridwidth=0.5  # Y축 간격선 너비 설정
            ),
            plot_bgcolor='rgba(255,255,255,1)',
            height=700  # 그래프의 세로 크기 조정
        )

        # 그래프 출력
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("먼저 피벗 테이블을 생성해주세요.")
        
             
