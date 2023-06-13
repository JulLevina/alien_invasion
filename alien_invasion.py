import sys

import pygame

from settings import Settings
from ship import Ship


class AlienInvasion:
    """Класс для управления ресурсам и поведенем игры."""

    def __init__(self):
        """Инициализирует игру и создает игровые ресурсы."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        self.ship = Ship(self)
    
    def run_game(self):
        """Запуск основного цикла игры."""
        while True:
            self._check_events()
            self.ship.update()
            # При каждом проходе цикла перерисовывать экран
            self._update_screen()
            
    
    def _check_events(self):
            """Обрабатывает нажатия клавиш и события мыши."""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """"Реагирует на нажатие клавиш."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
    
    def _check_keyup_events(self, event):
        """Реагрует на отпускание клавиш."""
        if event.key == pygame.K_RIGHT:
            # переместить корабль вправо
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
    
    def _update_screen(self):
        """Обновляет изображение на экране и отображает новый экран."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        pygame.display.flip()

if __name__ == "__main__":
    # Создание экземпляра и запуск игры
    ai = AlienInvasion()
    ai.run_game()