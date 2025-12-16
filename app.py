import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="매수매도 계산기",
    page_icon="📊",
    layout="wide"
)

# 세션 상태 초기화
if 'sell_orders' not in st.session_state:
    st.session_state.sell_orders = []

st.title("📊 매수매도 계산기")

# 매수 주문 섹션
st.header("매수 주문")
col1, col2, col3 = st.columns(3)
with col1:
    buy_type = st.text_input("종류", value="LOC", key="buy_type")
with col2:
    buy_price = st.number_input("가격", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="buy_price")
with col3:
    buy_quantity = st.number_input("수량", min_value=0, value=0, step=1, key="buy_quantity")

st.divider()

# 매도 주문 섹션
st.header("매도 주문")

# 매도 주문 추가 버튼
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("➕ 매도 주문 추가"):
        st.session_state.sell_orders.append({
            'type': 'LOC',
            'price': 0.0,
            'quantity': 0
        })
        st.rerun()

# 매도 주문 리스트 표시
if len(st.session_state.sell_orders) > 0:
    for idx, order in enumerate(st.session_state.sell_orders):
        col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
        with col1:
            sell_type = st.text_input(
                "종류", 
                value=order['type'], 
                key=f"sell_type_{idx}"
            )
            st.session_state.sell_orders[idx]['type'] = sell_type
        with col2:
            sell_price = st.number_input(
                "가격", 
                min_value=0.0, 
                value=order['price'], 
                step=0.01, 
                format="%.2f", 
                key=f"sell_price_{idx}"
            )
            st.session_state.sell_orders[idx]['price'] = sell_price
        with col3:
            sell_quantity = st.number_input(
                "수량", 
                min_value=0, 
                value=order['quantity'], 
                step=1, 
                key=f"sell_quantity_{idx}"
            )
            st.session_state.sell_orders[idx]['quantity'] = sell_quantity
        with col4:
            if st.button("🗑️", key=f"delete_{idx}", help="삭제"):
                st.session_state.sell_orders.pop(idx)
                st.rerun()

st.divider()

# 계산하기 버튼
if st.button("🔢 계산하기", type="primary", use_container_width=True):
    # 매도 주문들을 가격 높은 순으로 정렬
    sell_orders_sorted = sorted(
        st.session_state.sell_orders, 
        key=lambda x: x['price'], 
        reverse=True
    )
    
    # 매수가보다 낮은 매도가가 있는지 확인
    lower_sell_prices = [order['price'] for order in sell_orders_sorted if order['price'] < buy_price]
    
    # 매수가 조정: 매수가보다 낮은 매도가가 있으면 가장 낮은 매도가 - 0.01, 없으면 매수가 - 0.01
    if lower_sell_prices:
        min_lower_price = min(lower_sell_prices)
        new_buy_price = round(min_lower_price - 0.01, 2)
    else:
        new_buy_price = round(buy_price - 0.01, 2)
    
    new_sell_orders = []
    remaining_buy_quantity = buy_quantity
    
    for sell_order in sell_orders_sorted:
        sell_price = sell_order['price']
        sell_quantity = sell_order['quantity']
        
        # 매수가보다 낮은 매도가인 경우
        if sell_price < buy_price:
            adjusted_price = round(buy_price + 0.01, 2)
            
            # 남은 매수 수량이 있고, 매도 수량과 매칭되는 경우
            if remaining_buy_quantity > 0:
                if sell_quantity <= remaining_buy_quantity:
                    # 전체가 매칭되는 경우 - 조정된 가격으로 추가
                    new_sell_orders.append({
                        'type': sell_order['type'],
                        'price': adjusted_price,
                        'quantity': sell_quantity
                    })
                    remaining_buy_quantity -= sell_quantity
                else:
                    # 일부만 매칭되는 경우 - 매칭된 부분은 조정된 가격, 나머지는 원래 가격
                    new_sell_orders.append({
                        'type': sell_order['type'],
                        'price': adjusted_price,
                        'quantity': remaining_buy_quantity
                    })
                    new_sell_orders.append({
                        'type': sell_order['type'],
                        'price': sell_price,
                        'quantity': sell_quantity - remaining_buy_quantity
                    })
                    remaining_buy_quantity = 0
            else:
                # 매칭되지 않는 경우 - 원래 가격으로 추가
                new_sell_orders.append({
                    'type': sell_order['type'],
                    'price': sell_price,
                    'quantity': sell_quantity
                })
        else:
            # 매수가보다 높거나 같은 매도가는 그대로
            if remaining_buy_quantity > 0:
                if sell_quantity <= remaining_buy_quantity:
                    # 전체가 매칭되는 경우 - 결과에서 제외 (퉁치기)
                    remaining_buy_quantity -= sell_quantity
                else:
                    # 일부만 매칭되는 경우 - 남은 부분만 추가
                    new_sell_orders.append({
                        'type': sell_order['type'],
                        'price': sell_price,
                        'quantity': sell_quantity - remaining_buy_quantity
                    })
                    remaining_buy_quantity = 0
            else:
                # 매칭되지 않는 경우 - 그대로 추가
                new_sell_orders.append({
                    'type': sell_order['type'],
                    'price': sell_price,
                    'quantity': sell_quantity
                })
    
    # 매도 주문을 가격 높은 순으로 다시 정렬 (결과 표시용)
    new_sell_orders_sorted = sorted(new_sell_orders, key=lambda x: x['price'], reverse=True)
    
    # 결과 저장
    st.session_state.result = {
        'new_buy_order': {
            'type': buy_type,
            'price': new_buy_price,
            'quantity': buy_quantity
        },
        'new_sell_orders': new_sell_orders_sorted
    }

# 계산 결과 표시
if 'result' in st.session_state:
    st.divider()
    st.header("계산 결과")
    
    result = st.session_state.result
    new_buy = result['new_buy_order']
    new_sells = result['new_sell_orders']
    
    st.subheader("새로운 매수 주문")
    st.write(f"{new_buy['type']} - 가격: {new_buy['price']:.2f}, 수량: {new_buy['quantity']}")
    
    st.subheader("새로운 매도 주문")
    for sell_order in new_sells:
        st.write(f"{sell_order['type']} - 가격: {sell_order['price']:.2f}, 수량: {sell_order['quantity']}")

