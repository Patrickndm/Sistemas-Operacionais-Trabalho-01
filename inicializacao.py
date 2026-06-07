import sys

class Entrada:
    def __init__(self, numero_pids, pids):
        self.numero_pids = int(numero_pids)  # quantidade de processos
        self.pids = list(pids)               # lista com os PIDs

class Bloco_Requisicao:
    def __init__(self, tipo, pid):
        self.tipo = str(tipo)           # "aloca", "libera" ou "acessa"
        self.pid = str(pid)
        self.ua = None                  # preenchido só se for alocação
        self.endereco_logico = None     # preenchido só se for acesso
    def alocar(self, ua):
        self.ua = int(ua)
    def acessar(self, endereco_logico):
        self.endereco_logico = int(endereco_logico)

class Bloco_RAM:
    def __init__(self):
        self.alocado = False  # se essa UA está ocupada
        self.pid = None       # quem está ocupando
    def alocar(self, pid):
        self.alocado = True
        self.pid = pid
    def desalocar(self):
        self.alocado = False
        self.pid = None

class Bloco_Particao:
    def __init__(self, pid, inicio, limite):
        self.pid = str(pid)
        self.inicio = int(inicio)         # endereço físico onde começa
        self.limite = int(limite)         # tamanho em UAs
        self.fim = (inicio + limite) - 1  # endereço físico onde termina

class Bloco_Livre:
    def __init__(self, inicio=0, limite=4096, par_buddy_indice=None):
        self.inicio = int(inicio)
        self.limite = int(limite)
        self.fim = (inicio + limite) - 1
        self.par_buddy_indice = int(par_buddy_indice) if par_buddy_indice is not None else None  # índice do buddy, usado na estratégia buddy

