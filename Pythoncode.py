
import tkinter as tk  # Import the tkinter module for GUI
from tkinter import ttk  # Import themed tkinter widgets
from tkinter import messagebox  # Import messagebox for displaying messages
import datetime  # Import datetime module for date and time operations
import json  # Import json module for JSON handling

# Function to view transactions using GUI
transactions = {}
def view_transactions_using_GUI():
    # Define a class for the Finance Tracker GUI
    class FinanceTrackerGUI:
        def __init__(self, root, transactions):
            self.root = root
            self.transactions = transactions
            self.order = {}
            self.root.title("Personal Finance Tracker")
            self.create_widgets()

        def create_widgets(self):
            header_label = ttk.Label(self.root, text="Personal Finance Tracker", font=("Bahnschrift Condensed", 20),
                                     background="blue", foreground="white", anchor="center", justify="center")
            header_label.pack(fill="both")

            self.search_frame = tk.Frame(self.root, background="gray")
            self.search_frame.pack(fill="both")

            search_label = ttk.Label(self.search_frame, text="Search: ", background="black", foreground="white")
            search_label.grid(row=0, column=0, padx=5, pady=5)

            self.search_entry = ttk.Entry(self.search_frame)
            self.search_entry.grid(row=0, column=1, padx=5, pady=5)

            criteria_label = ttk.Label(self.search_frame, text="Search by: ", background="black", foreground="white")
            criteria_label.grid(row=0, column=2, padx=5, pady=5)

            self.search_criteria = ttk.Combobox(self.search_frame, values=["Amount", "Type", "Category", "Date"])
            self.search_criteria.set("Amount")
            self.search_criteria.grid(row=0, column=3, padx=5, pady=5)

            search_button = ttk.Button(self.search_frame, text="Search", command=self.perform_search, style="TButton")
            search_button.grid(row=0, column=4, padx=5, pady=5)

            reset_button = ttk.Button(self.search_frame, text="Reset", command=self.reset_search, style="TButton")
            reset_button.grid(row=0, column=5, padx=5, pady=5)

            self.tree_frame = ttk.Frame(self.root)
            self.tree_frame.pack(fill="both", expand=True)

            self.tree = ttk.Treeview(self.tree_frame, columns=("Amount", "Date", "Type", "Category",), show="headings")
            self.tree.heading("Amount", text="Amount", command=lambda: self.sort_by("Amount"))
            self.tree.heading("Date", text="Date", command=lambda: self.sort_by("Date"))
            self.tree.heading("Type", text="Type", command=lambda: self.sort_by("Type"))
            self.tree.heading("Category", text="Category", command=lambda: self.sort_by("Category"))
            self.tree.pack(side="left", fill="both", expand=True)

            scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
            scrollbar.pack(side="right", fill="y")
            self.tree.configure(yscrollcommand=scrollbar.set)

            self.summary_frame = tk.Frame(self.root, background="#DEB887")
            self.summary_frame.pack(fill="both")

            self.total_income_label = ttk.Label(self.summary_frame, text="", background="#DEB887", foreground="black")
            self.total_income_label.grid(row=0, column=0, padx=10)

            self.total_expense_label = ttk.Label(self.summary_frame, text="", background="#DEB887", foreground="black")
            self.total_expense_label.grid(row=0, column=1, padx=10)

            self.net_balance_label = ttk.Label(self.summary_frame, text="", background="#DEB887", foreground="black")
            self.net_balance_label.grid(row=0, column=2, padx=10)

            self.display_transactions()
            self.update_transaction_summary(self.transactions)

        def update_summary_labels(self, total_income, total_expense, net_balance):
            self.total_income_label.config(text=f"Total Income: ${total_income}")
            self.total_expense_label.config(text=f"Total Expense: ${abs(total_expense)}")
            self.net_balance_label.config(text=f"Net Balance: ${net_balance}")

        def perform_search(self):
            query = self.search_entry.get().strip().lower()
            criteria = self.search_criteria.get()

            if not query:
                messagebox.showerror("Error", "Please enter a search query.")
                return

            if criteria not in ["Amount", "Type", "Category", "Date"]:
                messagebox.showerror("Error", "Invalid search criteria.")
                return

            search_results = {}
            for category, transactions_list in self.transactions.items():
                if criteria == "Amount":
                    try:
                        query_float = float(query)
                    except ValueError:
                        messagebox.showerror("Error", "Amount must be a numeric value.")
                        return
                    search_results[category] = [transaction for transaction in transactions_list if
                                                query_float == transaction["amount"]]
                elif criteria == "Type":
                    if query.lower() not in ["income", "expense"]:
                        messagebox.showerror("Error", "Transaction type must be 'Income' or 'Expense'.")
                        return
                    search_results[category] = [transaction for transaction in transactions_list if
                                                query == transaction["type"].lower()]
                elif criteria == "Category":
                    search_results[category] = [transaction for transaction in transactions_list if
                                                query == category.lower()]
                elif criteria == "Date":
                    try:
                        datetime.datetime.strptime(query, '%Y-%m-%d')
                    except ValueError:
                        messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
                        return
                    search_results[category] = [transaction for transaction in transactions_list if
                                                query == transaction["date"].lower()]

            if any(search_results.values()):
                self.display_transactions(search_results)
            else:
                messagebox.showinfo("No Results", "No matching transactions found.")

        def reset_search(self):
            self.search_entry.delete(0, tk.END)
            self.search_criteria.set("Amount")
            self.display_transactions()

        def display_transactions(self, search_results=None):
            for item in self.tree.get_children():
                self.tree.delete(item)

            transactions_to_display = search_results or self.transactions

            for category, transactions_list in transactions_to_display.items():
                for transaction in transactions_list:
                    self.tree.insert("", "end", values=(transaction["amount"], transaction["date"],
                                                        transaction["type"], category))

        def update_transaction_summary(self, transactions):
            total_income = sum(transaction["amount"] for category, transactions_list in transactions.items() for
                               transaction in transactions_list if transaction["type"].lower() == "income")
            total_expense = sum(transaction["amount"] for category, transactions_list in transactions.items() for
                                transaction in transactions_list if transaction["type"].lower() == "expense")
            net_balance = total_income - total_expense

            self.update_summary_labels(total_income, total_expense, net_balance)

        def sort_by(self, column):
            if column in ["index"]:
                return

            current_order = self.order.get(column, "asc")
            reverse = current_order == "asc"

            items = self.tree.get_children("")
            if column == "Amount":
                key_func = lambda x: float(self.tree.set(x, column))
            elif column == "Date":
                key_func = lambda x: datetime.datetime.strptime(self.tree.set(x, column), '%Y-%m-%d')
            else:
                key_func = lambda x: self.tree.set(x, column)

            sorted_items = sorted(items, key=key_func, reverse=reverse)

            for i, item in enumerate(sorted_items):
                self.tree.move(item, "", i)

            # Reverse order for next click
            self.order[column] = "desc" if current_order == "asc" else "asc"

    def main():
        load_transactions("transactions.json")
        root = tk.Tk()
        app = FinanceTrackerGUI(root, transactions)
        root.mainloop()

    if __name__ == "__main__":
        main()


