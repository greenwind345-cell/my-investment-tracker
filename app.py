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
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        color: #FFFFFF !important; 
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #FFFFFF !important;
    }
    
    /* 唯讀輸入框樣式 */
    .stTextInput input:disabled {
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* 下拉選單選項 */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #003060;
        color: white;
    }

    /* --- 按鈕樣式 (黑色底，白色字) --- */
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
    
    /* 表格標題列 (灰色) */
    div[data-testid="stDataFrame"] table thead tr th {
        background-color: #E0E0E0 !important;
        color: #000000 !important;
        font-size: 14px !important;
        border-bottom: 1px solid #000 !important;
    }
    
    /* 表格內容 (白色) */
    div[data-testid="stDataFrame"] table tbody tr td {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* 導航列置中與樣式 */
    .nav-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
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
# 新增: 紀錄目前檢視的年份 (預設為今年)
if 'view_year' not in st.session_state:
    st.session_state.view_year = datetime.now().year

# ---------------------------------------------------------
# 3. 股票搜尋區
# ---------------------------------------------------------
col_input, col_output = st.columns(2)

with col_input:
    stock_input = st.text_input("輸入代號", placeholder="例如:0050，輸入完畢後請按enter")

display_name = ""
if stock_input:
    stock_id = stock_input.strip()
    ticker_name = f"{stock_id}.TW"
    
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
    
    st.session_state.current_stock_name = found_name
    st.session_state.current_stock_id = stock_id
    display_name = found_name
else:
    st.session_state.current_stock_name = ""
    st.session_state.current_stock_id = ""
    display_name = ""

with col_output:
    st.text_input("股票全名", value=display_name, disabled=True)

# ---------------------------------------------------------
# 4. 資料輸入區
# ---------------------------------------------------------
TRANS_TYPES = ["定期定額", "定期定額加碼", "個股", "賣出"]

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
    # 修正標籤文字
    avg_price = st.number_input("現均股價 (僅賣出時填寫)", min_value=0.0, step=0.1, format="%.2f")
with c8:
    # 修正標籤文字
    total_amount_val = st.number_input("成交價 (含手續費)", min_value=0.0, step=1.0, format="%.2f")
with c9:
    trade_mode = st.radio("資金流向", ["買入 (-)", "賣出 (+)"], horizontal=True)

# ---------------------------------------------------------
# 5. 按鈕邏輯 (新增資料)
# ---------------------------------------------------------
def create_entry_data():
    """ 輔助函式：建立資料 """
    is_buy = trade_mode == "買入 (-)"
    final_amount = -abs(total_amount_val) if is_buy else abs(total_amount_val)
    
    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "delete": False,
        "date": input_date, # 這裡的 date 是 datetime.date 物件
        "type": selected_type,
        "buy_price": price_in if price_in > 0 else 0,
        "buy_shares": shares_in if shares_in > 0 else 0,
        "sell_price": price_out if price_out > 0 else 0,
        "sell_shares": shares_out if shares_out > 0 else 0,
        "avg_price": avg_price if avg_price > 0 else 0,
        "total_amount": final_amount, 
    }

col_btn1, col_btn2 = st.columns(2)

# 按鈕 1: 開始全新的篇章
with col_btn1:
    if st.button("開始全新的篇章"):
        # 邏輯: 
        # 1. 寫入資料
        # 2. 將檢視年份切換到該筆資料的年份 (即"新的一頁")
        # 3. 不刪除舊資料
        new_entry = create_entry_data()
        st.session_state.data.append(new_entry)
        st.session_state.view_year = input_date.year # 切換至新章節
        st.success(f"已開啟 {input_date.year} 年的新篇章")
        st.rerun()

# 按鈕 2: 更新到同一章
with col_btn2:
    if st.button("更新到同一章"):
        # 邏輯:
        # 1. 寫入資料
        # 2. 檢視年份切換到該筆資料的年份 (確保使用者看得到剛輸入的資料)
        new_entry = create_entry_data()
        st.session_state.data.append(new_entry)
        st.session_state.data.sort(key=lambda x: x['date']) # 排序
        st.session_state.view_year = input_date.year
        st.success("已更新資料")
        st.rerun()

# ---------------------------------------------------------
# 6. 表格顯示區 (年份導航 + 資料表格)
# ---------------------------------------------------------

# 計算所有存在的年份
all_years = sorted(list(set([d['date'].year for d in st.session_state.data])))
if not all_years:
    # 若無資料，預設當前年份
    all_years = [datetime.now().year]

# 確保 view_year 在有效範圍內 (防呆)
if st.session_state.view_year not in all_years:
    if all_years:
        st.session_state.view_year = all_years[-1] # 預設顯示最新年份

current_year_idx = all_years.index(st.session_state.view_year)

st.markdown("---")

