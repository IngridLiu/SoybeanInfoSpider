

import pandas as pd

from time import sleep
from selenium import webdriver
from datetime import datetime
from dateutil.relativedelta import relativedelta

from cfg import chromedriver_path, data_root

from urllib.request import urlopen
from bs4 import BeautifulSoup


def exchage_rate_spider(url):

    print("start to crawl " + url )

    # 使用selenium模拟获取数据的流程，找到抓取数据的页面
    driver = webdriver.Chrome(chromedriver_path)
    driver.implicitly_wait(10)
    driver.get(url)
    elem = driver.find_element_by_id("widgetFieldDateRange")
    elem.click()

    elem_start_date = driver.find_element_by_id("startDate")
    elem_start_date.clear()
    elem_start_date.send_keys("2014/01/01")

    elem_end_date = driver.find_element_by_id("endDate")
    elem_end_date.clear()
    elem_end_date.send_keys(datetime.now().strftime("%Y/%m/%d"))

    elem_in = driver.find_element_by_id("applyBtn")
    elem_in.click()

    #data_table = driver.find_element_by_id("results_box")
    data_table = driver.find_element_by_id("curr_table")
    data_lines = data_table.text.split("\n")
    exchange_rate = []
    for data_line in data_lines:
        data_items = data_line.split(" ")
        data = []
        for i in range(len(data_items)-1):
            data.append(data_items[i])
        exchange_rate.append(data)

    return exchange_rate

def rate_list2df(exchange_rate):

    exchange_rate_header = ["date", "opening", "closing", "top", "low"]
    exchange_rate = exchange_rate[1:]

    exchange_rate_df = pd.DataFrame(exchange_rate)
    exchange_rate_df.columns = exchange_rate_header

    # exchange_rate_df.drop(columns = "percentage", axis=1)

    return exchange_rate_df


def change_date_form(exchange_rate_df):

    date_list = []
    for date in exchange_rate_df["date"]:
        date_list.append(date.strip("日").replace("年","-").replace("月", "-"))
    exchange_rate_df["date"] = date_list
    exchange_rate_df["date"] = pd.to_datetime(exchange_rate_df["date"])
    exchange_rate_df["date"] = [datetime.strftime(x,'%Y-%m-%d') for x in exchange_rate_df["date"]]
    exchange_rate_df.sort_values(by="date", inplace=True, ascending=True)

    exchange_rate_df.set_index(["date"], inplace=True)

    return exchange_rate_df


# 获取待爬取数据的时间区间的全部月份
def get_dur_months():
    start_date = datetime.strptime("2014-01-01", "%Y-%m-%d").date()
    end_date = datetime.now().date()

    dur_month = []
    some_date = start_date
    while some_date <= end_date:
        some_month = datetime.strftime(some_date, "%Y-%m-%d")[0:7]
        if some_month not in dur_month:
            dur_month.append(some_month)
        some_date = some_date + relativedelta(months=+1)
    return dur_month

# 获取待爬取数据的时间区间的全部日期
def get_dur_dates():
    start_date = datetime.strptime("2014-01-01", "%Y-%m-%d").date()
    end_date = datetime.now().date()

    dur_dates = []
    some_date = start_date
    while some_date <= end_date:
        dur_dates.append(datetime.strftime(some_date, "%Y-%m-%d"))
        some_date = some_date + relativedelta(days=+1)

    return dur_dates

# list求均值
def list_avg(list):
    total = 0
    for item in list:
        total = float(item) + float(total)
    if len(list) > 0:
        avg = total / len(list)
    else:
        avg = 0

    return round(avg, 4)


# 获取每月的平均开盘价，收盘价，最高价，最低价，变化百分比
def month_avg_rate(exchange_rate_df):

    dur_month = get_dur_months()

    month_avg = []
    for month in dur_month:
        month_opening_list = []
        month_closing_list = []
        month_top_list = []
        month_low_list = []

        for row in exchange_rate_df.iterrows():
            date = row [0]
            day_opening = row[1][0]
            day_closing = row[1][1]
            day_top = row[1][2]
            day_low = row[1][3]

            if str(date)[0:7] == month:
                month_opening_list.append(float(day_opening))
                month_closing_list.append(float(day_closing))
                month_top_list.append(float(day_top))
                month_low_list.append(float(day_low))


        month_opening = list_avg(month_opening_list)
        month_closing = list_avg(month_closing_list)
        month_top = list_avg(month_top_list)
        month_low = list_avg(month_low_list)
        month_avg.append([month, month_opening, month_closing, month_top, month_low])

    month_avg_df = pd.DataFrame(month_avg, columns=["date","opening", "closing", "top", "low"])
    month_avg_df.set_index(["date"], inplace=True)

    return month_avg_df

# 将爬取到的数据中空缺的日期补齐，值为该月的平均值
def add_null_date(exchange_rate_df, month_avg_df):
    print("start to add the null data of dataframe")

    dur_dates = get_dur_dates()

    add_exchange_rate = []
    for date in dur_dates:
        if date not in exchange_rate_df.index.tolist():
            month = str(date)[0:7]
            add_line = [ date ]
            for i in range(0, len(month_avg_df.loc[month])):
                add_line.append(round(month_avg_df.ix[[month], [i]].values[0, 0], 4))
            add_exchange_rate.append(add_line)

    add_exchange_rate_df = pd.DataFrame(add_exchange_rate, columns=["date", "opening", "closing", "top", "low"])
    add_exchange_rate_df["date"] = pd.to_datetime(add_exchange_rate_df["date"])
    add_exchange_rate_df.set_index(["date"], inplace=True)

    added_exchange_rate_df = pd.concat([add_exchange_rate_df, exchange_rate_df], axis=0)
    added_exchange_rate_df.index = pd.DatetimeIndex(added_exchange_rate_df.index)
    added_exchange_rate_df.sort_index(axis=0)

    return added_exchange_rate_df




if __name__ == "__main__":

    """
    数据来源：

    url 美元对人民币：https://cn.investing.com/currencies/usd-cny-historical-data

    url 巴西雷亚尔对人民币：https://cn.investing.com/currencies/brl-cny-historical-data

    url 阿根廷比索对人民币：https://cn.investing.com/currencies/ars-cny-historical-data

    url 俄罗斯卢布 人民币：https://cn.investing.com/currencies/rub-cny-historical-data

    """

    currencis = ["usd", "brl", "ars", "rub"]

    exchange_df = pd.DataFrame(columns=["opening", "closing", "top", "low", "currency"])

    for currency in currencis:

        print("crawl the exchange rate between {} and cny".format(currency))


        url = "https://cn.investing.com/currencies/{}-cny-historical-data".format(currency)

        exchange_rate = exchage_rate_spider(url)
        exchange_rate_df = rate_list2df(exchange_rate)
        exchange_rate_df = change_date_form(exchange_rate_df)

        month_avg_df = month_avg_rate(exchange_rate_df)
        exchange_rate_df = add_null_date(exchange_rate_df, month_avg_df)
        exchange_rate_df["currency"] = currency
        print("preprocess data of {} successfully.".format(currency))

        exchange_rate_df.index = pd.DatetimeIndex(exchange_rate_df.index)
        exchange_rate_df.sort_index( axis=0 )

        exchange_df = pd.concat([exchange_df, exchange_rate_df], axis=0)

    save_file = "cny_exchange_rate.csv"
    save_path = data_root + save_file

    exchange_df.to_csv(save_path, mode = 'a',index=True)


