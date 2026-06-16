import html

from flask import Flask, request, render_template
import mysql.connector
from sshtunnel import SSHTunnelForwarder

app = Flask(__name__)

def get_db_connection():
    server = SSHTunnelForwarder(
        ('172.26.55.48', 22),
        ssh_username='stsuser',
        ssh_password='Vilsts#user',   # 🔴 put ssh password here
        remote_bind_address=('172.26.55.48', 6037)
    )

    server.start()

    conn = mysql.connector.connect(
        host='172.26.55.48',
        port=server.local_bind_port,
        user='stsuser',
        password='Stsuser@123',
        database='CMP_CORE_PREPROD'
    )

    return conn, server


@app.route("/", methods=["GET", "POST"])
def update_record():
    if request.method == "POST":
        record_id = request.form["id"]
        status = request.form["status"]

        conn, server = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE YOUR_TABLE_NAME
        SET status = %s
        WHERE id = %s
        """

        cursor.execute(query, (status, record_id))
        conn.commit()

        cursor.close()
        conn.close()
        server.stop()

        return "Record updated successfully ✅"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
