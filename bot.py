def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
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
            if upcoming:
                for item in upcoming:
                    print(f"{item['name']} -> {item['birthday']}")
            else:
                print("No upcoming birthdays in next 7 days")

        else:
            print("Invalid command")
if __name__ == "__main__":
    main()
