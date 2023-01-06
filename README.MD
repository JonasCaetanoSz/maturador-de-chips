
# maturador de chips

maturador de chips é um pequeno programa para "esquentar" contas do whatssap e dessa forma, evitar banimento da rede social.

## Instalação

clone o repositorio:  

```bash
git clone https://github.com/JonasCaetanoSz/maturador-de-chips.git
```

inicia e instala as dependecias em um ambiente virtual:

    
```bash
python -m venv maturador-de-chips && cd maturador-de-chips/scripts && activate && cd.. pip install -r requirements.txt 
```

inicie o programa:

```bash
python main.py
```
## Funcionalidades

- Temas dark e light
- Log de mensagens enviadas detalhado
- Cache de sessão das contas adicionadas
- Pode definir máximo de mensagens
- Pode definir intervalo entre mensagens


## Roadmap

- Melhorar o suporte de navegadores (tkinter webviewer)

- Adicionar opção de envio de imagens e audios

## FAQ

#### o programa está indentificando mais contas do que foi adicionado:

a causa mais comum para este erro é um arquivo `.gikeep` na pasta `/utils/sessions` , nesta pasta está armazenado a sessão de todas as contas adicionadas, se você acessar essa pasta e ver um arquivo .gitkeep ou qualquer arquivos/pastas com nomes que não são iqual ao apelido de alguma conta adicionada, você pode deletar.


## Licença

distribuido sobre á licença [MIT](https://choosealicense.com/licenses/mit/)

