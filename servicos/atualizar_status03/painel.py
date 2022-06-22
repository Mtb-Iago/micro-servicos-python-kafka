from kafka import KafkaConsumer, TopicPartition
from time import sleep
import json

CONFIRMACAO_RESERVA = "confirmar_reserva"

painel_de_sugestao = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

offset = 0
while True:
    #print("Painel 03 para ativação da reserva")

    particao = TopicPartition(CONFIRMACAO_RESERVA, 0)
    painel_de_sugestao.assign([particao])
    painel_de_sugestao.poll()
    painel_de_sugestao.seek_to_end()
        
    for sugerir_livros_disponiveis in painel_de_sugestao:
        offset = sugerir_livros_disponiveis.offset + 1

        comando_sugestao = sugerir_livros_disponiveis.value
        comando_sugestao = json.loads(comando_sugestao)

        print("[PAINEL 03] - Livro reservado e status atualizado")

    sleep(0.3)
