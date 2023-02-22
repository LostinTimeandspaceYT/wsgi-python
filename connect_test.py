from mysql.connector import (connection)

cnx = connection.MySQLConnection(user='root', password='nhti',
                                 host='127.0.0.1',
                                 database='movies')
if cnx is not None:
    print("success!")

cursor = cnx.cursor()
query = "SELECT m_title FROM movie LIMIT 1"
cursor.execute(query)
for title in cursor:
    print(title)
cnx.close()
