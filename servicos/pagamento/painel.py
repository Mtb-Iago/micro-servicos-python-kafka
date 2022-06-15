from kafka import KafkaConsumer, TopicPartition
from time import sleep
import json

painel_de_pagamento = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

particao = TopicPartition("pagamento", 0)
painel_de_pagamento.assign([particao])

painel_de_pagamento.seek_to_beginning(particao)
offset = 0
while True:
    print("esperando pagamentos...")

    for pagamento in painel_de_pagamento:
        offset = pagamento.offset + 1

        dados_do_pagamento = json.loads(pagamento.value)
        print("dados do pagamento: ", dados_do_pagamento)

    painel_de_pagamento.seek(particao, offset)

    sleep(5)

# painel_de_estoque.close()
