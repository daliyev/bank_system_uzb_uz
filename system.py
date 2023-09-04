import sqlite3
from abc import ABC, abstractmethod

from contextlib import closing


def menu():
    print("""
    System Menu
    1. A'zo qoshish
    2. Depozit
    3. Pul yechish
    4. O'tkazma
    5. Foydalanuvchilar
    6. Chiqish
    """)


class BaseCRUD(ABC):
    def __init__(self, database_path, table_name):
        self.database_path = database_path
        self.table_name = table_name

    def get_connection(self):
        return closing(sqlite3.connect(self.database_path))

    def insert(self, **kwargs):
        with self.get_connection() as connection:
            cursor = connection.cursor()
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join('?' for _ in kwargs)
            query = f"insert into {self.table_name} ({columns}) values ({placeholders})"
            cursor.execute(query, tuple(kwargs.values()))
            connection.commit()

    def balance_update(self, id, balance, id_column="id"):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                cursor.execute("begin TRANSACTION")
                cursor.execute(f"select balance from {self.table_name} where {id_column}=?;", (id,))
                result = cursor.fetchone()
                new_balance = balance + int(result[0])
                query = f"UPDATE {self.table_name} SET balance={new_balance} where {id_column}=?;"
                cursor.execute(query, (id,))
                connection.commit()
            except:
                print(f"Xatolik chiqdi!")
                connection.rollback()

    def withdraw(self, id, summ, id_column="id"):
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("begin TRANSACTION")
            cursor.execute(f"select balance from {self.table_name} where {id_column}=?;", (id,))
            result = cursor.fetchone()
            new_balance = int(result[0]) - summ
            if new_balance >= 0:
                cursor.execute(f"update {self.table_name} set balance={new_balance} where {id_column}=?;", (id,))
                connection.commit()
                return 1
            else:
                connection.rollback()
                return 0

    def transfer(self, from_id, to_id, summ, id_column):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                cursor.execute(f"begin transaction")
                cursor.execute(f"select balance from {self.table_name} where {id_column}=?;", (from_id,))
                result = cursor.fetchone()
                new_balance = int(result[0]) - summ
                if new_balance >= 0:
                    cursor.execute(f"update {self.table_name} set balance={new_balance} where {id_column}=?;",(from_id,))
                    cursor.execute(f"select balance from {self.table_name} where {id_column}=?;", (to_id,))
                    result = cursor.fetchone()
                    new_balance = int(result[0]) + summ
                    cursor.execute(f"update {self.table_name} set balance={new_balance} where {id_column}=?;",(to_id,))
                    connection.commit()
                    return 1
                else:
                    print(f"Xatolik chiqdi!")
                    connection.rollback()
                    return 0
            except:
                print(f"Xatolik chiqdi!")
                connection.rollback()
                return 0
    def users(self):
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"select * from {self.table_name};")
            return cursor.fetchall()
users_crud = BaseCRUD("PaySysDb.db", "Users")

while True:
    menu()
    chooise = int(input("Tanglang: "))
    while chooise not in range(1, 7):
        print("Xato! Qayta tanlang.")
        chooise = int(input("Tanglang: "))

    if chooise == 1:
        cnt = 1
        while cnt == 1:
            id = int(input("ID kiriting: "))
            name = input("Ism kiriting: ")
            balance = int(input("Boshlang'ich mablag'i: "))
            users_crud.insert(id=id, name=name, balance=balance)
            cnt = int("Qo'shida davom etasizmi( 1/0 ): ")
    elif chooise == 2:
        id = int(input("ID kiriting: "))
        depozit = int(input("Qancha pul qo'yasiz: "))
        users_crud.balance_update(id, depozit, "id")
    elif chooise == 3:
        id = int(input("ID kiriting: "))
        w_sum = int(input("Summa: "))
        result = users_crud.withdraw(id, w_sum, "id")
        if result == 1:
            print("Muaffaqiyatli amalga oshirildi!")
        elif result == 0:
            print("Xatolik!")
    elif chooise == 4:
        id1 = int(input("Yuboruvchi ID raqamini kiriting: "))
        id2 = int(input("Oluvchi ID raqamini kiriting: "))
        sum = int(input("Yuborish miqdori: "))
        users_crud.transfer(id1, id2, sum, "id")
    elif chooise == 5:
        for i in users_crud.users():
            print(i)
    elif chooise == 6:
        print("Good bye!")
        break