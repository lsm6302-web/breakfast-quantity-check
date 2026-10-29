import streamlit as st

# 천원의 아침밥 잔여 수량 확인 웹페이지
# 가상 구매 버튼으로 작동을 시연하는 프로그램입니다.
# 실제 판매 시스템과 연결되어 있지 않습니다.

st.set_page_config(
    page_title="천원의 아침밥 수량 확인",
    page_icon="🍚",
    layout="centered"
)

total_quantity = 100

# 처음 실행할 때 가상 판매 수량을 0으로 설정합니다.
if "sold_quantity" not in st.session_state:
    st.session_state.sold_quantity = 0

st.title("🍚 천원의 아침밥 잔여 수량 확인")
st.write("상명대학교 서울캠퍼스 천원의 아침밥 수량 확인 시제품입니다.")
st.info(
    "시연용 가상 데이터입니다. 아래 구매 버튼은 실제 결제나 식권 발급을 하지 않습니다."
)

# 현재 수량 계산
sold_quantity = st.session_state.sold_quantity
remaining_quantity = total_quantity - sold_quantity

st.subheader("현재 수량")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("총 제공 수량", f"{total_quantity}식")

with col2:
    st.metric("가상 판매 수량", f"{sold_quantity}식")

with col3:
    st.metric("잔여 수량", f"{remaining_quantity}식")

if remaining_quantity == 0:
    st.error("판매 완료: 잔여 수량이 없습니다.")
else:
    st.success("현재 구매 가능")

st.divider()
st.subheader("가상 구매 시뮬레이션")
st.write("구매 버튼을 누르면 시연용 판매 수량이 1식 증가합니다.")

# 잔여 수량이 있을 때만 구매 버튼을 활성화합니다.
if remaining_quantity > 0:
    if st.button("가상으로 1식 구매하기"):
        st.session_state.sold_quantity += 1
        st.rerun()
else:
    st.button("가상으로 1식 구매하기", disabled=True)

# 시연을 다시 시작할 수 있도록 초기화 버튼을 둡니다.
if st.button("시연 수량 초기화"):
    st.session_state.sold_quantity = 0
    st.rerun()

st.caption(
    "※ 가상 구매 시뮬레이션입니다. 실제 결제·판매 내역과 연결되어 있지 않습니다. "
    "수량은 현재 브라우저 세션에서만 유지되며 다른 사용자와 공유되지 않습니다."
)
