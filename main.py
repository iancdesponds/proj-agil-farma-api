from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_pymongo import PyMongo
import bcrypt
from credentials import settings, credenciais

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
        username = request.json['username']
        users = mongo.db.usuarios
        user = users.find_one({'username': username})
        new_user = users.insert_one({'username': username})
        # session['username'] = username
        #print(session)
        print('d')
        return redirect(url_for('home')), 201
    return 'Formulário de Registro'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json['username']
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

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'GET':
        produtos = list(mongo.db.produtos.find({},{'marca_produto':1, 'nome_produto':1, 'descricao_produto':1, 'quantidade_por_unidade_produto':1, 'notificacao_baixo_estoque_produto':1, '_id':0}))
        produtos_list = [{"Marca":produto['marca_produto'], "Nome":produto['nome_produto'], "Descrição":produto['descricao_produto'], "Quantidade por Unidade":produto['quantidade_por_unidade_produto'], "Notificação de Baixo Estoque":produto['notificacao_baixo_estoque_produto']} for produto in produtos]
        return jsonify({"Produtos":produtos_list}), 200
    
    elif request.method == 'POST':
        try:
            request_data = request.json

            if 'marca_produto' not in request_data:
                return {'ERRO': 'marca do produto não informada'}, 400
            marca_produto = request_data.get('marca_produto')
            
            if 'nome_produto' not in request_data:
                return {'ERRO': 'nome do produto não informado'}, 400
            nome_produto = request_data.get('nome_produto')
            
            if 'descricao_produto' not in request_data: 
                return {'ERRO': 'descrição do produto não informada'}, 400
            descricao_produto = request_data.get('descricao_produto')
            
            if 'quantidade_por_unidade_produto' not in request_data:
                return {'ERRO': 'quantidade por unidade do produto não informada'}, 400
            quantidade_por_unidade_produto = request_data.get('quantidade_por_unidade_produto')
            
            if 'notificacao_baixo_estoque_produto' not in request_data:
                return {'ERRO': 'notificação de baixo estoque do produto não informada'}, 400
            notificacao_baixo_estoque_produto = int(request_data.get('notificacao_baixo_estoque_produto'))
            
            data_produto_novo = {'marca_produto': marca_produto, 'nome_produto': nome_produto, 'descricao_produto': descricao_produto, 'quantidade_por_unidade_produto': quantidade_por_unidade_produto, 'notificacao_baixo_estoque_produto': notificacao_baixo_estoque_produto}
            
            mongo.db.produtos.insert_one(data_produto_novo)
            return {"SUCESSO" :'Produto Adicionado com sucesso!'}, 201
        
        except:
            return {'ERRO': 'Erro ao tentar adicionar produto na base de dados'}, 500

@app.route('/produtos/<nome_produto>', methods=['DELETE'])
def deleta_pedidos(nome_produto):
    try:
        mongo.db.produtos.delete_one({"nome_produto": nome_produto})
        return jsonify({"message": f"Produto '{nome_produto}' deletado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao deletar produto: " + str(e)}), 500

@app.route('/produtos', methods=['PUT'])
def atualiza_pedidos():
    data = request.json
    try:
        
        nome_produto = data["nome_produto_update"]
        marca_produto = data["marca_produto_update"]
        descricao_produto = data["descricao_produto_update"]
        quantidade_por_unidade_produto = data["quantidade_por_unidade_produto_update"]
        notificacao_baixo_estoque_produto = data["notificacao_baixo_estoque_produto_update"]
        
        resultado = mongo.db.produtos.update_one(
            {"nome_produto": nome_produto}, 
            {"$set": {"marca_produto": marca_produto, 
                      "descricao_produto": descricao_produto, 
                      "quantidade_por_unidade_produto": quantidade_por_unidade_produto, 
                      "notificacao_baixo_estoque_produto": notificacao_baixo_estoque_produto}
            }
        )
        if resultado.modified_count > 0:
            return jsonify({"message": f"Preço do produto '{nome_produto}' atualizado com sucesso!"}), 200
        else:
            return jsonify({"message": "Nenhum produto foi atualizado."}), 400
    except Exception as e:
        return jsonify({"message": "Erro ao atualizar produto: " + str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)  