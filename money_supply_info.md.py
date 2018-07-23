
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup

from cfg import data_root


# 获取某年某月的全部的天数
def dates_in_month(month):
    """
        获取日期列表
        :param start: 开始日期
        :param end: 结束日期
        :return: dates list
        """
    dates_of_month = []

    start_date = datetime.strptime(month + "-01", "%Y-%m-%d")
    end_date = start_date + relativedelta(months=+1)

    days_count = (end_date - start_date).days

    for i in range(days_count):
        some_date = start_date + relativedelta( days = +i)
        dates_of_month.append(some_date)

    return dates_of_month

def date_test(month):
    date = datetime.strptime(month + "-01", "%Y-%m-%d")
    date_threshold = datetime.strptime("2014-01-01", "%Y-%m-%d")

    if date >= date_threshold :
        return True
    else:
        return False



def money_supply_spider(url):
    print("start to crawl the url: %s" % url)

    money_supply = []

    html = urlopen(url)
    page_obj = BeautifulSoup(html)

    data_table = page_obj.find_all("table", id="tb")[0]

    data_lines = []
    for tr in data_table.findAll('tr'):
        data_line = []
        for i, td in enumerate(tr.findAll('td')):
            add_index = [0, 1, 4, 7]
            if i in add_index:
                if i == 0:
                    date = td.text.strip("[*| |\r|\n]").strip("月份").replace("年", "-")
                    data_line.append(date)
                else:
                    data_line.append(td.text.strip("[*| |\r|\n]"))
        data_line.append("亿元")
        data_lines.append(data_line)

    del data_lines[0:2]
    del data_lines[-1]

    return data_lines


# 将某月的数据对应到该月的每一天
def get_month_data(money_supply_page):
    print("start to get the date data of some month.")

    data_page = []
    for data_line in money_supply_page:
        month = data_line[0]
        if date_test(month):
            pass
        else:
            break
        dates_of_month = dates_in_month(month)

        for date in dates_of_month:
            data_date = []
            for i, item in enumerate(data_line) :
                if i == 0:
                    data_date.append(str(date).split(" ")[0])
                else:
                    data_date.append(item)

            data_page.append(data_date)

    return data_page


if __name__ == "__main__":

    max_page = 3
    base_url = "http://data.eastmoney.com/cjsj/moneysupply.aspx?p="

    '''
    M2：货币和准货币
    M1：货币
    M0：流通中的现金
    '''
    data_columns = ["date", "M2", "M1", "M0", "unit"]
    data_date_total = []

    for page in range(max_page):
        url = base_url + str(page + 1)

        money_supply_page = money_supply_spider(url)
        data_date_page = get_month_data(money_supply_page)

        data_date_total = data_date_total + data_date_page

    # 将list转换为dataframe
    data_date_total_df = pd.DataFrame(data_date_total)
    data_date_total_df.columns = data_columns
    # 将数据按date升序排列
    data_date_total_df["date"] = pd.to_datetime(data_date_total_df["date"], format="%Y-%m-%d")
    data_date_total_df.sort_values(by="date", inplace=True, ascending=True)

    data_date_total_df.set_index(["date"], inplace=True)

    # 保存数据到csv文件
    save_file = "money_supply_info.csv"
    save_path = data_root + save_file

    data_date_total_df.to_csv(save_path, index=True)
