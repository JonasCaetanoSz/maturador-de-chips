![license](https://img.shields.io/badge/License-MIT-green.svg?logo=internetarchive&logoColor=white&labelColor=464646&style=for-the-badge)
![stars](https://img.shields.io/github/stars/jonasCaetanoSz/maturador-de-chips?style=for-the-badge)
![version](https://img.shields.io/github/v/release/jonasCaetanoSz/maturador-de-chips?style=for-the-badge)

# Maturador de chips

maturador de chips é um pequeno programa para "esquentar" contas do whatssap e dessa forma, evitar banimento da rede social.


## Instalação

Se você é usuário  Windows, pode <a href="https://github.com/JonasCaetanoSz/maturador-de-chips/releases/download/27.09.2023/MaturadorSetup_27.09.2023.exe"> fazer download do instalador x64</a> ou siga as instruções abaixo para executar o código-fonte:

- Clone o repositório

```shell
git clone https://github.com/JonasCaetanoSz/maturador-de-chips.git

```

Crie um ambiente virtual e ative-o

```shell
python -m venv .venv 
```

```shell
& .venv/scripts/activate.ps1
```

- Instale as dependências


```shell
pip install -r requirements.txt
```

- Inicie o programa


```shell
python main.py
```

## Funcionalidades

- Definir intervalo mínimo e máximo entre mensagens
- Definir troca de conta após X mensagens
- Definir máximo de mensagens
- Parar em caso de bloqueio
-   sem limite de instâncias
-  escolher nome instância
 - remover instância

## Roadmap

- Adicionar envio de arquivos
- Adicionar disparador

## FAQ


### Quais são as portas usadas por este programa?


A porta 5025 é usada pela API e a porta 5026 é usada pelo websocket.


### Como apagar uma conta?


Como ainda não é possível escolher o nome da instância, não achei necessário ter a opção de apagar uma conta. Portanto, se você deseja trocar uma conta, pode simplesmente desconectá-la pelo próprio WhatsApp e reiniciar o programa.


### Quais são os requisitos mínimos do sistema?


desenvolvi em uma maquina com processador i3 e 4GB de memoria RAM, portanto, se sua maquina possui configurações semelhantes ou superiores a essas, o maturador rodará sem problemas.


### Como gerar meu próprio executável?


Este é o comando pyinstaller para gerar o executável do servidor websocket:


```shell
pyinstaller --noconfirm --onefile --windowed  "<PATH-DO-ARQUIVO-WEBSOCKET_SERVER.PY>"
```


## Licença


distribuído sobre [MIT](https://choosealicense.com/licenses/mit/) Licença
