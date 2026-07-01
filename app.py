import streamlit as st
import requests
import datetime

# ----------------------------------------------------
# 1. API 호출 함수 정의
# ----------------------------------------------------

@st.cache_data(ttl=3600) # 1시간 동안 기상 데이터 캐싱 (속도 향상)
def get_current_weather():
    try:
        api_key = st.secrets["KMA_API_KEY"]
        url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
        
        now = datetime.datetime.now()
        if now.minute < 40:
            now = now - datetime.timedelta(hours=1)
            
        base_date = now.strftime('%Y%m%d')
        base_time = now.strftime('%H00')
        
        params = {
            'serviceKey': api_key, 'pageNo': '1', 'numOfRows': '10',
            'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time,
            'nx': '60', 'ny': '121' # 수원 기준
        }
        
        response = requests.get(url, params=params)
        items = response.json()['response']['body']['items']['item']
        
        weather_data = {}
        for item in items:
            if item['category'] == 'T1H': weather_data['temp'] = float(item['obsrValue'])
            elif item['category'] == 'RN1': weather_data['rain'] = float(item['obsrValue'])
            elif item['category'] == 'REH': weather_data['humid'] = float(item['obsrValue'])
        return weather_data
    except Exception as e:
        return None

@st.cache_data(ttl=86400) # 공단 데이터는 하루 1번만 호출하여 캐싱 (서버 부하 방지)
def get_kosha_safety_info(industry_keyword):
    """
    한국산업안전보건공단 API 연동 함수 (공공데이터포털 연동 예시)
    실제 사용 시 공공데이터포털에서 발급받은 KOSHA_API_KEY를 secrets에 추가해야 합니다.
    """
    try:
        # api_key = st.secrets["KOSHA_API_KEY"]
        # url = 'http://openapi.kosha.or.kr/openapi/service/rest/SafeHealthInfoService/getIndustrySafeGuide'
        # params = {'serviceKey': api_key, 'searchKeyword': industry_keyword, 'type': 'json'}
        # response = requests.get(url, params=params)
        # return response.json()['response']['body']['items']
        
        # [테스트용 임시 반환 데이터] - 실제 API 연동 전까지 UI를 구성하기 위한 목업 데이터
        return [
            f"[{industry_keyword} 주요 위험] 공단 API 연동 기반 맞춤형 위험 요인 안내",
            "법정 필수 안전보호구 착용 기준 (안전보건규칙 제 32조)",
            "최근 동종 업계 중대재해 발생 사례 및 예방 대책"
        ]
    except Exception as e:
        return ["데이터를 불러오는 중 오류가 발생했습니다. 관리자에게 문의하세요."]

# ----------------------------------------------------
# 2. 메인 화면 UI 및 EHS 콘텐츠
# ----------------------------------------------------
st.set_page_config(page_title="협력사 일일 안전 포털", page_icon="🛡️", layout="wide")
st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🛡️ 협력사 일일 안전보건 정보 포털</h2>", unsafe_allow_html=True)
st.caption(f"📅 **오늘의 날짜:** {datetime.date.today().strftime('%Y년 %m월 %d일')}")

# --- [기상청 실시간 연동 특보 및 날씨 맞춤형 안전 가이드] ---
st.subheader("📡 현장 실시간 기상 및 맞춤형 안전 지침 (수원 기준)")
weather = get_current_weather()

if weather:
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ 현재 기온", f"{weather['temp']} ℃")
    col2.metric("💧 현재 습도", f"{weather['humid']} %")
    col3.metric("☔ 1시간 강수량", f"{weather['rain']} mm")
    
    # 기온/강수량에 따른 심층 안전 가이드 제공
    if weather['temp'] >= 33.0:
        st.error("🚨 **[폭염 경보]** 온열질환 발생 위험이 매우 높습니다. 옥외작업 제한 권고.")
        with st.expander("👉 온열질환 예방 3대 수칙 (물, 그늘, 휴식) 상세 보기"):
            st.markdown("- **물:** 시원하고 깨끗한 물을 규칙적으로 제공 (보냉통 비치)\n- **그늘:** 작업장과 가까운 곳에 햇빛을 완전히 차단하는 휴식 공간 마련\n- **휴식:** 1시간 주기 15분 이상 휴식, 가장 더운 시간대(14~17시) 옥외작업 중지")
            
    elif weather['temp'] <= -5.0:
        st.info("🚨 **[한파 주의]** 동상, 저체온증 및 빙판길 전도 재해 주의.")
        with st.expander("👉 동절기 한랭질환 예방 가이드 상세 보기"):
            st.markdown("- **복장:** 방한복, 방한모, 방한화, 방한장갑 등 보온장구 지급 및 착용\n- **시설:** 작업장 인근에 따뜻한 장소(난로 등) 마련 및 따뜻한 음료 제공\n- **작업:** 결빙 구간 모래/염화칼슘 살포, 옥외작업 시 수시 교대")
            
    elif weather['rain'] > 0:
        st.warning("☔ **[강우 주의]** 감전 및 미끄러짐 재해 위험 발생.")
        with st.expander("👉 우천 시 작업 안전수칙 상세 보기"):
            st.markdown("- **전기:** 옥외 전기 기계·기구 사용 및 용접 작업 원칙적 금지\n- **추락/전도:** 비계, 지붕 위 작업 중지. 통로 및 가설계단 미끄럼 방지 조치\n- **토사:** 굴착면 붕괴 위험 점검 및 빗물 유입 방지 조치")
            
    else:
        st.success("✅ 현재 기상에 따른 특별 재해 위험은 낮습니다. 아래 업종별 기본 안전수칙을 준수 바랍니다.")
else:
    st.warning("현재 기상청 통신 지연으로 날씨를 불러올 수 없습니다. 기본 안전에 유의하세요.")

st.divider()

# --- [업종별 안전수칙 (KOSHA API 연동 기반)] ---
st.subheader("🏭 업종별 핵심 안전수칙 (한국산업안전보건공단 제공)")
industries = ["시설관리", "청소", "물류", "식당", "서비스", "폐기물처리", "제조"]
tabs = st.tabs(industries)

for index, industry in enumerate(industries):
    with tabs[index]:
        # KOSHA API를 통해 해당 업종의 동적 데이터를 불러옴
        kosha_data = get_kosha_safety_info(industry)
        
        st.markdown(f"#### 💡 {industry} 업종 안전보건 가이드")
        # API에서 받아온 리스트 데이터를 출력
        for item in kosha_data:
            st.info(f"✔️ {item}")
            
        # 기존의 고정 데이터(Fallback)도 함께 제공할 수 있습니다.
        if industry == "시설관리":
            st.write("**[필수 점검]** 2m 이상 고소작업 시 안전대/안전모 착용, 정비 전 전원차단(LOTO)")
        elif industry == "청소":
            st.write("**[필수 점검]** 작업 구간 '미끄럼 주의' 표지판 설치, 화학물질(세제) MSDS 확인")

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
■ 주요전달: 기상청 및 안전보건공단 기반 맞춤형 가이드라인 전파
-----------------------------------------
