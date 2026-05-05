import sys

class Processos:
    def __init__(self, numero_processos, pids_liberados):
        self.numero_processos = int(numero_processos)
        self.pids_liberados = list(pids_liberados)

class Requisicao:
    def __init__(self, tipo, pid, valor=None):
        self.tipo = tipo
        self.pid = pid
        self.valor = valor

def ler_arquivo(caminho_entrada):                   #recebe o caminho do arquivo de entrada
    
    arquivo = open(caminho_entrada, "r")            
    
    numero_processos = int(arquivo.readline().strip())
    pids = arquivo.readline().strip().split(";")
    processos = [Processos(numero_processos, pids)]
    
    requisicoes = []
    for linha in arquivo:
        parte = linha.strip().split(" ")
        requisicao = Requisicao(parte[0], parte[1]) 

        if requisicao.tipo == "aloca":
            requisicao.valor = parte[2]
        elif parte[0] == "acessa":
            requisicao.valor = parte[2]

        requisicoes.append(requisicao)

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

    for i in processos:
        print(f"{i.numero_processos} {i.pids_liberados}")
    
    for i in requisicoes:
        print(f"{i.tipo} {i.pid} {i.valor}")
    
    #linha, tarefas = simular(tarefas, algoritmo)

    #salvar_saida(linha, tarefas, caminho_saida)