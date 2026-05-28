"""
visualizacao.py — Interface gráfica do Simulador de Drones.

Estados:
    "config"     → tela de configuração (escolher nº de drones)
    "aguardando" → drones posicionados, aguardando PLAY
    "rodando"    → simulação em andamento
    "pausado"    → simulação pausada
    "concluido"  → simulação encerrada (drones congelados na tela)
"""

import math
import sys
import pygame
from simulacao import SimuladorDrones

# ── Dimensões ─────────────────────────────────────────────────────────
LARGURA       = 960
ALTURA_TOTAL  = 660
ALTURA_TOPO   = 52
ALTURA_BOTOES = 80
ALTURA_SIM    = ALTURA_TOTAL - ALTURA_TOPO - ALTURA_BOTOES   # 528
FPS           = 60

# ── Paleta ────────────────────────────────────────────────────────────
C_FUNDO       = (10,  14,  26)   # fundo config screen
C_BARRA       = (14,  19,  36)   # barras topo / botão
C_BORDA       = (38,  54,  92)
C_SIM_BG      = (255, 255, 255)  # fundo da área de simulação

C_TEXTO       = (210, 228, 255)
C_TEXTO_SEC   = (100, 128, 172)
C_ACENTO      = ( 72, 172, 255)

# Drones (cores visíveis sobre fundo branco)
C_DRONE_VOO    = ( 30, 110, 210)
C_DRONE_CHEGOU = ( 25, 150,  60)
C_DESTINO      = (100, 120, 160)
C_DEST_CHEGOU  = ( 30, 140,  70)
C_EXP_CENTRO   = (255, 200,  40)
C_EXP_BORDA    = (220,  60,  10)
C_ID_TEXTO     = ( 50,  70, 130)  # label ID (fundo branco)

# Ícones dos botões
C_ICON_BASE    = (140, 160, 210)  # cor em repouso
C_ICON_PLAY    = ( 45, 200,  85)  # verde
C_ICON_PAUSE   = (210, 175,  45)  # âmbar
C_ICON_RESTART = ( 80, 145, 255)  # azul
C_ICON_QUIT    = (225,  65,  65)  # vermelho

# Config screen
C_INPUT_BG    = (22,  30,  54)
C_INPUT_BG_AT = (28,  40,  70)
C_INPUT_BD    = (38,  54,  92)
C_INPUT_BD_AT = (72, 150, 248)
C_PLAY        = (38, 188,  82)
C_PLAY_H      = (52, 218,  98)


