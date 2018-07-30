import pandas as pd

from cfg import data_root

urbanization_info = [["2014", 136782, 74916, 61866, "万人", 0.5477],
                  ["2015", 137462, 77116, 60346, "万人", 0.5610],
                  ["2016", 138271, 79298, 58973, "万人", 0.5735],
                  ["2017", 139008, 81347, 57661, "万人", 0.5852]]
urbanization_info_df = pd.DataFrame(urbanization_info, columns= ["年份", "年末人口", "城镇人口", "乡村人口", "万人", "城镇人口占总人口比例"])

save_file = "urbanization_info.csv"
save_file_path = data_root + save_file
urbanization_info_df.to_csv(save_file_path, index=False)