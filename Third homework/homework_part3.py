import pickle
from collections import UserDict, defaultdict
from datetime import datetime, timedelta



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    pass

class Phone(Field):
    def __init__(self,phone):
        super().__init__(phone)
        if not self.is_valid_phone_number(phone):
            raise ValueError(f"Phone number should contain 10 digits: {phone}")
    def is_valid_phone_number(self, phone):
        return phone.isdigit() and len(phone) == 10

class Birthday(Field):
    def __init__(self,birthday):
         super().__init__(birthday)
         if not self.is_valid_birthday(birthday):
            raise ValueError(f"Invalid birthday format. Please use DD.MM.YYYY: {birthday}")
    def is_valid_birthday(self,birthday):
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
            return True
        except ValueError:
            return False


    
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    def add_phone(self,phone):
        self.phones.append(Phone(phone))
        return f"{phone} was added to {self.name.value}."
    def find_phone(self,phone):
        for number in self.phones:
            if number.value == phone:
                return number
        return None
    def remove_phone(self,phone):
        number = self.find_phone(phone)
        if number:
            self.phones.remove(number)
            return f"{phone} was successfully deleted"
        else:
            return f"Couldn't find {phone}"
    def edit_phone(self, old_phone,new_phone):
        number = self.find_phone(old_phone)
        if number:
            number.value = new_phone
    def add_birthday(self,birthday):
        self.birthday = Birthday(birthday)
    def show_birthday(self):
        return self.birthday.value if self.birthday else "Birthday not set"
    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, Phones: {phones_str}{birthday_str}"
    

class AddressBook(UserDict):
    def add_record(self,record):
        self.data[record.name.value] = record
    def find(self,name):
        return self.data.get(name)
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return f"{name} was successfully deleted"
        else:
            return f"Couldn't find {name}."
        
    def get_birthdays_per_week(self):
        today = datetime.today().date()
        in_a_week = today + timedelta(days=7)
        birthdays_this_week = defaultdict(list)
        for name, record in self.data.items():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)
                if today <= birthday_this_year <= in_a_week:
                    day_of_week = birthday_this_year.strftime("%A")
                    birthdays_this_week[day_of_week].append(name)
                
        return birthdays_this_week
    
    def save_to_file(self, file_name):
        with open(file_name, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, file_name):
        try:
            with open(file_name, 'rb') as file:
                self.data = pickle.load(file)
        except (FileNotFoundError, EOFError):
            print("File not found or empty file. Starting a new address book.")

def main():
    book = AddressBook()
    try:
        book.load_from_file('addressbook.pkl')  # Attempt to load existing data
    except (FileNotFoundError, EOFError):
        print("No existing address book found, starting a new one.")

    print("Welcome to the address book!")


    while True:
        command_line = input("Enter command: ")
        command_list = command_line.split()
        if not command_list:
            continue
        command = command_list[0].lower()
        
        if command == "add" and len(command_list) == 3:
            name, phone = command_list[1], command_list[2]
            if book.find(name):
                print(f"Contact {name} already exists. Use 'change' to update the phone number.")
            else:
                record = Record(name)
                record.add_phone(phone)
                book.add_record(record)
                print(f"Contact {name} with phone {phone} added.")
        elif command == "change" and len(command_list) == 3:
            name, new_phone = command_list[1], command_list[2]
            record = book.find(name)
            if record:
                record.edit_phone(record.phones[0].value, new_phone) 
                print(f"Phone for {name} changed to {new_phone}.")
            else:
                print(f"Contact {name} not found.")

        elif command == "phone" and len(command_list) == 2:
            name = command_list[1]
            record = book.find(name)
            if record:
                print(f"Phone for {name}: {', '.join(phone.value for phone in record.phones)}")
            else:
                print(f"Contact {name} not found.")

        elif command == "all":
            for name, record in book.items():
                print(record)

        elif command == "add-birthday" and len(command_list) == 3:
            name, birthday = command_list[1], command_list[2]
            record = book.find(name)
            if record:
                record.add_birthday(birthday)
                print(f"Birthday for {name} set to {birthday}.")
            else:
                print(f"Contact {name} not found.")

        elif command == "show-birthday" and len(command_list) == 2:
            name = command_list[1]
            record = book.find(name)
            if record and record.birthday:
                print(f"Birthday for {name} is on {record.birthday.value}.")
            else:
                print(f"Birthday for {name} not found or not set.")

        elif command == "birthdays":
            birthdays_this_week = book.get_birthdays_per_week()
            if birthdays_this_week:
                for day, names in birthdays_this_week.items():
                    print(f"{day}: {', '.join(names)}")
            else:
                print("No birthdays in the coming week.")

        elif command == "hello":
            print("Hello! How can I help you?")

        elif command in ["close", "exit"]:
            print("Goodbye!")
            break

        else:
            print("Unknown command. Please try again.")
        book.save_to_file('addressbook.pkl')  
        print("Your address book has been saved. Goodbye!")

if __name__ == "__main__":
    main()

 