Skip to main content
Temporary chat
35,801 tokens

Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
這是一個完整的 Streamlit 應用程式代碼，符合您所有的視覺與功能需求。我已經將它設計為單一 Python 檔案，您可以直接上傳到 GitHub 並在 Streamlit Cloud 上部署。
步驟 1: 準備檔案
請建立一個資料夾，並在裡面建立兩個檔案：
app.py (主程式碼)
requirements.txt (套件需求)
1. app.py
請將以下程式碼複製到 app.py：
code
Python
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ---------------------------------------------------------
# 1. 頁面設定與 CSS 樣式 (符合指定色碼)
# ---------------------------------------------------------
st.set_page_config(page_title="投資分析 App", layout="wide")

# 自定義 CSS
st.markdown("""
    <style>
    /* 全局背景色: 深藍色 #004B97 */
    .stApp {
        background-color: #004B97;
    }
    
    /* 文字預設白色 #FFFFFF, 大小 12 */
    .stApp, p, label, .stMarkdown {
        color: #FFFFFF !important;
        font-size: 12px;
    }

    /* 標題與輸入框標籤樣式調整 */
    h1, h2, h3 {
        color: #FFFFFF !important;
    }

    /* 第一列樣式: 股票全名及代號 (#66B3FF 背景, #000000 文字, 16px) */
    .stock-header {
        background-color: #66B3FF;
        color: #000000 !important;
        font-size: 16px;
        font-weight: bold;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        text-align: center;
    }

    /* 第二列樣式: 分類標題 (#E0E0E0 背景, #000000 文字, 14px) */
    .category-header {
        background-color: #E0E0E0;
        color: #000000 !important;
        font-size: 14px;
        font-weight: bold;
        padding: 8px;
        border-radius: 5px;
        margin-bottom: 10px;
        text-align: center;
    }

    /* 輸入區塊樣式微調 */
    .stTextInput input, .stNumberInput input, .stSelectbox, .stDateInput {
        color: #000000 !important;
    }
    
    /* 按鈕樣式 (模擬 Enter) */
    .stButton button {
        background-color: #E0E0E0;
        color: #000000;
        font-weight: bold;
    }
    
    /* 買入綠色 #00A600 */
    .money-buy {
        color: #00A600 !important;
        font-weight: bold;
    }
    
    /* 賣出紅色 #CE0000 */
    .money-sell {
        color: #CE0000 !important;
        font-weight: bold;
    }
    
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 初始化 Session State (儲存資料)
# ---------------------------------------------------------
if 'data' not in st.session_state:
    st.session_state.data = []  # 儲存所有交易紀錄
if 'current_stock_name' not in st.session_state:
    st.session_state.current_stock_name = "尚未選擇股票"
if 'current_stock_id' not in st.session_state:
    st.session_state.current_stock_id = ""

# ---------------------------------------------------------
# 3. 股票搜尋區 (第一列)
# ---------------------------------------------------------
col_input, col_display = st.columns([1, 3])

with col_input:
    stock_input = st.text_input("輸入代號 (按 Enter):", placeholder="例如: 2330")

if stock_input:
    # 簡單的 API 模擬與抓取 (使用 yfinance)
    stock_id = stock_input.strip()
    try:
        # 嘗試抓取台股
        ticker = f"{stock_id}.TW"
        info = yf.Ticker(ticker).info
        # 如果抓不到 longName，嘗試直接用輸入的代號
        stock_name = info.get('longName', f"股票代號 {stock_id}")
        st.session_state.current_stock_name = stock_name
        st.session_state.current_stock_id = stock_id
    except:
        st.session_state.current_stock_name = "查無此股 (或輸入錯誤)"
        st.session_state.current_stock_id = stock_id

# 顯示第一列 (背景色 #66B3FF)
st.markdown(f'<div class="stock-header">{st.session_state.current_stock_name} ({st.session_state.current_stock_id})</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 資料輸入區 (第二、三列)
# ---------------------------------------------------------

# 定義分類選項
TRANS_TYPES = ["定期定額", "定期定額加碼", "個股", "賣出"]

# 使用 Form 來處理輸入與 Enter 行為
with st.form("entry_form", clear_on_submit=True):
    
    # 第二列顯示 (背景色 #E0E0E0)
    st.markdown('<div class="category-header">交易類型 | 定期定額 | 定期定額加碼 | 個股 | 賣出</div>', unsafe_allow_html=True)
    
    # 第二列選擇
    selected_type = st.selectbox("選擇交易類型", TRANS_TYPES, label_visibility="collapsed")
    
    st.markdown("---")
    
    # 第三列輸入項目
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        input_date = st.date_input("1. 時間", datetime.today())
        # 金額輸入
        price_in = st.number_input("2. 購入股價", min_value=0.0, step=0.1, format="%.2f")
    
    with c2:
        shares_in = st.number_input("3. 購入股數", min_value=0, step=1)
        # 賣出相關 (僅在賣出時有效，但為了排版統一顯示，邏輯後續處理)
        price_out = st.number_input("4. 賣出股價", min_value=0.0, step=0.1, format="%.2f")

    with c3:
        shares_out = st.number_input("5. 賣出股數", min_value=0, step=1)
        avg_price = st.number_input("6. 現股均價 (僅賣出填寫)", min_value=0.0, step=0.1, format="%.2f")

    with c4:
        # 成交價處理
        total_mode = st.radio("資金流向", ["買入 (-)", "賣出 (+)"], horizontal=True)
        total_amount = st.number_input("7. 成交價(含手續費)", min_value=0.0, step=1.0, format="%.2f")

    # Enter 按鈕 (Form Submit)
    submitted = st.form_submit_button("確認輸入 (Enter)")

    if submitted:
        # 邏輯處理
        is_buy = total_mode == "買入 (-)"
        
        # 決定顏色與正負號
        display_amount = 0.0
        if is_buy:
            display_amount = -abs(total_amount) # 負號，綠色
        else:
            display_amount = abs(total_amount)  # 正號，紅色

        # 建立單筆資料字典
        new_entry = {
            "id": len(st.session_state.data) + 1,
            "stock_id": st.session_state.current_stock_id,
            "type": selected_type,
            "date": input_date,
            "buy_price": price_in if price_in > 0 else 0,
            "buy_shares": shares_in if shares_in > 0 else 0,
            "sell_price": price_out if price_out > 0 else 0,
            "sell_shares": shares_out if shares_out > 0 else 0,
            "avg_price": avg_price if avg_price > 0 else 0,
            "total_amount": display_amount, # 實際數值
            "total_display": total_amount # 顯示用絕對值
        }
        
        st.session_state.data.append(new_entry)
        # 重新排序 (時間早到晚)
        st.session_state.data.sort(key=lambda x: x['date'])
        st.success("資料已暫存！")

# ---------------------------------------------------------
# 5. 生成表格與功能按鈕
# ---------------------------------------------------------
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("生成表格 (清除舊資料)"):
        st.session_state.data = []
        st.rerun()

with col_btn2:
    st.button("輸入至同一表格 (刷新顯示)") # 實際上資料已經在 session_state，此按鈕觸發 rerun 刷新

st.markdown("---")

# ---------------------------------------------------------
# 6. 顯示資料表格 (可編輯、刪除邏輯)
# ---------------------------------------------------------

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    
    # 格式化日期
    df['date'] = pd.to_datetime(df['date']).dt.date

    # 準備顯示用的 DataFrame
    # 為了符合要求，我們需要自定義顯示格式，特別是顏色
    # Streamlit data_editor 支援 num_rows="dynamic" 進行刪除
    
    st.subheader("交易明細 (點擊儲存格編輯，選取行按 Delete 鍵或垃圾桶圖示刪除)")
    
    # 設定 Column Config 來優化顯示
    column_config = {
        "id": None, # 隱藏 ID
        "stock_id": "代號",
        "type": "分類",
        "date": "時間",
        "buy_price": st.column_config.NumberColumn("購入股價", format="$%.2f"),
        "buy_shares": st.column_config.NumberColumn("購入股數"),
        "sell_price": st.column_config.NumberColumn("賣出股價", format="$%.2f"),
        "sell_shares": st.column_config.NumberColumn("賣出股數"),
        "avg_price": st.column_config.NumberColumn("現股均價", format="$%.2f"),
        "total_amount": st.column_config.NumberColumn("成交價(含費)", format="$%.2f"),
        "total_display": None # 隱藏輔助欄
    }

    # 使用 data_editor 允許編輯與刪除
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic", # 允許增刪行
        use_container_width=True,
        hide_index=True,
        key="editor"
    )

    # 雙擊刪除防呆邏輯: Streamlit 原生 data_editor 刪除時沒有彈窗
    # 為了模擬"確認刪除"，我們可以比對 session_state 和 edited_df
    if len(edited_df) < len(st.session_state.data):
        # 偵測到刪除動作
        st.warning("您刪除了一筆資料。若需復原請勿重新整理頁面，但資料庫已更新。")
        st.session_state.data = edited_df.to_dict('records')
    elif not edited_df.equals(df):
        # 偵測到編輯動作
        st.session_state.data = edited_df.to_dict('records')

    # ---------------------------------------------------------
    # 7. 總計表格生成
    # ---------------------------------------------------------
    st.markdown("### 總計表格")
    
    # 計算邏輯
    # 篩選分類
    reg_df = df[df['type'] == "定期定額"]
    bonus_df = df[df['type'] == "定期定額加碼"]
    sell_df = df[df['type'] == "賣出"]
    
    # 1. 定期定額總價 (成交價加總，通常為負數，取絕對值顯示)
    reg_total_price = abs(reg_df['total_amount'].sum())
    # 2. 定期定額股數
    reg_total_shares = reg_df['buy_shares'].sum()
    
    # 3. 加碼總價
    bonus_total_price = abs(bonus_df['total_amount'].sum())
    # 4. 加碼股數
    bonus_total_shares = bonus_df['buy_shares'].sum()
    
    # 5. 買入總額 (定期 + 加碼) (個股 若算買入也要加，這裡依題目僅加這兩項)
    # 若 "個股" 分類也算買入，需在此加入。依照題目定義僅列出定期與加碼的加總。
    buy_total_amt = reg_total_price + bonus_total_price
    # 6. 買入總股數
    buy_total_shares = reg_total_shares + bonus_total_shares
    
    # 7. 賣出總額 (正數)
    sell_total_amt = sell_df['total_amount'].sum()
    # 8. 賣出總股數
    sell_total_shares = sell_df['sell_shares'].sum()
    
    # 9. 成本: 表格第三行的「現股均價」與同一列的「賣出股數」相乘的結果
    # 只有賣出的列才有意義
    cost = (sell_df['avg_price'] * sell_df['sell_shares']).sum()
    
    # 10. 獲利: 賣出總額 - 買入總額
    # 注意：這裡的買入總額依照題目是"定期+加碼"。如果有"個股"買入未計入，獲利會虛高。
    # 假設題目邏輯是針對這兩類策略的統計。
    profit = sell_total_amt - buy_total_amt

    # 建立總計 DataFrame
    summary_data = {
        "股票編號": [st.session_state.current_stock_id],
        "定期定額總價": [reg_total_price],
        "定期定額股數": [reg_total_shares],
        "加碼總價": [bonus_total_price],
        "加碼股數": [bonus_total_shares],
        "買入總額": [buy_total_amt],
        "買入總股數": [buy_total_shares],
        "賣出總額": [sell_total_amt],
        "賣出總股數": [sell_total_shares],
        "成本": [cost],
        "獲利": [profit]
    }
    
    summary_df = pd.DataFrame(summary_data)

    # 樣式函式: 針對特定欄位上色
    def highlight_summary(row):
        styles = [''] * len(row)
        # 欄位索引對應 (0-based)
        # 1: 定期定額總價 (Green)
        # 3: 加碼總價 (Green)
        # 5: 買入總額 (Green)
        # 7: 賣出總額 (Red)
        # 10: 獲利 (Red)
        
        green_style = 'color: #00A600; font-weight: bold;'
        red_style = 'color: #CE0000; font-weight: bold;'
        
        styles[1] = green_style
        styles[3] = green_style
        styles[5] = green_style
        styles[7] = red_style
        styles[10] = red_style
        return styles

    # 顯示總計表格 (使用 Pandas Styler)
    st.dataframe(
        summary_df.style.apply(highlight_summary, axis=1).format("{:.2f}", subset=["定期定額總價", "加碼總價", "買入總額", "賣出總額", "成本", "獲利"]),
        hide_index=True
    )
2. requirements.txt
請將以下內容複製到 requirements.txt：
code
Text
streamlit
pandas
yfinance
步驟 2: 如何上傳到 GitHub 並生成 App
GitHub 設定:
在 GitHub 建立一個新的 Repository (例如命名為 investment-app)。
將 app.py 和 requirements.txt 上傳到這個 Repository。
Streamlit Cloud 部署:
前往 share.streamlit.io 並註冊/登入。
點擊 "New app"。
選擇 "Use existing repo"。
選擇你剛剛建立的 GitHub Repository。
Branch 選擇 main (或 master)。
Main file path 輸入 app.py。
點擊 "Deploy"。
功能說明與操作流
版面與顏色:
背景已設為深藍色 (#004B97)。
文字顏色與大小皆依照需求調整 (白色為主，標題區塊有特定顏色)。
第一列 (股票搜尋):
輸入股票代號 (如 2330) 按 Enter。
系統會透過 API (yfinance) 抓取名稱，標題區塊背景為淺藍色 (#66B3FF)。
輸入區塊 (第二、三列):
包含所有指定欄位。
金額顏色邏輯: 在輸入「成交價」時，選擇「買入」會顯示為負數 (內部邏輯)，統計時顯示綠色；選擇「賣出」顯示紅色。
Enter 按鈕: 按下「確認輸入」按鈕後，資料會暫存，輸入框會清空以便輸入下一筆。
表格互動:
編輯: 生成的表格可以直接點擊修改數值。
刪除: 游標移到表格左側勾選行，按下 Delete 鍵 (電腦版) 或使用表格右上角的垃圾桶圖示 (手機版/電腦版皆有) 來刪除資料。會有提示訊息。
總計表格:
自動根據輸入的資料計算「定期定額」、「加碼」、「買入總和」、「賣出總和」、「成本」與「獲利」。
指定欄位已套用綠色 (#00A600) 與紅色 (#CE0000)。
這個 App 設計為 RWD (響應式)，在蘋果/安卓手機或平板上開啟瀏覽器皆可順暢使用。
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
這張截圖顯示的錯誤訊息 ModuleNotFoundError，且 traceback 指向 import yfinance as yf，這代表 Streamlit Cloud 的伺服器上沒有安裝到 yfinance 這個套件。
通常這是因為 requirements.txt 檔案有問題（遺失、命名錯誤或內容空白）所導致的。
請依照以下步驟檢查您的 GitHub 儲存庫（Repository）來修復這個問題：
解決步驟
1. 檢查檔案名稱
請確認您上傳到 GitHub 的檔案名稱必須一字不差，全小寫且包含副檔名：
✅ 正確：requirements.txt
❌ 錯誤：requirement.txt (少個 s)
❌ 錯誤：requirements.py (副檔名錯)
❌ 錯誤：Requirements.txt (大寫 R)
2. 檢查檔案內容
請確認 requirements.txt 檔案裡面有包含以下內容（每一行一個套件）：
code
Text
streamlit
pandas
yfinance
3. 檢查檔案位置
requirements.txt 必須跟您的 app.py 放都在最外層的同一個資料夾內。如果您的 app.py 在根目錄，requirements.txt 也要在根目錄。
如何修正並重新部署？
回到您的 GitHub 頁面。
確認是否有 requirements.txt 檔案。
如果沒有：點擊 "Add file" -> "Create new file"，檔名輸入 requirements.txt，內容貼上上面那三行，然後 Commit。
如果有但檔名錯了：點擊該檔案，按右上角的鉛筆圖示修改檔名。
回到 Streamlit Cloud 的管理介面。
通常 Streamlit 會偵測到 GitHub 的變更自動重新部署。如果沒有，請點擊右下角的 "Manage app"，然後點擊 "Reboot" (重啟)。
只要 requirements.txt 正確被讀取，Streamlit 在啟動時就會自動執行安裝 yfinance，這個錯誤就會消失了。
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
如果檢查過檔名 (requirements.txt) 和內容都正確，但錯誤依然存在，通常是因為 Streamlit Cloud「卡」在舊的環境設定裡了。
當第一次部署失敗（或是第一次部署時還沒有 requirements 檔）時，Streamlit 有時會快取（Cache）那個失敗的環境，導致你後來補上檔案後，它依然沒有重新安裝套件。
請嘗試以下最強制的解決方法：
方法一：徹底刪除並重新部署（最推薦，解決 90% 的卡頓問題）
單純的 Reboot（重啟）通常不夠，請依照以下步驟「打掉重練」：
進入 Streamlit Cloud 首頁。
找到你目前的 App。
點擊右邊的「三個點」圖示 ⋮，選擇 Delete（刪除）。
刪除後，點擊 New app。
重新選取你的 GitHub Repository 和 app.py。
點擊 Deploy。
為什麼這樣做有效？
這會強迫 Streamlit 分配一台全新的伺服器空間，並從頭開始讀取 requirements.txt 來安裝環境，避開舊的快取。
方法二：確認檔案層級（請再次檢查）
有時候是因為檔案放到了「資料夾」裡面。請確認你的 GitHub 檔案列表長得像下面這樣（都在最外層）：
code
Text
my-investment-app/  (你的 Repository 名字)
├── app.py          (主程式)
└── requirements.txt (設定檔)
錯誤示範（如果你的檔案在資料夾裡）：
code
Text
my-investment-app/
└── 程式碼資料夾/
    ├── app.py
    └── requirements.txt
如果是上面這種「錯誤示範」的情況，你在部署時，"Main file path" 那一欄必須填寫 程式碼資料夾/app.py，這樣 Streamlit 才會去該資料夾找 requirements 檔。
方法三：大絕招（寫在程式碼裡強迫安裝）
如果上面兩個方法都無效，你可以用 Python 程式碼強迫它在執行時安裝。請把 app.py 最上面的 import 區塊改成下面這樣：
code
Python
import streamlit as st
import subprocess
import sys

# --- 強迫安裝 yfinance ---
try:
    import yfinance as yf
except ImportError:
    # 如果找不到，就用指令安裝
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance as yf
# -----------------------

import pandas as pd
from datetime import datetime

# ... 以下接原本的程式碼 ...
注意：方法三雖然能解決問題，但會讓 App 每次啟動速度變慢（因為都要檢查安裝），建議還是以**方法一（刪除並重新部署）**為優先解決方案。
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
這是一個根據您的新需求調整後的 Streamlit 應用程式。我已經針對色碼 (#003060)、輸入框文字顏色、以及您指定的總計邏輯進行了修改。
修改重點：
背景色: 改為深藍色 #003060。
輸入框優化: 設定 CSS 讓輸入時文字顯示為白色 (#FFFFFF)，避免在深色背景下看不見。
表格邏輯:
採用單一表格整合所有交易資料（因為 Streamlit 難以在同一列做出左右分割且獨立捲動的表格，改為統一時間排序列表最適合手機閱讀）。
刪除功能: 由於 Streamlit 無法偵測「雙擊儲存格」 事件，我改用**「勾選刪除」**的方式。這是目前在手機網頁上最穩定的防呆刪除機制。
總計計算: 嚴格依照您提供的公式計算（包含獲利的正紅負綠顯示）。
程式碼 (app.py)
請將以下程式碼覆蓋原本的 app.py：
code
Python
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
    
    /* 全局文字: 白色 #FFFFFF */
    .stApp, p, label, .stMarkdown, h1, h2, h3, h4, h5, h6, span {
        color: #FFFFFF !important;
    }

    /* 第一列樣式: 股票全名及代號 (#66B3FF 背景, #000000 文字) */
    .stock-header {
        background-color: #66B3FF;
        color: #000000 !important;
        font-size: 20px;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: center;
    }

    /* 第二列樣式: 分類標題 (#E0E0E0 背景, #000000 文字) */
    .category-header {
        background-color: #E0E0E0;
        color: #000000 !important;
        font-size: 16px;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        text-align: center;
    }

    /* --- 輸入框樣式優化 --- */
    /* 讓輸入框背景稍微透明黑，文字白色，以免跟深藍背景混淆 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        color: #FFFFFF !important; 
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid #FFFFFF !important;
    }
    /* 下拉選單的選項顏色 (瀏覽器預設通常是白底黑字，這邊強制設黑底白字以防看不見) */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #003060;
        color: white;
    }

    /* 按鈕樣式 */
    .stButton button {
        background-color: #E0E0E0;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 5px;
    }
    
    /* 買入綠色 #00A600 (用於顯示) */
    .money-buy { color: #00A600 !important; font-weight: bold; }
    
    /* 賣出紅色 #CE0000 (用於顯示) */
    .money-sell { color: #CE0000 !important; font-weight: bold; }

    /* 表格樣式微調 */
    div[data-testid="stDataFrame"] {
        background-color: white; /* 表格本身保持亮色以便閱讀 */
        border-radius: 5px;
        padding: 5px;
    }
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
# 3. 股票搜尋區 (第一列)
# ---------------------------------------------------------
col_input, col_info = st.columns([1, 2])

with col_input:
    # 使用 Form 避免每次打字都刷新，直到按 Enter
    with st.form("stock_search"):
        stock_input = st.text_input("輸入代號 (按 Enter):", placeholder="例如: 0050")
        search_submitted = st.form_submit_button("搜尋 / 更改股票")

if search_submitted and stock_input:
    stock_id = stock_input.strip()
    ticker_name = f"{stock_id}.TW"
    
    # 嘗試抓取名稱 (包含常見 ETF 手動對應，因為 API 容易抓到英文)
    # 這裡做一個簡單的 Mapping 範例，實際可依 API 回傳為主
    manual_map = {
        "0050": "元大台灣50",
        "0056": "元大高股息",
        "2330": "台積電",
        "2317": "鴻海"
    }
    
    stock_name_display = manual_map.get(stock_id, None)
    
    if not stock_name_display:
        try:
            info = yf.Ticker(ticker_name).info
            # 優先找 longName，若無則用 shortName
            stock_name_display = info.get('longName', info.get('shortName', stock_id))
        except:
            stock_name_display = "未知股票"

    st.session_state.current_stock_name = stock_name_display
    st.session_state.current_stock_id = stock_id

# 顯示第一列標題
st.markdown(f'<div class="stock-header">{st.session_state.current_stock_id} {st.session_state.current_stock_name}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 資料輸入區 (第二、三列)
# ---------------------------------------------------------
TRANS_TYPES = ["定期定額", "定期定額加碼", "個股", "賣出"]

# 表單開始
with st.form("entry_form", clear_on_submit=True):
    
    # 第二列: 分類選擇
    st.markdown('<div class="category-header">定期定額 | 定期定額加碼 | 個股 | 賣出</div>', unsafe_allow_html=True)
    selected_type = st.selectbox("選擇交易類型", TRANS_TYPES, label_visibility="collapsed")
    
    st.markdown("---")
    
    # 第三列: 輸入欄位 (使用 columns 排版避免擋住)
    # 為了手機版面友善，我們分成兩行顯示輸入欄
    
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        input_date = st.date_input("1. 時間", datetime.today())
        price_in = st.number_input("2. 購入股價", min_value=0.0, step=0.1, format="%.2f")
    with row1_c2:
        shares_in = st.number_input("3. 購入股數", min_value=0, step=1)
        # 賣出相關
        price_out = st.number_input("4. 賣出股價", min_value=0.0, step=0.1, format="%.2f")

    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        shares_out = st.number_input("5. 賣出股數", min_value=0, step=1)
        avg_price = st.number_input("6. 現股均價 (僅賣出填)", min_value=0.0, step=0.1, format="%.2f")
    with row2_c2:
        # 成交價與流向
        total_amount = st.number_input("7. 成交價 (含手續費)", min_value=0.0, step=1.0, format="%.2f")
        trade_mode = st.radio("資金流向", ["買入 (-)", "賣出 (+)"], horizontal=True)

    # 提交按鈕
    submitted = st.form_submit_button("確認輸入 (Enter)")

    if submitted:
        # 邏輯: 根據選擇決定正負號
        is_buy = trade_mode == "買入 (-)"
        final_amount = -abs(total_amount) if is_buy else abs(total_amount)
        
        new_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"), # 唯一碼
            "delete": False, # 刪除勾選框
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
        # 排序
        st.session_state.data.sort(key=lambda x: x['date'])
        st.success("已暫存，請按下方按鈕更新表格")

# ---------------------------------------------------------
# 5. 功能按鈕
# ---------------------------------------------------------
c_btn1, c_btn2 = st.columns(2)
with c_btn1:
    if st.button("生成表格 (建立新表)"):
        st.session_state.data = []
        st.rerun()
with c_btn2:
    if st.button("輸入至同一表格 (更新)"):
        st.rerun()

# ---------------------------------------------------------
# 6. 表格顯示與編輯 (含刪除邏輯)
# ---------------------------------------------------------
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    st.markdown("### 交易明細")
    st.info("💡 編輯數值後點擊表格外任意處即可儲存。若要刪除，請勾選「刪除」欄位後，點擊下方的紅色按鈕確認。")

    # 設定顯示格式
    column_config = {
        "delete": st.column_config.CheckboxColumn("刪除?", help="勾選後按下方按鈕刪除", default=False),
        "date": "時間",
        "type": "分類",
        "buy_price": st.column_config.NumberColumn("購入股價", format="$%.2f"),
        "buy_shares": st.column_config.NumberColumn("購入股數"),
        "sell_price": st.column_config.NumberColumn("賣出股價", format="$%.2f"),
        "sell_shares": st.column_config.NumberColumn("賣出股數"),
        "avg_price": st.column_config.NumberColumn("現股均價", format="$%.2f"),
        "total_amount": st.column_config.NumberColumn("成交價(含費)", format="$%.2f"),
        "id": None # 隱藏 ID
    }

    # 顯示可編輯表格
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        disabled=["id"], # ID 不可編輯
        key="main_editor"
    )

    # 刪除邏輯處理按鈕
    # Streamlit 無法雙擊刪除，必須透過勾選+按鈕確認
    rows_to_delete = edited_df[edited_df.delete == True]
    
    if not rows_to_delete.empty:
        st.warning("⚠️ 您勾選了刪除資料，確定要刪除嗎？")
        col_conf_1, col_conf_2 = st.columns([1,4])
        with col_conf_1:
            if st.button("是 (刪除)", type="primary"):
                # 保留未被勾選的資料
                new_data = edited_df[edited_df.delete == False].drop(columns=['delete'], errors='ignore')
                # 補回 delete 欄位預設值以便下次邏輯
                new_data_records = new_data.to_dict('records')
                for d in new_data_records:
                    d['delete'] = False
                
                st.session_state.data = new_data_records
                st.rerun()
        with col_conf_2:
            if st.button("否 (取消)"):
                st.rerun() # 刷新取消勾選狀態 (需使用者手動取消或直接刷新)
    else:
        # 若沒有刪除操作，將編輯後的資料同步回 session (即時存檔)
        # 排除 delete 欄位避免髒資料累積，但在 session 中需要它嗎？
        # 為了保持狀態，我們把 edited_df 轉回 dict
        st.session_state.data = edited_df.to_dict('records')

    # ---------------------------------------------------------
    # 7. 總計表格
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### 總計表格")

    # 重新整理資料用於計算
    calc_df = pd.DataFrame(st.session_state.data)

    if not calc_df.empty:
        # 分類篩選
        reg_df = calc_df[calc_df['type'] == "定期定額"]
        bonus_df = calc_df[calc_df['type'] == "定期定額加碼"]
        sell_df = calc_df[calc_df['type'] == "賣出"]

        # 計算項目
        # 1. 定期定額總價 (取絕對值顯示)
        reg_total_price = abs(reg_df['total_amount'].sum())
        # 2. 定期定額股數
        reg_total_shares = reg_df['buy_shares'].sum()
        
        # 3. 加碼總價 (取絕對值顯示)
        bonus_total_price = abs(bonus_df['total_amount'].sum())
        # 4. 加碼股數
        bonus_total_shares = bonus_df['buy_shares'].sum()
        
        # 5. 買入總額 (定期 + 加碼)
        buy_total_amt = reg_total_price + bonus_total_price
        # 6. 買入總股數
        buy_total_shares = reg_total_shares + bonus_total_shares
        
        # 7. 賣出總額 (正數加總)
        sell_total_amt = sell_df['total_amount'].sum()
        # 8. 賣出總股數
        sell_total_shares = sell_df['sell_shares'].sum()
        
        # 9. 成本: 現股均價 * 賣出股數
        cost = (sell_df['avg_price'] * sell_df['sell_shares']).sum()
        
        # 10. 獲利: 賣出總額 - 買入總額
        profit = sell_total_amt - buy_total_amt

        # 建立 DataFrame
        summary_data = {
            "股票編號": [st.session_state.current_stock_id],
            "定期定額總價": [reg_total_price],
            "定期定額股數": [reg_total_shares],
            "加碼總價": [bonus_total_price],
            "加碼股數": [bonus_total_shares],
            "買入總額": [buy_total_amt],
            "買入總股數": [buy_total_shares],
            "賣出總額": [sell_total_amt],
            "總賣出股數": [sell_total_shares], # 修正欄位名稱
            "成本": [cost],
            "獲利": [profit]
        }
        
        summary_df = pd.DataFrame(summary_data)

        # 樣式設定
        def highlight_summary(row):
            styles = [''] * len(row)
            
            # 定義樣式
            green_style = 'color: #00A600; font-weight: bold;'
            red_style = 'color: #CE0000; font-weight: bold;'
            
            # 欄位索引 (0-based)
            # 1: 定期定額總價 (綠)
            styles[1] = green_style
            # 3: 加碼總價 (綠)
            styles[3] = green_style
            # 5: 買入總額 (綠)
            styles[5] = green_style
            # 7: 賣出總額 (紅)
            styles[7] = red_style
            
            # 10: 獲利 (正紅/負綠)
            profit_val = row[10]
            if profit_val > 0:
                styles[10] = red_style
            else:
                styles[10] = green_style
                
            return styles

        # 顯示
        st.dataframe(
            summary_df.style.apply(highlight_summary, axis=1).format("{:.2f}", subset=[
                "定期定額總價", "加碼總價", "買入總額", "賣出總額", "成本", "獲利"
            ]),
            hide_index=True,
            use_container_width=True
        )
部署說明
requirements.txt: 內容不變（streamlit, pandas, yfinance）。
上傳: 將此新程式碼複製到 app.py 並推送到 GitHub。
Streamlit Cloud: 建議先點擊 App 右下角的 "Manage app" -> "Reboot" 以確保它讀取到最新的 CSS 設定。
功能備註
輸入字體顏色: 我加入了 .stTextInput input { color: #FFFFFF !important; }，這會強制輸入框內的文字變成白色。
手機操作: 由於手機鍵盤彈出時會擠壓畫面，Streamlit 的 st.columns 已經盡量讓輸入框並排。建議輸入完畢後按一下鍵盤上的「完成」或收起鍵盤，再按「確認輸入」。
刪除資料: 請在表格左側（或第一欄）勾選 ☑️，下方會出現紅色的「是 (刪除)」按鈕，點擊後即可刪除。這是手機上最不易誤觸的作法。
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
這是一個依照您提供的圖片樣式與詳細需求完全客製化的 Streamlit App。
我針對以下幾點做了特別優化：
視覺還原: 依照圖片，將標題區塊設為藍色 (#66B3FF)、分類區塊設為灰色 (#E0E0E0)，並將背景統一為深藍色 (#003060)。
表格結構: 雖然 Streamlit 的編輯器 (data_editor) 本質上是單一表格，但我透過Column Config (欄位設定) 將欄位清楚標示，並依照時間排序，讓手機版面不會因強制分割左右兩欄而變得太窄難以閱讀。
輸入優化: 修正了深色背景下輸入框文字看不見的問題，設定輸入文字為白色。
刪除功能: 由於網頁版無法偵測「雙擊」，改為最穩定的「勾選刪除」模式，並加上防呆視窗。
1. app.py (主程式碼)
code
Python
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
        st.error("⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
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
2. requirements.txt (無變更)
code
Text
streamlit
pandas
yfinance
操作說明與設計理念：
介面樣式：
我使用 HTML/CSS 模擬了您圖片中的標題樣式。上方顯示藍底標題，下方顯示灰底分類。
背景色修正為 #003060。
輸入框內的文字修正為白色，解決了深色背景看不見輸入內容的問題。
表格設計 (重要)：
圖片中的表格是 Excel 的左右分割排版（定期定額在左、加碼在右）。
在 App (特別是手機版) 若採用這種左右分割，畫面會變得很窄且難以閱讀。
因此，我採用了標準交易紀錄模式（統一為一個表格，以時間排序）。這是 App 設計的最佳實踐，同時透過 column_config 讓您可以直接在表格上點擊編輯。
刪除資料：
由於網頁技術限制，無法直接做到「雙擊某格跳出視窗」。
我改用最直覺的 Checkbox (勾選) 方式。表格最左邊有「刪除?」欄位，勾選後下方會出現紅色的「是」按鈕，點擊即可刪除。
總計邏輯：
獲利顏色：依照您的指示，獲利 > 0 顯示紅色 (#CE0000)，獲利 < 0 顯示綠色 (#00A600)。
買入顯示：成交價為負數時 (買入)，表格內會自動顯示負號，總計表格會顯示綠色。
請依照之前的步驟更新 GitHub 上的 app.py 即可。
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
這是一個 Python 語法錯誤 (SyntaxError)。
原因：
請仔細看您的錯誤截圖，錯誤訊息指出的那一行程式碼：
st.error(⚠️ 您勾選了刪除...
在 Python 中，任何文字訊息（字串）都必須被引號 "" 或 '' 包起來。
截圖顯示您的程式碼中，st.error 括號內的文字缺少了開頭的引號，導致 Python 把 ⚠️ 這個符號當作程式指令執行，但因為它看不懂這個符號，所以報錯 invalid character。
如何修正？
請找到 app.py 中的第 264 行左右（依照您的檔案長度可能不同），找到 st.error 那一行。
❌ 錯誤的寫法 (您目前的狀態)：
code
Python
st.error(⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
# 注意：前面少了引號，或者引號位置不對
✅ 正確的寫法：
code
Python
st.error("⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
# 注意：文字的前後都要有雙引號 " "
為了避免還有其他類似的複製貼上錯誤，我將這一段完整的邏輯再次提供給您，您可以直接複製整段覆蓋掉原本 if not rows_to_delete.empty: 下方的程式碼：
code
Python
# 刪除防呆邏輯
    rows_to_delete = edited_df[edited_df.delete == True]
    if not rows_to_delete.empty:
        # 請確保下面這一行有雙引號
        st.error("⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
        
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
修改完後存檔，回到 Streamlit Cloud 點擊 Reboot 即可恢復正常。
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
這是一個根據您最新的圖片標示與詳細要求進行修正的版本。
修改重點：
搜尋欄位: 移除提示文字，保留搜尋按鈕。
版面簡化: 刪除了輸入區塊上方的藍色股票名稱顯示 (Point 2)。
輸入框優化: 透過 CSS 隱藏了數字輸入框右側的 + 與 - 按鈕 (Point 3)。
按鈕樣式: 所有功能按鈕（生成、刷新、刪除確認）的底色改為黑色，文字白色 (Point 4 & 6)。
表格樣式 (Point 5):
移除了表格外圍粗厚的白邊。
視覺整合: 將「股票名稱 (藍底)」直接做在表格的最上方，緊接著「欄位標題 (灰底)」，最後是「數據 (無背景)」，完全還原 Excel 截圖的視覺層級。
表格欄位標題背景設為灰色 #E0E0E0，文字黑色。
app.py 完整程式碼
code
Python
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

    /* --- Point 3: 隱藏數字輸入框的 +/- 按鈕 --- */
    div[data-testid="stNumberInput"] button {
        display: none;
    }

    /* --- 輸入框樣式優化 --- */
    /* 輸入框背景半透明黑，文字白色 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        color: #FFFFFF !important; 
        background-color: rgba(0, 0, 0, 0.3) !important; /* 改為深色半透明 */
        border: 1px solid #FFFFFF !important;
    }
    /* 下拉選單選項 */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #003060;
        color: white;
    }

    /* --- Point 4 & 6: 按鈕樣式 (黑色底，白色字) --- */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        font-weight: bold;
        border-radius: 5px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #333333 !important; /* 滑鼠懸停稍微變灰 */
        border-color: #66B3FF !important;
    }
    /* 針對 Primary 按鈕 (如刪除確認) 也統一設為黑底 */
    div.stButton > button[kind="primary"] {
        background-color: #000000 !important;
        color: #CE0000 !important; /* 刪除確認字體用紅色警示 */
        border: 1px solid #CE0000 !important;
    }

    /* --- Point 5: 表格樣式還原 --- */
    
    /* 1. 第一列: 股票全名 (藍色背景) - 自定義 HTML 類別 */
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
        margin-bottom: 0px; /* 貼合下方表格 */
    }

    /* 2. Streamlit 表格容器調整 */
    div[data-testid="stDataFrame"] {
        background-color: transparent !important;
        padding: 0px !important;
    }
    
    /* 3. 強制修改表格 Header (灰色背景 #E0E0E0, 黑色文字) */
    div[data-testid="stDataFrame"] table thead tr th {
        background-color: #E0E0E0 !important;
        color: #000000 !important;
        font-size: 14px !important;
        border-bottom: 1px solid #000 !important;
    }
    
    /* 4. 表格內容 (白色背景, 黑色文字) */
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
    st.session_state.current_stock_name = "尚未選擇股票"
if 'current_stock_id' not in st.session_state:
    st.session_state.current_stock_id = ""

# ---------------------------------------------------------
# 3. 股票搜尋區 (Point 1: 移除提示文字)
# ---------------------------------------------------------
col_search, col_space = st.columns([1, 2])

with col_search:
    with st.form("stock_search"):
        # Point 1: 移除 "按 Enter" 提示，僅留 "輸入代號"
        stock_input = st.text_input("輸入代號", placeholder="0050")
        search_submitted = st.form_submit_button("搜尋")

if search_submitted and stock_input:
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
    
    stock_name_display = manual_map.get(stock_id, None)
    
    if not stock_name_display:
        try:
            info = yf.Ticker(ticker_name).info
            stock_name_display = info.get('longName', info.get('shortName', stock_id))
        except:
            stock_name_display = "未知股票"

    st.session_state.current_stock_name = stock_name_display
    st.session_state.current_stock_id = stock_id

# Point 2: 已刪除此處原本顯示的大型藍色股票名稱區塊

# ---------------------------------------------------------
# 4. 資料輸入區 (Point 3: +/- 按鈕已隱藏)
# ---------------------------------------------------------
TRANS_TYPES = ["定期定額", "定期定額加碼", "個股", "賣出"]

# 移除原本的灰色標題列，保持介面簡潔，直接顯示輸入表單
with st.form("entry_form", clear_on_submit=True):
    
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_type = st.selectbox("交易類型", TRANS_TYPES)
    with c2:
        input_date = st.date_input("時間", datetime.today())
    with c3:
        # Point 3: CSS 已隱藏 +/- 按鈕
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
# 5. 表格生成與操作按鈕 (Point 4: 黑色按鈕)
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
# 6. 表格顯示區 (Point 5: Excel 樣式還原)
# ---------------------------------------------------------
if st.session_state.data:
    st.markdown("<br>", unsafe_allow_html=True) # 增加一點間距
    
    # 準備資料
    df = pd.DataFrame(st.session_state.data)
    df['date'] = pd.to_datetime(df['date']).dt.date

    # 顯示第一列 (Point 5 - 水藍色: 該股代號及全名)
    # 使用 Markdown HTML 來模擬表格的 Header，讓它跟下方的表格看起來是一體的
    header_text = f"{st.session_state.current_stock_id} {st.session_state.current_stock_name}" if st.session_state.current_stock_id else "尚未輸入代號"
    st.markdown(f'<div class="table-stock-header">{header_text}</div>', unsafe_allow_html=True)

    # 設定顯示格式
    # 這裡的標題會變成 "表格第二列 (灰色背景)" (透過 CSS 控制)
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

    # 顯示表格 (第三列資料: 無背景/白色)
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        disabled=["id"],
        key="editor"
    )

    # 刪除功能 (Point 6: 按鈕為黑色)
    rows_to_delete = edited_df[edited_df.delete == True]
    if not rows_to_delete.empty:
        # 修正之前的引號錯誤
        st.error("⚠️ 您勾選了刪除，確定要移除這些資料嗎？")
        c_del_1, c_del_2 = st.columns([1, 6])
        with c_del_1:
            if st.button("是", type="primary"): # CSS 已將 primary 設為黑底紅字
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
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
這是一個符合您需求修改後的版本。
修改重點：
移除搜尋按鈕與表單：原本的 st.form 機制需要按鈕觸發，現在改為直接使用 st.text_input。在 Streamlit 中，輸入框按下 Enter 鍵後會自動刷新頁面，正好符合您的需求。
新增第二個欄位：在代號欄位右側新增了「股票全名」欄位。
自動填入：當左側輸入代號並按下 Enter，程式會自動抓取名稱並填入右側欄位。右側欄位設定為 disabled=True (唯讀)，讓使用者知道這是自動產生的結果，但字體顏色我有特別調整為白色以利閱讀。
提示文字：輸入框內的提示文字 (Placeholder) 已更改為「例如:0050，輸入完畢後請按enter」。
請使用以下完整的 app.py 程式碼：
code
Python
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
56.7s
warning
Turn Drive on for future conversations

Your work is currently not being saved and will be lost, we recommend enabling Google Drive, you will always have the option to turn on Temporary chat for conversations you do not want to save to your chat history.
Use Arrow Up and Arrow Down to select a turn, Enter to jump to it, and Escape to return to the chat.
Start typing a prompt

Run
Ctrl
Response ready.
