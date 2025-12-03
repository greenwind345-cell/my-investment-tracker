import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ---------------------------------------------------------
# 1. 頁面設定與 CSS 樣式
# ---------------------------------------------------------
st.set_page_config(page_title="投資分析 App", layout="wide")

# 自定義 CSS
st.markdown("""
    <style>
    /* 全局背景色: 深藍色 #003060 */
    .stApp {
        background-color: #003060;
    }
    
    /* 全局文字: 白色 */
    .stApp, p, label, .stMarkdown, h1, h2, h3, h4, h5, h6, span, div {
        color: #FFFFFF;
    }

    /* 隱藏數字輸入框的 +/- 按鈕 */
    div[data-testid="stNumberInput"] button {
        display: none;
    }

    /* --- 輸入框樣式優化 --- */
    /* 輸入框背景半透明黑，文字白色 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        color: #FFFFFF !important; 
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #FFFFFF !important;
    }
    
    /* 唯讀輸入框 (disabled) 的樣式修正 - 確保字體是白色 */
    .stTextInput input:disabled {
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        opacity: 1 !important; /* 防止變灰 */
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* 下拉選單選項 */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #003060;
        color: white;
    }

    /* 按鈕樣式 (黑色底，白色字) */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        font-weight: bold;
        border-radius: 5px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #333333 !important;
        border-color: #66B3FF !important;
    }
    /* 刪除確認按鈕 (紅字) */
    div.stButton > button[kind="primary"] {
        background-color: #000000 !important;
        color: #CE0000 !important;
        border: 1px solid #CE0000 !important;
    }

    /* --- 表格樣式還原 --- */
    .table-stock-header {
        background-color: #66B3FF;
        color: #000000 !important;
        font-size: 18px;
        font-weight: bold;
        padding: 8px;
        text-align: center;
        border-top: 1px solid #000;
        border-left: 1px solid #000;
        border-right: 1px solid #000;
        margin-bottom: 0px;
    }

    div[data-testid="stDataFrame"] {
        background-color: transparent !important;
        padding: 0px !important;
    }
    
    div[data-testid="stDataFrame"] table thead tr th {
        background-color: #E0E0E0 !important;
        color: #000000 !important;
        font-size: 14px !important;
        border-bottom: 1px solid #000 !important;
    }
    
    div[data-testid="stDataFrame"] table tbody tr td {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 初始化 Session State
# ---------------------------------------------------------
if 'data' not in st.session_state:
    st.session_state.data = [] 
if 'current_stock_name' not in st.session_state:
    st.session_state.current_stock_name = ""
if 'current_stock_id' not in st.session_state:
    st.session_state.current_stock_id = ""

# ---------------------------------------------------------
# 3. 股票搜尋區 (修改版: 雙欄位 + Enter 自動搜尋)
# ---------------------------------------------------------
# 使用 columns 將兩個輸入框並排
col_input, col_output = st.columns(2)

with col_input:
    # 移除 form，這樣按下 Enter 就會觸發 rerun
    # 加上 key 讓 Streamlit 追蹤狀態
    stock_input = st.text_input("輸入代號", placeholder="例如:0050，輸入完畢後請按enter")

# 邏輯處理：當 stock_input 有值時執行搜尋
display_name = ""
if stock_input:
    stock_id = stock_input.strip()
    ticker_name = f"{stock_id}.TW"
    
    # 常用台股代碼對應
    manual_map = {
        "0050": "元大台灣50",
        "0056": "元大高股息",
        "00878": "國泰永續高股息",
        "2330": "台積電",
        "2317": "鴻海",
        "2454": "聯發科",
        "2603": "長榮"
    }
    
    found_name = manual_map.get(stock_id, None)
    
    if not found_name:
        try:
            info = yf.Ticker(ticker_name).info
            found_name = info.get('longName', info.get('shortName', stock_id))
        except:
            found_name = "查無資料 / API 無回應"
    
    # 更新 Session State
    st.session_state.current_stock_name = found_name
    st.session_state.current_stock_id = stock_id
    display_name = found_name
else:
    # 若清空輸入框，也清空名稱
    st.session_state.current_stock_name = ""
    st.session_state.current_stock_id = ""
    display_name = ""

with col_output:
    # 顯示全名的欄位，設定為 disabled (唯讀)，value 綁定搜尋結果
    st.text_input("股票全名", value=display_name, disabled=True)

# ---------------------------------------------------------
# 4. 資料輸入區
# ---------------------------------------------------------
TRANS_TYPES = ["定期定額", "定期定額加碼", "個股", "賣出"]

with st.form("entry_form", clear_on_submit=True):
    
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_type = st.selectbox("交易類型", TRANS_TYPES)
    with c2:
        input_date = st.date_input("時間", datetime.today())
    with c3:
        price_in = st.number_input("購入股價", min_value=0.0, step=0.1, format="%.2f")

    c4, c5, c6 = st.columns(3)
    with c4:
        shares_in = st.number_input("購入股數", min_value=0, step=1)
    with c5:
        price_out = st.number_input("賣出股價", min_value=0.0, step=0.1, format="%.2f")
    with c6:
        shares_out = st.number_input("賣出股數", min_value=0, step=1)
        
    c7, c8, c9 = st.columns(3)
    with c7:
        avg_price = st.number_input("現股均價 (賣出填)", min_value=0.0, step=0.1, format="%.2f")
    with c8:
        total_amount_val = st.number_input("成交價 (含費)", min_value=0.0, step=1.0, format="%.2f")
    with c9:
        trade_mode = st.radio("資金流向", ["買入 (-)", "賣出 (+)"], horizontal=True)

    submitted = st.form_submit_button("確認輸入 (Enter)")

    if submitted:
        is_buy = trade_mode == "買入 (-)"
        final_amount = -abs(total_amount_val) if is_buy else abs(total_amount_val)
        
        new_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "delete": False,
            "date": input_date,
            "type": selected_type,
            "buy_price": price_in if price_in > 0 else 0,
            "buy_shares": shares_in if shares_in > 0 else 0,
            "sell_price": price_out if price_out > 0 else 0,
            "sell_shares": shares_out if shares_out > 0 else 0,
            "avg_price": avg_price if avg_price > 0 else 0,
            "total_amount": final_amount, 
        }
        
        st.session_state.data.append(new_entry)
        st.session_state.data.sort(key=lambda x: x['date'])
        st.success("資料已輸入")

# ---------------------------------------------------------
# 5. 表格生成與操作按鈕
# ---------------------------------------------------------
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("生成表格 (清除舊資料)"):
        st.session_state.data = []
        st.rerun()
with col_btn2:
    if st.button("輸入至同一表格 (刷新)"):
        st.rerun()

# ---------------------------------------------------------
# 6. 表格顯示區
# ---------------------------------------------------------
if st.session_state.data:
    st.markdown("<br>", unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.data)
    df['date'] = pd.to_datetime(df['date']).dt.date

    # 顯示表格第一列標題
    header_text = f"{st.session_state.current_stock_id} {st.session_state.current_stock_name}" if st.session_state.current_stock_id else "尚未輸入代號"
    st.markdown(f'<div class="table-stock-header">{header_text}</div>', unsafe_allow_html=True)

    column_config = {
        "delete": st.column_config.CheckboxColumn("刪除", width="small"),
        "date": st.column_config.DateColumn("日期", format="YYYY/MM/DD"),
        "type": st.column_config.TextColumn("交易類型", width="medium"),
        "buy_price": st.column_config.NumberColumn("購入股價", format="$%.2f"),
        "buy_shares": st.column_config.NumberColumn("購入股數"),
        "sell_price": st.column_config.NumberColumn("賣出股價", format="$%.2f"),
        "sell_shares": st.column_config.NumberColumn("賣出股數"),
        "avg_price": st.column_config.NumberColumn("現股均價", format="$%.2f"),
        "total_amount": st.column_config.NumberColumn("成交價(含費)", format="$%.2f"),
        "id": None
    }

    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        disabled=["id"],
        key="editor"
    )

    # 刪除功能
    rows_to_delete = edited_df[edited_df.delete == True]
    if not rows_to_delete.empty:
        st.error("⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
        c_del_1, c_del_2 = st.columns([1, 6])
        with c_del_1:
            if st.button("是", type="primary"):
                st.session_state.data = edited_df[edited_df.delete == False].drop(columns=['delete']).to_dict('records')
                for d in st.session_state.data:
                    d['delete'] = False
                st.rerun()
        with c_del_2:
            if st.button("否"):
                st.rerun()
    else:
        st.session_state.data = edited_df.to_dict('records')

    # ---------------------------------------------------------
    # 7. 總計表格
    # ---------------------------------------------------------
    st.markdown("### 總計表格")
    
    if st.session_state.data:
        calc_df = pd.DataFrame(st.session_state.data)
        
        reg_df = calc_df[calc_df['type'] == "定期定額"]
        bonus_df = calc_df[calc_df['type'] == "定期定額加碼"]
        sell_df = calc_df[calc_df['type'] == "賣出"]
        
        reg_total_price = abs(reg_df['total_amount'].sum())
        reg_total_shares = reg_df['buy_shares'].sum()
        bonus_total_price = abs(bonus_df['total_amount'].sum())
        bonus_total_shares = bonus_df['buy_shares'].sum()
        
        buy_total_amt = reg_total_price + bonus_total_price
        buy_total_shares = reg_total_shares + bonus_total_shares
        
        sell_total_amt = sell_df['total_amount'].sum()
        sell_total_shares = sell_df['sell_shares'].sum()
        
        cost = (sell_df['avg_price'] * sell_df['sell_shares']).sum()
        profit = sell_total_amt - buy_total_amt

        summary_data = {
            "股票編號": [st.session_state.current_stock_id],
            "定期定額總價": [reg_total_price],
            "定期定額股數": [reg_total_shares],
            "加碼總價": [bonus_total_price],
            "加碼股數": [bonus_total_shares],
            "買入總額": [buy_total_amt],
            "買入總股數": [buy_total_shares],
            "賣出總額": [sell_total_amt],
            "總賣出股數": [sell_total_shares],
            "成本": [cost],
            "獲利": [profit]
        }
        
        summ_df = pd.DataFrame(summary_data)

        def highlight_summary(row):
            styles = [''] * len(row)
            green_text = 'color: #00A600; font-weight: bold;'
            red_text = 'color: #CE0000; font-weight: bold;'
            
            styles[1] = green_text
            styles[3] = green_text
            styles[5] = green_text
            styles[7] = red_text
            
            profit_val = row[10]
            if profit_val > 0:
                styles[10] = red_text
            elif profit_val < 0:
                styles[10] = green_text
            return styles

        st.dataframe(
            summ_df.style.apply(highlight_summary, axis=1).format("{:.2f}", subset=[
                "定期定額總價", "加碼總價", "買入總額", "賣出總額", "成本", "獲利"
            ]),
            hide_index=True,
            use_container_width=True
        )
