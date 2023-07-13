import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from button import Button
from alien import Alien
from bullet import Bullet
from scoreboard import Scoreboard
from ship import Ship


class AlienInvasion:
    """Класс для управления ресурсами и поведенем игры."""

    def __init__(self):
        """Инициализирует игру и создает игровые ресурсы."""
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        self.clock = pygame.time.Clock()

        pygame.mixer.music.load('sounds/space_music.mp3')
        pygame.mixer.music.play(-1)
        self.bullet_sound = pygame.mixer.Sound('sounds/blast_sound.ogg')

        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Alien Invasion")
        pygame.display.set_icon(pygame.image.load('images/ship.bmp'))
        self.bg_surf = pygame.image.load('images/m_space.jpg').convert()
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        self.ship = Ship(self)
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.aliens = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self._create_fleet()

        # Создание кнопки Play
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Запуск основного цикла игры."""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(self.settings.FPS)

    def _check_events(self):
        """Обрабатывает нажатия клавиш и события мыши."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Запускает новую игру при нажатии кнопки Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Сброс игровой статистики
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Очистка списков пршельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота и размещение корабля в центре
            self._create_fleet()
            self.ship.center_ship()

            # Указатель мыши скрывается
            pygame.mouse.set_visible(False)

            # Сброс игровых настроек
            self.settings.initialize_dynamic_settings()

    def _check_keydown_events(self, event):
        """"Реагирует на нажатие клавиш."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_1:
            pygame.display.iconify()

    def _check_keyup_events(self, event):
        """Реагрует на отпускание клавиш."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_aliens_bottom(self):
        """Проверяет, добрались ли пришельцы до нижнего края экрана."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Происходит то же, что при столкновении с кораблем
                self._ship_hit()
                break

    def _fire_bullet(self):
        """Создание нового снаряда и включение его в группу bullets."""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Изменяет позицию снарядов."""
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Обработка коллизий снарядов с пришельцами."""
        # Проверка попаданий в пришельцев
        # При попадании удалить снаряд и пришельца
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, False, True
        )

        if collisions:
            for aliens in collisions.values():
                self.bullet_sound.play()
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Уничтожение существующих снарядов и создание нового флота
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Увеличение уровня
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Обрабатывает столкновение корабля с пришельцем."""
        if self.stats.ships_left > 0:
            # Уменьшение ship_left и обновление панели счета
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # очистка списков прищельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()

            # создание нового флота и размещение корабля в центре
            self._create_fleet()
            self.ship.center_ship()

            # пауза
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """
        Проверяет, достиг ли флот края экран.
        Обновляет позиции всех пришельцев во флоте.
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Проверка коллизии пришелец-корабль
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # проверить, добрались ли пришельцы до нижнего края экрана
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Создание флота вторжения."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Определяет количество рядов, помещающихся на экране
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (
            3 * alien_height
        ) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Реагирует на достижение пришельцем края экрана."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction()
                break

    def change_fleet_direction(self):
        """Опускает весь флот и меняет напровление флота."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Обновляет изображение на экране и отображает новый экран."""
        self.screen.blit(self.bg_surf, (0, 0))
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # Вывод информации о счете
        self.sb.show_score()

        # Кнопка Play отображается в том случае, если игра неактивна
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == "__main__":
    # Создание экземпляра и запуск игры
    ai = AlienInvasion()
    ai.run_game()