def load_transactions(filename):
    global transactions  # Declare transactions as global
    try:
        with open(filename, "r") as file:
            data = file.read()  # Read file contents
            if data.strip() == "":
                print(f"File {filename} is empty.")
                return {}
            transactions = json.loads(data)  # Load transactions from the JSON data
    except FileNotFoundError:
        transactions = {}   # If the file is not found, set transactions as an empty dictionary
    except json.JSONDecodeError:
        print(f"Error decoding JSON data in file {filename}.")
        transactions = {}  # Set transactions as an empty dictionary
    return transactions


def read_bulk_transactions_from_file(filename):
    transactions = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    transaction_type, category, amount_str, date = parts
                    amount = float(amount_str)
                    if category in transactions:
                        transactions[category].append(
                            {"amount": amount, "type": transaction_type.lower(), "date": date})
                    else:
                        transactions[category] = [{"amount": amount, "type": transaction_type.lower(), "date": date}]
            print("Transactions read from file successfully.")
            return transactions
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except ValueError:
        print("Error parsing transaction data. Please check the data format in the file.")



# Welcome message function


# Function to load transactions from file

def save_transactions(transactions):
    try:
        with open("transactions.json", "w") as file:
            json.dump(transactions, file, indent=1)  # Write transactions to JSON file
    except Exception as e:
        print(f"Error saving transactions: {e}")  # Print error message if saving fails




