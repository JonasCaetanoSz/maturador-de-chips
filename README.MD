![license](https://img.shields.io/badge/License-MIT-green.svg?logo=internetarchive&logoColor=white&labelColor=464646&style=for-the-badge)
![stars](https://img.shields.io/github/stars/jonasCaetanoSz/maturador-de-chips?style=for-the-badge)
![version](https://img.shields.io/github/v/release/jonasCaetanoSz/maturador-de-chips?style=for-the-badge)

# Maturador de chips

maturador de chips é um pequeno programa para "esquentar" contas do whatssap e dessa forma, evitar banimento da rede social


## Instalação

Se você é usuário  Windows, pode <a href="https://github.com/JonasCaetanoSz/maturador-de-chips/releases/download/v16.12.2023/Maturador_setup16.12.2023.exe"> fazer download do instalador x64</a>  ou siga as instruções abaixo para executar o código-fonte da versão de codigo aberto:

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

### Versões Alternativas:
 
 - <a href="https://github.com/APIBrasil/maturador-de-chips"> https://github.com/APIBrasil/maturador-de-chips </a>
 - <a href="https://github.com/AdrianoF0nseca/maturador-de-chips"> https://github.com/AdrianoF0nseca/maturador-de-chips </a>


### Como gerar meu próprio executável?

Este é o comando pyinstaller para gerar o executavel do maturador:

```shell
pyinstaller  --noconfirm --onedir --windowed --icon "(pwd)/pages/assets/medias/icon.ico" --add-data "(pwd)/pages;pages/" --add-data "(pwd)/scripts;scripts/" --add-data "(pwd)/LICENSE;." --add-data "(pwd)/README.MD;." --add-data "(pwd)/user-agent;." --add-data "(pwd)/requirements.txt;."  "(pwd)/main.py"

```

## Licença


distribuído sobre [MIT](https://choosealicense.com/licenses/mit/) Licença
