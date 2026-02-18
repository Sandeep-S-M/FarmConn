from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('nursery', 'Nursery Owner'), ('farmer', 'Farmer')])
    # Basic location field for registration, detailed info later
    location = StringField('Location/Address', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please use a different email address.')

class NurseryProfileForm(FlaskForm):
    nursery_name = StringField('Nursery Name', validators=[DataRequired()])
    owner_name = StringField('Owner Name', validators=[DataRequired()])
    location = StringField('Address', validators=[DataRequired()])
    contact_details = StringField('Contact Details (Phone/Email)', validators=[DataRequired()])
    payment_methods = SelectField('Payment Methods', choices=[
        ('upi', 'UPI Payments'),
        ('cash', 'Cash'),
        ('both', 'Both Available[UPI/Cash]')
    ], validators=[DataRequired()])
    bio = TextAreaField('Description/Bio')
    submit = SubmitField('Update Profile')

class FarmerProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    location = StringField('Address', validators=[DataRequired()])
    contact_details = StringField('Contact Details (Phone/Email)', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class ProductForm(FlaskForm):
    name = StringField('Plant Name', validators=[DataRequired()])
    breed = StringField('Breed Name', validators=[DataRequired()])
    price = FloatField('Price per Plant (₹)', validators=[DataRequired()], render_kw={"step": "0.01", "placeholder": "Example: 15.50"})
    quantity = IntegerField('Quantity Available', validators=[DataRequired()])
    plant_age_days = IntegerField('Plant Age (Days)', validators=[DataRequired()])
    available_days = IntegerField('Available Until (Days)', validators=[DataRequired()])
    description = TextAreaField('Description')
    image_url = StringField('Image URL')
    submit = SubmitField('Add Plant')

class OrderForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired()])
    submit = SubmitField('Place Order')
