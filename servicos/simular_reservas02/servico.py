#SERVICO 02 - SIMULAR RESERVAS
from flask_apscheduler import APScheduler
from flask import Flask, jsonify
from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import json

servico = Flask(__name__)

PROCESSO = "listar_livros"
CONFIRMACAO_RESERVA = "confirmar_reserva"
SUGESTAO_LIVROS = "sugerir_livros"
REQUISICAO = "requisicao"

def iniciar():
    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1))
    cliente.add_topic(PROCESSO)
    cliente.close()


@servico.route("/escolherLivro/<int:id_livro>", methods=["POST", "GET"])
def escolher_livro(id_livro):
    
    try:
        produtor = KafkaProducer(
            bootstrap_servers=["kafka:29092"],
            api_version=(0, 10, 1)
        )
        produtor.send(topic=REQUISICAO, value=json.dumps(
            id_livro).encode("utf-8"))
        
    except KafkaError as erro:
        resultado = f"erro: {erro}"
        
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

def efetuar_reserva(informacoes_da_remessa, id_livro):
    index = 0
    for acervo in informacoes_da_remessa:
        if acervo["id"] == id_livro:
            identificador_livro = []
            autor = acervo["autor"]
            titulo = acervo["titulo"]
            disponibilidade = acervo["disponibilidade"] 
            index += 1
            if acervo["disponibilidade"] == True:
                email = (f"Email de confirmação de reserva enviado, caso o livro esteja dísponivel sua reserva será confirmada.")
                
                try:
                    produtor = KafkaProducer(
                        bootstrap_servers=["kafka:29092"],
                        api_version=(0, 10, 1)
                    )
                    produtor.send(topic=CONFIRMACAO_RESERVA, value=json.dumps(
                        id_livro).encode("utf-8"))
                    
                except KafkaError as erro:
                    resultado = f"erro: {erro}"
                
                return jsonify({"Dados recebidos": {"Id Livro":id_livro, "Autor": autor, "Disponibilidade": disponibilidade}, "Resposta": email})
            else:
                email = ("Livro indisponível no momento")
                
                try:
                    produtor = KafkaProducer(
                        bootstrap_servers=["kafka:29092"],
                        api_version=(0, 10, 1)
                    )
                    produtor.send(topic=SUGESTAO_LIVROS, value=json.dumps(
                        "sugerir").encode("utf-8"))
                    
                except KafkaError as erro:
                    resultado = f"erro: {erro}"
                return jsonify({"Resposta": email})
if __name__ == "__main__":
    iniciar()
    
servico.run(
    host="0.0.0.0",
    debug=True
)

