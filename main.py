from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
import bcrypt
from credentials import settings, credenciais

# app = Flask(__name__)

# # Configurar o MongoDB
# app.config["MONGO_URI"] = "mongodb://localhost:27017/seu_banco_de_dados"
# mongo = PyMongo(app)
app = Flask("Farmacia")
app.secret_key = 'deena'  # Substitua por uma chave secreta forte.
app.config["MONGO_URI"] = f"mongodb+srv://{credenciais['user_mongo']}:{credenciais['password_mongo']}@{settings['host']}/{settings['database']}?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/')
def home():
    if 'username' in session:
        return f'Bem-vindo, {session["username"]}! <a href="/logout">Sair</a>'
    return 'Página inicial - <a href="/login">Login</a>'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        users = mongo.db.usuarios
        users.insert_one({'username': username})
        session['username'] = username
        return redirect(url_for('home')), 201
    return 'Formulário de Registro'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        users = mongo.db.usuarios
        user = users.find_one({'username': username})
        if username:
            session['username'] = username
            return redirect(url_for('home')), 200
        return 'Usuário não encontrado!', 404
    return 'Formulário de Login'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)