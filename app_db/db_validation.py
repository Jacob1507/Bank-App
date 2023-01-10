# Main Import
import sqlite3
from sqlite3 import Error
import bcrypt
# Additional Import
import requests
import random
import datetime

"""
Moduł tworzy połączenie z bazą danych oraz jest odpowiedzialny za filtrowanie informacji
przekazywanych przez użytkownika.
"""
"""
TODO: 
      Validacja bank_id użytkownika
"""


class SqlConnection:

    def __init__(self, db_file="..\\bankApp.db"):
        self.db_file = db_file

    def create_connection(self):
        """ create a database connection to the SQLite database
            specified by db_file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            conn.execute('PRAGMA foreign_keys = 1')
        except Error as e:
            print(e)
        return conn

    def create_table_for_user(self):
        """Stworzenie tabeli dla użytkownika."""
        conn = self.create_connection()
        c = conn.cursor()
        c.execute("""
                CREATE TABLE IF NOT EXISTS user (
                bank_id INTEGER  PRIMARY KEY,
                first_name TEXT NOT NULL, 
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL, 
                birth_date TEXT NOT NULL,
                gender TEXT  NOT NULL,
                pesel INTEGER NOT NULL,
                phone_number INTEGER,
                password VARCHAR
                )""")

    def create_table_for_user_account(self):
        conn = self.create_connection()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS user_account (
            cash_deposit NUMERIC,
            cash_deposit_date TEXT,
            cash_withdrawal NUMERIC,
            cash_withdrawal_date TEXT,
            bank_id INTEGER,
            FOREIGN KEY (bank_id) REFERENCES user (bank_id)
            )""")

    def create_payment_record(self, form):
        sql = """ INSERT INTO user_account (
            cash_deposit,
            cash_deposit_date,
            cash_withdrawal,
            cash_withdrawal_date,
            bank_id
            ) VALUES (?, ?, ?, ?, ?)
        """

        conn = self.create_connection()
        c = conn.cursor()
        c.execute(sql, form)
        conn.commit()

    def create_user_data(self, user):
        sql = """ INSERT INTO user(
            first_name,
            last_name,
            age,
            birth_date,
            gender,
            pesel,
            phone_number,
            bank_id,
            password
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn = self.create_connection()
        c = conn.cursor()
        c.execute(sql, user)
        conn.commit()


class CreateUniqueBankId:
    """Klasa poświęcona generowaniu id do weryfikacji użytkowników banku"""

    @staticmethod
    def create_id():
        num_list = list(range(7))
        random.shuffle(num_list)
        num_list_str_convert = [str(num) for num in num_list]

        bank_id = ''.join(num_list_str_convert)
        return bank_id


class RegisterUser:
    """Klasa pobiera inforacje od użytkownika oraz je weryfikuje."""
    def __init__(self, name, last_name, age, gender, pesel, birth_date, phone_number, password):
        self.first_name = name.title()
        self.last_name = last_name.title()
        self.age = int(age)
        self.gender = gender
        self.pesel = pesel
        self.birth_date = birth_date
        self.phone_number = phone_number
        self.password = password

    def hash_password(self):
        passwd = self.password.encode("utf-8")
        hashed_pw = bcrypt.hashpw(passwd, bcrypt.gensalt())
        return hashed_pw

    def add_to_database(self):
        conn = SqlConnection().create_connection()

        with conn:
            user = (
                    self.first_name,
                    self.last_name,
                    self.age,
                    self.birth_date,
                    self.gender,
                    self.pesel,
                    self.phone_number,
                    CreateUniqueBankId().create_id(), self.hash_password())

            try:
                SqlConnection().create_user_data(user=user)
            except sqlite3.IntegrityError:
                new_id = CreateUniqueBankId().create_id()
                user = (
                        self.first_name, self.last_name,
                        self.age, self.birth_date,
                        self.gender, self.pesel,
                        self.phone_number, new_id, self.hash_password())
                SqlConnection().create_user_data(user=user)
                SqlConnection().create_table_for_user_account()

    @staticmethod
    def display_user_bank_id(pesel):
        conn = SqlConnection().create_connection()
        bank_id = list(conn.execute(f"""SELECT bank_id FROM user WHERE pesel={pesel}"""))[-1]
        print(f"Twój nr. id to {bank_id[0]}")


class Login:

    def __init__(self, bank_id, password):
        self.bank_id = bank_id
        self.password = password

    def bank_id_match(self):
        conn = SqlConnection().create_connection()
        c = conn.cursor()
        id_search = c.execute("""SELECT bank_id FROM user""")
        for id_num in id_search:
            id_num = id_num[0]
            if id_num == self.bank_id:
                return True
        return False

    def password_match(self):
        conn = SqlConnection().create_connection()
        c = conn.cursor()
        pw_search = c.execute("""SELECT password FROM user""")

        for pw in pw_search:
            pw = pw[0]
            if bcrypt.checkpw(self.password.encode("utf-8"), pw):
                return True

            else:
                return False


class AccountCashManagement:

    def __init__(self, user_id, cash_deposit=0, cash_withdrawal=0):
        self.cash_deposit = cash_deposit
        self.cash_withdrawal = f"-{cash_withdrawal}"
        self.cash_deposit_date = datetime.datetime.today()
        self.cash_withdrawal_date = datetime.datetime.today()
        self.user_id = user_id

    def deposit_cash(self):
        conn = SqlConnection().create_connection()
        self.cash_withdrawal = 0

        with conn:
            form = (
                self.cash_deposit, self.cash_deposit_date,
                self.cash_withdrawal, self.cash_withdrawal_date,
                self.user_id
            )
            SqlConnection().create_payment_record(form=form)

    def withdrawal_cash(self):
        conn = SqlConnection().create_connection()
        self.cash_deposit = 0

        with conn:
            form = (
                self.cash_deposit, self.cash_deposit_date,
                float(self.cash_withdrawal), self.cash_withdrawal_date,
                self.user_id
            )
            SqlConnection().create_payment_record(form=form)

    def acc_balance(self):
        conn = SqlConnection().create_connection()

        depo = conn.execute(f"""SELECT SUM (cash_deposit) FROM user_account WHERE bank_id={self.user_id}""")
        withdrawal = conn.execute(f"""SELECT SUM (cash_withdrawal) FROM user_account WHERE bank_id={self.user_id}""")

        balance = 0
        for x, y in zip(depo, withdrawal):
            try:
                balance = x[0] + y[0]
            except TypeError:
                balance = x[0]
        return balance

    @staticmethod
    def change_currency():
        url = "http://api.nbp.pl/api/exchangerates/tables/a/"
        x = requests.get(url).json()
        possible_rates = x[0]['rates'][1:5]

        print('Dostępne kursy walut:')
        count = 0
        for rate in possible_rates:
            count += 1
            print(f"\t{count}. {rate['currency']}")

        choice = int(input("\nNa jaki kurs chcesz zamienić walutę?(Nr.): "))
        currency = x[0]['rates'][choice]['mid']
        curr_name = x[0]['rates'][choice]['code']
        return round(currency, 2), curr_name

    @staticmethod
    def list_of_currencies():
        url = "http://api.nbp.pl/api/exchangerates/tables/a/"
        x = requests.get(url).json()
        possible_rates = x[0]['rates']
        return possible_rates[1:5]

    @staticmethod
    def last_transactions(user_id):
        conn = SqlConnection().create_connection()

        last_depo = conn.execute(f"""SELECT cash_deposit, cash_deposit_date FROM user_account 
                                WHERE bank_id={user_id} ORDER BY cash_deposit_date DESC LIMIT 10""")

        last_withdrawal = conn.execute(f"""SELECT cash_withdrawal, cash_withdrawal_date FROM user_account
                                        WHERE bank_id={user_id} ORDER BY cash_withdrawal_date DESC LIMIT 10""")

        print('\nOstatnie wpłaty:')
        for value in last_depo:
            try:
                cash = round(value[0], 2)
                date = value[1][:-7]
                print(f'\t- {cash}, {date}')
            except TypeError:
                continue

        print('\nOstatnie wypłaty:')
        for value in last_withdrawal:
            try:
                cash = round(value[0], 2)
                date = value[1][:-7]
                print(f'\t- {cash}, {date}')
            except TypeError:
                continue


def full_name_validation(f_name: str, l_name: str):
    data_false = False
    if len(f_name) > 30:
        print('Długość imienia nie moze przekraczać 30 liter.')
        data_false = True
    elif len(l_name) > 30:
        print('Długość nazwiska nie może przekrac 30 liter.')
        data_false = True
    return data_false


def check_password(passwd: str):
    if len(passwd) < 6:
        print('Hasło jest za krótkie')
        return True


def age_validation(age: int):
    if age <= 3 or age >= 120:
        print("Upewnij się, że wiek został dobrze wpisany.")
        return True


def birth_date_validation(birthday: str, age: int):
    data_false = False

    date = birthday
    current_year = datetime.datetime.today().year
    current_year = str(current_year)[2:]

    day = date[:2]
    month = date[2:4]
    year = date[4:]

    if month.startswith("0"):
        month = date[3]

    if day.startswith("0"):
        day = date[1]

    if 1 < int(day) > 31:
        print("Dzień nie może być mniejszy od 1 lub większy od 31.")
        data_false = True

    if 1 < int(month) > 12:
        print("Miesiąc nie może być mniejszy od 1 lub większy od 12.")
        data_false = True
    if age < 18 or (age - int(current_year) == year):
        print('Musisz mieć skończone 18 lat aby założyć konto.')
        data_false = True

    # if len(str(month)) == 1:
    #     date = f'{day}-0{month}-{year}'
    #     if len(str(day)) == 1 and len(str(month)) == 1:
    #         date = f'0{day}-0{month}-{year}'
    # else:
    #     date = f'{day}-{month}-{year}'
    return data_false


def basic_pesel_validation(pesel: str, birth_date: str):
    """Podzielenie peselu na elementy"""

    year1, year2 = pesel[:2], birth_date[4:]
    month1, month2 = pesel[2:4], birth_date[2:4]
    day1, day2 = pesel[4:6], birth_date[:2]

    pesel_date_objects = [year1, month1, day1]
    birth_date_objects = [year2, month2, day2]

    for pesel_object, date_object in zip(pesel_date_objects, birth_date_objects):
        if pesel_object != date_object:
            return True
        else:
            return False


def gender_validation(gender: str):
    options = ('male', 'female')
    if gender not in options:
        print('Sprawdź czy poprawnie została wpisana płeć')


if __name__ == '__main__':
    print(SqlConnection().db_file)
