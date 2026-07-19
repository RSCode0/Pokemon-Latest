import json
import pygame
import random

from pokemon import Pokemon
from utils import ease_out_cubic

import math

class Fight:
    def __init__(self, type, player_pokedex, ennemi_pokemons, screen: pygame.Surface, keys):
        self.screen          = screen
        self.keys            = keys
        self.type            = type
        self.player_pokedex = player_pokedex
        self.player_pokedex.state = "choose_fight"
        self.ennemi_pokemons = ennemi_pokemons

        self.font       = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 22)
        self.font_big   = pygame.font.Font(None, 40)

        self.ennemi_pokemons_stats   = {}
        self.ennemi_pokemons_base_hp = {}
        self.ennemi_pokemons_moves   = {}
        self.player_pokemons_stats   = {}
        self.player_pokemons_base_hp = {}
        self.player_pokemons_moves   = {}
        self.player_pokemons_images  = {}
        self.ennemi_pokemons_images  = {}

        if len(self.ennemi_pokemons) == 1:
            self.player_pokedex.max_team = 1
        else: 
            self.player_pokedex.max_team = 2
        self.selected_team   = []

        self.player_selected_pokemon = None
        self.ennemi_selected_pokemon = self.ennemi_pokemons[0]

        self.state = "select_team"

        self.acting_pokemon  = None
        self.pending_move    = None
        self.player_actions  = []
        self.actions_done    = 0

        self.log_message  = ""
        self.log_timer    = 0
        self.LOG_DURATION = 1800

        self.animation_duration = 800

        self.typewritter_speed = 20
        self.last_typwritter_time = 20
        self.current_time = 0

        self.in_animation = False
        self.frame_index = 0

        self.pokeball_escape_images = [pygame.image.load(f"venv/assets/sprite/items/pokeballs/pokeball_animation_escape/frame_{i}.png") for i in range(1, 6)]

        self.is_over  = False
        self.winner   = None

        self._player_sprite_rects = {}
        self._ennemi_sprite_rects = {}

        self._load_ennemi()

    def _load_ennemi(self):
        self._load_ennemi_stats()
        self._load_ennemi_moves()
        self._load_ennemi_images()

    def _load_ennemi_stats(self):
        with open("venv/code/json/pokemon_gen1.json", encoding="utf-8") as f:
            data = json.load(f)
        for pokemon in self.ennemi_pokemons:
            name  = pokemon["name"]
            stats = json.loads(json.dumps(data[name]))
            stats["level"]       = pokemon["stats"]["level"]
            stats["stats"]["hp"] = int(pokemon["stats"]["stats"]["hp"])
            self.ennemi_pokemons_stats[name]   = stats
            self.ennemi_pokemons_base_hp[name] = int(stats["stats"]["hp"])

    def _load_ennemi_moves(self):
        with open("venv/code/json/moves_gen1.json", encoding="utf-8") as f:
            data_moves = json.load(f)
        for name, stats in self.ennemi_pokemons_stats.items():
            moves = [data_moves[m["name"]] for m in stats.get("moves", [])
                     if m["learn_level"] <= stats["level"] and m["name"] in data_moves]
            if not moves and "Tackle" in data_moves:
                moves.append(data_moves["Tackle"])
            self.ennemi_pokemons_moves[name] = moves

    def _load_ennemi_images(self):
        for pokemon in self.ennemi_pokemons:
            name = pokemon["name"]
            img  = pygame.image.load(
                f"venv/assets/pokemons/pokemons_gen1_fronts/{name}_front.png"
            ).convert_alpha()
            self.ennemi_pokemons_images[name] = pygame.transform.scale2x(img)

    def _load_player_team(self):
        with open("venv/code/json/pokemon_gen1.json", encoding="utf-8") as f:
            data = json.load(f)
        with open("venv/code/json/moves_gen1.json", encoding="utf-8") as f:
            data_moves = json.load(f)

        for slot in self.selected_team:
            pokemon = self.player_pokedex["pokemons"][slot]
            pname   = pokemon["name"]
            stats   = json.loads(json.dumps(data[pname]))
            level   = pokemon.get("stats", {}).get("level", 1)
            stats["level"]       = level
            stats["stats"]["hp"] = int(stats["stats"]["hp"])
            self.player_pokemons_stats[slot]   = stats
            self.player_pokemons_base_hp[slot] = int(stats["stats"]["hp"])

            moves = [data_moves[m["name"]] for m in stats.get("moves", [])
                     if m["learn_level"] <= level and m["name"] in data_moves]
            if not moves and "Tackle" in data_moves:
                moves.append(data_moves["Tackle"])
            self.player_pokemons_moves[slot] = moves

            img = pygame.image.load(
                f"venv/assets/pokemons/pokemons_gen1_backs/{pname}_backs.png"
            ).convert_alpha()
            self.player_pokemons_images[slot] = pygame.transform.scale_by(img, 2.5)

    def _calc_damage(self, atk_stats, def_stats, move):
        power   = int(move.get("power") or 0)
        if power == 0:
            return 0
        level   = int(atk_stats.get("level", 1))
        attack  = int(atk_stats["stats"].get("attack", 10))
        defense = int(def_stats["stats"].get("defense", 10))
        dmg     = (((2 * level / 5 + 2) * power * attack / defense) / 50 + 2)
        return max(1, int(dmg * random.randint(85, 100) / 100))

    def _alive_players(self):
        return [s for s, st in self.player_pokemons_stats.items()
                if int(st["stats"]["hp"]) > 0]

    def _alive_ennemis(self):
        return [n for n, st in self.ennemi_pokemons_stats.items()
                if int(st["stats"]["hp"]) > 0]

    def _next_actor(self):
        acted = {a for a, _, _ in self.player_actions}
        for slot in self._alive_players():
            if slot not in acted:
                return slot
        return None

    def _execute_player_actions(self):
        for attacker, move, target in self.player_actions:
            if int(self.player_pokemons_stats[attacker]["stats"]["hp"]) <= 0:
                continue
            if int(self.ennemi_pokemons_stats[target]["stats"]["hp"]) <= 0:
                alive = self._alive_ennemis()
                if not alive:
                    break
                target = alive[0]
            atk_stats = self.player_pokemons_stats[attacker]
            def_stats = self.ennemi_pokemons_stats[target]
            dmg = self._calc_damage(atk_stats, def_stats, move)
            def_stats["stats"]["hp"] = max(0, int(def_stats["stats"]["hp"]) - dmg)
            pname = atk_stats.get("name", attacker)
            self._set_log(f"{pname} utilise {move['name']} sur {target} ! ({dmg} dégâts)")
            if int(def_stats["stats"]["hp"]) <= 0:
                self._set_log(f"{target} est K.O. !")

        self.player_actions = []
        if not self._alive_ennemis():
            self.state  = "over"
            self.winner = "player"
        else:
            self.state = "ennemi_attack"

    def _ennemi_attack_turn(self):
        alive_players = self._alive_players()
        if not alive_players:
            self.state  = "over"
            self.winner = "ennemi"
            return
        for e_name in self._alive_ennemis():
            moves  = self.ennemi_pokemons_moves.get(e_name, [])
            if not moves:
                continue
            move   = random.choice(moves)
            target = random.choice(alive_players)
            atk    = self.ennemi_pokemons_stats[e_name]
            defn   = self.player_pokemons_stats[target]
            dmg    = self._calc_damage(atk, defn, move)
            defn["stats"]["hp"] = max(0, int(defn["stats"]["hp"]) - dmg)
            pname = self.player_pokemons_stats[target].get("name", target)
            self._set_log(f"{e_name} utilise {move['name']} sur {pname} ! ({dmg} dégâts)")
            if int(defn["stats"]["hp"]) <= 0:
                self._set_log(f"{pname} est K.O. !")
                alive_players = self._alive_players()
                if not alive_players:
                    break

        if not self._alive_players():
            self.state  = "over"
            self.winner = "ennemi"
        else:
            self.handle_input()
            self.state = "choose_move"

    def _set_log(self, msg):
        self.log_message = msg
        self.log_timer   = self.LOG_DURATION

    def handle_input(self):
        mouse_pos     = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_just_pressed()

        if self.state == "over":
            if self.keys and self.keys.is_pressed(pygame.K_SPACE):
                self.keys.remove_key(pygame.K_SPACE)
                self.is_over = True
            return

        if self.state == "ennemi_attack":
            if self.log_timer <= 0:
                self._ennemi_attack_turn()
            return

        if self.state == "choose_move":
            self._handle_choose_move(mouse_pos, mouse_clicked)

        elif self.state == "choose_target":
            self._handle_choose_target(mouse_pos, mouse_clicked)

        if self.keys and self.keys.is_pressed(pygame.K_ESCAPE):
            self.keys.remove_key(pygame.K_ESCAPE)
            self.pending_move   = None
            self.acting_pokemon = self._next_actor()
            self.state = "choose_move"

    def _handle_choose_move(self, mouse_pos, mouse_clicked):
        if mouse_clicked[0]:
            for slot, rect in self._player_sprite_rects.items():
                if rect.collidepoint(mouse_pos) and int(self.player_pokemons_stats[slot]["stats"]["hp"]) > 0:
                    acted = {a for a, _, _ in self.player_actions}
                    if slot not in acted:
                        self.acting_pokemon = slot
                    break

        if self.acting_pokemon:
            self._handle_move_menu_click(mouse_pos, mouse_clicked)

    def _handle_move_menu_click(self, mouse_pos, mouse_clicked):
        moves = self.player_pokemons_moves.get(self.acting_pokemon, [])
        rects = self._get_move_rects(moves)
        for i, rect in enumerate(rects):
            if rect.collidepoint(mouse_pos):
                if mouse_clicked[0] and i < len(moves):
                    self.pending_move = moves[i]
                    self.state = "choose_target"
                    return

    def _handle_choose_target(self, mouse_pos, mouse_clicked):
        if not mouse_clicked[0]:
            return
        for name, rect in self._ennemi_sprite_rects.items():
            if rect.collidepoint(mouse_pos) and int(self.ennemi_pokemons_stats[name]["stats"]["hp"]) > 0:
                self.player_actions.append((self.acting_pokemon, self.pending_move, name))
                self.pending_move   = None
                self.acting_pokemon = None
                self._execute_player_actions()
    
    def draw_starting_animation(self):
        dt_ms = pygame.time.get_ticks()
        elapsed = -(self.started_animation_ms - dt_ms)

        p_iw, p_ih = self.player_pokemons_images[self.player_selected_pokemon].get_size()
        p_pos = [120 + (p_iw + 20), 780 - 250 - p_ih]
        e_iw, e_ih = self.ennemi_pokemons_images[self.ennemi_selected_pokemon["name"]].get_size()
        e_pos = [1280 - 200 - (e_iw + 20) - e_iw, 80]

        if self.animation_duration > elapsed:
            t = elapsed / self.animation_duration
            t_eased = ease_out_cubic(t)

            offset = -(500 * (1 - t_eased))

            self._draw_platform(p_pos[0] + p_iw // 2 - offset, p_pos[1] + p_ih, p_iw + 40)
            self._draw_platform(e_pos[0] + e_iw // 2 + offset, e_pos[1] + e_ih, e_iw + 40)
        else:
            self._draw_platform(p_pos[0] + p_iw // 2, p_pos[1] + p_ih, p_iw + 40)
            self._draw_platform(e_pos[0] + e_iw // 2, e_pos[1] + e_ih, e_iw + 40)
            if not self.in_animation:
                self.in_animation = True
                self.pokemon_entering_animation_ms = pygame.time.get_ticks()
            self.pokemon_entering_animation("player", [20, 20], [p_pos[0] + p_iw // 2, p_pos[1] + p_ih])
            self.pokemon_entering_animation("ennemi", [1280 + 200, - 200], [e_pos[0] + e_iw // 2, e_pos[1] + e_ih])

    def pokemon_entering_animation(self, name, start, end):
        dt_ms = pygame.time.get_ticks()
        elapsed = -(self.pokemon_entering_animation_ms - dt_ms)

        t = elapsed / self.animation_duration
        t = 1 - (1 - t) ** 3

        x = start[0] + (end[0] - start[0]) * t
        y = (start[1] + (end[1] - start[1]) * t)

        pos = [x, y]

        self.frame_index += 1
        self.frame_index = int(self.frame_index) % (len(self.pokeball_escape_images) - 1)

        fade_t = (elapsed - 800) / self.animation_duration
        fade_t = 1 - (1 - fade_t) ** 3
        alpha = 255 * fade_t

        rect = self.pokeball_escape_images[self.frame_index].get_rect(center=pos)
        if elapsed < self.animation_duration:
            self.screen.blit(self.pokeball_escape_images[self.frame_index], rect)
        else:
            if elapsed - 100 < self.animation_duration:
                self.screen.blit(self.pokeball_escape_images[4], rect)
            else:
                if elapsed - 800 < self.animation_duration:
                    pokemon_surface = self.player_pokemons_images[self.player_selected_pokemon] if name == "player" else self.ennemi_pokemons_images[self.ennemi_selected_pokemon["name"]]
                    rect = pokemon_surface.get_rect(midbottom=end)
                    pokemon_surface.set_alpha(0 if alpha < 0 else alpha)
                    self.screen.blit(pokemon_surface, rect)
                else:
                    self.draw_pokemons()
                    self.state = "choose_move"

    def draw_fight(self):
        dt_ms = pygame.time.get_ticks()
        if not hasattr(self, '_last_ticks'):
            self._last_ticks = dt_ms
        elapsed = dt_ms - self._last_ticks
        self._last_ticks = dt_ms
        if self.log_timer > 0:
            self.log_timer -= elapsed

        if self.state == "select_team":
            self._draw_team_selection()
            self.handle_input()
            return

        self.screen.fill((240, 240, 220))
        self._draw_battlefield_bg()
        if self.state == "starting_animation":
            if not hasattr(self, "started_animation_ms"):
                self.started_animation_ms = pygame.time.get_ticks()
            self.draw_starting_animation()
        else:
            self.draw_pokemons()

        self._draw_ui_panel()

        if self.state in ("choose_move", "choose_target"):
            if self.acting_pokemon:
                self._draw_move_menu()
        if self.state == "choose_target":
            self._draw_target_hint()

        if self.log_timer > 0:
            self._draw_log()
        if self.state == "over":
            self._draw_over_screen()

        self.handle_input()

    def _draw_team_selection(self):
        self.selected = self.player_pokedex.draw_pokedex(self.keys)
        if self.selected:
            self.selected_team = self.selected
            self.player_selected_pokemon = self.selected_team[0]
            self._load_player_team()
            self.state = "starting_animation"

    def _draw_battlefield_bg(self):
        SW, SH = self.screen.get_size()
        surface = pygame.Surface((SW, SH), pygame.SRCALPHA)
        for i in range(SH // 2):
            pygame.draw.line(surface, [100, 160, 120, 100], (0, i * 2), (SW, i * 2))
        self.screen.blit(surface, (0, 0))

    def _draw_platform(self, cx, bottom_y, w=260, h=28, color=(160, 200, 120)):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (cx, bottom_y + h // 2 - 10)
        pygame.draw.ellipse(self.screen, color, rect)

    def draw_pokemons(self):
        SW, SH = self.screen.get_size()

        x_base = 120
        y_base = SH - 250
        slot = self.player_selected_pokemon

        if int(self.player_pokemons_stats[slot]["stats"]["hp"]) <= 0:
            self.player_pokemons_stats
        img = self.player_pokemons_images.get(slot)
        if img is not None:
            iw, ih = img.get_size()
            pos = (x_base + (iw + 20), y_base - ih)
            cx  = pos[0] + iw // 2
            self._draw_platform(cx, pos[1] + ih, w=iw + 40, color=(180, 210, 140))
            self.screen.blit(img, pos)
            rect = pygame.Rect(*pos, iw, ih)
            self._player_sprite_rects[slot] = rect

        if self.state == "choose_move":
            mouse = pygame.mouse.get_pos()
            if rect.collidepoint(mouse):
                w, h = iw + 40, 28
                bottom_y = pos[1] + ih
                color = (100, 200, 100)
                rect = pygame.Rect(0, 0, w, h)
                rect.center = (cx, bottom_y + h // 2 - 10)
                pygame.draw.ellipse(self.screen, color, rect, 3)

        name = self.player_pokemons_stats[slot].get("name", slot)
        lvl  = self.player_pokemons_stats[slot].get("level", "?")

        self._draw_hp_bar(pos[0] + iw + 50, pos[1] + ih // 2, iw ,self.player_pokemons_stats[slot]["stats"]["hp"],self.player_pokemons_base_hp[slot], lvl, name)

        x_base = SW - 200
        y_base = 80
        name = self.ennemi_selected_pokemon["name"]
        if int(self.ennemi_pokemons_stats[name]["stats"]["hp"]) <= 0:
            pass
        img = self.ennemi_pokemons_images.get(name)
        if img is not None:
            iw, ih = img.get_size()
            pos = (x_base - (iw + 20) - iw, y_base)
            cx  = pos[0] + iw // 2
            self._draw_platform(cx, pos[1] + ih, w=iw + 40, color=(160, 200, 120))
            self.screen.blit(img, pos)
            rect = pygame.Rect(*pos, iw, ih)
            self._ennemi_sprite_rects[name] = rect

        if self.state == "choose_target":
            mouse = pygame.mouse.get_pos()
            if rect.collidepoint(mouse):
                w, h = iw + 40, 28
                bottom_y = pos[1] + ih
                color = (200, 100, 100)
                rect = pygame.Rect(0, 0, w, h)
                rect.center = (cx, bottom_y + h // 2 - 10)
                pygame.draw.ellipse(self.screen, color, rect, 3)

        lvl = self.ennemi_pokemons_stats[name].get("level", "?")
        self._draw_hp_bar(pos[0] - iw - 100, pos[1] + ih // 2, iw,self.ennemi_pokemons_stats[name]["stats"]["hp"],self.ennemi_pokemons_base_hp[name], lvl, name)

    def _draw_hp_bar(self, x, y, width, hp, base_hp, lvl, name):
        hp      = max(0, int(hp))
        base_hp = max(1, int(base_hp))
        ratio   = hp / base_hp
        bar_w   = int(width * ratio)
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, width, 12), border_radius=4)
        color = (60, 200, 60) if ratio > 0.5 else (220, 180, 0) if ratio > 0.25 else (200, 40, 40)
        if bar_w > 0:
            pygame.draw.rect(self.screen, color, (x, y, bar_w, 12), border_radius=4)
        self.screen.blit(
            self.font_small.render(f"{hp}/{base_hp}", True, (255, 255, 255)),
            (x + width + 6, y - 2)
        )

    def _draw_ui_panel(self):
        SW, SH = self.screen.get_size()

        pygame.draw.rect(self.screen, (80, 80, 80), (0, 780 - 200, SW, 200))
        if not self.state == "choose_move":
            pygame.draw.rect(self.screen, (80, 80, 80), (200, 780 - 150, 1280 - 400, 140), 0, 10)
            pygame.draw.rect(self.screen, (245, 206, 78), (200, 780 - 150, 1280 - 400, 140), 2, 10)
            pygame.draw.rect(self.screen, (255, 255, 255), (220, 780 - 140, 1280 - 500, 120), 0, 10)

        if self.state == "choose_move":
            if not self.acting_pokemon:
                self.handle_input()
                txt = "Choisissez un pokemon"
            elif self.acting_pokemon:
                pname = self.player_pokemons_stats[self.acting_pokemon].get("name", self.acting_pokemon)
                txt = f"Choisissez une attaque pour {pname}"
            else:
                txt = "Cliquez sur un de vos Pokémons pour choisir son attaque"
            surf = self.font.render(txt, True, (40, 40, 40))
            self.screen.blit(surf, surf.get_rect(center=(SW // 2, SH - 80)))

        elif self.state == "choose_target":
            pname = self.player_pokemons_stats[self.acting_pokemon].get("name", self.acting_pokemon)
            move_name = self.pending_move.get("name", "???") if self.pending_move else "???"
            surf = self.font.render(f"{pname} utilise {move_name} : cliquez sur un ennemi", True, (255, 200, 80))
            self.screen.blit(surf, surf.get_rect(center=(SW // 2, SH - 80)))

        elif self.state == "ennemi_attack":
            surf = self.font.render("L'ennemi prépare son attaque…", True, (220, 140, 140))
            self.screen.blit(surf, surf.get_rect(center=(SW // 2, SH - 80)))

    def _get_move_rects(self, moves):
        SW, SH = self.screen.get_size()
        btn_w, btn_h = (SW // 2) - 200, 200 // 2 - 20
        x0 = 200 - 20
        y0 = SH - (200 - 10)

        lines = []
        current_line = []
        index = 0
        for move in moves:
            index += 1
            if index <= 2:
                current_line.append(move)
            else:
                lines.append(move)
                current_line = []
            lines.append(current_line)
        
        rects = []
        for i, line in enumerate(lines):
            for j, move in enumerate(line):
                rects.append(pygame.rect.Rect((x0 + j * (btn_w + 20), y0 + i * (btn_h + 20), btn_w, btn_h)))
        return rects


    def _draw_move_menu(self):
        moves = self.player_pokemons_moves.get(self.acting_pokemon, [])
        if not moves:
            return
        rects = self._get_move_rects(moves)
        mouse = pygame.mouse.get_pos()

        for move, rect in zip(moves, rects):
            hovered = rect.collidepoint(mouse)
            color   = (120, 120, 120, 255) if hovered else (200, 200, 200, 255)
            surface = pygame.Surface(self.screen.size, pygame.SRCALPHA)
            
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, (170, 170, 170, 255), (rect.x, rect.y, rect.width, rect.height // 2), 0, 5)
            pygame.draw.rect(surface, (20, 20, 20), rect, 2, border_radius=5)

            self.screen.blit(surface, (0, 0))
            self.screen.blit(
                self.font.render(move.get("name", "???"), True, (40, 40, 40)),
                self.font.render(move.get("name", "???"), True, (40, 40, 40)).get_rect(center=rect.center).move(0, -8)
            )
            power = move.get("power") or "inconnu"
            info  = self.font_small.render(f"Puissance : {power}", True, (80, 80, 80))
            self.screen.blit(info, info.get_rect(center=rect.center).move(0, 12))

    def _draw_target_hint(self):
        SW, SH = self.screen.get_size()
        surf = self.font_small.render("Cliquez sur un ennemi pour attaquer", True, (255, 160, 60))
        self.screen.blit(surf, surf.get_rect(center=(SW // 2, SH - 230)))

    def _draw_log(self):
        SW, SH = self.screen.get_size()
        ratio   = self.log_timer / self.LOG_DURATION
        if ratio > (1 - 200 / self.LOG_DURATION):
            alpha = int(255 * (1 - ratio) / (200 / self.LOG_DURATION))
        elif ratio < (400 / self.LOG_DURATION):
            alpha = int(255 * ratio / (400 / self.LOG_DURATION))
        else:
            alpha = 255
        alpha = max(0, min(255, alpha))

        font_log   = pygame.font.Font("venv/assets/fonts/Abel-Regular.ttf", 26)
        px, py     = 28, 14
        text_surf  = font_log.render(self.log_message, True, (255, 255, 255))
        tw, th     = text_surf.get_size()
        bg_w, bg_h = tw + px * 2, th + py * 2
        bx = SW // 2 - bg_w // 2
        by = SH - 160

        bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        pygame.draw.rect(bg, (10, 10, 30), (0, 0, bg_w, bg_h), border_radius=12)
        border = (255, 60, 60) if "K.O" in self.log_message else (80, 200, 255) if "utilise" in self.log_message else (255, 200, 0)
        pygame.draw.rect(bg, (*border, 255), (0, 0, bg_w, bg_h), 3, border_radius=12)
        bg.set_alpha(alpha)
        self.screen.blit(bg, (bx, by))
        text_surf.set_alpha(alpha)
        self.screen.blit(text_surf, (bx + px, by + py))

    def _draw_over_screen(self):
        SW, SH = self.screen.get_size()
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        msg   = "Victoire !" if self.winner == "player" else "Défaite…"
        color = (80, 255, 120) if self.winner == "player" else (255, 80, 80)
        self.screen.blit(
            self.font_big.render(msg, True, color),
            self.font_big.render(msg, True, color).get_rect(center=(SW // 2, SH // 2))
        )
        self.screen.blit(
            self.font.render("Appuyez sur ESPACE pour continuer", True, (200, 200, 200)),
            self.font.render("Appuyez sur ESPACE pour continuer", True, (200, 200, 200)).get_rect(center=(SW // 2, SH // 2 + 55))
        )
    
    def over(self):
        if self.type == "pokemon":
            self.player_pokedex.add_pokemon(Pokemon(self.ennemi_pokemons[0]))