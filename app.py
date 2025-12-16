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
col1, col2, col3 = st.columns([2, 2.5, 2.5])
with col1:
    buy_type = st.selectbox("종류", ["LOC", "MOC"], key="buy_type")
with col2:
    if buy_type == "MOC":
        buy_price = 0.0
        st.number_input("가격 (MOC)", value=0.0, disabled=True, key="buy_price")
    else:
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
            'quantity': 0,
            'is_moc': False
        })
        st.rerun()

# 매도 주문 리스트 표시
if len(st.session_state.sell_orders) > 0:
    for idx, order in enumerate(st.session_state.sell_orders):
        # 기존 주문에 is_moc 속성이 없으면 추가
        if 'is_moc' not in st.session_state.sell_orders[idx]:
            st.session_state.sell_orders[idx]['is_moc'] = (order.get('type', 'LOC') == 'MOC')
        
        col1, col2, col3, col4 = st.columns([1.5, 2, 2, 1])
        with col1:
            sell_type = st.selectbox(
                "종류", 
                ["LOC", "MOC"],
                index=0 if order.get('type', 'LOC') == 'LOC' else 1,
                key=f"sell_type_{idx}"
            )
            st.session_state.sell_orders[idx]['type'] = sell_type
            st.session_state.sell_orders[idx]['is_moc'] = (sell_type == 'MOC')
        with col2:
            if sell_type == "MOC":
                st.session_state.sell_orders[idx]['price'] = 0.0
                st.number_input(
                    "가격 (MOC)", 
                    value=0.0, 
                    disabled=True, 
                    key=f"sell_price_{idx}"
                )
            else:
                sell_price = st.number_input(
                    "가격", 
                    min_value=0.0, 
                    value=order.get('price', 0.0), 
                    step=0.01, 
                    format="%.2f", 
                    key=f"sell_price_{idx}"
                )
                st.session_state.sell_orders[idx]['price'] = sell_price
        with col3:
            sell_quantity = st.number_input(
                "수량", 
                min_value=0, 
                value=order.get('quantity', 0), 
                step=1, 
                key=f"sell_quantity_{idx}"
            )
            st.session_state.sell_orders[idx]['quantity'] = sell_quantity
        with col4:
            st.write("")  # 여백
            st.write("")  # 여백
            if st.button("🗑️", key=f"delete_{idx}", help="삭제", use_container_width=True):
                st.session_state.sell_orders.pop(idx)
                st.rerun()

st.divider()

# 계산하기 버튼
if st.button("🔢 계산하기", type="primary", use_container_width=True):
    # MOC가 아닌 매도 주문들만 가격 기준으로 정렬 (MOC는 별도 처리)
    loc_sell_orders = [order for order in st.session_state.sell_orders if order.get('type', 'LOC') != 'MOC' and order.get('price', 0) > 0]
    moc_sell_orders = [order for order in st.session_state.sell_orders if order.get('type', 'LOC') == 'MOC']
    
    # LOC 주문들을 가격 높은 순으로 정렬
    sell_orders_sorted = sorted(
        loc_sell_orders, 
        key=lambda x: x.get('price', 0), 
        reverse=True
    )
    
    # MOC 주문들을 맨 뒤에 추가
    sell_orders_sorted.extend(moc_sell_orders)
    
    # 매수가보다 낮은 매도가가 있는지 확인 (MOC 제외)
    lower_sell_prices = [order.get('price', 0) for order in sell_orders_sorted if order.get('type', 'LOC') != 'MOC' and order.get('price', 0) > 0 and order.get('price', 0) < buy_price]
    
    # 매수가 조정: 매수가보다 낮은 매도가가 있으면 가장 낮은 매도가 - 0.01, 없으면 매수가 - 0.01
    # MOC인 경우 매수가 조정 없음
    if buy_type == "MOC":
        new_buy_price = 0.0
    elif lower_sell_prices:
        min_lower_price = min(lower_sell_prices)
        new_buy_price = round(min_lower_price - 0.01, 2)
    else:
        new_buy_price = round(buy_price - 0.01, 2) if buy_price > 0 else 0.0
    
    new_sell_orders = []
    remaining_buy_quantity = buy_quantity
    
    for sell_order in sell_orders_sorted:
        sell_price = sell_order.get('price', 0)
        sell_quantity = sell_order.get('quantity', 0)
        is_moc = sell_order.get('type', 'LOC') == 'MOC'
        
        # MOC인 경우 종가 매도로 처리
        if is_moc:
            if remaining_buy_quantity > 0:
                if sell_quantity <= remaining_buy_quantity:
                    # 전체가 매칭되는 경우 - MOC는 결과에서 제외 (퉁치기)
                    remaining_buy_quantity -= sell_quantity
                else:
                    # 일부만 매칭되는 경우 - 남은 부분만 MOC로 추가
                    new_sell_orders.append({
                        'type': 'MOC',
                        'price': 0.0,
                        'quantity': sell_quantity - remaining_buy_quantity
                    })
                    remaining_buy_quantity = 0
            else:
                # 매칭되지 않는 경우 - MOC로 추가
                new_sell_orders.append({
                    'type': 'MOC',
                    'price': 0.0,
                    'quantity': sell_quantity
                })
            continue
        
        # 매수가보다 낮은 매도가인 경우 (LOC만, 매수 주문도 LOC인 경우만)
        if buy_type != "MOC" and buy_price > 0 and sell_price > 0 and sell_price < buy_price:
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
            # 매수가보다 높거나 같은 매도가는 그대로 (LOC만, 가격이 있는 경우만)
            if buy_type != "MOC" and sell_price > 0:
                if remaining_buy_quantity > 0:
                    if sell_quantity <= remaining_buy_quantity:
                        # 전체가 매칭되는 경우 - 결과에서 제외 (퉁치기)
                        remaining_buy_quantity -= sell_quantity
                    else:
                        # 일부만 매칭되는 경우 - 남은 부분만 추가
                        new_sell_orders.append({
                            'type': sell_order.get('type', 'LOC'),
                            'price': sell_price,
                            'quantity': sell_quantity - remaining_buy_quantity
                        })
                        remaining_buy_quantity = 0
                else:
                    # 매칭되지 않는 경우 - 그대로 추가
                    new_sell_orders.append({
                        'type': sell_order.get('type', 'LOC'),
                        'price': sell_price,
                        'quantity': sell_quantity
                    })
    
    # 매도 주문을 가격 높은 순으로 다시 정렬 (결과 표시용, MOC는 맨 뒤에)
    loc_results = [order for order in new_sell_orders if order.get('type', 'LOC') != 'MOC']
    moc_results = [order for order in new_sell_orders if order.get('type', 'LOC') == 'MOC']
    new_sell_orders_sorted = sorted(loc_results, key=lambda x: x.get('price', 0), reverse=True)
    new_sell_orders_sorted.extend(moc_results)
    
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
    if new_buy['type'] == 'MOC':
        st.write(f"{new_buy['type']} - 가격: 종가, 수량: {new_buy['quantity']}")
    else:
        st.write(f"{new_buy['type']} - 가격: {new_buy['price']:.2f}, 수량: {new_buy['quantity']}")
    
    st.subheader("새로운 매도 주문")
    for sell_order in new_sells:
        if sell_order.get('type', 'LOC') == 'MOC':
            st.write(f"{sell_order['type']} - 가격: 종가, 수량: {sell_order['quantity']}")
        else:
            st.write(f"{sell_order['type']} - 가격: {sell_order['price']:.2f}, 수량: {sell_order['quantity']}")

