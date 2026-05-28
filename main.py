"""
main.py — Ponto de entrada do Simulador de Drones.

Execute este arquivo para iniciar a aplicação:
    python main.py

Estrutura do projeto:
    main.py         → ponto de entrada
    drone.py        → classe Drone (lógica individual)
    simulacao.py    → classe SimuladorDrones (lógica e métricas)
    visualizacao.py → interface gráfica pygame (telas, botões, renderização)
"""

from visualizacao import App

if __name__ == "__main__":
    App().run()