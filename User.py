from flask import Flask, jsonify
import mysql.connector
import os

app = Flask(__name__)
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT
            User.nickname,
            User.name,
            User.email AS representative_email,
            User.login_method,
            User_Picture.picture_url AS profile_picture
        FROM User
        LEFT JOIN User_Picture ON User.user_ID = User_Picture.user_ID
        WHERE User.user_ID = %s;
        """
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return jsonify(user_data), 200
        else:
            return jsonify({"error": "User not found"}), 404 
        
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True)