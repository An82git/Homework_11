from collections import UserDict
from collections.abc import Iterator
from datetime import date, datetime


ERROR_DIC = {
             "NoneKeyError": "a non-existent team",
             "AddTypeError": "give me name and phone please",
             "ChangeTypeError": "give me name and phone please",
             "ChangeIndexError": "give the old and new phone number",
             "ChangeAttributeError": "no such contact exists",
             "ChangeValueError": "no such number exists",
             }

class Field:
    def __init__(self, value: str):
        self.__value = None
        if not value[0].isdigit() :
            self.value = value.title()
        else:
            self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("invalid phone number, must be 10 digits")
        self.__value = value

class Birthday(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = datetime.strptime(value, "%d.%m.%Y")

class Iterable:
    def __init__(self, data: dict, n_records) -> None:
        self.data = []
        self.values_list = [str(v) for v in data.values()]
        self.current_index = 0

        while len(self.data) < (len(data) / n_records):
            self.data.append([f"Page {self.current_index + 1}"] + [v for v in self.values_list[:n_records]])

            for item in self.values_list[:n_records]:
                self.values_list.remove(item)

            self.current_index += 1
        self.current_index = 0

    def __next__(self):
        if self.current_index < len(self.data):
            rezult = self.data[self.current_index]
            self.current_index += 1
            return rezult
        raise StopIteration

class Record:
    def __init__(self, name: str, phone: list | None = None, birthday: str | None = None):
        self.name = Name(name)
        self.phones = [Phone(p) for p in phone] if phone else []
        self.birthday = Birthday(birthday) if birthday else None

    # реалізація класу
    def add_phone(self, phone: str): # додавання Phone
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str): # видалення Phone
        index_phone = [str(p) for p in self.phones].index(phone)
        self.phones.pop(index_phone)

    def edit_phone(self, old_phone: str, new_phone: str): # редагування Phone
        index_phone = [str(p) for p in self.phones].index(old_phone)
        self.phones.pop(index_phone)
        self.phones.insert(index_phone, Phone(new_phone))

    def find_phone(self, phone: str) -> Phone: # пошуку Phone
        for p in self.phones:
            if str(p) == phone:
                return p

    def days_to_birthday(self) -> int | None:
        if self.birthday:
            birthday = self.birthday.value
            today = date.today()
            
            if birthday.replace(year=today.year) < today:
                return (birthday.replace(year=today.year + 1) - today).days
            return (birthday.replace(year=today.year) - today).days

    def __str__(self):
        day = self.birthday.value.strftime('%d %B %Y') if self.birthday else ""
        return "Contact name: {}, birthday: {}, phones: {}".format(
                                                                    self.name.value, 
                                                                    day, 
                                                                    '; '.join(p.value for p in self.phones)
                                                                    )

class AddressBook(UserDict):
    # реалізація класу
    data = {}
    n_records = 4

    def add_record(self, record: Record): # який додає запис до self.data
        self.data.update({record.name.value: record})

    def find(self, name: str) -> Record: # знаходить запис за ім'ям
        for n in self.data:
            if name.title() == n:
                return self.data.get(n)

    def delete(self, name: str): # видаляє запис за ім'ям
        for n in self.data:
            if name.title() == n:
                self.data.pop(n)
                return

    def __iter__(self) -> Iterator:
        return Iterable(self.data, self.n_records)


def hello(data: AddressBook) -> str:
    return "How can I help you?"


def add(data: AddressBook, name: str, phone: list | None = None, birthday: str | None = None):
    return data.add_record(Record(name, phone, birthday))


def change(data: AddressBook, name: str, old_phone: str , new_phone: str):
    return data.find(name).edit_phone(old_phone, new_phone)


def phone(data: AddressBook, name: str) -> str:
    return data.find(name)


def show_all(data: AddressBook) -> dict:
    return data


def good_bye(data: AddressBook) -> str:
    return "Good bye!"


def close(data: AddressBook) -> str:
    return "Good bye!"


def exit(data: AddressBook) -> str:
    return "Good bye!"


COMMAND_DIC = {"hello": hello,
               "add": add,
               "change": change,
               "phone": phone,
               "show all": show_all,
               "good bye": good_bye,
               "close": close,
               "exit": exit}


def input_error(func):
    def inner(data: AddressBook , string: str):

        try:
            return func(data, string)
        
        except Exception as error:
            command = str(pars(string).get("command")).title()
            _error_ = (repr(error)
                       .removesuffix(f"({str(error)})")
                       .removesuffix(f"('{str(error)}')")
                       .removesuffix(f'("{str(error)}")'))

            if command + _error_ in ERROR_DIC:
                error_value = ERROR_DIC.get(command + _error_)

                if type(error_value) == list and error.args[0] in error_value:
                    return str(error)
                
                return str(error_value)
            return f"Type: '{_error_}'. {error}"

    return inner

@input_error
def command_processing(data: AddressBook, string: str):
    string_dict = pars(string)
    str_command: str = string_dict.get("command")
    name: str = string_dict.get("name")
    birthday: str = string_dict.get("birthday")
    phones: list = string_dict.get("phones")
    command = COMMAND_DIC[str_command]

    if str_command in ["add"]:
        return command(data, name, phones, birthday)
    elif str_command in ["change"]:
        return command(data, name, phones[0], phones[1])
    elif str_command in ["phone"]:
        return command(data, name)
    else:
        return command(data)


def pars(string: str) -> dict:
    string_dict = {}
    string = string.strip()
    phones = []

    for command in COMMAND_DIC:
        if command in string:
            string_dict.update({"command": command})
            string = string.removeprefix(command).strip()

    if string:
        for item in string.split(" "):
            if item.isdigit():
                phones.append(item)
                string_dict.update({"phones": phones})
            elif item.isalnum():
                string_dict.update({"name": item})
            else:
                string_dict.update({"birthday": item})

    return string_dict


def main():
    end = True

    contacts = AddressBook()

    while end:
        string = input().lower()

        if string:
            rezult_command = command_processing(contacts, string)

            if type(rezult_command) == AddressBook:
                for record in rezult_command:
                    print(record)
            elif type(rezult_command) == str:
                print(rezult_command)

                if rezult_command == "Good bye!":
                    end = False

        else:
            end = False


if __name__ == "__main__":
    main()
