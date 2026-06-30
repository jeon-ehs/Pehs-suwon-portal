
import streamlit as st
import requests
import datetime

# ----------------------------------------------------
# 1. 기상청 실시간 API 호출 함수 (수원 기준)
# ----------------------------------------------------
def get_current_weather():
    try:
        # 스트림릿 Secrets에서 보호된 API 키 불러오기
        api_key = st.secrets["KMA_API_KEY"]
        url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
        
        now = datetime.datetime.now()
        # 기상청 초단기실황은 매시간 40분에 최신화됨
        if now.minute < 40:
            now = now - datetime.timedelta(hours=1)
            
        base_date = now.strftime('%Y%m%d')
        base_time = now.strftime('%H00')
        
        # 📍 수원시 좌표 기준 (NX: 60, NY: 121)
        params = {
            'serviceKey': api_key, 'pageNo': '1', 'numOfRows': '10',
            'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time,
            'nx': '60', 'ny': '121'
        }
        
        response = requests.get(url, params=params)
        items = response.json()['response']['body']['items']['item']
        
        weather_data = {}
        for item in items:
            if item['category'] == 'T1H': weather_data['temp'] = float(item['obsrValue']) # 기온
            elif item['category'] == 'RN1': weather_data['rain'] = float(item['obsrValue']) # 강수량
            elif item['category'] == 'REH': weather_data['humid'] = float(item['obsrValue']) # 습도
        return weather_data
    except Exception as e:
        return None

# ----------------------------------------------------
# 2. 메인 화면 UI 및 EHS 콘텐츠
# ----------------------------------------------------
st.set_page_config(page_title="협력사 일일 안전 포털", page_icon="🛡️", layout="wide")

st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🛡️ 협력사 일일 안전보건 정보 포털</h2>", unsafe_allow_html=True)
st.caption(f"📅 **오늘의 날짜:** {datetime.date.today().strftime('%Y년 %m월 %d일')}")

# --- [기상청 실시간 연동 특보] ---
st.subheader("📡 현장 실시간 기상 현황 (수원 기준)")
weather = get_current_weather()

if weather:
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ 현재 기온", f"{weather['temp']} ℃")
    col2.metric("💧 현재 습도", f"{weather['humid']} %")
    col3.metric("☔ 1시간 강수량", f"{weather['rain']} mm")
    
    # 기온에 따른 안전 경보 자동화
    if weather['temp'] >= 33.0:
        st.error("🚨 **[폭염 주의]** 기온이 33도 이상입니다. 매 15분 휴식 및 수분 섭취를 의무화하세요.")
    elif weather['temp'] <= -5.0:
        st.info("🚨 **[한파 주의]** 기온이 급강하했습니다. 방한구 착용 및 빙판길 미끄럼에 주의하세요.")
    elif weather['rain'] > 0:
        st.warning("☔ **[강우 주의]** 우천 중입니다. 옥외 전기 작업 통제 및 전도(넘어짐) 재해에 유의하세요.")
    else:
        st.success("✅ 현재 기상에 따른 특별 재해 위험은 낮습니다. 기본 안전수칙을 준수 바랍니다.")
else:
    st.warning("현재 기상청 통신 지연으로 날씨를 불러올 수 없습니다. 안전 작업에 유의하세요.")

st.divider()

# --- [업종별 안전수칙] ---
st.subheader("🏭 업종별 핵심 안전수칙 가이드")
tabs = st.tabs(["시설관리", "청소", "물류", "식당", "서비스", "폐기물처리", "제조"])

with tabs[0]:
    st.markdown("#### 🛠️ 시설관리\n- **추락 방지:** 2m 이상 고소작업 시 안전대/안전모 착용 필수\n- **감전 예방:** 정비 전 전원차단 및 LOTO 조치 확행")
with tabs[1]:
    st.markdown("#### 🧹 청소\n- **전도 방지:** 작업 구간 '미끄럼 주의' 표지판 설치 및 미끄럼방지화 착용\n- **화학물질:** 세제 혼합 금지 및 MSDS 경고표지 준수")
with tabs[2]:
    st.markdown("#### 📦 물류 (하역)\n- **충돌 예방:** 지게차 작업 반경 내 보행자 절대 출입 금지\n- **낙하 방지:** 고단 랙 적재 시 랩핑 고정 철저")
with tabs[3]:
    st.markdown("#### 🍳 식당\n- **화상 예방:** 방열장갑 착용 및 튀김기름 온도 관리 철저\n- **전도 방지:** 바닥 물기/기름기 즉시 제거 및 미끄럼 방지 장화 착용")
with tabs[4]:
    st.markdown("#### 🧑‍💼 서비스\n- **감정노동:** 문제상황 발생 시 관리자 지원 및 휴식 보장\n- **VDT 증후군:** 50분 컴퓨터 작업 후 10분 휴식 및 스트레칭")
with tabs[5]:
    st.markdown("#### ♻️ 폐기물처리\n- **협착 예방:** 파쇄기 정비 시 반드시 전원 차단(LOTO)\n- **자상 예방:** 날카로운 물질 수거 시 절단 방지 특수 장갑 착용")
with tabs[6]:
    st.markdown("#### ⚙️ 제조업\n- **끼임 방지:** 구동 회전체 방호덮개 임의 해제 절대 금지\n- **직업병 예방:** 고소음/분진 발생 공정 시 귀마개 및 마스크 착용")

st.divider()

# --- [TBM 서명 카드] ---
st.subheader("📋 일일 TBM(Tool Box Meeting) 모바일 확인서")
c1, c2 = st.columns(2)
with c1:
    contractor_name = st.text_input("협력사명을 입력하세요 (예: 삼성안전)")
with c2:
    worker_cnt = st.number_input("금일 작업 투입 인원 (명)", min_value=1, value=3)

if st.button("🖨️ TBM 확인서 텍스트 생성"):
    if contractor_name:
        tbm_result = f"""=========================================
[ 일일 TBM 무재해 이행 확인서 ]
■ 협력사명: {contractor_name} (투입인원: {worker_cnt}명)
-----------------------------------------
1. 작업 전 위험성평가 내용을 전원 숙지하였는가? ( O )
2. 안전모, 안전화 등 개인보호구를 완벽히 착용하였는가? ( O )
3. 음주자, 질병자 등 건강이상자가 없는가? ( O )
========================================="""
        st.text_area("현장 소장님께 아래 내용을 복사하여 공유하세요:", value=tbm_result, height=200)
    else:
        st.error("협력사명을 먼저 입력해 주세요.")
