from flask import Flask, jsonify

from kafka import KafkaClient, KafkaProducer
from kafka.errors import KafkaError

from time import sleep

import hashlib
import random
import string
import json

servico = Flask(__name__)

PROCESSO = "venda_de_giftcard"


def iniciar():
    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1))
    cliente.add_topic(PROCESSO)
    cliente.close()

@servico.route("/gift/<string:id_livro>/", methods=["POST", "GET"])
def executar(id_livro):
    resultado = {
        "resultado": "sucesso",
        "id_transacao": ""
    }

    # simula algum processamento atraves de espera ocupada
    sleep(random.randint(1, 6))

    ID = "".join(random.choice(string.ascii_letters +
                               string.punctuation) for _ in range(12))
    ID = hashlib.md5(ID.encode("utf-8")).hexdigest()

    try:
        produtor = KafkaProducer(
            bootstrap_servers=["kafka:29092"],
            api_version=(0, 10, 1))

        pedido_de_compra = {
            "identificacao": ID,
            "sucesso": 1,
            "mensagem": "pedido de compra iniciado",
            "id_livro": id_livro
        }
        produtor.send(topic=PROCESSO, value=json.dumps(
            pedido_de_compra).encode("utf-8"))

        resultado["id_transacao"] = ID
    except KafkaError as erro:
        resultado["resultado"] = f"erro ocorrido durante inicialização da reserva: {erro}"

    return json.dumps(resultado).encode("utf-8")


if __name__ == "__main__":
    iniciar()

    servico.run(
        host="0.0.0.0",
        debug=True
    )
