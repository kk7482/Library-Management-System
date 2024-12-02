from flask import Flask, render_template, flash, redirect, url_for, request
from flask_mysqldb import MySQL
from wtforms import Form, validators, StringField, FloatField, IntegerField, DateField, SelectField
from datetime import datetime
import MySQLdb
import urllib
import requests

# Creating instance of flask app
app = Flask(__name__)

# MySQL setup
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'librarydb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# Homepage
@app.route('/')
def index():
    return render_template('home.html')


# Members
@app.route('/members')
def members():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM members")
    members = cur.fetchall()

    if result > 0:
        return render_template('members.html', members=members)
    else:
        msg = 'No Members Found'
        return render_template('members.html', warning=msg)

    cur.close()


# Details of Member by ID
@app.route('/member/<string:id>')
def viewMember(id):
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM members WHERE id=%s", [id])
    member = cur.fetchone()

    if result > 0:
        return render_template('view_member_details.html', member=member)
    else:
        msg = 'This Member Does Not Exist'
        return render_template('view_member_details.html', warning=msg)

    cur.close()


# Defining Add-Member-Form
class AddMember(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.length(min=6, max=50)])


# Adding Member
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    form = AddMember(request.form)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO members (name, email) VALUES (%s, %s)", (name, email))

        mysql.connection.commit()

        cur.close()

        flash("New Member Added", "success")

        return redirect(url_for('members'))

    return render_template('add_member.html', form=form)


# Edit Member by ID
@app.route('/edit_member/<string:id>', methods=['GET', 'POST'])
def edit_member(id):
    form = AddMember(request.form)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data

        cur = mysql.connection.cursor()

        cur.execute(
            "UPDATE members SET name=%s, email=%s WHERE id=%s", (name, email, id))

        mysql.connection.commit()

        cur.close()

        flash("Member Updated", "success")

        return redirect(url_for('members'))


    cur2 = mysql.connection.cursor()
    result = cur2.execute("SELECT name,email FROM members WHERE id=%s", [id])
    member = cur2.fetchone()
    return render_template('edit_member.html', form=form, member=member)



@app.route('/delete_member/<string:id>', methods=['POST'])
def delete_member(id):

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM members WHERE id=%s", [id])

        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e)
        flash("Member could not be deleted", "danger")
        flash(str(e), "danger")

        return redirect(url_for('members'))
    finally:
        cur.close()

    flash("Member Deleted", "success")

    return redirect(url_for('members'))


# Books
@app.route('/books')
def books():
    
    cur = mysql.connection.cursor()

    result = cur.execute(
        "SELECT id,title,author,total_quantity,available_quantity,rented_count FROM books")
    books = cur.fetchall()

    if result > 0:
        return render_template('books.html', books=books)
    else:
        msg = 'No Books Found'
        return render_template('books.html', warning=msg)

    cur.close()


# View Details of Book by ID
@app.route('/book/<string:id>')
def viewBook(id):
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM books WHERE id=%s", [id])
    book = cur.fetchone()

    if result > 0:
        return render_template('view_book_details.html', book=book)
    else:
        msg = 'This Book Does Not Exist'
        return render_template('view_book_details.html', warning=msg)

    cur.close()


# Define Add-Book-Form
class AddBook(Form):
    id = StringField('Book ID', [validators.Length(min=1, max=11)])
    title = StringField('Title', [validators.Length(min=2, max=255)])
    author = StringField('Author(s)', [validators.Length(min=2, max=255)])
    average_rating = FloatField(
        'Average Rating', [validators.NumberRange(min=0, max=5)])
    isbn = StringField('ISBN', [validators.Length(min=10, max=10)])
    isbn13 = StringField('ISBN13', [validators.Length(min=13, max=13)])
    language_code = StringField('Language', [validators.Length(min=1, max=3)])
    num_pages = IntegerField('No. of Pages', [validators.NumberRange(min=1)])
    ratings_count = IntegerField(
        'No. of Ratings', [validators.NumberRange(min=0)])
    text_reviews_count = IntegerField(
        'No. of Text Reviews', [validators.NumberRange(min=0)])
    publication_date = DateField(
        'Publication Date', [validators.InputRequired()])
    publisher = StringField('Publisher', [validators.Length(min=2, max=255)])
    total_quantity = IntegerField(
        'Total No. of Books', [validators.NumberRange(min=1)])


