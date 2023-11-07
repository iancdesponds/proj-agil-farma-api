from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_pymongo import PyMongo
import bcrypt
from credentials import settings, credenciais

app = Flask("Farmacia")
app.secret_key = 'deena'  # Substitua por uma chave secreta forte.
app.config["MONGO_URI"] = f"mongodb+srv://{credenciais['user_mongo']}:{credenciais['password_mongo']}@{settings['host']}/{settings['database']}?retryWrites=true&w=majority"
mongo = PyMongo(app)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.json['username']
        senha = request.json['senha']
        users = mongo.db.usuarios
        user = users.find_one({'username': username, 'senha': senha})
        new_user = users.insert_one({'username': username, 'senha': senha})
        return "Usuário registrado com sucesso!", 201
    return 'Formulário de Registro'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        senha = request.json['senha']
        users = mongo.db.usuarios
        user = users.find_one({'username': username, 'senha': senha})
        if username == user['username'] and senha == user['senha']:
            session['username'] = username
            return "Login realizado com sucesso!", 200
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

@app.route('/estoque', methods=['GET', 'POST'])
def estoque():
    if request.method == 'GET':
        try:
            estoque = list(mongo.db.estoque.find({},{'dados_produto':1, 'quantidade':1, 'data_de_validade':1, 'preco_venda':1, 'custo_por_unidade':1, 'fornecedor':1, 'notificacao_baixo_estoque':1, '_id':0}))
            estoque_list = [{"Produto":produto['dados_produto'], "Quantidade":produto['quantidade'], "Data de Validade":produto['data_de_validade'], "Fornecedor":produto['fornecedor'], "Custo por Unidade":produto['custo_por_unidade'], "Preço de Venda":produto['preco_venda'], "Notificação de Baixo Estoque":produto['notificacao_baixo_estoque']} for produto in estoque]
        except:
            estoque_list = []
        return jsonify({"Estoque":estoque_list}), 200
    elif request.method == 'POST':
        try:
            request_data = request.json

            if 'dados_produto' not in request_data:
                return {'ERRO': 'dados do produto não informados'}, 400
            dados_produto = request_data['dados_produto']

            if 'fornecedor' not in request_data:
                return {'ERRO': 'fornecedor do produto não informado'}, 400
            fornecedor_produto = request_data['fornecedor']
            
            if 'quantidade' not in request_data:
                return {'ERRO': 'quantidade do produto não informada'}, 400
            quantidade_produto = request_data['quantidade']
            
            if 'data_de_validade' not in request_data: 
                return {'ERRO': 'data de validade do produto não informada'}, 400
            data_validade_produto = request_data['data_de_validade']

            if 'custo_por_unidade' not in request_data:
                return {'ERRO': 'custo por unidade do produto não informado'}, 400
            custo_produto = request_data['custo_por_unidade']
            
            if 'preco_venda' not in request_data:
                return {'ERRO': 'preço de venda do produto não informado'}, 400
            preco_venda_produto = request_data['preco_venda']

            if 'notificacao_baixo_estoque' not in request_data:
                return {'ERRO': 'notificação de baixo estoque do produto não informada'}, 400
            notificacao_baixo_estoque_produto = request_data['notificacao_baixo_estoque']


            
            data_produto_novo = {'dados_produto': dados_produto, 'fornecedor': fornecedor_produto, 'quantidade': quantidade_produto, 'data_de_validade': data_validade_produto, 'custo_por_unidade': custo_produto, 'preco_venda': preco_venda_produto, 'notificacao_baixo_estoque': notificacao_baixo_estoque_produto}
            
            mongo.db.estoque.insert_one(data_produto_novo)
            return {"SUCESSO" :'Produto Adicionado com sucesso!'}, 201
        
        except:
            return {'ERRO': 'Erro ao tentar adicionar produto na base de dados'}, 500
        
@app.route('/estoque/<dados_produto>', methods=['DELETE'])
def deleta_estoque(dados_produto):
    try:
        mongo.db.estoque.delete_one({"dados_produto": dados_produto})
        return jsonify({"message": f"Produto '{dados_produto}' deletado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao deletar produto: " + str(e)}), 500
    
