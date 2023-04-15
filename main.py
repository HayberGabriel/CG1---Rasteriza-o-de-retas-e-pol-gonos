import math
from math import *
from tkinter import messagebox
from PIL import Image
from random import *
import tkinter as tk

class Raster():
    # Inicializa a classe com a resolução inicial e todas as estruturas vazias
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.vertices = []
        self.arestas = []
        self.faces = []
        self.modelo = []

    # Adiciona novo vertice na lista de vertices se este já não existir
    def adiciona_vertice(self, x, y):
        # Checa se as coordenadas do vertice cabem no espaço
        if math.fabs(x) <= self.width / 2 and math.fabs(y) <= self.height / 2:
            for v in self.vertices:
                if v == [x, y]:
                    print("Vertice ", v, " já existe e não foi adicionado\n")
                    return
            self.vertices.append([x, y])
        else:
            input("Coordenadas do vertice não cabem no espaço")

    # Adiciona uma aresta na forma [v1, v2] onde v é a posição do vertice na lista de vertices
    def adiciona_aresta(self, v1, v2):
        if max(v1, v2) < len(self.vertices) and min(v1, v2) >= 0:
            if [v1, v2] in self.arestas:
                pass
            else:
                self.arestas.append([v1, v2])


        else:
            print(v1)
            print(v2)
            input("Aresta impossível")

    # Adiciona uma face a lista de faces na forma [v1, v2, ..., vn] onde v é a posição do vertice na
    # lista de vertices
    def adiciona_face(self, lista):
        # Uma face precisa ter pelo menos 3 vertices
        if len(lista) < 3:
            input("Face impossível")
        else:
            if max(lista) < len(self.vertices) and min(lista) >= 0:
                # Adiciona a face à lista de faces e coloca as arestas da borda na lista de arestas se já
                # não existirem
                self.faces.append(lista)
                for i in range(len(lista)):
                    # checa se existe uma aresta que vai do vertice A para o vertice B
                    # ou do vertice B para o vertice A
                    if i == len(lista) - 1:
                        if [lista[-1], lista[0]] not in self.arestas and [lista[0], lista[-1]] not in self.arestas:
                            self.arestas.append([lista[-1], lista[0]])
                    elif [lista[i], lista[i + 1]] not in self.arestas and [lista[i + 1], lista[i]] not in self.arestas:
                        self.arestas.append([lista[i], lista[i + 1]])
            else:
                input("Face impossível")

    # Deleta a lista de vertices, arestas e faces
    def reseta_espaço(self):
        self.vertices = []
        self.arestas = []
        self.faces = []

    # Lista os vertices da lista de vertices para facilitar a criação de arestas e faces
    def enum_vertices(self):
        print("Vertices:")
        for i, j in enumerate(self.vertices):
            print(i, j)

    # Altera a resolução do espaço e rearranja as coordenadas dos vertices de acordo com a mudança da resolução
    def altera_resolução(self, width, height):
        fatorx = width / self.width
        fatory = height / self.height
        self.width = width
        self.height = height
        for v in self.vertices:
            v[0] *= fatorx
            v[1] *= fatory

    # arredonda as coordenadas de um pixel e o adiciona a um modelo
    def produz_fragmento(self, x, y, modelo):
        xm = ceil(x)
        ym = ceil(y)
        p = [xm, ym]
        modelo.append(p)

    # Algoritmo par impar limitado ao espaço de um polígono
    def preenche_face(self, x_min, y_min, x_max, y_max, modelo_face):
        lista = []
        lista_aux = []
        for y in range(int(y_min) + 1, int(y_max), 1):
            count = 0
            ant = False  # pixel anterior pertence ao modelo?
            inside = False  # pixel está dentro de um poligono?

            for x in range(int(x_min), int(x_max) + 1, 1):
                # Soma o contador na transição de borda para espaço em branco
                if [x, y] not in modelo_face and ant:  # pixel fora do modelo mas pixel anterior era borda
                    count += 1
                if count % 2 != 0:
                    if [x, y] not in modelo_face:
                        lista_aux.append([x, y])
                    else:
                        inside = True  # Encontra borda enquanto pinta, portanto esta borda deve pertencer ao poligono
                if [x, y] in modelo_face:
                    ant = True
                else:
                    ant = False
            if inside:
                for i in lista_aux:
                    lista.append(i)
            lista_aux = []
        for v in lista:
            self.produz_fragmento(v[0], v[1], modelo_face)
        return modelo_face

    # Produz as bordas de uma face em um modelo alternativo
    def produz_modelo_face(self, vertices):
        modelo = []
        for aresta in [[i, j] for i in vertices for j in vertices if
                       j == i + 1 or (i == vertices[-1] and j == vertices[0])]:
            x1 = int(self.vertices[aresta[0]][0])  # Posição x do vertice aresta[0]
            y1 = int(self.vertices[aresta[0]][1])
            x2 = int(self.vertices[aresta[1]][0])
            y2 = int(self.vertices[aresta[1]][1])  # Posição y do vertice aresta[1]
            # Inicia o modelo da reta a partir do ponto inicial
            self.produz_fragmento(x1, y1, modelo)
            # Checa se dx não é 0
            if x2 - x1 != 0:
                # Coeficiente angular da reta
                m = (y2 - y1) / (x2 - x1)
                # Constante da reta
                b = y1 - (m * x1)
                # Se o intervalo entre as posições de x for maior ou igual a dy
                # percorre x e encontra y para cada valor de x
                if math.fabs(x2 - x1) >= math.fabs(y2 - y1):
                    xm = min(x1, x2)
                    x = xm
                    # Obtem o vertice com o menor valor de x e o percorre até o outro vertice
                    while x < xm + math.fabs(x2 - x1):
                        x += 1
                        y = (m * x) + b
                        self.produz_fragmento(x, y, modelo)
                # Se dy > dx, encontra x para cada valor de y
                else:
                    ym = min(y1, y2)
                    y = ym
                    while y < ym + math.fabs(y2 - y1):
                        y += 1
                        # Formula da reta adaptada para encontrar x
                        x = (y - b) / m
                        self.produz_fragmento(x, y, modelo)
            # Trata do caso da reta vertical (dx == 0)
            else:
                ym = min(y1, y2)
                y = ym
                while y < ym + math.fabs(y2 - y1):
                    y += 1
                    # Repete o valor de x enquanto percorre y
                    self.produz_fragmento(x1, y, modelo)
        return modelo

    # Carrega as arestas e as faces no modelo
    def produz_modelo(self):
        self.modelo = []
        # Coloca as arestas da lista de arestas no modelo
        for aresta in self.arestas:
            x1 = int(self.vertices[aresta[0]][0])  # Posição x do vertice aresta[0]
            y1 = int(self.vertices[aresta[0]][1])
            x2 = int(self.vertices[aresta[1]][0])
            y2 = int(self.vertices[aresta[1]][1])  # Posição y do vertice aresta[1]
            # Inicia o modelo da reta a partir do ponto inicial
            self.produz_fragmento(x1, y1, self.modelo)
            # Checa se dx não é 0
            if x2 - x1 != 0:
                # Coeficiente angular da reta
                m = (y2 - y1) / (x2 - x1)
                # Constante da reta
                b = y1 - (m * x1)
                # Se o intervalo entre as posições de x for maior ou igual a dy
                # percorre x e encontra y para cada valor de x
                if math.fabs(x2 - x1) >= math.fabs(y2 - y1):
                    xm = min(x1, x2)
                    x = xm
                    # Obtem o vertice com o menor valor de x e o percorre até o outro vertice
                    while x < xm + math.fabs(x2 - x1):
                        x += 1
                        y = (m * x) + b
                        self.produz_fragmento(x, y, self.modelo)
                # Se dy > dx, encontra x para cada valor de y
                else:
                    ym = min(y1, y2)
                    y = ym
                    while y < ym + math.fabs(y2 - y1):
                        y += 1
                        # Formula da reta adaptada para encontrar x
                        x = (y - b) / m
                        self.produz_fragmento(x, y, self.modelo)
            # Trata do caso da reta vertical (dx == 0)
            else:
                ym = min(y1, y2)
                y = ym
                while y < ym + math.fabs(y2 - y1):
                    y += 1
                    # Repete o valor de x enquanto percorre y
                    self.produz_fragmento(x1, y, self.modelo)
        # preenche as faces dos polígonos da lista de faces
        for face in self.faces:
            # Cria um espaço alternativo para cada face e preenche a face neste espaço
            # para evitar colisões
            modelo_face = self.produz_modelo_face(face)
            lista_vx = []
            lista_vy = []
            # Encontra todos o valores de x e y para cada vertice que define a face, e então encontra seus
            # valores mínimos e máximos
            for v in face:
                lista_vx.append(self.vertices[v][0])  # lista as posições de x para cada vertice da face
                lista_vy.append(self.vertices[v][1])  # lista as posições de y para cada vertice da face
            x_min = min(lista_vx)
            y_min = min(lista_vy)
            x_max = max(lista_vx)
            y_max = max(lista_vy)
            # Preenche uma das faces utilizando os limites dos vertices da face para delimitar o espaço
            modelo_face = self.preenche_face(x_min, y_min, x_max, y_max, modelo_face)
            # Copia os pixels do espaço alternativo para o modelo principal
            for pixel in modelo_face:
                self.produz_fragmento(pixel[0], pixel[1], self.modelo)

    # Desenha os pixels contidos no modelo
    def desenha_imagem(self):
        self.produz_modelo()
        img = Image.new("RGB", (self.width, self.height), "white")
        pixels = img.load()

        # Desenha o modelo com origem no centro da imagem
        for coords in self.modelo:
            pixels[(self.width / 2 + coords[0] - 1, self.height / 2 - coords[1])] = (255, 0, 0)
        img.show()

    def lista_modelo(self):
        for pixel in self.modelo:
            print(pixel)

    # Encontra as posições mínimas e máximas em uma lista de vertices
    def find_minimax(self, face):
        lista_vx = []
        lista_vy = []
        for v in face:
            lista_vx.append(self.vertices[v][0])
            lista_vy.append(self.vertices[v][1])
        x_min = min(lista_vx)
        x_max = max(lista_vx)
        y_min = min(lista_vy)
        y_max = max(lista_vy)
        return x_min, x_max, y_min, y_max

    def cria_poligono(self, tipo, base, x, y, ttl=100):

        if ttl == 0:
            return None

        match tipo:
            case 'quadrado':
                vertices = [[x, y], [x + base, y], [x + base, y + base], [x, y + base]]
                ind = [i for i in range(len(self.vertices), len(self.vertices) + 4)]
            case 'triangulo':
                vertices = [[x, y], [x + base, y], [x + (base / 2), y + sqrt(3) * (base / 2)]]
                ind = [i for i in range(len(self.vertices), len(self.vertices) + 3)]
            case 'hexagono':
                vertices = [[x, y], [x + base, y], [x + 3 * (base / 2), y + sqrt(3) * (base / 2)],
                            [x + base, y + sqrt(3) * base], [x, y + sqrt(3) * base],
                            [x - base / 2, y + sqrt(3) * (base / 2)]]
                ind = [i for i in range(len(self.vertices), len(self.vertices) + 6)]
            case _:
                return input("tipo invalido")

        # Trata de colisões
        for face in self.faces:
            x_min, x_max, y_min, y_max = self.find_minimax(face)
            pm_x = sum(vertices[i][0] for i in range(len(vertices))) / len(vertices)
            pm_y = sum(vertices[i][1] for i in range(len(vertices))) / len(vertices)
            pm_atual = [pm_x, pm_y]
            pm_face = [(x_max + x_min) / 2, (y_max + y_min) / 2]
            dist_aprox = sqrt((pm_atual[0] - pm_face[0]) ** 2 + (pm_atual[1] - pm_face[1]) ** 2)
            if tipo == 'hexagono':
                if dist_aprox < base * 2:
                    x = randint(int(-self.width / 2 + base / 2), int(self.width / 2 - 3 * (base / 2)))
                    y = randint(int(-self.height / 2 + 1), int(self.height / 2 - base * sqrt(3)))
                    return self.cria_poligono(tipo, base, x, y, ttl - 1)
            elif dist_aprox < 3 * base / 2:
                x = randint(int(-self.width / 2 + 1), int(self.width / 2 - base))
                y = randint(int(-self.height / 2 + 1), int(self.height / 2 - base))
                return self.cria_poligono(tipo, base, x, y, ttl - 1)
        return vertices, ind