def main_menu():
    while True:
        print("\nPersonal Finance Tracker")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Update Transaction")
        print("4. Delete Transaction")
        print("5. Export Transactions to JSON File")
        print("6. Read Transactions in Bulk from Text File")
        print("7.Run GUI")
        print("8. Exit")

        choice = input("Enter your choice: ")  # Get user choice

        # Branch based on user choice
        if choice == "1":
            add_transaction()  # Add transaction
        elif choice == "2":
            view_transactions(transactions)  # View transactions
        elif choice == "3":
            update_transaction()  # Update transaction
        elif choice == "4":
            delete_transaction(transactions)  # Delete transaction
        elif choice == "5":
            export_transactions_to_file()  # Export transactions to file
        elif choice == "6":
            filename = input("Enter the name of the text file: ")
            bulk_transactions = read_bulk_transactions_from_file(filename)
            if bulk_transactions:
                transactions.update(bulk_transactions)
        elif choice == "6":
            display_summary(transactions)  # Display summary of transactions
        elif choice == "7":
            if transactions:  # Check if transactions dictionary has data
                view_transactions_using_GUI()
            else:
                print("No transactions loaded yet. Please add transactions or load from a file.")
            # Pass transactions to GUI function
        elif choice == "8":
            save_transactions(transactions)  # Save transactions to file
            print("Transactions saved successfully")
            print("Exiting program.")
            break  # Exit program
        else:
            print("Invalid choice. Please try again.")  # Invalid choice

# Function to add transaction
# Function to add transaction
def add_transaction():
    amount = get_valid_amount()  # Get valid amount
    transaction_type = get_valid_transaction_type()  # Get valid transaction type
    category = get_valid_transaction_category()  # Get valid transaction category
    date = get_valid_date()  # Get valid date
    add_transaction_to_dictionary( transaction_type, category, amount, date)  # Add transaction
    save_transactions(transactions)  # Save transactions to file



# Function to add transaction to dictionary
def add_transaction_to_dictionary(transaction_type, category, amount, date):
    new_transaction = {"type": transaction_type, "amount": amount, "date": date}  # New transaction
    if category not in transactions:
        transactions[category] = [new_transaction]
    else:
        transactions[category].append(new_transaction)

# Function to view transaction
def view_transactions(transactions):
    if transactions:
        for category, transaction_list in transactions.items():
            print(f"\nCategory: {category}")
            for index, transaction in enumerate(transaction_list, start=1):
                print(
                    f"{index}. Amount: ${transaction['amount']}, Type: {transaction['type'].title()}, Date: {transaction['date']}")
    else:
        print("No transactions available.")


# Function to update a transaction
def update_transaction():
    view_transactions(transactions)
    category = input("Enter the category of the transaction you want to update: ")

    if category in transactions:
        transaction_list = transactions[category]
        index = get_valid_transaction_index(len(transaction_list))
        transaction = transaction_list[index - 1]  # Adjust index to 0-based

        print("\nCurrent Transaction Details:")
        print(f"1. Amount: ${transaction['amount']}")
        print(f"2. Type: {transaction['type'].title()}")
        print(f"3. Date: {transaction['date']}")

        field = int(input("Enter the number corresponding to the field you want to update: "))

        if field == 1:
            transaction['amount'] = get_valid_amount()
        elif field == 2:
            transaction['type'] = get_valid_transaction_type().lower()
        elif field == 3:
            transaction['date'] = get_valid_date()

        # Update the transaction in the transactions dictionary
        transactions[category][index - 1] = transaction

        # Save the updated transactions to the JSON file
        save_transactions(transactions)

        print("Transaction updated successfully.")
    else:
        print("Category not found.")


def display_transactions_from_file(): # Function that displays transactions from file
    print("\nTransactions from file:")
    for expense_type, transactions_list in transactions.items():
        for transaction in transactions_list:
            print(f"Expense Type: {expense_type}, Amount: {transaction['amount']}, Date: {transaction['date']}")
    print("These Transactions saved successfully")
    save_transactions(transactions)
# Function to update transaction field


