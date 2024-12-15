from flask import Flask, request
import pymysql
import pandas as pd 

app = Flask(__name__)
@app.route('/basket-info', methods=['POST'])

def student_query() : 
    request_json = request.get_json()
    user_input = request_json['user_id']
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='0000', db='baemin')

    sql_info = """
    select s.store_name, b.delivery_method, group_concat(' ', m.menu_name) menu_name,
       group_concat(' ', m.price) price, group_concat(' ', ifnull(bi.menu_option, '옵션 없음')) menu_option,
       concat(max(timestampdiff(minute, b.order_time, b.expect_time)), '분') expected_time,
       group_concat(' ', bi.amount) amount, group_concat(' ', mp.picture_url) url,
       max(b.delivery_tip) delivery_tip, max(b.total_amount) total_menu_price, max(b.estimated_total) total_price
    from Basket b
    join basket_item bi on b.basket_ID = bi.basket_ID
    join menu m on bi.menu_ID = m.menu_ID
    left join Menu_picture mp on m.menu_ID = mp.menu_ID
    join store s on m.store_ID = s.store_ID
    where b.user_ID = %s
    group by s.store_name, b.delivery_method;
    """% user_input
    df_info = pd.read_sql_query(sql_info, conn)

    df_dict = {
        "store_name": df_info['store_name'].tolist(),
        "menu": {
            "url": df_info['url'].tolist(),
            "menu_name": df_info['menu_name'].tolist(),
            "menu_option": df_info['menu_option'].tolist(),
            "amount": df_info['amount'].tolist(),
        },
        "delivery": {
            "delivery_method": df_info['delivery_info'].tolist(),
            "expected_time": df_info['expected_time'].tolist(),
        },
        "price": {
            "delivery_tip": df_info['delivery_tip'].tolist(),
            "total_menu_price": df_info['total_menu_price'].tolist(),
            "total_price": df_info['total_price'].tolist(),
        }
    }

    return df_dict

if __name__ == "__main__":
    app.run()