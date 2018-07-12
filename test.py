import pandas as pd

from cfg import data_root

save_file = "soybean_price.csv"
save_file_path = data_root + save_file

#初始化数据存储数组
soybean_price_columns = ["product", "date", "market", "price", "unit"]

# 给数据添加表头
soybean_price_df = pd.read_csv(save_file_path, header=0)
soybean_price_df.columns = soybean_price_columns

soybean_price_df["date"] = pd.to_datetime(soybean_price_df["date"], format="%Y-%m-%d" )

print(soybean_price_df.info())
soybean_price_df.sort_values("date", inplace=True, ascending=True)

# 重新将数据写入csv文件
soybean_price_df.to_csv(save_file_path, index = False)