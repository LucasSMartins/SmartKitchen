import json
from datetime import datetime

from faker import Faker

# Inicializando o Faker
fake = Faker()

# Quantidade de registros a serem gerados
num_records = 5

# Gerando os dados fictícios
data = []
for _ in range(num_records):
    record = {
        "username": fake.name(),
        "email": fake.email(),
        "password": fake.password(),
    }
    data.append(record)

# Salvando os dados em um arquivo JSON
with open("fake_data.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"{num_records} registros foram salvos no arquivo fake_data.json")
