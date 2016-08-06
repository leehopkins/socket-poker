import os
import redis
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError

def session_check(form, field):
    r = redis.from_url(os.environ.get('REDIS_URL'))
    if len(field.data) > 0 and not r.exists('session:' + field.data):
        raise ValidationError('Session ' + field.data + ' does not exist, leave field blank to create a new session.')

class CreateSessionForm(Form):
    session_id = StringField('Session Id', validators=[session_check])
    username = StringField('Display Name', validators=[DataRequired(message="required")])
    role = SelectField('Role', choices=[('player', 'player'), ('observer', 'observer'), ('admin', 'admin')], validators=[DataRequired(message="required")])
    submit = SubmitField('Create or Join Session')
