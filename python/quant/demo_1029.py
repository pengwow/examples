import baostock as bs
import pandas as pd

lg = bs.login()
# 日线（前复权）
rs_day = bs.query_history_k_data_plus(
    "sh.600519", "date,open,high,low,close,volume,amount",
    start_date="2024-01-01", end_date="2024-12-31", frequency="d", adjustflag="3"
)
df_day = pd.DataFrame(rs_day.get_data(), columns=rs_day.fields)

# 5分钟线（前复权）
rs_min = bs.query_history_k_data_plus(
    "sh.600519", "date,time,open,high,low,close,volume",
    start_date="2024-01-01", end_date="2024-12-31", frequency="5", adjustflag="2"
)
df_min = pd.DataFrame(rs_min.get_data(), columns=rs_min.fields)

# 打印结果
print(df_day)
print(df_min)

bs.logout()