import random
import heapq


class Cidade:

    def __init__(self, numero, x_coord, y_coord):
        self.numero = numero
        self.x_coord = x_coord
        self.y_coord = y_coord


cidades = [
    Cidade(1, 565.0, 575.0),
    Cidade(2, 25.0, 185.0),
    Cidade(3, 345.0, 750.0),
    Cidade(4, 945.0, 685.0),
    Cidade(5, 845.0, 655.0),
    Cidade(6, 845.0, 25.0),
    Cidade(7, 25.0, 5.0),
    Cidade(8, 125.0, 925.0),
    Cidade(9, 835.0, 855.0),
    Cidade(10, 25.0, 805.0),
]


class AlgoritmoGenetico:

    # O caminho é o conjunto de genes. E cada gene é uma cidade/vértice.
    caminho = []
    inicializa_populacao = []
    valor_fit = -1
    populacao = []
    tamanho_populacao = 50
    qtd_cidades = len(cidades)

    def __lt__(self, other):
        return self.fit() < other.fit()

    def fit(self):
        '''
        Calcula o fitness do caminho. O fitness é o valor da distância total do caminho.
        O menor fitness é o melhor caminho.
        '''
        global cidades

        if self.valor_fit == -1:
            soma = 0
            for x in range(self.qtd_cidades - 1):
                vertice_um = cidades[self.caminho[x] - 1]
                vertice_dois = cidades[self.caminho[x+1] - 1]

                soma += abs((vertice_um.x_coord - vertice_dois.x_coord)
                            + (vertice_um.y_coord - vertice_dois.y_coord))

            vertice_um_origem = cidades[self.caminho[0] - 1]
            vertice_dois_origem = cidades[self.caminho[self.qtd_cidades - 1] - 1]

            soma += abs((vertice_um_origem.x_coord - vertice_dois_origem.x_coord)
                        + (vertice_um_origem.y_coord - vertice_dois_origem.y_coord))

            self.valor_fit = soma

        return self.valor_fit

    def gera_populacao(self):
        '''
        Gera os cromossomos iniciais.
        Para cada invididuo da população, gera um cromossomo.
        '''
        self.inicializa_populacao = list(
            range(1, self.qtd_cidades + 1))
        for _ in range(self.tamanho_populacao):
            cromossomo = AlgoritmoGenetico()
            cromossomo.caminho = self.inicializa_populacao[:]
            random.shuffle(cromossomo.caminho)  # Embaralha o cromossomo
            # Insere o cromossomo na população
            heapq.heappush(self.populacao, cromossomo)
        return self.populacao

    def seleciona_individuo(self, individuos_da_populacao):
        '''
        Seleciona o individuo com o melhor fitness randomicamente.
        Pega os dois melhores individuos para gera um novo individuo a partir de um cruzamento.
        '''
        valor_um = random.randrange(self.tamanho_populacao//2)
        valor_dois = random.randrange(
            self.tamanho_populacao//2, self.tamanho_populacao)

        if individuos_da_populacao[valor_um].fit() < individuos_da_populacao[valor_dois].fit():
            return individuos_da_populacao[valor_um]
        else:
            return individuos_da_populacao[valor_dois]

    def mutacao_individuo(self, caminho_do_novo_filho):
        '''
        Realiza a mutação de um individuo. 
        Seleciona dois genes e troca de lugar.
        '''
        gene1 = random.randrange(self.qtd_cidades - 1)
        gene2 = random.randrange(gene1, self.qtd_cidades - 1)

        caminho_do_novo_filho[gene1], caminho_do_novo_filho[
            gene2] = caminho_do_novo_filho[gene2], caminho_do_novo_filho[gene1]

        return caminho_do_novo_filho

    def cruzamento(self, qtd_geracao):
        '''
        Realiza o cruzamento dos individuos.
        Adiciona caracteristicas dos individuos selecionados a partir de um cruzamento.
        '''

        novos_individuos = []

        tam_corte = int(self.qtd_cidades * 0.90)

        # Realiza a seleção dos individuos
        individuo1 = self.seleciona_individuo(self.populacao)
        individuo2 = self.seleciona_individuo(self.populacao)

        # Corta o cromossomo e adicona os valores do pai que ainda não estão no filho.
        for _ in range(qtd_geracao):
            qtd_genes_adicionados = 0

            gene_dos_pais_para_filho = individuo1.caminho[:tam_corte]

            for ind_2 in individuo2.caminho:
                if (ind_2 not in gene_dos_pais_para_filho):
                    gene_dos_pais_para_filho.append(ind_2)
                    qtd_genes_adicionados += 1
                if (qtd_genes_adicionados == (self.qtd_cidades - tam_corte)):
                    break

            # Mutação que gera indivíduos diferentes e mantenha a diversidade
            gene_dos_pais_para_filho = self.mutacao_individuo(
                gene_dos_pais_para_filho)

            novo_individuo = AlgoritmoGenetico()
            novo_individuo.caminho = gene_dos_pais_para_filho

            novos_individuos.append(novo_individuo)

        return novos_individuos

    def atualiza_populacao(self, individuos_da_populacao, lista_novos_individuos):
        '''
        Atualiza a população.
        Percorre os individuos da população e verifica se o individuo é o melhor.
        Se não for, o individuo é removido.
        '''
        qtd_tentativas = 0

        for x in lista_novos_individuos:

            individuo_maior_fit = heapq.nlargest(1, individuos_da_populacao)[0]
            menor = individuos_da_populacao[0]
            x_fit = x.fit()
            if x_fit < individuo_maior_fit.fit():
                individuos_da_populacao.remove(individuo_maior_fit)
                heapq.heappush(individuos_da_populacao, x)
                heapq.heapify(individuos_da_populacao)

                if x_fit < menor.fit():
                    # Controle de tentativas, se gerar individuos ruins, para.
                    qtd_tentativas = 0
                else:
                    qtd_tentativas += 1
            else:
                qtd_tentativas += 1

            if qtd_tentativas == 1000:
                break

        return individuos_da_populacao

    def obter_melhor_individuo(self, individuos_da_populacao):
        '''
        Obtém o melhor individuo da população.
        '''
        return heapq.nsmallest(1, individuos_da_populacao)[0]

    def obter_pior_individuo(self, individuos_da_populacao):
        '''
        Obtém o pior individuo da população.
        '''
        return heapq.nlargest(1, individuos_da_populacao)[0]

    def print_individuos(self, individuos_da_populacao):
        '''
        Imprime os individuos da população.
        '''
        for key, value in enumerate(individuos_da_populacao):
            print(key+1, "ª indivíduo:", value.caminho,
                  " | Fitness:", value.fit(), "\n")


cromossomo = AlgoritmoGenetico()
populacao = cromossomo.gera_populacao()
novosIndividuosGerados = cromossomo.cruzamento(50)
populacao = cromossomo.atualiza_populacao(populacao, novosIndividuosGerados)
cromossomo.print_individuos(populacao)
print("Melhor indivíduo: (Menor distância)",
      cromossomo.obter_melhor_individuo(populacao).fit())
print("Pior indivíduo: (Maior distância)",
      cromossomo.obter_pior_individuo(populacao).fit())