class Simulador:
    def __init__(self, entrada, requisicoes):
        self.Entrada = entrada
        self.Lista_Processos = requisicoes
        self.RAM = [Bloco_RAM() for _ in range(4096)]  # memória física com 4096 posições
        self.Tabela_Particao = []                       # regiões atualmente alocadas
        self.Tabela_Livre = [Bloco_Livre()]             # começa com a memória toda livre

    def alocar(self, processo, indice_livre):
        # se encontrou um bloco livre válido, faz a alocação; senão, retorna erro
        if indice_livre is not None:
            inicio_ocupado = self.Tabela_Livre[indice_livre].inicio
            self.alocar_Tabela_Livre(processo, indice_livre)
            self.alocar_RAM(processo, inicio_ocupado)
            indice_ocupado = self.alocar_Tabela_Particao(processo, inicio_ocupado)
            return f"alocacao {processo.pid} {self.Tabela_Particao[indice_ocupado].inicio} {self.Tabela_Particao[indice_ocupado].fim}"
        else:
            return f"alocacao {processo.pid} erro!"

    def alocar_RAM(self, processo, inicio_ocupado):
        # marca cada UA do intervalo alocado como ocupada
        for i in range(inicio_ocupado, inicio_ocupado + processo.ua):
            self.RAM[i].alocar(processo.pid)

    def alocar_Tabela_Livre(self, processo, indice_livre):
        # se o bloco é maior que o necessário, o que sobrar vira um novo bloco livre
        if self.Tabela_Livre[indice_livre].limite > processo.ua:
            self.Tabela_Livre.insert(
                indice_livre,
                Bloco_Livre(
                    self.Tabela_Livre[indice_livre].inicio + processo.ua,
                    self.Tabela_Livre[indice_livre].limite - processo.ua
                )
            )
        self.Tabela_Livre.pop(indice_livre + 1)  # remove o bloco que foi consumido

    def alocar_Tabela_Particao(self, processo, inicio_ocupado):
        # insere a nova partição na posição certa para manter a ordem por endereço
        indice_ocupado = len(self.Tabela_Particao)
        for i in range(len(self.Tabela_Particao)):
            if inicio_ocupado < self.Tabela_Particao[i].inicio:
                self.Tabela_Particao.insert(i, Bloco_Particao(processo.pid, inicio_ocupado, processo.ua))
                indice_ocupado = i
                break
        else:
            self.Tabela_Particao.append(Bloco_Particao(processo.pid, inicio_ocupado, processo.ua))
        return indice_ocupado

    def desalocar(self, requisicao):
        # acha a partição do processo, libera tudo e tenta juntar com blocos livres vizinhos
        for particao in self.Tabela_Particao:
            if particao.pid == requisicao.pid:
                inicio, limite = particao.inicio, particao.limite
                self.desalocar_RAM(particao)
                self.Tabela_Particao.remove(particao)
                indice = self.desalocar_Tabela_Livre(inicio, limite)
                self.mesclar_Tabela_Livre(indice)
                return f"liberacao {requisicao.pid} {inicio} {inicio + limite - 1}"

    def desalocar_RAM(self, particao):
        # libera cada UA que estava ocupada por essa partição
        for i in range(particao.inicio, particao.inicio + particao.limite):
            self.RAM[i].desalocar()

    def desalocar_Tabela_Livre(self, inicio, limite):
        # reinsere o bloco liberado na tabela livre, mantendo a ordem crescente de endereço
        for i, espaco_livre in enumerate(self.Tabela_Livre):
            if inicio + limite - 1 < espaco_livre.inicio:
                self.Tabela_Livre.insert(i, Bloco_Livre(inicio, limite))
                return i
        self.Tabela_Livre.append(Bloco_Livre(inicio, limite))
        return len(self.Tabela_Livre) - 1

    def mesclar_Tabela_Livre(self, indice):
        # tenta fundir o bloco recém-liberado com os vizinhos enquanto forem contíguos
        mesclou = True
        while mesclou:
            mesclou = False
            if indice + 1 < len(self.Tabela_Livre):
                atual = self.Tabela_Livre[indice]
                prox  = self.Tabela_Livre[indice + 1]
                if atual.inicio + atual.limite == prox.inicio:  # próximo começa onde atual termina
                    atual.limite += prox.limite
                    atual.fim = atual.inicio + atual.limite - 1
                    self.Tabela_Livre.pop(indice + 1)
                    mesclou = True
            if indice - 1 >= 0:
                ant   = self.Tabela_Livre[indice - 1]
                atual = self.Tabela_Livre[indice]
                if ant.inicio + ant.limite == atual.inicio:  # atual começa onde anterior termina
                    ant.limite += atual.limite
                    ant.fim = ant.inicio + ant.limite - 1
                    self.Tabela_Livre.pop(indice)
                    indice -= 1
                    mesclou = True

    def acessar(self, processo):
        # traduz o endereço lógico para físico; se passar do limite da partição, é violação
        for particao in self.Tabela_Particao:
            if particao.pid == processo.pid and processo.endereco_logico < particao.limite:
                return f"acesso {processo.pid} {processo.endereco_logico} {particao.inicio + processo.endereco_logico}"
        return f"acesso {processo.pid} {processo.endereco_logico} violacao"


def ler_arquivo(caminho_entrada):
    # lê o arquivo linha por linha e monta a lista de requisições
    arquivo = open(caminho_entrada, "r")
    entrada = Entrada(arquivo.readline().strip(), arquivo.readline().strip().split(";"))
    requisicoes = []
    for linha in arquivo:
        parte = linha.strip().split(" ")
        requisicao = Bloco_Requisicao(parte[0], parte[1])
        if requisicao.tipo == "aloca":
            requisicao.alocar(parte[2])
        elif requisicao.tipo == "acessa":
            requisicao.acessar(parte[2])
        requisicoes.append(requisicao)
    simulador = Simulador(entrada, requisicoes)
    arquivo.close()
    return simulador


