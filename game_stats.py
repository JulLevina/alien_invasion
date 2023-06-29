class GameStats():
    """Отслеживание статистики для игры."""

    def __init__(self, ai_game):
        """Инициализирует статистику."""
        self.settings = ai_game.settings
        self.reset_stats()

        # Игра запускается в активном сотсоянии
        self.game_active = True
    
    def reset_stats(self):
        """Инициализирует статистику, изменяющуюся во время игры."""
        self.ships_left = self.settings.ship_limit
