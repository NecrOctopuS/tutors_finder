from flask import Flask, render_template
from data_tools import get_profile_from_json_by_id, get_profile_goals, get_free_profile_hours, \
    WEEKDAYS, write_lesson_to_json, get_goals_for_request_form, read_json, write_request_to_json, \
    get_profiles_by_goal, get_random_profiles_from_file, ICONS
from forms import RequestForm, BookingForm
from environs import Env

app = Flask(__name__)
env = Env()
env.read_env()

app.secret_key = env.str('SECRET_KEY', 'my-super-secret-phrase-I-dont-tell-this-to-nobody')
GOALS_JSON_PATH = env.str('GOALS_JSON_PATH', 'goals.json')
TEACHERS_JSON_PATH = env.str('TEACHERS_JSON_PATH', 'teachers.json')
REQUESTS_JSON_PATH = env.str('REQUESTS_JSON_PATH', 'request.json')
PROFILE_NUMBERS_PER_MAIN_PAGE = int(env.str('PROFILE_NUMBERS_PER_MAIN_PAGE', '6'))


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


@app.route('/request/')
def render_request():
    form = RequestForm()
    goals = get_goals_for_request_form(GOALS_JSON_PATH)
    form.goal.choices = goals
    form.goal.default = goals[0][0]
    form.process()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=["POST"])
def render_request_done():
    goals = get_goals_for_request_form(GOALS_JSON_PATH)
    form = RequestForm()
    form.goal.choices = goals
    if form.validate():
        goals = read_json(GOALS_JSON_PATH)
        goal = form.goal.data
        time = form.time.data
        name = form.name.data
        phone = form.phone.data
        write_request_to_json(goal, time, name, phone, REQUESTS_JSON_PATH)
        return render_template('request_done.html', goal=goals[goal], time=time, name=name, phone=phone)
    return 'Данные не получены '


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