# Add Book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = AddBook(request.form)

    if request.method == 'POST' and form.validate():

        cur = mysql.connection.cursor()

        result = cur.execute(
            "SELECT id FROM books WHERE id=%s", [form.id.data])
        book = cur.fetchone()
        if(book):
            error = 'Book with that ID already exists'
            return render_template('add_book.html', form=form, error=error)

        cur.execute("INSERT INTO books (id,title,author,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
            form.id.data,
            form.title.data,
            form.author.data,
            form.average_rating.data,
            form.isbn.data,
            form.isbn13.data,
            form.language_code.data,
            form.num_pages.data,
            form.ratings_count.data,
            form.text_reviews_count.data,
            form.publication_date.data,
            form.publisher.data,
            form.total_quantity.data,
            form.total_quantity.data
        ])

        mysql.connection.commit()

        cur.close()

        flash("New Book Added", "success")

        return redirect(url_for('books'))

    return render_template('add_book.html', form=form)


# Define Import-Books-Form
class ImportBooks(Form):
    no_of_books = IntegerField('No. of Books*', [validators.NumberRange(min=1)])
    quantity_per_book = IntegerField(
        'Quantity Per Book*', [validators.NumberRange(min=1)])
    title = StringField(
        'Title', [validators.Optional(), validators.Length(min=2, max=255)])
    author = StringField(
        'Author(s)', [validators.Optional(), validators.Length(min=2, max=255)])
    isbn = StringField(
        'ISBN', [validators.Optional(), validators.Length(min=10, max=10)])
    publisher = StringField(
        'Publisher', [validators.Optional(), validators.Length(min=2, max=255)])


# Import Books from Frappe API
@app.route('/import_books', methods=['GET', 'POST'])
def import_books():
    form = ImportBooks(request.form)

    if request.method == 'POST' and form.validate():
        url = 'https://frappe.io/api/method/frappe-library?'
        parameters = {'page': 1}
        if form.title.data:
            parameters['title'] = form.title.data
        if form.author.data:
            parameters['author'] = form.author.data
        if form.isbn.data:
            parameters['isbn'] = form.isbn.data
        if form.publisher.data:
            parameters['publisher'] = form.publisher.data

        cur = mysql.connection.cursor()

        no_of_books_imported = 0
        repeated_book_ids = []
        while(no_of_books_imported != form.no_of_books.data):
            r = requests.get(url + urllib.parse.urlencode(parameters))
            res = r.json()
            if not res['message']:
                break

            for book in res['message']:
                result = cur.execute(
                    "SELECT id FROM books WHERE id=%s", [book['bookID']])
                book_found = cur.fetchone()
                if(not book_found):
                    cur.execute("INSERT INTO books (id,title,author,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                        book['bookID'],
                        book['title'],
                        book['authors'],
                        book['average_rating'],
                        book['isbn'],
                        book['isbn13'],
                        book['language_code'],
                        book['  num_pages'],
                        book['ratings_count'],
                        book['text_reviews_count'],
                        book['publication_date'],
                        book['publisher'],
                        form.quantity_per_book.data,
                        form.quantity_per_book.data
                    ])
                    no_of_books_imported += 1
                    if no_of_books_imported == form.no_of_books.data:
                        break
                else:
                    repeated_book_ids.append(book['bookID'])
            parameters['page'] = parameters['page'] + 1

        mysql.connection.commit()

        cur.close()

        msg = str(no_of_books_imported) + "/" + \
            str(form.no_of_books.data) + " books have been imported. "
        msgType = 'success'
        if no_of_books_imported != form.no_of_books.data:
            msgType = 'warning'
            if len(repeated_book_ids) > 0:
                msg += str(len(repeated_book_ids)) + \
                    " books were found with already exisiting IDs."
            else:
                msg += str(form.no_of_books.data - no_of_books_imported) + \
                    " matching books were not found."

        flash(msg, msgType)

        return redirect(url_for('books'))

    return render_template('import_books.html', form=form)


