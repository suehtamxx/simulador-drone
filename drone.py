import math

class Drone:
    """Representa um drone individual na simulação."""

    def __init__(self, id_drone, pos_x, pos_y, dest_x, dest_y, velocidade=1.5):
        self.id = id_drone
        self.x = float(pos_x)
        self.y = float(pos_y)
        self.dest_x = float(dest_x)
        self.dest_y = float(dest_y)
        self.velocidade = velocidade
        self.status = "em_voo"  # 'em_voo', 'chegou', 'colidiu', 'destruido'
        self.raio = 6

        # --- Métricas por drone ---
        self.distancia_percorrida = 0.0
        self.tempo_chegada = None  # Segundos (excluindo pausas) até chegar ao destino

        # --- Animação de explosão ---
        self.raio_explosao = float(self.raio)
        self.max_raio_explosao = 24

    # ------------------------------------------------------------------
    def mover(self):
        """Move o drone em direção ao seu destino."""
        if self.status != "em_voo":
            return

        dist_x = self.dest_x - self.x
        dist_y = self.dest_y - self.y
        distancia = math.hypot(dist_x, dist_y)

        if distancia < 2.0:
            # Chegou — acumula o trecho final antes de parar
            self.distancia_percorrida += distancia
            self.x, self.y = self.dest_x, self.dest_y
            self.status = "chegou"
            return

        # Acumula distância e move na direção do destino
        self.distancia_percorrida += self.velocidade
        self.x += (dist_x / distancia) * self.velocidade
        self.y += (dist_y / distancia) * self.velocidade

    # ------------------------------------------------------------------
    def calcular_distancia(self, outro):
        """Distância euclidiana até outro drone."""
        return math.hypot(self.x - outro.x, self.y - outro.y)
