import sys

class Informacoes_Arquivo_Entrada:
    def __init__(self, numero_processos, pids_liberados):
        self.numero_processos = int(numero_processos)
        self.pids_liberados = list(pids_liberados)

class Lista_Processos:
    def __init__(self, tipo, pid, ua=None, end_log=None):
        self.tipo = tipo
        self.pid = pid
        self.ua = ua
        self.end_log = end_log

class Bloco_RAM:
    def _initi_(self):
        self.alocado = False
        
    def alocar(self):
        self.alocado = True

    def desalocar(self):
        self.alocado = False

    def __repr__(self):
        return "Alocado" if self.alocado else "Desalocado"
    
class Bloco_Tabela:
    def _init(self):
        self.pid = self.pid
        self.end_log = self.end_log
        self.limite = self.limite

    def informar_pid(self, pid):
        self.pid = pid
    
    def informar_end_log(self, end_log):
        self.pid = end_log
    
    def informar_limite(self, limite):
        self.limite = limite
    
class Simulador:
    def _init_(self, numero_processos):
        self.RAM = []
        for _ in range(4096):
            self.RAM.append(Bloco_RAM())

        self.Tabela = []
        for _ in range(numero_processos):
            self.RAM.append(Bloco_Tabela())

def ler_arquivo(caminho_entrada):         
    
    arquivo = open(caminho_entrada, "r")            
    
    numero_processos = int(arquivo.readline().strip())
    pids = arquivo.readline().strip().split(";")
    informacoes_arquivo_entrada = [Informacoes_Arquivo_Entrada(numero_processos, pids)]
    
    lista_de_processos = []
    for linha in arquivo:
        parte = linha.strip().split(" ")
        processo = Lista_Processos(parte[0], parte[1]) 

        if processo.tipo == "aloca":
            processo.ua = parte[2]
        elif processo.tipo == "acessa":
            processo.end_log = parte[2]

        lista_de_processos.append(processo)

    arquivo.close()
    return processos, requisicoes



# Como invocar pelo terminar: python leitura.py [algoritmo (first | best | worst | buddy)] [caminho do arquivo]
# Exemplo: python leitura.py first ./exemplos_entrada/entrada001.txt
if __name__ == "__main__":

    algoritmo = sys.argv[1]
    caminho_entrada = sys.argv[2]
    
    caminho_entrada_refinado = caminho_entrada.replace("./exemplos_entrada/", "").replace(".txt", "")
    caminho_saida = f"log_{caminho_entrada_refinado}_{algoritmo}.txt"
    
    processos, requisicoes = ler_arquivo(caminho_entrada)
    
    #linha, tarefas = simular(tarefas, algoritmo)

    #salvar_saida(linha, tarefas, caminho_saida)