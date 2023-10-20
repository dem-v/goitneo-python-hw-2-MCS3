from collections import UserDict


class DefaultExecutionDict(UserDict):
    def __getitem__(self, key):
        if not key in self.data.keys():
            return DEFAULT_METHOD
        else:
            return self.data.get(key)


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyNotExistInContacts as e:
            return f"This contact exists {e}."
        except KeyExistInContacts as e:
            return f"This contact does not exist {e}."
        except KeyError as e:
            return f"This contact does not exist {e}."
        except IndexError:
            return f"Bad arguments {args[1:]}."
        except BadPhoneNumber as e:
            return f"The phone number does not match the requirements {e}."
        except PhoneNumberIsMissing as e:
            return f"This number does not exist {e}."

    return inner


class KeyExistInContacts(Exception):
    pass


class KeyNotExistInContacts(Exception):
    pass


class BadPhoneNumber(Exception):
    pass


class PhoneNumberIsMissing(Exception):
    pass


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value


class Name(Field):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return str(self.value) == str(other.value)


class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isnumeric():
            self.value = value
        else:
            raise BadPhoneNumber(value)

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return str(self.value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name and not bool(
            set(self.phones).intersection(__value.phones)
        )

    @input_error
    def add_phone(self, phone: str):
        p = Phone(phone)
        self.phones.append(p)

    @input_error
    def edit_phone(self, orig_phone: str, new_phone: str):
        a = Phone(orig_phone)
        b = Phone(new_phone)

        try:
            ind = self.phones.index(a)
        except ValueError:
            raise PhoneNumberIsMissing(orig_phone)

        self.phones[ind] = b

    @input_error
    def remove_phone(self, phone: str):
        p = Phone(phone)
        self.phones.remove(p)

    @input_error
    def find_phone(self, phone: str):
        p = Phone(phone)
        return p if p in self.phones else None


class AddressBook(UserDict):
    def add_record(self, rec: Record):
        self.data[str(rec.name)] = rec

    def find(self, name: str):
        if not name in self.data.keys():
            return None
        else:
            return self.data.get(name)

    def delete(self, name: str):
        if name in self.data.keys():
            _ = self.data.pop(name)


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def write_contact(contacts, args, is_change=False, *_):
    if len(args) != 2:
        raise IndexError()
    name, phone = args

    if name in contacts.keys() and not is_change:
        raise KeyExistInContacts(name)
    elif name not in contacts.keys() and is_change:
        raise KeyNotExistInContacts(name)

    contacts[name] = phone
    return f"Contact {name} {'changed' if is_change else 'added'}."


def write_contact_add(contacts, args, *_):
    return write_contact(contacts, args, False)


def write_contact_change(contacts, args, *_):
    return write_contact(contacts, args, True)


@input_error
def get_phone(contacts, args, *_):
    name = args[0]
    if name not in contacts.keys():
        raise KeyNotExistInContacts(name)
    return f"{contacts[name]}"


def print_phonebook(contacts, *_):
    return "\n".join(["{} {}".format(k, v) for k, v in contacts.items()])


def print_goodbye(*_):
    return "Good bye!"


def print_hello(*_):
    return "How can I help you?"


def print_bad(*_):
    return "Invalid command."


OPERATIONS = DefaultExecutionDict(
    {
        "close": print_goodbye,
        "exit": print_goodbye,
        "hello": print_hello,
        "add": write_contact_add,
        "change": write_contact_change,
        "phone": get_phone,
        "all": print_phonebook,
    }
)

DEFAULT_METHOD = print_bad


def main():
    contacts = {}
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        print(
            OPERATIONS[command](contacts, args, True if command == "change" else False)
        )
        if command in ["close", "exit"]:
            break


if __name__ == "__main__":
    # main()

    # test code
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Видалення запису Jane
    book.delete("Jane")