# Edit Book by ID
@app.route('/edit_book/<string:id>', methods=['GET', 'POST'])
def edit_book(id):
    form = AddBook(request.form)

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM books WHERE id=%s", [id])
    book = cur.fetchone()

    if request.method == 'POST' and form.validate():
        if(form.id.data != id):
            result = cur.execute(
                "SELECT id FROM books WHERE id=%s", [form.id.data])
            book = cur.fetchone()
            if(book):
                error = 'Book with that ID already exists'
                return render_template('edit_book.html', form=form, error=error, book=form.data)

        available_quantity = book['available_quantity'] + \
            (form.total_quantity.data - book['total_quantity'])

        cur.execute("UPDATE books SET id=%s,title=%s,author=%s,average_rating=%s,isbn=%s,isbn13=%s,language_code=%s,num_pages=%s,ratings_count=%s,text_reviews_count=%s,publication_date=%s,publisher=%s,total_quantity=%s,available_quantity=%s WHERE id=%s", [
            form.id.data,
            form.title.data,
            form.author.data,
            form.average_rating.data,
            form.isbn.data,
            form.isbn13.data,
            form.language_code.data,
            form.num_pages.data,
            form.ratings_count.data,
            form.text_reviews_count.data,
            form.publication_date.data,
            form.publisher.data,
            form.total_quantity.data,
            available_quantity,
            id])

        mysql.connection.commit()

        cur.close()

        flash("Book Updated", "success")

        return redirect(url_for('books'))

    return render_template('edit_book.html', form=form, book=book)


# Delete Book by ID
@app.route('/delete_book/<string:id>', methods=['POST'])
def delete_book(id):
    cur = mysql.connection.cursor()

    try:
        cur.execute("DELETE FROM books WHERE id=%s", [id])

        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:

        print(e)
        flash("Book could not be deleted", "danger")
        flash(str(e), "danger")

        return redirect(url_for('books'))
    finally:
        cur.close()

    flash("Book Deleted", "success")

    return redirect(url_for('books'))


# Transactions
@app.route('/transactions')
def transactions():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM transactions")
    transactions = cur.fetchall()

    for transaction in transactions:
        for key, value in transaction.items():
            if value is None:
                transaction[key] = "-"

    if result > 0:
        return render_template('transactions.html', transactions=transactions)
    else:
        msg = 'No Transactions Found'
        return render_template('transactions.html', warning=msg)

    cur.close()


# Define Issue-Book-Form
class IssueBook(Form):
    book_id = SelectField('Book ID', choices=[])
    member_id = SelectField('Member ID', choices=[])
    per_day_fee = FloatField('Per Day Renting Fee', [
                             validators.NumberRange(min=1)])


# Issue Book
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    form = IssueBook(request.form)

    cur = mysql.connection.cursor()

   
    cur.execute("SELECT id, title FROM books")
    books = cur.fetchall()
    book_ids_list = []
    for book in books:
        t = (book['id'], book['title'])
        book_ids_list.append(t)

    cur.execute("SELECT id, name FROM members")
    members = cur.fetchall()
    member_ids_list = []
    for member in members:
        t = (member['id'], member['name'])
        member_ids_list.append(t)

    form.book_id.choices = book_ids_list
    form.member_id.choices = member_ids_list

    if request.method == 'POST' and form.validate():

        cur.execute("SELECT available_quantity FROM books WHERE id=%s", [
                    form.book_id.data])
        result = cur.fetchone()
        available_quantity = result['available_quantity']

        if(available_quantity < 1):
            error = 'No copies of this book are availabe to be rented'
            return render_template('issue_book.html', form=form, error=error)

        cur.execute("INSERT INTO transactions (book_id,member_id,per_day_fee) VALUES (%s, %s, %s)", [
            form.book_id.data,
            form.member_id.data,
            form.per_day_fee.data,
        ])

        cur.execute(
            "UPDATE books SET available_quantity=available_quantity-1, rented_count=rented_count+1 WHERE id=%s", [form.book_id.data])

        mysql.connection.commit()

        cur.close()

        flash("Book Issued", "success")

        return redirect(url_for('transactions'))

    return render_template('issue_book.html', form=form)


