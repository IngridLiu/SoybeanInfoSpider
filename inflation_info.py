# 2014-2016 info from http://databank.worldbank.org/data/reports.aspx?source=2&series=FP.CPI.TOTL.ZG
# 2017 info from

import pandas as pd

from cfg import data_root

inflation_info = [["2014", "2.0"], ["2015", "1.4"], ["2016", "2.0"], ["2017", "1.6"]]
inflation_info_df = pd.DataFrame(inflation_info, columns= ["year", "infaltion"])

save_file = "inflation_info.csv"
save_file_path = data_root + save_file
inflation_info_df.to_csv(save_file_path, index=False)

