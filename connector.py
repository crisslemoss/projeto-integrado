import mysql.connector
from dbfread import DBF
import os

try:
    path = 'files\\'
    files = os.listdir(path)

    connection = mysql.connector.connect(host='localhost',
                                         database='votacao_camara_deputados',
                                         user='root',
                                         password='medsys')

    create = "CREATE TABLE `votos` (`Proposicao` varchar(255) DEFAULT NULL," +\
        "`NumeroVotacao` varchar(255) DEFAULT NULL," +\
        "`Parlamentar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL," + \
        "`UF` varchar(100) DEFAULT NULL," + \
        "`VotoParlamentar` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL," + \
        "`Partido` varchar(50) DEFAULT NULL," + \
        "`VotoPartido` varchar(50) DEFAULT NULL" + \
        ") ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci"

    cursor = connection.cursor()
    cursor.execute(create)
    connection.commit()
    cursor.close()

    for file_name in files:
        full_path = path + file_name

        cursor = connection.cursor()
        for record in DBF(full_path):

            values = "'" + file_name.split('_C')[0] + "','" + record["NUMVOT"] + "','" + record["NOME_PAR"] + \
                "','" + record["ESTADO"] + "','" + record["VOTO"] + \
                "','" + record["PARTIDO"] + "'"

            mySql_insert_query = """INSERT INTO votos (Proposicao, NumeroVotacao, Parlamentar, UF, VotoParlamentar, Partido) 
                           VALUES (""" + values + """) """
            print(mySql_insert_query)

            cursor.execute(mySql_insert_query)
            connection.commit()

        cursor.close()

except mysql.connector.Error as error:
    print("Failed to insert record into votos table {}".format(error))

finally:
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")
