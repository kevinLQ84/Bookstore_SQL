from flask import Flask
from flask_wtf import FlaskForm
from wtforms.fields import DateField
#from wtforms.fields.html5 import DateField
from wtforms import BooleanField, SubmitField,IntegerField, StringField, SelectField, RadioField, PasswordField, DecimalField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import InputRequired, NumberRange, EqualTo, Optional

class OrderForm(FlaskForm):
    customer_id = StringField("Customer: ")
    date = DateField("Date of purchase: ", validators=[Optional()])
    submit = SubmitField("Search")


class BookForm(FlaskForm):
    amount=IntegerField("Amount:", default=1, validators=[NumberRange(-100,100)])
    submit = SubmitField("Add To Cart")
    quantity=IntegerField("Quantity:", default=1, validators=[NumberRange(-100,100)])

    #editing book values
    confirm= SubmitField("Confirm Changes")
    delete_entry=BooleanField("Delete Book from database?")
    edit_price=DecimalField("Edit Price:")
   
class AddBookForm(FlaskForm):
    book_author=SelectField("Author: ")
    book_title=StringField("Book Title: ", validators=[InputRequired()])
    book_price=DecimalField("Price: ", validators=[InputRequired(), NumberRange(0,9999)])
    book_genre=SelectMultipleField("Genres: ", validators=[InputRequired()])
    book_desc=TextAreaField("Description", validators=[InputRequired()])
    submit=SubmitField("Submit")

class RegistrationForm(FlaskForm):
    user_id = StringField("Username:", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Confirm password", 
        validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    user_id = StringField("Username:", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    #password 2 not needed
    submit = SubmitField("Submit")

class AccountForm(FlaskForm):
    #user_ids
    new_user_id = StringField("Change Username: ")
    #passwords
    old_password = PasswordField("Password: ", validators=[InputRequired()])
    new_password = PasswordField("New Password")
    submit = SubmitField("Confirm Changes")

class SearchForm(FlaskForm):
    genre_search=SelectField("Genre: ")
    title_search=StringField("Title: ")
    search = SubmitField("Search")

class CartForm(FlaskForm):
    checkout = SubmitField("Checkout")

class CheckoutForm(FlaskForm):
    pay_now = SubmitField("Pay Now")