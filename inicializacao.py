import sys

class Entrada:
    def __init__(self, numero_pids, pids):
        self.num_pids = int(numero_pids)
        self.pids = list(pids)

class Bloco_Processo:
    def __init__(self, tipo, pid):
        self.tipo = str(tipo)
        self.pid = str(pid)
        self.ua = None
        self.end_log = None

    def alocar(self, ua):
        self.ua = int(ua)
    
    def acessar(self, end_log):
        self.end_log = int(end_log)

class Bloco_RAM:
    def __init__(self):
        self.alocado = False
        self.pid = None
        
    def alocar(self, pid):
        self.alocado = True
        self.pid = pid

    def desalocar(self):
        self.alocado = False
        self.pid = None

    def __repr__(self):
        return "Alocado" if self.alocado else "Desalocado"
    
class Bloco_Tabela:
    def __init__(self):
        self.pid = None
        self.base = None
        self.limite = None

    def informar_pid(self, pid):
        self.pid = str(pid)
    
    def informar_base(self, base):
        self.base = int(base)
    
    def informar_limite(self, limite):
        self.limite = int(limite)
    
class Simulador:
    def __init__(self, processos, entrada):
        self.Entrada = entrada
        
        self.Lista_de_Processos = processos
        
        self.RAM = []
        for _ in range(4096):
            self.RAM.append(Bloco_RAM())

        self.Tabela_de_Particoes = []
        for _ in range(entrada.num_pids):
            self.Tabela_de_Particoes.append(Bloco_Tabela())

def ler_arquivo(caminho_entrada):         
    
    arquivo = open(caminho_entrada, "r")            
    
    entrada = Entrada(int(arquivo.readline().strip()), arquivo.readline().strip().split(";"))
    
    processos = []
    for linha in arquivo:
        parte = linha.strip().split(" ")
        processo = Bloco_Processo(parte[0], str(parte[1])) 

        if processo.tipo == "aloca":
            processo.alocar(parte[2])
        elif processo.tipo == "acessa":
            processo.acessar(parte[2])
        processos.append(processo)
    
    simulador = Simulador(processos, entrada)
    arquivo.close()
    
    return simulador


# Como invocar pelo terminar: python leitura.py [algoritmo (first | best | worst | buddy)] [caminho do arquivo]
# Exemplo: python leitura.py first ./exemplos_entrada/entrada001.txt
if __name__ == "__main__":

    algoritmo = sys.argv[1]
    caminho_entrada = sys.argv[2]
    
    simulador = ler_arquivo(caminho_entrada)
    
    #simulador = iniciar_simulacao(processos, entrada)

    #caminho_entrada_refinado = caminho_entrada.replace("./exemplos_entrada/", "").replace(".txt", "")
    #caminho_saida = f"log_{caminho_entrada_refinado}_{algoritmo}.txt"
    #salvar_saida(linha, tarefas, caminho_saida)