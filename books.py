import streamlit as st
import sqlite3
from datetime import datetime

# ---------- DATABASE SETUP ----------
conn = sqlite3.connect("library.db", check_same_thread=False)
c = conn.cursor()

def create_tables():
    c.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        available INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS borrow_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        borrower TEXT,
        borrow_date TEXT,
        return_date TEXT
    )
    """)
    conn.commit()

create_tables()


# ---------- FUNCTIONS ----------
def add_book(title, author):
    c.execute(
        "INSERT INTO books (title, author, available) VALUES (?, ?, 1)",
        (title, author),
    )
    conn.commit()


def get_books():
    c.execute("SELECT * FROM books")
    return c.fetchall()


def get_available_books():
    c.execute("SELECT * FROM books WHERE available=1")
    return c.fetchall()


def borrow_book(book_id, borrower):
    borrow_date = datetime.now().strftime("%Y-%m-%d")

    c.execute(
        "INSERT INTO borrow_records (book_id, borrower, borrow_date, return_date) VALUES (?, ?, ?, NULL)",
        (book_id, borrower, borrow_date),
    )

    c.execute("UPDATE books SET available=0 WHERE id=?", (book_id,))
    conn.commit()


def return_book(book_id):
    return_date = datetime.now().strftime("%Y-%m-%d")

    c.execute(
        "UPDATE borrow_records SET return_date=? WHERE book_id=? AND return_date IS NULL",
        (return_date, book_id),
    )

    c.execute("UPDATE books SET available=1 WHERE id=?", (book_id,))
    conn.commit()


def get_borrowed_books():
    c.execute("""
    SELECT books.id, books.title, borrow_records.borrower, borrow_records.borrow_date
    FROM books
    JOIN borrow_records ON books.id = borrow_records.book_id
    WHERE borrow_records.return_date IS NULL
    """)
    return c.fetchall()


# ---------- STREAMLIT UI ----------
st.title("📚 Book Borrowing Management System")

menu = ["Add Book", "View Books", "Borrow Book", "Return Book", "Borrow Records"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------- ADD BOOK ----------
if choice == "Add Book":
    st.subheader("Add New Book")

    title = st.text_input("Book Title")
    author = st.text_input("Author")

    if st.button("Add Book"):
        if title and author:
            add_book(title, author)
            st.success("Book added successfully!")
        else:
            st.warning("Please fill all fields.")


# ---------- VIEW BOOKS ----------
elif choice == "View Books":
    st.subheader("All Books")

    books = get_books()

    if books:
        for book in books:
            status = "Available" if book[3] == 1 else "Borrowed"
            st.write(f"ID: {book[0]} | {book[1]} by {book[2]} — {status}")
    else:
        st.info("No books available.")


# ---------- BORROW BOOK ----------
elif choice == "Borrow Book":
    st.subheader("Borrow a Book")

    books = get_available_books()

    if books:
        book_dict = {f"{book[1]} by {book[2]} (ID {book[0]})": book[0] for book in books}
        selected_book = st.selectbox("Select Book", list(book_dict.keys()))
        borrower = st.text_input("Borrower Name")

        if st.button("Borrow"):
            if borrower:
                borrow_book(book_dict[selected_book], borrower)
                st.success("Book borrowed successfully!")
            else:
                st.warning("Enter borrower name.")
    else:
        st.info("No books available for borrowing.")


# ---------- RETURN BOOK ----------
elif choice == "Return Book":
    st.subheader("Return a Book")

    borrowed = get_borrowed_books()

    if borrowed:
        book_dict = {f"{b[1]} borrowed by {b[2]} (ID {b[0]})": b[0] for b in borrowed}
        selected_book = st.selectbox("Select Book", list(book_dict.keys()))

        if st.button("Return"):
            return_book(book_dict[selected_book])
            st.success("Book returned successfully!")
    else:
        st.info("No borrowed books.")


# ---------- BORROW RECORDS ----------
elif choice == "Borrow Records":
    st.subheader("Currently Borrowed Books")

    borrowed = get_borrowed_books()

    if borrowed:
        for b in borrowed:
            st.write(f"{b[1]} borrowed by {b[2]} on {b[3]}")
    else:
        st.info("No active borrow records.")
