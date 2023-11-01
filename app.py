from flask import Flask, session, request, jsonify, render_template,  redirect, url_for
from flask_pymongo import PyMongo, ObjectId
from credentials import settings, credenciais

app = Flask("Farmacia")
app.config["MONGO_URI"] = f"mongodb+srv://{credenciais['user_mongo']}:{credenciais['password_mongo']}@{settings['host']}/{settings['database']}?retryWrites=true&w=majority"
mongo = PyMongo(app)


# Usuários



# Produtos



# Vendas



# Relatórios




if __name__ == "__main__":
    app.run(debug=True)