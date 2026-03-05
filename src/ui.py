import pygame
import os
import chess
import settings

# Constante layout panou stâng
_HEADER_Y    = 20
_START_Y     = 50
_LINE_HEIGHT = 25
_SB_W        = 12
_SB_PAD      = 6

# Text About — modifică după dorință
ABOUT_TEXT = [
    "Chess vs Stockfish ELO 1400",
    "",
    "Un joc de sah dezvoltat în Python",
    "cu pygame si motorul Stockfish.",
    "",
    "Controale:",
    "  • Click pe piesa -> selectare",
    "  • Click pe destinatie -> mutare",
    "  • Scroll -> istoric mutari",
    "",
    "Butoane dreapta:",
    "  • Restart         — joc nou",
    "  • Restart+Colors  — schimbă culoarea",
    "  • About           — aceasta fereastra",
    "  • Exit            — ieșire din program",
    "",
    "Succes la joc!",
]


class ChessUI:
    def __init__(self, screen):
        self.screen        = screen
        self.pieces_images = {}
        self.load_images()
        self.font       = pygame.font.SysFont("Arial", 24, bold=True)
        self.move_font  = pygame.font.SysFont("Courier", 18)
        self.btn_font   = pygame.font.SysFont("Arial", 20, bold=True)
        self.about_font = pygame.font.SysFont("Arial", 18)

        self.scroll_y        = 0
        self.promotion_rects = []

        # Scrollbar drag state
        self._sb_dragging      = False
        self._sb_drag_start_y  = 0
        self._sb_drag_start_sc = 0
        self._sb_track_rect    = pygame.Rect(0, 0, 0, 0)
        self._sb_thumb_rect    = pygame.Rect(0, 0, 0, 0)
        self._sb_max_scroll    = 0
        self._sb_visible       = False

        # Butoane panou dreapta — rect-urile sunt recalculate la fiecare draw
        self.btn_rects = {}   # { 'restart': Rect, 'restart_colors': Rect,
                              #   'about': Rect, 'exit': Rect }

    # ------------------------------------------------------------------ #
    # HELPER SCROLLBAR                                                    #
    # ------------------------------------------------------------------ #
    def _calc_scroll_metrics(self, move_stack):
        panel_width     = settings.OFFSET_X - 10
        visible_h       = settings.HEIGHT - _START_Y - 10
        total_pairs     = (len(move_stack) + 1) // 2
        total_content_h = total_pairs * _LINE_HEIGHT
        max_scroll      = max(0, total_content_h - visible_h)

        sb_x       = panel_width - _SB_W - _SB_PAD
        track_rect = pygame.Rect(sb_x, _START_Y, _SB_W, visible_h)

        thumb_ratio  = (visible_h / total_content_h) if total_content_h > 0 else 1.0
        thumb_h      = max(20, int(visible_h * thumb_ratio))
        scroll_ratio = self.scroll_y / max_scroll if max_scroll > 0 else 0
        thumb_y      = _START_Y + int((visible_h - thumb_h) * scroll_ratio)
        thumb_rect   = pygame.Rect(sb_x, thumb_y, _SB_W, thumb_h)

        return visible_h, total_content_h, max_scroll, track_rect, thumb_rect

    # ------------------------------------------------------------------ #
    # PANOURI LATERALE                                                    #
    # ------------------------------------------------------------------ #
    def draw_panels(self):
        panel_color = (40, 40, 40)
        line_color  = (100, 100, 100)

        # Stânga
        pygame.draw.rect(self.screen, panel_color,
                         pygame.Rect(0, 0, settings.OFFSET_X - 10, settings.HEIGHT))
        pygame.draw.line(self.screen, line_color,
                         (settings.OFFSET_X - 10, 0),
                         (settings.OFFSET_X - 10, settings.HEIGHT), 2)

        # Dreapta
        right_start_x = settings.OFFSET_X + settings.BOARD_SIZE + 10
        pygame.draw.rect(self.screen, panel_color,
                         pygame.Rect(right_start_x, 0,
                                     settings.WIDTH - right_start_x, settings.HEIGHT))
        pygame.draw.line(self.screen, line_color,
                         (right_start_x, 0),
                         (right_start_x, settings.HEIGHT), 2)

    # ------------------------------------------------------------------ #
    # BUTOANE PANOU DREAPTA                                               #
    # ------------------------------------------------------------------ #
    def draw_right_panel_buttons(self, player_color=chess.WHITE):
        """Desenează cele 4 butoane centrate în panoul drept."""
        right_start_x = settings.OFFSET_X + settings.BOARD_SIZE + 10
        panel_w       = settings.WIDTH - right_start_x
        panel_cx      = right_start_x + panel_w // 2   # centrul orizontal

        btn_w   = max(160, panel_w - 40)
        btn_h   = 55
        gap     = 20
        labels  = [
            ('restart',        'Restart'),
            ('restart_colors', 'Restart +\nChange Colors'),
            ('about',          'About'),
            ('exit',           'Exit'),
        ]

        # Grupul de butoane centrat vertical
        total_h     = len(labels) * btn_h + (len(labels) - 1) * gap
        group_top_y = (settings.HEIGHT - total_h) // 2

        self.btn_rects = {}
        mouse_pos = pygame.mouse.get_pos()

        for idx, (key, label) in enumerate(labels):
            bx   = panel_cx - btn_w // 2
            by   = group_top_y + idx * (btn_h + gap)
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            self.btn_rects[key] = rect

            hover  = rect.collidepoint(mouse_pos)
            # Culori butoane
            if key == 'exit':
                base_color  = (160, 40, 40)
                hover_color = (200, 60, 60)
                text_color  = (255, 255, 255)
            elif key == 'restart_colors':
                base_color  = (50, 100, 160)
                hover_color = (70, 130, 200)
                text_color  = (255, 255, 255)
            else:
                base_color  = (70, 70, 70)
                hover_color = (100, 100, 100)
                text_color  = (230, 230, 230)

            color = hover_color if hover else base_color
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 150, 150), rect, 2, border_radius=8)

            # Text (suportă \n pentru două rânduri)
            lines = label.split('\n')
            line_h = self.btn_font.get_height()
            total_text_h = len(lines) * line_h + (len(lines) - 1) * 4
            text_start_y = by + (btn_h - total_text_h) // 2

            for li, line in enumerate(lines):
                surf = self.btn_font.render(line, True, text_color)
                tx   = bx + (btn_w - surf.get_width()) // 2
                ty   = text_start_y + li * (line_h + 4)
                self.screen.blit(surf, (tx, ty))

        # Indicator culoare curentă sub butoane
        color_label = "You play as: " + ("WHITE ♙" if player_color == chess.WHITE else "BLACK ♟")
        color_surf  = self.about_font.render(color_label, True, (180, 180, 180))
        cx          = panel_cx - color_surf.get_width() // 2
        cy          = group_top_y + total_h + 20
        if cy < settings.HEIGHT - 20:
            self.screen.blit(color_surf, (cx, cy))

    # ------------------------------------------------------------------ #
    # HISTORIC MUTĂRI CU SCROLLBAR                                        #
    # ------------------------------------------------------------------ #
    def draw_move_history(self, move_stack):
        text_color  = (200, 200, 200)
        panel_width = settings.OFFSET_X - 10

        header = self.move_font.render("#    White      Black", True, (255, 215, 0))
        self.screen.blit(header, (20, _HEADER_Y))

        visible_h, total_content_h, max_scroll, track_rect, thumb_rect = \
            self._calc_scroll_metrics(move_stack)

        self.scroll_y       = max(0, min(self.scroll_y, max_scroll))
        self._sb_max_scroll = max_scroll
        self._sb_track_rect = track_rect
        self._sb_thumb_rect = thumb_rect
        self._sb_visible    = total_content_h > visible_h

        clip_rect = pygame.Rect(0, _START_Y,
                                panel_width - _SB_W - _SB_PAD * 2, visible_h)
        self.screen.set_clip(clip_rect)

        for i in range(0, len(move_stack), 2):
            move_num = (i // 2) + 1
            y_pos    = _START_Y + (i // 2) * _LINE_HEIGHT - int(self.scroll_y)

            if y_pos + _LINE_HEIGHT < _START_Y or y_pos > settings.HEIGHT:
                continue

            self.screen.blit(
                self.move_font.render(f"{move_num}.", True, (150, 150, 150)),
                (20, y_pos))
            self.screen.blit(
                self.move_font.render(move_stack[i], True, text_color),
                (70, y_pos))
            if i + 1 < len(move_stack):
                self.screen.blit(
                    self.move_font.render(move_stack[i + 1], True, text_color),
                    (170, y_pos))

        self.screen.set_clip(None)

        if self._sb_visible:
            pygame.draw.rect(self.screen, (60, 60, 60), track_rect, border_radius=6)
            mx, my = pygame.mouse.get_pos()
            hover  = thumb_rect.collidepoint(mx, my)
            color  = (230, 230, 230) if (self._sb_dragging or hover) else (160, 160, 160)
            pygame.draw.rect(self.screen, color, thumb_rect, border_radius=6)

    # ------------------------------------------------------------------ #
    # POPUP ABOUT                                                         #
    # ------------------------------------------------------------------ #
    def draw_about_popup(self):
        """Fereastră modală cu informații despre proiect."""
        # Fundal semi-transparent
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        line_h   = self.about_font.get_height() + 6
        padding  = 30
        popup_w  = min(500, settings.WIDTH - 100)
        popup_h  = len(ABOUT_TEXT) * line_h + padding * 2 + 50  # +50 pentru titlu
        popup_x  = (settings.WIDTH  - popup_w) // 2
        popup_y  = (settings.HEIGHT - popup_h) // 2

        popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
        pygame.draw.rect(self.screen, (30, 30, 30), popup_rect, border_radius=12)
        pygame.draw.rect(self.screen, (200, 200, 200), popup_rect, 2, border_radius=12)

        # Titlu
        title_surf = self.font.render("About", True, (255, 215, 0))
        self.screen.blit(title_surf,
                         (popup_x + (popup_w - title_surf.get_width()) // 2,
                          popup_y + 15))

        # Linii de text
        for idx, line in enumerate(ABOUT_TEXT):
            color = (255, 255, 255) if line and not line.startswith(" ") else (200, 200, 200)
            surf  = self.about_font.render(line, True, color)
            self.screen.blit(surf, (popup_x + padding,
                                    popup_y + 50 + idx * line_h))

        # Buton Close
        close_w, close_h = 120, 36
        close_rect = pygame.Rect(
            popup_x + (popup_w - close_w) // 2,
            popup_y + popup_h - close_h - 15,
            close_w, close_h)
        mx, my     = pygame.mouse.get_pos()
        close_col  = (180, 50, 50) if close_rect.collidepoint(mx, my) else (130, 40, 40)
        pygame.draw.rect(self.screen, close_col, close_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), close_rect, 1, border_radius=8)
        close_surf = self.btn_font.render("Close", True, (255, 255, 255))
        self.screen.blit(close_surf,
                         (close_rect.x + (close_w - close_surf.get_width()) // 2,
                          close_rect.y + (close_h - close_surf.get_height()) // 2))
        return close_rect   # îl returnăm ca main.py să detecteze click-ul

    # ------------------------------------------------------------------ #
    # SCROLL API                                                          #
    # ------------------------------------------------------------------ #
    def handle_scroll(self, delta):
        self.scroll_y += delta * _LINE_HEIGHT
        self.scroll_y  = max(0, self.scroll_y)

    def scroll_to_bottom(self, move_stack):
        visible_h       = settings.HEIGHT - _START_Y - 10
        total_pairs     = (len(move_stack) + 1) // 2
        total_content_h = total_pairs * _LINE_HEIGHT
        self.scroll_y   = max(0, total_content_h - visible_h)

    # ------------------------------------------------------------------ #
    # MOUSE EVENTS SCROLLBAR                                              #
    # ------------------------------------------------------------------ #
    def on_mouse_down(self, pos):
        if not self._sb_visible:
            return False
        mx, my = pos
        if self._sb_thumb_rect.collidepoint(mx, my):
            self._sb_dragging      = True
            self._sb_drag_start_y  = my
            self._sb_drag_start_sc = self.scroll_y
            return True
        if self._sb_track_rect.collidepoint(mx, my):
            track_h    = self._sb_track_rect.height
            thumb_h    = self._sb_thumb_rect.height
            move_range = max(1, track_h - thumb_h)
            ratio      = (my - self._sb_track_rect.y - thumb_h / 2) / move_range
            self.scroll_y = max(0, min(ratio * self._sb_max_scroll, self._sb_max_scroll))
            return True
        return False

    def on_mouse_up(self):
        self._sb_dragging = False

    def on_mouse_motion(self, pos):
        if not self._sb_dragging:
            return
        _, my      = pos
        delta_y    = my - self._sb_drag_start_y
        track_h    = self._sb_track_rect.height
        thumb_h    = self._sb_thumb_rect.height
        move_range = max(1, track_h - thumb_h)
        self.scroll_y = self._sb_drag_start_sc + delta_y * (self._sb_max_scroll / move_range)
        self.scroll_y = max(0, min(self.scroll_y, self._sb_max_scroll))

    # ------------------------------------------------------------------ #
    # IMAGINI PIESE                                                       #
    # ------------------------------------------------------------------ #
    def load_images(self):
        pieces = [
            'white_pawn', 'white_knight', 'white_bishop',
            'white_rook', 'white_queen', 'white_king',
            'black_pawn', 'black_knight', 'black_bishop',
            'black_rook', 'black_queen', 'black_king'
        ]
        for p in pieces:
            path = os.path.join(settings.PIECES_PATH, f"{p}")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.pieces_images[p] = pygame.transform.smoothscale(
                    img, (settings.SQ_SIZE, settings.SQ_SIZE))
            else:
                print(f"EROARE: Nu gasesc piesa la: {path}")

    # ------------------------------------------------------------------ #
    # TABLĂ ȘI PIESE                                                      #
    # ------------------------------------------------------------------ #
    def draw_board(self, highlight_squares=[]):
        for r in range(settings.ROWS):
            for c in range(settings.COLS):
                square_index = chess.square(c, 7 - r)
                rect = (c * settings.SQ_SIZE + settings.OFFSET_X,
                        r * settings.SQ_SIZE + settings.OFFSET_Y,
                        settings.SQ_SIZE, settings.SQ_SIZE)
                if square_index in highlight_squares:
                    color = (247, 247, 105) if (r + c) % 2 == 0 else (187, 203, 43)
                else:
                    color = settings.LIGHT_SQUARE if (r + c) % 2 == 0 else settings.DARK_SQUARE
                pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self, board):
        for i in range(64):
            piece = board.piece_at(i)
            if piece:
                row = 7 - (i // 8)
                col = i % 8
                pos = (col * settings.SQ_SIZE + settings.OFFSET_X,
                       row * settings.SQ_SIZE + settings.OFFSET_Y)
                color_prefix   = "white" if piece.color == chess.WHITE else "black"
                piece_type_map = {1: 'pawn', 2: 'knight', 3: 'bishop',
                                  4: 'rook',  5: 'queen',  6: 'king'}
                image_name     = f"{color_prefix}_{piece_type_map[piece.piece_type]}"
                self.screen.blit(self.pieces_images[image_name], pos)

    # ------------------------------------------------------------------ #
    # SUGESTII MUTĂRI                                                     #
    # ------------------------------------------------------------------ #
    def draw_suggestions(self, board, selected_square):
        if selected_square is None:
            return
        overlay = pygame.Surface((settings.SQ_SIZE, settings.SQ_SIZE), pygame.SRCALPHA)
        for move in board.legal_moves:
            if move.from_square != selected_square:
                continue
            row    = 7 - (move.to_square // 8)
            col    = move.to_square % 8
            center = (settings.SQ_SIZE // 2, settings.SQ_SIZE // 2)
            overlay.fill((0, 0, 0, 0))
            if board.piece_at(move.to_square):
                pygame.draw.circle(overlay, (80, 80, 80, 160), center,
                                   settings.SQ_SIZE // 2, 6)
            else:
                pygame.draw.circle(overlay, (80, 80, 80, 160), center, 15)
            self.screen.blit(overlay, (col * settings.SQ_SIZE + settings.OFFSET_X,
                                       row * settings.SQ_SIZE + settings.OFFSET_Y))

    # ------------------------------------------------------------------ #
    # MENIU PROMOVARE                                                     #
    # ------------------------------------------------------------------ #
    def draw_promotion_menu(self, color):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        menu_rect = pygame.Rect(settings.WIDTH // 4, settings.HEIGHT // 3,
                                settings.WIDTH // 2, settings.HEIGHT // 4)
        pygame.draw.rect(self.screen, (255, 255, 255), menu_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), menu_rect, 2)

        prefix  = "white" if color == chess.WHITE else "black"
        options = ['queen', 'rook', 'bishop', 'knight']
        self.promotion_rects = []

        for i, opt in enumerate(options):
            x = (menu_rect.x + i * (menu_rect.width // 4)
                 + (menu_rect.width // 8) - (settings.SQ_SIZE // 2))
            y = menu_rect.y + (menu_rect.height // 2) - (settings.SQ_SIZE // 2)
            rect = pygame.Rect(x, y, settings.SQ_SIZE, settings.SQ_SIZE)
            self.screen.blit(self.pieces_images[f"{prefix}_{opt}"], rect)
            self.promotion_rects.append((rect, opt))

    # ------------------------------------------------------------------ #
    # NUME JUCĂTORI                                                       #
    # ------------------------------------------------------------------ #
    def draw_player_names(self, player_color=chess.WHITE):
        text_color = (255, 255, 255)

        # Sus = Stockfish (joacă cu culoarea opusă jucătorului)
        ai_color_str = "BLACK" if player_color == chess.WHITE else "WHITE"
        ai_text  = self.font.render(f"Stockfish ELO: 1400 ({ai_color_str})", True, text_color)
        ai_rect  = ai_text.get_rect(
            center=(settings.WIDTH // 2, settings.OFFSET_Y - 25))
        self.screen.blit(ai_text, ai_rect)

        # Jos = Jucătorul
        player_color_str = "WHITE" if player_color == chess.WHITE else "BLACK"
        user_text = self.font.render(f"You ({player_color_str})", True, text_color)
        user_rect = user_text.get_rect(
            center=(settings.WIDTH // 2,
                    settings.OFFSET_Y + settings.BOARD_SIZE + 25))
        self.screen.blit(user_text, user_rect)