# --- 年份導航列 ---
c_nav1, c_nav2, c_nav3, c_nav4, c_nav5 = st.columns([2, 1, 2, 1, 2])

# 左箭頭 (←)
with c_nav2:
    if current_year_idx > 0: # 如果不是最舊年份
        if st.button("←", key="prev_year"):
            st.session_state.view_year = all_years[current_year_idx - 1]
            st.rerun()

# 中間下拉選單 (模擬長按選擇年份)
with c_nav3:
    selected_year = st.selectbox(
        "選擇篇章", 
        all_years, 
        index=current_year_idx, 
        label_visibility="collapsed"
    )
    if selected_year != st.session_state.view_year:
        st.session_state.view_year = selected_year
        st.rerun()

# 右箭頭 (→)
with c_nav4:
    if current_year_idx < len(all_years) - 1: # 如果不是最新年份
        if st.button("→", key="next_year"):
            st.session_state.view_year = all_years[current_year_idx + 1]
            st.rerun()

# --- 資料篩選與顯示 ---
# 篩選出當前 view_year 的資料
current_year_data = [d for d in st.session_state.data if d['date'].year == st.session_state.view_year]

if current_year_data:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 顯示股票標題
    header_text = f"{st.session_state.current_stock_id} {st.session_state.current_stock_name} ({st.session_state.view_year}年)" if st.session_state.current_stock_id else f"尚未輸入代號 ({st.session_state.view_year}年)"
    st.markdown(f'<div class="table-stock-header">{header_text}</div>', unsafe_allow_html=True)

    # 顯示操作說明
    st.info("💡 點擊表格可以編輯數值，編輯完成後點擊表格外任意處即可儲存。若要刪除，請勾選「刪除」欄位後，點擊下方的紅色按鈕確認。")

    df = pd.DataFrame(current_year_data)
    df['date'] = pd.to_datetime(df['date']).dt.date

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

    # 刪除功能邏輯
    rows_to_delete = edited_df[edited_df.delete == True]
    if not rows_to_delete.empty:
        st.error("⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
        c_del_1, c_del_2 = st.columns([1, 6])
        with c_del_1:
            if st.button("是", type="primary"):
                # 找出要刪除的 IDs
                delete_ids = rows_to_delete['id'].tolist()
                # 從原始 session_state.data 中移除
                st.session_state.data = [d for d in st.session_state.data if d['id'] not in delete_ids]
                st.rerun()
        with c_del_2:
            if st.button("否"):
                st.rerun()
    else:
        # 更新編輯後的資料 (只更新當前年份的資料)
        # 這邊稍微複雜：我們需要將 edited_df 的變更寫回 session_state.data
        # 簡單作法：先從 session 中移除當年份舊資料，再加入編輯後的新資料
        # 但要注意不要把其他年份刪了
        
        # 1. 取得編輯後的 records
        edited_records = edited_df.to_dict('records')
        
        # 2. 更新 session_state
        # 建立一個 id 對應 map
        id_map = {d['id']: d for d in edited_records}
        
        # 3. 遍歷 session data，如果有在編輯清單中，就更新，否則保留
        new_session_data = []
        for d in st.session_state.data:
            if d['id'] in id_map:
                # 為了避免日期被 data_editor 改成 Timestamp，需轉回 date 物件
                updated_record = id_map[d['id']]
                if isinstance(updated_record['date'], pd.Timestamp):
                    updated_record['date'] = updated_record['date'].date()
                new_session_data.append(updated_record)
            else:
                new_session_data.append(d)
        
        st.session_state.data = new_session_data

    # ---------------------------------------------------------
    # 7. 本章重點 (總計表格)
    # ---------------------------------------------------------
    st.markdown("### 本章重點") # 名稱修改
    
    # 只計算「當前年份」的資料
    calc_df = pd.DataFrame(current_year_data)
    
    if not calc_df.empty:
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

        # 設定總計表格的欄位寬度 (解決負號被遮住的問題)
        st.dataframe(
            summ_df.style.apply(highlight_summary, axis=1).format("{:.2f}", subset=[
                "定期定額總價", "加碼總價", "買入總額", "賣出總額", "成本", "獲利"
            ]),
            hide_index=True,
            use_container_width=True,
            column_config={
                # 強制設定寬度為 medium，讓負號有空間顯示
                "買入總額": st.column_config.NumberColumn(width="medium"),
                "獲利": st.column_config.NumberColumn(width="medium"),
                "定期定額總價": st.column_config.NumberColumn(width="medium"),
                "加碼總價": st.column_config.NumberColumn(width="medium"),
                "賣出總額": st.column_config.NumberColumn(width="medium"),
                "成本": st.column_config.NumberColumn(width="medium"),
            }
        )
else:
    st.info(f"目前 {st.session_state.view_year} 年尚無資料，請由上方輸入。")