# Function to delete transaction
def delete_transaction(transactions):
    view_transactions(transactions)
    category = input("Enter the category of the transaction you want to delete: ")

    if category in transactions:
        transaction_list = transactions[category]
        index = get_valid_transaction_index(len(transaction_list))
        del transaction_list[index - 1]  # Adjust index to 0-based
        print("Transaction deleted successfully.")
    else:
        print("Category not found.")
# Function to display summary
def display_summary(transactions):
    total_income = 0
    total_expense = 0
    for expense_type, transactions_list in transactions.items():
        for transaction in transactions_list:
            total_amount = transaction["amount"]
            if total_amount > 0:
                if transaction["type"] == "income":
                    print("Summary of incomes")
                    date = transaction["date"]
                    if len(transactions_list) == 1:
                        print(f"You received ${total_amount} on {date} as {expense_type}.")
                    else:
                        print(
                            f"You received ${total_amount} between {transactions_list[0]['date']} and {transactions_list[-1]['date']} as {expense_type}.")
                    total_income += total_amount
                else:
                    if len(transactions_list) == 1:
                        print("Summary of Expenses")
                        date = transaction["date"]
                        print(f"You spent ${total_amount} on {expense_type}, on {date}.")
                    else:
                        print(
                            f"You spent ${total_amount} on {expense_type}, between {transactions_list[0]['date']} and {transactions_list[-1]['date']}.")
                    total_expense += total_amount

    net_balance = total_income - total_expense

    print("\nSummary:")
    print(f"Total Income: ${total_income}")
    print(f"Total Expense: ${total_expense}")
    print(f"Net Balance: ${net_balance}")


#Funtions that validate user inputs
def get_valid_file_name():  # Function that gets valid file name from user
    while True:  # Loop until a valid file name is entered
        filename = input("Enter file name (Do not include .txt extension): ")
        if any(characters in r'\/.,:*?"<>|' for characters in filename):
            print("Error! File name cannot contain symbols like . / \\ \" : , . * ? < > |")
        else:
            filename += '.txt'  # Append '.txt' if not already included
            if filename == '.txt':  # Check if the filename is only '.txt'
                print("Error: Filename cannot be empty.")
            else:
                return filename  # Return the valid filename


def export_transactions_to_file(): # Function that exports transactions to file
    filename = get_valid_file_name()
    try:
        with open(filename, "w") as file:
            for category, transactions_list in transactions.items():
                for transaction in transactions_list:
                    file.write(f"{transaction['type']},{category},{transaction['amount']},{transaction['date']}\n")
        print("Transactions exported successfully.")
    except Exception as e: # Handle the exceptions that occur during the process
        print(f"Error exporting transactions: {e}")

# Function to get valid amount
def get_valid_transaction_index(max_index):
    while True:
        try:
            index = int(input("Enter the index of the transaction you want to update: "))
            if index < 1 or index > max_index:
                print(f"Error! Index must be between 1 and {max_index}. Please try again.")
            else:
                return index
        except ValueError:
            print("Error! Please enter a valid index.")

def get_valid_amount():
    while True:
        try:
            amount = float(input("Enter transaction amount: "))
            if amount <= 0:
                print("Error! Amount must be a positive number. Please try again.")
            else:
                return amount
        except ValueError:
            print("Error! Please enter a valid numeric amount. Please try again.")

# Function to get valid transaction type
def get_valid_transaction_type():
    while True:
        transaction_type = input("Enter transaction type (Income/Expense): ")
        if transaction_type.lower() not in ['income', 'expense']:
            print("Error! Type must be 'Income' or 'Expense'. Please try again.")
        else:
            return transaction_type

# Function to get valid transaction category
def get_valid_transaction_category():
    while True:
        transaction_category = input("Enter transaction category: ")
        if transaction_category.isalpha():
            return transaction_category
        else:
            print("Error! Transaction category must contain only letters (no numbers or special characters). Please try again.")

# Function to get valid date
def get_valid_date():
    while True:
        date = input("Enter transaction date (YYYY-MM-DD): ")
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
            return date
        except ValueError:
            print("Error! Invalid date. Please try again.")

if __name__ == "__main__":
    load_transactions("transactions.json")  # Call function that loads data on startup
    main_menu()  # Call function that displays main menu