@app.route('/estoque', methods=['PUT'])
def atualiza_estoque():
    data = request.json
    try:
        
        dados_produto = data["produto_update"]
        fornecedor_produto = data["fornecedor_update"]
        quantidade_produto = data["quantidade_update"]
        data_validade_produto = data["data_de_validade_update"]
        custo_produto = data["custo_por_unidade_update"]
        preco_venda_produto = data["preco_venda_update"]
        notificacao_baixo_estoque_produto = data["notificacao_baixo_estoque_update"]
        
        resultado = mongo.db.estoque.update_one(
            {"dados_produto": dados_produto}, 
            {"$set": {"fornecedor": fornecedor_produto, 
                      "quantidade": quantidade_produto, 
                      "data_de_validade": data_validade_produto, 
                      "custo_por_unidade": custo_produto,
                      "preco_venda": preco_venda_produto,
                      "notificacao_baixo_estoque": notificacao_baixo_estoque_produto}
            }
        )
        if resultado.modified_count > 0:
            return jsonify({"message": f"Produto '{dados_produto}' atualizado com sucesso!"}), 200
        else:
            return jsonify({"message": "Nenhum produto foi atualizado."}), 400
    except Exception as e:
        return jsonify({"message": "Erro ao atualizar produto: " + str(e)}), 500
    
@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    if request.method == 'GET':
        try:
            vendas = list(mongo.db.vendas.find({},{'dados_produto':1, 'quantidade':1, 'data_de_validade':1, 'preco_venda':1, 'custo_por_unidade':1, 'fornecedor':1, 'data_venda':1, '_id':0}))
            vendas_list = [{"Produto":produto['dados_produto'], "Quantidade":produto['quantidade'], "Data de Validade":produto['data_de_validade'], "Fornecedor":produto['fornecedor'], "Custo por Unidade":produto['custo_por_unidade'], "Preço de Venda":produto['preco_venda'], "Data da Venda":produto['data_venda']} for produto in vendas]
        except:
            vendas_list = []
        return jsonify({"Vendas":vendas_list}), 200
    elif request.method == 'POST':
        try:
            request_data = request.json

            if 'dados_produto' not in request_data:
                return {'ERRO': 'dados do produto não informados'}, 400
            dados_produto = request_data['dados_produto']

            if 'fornecedor' not in request_data:
                return {'ERRO': 'fornecedor do produto não informado'}, 400
            fornecedor_produto = request_data['fornecedor']
            
            if 'quantidade' not in request_data:
                return {'ERRO': 'quantidade do produto não informada'}, 400
            quantidade_produto = request_data['quantidade']
            
            if 'data_de_validade' not in request_data: 
                return {'ERRO': 'data de validade do produto não informada'}, 400
            data_validade_produto = request_data['data_de_validade']

            if 'custo_por_unidade' not in request_data:
                return {'ERRO': 'custo por unidade do produto não informado'}, 400
            custo_produto = request_data['custo_por_unidade']
            
            if 'preco_venda' not in request_data:
                return {'ERRO': 'preço de venda do produto não informado'}, 400
            preco_venda_produto = request_data['preco_venda']

            if 'data_venda' not in request_data:
                return {'ERRO': 'data da venda do produto não informada'}, 400
            data_venda_produto = request_data['data_venda']


            dados_venda = {'dados_produto': dados_produto, 'fornecedor': fornecedor_produto, 'quantidade': quantidade_produto, 'data_de_validade': data_validade_produto, 'custo_por_unidade': custo_produto, 'preco_venda': preco_venda_produto, 'data_venda': data_venda_produto}

            mongo.db.vendas.insert_one(dados_venda)

            return {"SUCESSO" :'Venda Adicionada com sucesso!'}, 201
        except:
            return {'ERRO': 'Erro ao tentar adicionar venda na base de dados'}, 500


if __name__ == '__main__':
    app.run(debug=True)  