from collections import UserDict
from datetime import datetime, timedelta

# === Базові класи ===
class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

# === Record ===
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Phone not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

# === AddressBook ===
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday.replace(year=today.year)

                # Якщо вже пройшов, дивимося наступний рік
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)

                delta_days = (bday_this_year - today).days
                if 0 <= delta_days <= 7:
                    # Перенос на понеділок, якщо вихідний
                    if bday_this_year.weekday() >= 5:  
                        days_to_monday = 7 - bday_this_year.weekday()
                        bday_this_year += timedelta(days=days_to_monday)

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": bday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays

# === Декоратор для обробки помилок ===
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments."
        except KeyError:
            return "Contact not found."
    return inner

# === Хендлери команд ===
@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."
    raise KeyError

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return ", ".join(p.value for p in record.phones)
    raise KeyError

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    result = []
    for record in book.values():
        phones = ", ".join(p.value for p in record.phones)
        bday = record.birthday.value if record.birthday else "N/A"
        result.append(f"{record.name.value}: {phones}, Birthday: {bday}")
    return "\n".join(result)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    raise KeyError

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value
    elif record:
        return "No birthday set."
    raise KeyError

@input_error
def birthdays(args, book: AddressBook):
    result = book.get_upcoming_birthdays()
    if not result:
        return "No upcoming birthdays."
    return "\n".join(f"{r['name']}: {r['birthday']}" for r in result)

# === Парсер команд ===
def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

# === Основний цикл ===
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
