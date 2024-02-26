from openai import OpenAI
import random
import g4f
import sys

sys.stdout = open("MaturadorLogs.txt", "a", encoding="utf-8")
sys.stderr = open("MaturadorLogs.txt", "a", encoding="utf-8")

TOPICS = [
    "História mundial",
    "Ciência",
    "Cultura",
    "Tecnologia",
    "Política",
    "Filosofia",
    "Arte",
    "Literatura",
    "Geografia",
    "Astronomia",
    "Medicina",
    "Música",
    "Matemática",
    "Biologia",
    "Economia",
    "Psicologia",
    "Sociologia",
    "Antropologia",
    "Arqueologia",
    "Educação",
    "Religião",
    "Esportes",
    "Meio ambiente",
    "Direito",
    "Engenharia",
    "Alimentação e nutrição",
    "Moda",
    "Cinema",
    "Teatro",
    "Fotografia",
    "Dança",
    "Agricultura",
    "Energias renováveis",
    "Jogos",
    "Design",
    "Saúde pública",
    "Marketing",
    "Administração",
    "Linguística",
    "Química",
    "Física",
    "Robótica",
    "Inteligência artificial",
    "Guerras mundiais",
    "Revoluções",
    "Movimentos sociais",
    "Grandes descobrimentos",
    "Colonização",
    "Imperialismo",
    "Revolução industrial",
    "Revolução tecnológica",
    "Guerra fria",
    "Globalização",
    "Mudanças climáticas",
    "Exploração espacial",
    "Avanços médicos",
    "Invenções",
    "Descobertas científicas",
    "Grandes artistas",
    "Grandes escritores",
    "Grandes cientistas",
    "Grandes filósofos",
    "Grandes músicos",
    "Grandes líderes políticos",
    "Grandes inventores",
    "Grandes exploradores",
    "Grandes batalhas",
    "Grandes catástrofes naturais",
    "Grandes epidemias",
    "Geopolítica",
    "Inteligência emocional",
    "Desenvolvimento sustentável",
    "Economia comportamental",
    "Criptomoedas",
    "Inteligência de mercado",
    "Tendências de consumo",
    "Inovação tecnológica",
    "Cibersegurança",
    "Privacidade de dados",
    "Bioética",
    "Direitos humanos",
    "Neurociência",
    "Interação humano-computador",
    "Robótica assistencial",
    "Realidade virtual",
    "Realidade aumentada",
    "Nanotecnologia",
    "Internet das coisas",
    "Machine learning",
    "Aprendizado profundo",
    "Redes neurais",
    "Computação quântica",
    "Impressão 3D",
    "Biotecnologia",
    "Genética",
    "Clonagem",
    "Transplantes de órgãos",
    "Neurotecnologia"

]

class GptGenerateMessage():
    def __init__(self) -> None:
        g4f.check_version = False
        self._last_message = None
        self._last_question = None
        self.client:OpenAI = None
    

    def generate_question_by_unnoficial(self) -> str:
            response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4_turbo,
            provider=g4f.Provider.Bing,
            messages=[{"role": "user", "content":  random.choice(["conte uma curiosidade sobre " + random.choice(TOPICS) , "me faça uma pergunta sobre " + random.choice(TOPICS)]) }],
            stream=False)
            return response

    def generate_response_by_unnoficial(self, question:str) -> str:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4_turbo,
            provider=g4f.Provider.Bing,
            messages=[{"role": "user", "content": "uma pergunta para você: " + question}],
            stream=False            
            
        )
        return response
    
    def by_unnoficial(self) -> str|tuple[bool, str]:
        try:
            if random.choice([True, True, False]) and self._last_message:
                self._last_message = self.generate_response_by_unnoficial(question=self._last_message)
                return self._last_message

            self._last_message = self.generate_question_by_unnoficial()
            return self.parser_message(self._last_message)
        
        except Exception as response_by_unnoficial_error:
             return (False, str(response_by_unnoficial_error))

    def generate_question_by_official(self) -> str:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content":  random.choice(["conte uma curiosidade sobre " + random.choice(TOPICS) , "me faça uma pergunta sobre " + random.choice(TOPICS)]),}],
                model="gpt-3.5-turbo",
            )
            return response

    def generate_response_by_official(self, question:str) -> str:
        response = self.client.chat.completions.create(
            messages=[{"role": "user","content": "uma pergunta para você: " + question,}],
            model="gpt-3.5-turbo",
        )
        return response.strip()
    
    def by_official(self) -> str|tuple[bool, str]:
        try:
            if random.choice([True, True, False]) and self._last_message:
                self._last_message = self.generate_response_by_official(question=self._last_message)
                return self._last_message

            self._last_message = self.generate_question_by_official()
            return self.parser_message(self._last_message)
        
        except Exception as response_by_official_error:
             return (False, str(response_by_official_error))
    
    def set_bing_cookie(self, cookie:str) -> None:
        g4f.set_cookies(".bing.com", {"_U": cookie})


    def ininialize_openai_client(self, token:str) -> None:
        self.client = OpenAI(api_key=token)
    
    @staticmethod
    def parser_message(text:str):
        parsed_message = ""
        for _ in text.split():
             parsed_message += " " + _.replace("**", "*")
        return parsed_message \
                .replace("**Pergunta aleatória:**", "") \
                .replace("**Curiosidade Aleatória: ", "") \
                .replace("Olá, este é o Copilot. Eu sou um assistente de inteligência artificial que pode conversar com você sobre vários tópicos e criar conteúdo interessante.", "") \
                .replace( "Olá, este é o Copilot. Eu sou um assistente de inteligência artificial que pode conversar com você sobre vários tópicos e ajudá-lo com algumas tarefas.", "") \
                .replace( "Olá, Eu sou o Copilot.", "") \
                .replace("**Pergunta aleatória:**", "") \
                .replace("**Pergunta aleatória:**", "") \
                .replace("**Curiosidade Aleatória: ", "") \
                .replace("**Curiosidade Aleatória:**", "") \
                .replace( "Olá, este é o Copilot.", "")