#SERVICO 02 - SIMULAR RESERVAS

from flask_apscheduler import APScheduler
from flask import Flask, jsonify
from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import random
import json

servico = Flask(__name__)

PROCESSO = "listar_livros"

def iniciar():
    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1))
    cliente.add_topic(PROCESSO)
    cliente.close()


@servico.route("/escolherLivro/<int:id_livro>", methods=["POST", "GET"])
def escolher_livro(id_livro):    
    consumir_livros = KafkaConsumer(
        bootstrap_servers = ["kafka:29092"],
        api_version = (0, 10, 1),
        auto_offset_reset = "earliest",
        consumer_timeout_ms=1000)
    
    particao = TopicPartition(PROCESSO, 0)
    consumir_livros.assign([particao])
    consumir_livros.seek_to_beginning(particao)
    offset = 0

    for acervo in consumir_livros:
        offset = acervo.offset + 1
        informacoes_da_remessa = acervo.value
        informacoes_da_remessa = json.loads(informacoes_da_remessa)

    consumir_livros.seek(particao, offset)
    retorno = efetuar_reserva(informacoes_da_remessa, id_livro)
    return retorno

# Lista todos os livros do acervo
def efetuar_reserva(informacoes_da_remessa, id_livro):
    mensagem = "Processando"
    index = 0
    for acervo in informacoes_da_remessa:
            if acervo["id"] == id_livro:
                autor = acervo["autor"]
                if acervo["disponibilidade"] == True:
                    print(f"Autor: {autor}")
                    print(f"Pode enviar email com a reserva.")
                    
                    return jsonify("Pode enviar email com a reserva.")
                    break
                else:
                    print(f"Autor: {autor}")
                    print(f"Manda para o servico 4")
                    
                    return "Manda para o servico 4"
                    break
            else:
                return jsonify(f"Não existe livro com esse id: {id_livro}")
            index += 1

def validar_desbloqueio(id_pedido, informacoes_da_remessa):
    # simula um gasto de tempo de processamento
    sleep(random.randint(1, 6))

    desbloqueado, mensagem = True, "desbloqueio realizado com sucesso"
    return desbloqueado, mensagem

if __name__ == "__main__":
    iniciar()
    
    # agendador = APScheduler()
    # agendador.add_job(id=PROCESSO, func=escolher_livro,
    #                 trigger="interval", seconds=3)
    # agendador.start()
    # while True:
    #     sleep(5)
servico.run(
    host="0.0.0.0",
    debug=True
)

