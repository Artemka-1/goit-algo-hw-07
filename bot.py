from datetime import datetime, date, timedelta
from collections import UserDict

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Ошибка этот контакт не найден"
        except ValueError as e:
            return f"Ошибочка: {e}"
        except IndexError:
            return "ата-та-та недостаточно аргументов."
        except TypeError:
            return "ата-та-та неправильный тип данных."
        except Exception as e:
            return f"Непредвиденная ошибочка: {e}"
        except IndexError:
            return f"ошибка {e}"
    return inner


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
            raise ValueError("Phone number must be exactly 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY")
        super().__init__(value)

    def __str__(self):
        return self.value
    



class Record:
    def __init__(self, name: str):
        self.name = Name(name)      
        self.phones = []          
        self.birthday = None     

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str):
        for p in self.phones:
            if p.value == old_phone:
                self.phones.remove(p)
                self.phones.append(Phone(new_phone))
                return
        raise ValueError("Old phone number not found.")

    def add_birthday(self, bday: str):
        self.birthday = Birthday(bday)

    def days_to_next_birthday(self) -> int:
        if not self.birthday:
            raise ValueError("Birthday not set")
        today = date.today()
        bday = datetime.strptime(self.birthday.value, "%d.%m.%Y").date()
        next_bday = bday.replace(year=today.year)
        if next_bday < today:
            next_bday = next_bday.replace(year=today.year + 1)
        return (next_bday - today).days

    def age(self) -> int:
        if not self.birthday:
            raise ValueError("Birthday not set")
        today = date.today()
        bday = datetime.strptime(self.birthday.value, "%d.%m.%Y").date()
        years = today.year - bday.year
        if (today.month, today.day) < (bday.month, bday.day):
            years -= 1
        return years

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        bday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"{self.name.value}: {phones}{bday}"

    




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
            if record.birthday is None:
                continue
            bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            if bday < today:
                bday = bday.replace(year=today.year + 1)
            if bday.weekday() == 5:
                bday += timedelta(days=2)
            elif bday.weekday() == 6:
                bday += timedelta(days=1)
            if 0 <= (bday - today).days <= 6:
                result.append({"name": record.name.value, "birthday": bday.strftime("%Y-%m-%d")})
        return result

def parse_input(user_input: str):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]
@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        return "Usage: add <name> <phone>"
    name, phone = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return f"Contact {name} added/updated."
    
    while True:
    command = input("Enter a command: ").strip()
    if not command:
        continue

    parts = command.split()
    cmd = parts[0].lower()   # игнорируем регистр команды
    args = parts[1:]         # остальные части — аргументы

    if cmd == "add":
        print(add_contact(args))
    elif cmd == "exit":
        break
    else:
        print(f"Unknown command: {cmd}")

def change_contact(args, book: AddressBook):
    if len(args) != 3:
        return "Usage: change <name> <old_phone> <new_phone>"
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone for {name} changed."

def phone_username(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: phone <name>"
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    phones = "; ".join(p.value for p in record.phones)
    return f"{name}: {phones}"

def all_contacts(book: AddressBook):
    return str(book) if book.data else "No contacts found."

def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        return "Usage: add-birthday <name> <YYYY-MM-DD>"
    name, bday = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    try:
        record.add_birthday(bday)
        return f"Birthday for {name} added: {bday}"
    except ValueError as e:
        return str(e)

def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: show-birthday <name>"
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    return f"{name}'s birthday: {record.birthday}" if record.birthday else f"{name} has no birthday set."

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("Hello! How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(phone_username(args, book))
        elif command == "show" and args and args[0] == "all":
            print(all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            upcoming = book.get_upcoming_birthdays()
        elif command == "all":
            print(all_contacts(book))
            if upcoming:
                for item in upcoming:
                    print(f"{item['name']} -> {item['birthday']}")
            else:
                print("No upcoming birthdays in next 7 days")
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
