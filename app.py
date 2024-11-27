from flask import Flask, request, jsonify, render_template
import random
import requests

app = Flask(__name__)

# Configuração Zenvia
ZENVIA_API_TOKEN = 'seu_token_da_zenvia'  # Substitua pelo seu token real
ZENVIA_BASE_URL = 'https://api.zenvia.com/v2/channels'

# Validação de nome (máximo 25 caracteres)
def validar_nome(nome):
    return len(nome) <= 25

# Página inicial com formulário
@app.route('/')
def index():
    return render_template('index.html')

# Enviar o código
@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.json
    nome = data.get('name')  # Nome do perfil
    method = data.get('method')  # 'sms', 'voice' ou 'whatsapp'
    contact = data.get('contact')  # Número de telefone
    code = str(random.randint(100000, 999999))  # Código de 6 dígitos

    # Validação de entrada
    if not nome or not method or not contact:
        return jsonify({"error": "Nome, método e contato são obrigatórios"}), 400

    if not validar_nome(nome):
        return jsonify({"error": "O nome deve ter no máximo 25 caracteres"}), 400

    # Mensagem personalizada
    message = f"Olá, {nome} bem-vindo ao CoinBeer.AI! O Seu código de verificação é: {code}. Evite filas e ganhe um chorinho cashback a cada compra."

    # Verificar se a mensagem não ultrapassa 160 caracteres
    total_chars = len(message)
    if total_chars > 160:
        return jsonify({"error": "A mensagem gerada excede 160 caracteres!"}), 400

    # Exibir mensagem e quantidade de caracteres no terminal
    print(f"Mensagem que será enviada: {message}")
    print(f"Quantidade de caracteres: {total_chars}")

    # Mensagem antes da principal
    pre_message = f"Olá, {nome}, sua mensagem está sendo preparada..."

    # URL da imagem (print)
    image_url = "/static/images/print.png"  # Certifique-se de que a imagem está em 'static/images/print.png'

    # Configuração do canal
    if method == "sms":
        url = f"{ZENVIA_BASE_URL}/sms/messages"
    elif method == "voice":
        url = f"{ZENVIA_BASE_URL}/voice/messages"
    elif method == "whatsapp":
        url = f"{ZENVIA_BASE_URL}/whatsapp/messages"
    else:
        return jsonify({"error": "Método inválido. Use 'sms', 'voice' ou 'whatsapp'."}), 400

    payload = {
        "from": "CoinBeer",
        "to": contact,
        "contents": [{"type": "text", "text": message}]
    }

    headers = {
        "Authorization": f"Bearer {ZENVIA_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        # Retornar a mensagem e detalhes para o front-end
        return jsonify({
            "pre_message": pre_message,
            "sent_message": message,
            "total_chars": total_chars,
            "image_url": image_url,
            "message": f"Código enviado via {method} com sucesso!"
        })
    except requests.exceptions.RequestException as e:
        # Exibir a mensagem e erro no terminal
        print(f"Erro: {e}")
        print(f"Mensagem que não foi enviada: {message} ({total_chars} caracteres)")
        # Retornar a mensagem e detalhes para o front-end mesmo em caso de erro
        return jsonify({
            "error": str(e),
            "pre_message": pre_message,
            "sent_message": message,
            "total_chars": total_chars,
            "image_url": image_url
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
