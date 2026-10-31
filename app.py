import streamlit as st
import extra_streamlit_components as stx
from supabase import create_client
from datetime import date
import uuid

st.set_page_config(page_title="천원의 아침밥 수량 확인", page_icon="🍎", layout="centered")
st.title("🍎 천원의 아침밥 수량 확인")
st.caption("가상 구매 시연용입니다. 실제 학교 판매 시스템과 연결되어 있지 않습니다.")

@st.cache_resource
def get_db():streamlit\nsupabase\nextra-streamlit-components\n
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["anon_key"])

try:
    db = get_db()
except Exception:
    st.error("Supabase 연결 정보가 필요합니다. 앱 설정의 Secrets에 URL과 anon key를 입력해 주세요.")
    st.stop()

cookies = stx.CookieManager(key="demo_cookie")
user_id = cookies.get("breakfast_demo_user_id")
if not user_id:
    user_id = str(uuid.uuid4())
    cookies.set("breakfast_demo_user_id", user_id)
    st.info("시연용 사용자 ID를 만들었습니다. 페이지를 새로고침한 뒤 이용해 주세요.")
    st.stop()

today = date.today().isoformat()

def counts():
    result = db.rpc("get_breakfast_counts", {"p_service_date": today}).execute().data
    return int(result["total_quantity"]), int(result["sold_quantity"])

def has_purchased():
    result = db.rpc("has_demo_purchased", {
        "p_demo_user_id": user_id, "p_service_date": today
    }).execute().data
    return bool(result)

try:
    total, sold = counts()
    purchased = has_purchased()
except Exception as e:
    st.error("데이터베이스 설정을 확인해 주세요. Supabase에서 supabase_setup.sql을 실행했는지 확인하세요.")
    st.caption(str(e))
    st.stop()

remaining = max(total - sold, 0)
a, b, c = st.columns(3)
a.metric("총수량", f"{total}개")
b.metric("가상 판매 수량", f"{sold}개")
c.metric("잔여 수량", f"{remaining}개")

if remaining == 0:
    st.error("품절되었습니다.")
elif remaining <= 10:
    st.warning("잔여 수량이 얼마 남지 않았습니다.")
else:
    st.success("현재 가상 구매가 가능합니다.")

st.divider()
st.subheader("가상 구매")
if purchased:
    st.info("이 브라우저에서는 오늘 이미 가상 구매를 완료했습니다.")
    st.button("가상으로 1식 구매하기", disabled=True, use_container_width=True)
elif remaining <= 0:
    st.button("가상으로 1식 구매하기", disabled=True, use_container_width=True)
else:
    if st.button("가상으로 1식 구매하기", type="primary", use_container_width=True):
        try:
            result = db.rpc("make_demo_purchase", {
                "p_demo_user_id": user_id, "p_service_date": today
            }).execute().data
            if result == "purchased":
                st.success("가상 구매가 완료되었습니다!")
            elif result == "already_purchased":
                st.warning("이 브라우저에서는 오늘 이미 구매했습니다.")
            elif result == "sold_out":
                st.error("잔여 수량이 없어 구매할 수 없습니다.")
            else:
                st.error(f"구매 처리 결과: {result}")
            st.rerun()
        except Exception as e:
            st.error("구매 처리에 실패했습니다. Supabase 설정을 확인해 주세요.")
            st.caption(str(e))

if st.button("수량 새로고침", use_container_width=True):
    st.rerun()

st.caption("다른 사용자의 구매는 수량 새로고침 버튼을 눌러 반영할 수 있습니다.")
st.caption("주의: 로그인 없는 시연용 제한입니다. 쿠키 삭제 또는 다른 브라우저 사용으로 우회할 수 있으며 실제 구매 제한 용도로 사용할 수 없습니다.")

천원의 아침밥 공유 수량 시연 앱

포함 파일:
- app.py: Streamlit 웹 앱
- requirements.txt: 필요한 라이브러리
- supabase_setup.sql: 데이터베이스 설정 SQL

설정 순서
1. https://supabase.com 에서 새 프로젝트를 만듭니다.
2. Supabase의 SQL Editor에서 supabase_setup.sql 전체를 실행합니다.
3. Project URL과 anon/public key를 복사합니다. service_role 키는 사용하거나 공개하지 마세요.
4. Streamlit Community Cloud 앱의 Settings > Secrets에 다음 형식으로 입력합니다.

[supabase]
url = "https://YOUR_PROJECT.supabase.co"
anon_key = "YOUR_SUPABASE_ANON_KEY"

5. app.py와 requirements.txt를 GitHub 저장소 최상위 폴더에 올리고 Streamlit Community Cloud에서 app.py를 배포합니다.

주의
- 실제 판매 시스템과 연결되지 않은 가상 구매 시연용입니다.
- 로그인 없는 1회 제한은 브라우저 쿠키 ID를 사용합니다. 쿠키 삭제, 다른 브라우저/기기 사용으로 우회할 수 있어 실제 구매 제한 용도로는 부적합합니다.
- 수량 새로고침은 현재 수동입니다. 자동 주기 갱신은 추가 개발할 수 있습니다.
- 관리자용 수량 수정 기능은 포함되어 있지 않습니다.
