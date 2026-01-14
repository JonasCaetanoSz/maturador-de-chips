![license](https://img.shields.io/badge/License-MIT-green.svg?logo=internetarchive&logoColor=white&labelColor=464646&style=for-the-badge)
![stars](https://img.shields.io/github/stars/jonasCaetanoSz/maturador-de-chips?style=for-the-badge)
![version](https://img.shields.io/github/v/release/jonasCaetanoSz/maturador-de-chips?style=for-the-badge)

# Maturador de chips

Maturador de chips é um pequeno programa para "esquentar" contas do WhatsApp e, dessa forma, evitar banimento da rede social.

## Instalação

Se você é usuário Windows, pode <a href="https://github.com/JonasCaetanoSz/maturador-de-chips/releases/download/v2025.11.12/MaturadorSetup2025.11.12.exe"> fazer download do instalador x64</a>  ou siga as instruções abaixo para executar o código-fonte da versão de código aberto:

- Clone o repositório

```shell
git clone https://github.com/JonasCaetanoSz/maturador-de-chips.git
```

- Vá para o diretório do programa

```shell
cd maturador-de-chips
```

- Crie um ambiente virtual e ative-o

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
- Mensagens com ChatGpt
- Sem limite de instâncias
- Escolher nome da instância
- Remover instância

### Como gerar meu próprio executável?

Este é o comando pyinstaller para gerar o executável do maturador:

```shell
pyinstaller --noconfirm --onedir --windowed --icon "$(pwd)/assets/medias/icon.ico" --name "Maturador de chips" --add-data "$(pwd)/preferences.json;." --add-data "$(pwd)/injected.js;." --add-data "$(pwd)/settings.html;." --add-data "$(pwd)/status.html;." --add-data "$(pwd)/whatsapp_list.html;." --add-data "$(pwd)/delete.json;." --add-data "$(pwd)/assets;assets" "$(pwd)/main.py"
```

### Como usar o Chat GPT para gerar mensagens?

 - Acesse <a href="https://platform.openai.com/settings/organization/api-keys">https://platform.openai.com/settings/organization/api-keys</a>

 - Clique em "Create new secret key".

 - Copie a chave (começa com sk-).

 - Cole no campo Token da OpenAI no programa.

## Licença

Distribuído sob Licença [MIT](https://choosealicense.com/licenses/mit/)


