import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ---------------------------------------------------------
# 1. 頁面設定與 CSS 樣式 (視覺還原)
# ---------------------------------------------------------
st.set_page_config(page_title="投資分析 App", layout="wide")

# 自定義 CSS
st.markdown("""
    <style>
    /* 全局背景色: 深藍色 #003060 */
    .stApp {
        background-color: #003060;
    }
    
    /* 全局文字: 白色 #FFFFFF */
    .stApp, p, label, .stMarkdown, h1, h2, h3, h4, h5, h6, span, div {
        color: #FFFFFF;
    }

    /* 表格第一列樣式: 股票全名及代號 (#66B3FF 背景, #000000 文字) */
    .stock-header {
        background-color: #66B3FF;
        color: #000000 !important;
        font-size: 20px;
        font-weight: bold;
        padding: 12px;
        border-radius: 5px 5px 0 0; /* 上圓角 */
        margin-bottom: 0px;
        text-align: center;
        border: 1px solid #000;
    }

    /* 表格第二列樣式: 分類標題 (#E0E0E0 背景, #000000 文字) */
    .category-header {
        background-color: #E0E0E0;
        color: #000000 !important;
        font-size: 16px;
        font-weight: bold;
        padding: 10px;
        margin-top: 0px;
        margin-bottom: 15px;
        text-align: center;
        border-left: 1px solid #000;
        border-right: 1px solid #000;
        border-bottom: 1px solid #000;
    }

    /* --- 輸入框樣式優化 --- */
    /* 讓輸入框背景半透明，文字白色，避免被背景吃掉 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        color: #FFFFFF !important; 
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid #FFFFFF !important;
    }
    /* 下拉選單的選項顏色修正 */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #003060;
        color: white;
    }

    /* 按鈕樣式 (Enter) */
    .stButton button {
        background-color: #E0E0E0;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 5px;
        border: 1px solid #000;
    }

    /* 表格容器樣式 (讓表格在深色背景中突顯，模仿 Excel 白底) */
    div[data-testid="stDataFrame"] {
        background-color: white; 
        padding: 5px;
        border-radius: 5px;
        color: black !important;
    }
    
    /* 修正表格內文字顏色為黑色 (Streamlit data editor 預設) */
    div[data-testid="stDataFrame"] * {
        color: #000000 !important;
    }

    /* 總計表格的文字顏色邏輯會由 Pandas Styler 處理，但確保背景可讀 */
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 初始化 Session State
# ---------------------------------------------------------
if 'data' not in st.session_state:
    st.session_state.data = [] 
if 'current_stock_name' not in st.session_state:
    st.session_state.current_stock_name = "尚未選擇股票"
if 'current_stock_id' not in st.session_state:
    st.session_state.current_stock_id = ""

# ---------------------------------------------------------
# 3. 股票搜尋區 (模擬表格第一列)
# ---------------------------------------------------------
col_search, col_space = st.columns([1, 2])

with col_search:
    # 使用 Form 處理 Enter
    with st.form("stock_search"):
        stock_input = st.text_input("輸入代號 (按 Enter):", placeholder="例如: 0050")
        search_submitted = st.form_submit_button("搜尋")

if search_submitted and stock_input:
    stock_id = stock_input.strip()
    ticker_name = f"{stock_id}.TW"
    
    # 常用台股代碼對應 (因為 Yahoo Finance API 抓中文名稱有時不穩)
    # 您可以根據需求擴充這個字典
    manual_map = {
        "0050": "元大台灣50",
        "0056": "元大高股息",
        "00878": "國泰永續高股息",
        "2330": "台積電",
        "2317": "鴻海",
        "2454": "聯發科",
        "2603": "長榮"
    }
    
    stock_name_display = manual_map.get(stock_id, None)
    
    if not stock_name_display:
        try:
            info = yf.Ticker(ticker_name).info
            # 嘗試抓取 longName，若無則用代號
            stock_name_display = info.get('longName', info.get('shortName', stock_id))
        except:
            stock_name_display = "未知股票 / API 無回應"

    st.session_state.current_stock_name = stock_name_display
    st.session_state.current_stock_id = stock_id

# 顯示表格標題樣式 (Row 1)
header_text = f"{st.session_state.current_stock_id} {st.session_state.current_stock_name}" if st.session_state.current_stock_id else "請輸入代號"
st.markdown(f'<div class="stock-header">{header_text}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 資料輸入區 (模擬表格第二、三列)
# ---------------------------------------------------------
TRANS_TYPES = ["定期定額", "定期定額加碼", "個股", "賣出"]

# 顯示分類標題樣式 (Row 2)
st.markdown('<div class="category-header">定期定額 | 定期定額加碼 | 個股 | 賣出</div>', unsafe_allow_html=True)

with st.form("entry_form", clear_on_submit=True):
    
    # 輸入區塊 - 盡量不擋住下一行
    # 第一行輸入
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_type = st.selectbox("交易類型", TRANS_TYPES)
    with c2:
        input_date = st.date_input("1. 時間", datetime.today())
    with c3:
        price_in = st.number_input("2. 購入股價", min_value=0.0, step=0.1, format="%.2f")

    # 第二行輸入
    c4, c5, c6 = st.columns(3)
    with c4:
        shares_in = st.number_input("3. 購入股數", min_value=0, step=1)
    with c5:
        # 賣出相關 (預設0，選賣出時填寫)
        price_out = st.number_input("4. 賣出股價", min_value=0.0, step=0.1, format="%.2f")
    with c6:
        shares_out = st.number_input("5. 賣出股數", min_value=0, step=1)
        
    # 第三行輸入
    c7, c8, c9 = st.columns(3)
    with c7:
        avg_price = st.number_input("6. 現股均價 (僅賣出填)", min_value=0.0, step=0.1, format="%.2f")
    with c8:
        # 成交價選擇
        total_amount_val = st.number_input("7. 成交價 (含費)", min_value=0.0, step=1.0, format="%.2f")
    with c9:
        trade_mode = st.radio("資金流向", ["買入 (-)", "賣出 (+)"], horizontal=True)

    # 模擬 Enter 按鈕
    submitted = st.form_submit_button("確認輸入 (Enter)")

    if submitted:
        # 處理正負號與顏色邏輯
        is_buy = trade_mode == "買入 (-)"
        # 雖然存入數值，但顯示顏色由 Pandas Styler 或 Column Config 決定
        # 為了計算方便，買入存負值，賣出存正值 (或依需求全存正值，計算時判斷)
        # 依照題目：輸入欄位顯示 - 或 +
        final_amount = -abs(total_amount_val) if is_buy else abs(total_amount_val)
        
        new_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"), # 唯一ID
            "delete": False,
            "date": input_date,
            "type": selected_type,
            "buy_price": price_in if price_in > 0 else 0,
            "buy_shares": shares_in if shares_in > 0 else 0,
            "sell_price": price_out if price_out > 0 else 0,
            "sell_shares": shares_out if shares_out > 0 else 0,
            "avg_price": avg_price if avg_price > 0 else 0,
            "total_amount": final_amount, # 實際數值
        }
        
        st.session_state.data.append(new_entry)
        # 時間排序 (早到晚)
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
# 6. 表格顯示區 (Editable)
# ---------------------------------------------------------
if st.session_state.data:
    st.markdown("---")
    
    df = pd.DataFrame(st.session_state.data)
    df['date'] = pd.to_datetime(df['date']).dt.date

    # 設定顯示格式 (Column Config)
    column_config = {
        "delete": st.column_config.CheckboxColumn("刪除?", width="small"),
        "date": st.column_config.DateColumn("日期", format="YYYY/MM/DD"),
        "type": st.column_config.TextColumn("分類", width="medium"),
        "buy_price": st.column_config.NumberColumn("購入股價", format="$%.2f"),
        "buy_shares": st.column_config.NumberColumn("購入股數"),
        "sell_price": st.column_config.NumberColumn("賣出股價", format="$%.2f"),
        "sell_shares": st.column_config.NumberColumn("賣出股數"),
        "avg_price": st.column_config.NumberColumn("現股均價", format="$%.2f"),
        "total_amount": st.column_config.NumberColumn("成交價(含費)", format="$%.2f"),
        "id": None # 隱藏
    }

    # 顯示編輯器
    # 注意：這裡使用單一表格呈現，因為手機上左右分割兩個表格會非常難以閱讀與編輯
    # 我們利用「分類」欄位來區分 定期定額/加碼
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        disabled=["id"],
        key="editor"
    )

    # 刪除防呆邏輯
    rows_to_delete = edited_df[edited_df.delete == True]
    if not rows_to_delete.empty:
        st.error(⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
        c_del_1, c_del_2 = st.columns([1, 6])
        with c_del_1:
            if st.button("是", type="primary"):
                # 執行刪除
                st.session_state.data = edited_df[edited_df.delete == False].drop(columns=['delete']).to_dict('records')
                # 補回 delete 預設值
                for d in st.session_state.data:
                    d['delete'] = False
                st.rerun()
        with c_del_2:
            if st.button("否"):
                st.rerun()
    else:
        # 儲存編輯結果
        # 移除 delete 欄位再存，避免髒資料，但為了 UI 狀態保持，我們先直接轉存
        st.session_state.data = edited_df.to_dict('records')


    # ---------------------------------------------------------
    # 7. 總計表格生成
    # ---------------------------------------------------------
    st.markdown("### 總計表格")
    
    if st.session_state.data:
        calc_df = pd.DataFrame(st.session_state.data)
        
        # 篩選資料
        reg_df = calc_df[calc_df['type'] == "定期定額"]
        bonus_df = calc_df[calc_df['type'] == "定期定額加碼"]
        sell_df = calc_df[calc_df['type'] == "賣出"]
        
        # 計算各項總和
        # 1. 定期定額總價 (成交價加總，通常輸入為負，取絕對值)
        reg_total_price = abs(reg_df['total_amount'].sum())
        reg_total_shares = reg_df['buy_shares'].sum()
        
        # 2. 加碼總價
        bonus_total_price = abs(bonus_df['total_amount'].sum())
        bonus_total_shares = bonus_df['buy_shares'].sum()
        
        # 3. 買入總額 (定期 + 加碼)
        buy_total_amt = reg_total_price + bonus_total_price
        buy_total_shares = reg_total_shares + bonus_total_shares
        
        # 4. 賣出總額 (正數)
        sell_total_amt = sell_df['total_amount'].sum()
        sell_total_shares = sell_df['sell_shares'].sum()
        
        # 5. 成本 (現股均價 * 賣出股數)
        cost = (sell_df['avg_price'] * sell_df['sell_shares']).sum()
        
        # 6. 獲利 (賣出總額 - 買入總額)
        # 注意：這裡邏輯是 "總賣出回收金額" - "總投入成本" 嗎？
        # 題目公式：獲利 = 賣出總額 - 買入總額
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

        # 樣式與顏色邏輯
        def highlight_summary(row):
            styles = [''] * len(row)
            
            # 定義色碼
            green_text = 'color: #00A600; font-weight: bold;'
            red_text = 'color: #CE0000; font-weight: bold;'
            
            # 欄位索引對應 (0-based)
            # 1: 定期定額總價 (綠)
            styles[1] = green_text
            # 3: 加碼總價 (綠)
            styles[3] = green_text
            # 5: 買入總額 (綠)
            styles[5] = green_text
            # 7: 賣出總額 (紅)
            styles[7] = red_text
            
            # 10: 獲利 (正紅/負綠)
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