if __name__ == '__main__':
    espaço = Raster(1920, 1080)

    while True:
        # Cria uma janela
        janela = tk.Tk()
        janela.title("Menu")
        from tkinter import simpledialog


        def menu_adiciona_vertice():
            # Exibe um diálogo para solicitar as coordenadas do novo vértice
            x = simpledialog.askfloat("Adicionar Vértice", "Coordenada X:")
            y = simpledialog.askfloat("Adicionar Vértice", "Coordenada Y:")

            # Verifica se as coordenadas são válidas
            if x is None or y is None:
                return

            espaço.adiciona_vertice(x, y)


        def menu_adiciona_aresta():
            int1 = simpledialog.askinteger("Escolha o número do vértice 1", "Vértice 1:")
            int2 = simpledialog.askinteger("Escolha o número do vértice 2", "Vértice 2:")

            if int1 is None or int2 is None:
                return

            espaço.adiciona_aresta(int1, int2)


        def menu_altera_resolução():
            width = simpledialog.askinteger("Escolha a largura", "Largura:")
            height = simpledialog.askinteger("Escolha a altura", "Altura:")

            espaço.altera_resolução(width, height)


        def menu_adiciona_face():

            faces = []
            v1 = simpledialog.askinteger("Escolha o vértice 1", "Vértice 1:")
            v2 = simpledialog.askinteger("Escolha o vértice 2", "Vértice 2:")
            v3 = simpledialog.askinteger("Escolha o vértice 3", "Vértice 3:")
            v4 = simpledialog.askinteger("Escolha o vértice 4", "Vértice 4 (Caso n tenha, digita -1):")
            v5 = simpledialog.askinteger("Escolha o vértice 5", "Vértice 5 (Caso n tenha, digita -1):")
            v6 = simpledialog.askinteger("Escolha o vértice 5", "Vértice 6 (Caso n tenha, digita -1):")

            faces.append(v1)
            faces.append(v2)
            faces.append(v3)

            if(v3 != -1): faces.append(v3)

            if (v4 != -1): faces.append(v4)

            if (v5 != -1): faces.append(v5)

            if (v6 != -1): faces.append(v6)

            espaço.adiciona_face(faces)


        botao_adicionar_vertice = tk.Button(janela, text="Adicionar Vertice", command=menu_adiciona_vertice)
        botao_adicionar_vertice.pack()

        botao_adicionar_aresta = tk.Button(janela, text="Adicionar Aresta", command=menu_adiciona_aresta)
        botao_adicionar_aresta.pack()

        botao_adicionar_face = tk.Button(janela, text="Adicionar Face", command=menu_adiciona_face)
        botao_adicionar_face.pack()

        botao_desenhar_modelo = tk.Button(janela, text="Desenhar Modelo", command=espaço.desenha_imagem)
        botao_desenhar_modelo.pack()

        botao_alterar_resolucao = tk.Button(janela, text="Alterar Resolução", command=menu_altera_resolução)
        botao_alterar_resolucao.pack()

        botao_resetar_modelo = tk.Button(janela, text="Resetar Modelo", command=lambda: confirmar_resetar_modelo())
        botao_resetar_modelo.pack()


        def confirmar_resetar_modelo():
            if messagebox.askyesno("Confirmação", "Tem certeza que deseja resetar o modelo?"):
                espaço.reseta_espaço()
                messagebox.showinfo("Modelo resetado", "O modelo foi resetado com sucesso.")


        # Inicia o loop principal da janela
        janela.mainloop()
