from datetime import datetime, date, timedelta
from collections import UserDict

# Декоратор для обработки ошибок
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return f"Error: {e}"
        except IndexError:
            return "Not enough arguments provided."
        except TypeError:
            return "Incorrect type of arguments."
    return inner

# Базовый класс для всех полей
class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value: str):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

# Класс записи контакта
class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone not found.")

    def edit_phone(self, old_phone: str, new_phone: str):
        for p in self.phones:
            if p.value == old_phone:
                self.phones.remove(p)
                self.phones.append(Phone(new_phone))
                return
        raise ValueError("Old phone number not found.")

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, bday: str):
        self.birthday = Birthday(bday)

    def days_to_next_birthday(self) -> int:
        if not self.birthday:
            raise ValueError("Birthday not set.")
        today = date.today()
        bday = datetime.strptime(self.birthday.value, "%d.%m.%Y").date()
        next_bday = bday.replace(year=today.year)
        if next_bday < today:
            next_bday = next_bday.replace(year=today.year + 1)
        return (next_bday - today).days

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        bday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"{self.name.value}: {phones}{bday}"

# Класс адресной книги
class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        self.data.pop(name, None)

    def __str__(self):
        return "\n".join(str(rec) for rec in self.data.values())

    def get_upcoming_birthdays(self):
        result = []
        today = date.today()
        for record in self.data.values():
            if not record.birthday:
                continue
            bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            next_bday = bday.replace(year=today.year)
            if next_bday < today:
                next_bday = next_bday.replace(year=today.year + 1)
            # Перенос на следующий рабочий день если выходной
            if next_bday.weekday() == 5:
                next_bday += timedelta(days=2)
            elif next_bday.weekday() == 6:
                next_bday += timedelta(days=1)
            if 0 <= (next_bday - today).days <= 6:
                result.append({"name": record.name.value, "birthday": next_bday.strftime("%d.%m.%Y")})
        return result

# Парсер команд
def parse_input(user_input: str):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]

# Обработчики команд
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return f"Phone for {name} changed."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    return "; ".join(p.value for p in record.phones)

@input_error
def add_birthday(args, book: AddressBook):
    name, bday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(bday)
    return f"Birthday for {name} added: {bday}"

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    return f"{name}'s birthday: {record.birthday.value}" if record.birthday else f"{name} has no birthday set."

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in next 7 days."
    return "\n".join(f"{item['name']} -> {item['birthday']}" for item in upcoming)

# Основной цикл бота
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
            print(book if book.data else "No contacts found.")
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

