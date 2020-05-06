from flask import Flask, render_template
from data_tools import get_profile_from_json_by_id, get_profile_goals, get_free_profile_hours, \
    WEEKDAYS, write_lesson_to_json, get_goals_for_request_form, read_json, TIMES, write_request_to_json, \
    get_profiles_by_goal, get_random_profiles_from_file, ICONS
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY', 'my-super-secret-phrase-I-dont-tell-this-to-nobody')
GOALS_JSON_PATH = os.getenv('GOALS_JSON_PATH', 'goals.json')
TEACHERS_JSON_PATH = os.getenv('TEACHERS_JSON_PATH', 'teachers.json')
REQUESTS_JSON_PATH = os.getenv('REQUESTS_JSON_PATH', 'request.json')
PROFILE_NUMBERS_PER_MAIN_PAGE = int(os.getenv('PROFILE_NUMBERS_PER_MAIN_PAGE', 6))
GOALS = get_goals_for_request_form(GOALS_JSON_PATH)


@app.route('/')
def render_main():
    profiles = get_random_profiles_from_file(PROFILE_NUMBERS_PER_MAIN_PAGE, TEACHERS_JSON_PATH)
    goals = read_json(GOALS_JSON_PATH)
    return render_template('index.html', profiles=profiles, goals=goals, icons=ICONS)


@app.route('/goals/<goal>/')
def render_goal(goal):
    goals = read_json(GOALS_JSON_PATH)
    profiles = get_profiles_by_goal(goal, TEACHERS_JSON_PATH)
    icon = ICONS[goal]
    return render_template('goal.html', goal=goals[goal].lower(), profiles=profiles, icon=icon)


@app.route('/profiles/<int:profile_id>/')
def render_profile(profile_id):
    profile = get_profile_from_json_by_id(profile_id, TEACHERS_JSON_PATH)
    goals = get_profile_goals(profile, GOALS_JSON_PATH)
    free_hours = get_free_profile_hours(profile)
    return render_template('profile.html', profile=profile, goals=goals, free_hours=free_hours, weekday=WEEKDAYS)


class RequestForm(FlaskForm):
    goal = RadioField('Какая цель занятий?', choices=GOALS, default=GOALS[0][0], validators=[InputRequired()])
    time = RadioField('Сколько времени есть?', choices=TIMES, default=TIMES[0][0], validators=[InputRequired()])
    name = StringField('Вас зовут', [InputRequired(message="Введите что-нибудь")])
    phone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь"),
                                        Length(min=7, message="Неправильный номер")])
    submit = SubmitField('Найдите мне преподавателя')


@app.route('/request/')
def render_request():
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=["POST"])
def render_request_done():
    form = RequestForm()
    if form.validate():
        goals = read_json(GOALS_JSON_PATH)
        goal = form.goal.data
        time = form.time.data
        name = form.name.data
        phone = form.phone.data
        write_request_to_json(goal, time, name, phone, REQUESTS_JSON_PATH)
        return render_template('request_done.html', goal=goals[goal], time=time, name=name, phone=phone)
    return 'Данные не получены '


class BookingForm(FlaskForm):
    weekday = HiddenField('День недели', [InputRequired(message="Введите что-нибудь")])
    time = HiddenField('Время', [InputRequired(message="Введите что-нибудь")])
    teacher = HiddenField('Учитель', [InputRequired(message="Введите что-нибудь")])
    name = StringField('Вас зовут', [InputRequired(message="Введите что-нибудь")])
    phone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь"),
                                        Length(min=7, message="Неправильный номер")])
    submit = SubmitField('Записаться на пробный урок')


@app.route('/booking/<int:profile_id>/<weekday>/<time>/')
def render_booking(profile_id, weekday, time):
    profile = get_profile_from_json_by_id(profile_id, TEACHERS_JSON_PATH)
    form = BookingForm()
    form.weekday.default = weekday
    form.time.default = time
    form.teacher.default = profile_id
    return render_template('booking.html', profile=profile, weekday=WEEKDAYS[weekday], form=form)


@app.route('/booking_done/', methods=["POST"])
def render_booking_done():
    form = BookingForm()
    if form.validate():
        name = form.name.data
        time = form.time.data
        weekday = form.weekday.data
        teacher_id = form.teacher.data
        phone = form.phone.data
        write_lesson_to_json(teacher_id, weekday, time, TEACHERS_JSON_PATH)
        return render_template('booking_done.html', name=name, time=time, weekday=WEEKDAYS[weekday], phone=phone)
    return 'Данные не получены '


if __name__ == '__main__':
    app.run()
