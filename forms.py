from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_wtf import FlaskForm
from models import User


class PostForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    content = TextAreaField('Conteúdo', validators=[DataRequired()])
    submit = SubmitField('Publicar')


class RegistrationForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[
                           DataRequired(), Length(min=2, max=150)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar senha', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar-se')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Esse nome de usuário já está em uso. Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Esse e-mail já está registrado.')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')


class PostForm(FlaskForm):
    title = StringField('Título', validators=[
                        DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Conteúdo', validators=[DataRequired()])
    submit = SubmitField('Enviar')
