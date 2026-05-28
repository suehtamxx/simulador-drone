import random
from time import time
from drone import Drone


class SimuladorDrones:
    """
    Gerencia toda a lógica da simulação:
    drones, detecção de colisões, métricas e controle de pausa.
    """

    def __init__(self):
        self.drones = []
        self.passos = 0
        self.tempo_inicio = None
        self.tempo_fim = None
        # Controle de pausa (para excluir do cálculo de tempo)
        self._pausa_inicio = None
        self._pausa_acumulada = 0.0

    # ------------------------------------------------------------------ #
    # Ciclo de vida                                                        #
    # ------------------------------------------------------------------ #

    def resetar(self):
        """Reinicia todos os dados para uma nova simulação."""
        self.drones.clear()
        self.passos = 0
        self.tempo_inicio = None
        self.tempo_fim = None
        self._pausa_inicio = None
        self._pausa_acumulada = 0.0

    def adicionar_drone(self, drone):
        self.drones.append(drone)

    def iniciar(self):
        """Marca o início oficial da simulação (quando PLAY é clicado)."""
        self.tempo_inicio = time()

    def pausar(self):
        """Registra o instante em que a simulação foi pausada."""
        if self._pausa_inicio is None and self.tempo_inicio is not None:
            self._pausa_inicio = time()

    def retomar(self):
        """Acumula o tempo pausado e retoma a contagem."""
        if self._pausa_inicio is not None:
            self._pausa_acumulada += time() - self._pausa_inicio
            self._pausa_inicio = None

    def finalizar(self):
        """Garante que tempo_fim é definido (ex: usuário fecha a janela)."""
        if self.tempo_fim is None and self.tempo_inicio is not None:
            self.tempo_fim = time()

    # ------------------------------------------------------------------ #
    # Loop de atualização (chamado a cada frame enquanto 'rodando')        #
    # ------------------------------------------------------------------ #

    def atualizar(self):
        """
        Executa um passo da simulação.
        Retorna True se a simulação ainda tem drones ativos.
        """
        if self.tempo_inicio is None:
            return True  # Não iniciada

        self.passos += 1
        # Tempo de simulação (excluindo pausas)
        tempo_atual = time() - self.tempo_inicio - self._pausa_acumulada

        for drone in self.drones:
            era_voo = drone.status == "em_voo"
            drone.mover()
            if era_voo and drone.status == "chegou":
                drone.tempo_chegada = tempo_atual

        self._checar_colisoes()

        ativa = self.esta_ativa()
        if not ativa and self.tempo_fim is None:
            self.tempo_fim = time()
        return ativa

    # ------------------------------------------------------------------ #
    # Lógica interna                                                       #
    # ------------------------------------------------------------------ #

    def _checar_colisoes(self):
        for i in range(len(self.drones)):
            for j in range(i + 1, len(self.drones)):
                di, dj = self.drones[i], self.drones[j]
                if di.status == "em_voo" and dj.status == "em_voo":
                    if di.calcular_distancia(dj) < 12.0:
                        di.status = "colidiu"
                        dj.status = "colidiu"

    def esta_ativa(self):
        """True enquanto houver drones em voo ou em animação de explosão."""
        return any(d.status in ("em_voo", "colidiu") for d in self.drones)

    def tempo_simulado(self):
        """
        Retorna o tempo de simulação decorrido em segundos,
        excluindo períodos pausados. Funciona durante e após a simulação.
        """
        if self.tempo_inicio is None:
            return 0.0
        pausa_atual = (time() - self._pausa_inicio) if self._pausa_inicio else 0.0
        if self.tempo_fim is not None:
            return self.tempo_fim - self.tempo_inicio - self._pausa_acumulada
        return time() - self.tempo_inicio - self._pausa_acumulada - pausa_atual

    # ------------------------------------------------------------------ #
    # Geração de cenário                                                   #
    # ------------------------------------------------------------------ #

    def gerar_drones_aleatorios(self, quantidade, x_max, y_min, y_max, margem=40):
        """Gera N drones com posições e destinos aleatórios dentro da área dada."""
        for i in range(quantidade):
            x_ini  = random.randint(margem, x_max - margem)
            y_ini  = random.randint(y_min + margem, y_max - margem)
            x_dest = random.randint(margem, x_max - margem)
            y_dest = random.randint(y_min + margem, y_max - margem)
            vel    = random.uniform(1.0, 2.5)
            self.adicionar_drone(
                Drone(i + 1, x_ini, y_ini, x_dest, y_dest, velocidade=vel)
            )

    # ------------------------------------------------------------------ #
    # Métricas                                                             #
    # ------------------------------------------------------------------ #

    def calcular_metricas(self):
        """Retorna um dicionário com todas as métricas da simulação."""
        total = len(self.drones)
        if total == 0:
            return {}

        chegaram  = sum(1 for d in self.drones if d.status == "chegou")
        colidiram = sum(1 for d in self.drones if d.status in ("colidiu", "destruido"))
        nao_conc  = total - chegaram

        t_total = self.tempo_simulado()
        tempos  = [d.tempo_chegada for d in self.drones if d.tempo_chegada is not None]
        t_medio = (sum(tempos) / len(tempos)) if tempos else 0.0

        return {
            "total":               total,
            "chegaram":            chegaram,
            "colidiram":           colidiram,
            "nao_concluiram":      nao_conc,
            "tempo_total":         t_total,
            "tempo_medio_chegada": t_medio,
            "taxa_colisao":        (colidiram / total) * 100,
            "taxa_sucesso":        (chegaram  / total) * 100,
            "distancia_media":     sum(d.distancia_percorrida for d in self.drones) / total,
            "passos":              self.passos,
        }

    def imprimir_metricas(self):
        """Exibe o relatório completo no terminal."""
        m = self.calcular_metricas()
        if not m:
            print("Nenhum drone instanciado.")
            return
        sep = "=" * 52
        print(f"\n{sep}")
        print("   RELATÓRIO FINAL DA SIMULAÇÃO - MÉTRICAS")
        print(sep)
        print(f"  Total de drones no cenário:            {m['total']}")
        print(f"  Drones que chegaram ao destino:        {m['chegaram']}")
        print(f"  Drones que colidiram:                  {m['colidiram']}")
        print(f"  Drones que não concluíram a missão:    {m['nao_concluiram']}")
        print("-" * 52)
        print(f"  Tempo total de simulação:              {m['tempo_total']:.2f}s")
        print(f"  Tempo médio para chegada ao destino:   {m['tempo_medio_chegada']:.2f}s")
        print(f"  Taxa de colisão:                       {m['taxa_colisao']:.1f}%")
        print(f"  Percentual de sucesso das missões:     {m['taxa_sucesso']:.1f}%")
        print(f"  Distância média percorrida:            {m['distancia_media']:.1f}px")
        print(f"  Número de iterações da simulação:      {m['passos']}")
        print(f"{sep}\n")
