import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ---------------------------------------------------------
# 1. 頁面設定與 CSS 樣式
# ---------------------------------------------------------
st.set_page_config(page_title="投資分析 App", layout="wide")

# Google Drive 圖片處理 (維持上一個版本的設定，您可以替換 ID)
input_border_url = "https://drive.google.com/uc?export=view&id=1Qu2Pr214eYhT0vMbCPLTPpzj0iPFklxV"
# 請填入您的表格邊框圖片 ID
table_border_id = "YOUR_IMAGE_ID_HERE" 
table_border_url = f"https://drive.google.com/uc?export=view&id={table_border_id}"

# 自定義 CSS
st.markdown(f"""
    <style>
    /* 1. 全局背景色: #132436 */
    .stApp {{
        background-color: #132436;
    }}
    
    /* 全局文字: 白色 */
    .stApp, p, label, .stMarkdown, h1, h2, h3, h4, h5, h6, span, div {{
        color: #FFFFFF;
    }}

    /* 隱藏數字輸入框的 +/- 按鈕 */
    div[data-testid="stNumberInput"] button {{
        display: none;
    }}

    /* --- 輸入框樣式 (羽毛邊框) --- */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {{
        background-color: transparent !important;
        border: none !important;
        border-bottom: 0px solid transparent !important;
        color: #FFFFFF !important;
        padding-left: 5px;
    }}
    
    div[data-testid="stTextInput"], div[data-testid="stNumberInput"], div[data-testid="stSelectbox"], div[data-testid="stDateInput"] {{
        background-image: url('{input_border_url}');
        background-size: 100% 40px;
        background-repeat: no-repeat;
        background-position: bottom center;
        padding-bottom: 15px;
        margin-bottom: 10px;
    }}
    
    ul[data-testid="stSelectboxVirtualDropdown"] li {{
        background-color: #132436;
        color: white;
    }}

    /* --- 按鈕樣式 (黑底白字) --- */
    div.stButton > button {{
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        font-weight: bold;
        border-radius: 5px;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: #333333 !important;
        border-color: #66B3FF !important;
    }}
    /* 刪除確認按鈕 (紅字) */
    div.stButton > button[kind="primary"] {{
        background-color: #000000 !important;
        color: #CE0000 !important;
        border: 1px solid #CE0000 !important;
    }}

    /* --- 表格樣式 --- */
    
    .table-stock-header {{
        background-color: #66B3FF;
        color: #000000 !important;
        font-size: 18px;
        font-weight: bold;
        padding: 8px;
        text-align: center;
        margin-bottom: 10px; 
    }}

    /* 表格容器與自定義邊框 (圖三) */
    div[data-testid="stDataFrame"] {{
        background-color: white;
        padding: 15px;
        
        /* 圖片邊框設定 */
        border-image: url('{table_border_url}') 30 stretch;
        border-width: 20px;
        border-style: solid;
        
        /* 預設邊框 (若圖片讀取不到) */
        border: 5px double #FFD700; 
        border-radius: 10px;
        transition: 0.2s;
    }}
    
    /* --- 紅色邊框互動設計 --- */
    /* 點擊表格內(編輯模式)時顯示紅框，點擊表格外(如按鈕)時消失 */
    div[data-testid="stDataFrame"]:focus-within {{
        border: 2px solid #CE0000 !important; /* 強制覆蓋原有邊框顯示紅框 */
        border-image: none !important; /* 編輯時暫時移除圖片邊框以顯示紅框，或可疊加 */
        box-shadow: 0 0 10px rgba(206, 0, 0, 0.8);
    }}
    
    /* 表格標題列 (灰色, 禁止選取) */
    div[data-testid="stDataFrame"] table thead tr th {{
        background-color: #E0E0E0 !important;
        color: #000000 !important;
        font-size: 14px !important;
        border-bottom: 1px solid #000 !important;
        pointer-events: none; /* 讓標題無法被點擊或拖曳 (模擬鎖定) */
    }}
    
    /* 表格內容 (白色) */
    div[data-testid="stDataFrame"] table tbody tr td {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }}
    
    /* 說明文字區塊 */
    div.stAlert {{
        background-color: rgba(0, 0, 0, 0.5);
        border: 1px solid #FFFFFF;
        color: #FFFFFF;
    }}

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
if 'view_year' not in st.session_state:
    st.session_state.view_year = datetime.now().year
if 'page' not in st.session_state:
    st.session_state.page = 'input'

# ---------------------------------------------------------
# 邏輯區塊
# ---------------------------------------------------------

if st.session_state.page == 'input':
    # ==========================================
    #               頁面 1: 輸入頁
    # ==========================================
    
    col_top_1, col_top_2 = st.columns([5, 1])
    with col_top_2:
        if st.session_state.data:
            if st.button("前往目前紀錄"):
                st.session_state.page = 'table'
                st.rerun()

    col_input, col_output = st.columns(2)
    with col_input:
        stock_input = st.text_input("輸入代號", placeholder="例如:0050，輸入完畢後請按enter")

    display_name = ""
    if stock_input:
        stock_id = stock_input.strip()
        ticker_name = f"{stock_id}.TW"
        manual_map = {
            "0050": "元大台灣50", "0056": "元大高股息", "00878": "國泰永續高股息",
            "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2603": "長榮"
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

    st.markdown("---")

    TRANS_TYPES = ["定期定額", "定期定額加碼", "個股", "賣出"]
    c1, c2, c3 = st.columns(3)
    with c1: selected_type = st.selectbox("交易類型", TRANS_TYPES)
    with c2: input_date = st.date_input("時間", datetime.today())
    with c3: price_in = st.number_input("購入股價", min_value=0.0, step=0.1, format="%.2f")

    c4, c5, c6 = st.columns(3)
    with c4: shares_in = st.number_input("購入股數", min_value=0, step=1)
    with c5: price_out = st.number_input("賣出股價", min_value=0.0, step=0.1, format="%.2f")
    with c6: shares_out = st.number_input("賣出股數", min_value=0, step=1)
        
    c7, c8, c9 = st.columns(3)
    with c7: avg_price = st.number_input("現均股價 (僅賣出時填寫)", min_value=0.0, step=0.1, format="%.2f")
    with c8: total_amount_val = st.number_input("成交價 (含手續費)", min_value=0.0, step=1.0, format="%.2f")
    with c9: trade_mode = st.radio("資金流向", ["買入 (-)", "賣出 (+)"], horizontal=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def create_entry_data():
        is_buy = trade_mode == "買入 (-)"
        final_amount = -abs(total_amount_val) if is_buy else abs(total_amount_val)
        return {
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

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("開始全新的篇章"):
            new_entry = create_entry_data()
            st.session_state.data.append(new_entry)
            st.session_state.view_year = input_date.year
            st.session_state.page = 'table'
            st.rerun()
    with col_btn2:
        if st.button("更新到同一章"):
            new_entry = create_entry_data()
            st.session_state.data.append(new_entry)
            st.session_state.data.sort(key=lambda x: x['date'])
            st.session_state.view_year = input_date.year
            st.session_state.page = 'table'
            st.rerun()


elif st.session_state.page == 'table':
    # ==========================================
    #               頁面 2: 表格頁
    # ==========================================
    
    if st.button("⬅️ 返回輸入頁面"):
        st.session_state.page = 'input'
        st.rerun()

    all_years = sorted(list(set([d['date'].year for d in st.session_state.data])))
    if not all_years:
        all_years = [datetime.now().year]
    if st.session_state.view_year not in all_years:
        if all_years:
            st.session_state.view_year = all_years[-1]
    current_year_idx = all_years.index(st.session_state.view_year)

    st.markdown("---")

    c_nav1, c_nav2, c_nav3, c_nav4, c_nav5 = st.columns([2, 1, 2, 1, 2])
    with c_nav2:
        if current_year_idx > 0:
            if st.button("←", key="prev_year"):
                st.session_state.view_year = all_years[current_year_idx - 1]
                st.rerun()
    with c_nav3:
        selected_year = st.selectbox("選擇篇章", all_years, index=current_year_idx, label_visibility="collapsed")
        if selected_year != st.session_state.view_year:
            st.session_state.view_year = selected_year
            st.rerun()
    with c_nav4:
        if current_year_idx < len(all_years) - 1:
            if st.button("→", key="next_year"):
                st.session_state.view_year = all_years[current_year_idx + 1]
                st.rerun()

    current_year_data = [d for d in st.session_state.data if d['date'].year == st.session_state.view_year]

    if current_year_data:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 1. 說明文字 (現在在標題上方)
        st.info("💡 點擊表格兩下編輯數值，編輯完成後點擊表格外任意處即可儲存。若要刪除，請勾選「刪除」欄位後，點擊下方的紅色按鈕確認。")

        # 2. 股票標題
        header_text = f"{st.session_state.current_stock_id} {st.session_state.current_stock_name} ({st.session_state.view_year}年)" if st.session_state.current_stock_id else f"尚未輸入代號 ({st.session_state.view_year}年)"
        st.markdown(f'<div class="table-stock-header">{header_text}</div>', unsafe_allow_html=True)

        # 3. 表格顯示
        df = pd.DataFrame(current_year_data)
        df['date'] = pd.to_datetime(df['date']).dt.date

        # 定義欄位順序 (防止亂序)
        column_order = [
            "delete", "date", "type", "buy_price", "buy_shares", 
            "sell_price", "sell_shares", "avg_price", "total_amount"
        ]

        column_config = {
            "delete": st.column_config.CheckboxColumn("刪除", width="small"),
            "date": st.column_config.DateColumn("日期", format="YYYY/MM/DD"),
            # 交易類型不可編輯
            "type": st.column_config.TextColumn("交易類型", width="medium", disabled=True),
            "buy_price": st.column_config.NumberColumn("購入股價", format="$%.2f"),
            "buy_shares": st.column_config.NumberColumn("購入股數"),
            "sell_price": st.column_config.NumberColumn("賣出股價", format="$%.2f"),
            "sell_shares": st.column_config.NumberColumn("賣出股數"),
            "avg_price": st.column_config.NumberColumn("現股均價", format="$%.2f"),
            # 成交價改成 (含手續費)
            "total_amount": st.column_config.NumberColumn("成交價(含手續費)", format="$%.2f"),
            "id": None
        }

        edited_df = st.data_editor(
            df,
            column_config=column_config,
            column_order=column_order, # 強制欄位順序
            use_container_width=True,  # 強制固定寬度
            hide_index=True,
            disabled=["id"],
            key="editor"
        )
        
        # 完成/儲存 按鈕 (處理紅框消失與自動計算)
        if st.button("完成 (儲存並計算)", use_container_width=True):
            # 更新編輯並執行計算
            edited_records = edited_df.to_dict('records')
            id_map = {d['id']: d for d in edited_records}
            
            new_session_data = []
            for d in st.session_state.data:
                if d['id'] in id_map:
                    updated_record = id_map[d['id']]
                    
                    # --- 自動計算邏輯 ---
                    t_type = updated_record.get('type', '')
                    if t_type == "賣出":
                        p = updated_record.get('sell_price', 0)
                        s = updated_record.get('sell_shares', 0)
                        updated_record['total_amount'] = abs(p * s)
                    else:
                        p = updated_record.get('buy_price', 0)
                        s = updated_record.get('buy_shares', 0)
                        updated_record['total_amount'] = -abs(p * s)
                    
                    if isinstance(updated_record['date'], pd.Timestamp):
                        updated_record['date'] = updated_record['date'].date()
                    new_session_data.append(updated_record)
                else:
                    new_session_data.append(d)
            st.session_state.data = new_session_data
            st.success("資料已更新並自動計算成交價！")
            st.rerun()

        # 刪除功能
        rows_to_delete = edited_df[edited_df.delete == True]
        if not rows_to_delete.empty:
            st.error("⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
            c_del_1, c_del_2 = st.columns([1, 6])
            with c_del_1:
                if st.button("是", type="primary"):
                    delete_ids = rows_to_delete['id'].tolist()
                    st.session_state.data = [d for d in st.session_state.data if d['id'] not in delete_ids]
                    st.rerun()
            with c_del_2:
                if st.button("否"):
                    st.rerun()

        # 4. 本章重點 (總計)
        st.markdown("### 本章重點")
        
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

            st.dataframe(
                summ_df.style.apply(highlight_summary, axis=1).format("{:.2f}", subset=[
                    "定期定額總價", "加碼總價", "買入總額", "賣出總額", "成本", "獲利"
                ]),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "買入總額": st.column_config.NumberColumn(width="medium"),
                    "獲利": st.column_config.NumberColumn(width="medium"),
                    "定期定額總價": st.column_config.NumberColumn(width="medium"),
                    "加碼總價": st.column_config.NumberColumn(width="medium"),
                    "賣出總額": st.column_config.NumberColumn(width="medium"),
                    "成本": st.column_config.NumberColumn(width="medium"),
                }
            )
    else:
        st.info(f"目前 {st.session_state.view_year} 年尚無資料。")
