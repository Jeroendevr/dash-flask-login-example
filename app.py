from os import name, urandom
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from flask_login.utils import _secret_key
import pandas as pd
import plotly.express as px
from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dash_flask_login import FlaskLoginAuth

# Setup the Flask server
server = Flask(__name__)

# config
server.config.update(
    _secret_key = urandom(12),
)

# Setup the loginmanager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"



# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]
# Create our intital Dash App
# app = Flask(__name__)
app = Dash(name="app1", url_base_pathname='/app1/', server=server,
                external_stylesheets=external_stylesheets)

app.scripts.config.serve_locally = False

# Create Login Dash App with a login form
login_app = Dash(name='login-app', url_base_pathname='/login/', server=server,
                    external_stylesheets=external_stylesheets)

login_app.scripts.config.serve_locally = False

login_app.layout = html.Div([
    html.H1('Please log in to continue.', id='h1'),
    html.Form(
        method='Post',
        children=[
            dcc.Input(
                placeholder='Enter your username',
                type='text',
                id='uname-box'
            ),
            dcc.Input(
                placeholder='Enter your password',
                type='password',
                id='pwd-box'
            ),
            html.Button(
                children='Login',
                n_clicks=0,
                type='submit',
                id='submit-button'
            ),

        ]
    ),
    html.A(html.Button('app1'), href='/app1', style={'display':'none'}, id='hidden-link')
]
)

# This callback to the login app should encapsulate the login functionality
# Set the output to a non-visible location
@login_app.callback(
            Output('h1', 'n_clicks'),
            [Input('submit-button', 'n_clicks')],
            [State('uname-box', 'value'),
             State('pwd-box', 'value')]
        )
def login(n_clicks, uname, pwd):

    if uname == 'user' and pwd == 'password':
        login_user(load_user(users[0].name))

    else:pass

#Create logout Dash App
logout_app = Dash(name='logout-app', url_base_pathname='/logout/', server=server,
                    external_stylesheets=external_stylesheets)

logout_app.layout = html.Div([
    html.H1('You have successfully logged out!', id='h1'),

    # Since we've logged out, this will force a redirect to the login page with a next page of /app1
    html.A(html.Button('Log Back In'), href='/app1', id='login-button'),
]
)

# This callback to the logout app simply logs the user out each time the logout page is loaded
@logout_app.callback(
            Output('h1', 'n_clicks'),
            [Input('login-button', 'children')]
        )
def logout(children):
    logout_user()

# Create FlaskLoginAuth object to require login for Dash Apps
auth = FlaskLoginAuth(app)

# add logout app to FlaskLoginAuth
auth.add_app(logout_app)

# Database
users = {'tim@tim.tld':{'password': 'hoi'}}

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@server.route('/login', methods=['GET', 'Post'])
def login():
    if request.method == 'POST':
        if request.args.get('next'):
            return redirect(request.args.get('next'))
        else:
            return redirect('/login')
    else:
        return redirect('/login')

@server.route('/protected')
@login_required
def protected():
    return 'logged in as : ' + current_user.id

@server.route('/logout')
def logout():
    logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    ),
    html.A(html.Button('Log Out!'), href='/logout')
])

if __name__ == '__main__':
    server.run(debug=True)