def estrategia_first(simulador, processo):
    # pega o primeiro bloco que couber, sem critério de tamanho
    indice_livre = None
    for i, espaco_livre in enumerate(simulador.Tabela_Livre):
        if processo.ua <= espaco_livre.limite:
            indice_livre = i
            break
    return simulador.alocar(processo, indice_livre)

def estrategia_best(simulador, processo):
    # procura o bloco que desperdiça menos espaço
    indice_livre = None
    restante = 4097
    for i, espaco in enumerate(simulador.Tabela_Livre):
        if processo.ua <= espaco.limite and espaco.limite - processo.ua < restante:
            indice_livre = i
            restante = espaco.limite - processo.ua
    return simulador.alocar(processo, indice_livre)

def estrategia_worst(simulador, processo):
    # pega o maior bloco disponível para deixar sobras maiores
    indice_livre = None
    restante = -1
    for i, espaco in enumerate(simulador.Tabela_Livre):
        if processo.ua <= espaco.limite and espaco.limite - processo.ua > restante:
            indice_livre = i
            restante = espaco.limite - processo.ua
    return simulador.alocar(processo, indice_livre)

""" PARA FAZER. APRESENTA PROBLEMA DE LÓGICA.
def estrategia_buddy(simulador, processo):
    # ajusta o tamanho pedido para a potência de 2 mais próxima acima
    potencia = 1
    while potencia < processo.ua:
        potencia *= 2
    processo.ua = potencia

    if processo.ua > 4096:  # impossível alocar acima do tamanho da RAM
        return simulador.alocar(processo, None)

    # tenta achar um bloco livre do tamanho exato
    for i, espaco in enumerate(simulador.Tabela_Livre):
        if espaco.limite == processo.ua:
            return simulador.alocar(processo, i)

    # se não achou, pega o menor bloco maior e vai dividindo ao meio até chegar no tamanho certo
    for i, espaco in enumerate(simulador.Tabela_Livre):
        if espaco.limite > processo.ua:
            while espaco.limite > processo.ua:
                metade = espaco.limite // 2
                espaco.limite = metade
                espaco.fim = espaco.inicio + espaco.limite - 1
                simulador.Tabela_Livre.insert(i + 1, Bloco_Livre(espaco.inicio + metade, metade))
            return simulador.alocar(processo, i)

    return simulador.alocar(processo, None) """


def salvar_saida(resultado, caminho_saida):
    with open(caminho_saida, "a") as arquivo:  # append: cada linha é adicionada ao final
        arquivo.write(resultado + "\n")


if __name__ == "__main__":

    algoritmo = sys.argv[1]       # first, best, worst ou buddy
    caminho_entrada = sys.argv[2]
    caminho_entrada_refinado = caminho_entrada.replace("./exemplos_entrada/", "").replace(".txt", "")
    caminho_saida = f"log_{caminho_entrada_refinado}_{algoritmo}.txt"

    simulador = ler_arquivo(caminho_entrada)

    for requisicao in simulador.Lista_Processos:
        match (requisicao.tipo, algoritmo):
            case ("aloca", "first"):
                resultado = estrategia_first(simulador, requisicao)
            case ("aloca", "best"):
                resultado = estrategia_best(simulador, requisicao)
            case ("aloca", "worst"):
                resultado = estrategia_worst(simulador, requisicao)
            # Pra fazer: descomentar quando estrategia_buddy, alocar_buddy e desalocar_buddy estiver pronto
            #case ("aloca", "buddy"):
            #    resultado = estrategia_buddy(simulador, requisicao)
            #case ("libera", "buddy"):
            #    resultado = simulador.desalocar_buddy(requisicao)
            case ("libera", _):
                resultado = simulador.desalocar(requisicao)
            case ("acessa", _):
                resultado = simulador.acessar(requisicao)

        salvar_saida(resultado, caminho_saida)

        if resultado.split()[-1] == "erro!":  # alocação falhou, encerra tudo
            break