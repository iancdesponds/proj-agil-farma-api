from flask import Flask, jsonify, request
from flask_pymongo import PyMongo, ObjectId
from credentials import settings, credenciais

app = Flask("Farmacia")
app.config["MONGO_URI"] = f"mongodb+srv://{credenciais['user_mongo']}:{credenciais['password_mongo']}@{settings['host']}{settings['database']}?retryWrites=true&w=majority"
mongo = PyMongo(app)
mongo.db.usuarios

# Usuários
@app.route('/usuarios', methods=['POST'])
def adicionar_usuario():
    request_data = request.json

    try:
        usuario = request_data.get('usuario')
        if 'usuario' not in request_data:
            return {'ERRO': 'usuário não informado'}, 400
        if mongo.db.usuarios.find_one({"usuário": usuario}):
            return {'ERRO': 'Esse usuário já está cadastrado'}, 400
        
        senha = request_data.get('senha')
        if 'senha' not in request_data:
            return {'ERRO': 'senha não informada'}, 400

        mongo.db.usuarios.insert_one(request_data)

        return {"SUCESSO" :'Usuário Adicionado com sucesso!'}, 201

    except:
        return {'ERRO': 'Erro ao tentar adicionar usuário na base de dados'}, 500


# Produtos



# Vendas



# Relatórios




if __name__ == "__main__":
    app.run(debug=True)