# ══════════════════════════════════════════════════════════════════════
#  Componente: Botão com fundo (usado somente na config screen)
# ══════════════════════════════════════════════════════════════════════
class Botao:
    def __init__(self, x, y, w, h, texto, cor, cor_hover, rb=10):
        self.rect      = pygame.Rect(x, y, w, h)
        self.texto     = texto
        self.cor       = cor
        self.cor_hover = cor_hover
        self.rb        = rb
        self._hover    = False

    def atualizar(self, pos):
        self._hover = self.rect.collidepoint(pos)

    def desenhar(self, surf, fonte):
        cor = self.cor_hover if self._hover else self.cor
        pygame.draw.rect(surf, (4, 6, 14), self.rect.move(0, 3), border_radius=self.rb)
        pygame.draw.rect(surf, cor, self.rect, border_radius=self.rb)
        hl = pygame.Surface((self.rect.w - 6, 2), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 45))
        surf.blit(hl, (self.rect.x + 3, self.rect.y + 3))
        txt = fonte.render(self.texto, True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def clicado(self, pos):
        return self.rect.collidepoint(pos)


# ══════════════════════════════════════════════════════════════════════
#  App
# ══════════════════════════════════════════════════════════════════════
class App:

    # ── Inicialização ─────────────────────────────────────────────────
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simulador de Drones")
        self.tela    = pygame.display.set_mode((LARGURA, ALTURA_TOTAL))
        self.relogio = pygame.time.Clock()

        self._init_fontes()

        self.sim          = SimuladorDrones()
        self.estado       = "config"
        self.qtd          = 10
        self._input       = "10"
        self._input_at    = False
        self._erro        = ""
        self._barra_btns  = {}   # posições {nome: (cx, cy)} dos ícones da barra

        self._criar_botoes()

    def _init_fontes(self):
        f = "Segoe UI"
        self.f_titulo  = pygame.font.SysFont(f, 40, bold=True)
        self.f_grande  = pygame.font.SysFont(f, 30, bold=True)
        self.f_media   = pygame.font.SysFont(f, 20)
        self.f_pequena = pygame.font.SysFont(f, 15)
        self.f_btn     = pygame.font.SysFont(f, 17, bold=True)

    def _criar_botoes(self):
        cx = LARGURA // 2
        self.btn_start_cfg = Botao(cx - 130, 0, 260, 52, "INICIAR SIMULAÇÃO", C_PLAY, C_PLAY_H)
        self.rect_input    = pygame.Rect(cx - 110, 0, 220, 50)

    # ── Loop principal ────────────────────────────────────────────────
    def run(self):
        while True:
            eventos = pygame.event.get()
            for ev in eventos:
                if ev.type == pygame.QUIT:
                    self._sair()
            if self.estado == "config":
                self._draw_config(eventos)
            else:
                self._draw_sim(eventos)
            pygame.display.flip()
            self.relogio.tick(FPS)

    # ══ Tela de Configuração ══════════════════════════════════════════
    def _draw_config(self, eventos):
        self.tela.fill(C_FUNDO)
        cx, cy = LARGURA // 2, ALTURA_TOTAL // 2

        # Título
        titulo = self.f_titulo.render("Simulador de Drones", True, C_ACENTO)
        self.tela.blit(titulo, titulo.get_rect(centerx=cx, top=cy - 210))

        # Campo de entrada
        lbl = self.f_media.render("Número de drones:", True, C_TEXTO)
        self.tela.blit(lbl, lbl.get_rect(centerx=cx, top=cy - 140))

        self.rect_input.center = (cx, cy - 82)
        cor_bd = C_INPUT_BD_AT if self._input_at else C_INPUT_BD
        cor_bg = C_INPUT_BG_AT if self._input_at else C_INPUT_BG
        pygame.draw.rect(self.tela, cor_bg, self.rect_input, border_radius=10)
        pygame.draw.rect(self.tela, cor_bd, self.rect_input, 2, border_radius=10)

        txt_inp = self.f_grande.render(self._input or " ", True, C_TEXTO)
        self.tela.blit(txt_inp, txt_inp.get_rect(center=self.rect_input.center))

        # Cursor piscante
        if self._input_at and pygame.time.get_ticks() % 1000 < 520:
            cur_x = self.rect_input.centerx + txt_inp.get_width() // 2 + 4
            pygame.draw.line(self.tela, C_TEXTO,
                             (cur_x, self.rect_input.top + 10),
                             (cur_x, self.rect_input.bottom - 10), 2)

        hint = self.f_pequena.render("Clique no campo e digite (1 – 50)", True, C_TEXTO_SEC)
        self.tela.blit(hint, hint.get_rect(centerx=cx, top=self.rect_input.bottom + 8))

        if self._erro:
            err_s = self.f_pequena.render(self._erro, True, C_EXP_BORDA)
            self.tela.blit(err_s, err_s.get_rect(centerx=cx, top=self.rect_input.bottom + 28))

        # Botão iniciar
        pos_m = pygame.mouse.get_pos()
        self.btn_start_cfg.rect.center = (cx, cy + 10)
        self.btn_start_cfg.atualizar(pos_m)
        self.btn_start_cfg.desenhar(self.tela, self.f_btn)

        # Eventos
        for ev in eventos:
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self._input_at = self.rect_input.collidepoint(ev.pos)
                if self.btn_start_cfg.clicado(ev.pos):
                    self._tentar_iniciar()
            elif ev.type == pygame.KEYDOWN and self._input_at:
                if ev.key == pygame.K_BACKSPACE:
                    self._input = self._input[:-1]; self._erro = ""
                elif ev.key == pygame.K_RETURN:
                    self._tentar_iniciar()
                elif ev.unicode.isdigit() and len(self._input) < 2:
                    self._input += ev.unicode; self._erro = ""

    def _tentar_iniciar(self):
        try:
            qtd = int(self._input)
            if 1 <= qtd <= 50:
                self.qtd = qtd; self._erro = ""
                self._preparar_simulacao()
            else:
                self._erro = "Digite um valor entre 1 e 50."
        except ValueError:
            self._erro = "Valor inválido. Digite apenas números."

    def _preparar_simulacao(self):
        """Reseta e gera drones — mantém self.qtd atual."""
        self.sim.resetar()
        self.sim.gerar_drones_aleatorios(
            self.qtd,
            x_max=LARGURA,
            y_min=ALTURA_TOPO,
            y_max=ALTURA_TOPO + ALTURA_SIM,
            margem=40,
        )
        self.estado = "aguardando"

    # ══ Tela de Simulação ═════════════════════════════════════════════
    def _draw_sim(self, eventos):
        # Barras escuras (preenchimento base) + área de simulação branca
        self.tela.fill(C_BARRA)
        area = pygame.Rect(0, ALTURA_TOPO, LARGURA, ALTURA_SIM)
        pygame.draw.rect(self.tela, C_SIM_BG, area)

        # Atualiza lógica (somente quando rodando)
        if self.estado == "rodando":
            if not self.sim.atualizar():
                self.estado = "concluido"
                self.sim.imprimir_metricas()

        # Desenha drones
        for drone in self.sim.drones:
            self._desenhar_drone(drone)

        # Mensagem de status sobre a área de simulação
        msgs = {
            "aguardando": ("Clique em INICIAR para começar a simulação", (80, 100, 160)),
            "pausado":    ("— SIMULAÇÃO PAUSADA —",                       (180, 148, 35)),
            "concluido":  ("Simulação concluída!",                         (25, 140, 65)),
        }
        if self.estado in msgs:
            txt, cor = msgs[self.estado]
            s = self.f_media.render(txt, True, cor)
            self.tela.blit(s, s.get_rect(centerx=LARGURA // 2, top=ALTURA_TOPO + 12))

        # Barras superior e inferior
        self._draw_barra_topo()
        self._draw_barra_botoes()

        # Eventos
        self._handle_sim_eventos(eventos)

    def _handle_sim_eventos(self, eventos):
        r_hit = 26
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                self._handle_key(ev); continue
            if ev.type != pygame.MOUSEBUTTONDOWN or ev.button != 1:
                continue

            def hit(nome):
                if nome not in self._barra_btns:
                    return False
                bx, by = self._barra_btns[nome]
                return (ev.pos[0] - bx) ** 2 + (ev.pos[1] - by) ** 2 <= r_hit ** 2

            if hit("quit"):
                self._sair()
            elif hit("restart"):
                self._preparar_simulacao()          # mesmo qtd, novos drones
            elif hit("play"):
                if self.estado == "aguardando":
                    self.sim.iniciar()
                else:
                    self.sim.retomar()
                self.estado = "rodando"
            elif hit("pause"):
                self.sim.pausar(); self.estado = "pausado"

    def _handle_key(self, ev):
        if ev.key == pygame.K_SPACE:
            if self.estado == "rodando":
                self.sim.pausar(); self.estado = "pausado"
            elif self.estado == "pausado":
                self.sim.retomar(); self.estado = "rodando"
            elif self.estado == "aguardando":
                self.sim.iniciar(); self.estado = "rodando"
        elif ev.key == pygame.K_r:
            self._preparar_simulacao()
        elif ev.key == pygame.K_ESCAPE:
            self.sim.finalizar()
            self._input = str(self.qtd); self._erro = ""
            self.estado = "config"

    def _sair(self):
        self.sim.finalizar()
        pygame.quit(); sys.exit()

    # ── Barra superior ────────────────────────────────────────────────
    def _draw_barra_topo(self):
        pygame.draw.rect(self.tela, C_BARRA, (0, 0, LARGURA, ALTURA_TOPO))
        pygame.draw.line(self.tela, C_BORDA,
                         (0, ALTURA_TOPO - 1), (LARGURA, ALTURA_TOPO - 1))

        titulo = self.f_media.render("SIMULADOR DE DRONES", True, C_ACENTO)
        self.tela.blit(titulo, (20, (ALTURA_TOPO - titulo.get_height()) // 2))

        # Timer (sem ícone Unicode)
        t = self.sim.tempo_simulado()
        timer_s = self.f_media.render(f"Tempo: {t:.1f}s", True, C_TEXTO_SEC)
        self.tela.blit(timer_s, (LARGURA - timer_s.get_width() - 20,
                                  (ALTURA_TOPO - timer_s.get_height()) // 2))

        # Mini contadores centrais (sem ícones Unicode)
        if self.sim.drones:
            em_voo   = sum(1 for d in self.sim.drones if d.status == "em_voo")
            chegaram = sum(1 for d in self.sim.drones if d.status == "chegou")
            colisoes = sum(1 for d in self.sim.drones
                           if d.status in ("colidiu", "destruido"))
            info = f"Voo: {em_voo}   OK: {chegaram}   Col: {colisoes}"
            inf_s = self.f_pequena.render(info, True, C_TEXTO_SEC)
            self.tela.blit(inf_s, inf_s.get_rect(
                centerx=LARGURA // 2, centery=ALTURA_TOPO // 2))

    # ── Barra inferior com botões ícone ───────────────────────────────
    def _draw_barra_botoes(self):
        y0 = ALTURA_TOTAL - ALTURA_BOTOES
        pygame.draw.rect(self.tela, C_BARRA, (0, y0, LARGURA, ALTURA_BOTOES))
        pygame.draw.line(self.tela, C_BORDA, (0, y0), (LARGURA, y0))

        pos      = pygame.mouse.get_pos()
        cy       = y0 + ALTURA_BOTOES // 2
        cx       = LARGURA // 2
        r_hit    = 26
        icon_sz  = 16

        # Layout de ícones por estado
        if self.estado == "rodando":
            layout = [("pause",   cx - 80), ("restart", cx), ("quit", cx + 80)]
        elif self.estado in ("aguardando", "pausado"):
            layout = [("play",    cx - 80), ("restart", cx), ("quit", cx + 80)]
        else:  # concluido — sem play/pause
            layout = [("restart", cx - 40), ("quit",    cx + 40)]

        # Salva posições para detecção de clique
        self._barra_btns = {nome: (bx, cy) for nome, bx in layout}

        hover_colors = {
            "play":    C_ICON_PLAY,
            "pause":   C_ICON_PAUSE,
            "restart": C_ICON_RESTART,
            "quit":    C_ICON_QUIT,
        }

        for nome, bx in layout:
            hovering = (pos[0] - bx) ** 2 + (pos[1] - cy) ** 2 <= r_hit ** 2
            color    = hover_colors[nome] if hovering else C_ICON_BASE

            # Círculo de hover
            if hovering:
                pygame.draw.circle(self.tela, (28, 36, 62), (bx, cy), r_hit)

            # Desenha o ícone
            if   nome == "play":    self._icon_play(bx, cy, icon_sz, color)
            elif nome == "pause":   self._icon_pause(bx, cy, icon_sz, color)
            elif nome == "restart": self._icon_restart(bx, cy, icon_sz, color)
            elif nome == "quit":    self._icon_quit(bx, cy, icon_sz, color)

    # ── Ícones desenhados com pygame.draw ─────────────────────────────
    def _icon_play(self, cx, cy, size, color):
        """Triângulo apontando para a direita."""
        pts = [(cx - size // 2, cy - size),
               (cx - size // 2, cy + size),
               (cx + size,      cy)]
        pygame.draw.polygon(self.tela, color, pts)

    def _icon_pause(self, cx, cy, size, color):
        """Duas barras verticais."""
        w   = max(2, size // 3)
        h   = size + 6
        gap = max(2, size // 3)
        pygame.draw.rect(self.tela, color, (cx - gap - w, cy - h // 2, w, h))
        pygame.draw.rect(self.tela, color, (cx + gap,     cy - h // 2, w, h))

    def _icon_restart(self, cx, cy, size, color):
        """Arco circular com seta na ponta."""
        r    = size
        rect = pygame.Rect(cx - r, cy - r, 2 * r, 2 * r)
        pygame.draw.arc(self.tela, color, rect,
                        math.radians(30), math.radians(340), 3)
        # Seta no início do arco (~30°)
        a  = math.radians(30)
        tx = cx + r * math.cos(a)
        ty = cy - r * math.sin(a)
        ta = a - math.pi / 2
        s  = 7
        p1 = (tx, ty)
        p2 = (tx + s * math.cos(ta + math.radians(145)),
               ty - s * math.sin(ta + math.radians(145)))
        p3 = (tx + s * math.cos(ta - math.radians(145)),
               ty - s * math.sin(ta - math.radians(145)))
        pygame.draw.polygon(self.tela, color, [p1, p2, p3])

    def _icon_quit(self, cx, cy, size, color):
        """X cruzado."""
        th = max(2, size // 4)
        pygame.draw.line(self.tela, color,
                         (cx - size, cy - size), (cx + size, cy + size), th)
        pygame.draw.line(self.tela, color,
                         (cx + size, cy - size), (cx - size, cy + size), th)

    # ── Desenho de drone ──────────────────────────────────────────────
    def _desenhar_drone(self, drone):
        # Destino
        if drone.status != "destruido":
            cor_d = C_DEST_CHEGOU if drone.status == "chegou" else C_DESTINO
            pygame.draw.rect(self.tela, cor_d,
                             (drone.dest_x - 5, drone.dest_y - 5, 10, 10))
            pygame.draw.rect(self.tela, (80, 100, 140),
                             (drone.dest_x - 5, drone.dest_y - 5, 10, 10), 1)

        if drone.status == "destruido":
            return

        # Explosão
        if drone.status == "colidiu":
            if drone.raio_explosao < drone.max_raio_explosao:
                drone.raio_explosao += 2.0
                pygame.draw.circle(self.tela, C_EXP_BORDA,
                                   (int(drone.x), int(drone.y)),
                                   int(drone.raio_explosao))
                pygame.draw.circle(self.tela, C_EXP_CENTRO,
                                   (int(drone.x), int(drone.y)),
                                   max(2, int(drone.raio_explosao * 0.5)))
            else:
                drone.status = "destruido"
            return

        # Drone normal
        cor = C_DRONE_VOO if drone.status == "em_voo" else C_DRONE_CHEGOU
        pygame.draw.circle(self.tela, cor,
                           (int(drone.x), int(drone.y)), drone.raio)
        # Contorno branco para destacar no fundo claro
        pygame.draw.circle(self.tela, (255, 255, 255),
                           (int(drone.x), int(drone.y)), drone.raio, 1)

        # ID do drone
        label = self.f_pequena.render(str(drone.id), True, C_ID_TEXTO)
        self.tela.blit(label, (int(drone.x) + drone.raio + 3,
                                int(drone.y) - label.get_height() // 2))
