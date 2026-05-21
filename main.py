import math

class Drone:
    def __init__(self, id_drone, pos_x, pos_y, dest_x, dest_y, velocidade = 1.0):
        self.id = id_drone
        self.x = pos_x
        self.y = pos_y
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.velocidade = velocidade
        self.status = "em_voo"  # 'em_voo', 'chegou', 'colidiu'

    def mover(self):
        """Move o drone em direção ao seu destino."""
        if self.status != "em_voo":
            return  # O drone não se move se não estiver em voo

        dx = self.dest_x - self.x
        dy = self.dest_y - self.y
        distancia = math.sqrt(dx ** 2 + dy ** 2)

        if distancia < self.velocidade:
            # Chegou ao destino
            self.x = self.dest_x
            self.y = self.dest_y
            self.status = "chegou"
        else:
            # Move na direção do destino
            self.x += (dx / distancia) * self.velocidade
            self.y += (dy / distancia) * self.velocidade

    def calcular_distancia(self, outro_drone):
        """Calcula a distância euclidiana entre este drone e outro drone."""
        return math.sqrt((self.x - outro_drone.x) ** 2 + (self.y - outro_drone.y) ** 2)
    
class SimuladorDrones:
    def __init__(self, num_drones):
        self.drones = []
        # Métricas
        self.metricas = {
            "colisao": 0,
            "chegaram": 0,
            "nao_concluiram": num_drones 
        }
        
    def adicionar_drone(self, drone):
        """Adiciona um drone à simulação."""
        self.drones.append(drone)

    def checar_colisoes(self):
        """Verifica se houve colisões entre os drones."""

        for i in range(len(self.drones)):
            for j in range(i + 1, len(self.drones)):
                if self.drones[i].calcular_distancia(self.drones[j]) < 1.0:  # Distância mínima para colisão
                    self.metricas["colisao"] += 1
                    self.drones[i].status = "colidiu"
                    self.drones[j].status = "colidiu"

    def executar(self):
        # Loop principal do simulador (o tempo passando)
        # 1. Mover drones
        # 2. Checar colisões
        # 3. Atualizar visualização
        # 4. Registrar eventos
        pass
