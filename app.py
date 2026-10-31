import streamlit as st
import extra_streamlit_components as stx
from supabase import create_client
from datetime import date
import uuid

st.set_page_config(page_title="천원의 아침밥 수량 확인", page_icon="🍎", layout="centered")
st.title("🍎 천원의 아침밥 수량 확인")
st.caption("가상 구매 시연용입니다. 실제 학교 판매 시스템과 연결되어 있지 않습니다.")


@st.cache_resource
def get_db():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["anon_key"]
    )


try:
    db = get_db()
except Exception as e:
    st.error("Supabase 연결 정보가 필요합니다. 앱 설정의 Secrets에 URL과 anon key를 입력해 주세요.")
    st.caption(f"오류 내용: {e}")
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
    result = db.rpc(
        "has_demo_purchased",
        {"p_demo_user_id": user_id, "p_service_date": today}
    ).execute().data
    return bool(result)


try:
    total, sold = counts()
    purchased = has_purchased()
except Exception as e:
    st.error("데이터베이스 설정을 확인해 주세요. Supabase에서 supabase_setup.sql을 실행했는지 확인하세요.")
    st.caption(f"오류 내용: {e}")
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
            result = db.rpc(
                "make_demo_purchase",
                {"p_demo_user_id": user_id, "p_service_date": today}
            ).execute().data

            if result == "purchased":
                st.success("가상 구매가 완료되었습니다!")
            elif result == "already_purchased":
                st.warning("이 브라우저에서는 오늘 이미 구매했습니다.")
            elif result == "sold_out":
                st.error("잔여 수량이 없어 구매할 수 없습니다.")
            else:
                st.warning(f"구매 처리 결과를 확인해 주세요: {result}")

            st.rerun()
        except Exception as e:
            st.error("구매 처리에 실패했습니다. Supabase 설정을 확인해 주세요.")
            st.caption(f"오류 내용: {e}")


st.divider()
st.subheader("관리자 메뉴")
st.caption("관리자 비밀번호를 입력하고 확인 절차를 완료하면 오늘의 가상 구매 기록을 초기화합니다.")

try:
    admin_password = st.secrets["admin"]["password"]
except Exception:
    admin_password = None

if not admin_password:
    st.error("관리자 비밀번호가 설정되지 않았습니다. Streamlit 앱의 Settings → Secrets에 [admin] password를 추가해 주세요.")
else:
    entered_password = st.text_input(
        "관리자 비밀번호",
        type="password",
        key="admin_password_input"
    )

    if entered_password == admin_password:
        st.success("관리자 비밀번호가 확인되었습니다.")
        confirm_reset = st.checkbox(
            "오늘 날짜의 모든 가상 구매 기록을 삭제하는 것에 동의합니다.",
            key="confirm_reset"
        )

        clicked_reset = st.button(
            "오늘 수량 초기화",
            type="secondary",
            disabled=not confirm_reset,
            use_container_width=True,
            key="reset_today_button"
        )

        if not confirm_reset:
            st.caption("위 확인란을 체크해야 초기화 버튼을 누를 수 있습니다.")

        if clicked_reset:
            try:
                with st.spinner("오늘의 가상 구매 기록을 초기화하고 있습니다..."):
                    result = db.rpc(
                        "reset_demo_purchases",
                        {
                            "p_service_date": today,
                            "p_admin_password": entered_password
                        }
                    ).execute()

                st.success(f"초기화 요청이 처리되었습니다. 서버 응답: {result.data}")
                st.rerun()

            except Exception as e:
                st.error("초기화 요청이 Supabase에서 거부되었습니다.")
                st.code(str(e))
                st.info(
                    "Supabase SQL Editor에서 reset_demo_purchases(date, text) 함수가 생성되었는지, "
                    "SQL 안의 비밀번호와 Streamlit Secrets의 [admin] password가 같은지 확인해 주세요."
                )

    elif entered_password:
        st.error("관리자 비밀번호가 Secrets에 저장된 값과 일치하지 않습니다.")


st.divider()
if st.button("수량 새로고침", use_container_width=True):
    st.rerun()

st.caption("다른 사용자의 구매는 수량 새로고침 버튼을 눌러 반영할 수 있습니다.")
st.caption("주의: 로그인 없는 시연용 제한입니다. 쿠키 삭제 또는 다른 브라우저 사용으로 우회할 수 있으며 실제 구매 제한 용도로 사용할 수 없습니다.")