class ReturnBook(Form):
    amount_paid = FloatField('Amount Paid', [validators.NumberRange(min=0)])


@app.route('/return_book/<string:transaction_id>', methods=['GET', 'POST'])
def return_book(transaction_id):
    form = ReturnBook(request.form)

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM transactions WHERE id=%s", [transaction_id])
    transaction = cur.fetchone()

    date = datetime.now()
    difference = date - transaction['borrowed_on']
    difference = difference.days
    total_charge = difference * transaction['per_day_fee']

    if request.method == 'POST' and form.validate():

        transaction_debt = total_charge - form.amount_paid.data

        cur.execute("SELECT outstanding_debt,amount_spent FROM members WHERE id=%s", [
                    transaction['member_id']])
        result = cur.fetchone()
        outstanding_debt = result['outstanding_debt']
        amount_spent = result['amount_spent']
        if(outstanding_debt + transaction_debt > 500):
            error = 'Outstanding Debt Cannot Exceed Rs.500'
            return render_template('return_book.html', form=form, error=error)

        cur.execute("UPDATE transactions SET returned_on=%s,total_charge=%s,amount_paid=%s WHERE id=%s", [
            date,
            total_charge,
            form.amount_paid.data,
            transaction_id
        ])

        cur.execute("UPDATE members SET outstanding_debt=%s, amount_spent=%s WHERE id=%s", [
            outstanding_debt+transaction_debt,
            amount_spent+form.amount_paid.data,
            transaction['member_id']
        ])

        cur.execute(
            "UPDATE books SET available_quantity=available_quantity+1 WHERE id=%s", [transaction['book_id']])

        mysql.connection.commit()

        cur.close()

        flash("Book Returned", "success")

        return redirect(url_for('transactions'))

    return render_template('return_book.html', form=form, total_charge=total_charge, difference=difference, transaction=transaction)


# Reports
@app.route('/reports')
def reports():
    cur = mysql.connection.cursor()

    result_members = cur.execute(
        "SELECT id,name,amount_spent FROM members ORDER BY amount_spent DESC LIMIT 5")
    members = cur.fetchall()

    result_books = cur.execute(
        "SELECT id,title,author,total_quantity,available_quantity,rented_count FROM books ORDER BY rented_count DESC LIMIT 5")
    books = cur.fetchall()

    msg = ''
    if result_members <= 0:
        msg = 'No Members Found. '
    if result_books <= 0:
        msg = msg+'No Books Found'
    return render_template('reports.html', members=members, books=books, warning=msg)

    cur.close()


# Define Search-Form
class SearchBook(Form):
    title = StringField('Title', [validators.Length(min=2, max=255)])
    author = StringField('Author(s)', [validators.Length(min=2, max=255)])


# Search
@app.route('/search_book', methods=['GET', 'POST'])
def search_book():
    form = SearchBook(request.form)

    if request.method == 'POST' and form.validate():
        cur = mysql.connection.cursor()
        title = '%'+form.title.data+'%'
        author = '%'+form.author.data+'%'
        result = cur.execute(
            "SELECT * FROM books WHERE title LIKE %s OR author LIKE %s", [title, author])
        books = cur.fetchall()
        cur.close()

        if result <= 0:
            msg = 'No Results Found'
            return render_template('search_book.html', form=form, warning=msg)

        flash("Results Found", "success")
        return render_template('search_book.html', form=form, books=books)

    return render_template('search_book.html', form=form)


if __name__ == '__main__':
    app.secret_key = "secret"
    app.run(debug=True)
