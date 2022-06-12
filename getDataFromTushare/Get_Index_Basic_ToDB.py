'''
Created on 2021年7月17日

@author: 无相大师

指数基本信息
接口：index_basic，可以通过数据工具调试和查看数据。
描述：获取指数基础信息。

输入参数

名称	类型	必选	描述
ts_code	str	N	指数代码
name	str	N	指数简称
market	str	N	交易所或服务商(默认SSE)
publisher	str	N	发布商
category	str	N	指数类别
输出参数

名称	类型	描述
ts_code	str	TS代码
name	str	简称
fullname	str	指数全称
market	str	市场
publisher	str	发布方
index_type	str	指数风格
category	str	指数类别
base_date	str	基期
base_point	float	基点
list_date	str	发布日期
weight_rule	str	加权方式
desc	str	描述
exp_date	str	终止日期
市场说明(market)

市场代码	说明
MSCI	MSCI指数
CSI	中证指数
SSE	上交所指数
SZSE	深交所指数
CICC	中金指数
SW	申万指数
OTH	其他指数
指数列表

主题指数
规模指数
策略指数
风格指数
综合指数
成长指数
价值指数
有色指数
化工指数
能源指数
其他指数
外汇指数
基金指数
商品指数
债券指数
行业指数
贵金属指数
农副产品指数
软商品指数
油脂油料指数
非金属建材指数
煤焦钢矿指数
谷物指数
接口使用


pro = ts.pro_api()

df = pro.index_basic(market='SW')
数据样例

       ts_code    name              market     publisher   category     base_date  base_point  \
5    801010.SI    农林牧渔             SW      申万   一级行业指数  19991230      1000.0
6    801011.SI    林业Ⅱ               SW     申万  二级行业指数  19991230      1000.0
7    801012.SI    农产品加工           SW      申万   二级行业指数  19991230      1000.0
8    801013.SI    农业综合Ⅱ           SW      申万  二级行业指数  19991230      1000.0
9    801014.SI    饲料Ⅱ               SW     申万  二级行业指数  19991230      1000.0
10   801015.SI    渔业                 SW      申万   二级行业指数  19991230      1000.0
11   801016.SI    种植业               SW      申万   二级行业指数  19991230      1000.0
12   801017.SI    畜禽养殖Ⅱ           SW      申万  二级行业指数  20111010      1000.0
13   801018.SI    动物保健Ⅱ           SW      申万研  二级行业指数  19991230      1000.0
14   801020.SI    采掘                 SW      申万   一级行业指数  19991230      1000.0
15   801021.SI    煤炭开采Ⅱ           SW      申万  二级行业指数  19991230      1000.0
16   801022.SI    其他采掘Ⅱ           SW      申万  二级行业指数  19991230      1000.0
17   801023.SI    石油开采Ⅱ           SW      申万  二级行业指数  19991230      1000.0
18   801024.SI    采掘服务Ⅱ           SW      申万  二级行业指数  19991230      1000.0
'''
import time

from retry import retry
from sqlalchemy.types import NVARCHAR, DATE, Integer, DECIMAL
from basis.Init_Env import init_db, init_ts_pro, init_currentDate
from basis.Tools import get_and_write_data_by_limit, drop_Table

rows_limit = 8000  # 该接口限制每次调用，最大获取数据量
times_limit = 1000000  # 该接口限制,每分钟最多调用次数
sleeptime = 61
currentDate = init_currentDate()
prefix = 'hq_index_basic'


def write_db(df, db_engine):
    res = df.to_sql(prefix, db_engine, index=False, if_exists='append', chunksize=10000,
                    dtype={'ts_code': NVARCHAR(20),
                           'name': NVARCHAR(250),
                           'market': NVARCHAR(20),
                           'publisher': NVARCHAR(250),
                           'category': NVARCHAR(50),
                           'base_date': DATE,
                           'base_point': DECIMAL(17, 2),
                           'list_date': DATE})
    return res


@retry(tries=2, delay=61)
def get_data(ts_pro, rows_limit, offset):
    df = ts_pro.index_basic(limit=rows_limit, offset=offset)
    return df


def get_index_basic(db_engine, ts_pro):
    drop_Table(db_engine, prefix)
    get_and_write_data_by_limit(prefix, db_engine, ts_pro,
                                get_data, write_db, rows_limit, times_limit, sleeptime)


if __name__ == '__main__':
    ts_pro = init_ts_pro()
    db_engine = init_db()

    get_index_basic(db_engine, ts_pro)

    print('数据日期：', currentDate)
    end_str = input("加载完毕，请复核是否正确执行！")
