from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length, Email
from flask_babel import lazy_gettext


class PasswordResetForm(FlaskForm):
    email = StringField(lazy_gettext("Email"), validators=[DataRequired(), Length(1, 64), Email()])
    email_sent = BooleanField("email_sent", validators=[])
