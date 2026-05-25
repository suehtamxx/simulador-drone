import math
import sys
from time import time, sleep
import pygame
import random

#---- TELA ----
largura_tela = 800
altura_tela = 600
fps = 60

#---- CORES ----
branco = (255, 255, 255)
azul = (0, 120, 255)
verde = (0, 200, 0)
vermelho = (220, 0, 0)
cinza = (150, 150, 150)
laranja = (255, 140, 0)

class Drone:
    def __init__(self, id_drone, pos_x, pos_y, dest_x, dest_y, velocidade = 1.0):
        self.id = id_drone
        self.x = float(pos_x)
        self.y = float(pos_y)
        self.dest_x = float(dest_x)
        self.dest_y = float(dest_y)
        self.velocidade = velocidade
        self.status = "em_voo"  # 'em_voo', 'chegou', 'colidiu'
        self.raio = 6
        
        self.raio_explosao = 6
        self.max_raio_explosao = 20

    def mover(self):
        """Move o drone em direção ao seu destino."""
        if self.status != "em_voo":
            return  # O drone não se move se não estiver em voo

        dist_x = self.dest_x - self.x
        dist_y = self.dest_y - self.y
        distancia = math.hypot(dist_x, dist_y)

        if distancia < 2.0:
            # Chegou ao destino
            self.x, self.y = self.dest_x, self.dest_y
            self.status = "chegou"
            return
       
        # Move na direção do destino
        self.x += (dist_x / distancia) * self.velocidade
        self.y += (dist_y / distancia) * self.velocidade

    def desenhar(self, tela):
        # 1. Se o drone foi totalmente destruído, não desenha mais nada (exclui visualmente)
        if self.status == "destruido":
            return

        # Desenhar o destino (um pequeno quadrado cinza)
        pygame.draw.rect(tela, cinza, (self.dest_x - 3, self.dest_y - 3, 6, 6))
        
        # 2. Lógica da Explosão
        if self.status == "colidiu":
            # Animação do círculo crescendo
            if self.raio_explosao < self.max_raio_explosao:
                self.raio_explosao += 1.5 # Velocidade da expansão
                
                # Desenha a bola de fogo (Laranja) e os destroços (Vermelho)
                pygame.draw.circle(tela, laranja, (int(self.x), int(self.y)), int(self.raio_explosao))
                pygame.draw.circle(tela, vermelho, (int(self.x), int(self.y)), self.raio)
            else:
                # 3. Quando a explosão atinge o limite, muda o status para sumir no próximo frame
                self.status = "destruido"
            
            return # Sai da função para não desenhar o drone normal

        # Cores normais de voo ou chegada
        if self.status == "em_voo":
            cor = azul
        elif self.status == "chegou":
            cor = verde

        # Desenhar o drone normal (um círculo)
        pygame.draw.circle(tela, cor, (int(self.x), int(self.y)), self.raio)

    def calcular_distancia(self, outro_drone):
        """Calcula a distância euclidiana entre este drone e outro drone."""
        return math.hypot(self.x - outro_drone.x, self.y - outro_drone.y)

    
class SimuladorDrones:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((largura_tela, altura_tela))
        pygame.display.set_caption("Simulador de Drones - Modelagem Analítica")
        self.relogio = pygame.time.Clock()
        self.drones = []
        self.metricas = {"colisao": 0}
        
    def adicionar_drone(self, drone):
        """Adiciona um drone à simulação."""
        self.drones.append(drone)

    def checar_colisoes(self):
        """Verifica se houve colisões entre os drones."""

        for i in range(len(self.drones)):
            for j in range(i + 1, len(self.drones)):
                if self.drones[i].status == "em_voo" and self.drones[j].status == "em_voo":
                    if self.drones[i].calcular_distancia(self.drones[j]) < 12.0:
                        self.metricas["colisao"] += 2
                        self.drones[i].status = "colidiu"
                        self.drones[j].status = "colidiu"

    def executar(self):
        rodando = True

        while rodando:
            self.relogio.tick(fps)
            self.tela.fill(branco)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
            
            for drone in self.drones:
                drone.mover()

            self.checar_colisoes()
            for drone in self.drones:
                drone.desenhar(self.tela)
            
            pygame.display.flip()

            simulacao_ativa = any(d.status in ["em_voo", "colidiu"] for d in self.drones)
            
            if not simulacao_ativa and len(self.drones) > 0:
                print("Simulação concluída! Fechando a interface...")
                rodando = False

        self.imprimir_metricas()

        pygame.quit()
        sys.exit()

    def imprimir_metricas(self):
        """Calcula e exibe as métricas obrigatórias no terminal."""
        total_drones = len(self.drones)
        
        if total_drones == 0:
            print("Nenhum drone instanciado.")
            return

        # Conta quantos drones estão em cada estado final
        chegaram = sum(1 for d in self.drones if d.status == "chegou")
        colidiram = sum(1 for d in self.drones if d.status in ["colidiu", "destruido"])
        
        # Quem não concluiu é o total menos os que chegaram com sucesso
        nao_concluiram = total_drones - chegaram 

        print("\n" + "="*50)
        print("RELATÓRIO FINAL DA SIMULAÇÃO - MÉTRICAS")
        print("="*50)
        print(f"Total de Drones no Cenário: {total_drones}")
        print(f"Drones que chegaram ao destino: {chegaram}")
        print(f"Drones que colidiram: {colidiram}")
        print(f"Drones que não concluíram a missão: {nao_concluiram}")
        
        # Métrica extra opcional sugerida no documento
        taxa_sucesso = (chegaram / total_drones) * 100
        print(f"Percentual de sucesso das missões: {taxa_sucesso:.1f}%")
        print("="*50 + "\n")

    def gerar_drones_aleatorios(self, quantidade):
        """Gera N drones com posições, destinos e velocidades aleatórias."""
        for i in range(quantidade):
            # Sorteia posições respeitando uma margem de 20 pixels da borda
            x_ini = random.randint(20, largura_tela - 20)
            y_ini = random.randint(20, altura_tela - 20)
            
            x_dest = random.randint(20, largura_tela - 20)
            y_dest = random.randint(20, altura_tela - 20)
            
            # Dá uma leve variada na velocidade (entre 1.0 e 2.5) para ficar mais realista
            vel = random.uniform(1.0, 2.5)
            
            # Cria e adiciona o drone
            novo_drone = Drone(i + 1, x_ini, y_ini, x_dest, y_dest, velocidade=vel)
            self.adicionar_drone(novo_drone)
if __name__ == "__main__":
    print("\n" + "="*40)
    print("CONFIGURAÇÃO DO SIMULADOR")
    print("="*40)
    
    # Captura a entrada do usuário no terminal
    try:
        qtd = int(input("Digite a quantidade de drones para simular: "))
    except ValueError:
        print("Valor inválido. Iniciando com 15 drones por padrão.")
        qtd = 15

    print("Iniciando interface gráfica.")
    
    # Instancia e roda o simulador
    simulador = SimuladorDrones()
    simulador.gerar_drones_aleatorios(qtd)
    simulador.executar()