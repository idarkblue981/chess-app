import pygame
import chess
import sys
import os
import settings
from engine import ChessEngine
from ui import ChessUI
from ai import ChessAI


def make_new_game(ai_instance, elo=1400):
    """Creează un engine nou și resetează AI-ul."""
    engine = ChessEngine()
    # Refolosim instanța AI existentă (nu o repornim)
    return engine


def main():
    # 1. Inițializare
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    pygame.display.set_caption("Chess vs Stockfish")

    actual_w, actual_h = screen.get_size()
    settings.update_offsets(actual_w, actual_h)

    # 2. Sunet
    move_sound_path = os.path.join(
        settings.BASE_DIR, "assets", "sound_effects", "piece_move_sound")
    try:
        move_sound = pygame.mixer.Sound(move_sound_path)
    except Exception as e:
        print(f"Atenție: Nu am putut încărca sunetul: {e}")
        move_sound = None

    # 3. Componente
    clock        = pygame.time.Clock()
    engine       = ChessEngine()
    ui           = ChessUI(screen)
    ai           = ChessAI(elo=1400)

    # Culoarea jucătorului uman (chess.WHITE sau chess.BLACK)
    player_color = chess.WHITE

    last_move             = None
    waiting_for_promotion = False
    promotion_data        = None
    show_about            = False
    about_close_rect      = None   # rect-ul butonului Close din popup About

    print("Jocul a pornit!")
    print("Butoane dreapta: Restart | Restart+Colors | About | Exit")

    # Dacă jucătorul e negru, AI-ul face prima mutare
    def maybe_ai_first():
        nonlocal last_move
        if player_color == chess.BLACK and not engine.board.is_game_over():
            last_move = process_ai_move(engine, ai, move_sound) or last_move
            if last_move:
                ui.scroll_to_bottom(engine.move_history_san)

    # 4. Bucla principală
    running = True
    while running:
        for event in pygame.event.get():

            # ── Ieșire fereastră ──────────────────────────────────────
            if event.type == pygame.QUIT:
                running = False

            # ── Scroll rotița ─────────────────────────────────────────
            elif event.type == pygame.MOUSEWHEEL:
                mx, _ = pygame.mouse.get_pos()
                if mx < settings.OFFSET_X - 10:
                    ui.handle_scroll(-event.y)

            # ── Taste săgeți / Home / End ─────────────────────────────
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and show_about:
                    show_about = False
                elif event.key == pygame.K_UP:
                    ui.handle_scroll(-3)
                elif event.key == pygame.K_DOWN:
                    ui.handle_scroll(3)
                elif event.key == pygame.K_HOME:
                    ui.scroll_y = 0
                elif event.key == pygame.K_END:
                    ui.scroll_to_bottom(engine.move_history_san)

            # ── Click stânga ──────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # --- Popup About (are prioritate maximă) ---
                if show_about:
                    if about_close_rect and about_close_rect.collidepoint(mouse_pos):
                        show_about = False
                    continue   # ignorăm orice alt click cât timp About e deschis

                # --- Butoane panou dreapta ---
                btn_action = _check_button_click(ui.btn_rects, mouse_pos)
                if btn_action == 'restart':
                    engine       = make_new_game(ai)
                    last_move    = None
                    waiting_for_promotion = False
                    ui.scroll_y  = 0
                    maybe_ai_first()
                    continue

                elif btn_action == 'restart_colors':
                    player_color = chess.BLACK if player_color == chess.WHITE else chess.WHITE
                    engine       = make_new_game(ai)
                    last_move    = None
                    waiting_for_promotion = False
                    ui.scroll_y  = 0
                    maybe_ai_first()
                    continue

                elif btn_action == 'about':
                    show_about = True
                    continue

                elif btn_action == 'exit':
                    running = False
                    continue

                # --- Scrollbar ---
                consumed = ui.on_mouse_down(mouse_pos)
                if consumed:
                    continue

                # --- Logica joc (doar dacă e rândul jucătorului) ---
                if engine.board.turn != player_color:
                    continue   # nu e rândul tău

                if waiting_for_promotion:
                    for rect, piece_name in ui.promotion_rects:
                        if rect.collidepoint(mouse_pos):
                            p_type = {'queen': 5, 'rook': 4,
                                      'bishop': 3, 'knight': 2}[piece_name]
                            from_sq, to_sq = promotion_data
                            final_move     = chess.Move(from_sq, to_sq, promotion=p_type)
                            engine.move_history_san.append(engine.board.san(final_move))
                            engine.board.push(final_move)
                            last_move             = final_move
                            waiting_for_promotion = False
                            ui.scroll_to_bottom(engine.move_history_san)

                            draw_current_state(ui, engine, last_move, player_color)
                            pygame.display.flip()

                            last_move = process_ai_move(engine, ai, move_sound) or last_move
                            if last_move:
                                ui.scroll_to_bottom(engine.move_history_san)
                            break
                else:
                    result = engine.handle_click(mouse_pos)

                    if result == "move":
                        last_move = engine.board.peek()
                        if move_sound:
                            move_sound.play()
                        ui.scroll_to_bottom(engine.move_history_san)

                        draw_current_state(ui, engine, last_move, player_color)
                        pygame.display.flip()

                        last_move = process_ai_move(engine, ai, move_sound) or last_move
                        if last_move:
                            ui.scroll_to_bottom(engine.move_history_san)

                    elif isinstance(result, tuple) and result[0] == "promotion_needed":
                        waiting_for_promotion = True
                        promotion_data        = result[1]

            # ── Mouse eliberat ────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                ui.on_mouse_up()

            # ── Mouse mișcat ──────────────────────────────────────────
            elif event.type == pygame.MOUSEMOTION:
                ui.on_mouse_motion(event.pos)

        # 5. Desenare cadru
        draw_current_state(ui, engine, last_move, player_color)

        if waiting_for_promotion:
            ui.draw_promotion_menu(player_color)

        if show_about:
            about_close_rect = ui.draw_about_popup()

        pygame.display.flip()
        clock.tick(60)

    # 6. Închidere
    ai.quit()
    pygame.quit()
    sys.exit()


# ------------------------------------------------------------------ #
# FUNCȚII AJUTĂTOARE                                                  #
# ------------------------------------------------------------------ #

def _check_button_click(btn_rects, mouse_pos):
    """Returnează cheia butonului apăsat sau None."""
    for key, rect in btn_rects.items():
        if rect.collidepoint(mouse_pos):
            return key
    return None


def draw_current_state(ui, engine, last_move, player_color=chess.WHITE):
    ui.screen.fill((0, 0, 0))
    ui.draw_panels()
    ui.draw_move_history(engine.move_history_san)
    ui.draw_player_names(player_color)
    ui.draw_right_panel_buttons(player_color)

    highlights = []
    if last_move:
        highlights.append(last_move.from_square)
        highlights.append(last_move.to_square)
    if engine.selected_square is not None:
        highlights.append(engine.selected_square)

    ui.draw_board(highlights)
    ui.draw_suggestions(engine.board, engine.selected_square)
    ui.draw_pieces(engine.board)


def process_ai_move(engine, ai, move_sound):
    if not engine.board.is_game_over():
        print("Robotul se gândește (4 secunde)...")
        ai_move = ai.get_move(engine.board)
        if ai_move:
            engine.move_history_san.append(engine.board.san(ai_move))
            engine.board.push(ai_move)
            if move_sound:
                move_sound.play()
            return ai_move
    return None


if __name__ == "__main__":
    main()