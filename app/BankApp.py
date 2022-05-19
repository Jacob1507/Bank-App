from app_db.db_validation import *


class BankApp:

    @staticmethod
    def main_view():
        actions = {
            "register": 1,
            "login": 2,
            "exit": 3
        }
        return actions

    @staticmethod
    def menu_view(user_id: int):
        while True:
            msg = int(input('\nWitaj użytkowniku!\n'
                            '1) Stan konta\n'
                            '2) Wpłać pieniądze\n'
                            '3) Wypłać pieniądze\n'
                            '-------------------\n'
                            '4) Wpłać w innej walucie\n'
                            '5) Wypłać w innej walucie\n'
                            '-------------------\n'
                            '6) Historia transakcji\n'
                            '7) Logout\n'))
            actions = {
                "acc_balance": 1,
                "deposit_cash": 2,
                "withdrawal_cash": 3,
                "deposit_in_diff_currency": 4,
                "withdrawal_in_diff_currency": 5,
                "last_transactions": 6
            }

            if msg == actions["acc_balance"]:
                acc = AccountCashManagement(cash_deposit=0, cash_withdrawal=0, user_id=user_id)
                if acc.acc_balance() is None:
                    print('Nie ma środków na koncie')
                else:
                    print(f"Aktualnie masz na koncie: {round(acc.acc_balance(), 2)} zł.\n")

            elif msg == actions["deposit_cash"]:
                amount = float(input("\nIle chcesz wpłacić pieniędzy?: "))
                acc = AccountCashManagement(cash_deposit=amount, cash_withdrawal=0, user_id=user_id)
                acc.deposit_cash()
                print(f"Wpłacono: {amount} PLN\n")

            elif msg == actions["withdrawal_cash"]:
                amount = float(input("\nIle chcesz wypłacić pieniędzy?: "))
                acc = AccountCashManagement(cash_deposit=0, cash_withdrawal=amount, user_id=user_id)
                acc.withdrawal_cash()
                print(f"Wypłacono: {amount} PLN\n")

            elif msg == actions['deposit_in_diff_currency']:
                currency = AccountCashManagement.change_currency()
                amount = float(input("\nIle chcesz wpłacić pieniędzy?: "))
                acc = AccountCashManagement(cash_deposit=amount*currency[0], cash_withdrawal=0, user_id=user_id)
                acc.deposit_cash()
                print(f"Wpłacono: {round(amount * currency[0], 2)} PLN\n")

            elif msg == actions['withdrawal_in_diff_currency']:
                currency = AccountCashManagement.change_currency()
                amount = float(input("\nIle chcesz wypłacić pieniędzy?: "))
                acc = AccountCashManagement(cash_deposit=0, cash_withdrawal=amount, user_id=user_id)
                acc.withdrawal_cash()
                print(f"Wypłacono: {round(amount / currency[0], 2)} {currency[1]}\n")

            elif msg == actions['last_transactions']:
                AccountCashManagement.last_transactions(user_id=user_id)

    def login_view(self):
        bank_id = int(input("Nr. Weryfikacyjny: "))
        password = input('Hasło: ')

        form = Login(bank_id, password)

        if form.password_match() and form.bank_id_match():
            self.menu_view(bank_id)
        else:
            print("Upewnij się że wpisałeś(aś) dobre dane\n")

    @staticmethod
    def register_model():
        status_ok = True
        tries = 3
        while status_ok:
            if tries == 0:
                print("Wyczerpano wszystkie próby.")
                break

            stop_registration = False

            name = None
            last_name = None
            age = None
            birth_date = None
            gender = None
            pesel = None
            phone_number = None
            password = None

            if not stop_registration:
                name = input('Imię: ')
                last_name = input('Nazwisko: ')
                stop_registration = full_name_validation(name, last_name)

            if not stop_registration:
                age = int(input('Wiek: '))
                stop_registration = age_validation(age)

            if not stop_registration:
                birth_date = input('Data urodzenia (ddmmyy): ')
                stop_registration = birth_date_validation(birth_date, age)

            if not stop_registration:
                gender = input('Płeć (male/female) ')
                stop_registration = sex_validation(gender)

            if not stop_registration:
                pesel = input('PESEL: ')
                stop_registration = basic_pesel_validation(pesel, birth_date)

            if not stop_registration:
                phone_number = input('Numer telefonu: ')
                password = input('Hasło (Więcej niż 6 znaków): ')
                stop_registration = check_password(password)

            if not stop_registration:
                form = RegisterUser(name=name,
                                    last_name=last_name,
                                    age=age,
                                    gender=gender,
                                    pesel=pesel,
                                    birth_date=birth_date,
                                    phone_number=phone_number,
                                    password=check_password(password)
                                    )
                # Jeśli użytkownik przejdzie weryfikacje zostaje dodany do dazy danych.
                form.add_to_database()
                form.display_user_bank_id(form.pesel)

            tries -= 1
            print(tries)


if __name__ == '__main__':

    while True:
        message = int(input('Opcje:\n'
                            '1) Rejstreacja\n'
                            '2) Login\n'
                            '3) Exit\n'))
        choice = BankApp.main_view()
        if message == choice['register']:
            try:
                BankApp.register_model()
                break
            except ValueError:
                print('Odświeżyć stronę?(t/n)')
                try_again = input('Wystąpił błąd podczas rejstracji. ')

                if try_again == 't':
                    continue
                else:
                    break

        elif message == choice['login']:
            BankApp().login_view()

        elif message == choice['exit']:
            print('Do zobaczenia!')
            break

        else:
            print('Nie ma takiej opcji.')
