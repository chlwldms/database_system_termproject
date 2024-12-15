from flask import Flask, jsonify  # jsonify 추가
import pymysql
import pandas as pd

app = Flask(__name__)
@app.route('/api/v1/users/<int:user_id>/reviews', methods=['GET'])

def get_all_user_reviews(user_id):
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='0000', db='baemin')

    reviews_sql = """
       select r.review_ID,
       r.basket_ID,
       s.store_name,
       r.rating,
     r.content,
       group_concat(distinct concat(
                             (select m2.menu_name
                             from Menu m2
                             where m2.menu_ID = bi.menu_ID)
                             )) as menu_names,
       group_concat(distinct rp.picture_url) as picture_urls,
       CASE
           WHEN TIMESTAMPDIFF(MINUTE, review_time, NOW()) < 1 THEN '방금 전'
           WHEN TIMESTAMPDIFF(MINUTE, review_time, NOW()) < 60 THEN CONCAT(TIMESTAMPDIFF(MINUTE, review_time, NOW()), '분 전')
           WHEN TIMESTAMPDIFF(HOUR, review_time, NOW()) < 24 THEN CONCAT(TIMESTAMPDIFF(HOUR, review_time, NOW()), '시간 전')
           WHEN TIMESTAMPDIFF(DAY, review_time, NOW()) < 30 THEN CONCAT(TIMESTAMPDIFF(DAY, review_time, NOW()), '일 전')
           ELSE CONCAT(TIMESTAMPDIFF(MONTH, review_time, NOW()), '달 전')
       END as time_ago,
       rc.content as comment
    from Review r
    join store s on r.store_ID = s.store_ID
    join menu m on s.store_ID = m.store_ID
    left join Review_picture rp on r.review_ID = rp.review_ID
    join basket b on r.basket_ID = b.basket_ID
    join basket_item bi on b.basket_ID = bi.basket_ID
    left join Review_comment rc on r.review_ID = rc.review_ID
    where r.user_ID = %s
group by r.review_ID, s.store_name, r.rating, r.content, comment
order by r.review_time desc;
    """ %user_id
    
    try:
        df = pd.read_sql_query(reviews_sql, conn)

        reviews = []
        for _, row in df.iterrows():
            review_dict = {
                'review_id': int(row['review_ID']),
                'basket_id': int(row['basket_ID']),
                'store_name': row['store_name'],
                'rating': int(row['rating']),
                'content': row['content'],
                'menu_names': row['menu_names'].split(',') if row['menu_names'] else [],
                'picture_urls': row['picture_urls'].split(',') if row['picture_urls'] else [],
                'time_ago': row['time_ago'],
                'comment': row['comment'] if row['comment'] else None
            }
            reviews.append(review_dict)

        df_dict = {
            'status': 'success',
            'message': 'Reviews retrieved successfully',
            'data': {
                'reviews': reviews,
                'total_count': len(reviews)
            }
        }
        
        return jsonify(df_dict)

    except Exception as e:
        error_dict = {
            'status': 'error',
            'message': str(e)
        }
        return jsonify(error_dict)
        
    finally:
        conn.close()

if __name__ == "__main__":
    app.run()