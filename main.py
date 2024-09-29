import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
from enemy_data import infos
import constants as c

def main(z):
  #inicia o pygame
  pg.init()

  #cria o clock
  clock = pg.time.Clock()

  #cria a janela do jogo
  screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
  pg.display.set_caption("Tower Defence")

  #variáveis do jogo
  game_over = False
  game_outcome = 0# -1 is loss & 1 is win
  level_started = False
  last_enemy_spawn = pg.time.get_ticks()
  placing_turrets = False
  selected_turret = None

  #carregamento das imagens
  #mapa
  map = 'levels/map' + str(z) + '.png'
  map_image = pg.image.load(map).convert_alpha()
  
  #spritesheets das torres
  turret_spritesheets = []
  for x in range(1, (c.TURRET_LEVELS)*3+1):
    turret_sheet = pg.image.load(f'assets/images/turrets/turret_{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)
    
  #imagens individuais das torres no cursor
  cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
  cursor_turret1 = pg.image.load('assets/images/turrets/cursor_turret1.png').convert_alpha()
  cursor_turret2 = pg.image.load('assets/images/turrets/cursor_turret2.png').convert_alpha()
  
  #inimigos
  enemy_images = {
    "weak": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
    "medium": pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
    "strong": pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha(),
    "elite": pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha(),
    "camouflaged": pg.image.load('assets/images/enemies/enemy_5.png').convert_alpha(),
    "armored": pg.image.load('assets/images/enemies/enemy_6.png').convert_alpha()
  }
  
  #botoes
  buy_turret_image = pg.image.load('assets/images/buttons/buy_turret.png').convert_alpha()
  buy_turret_image1 = pg.image.load('assets/images/buttons/buy_turret1.png').convert_alpha()
  buy_turret_image2 = pg.image.load('assets/images/buttons/buy_turret2.png').convert_alpha()
  cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
  upgrade_turret_image = pg.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()
  begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()
  restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
  next_image = pg.image.load('assets/images/buttons/next.png').convert_alpha()
  fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
  
  #gui
  heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
  coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()
  enemy1_image = pg.image.load("assets/images/enemies/enemy_1.png").convert_alpha()
  enemy2_image = pg.image.load("assets/images/enemies/enemy_2.png").convert_alpha()
  enemy3_image = pg.image.load("assets/images/enemies/enemy_3.png").convert_alpha()
  enemy4_image = pg.image.load("assets/images/enemies/enemy_4.png").convert_alpha()
  enemy5_image = pg.image.load("assets/images/enemies/enemy_5.png").convert_alpha()
  enemy6_image = pg.image.load("assets/images/enemies/enemy_6.png").convert_alpha()

  #som........
  shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
  shot_fx.set_volume(0.5)

  #carregamento do json data
  tmj = 'levels/map' + str(z) + '.tmj'
  with open(tmj) as file:
    world_data = json.load(file)

  #carregamento das fontes usadas
  text_font = pg.font.SysFont("Consolas", 24, bold = True)
  large_font = pg.font.SysFont("Consolas", 36)

  #funçao para desenhar o texto na tela
  def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
  
  #funçao para desenhar as informaçoes da lateral
  def display_data():
    #desenha o painel
    pg.draw.rect(screen, "#b5edf5", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
    
    #desenha as informaçoes da lateral
    if world.level != 11:
      draw_text("LEVEL: " + str(world.level), text_font, "grey0", c.SCREEN_WIDTH + 10, 10)
      screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
      draw_text(str(world.health), text_font, "grey0", c.SCREEN_WIDTH + 50, 40)
      screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
      draw_text(str(world.money), text_font, "grey0", c.SCREEN_WIDTH + 50, 70)
      screen.blit(enemy1_image, (c.SCREEN_WIDTH, 430))
      screen.blit(enemy2_image, (c.SCREEN_WIDTH, 510))
      screen.blit(enemy3_image, (c.SCREEN_WIDTH + 150, 430))
      screen.blit(enemy4_image, (c.SCREEN_WIDTH + 150, 510))
      screen.blit(enemy5_image, (c.SCREEN_WIDTH, 590))
      screen.blit(enemy6_image, (c.SCREEN_WIDTH + 150, 590))
      draw_text(": " + str(infos[world.level]["weak"]), text_font, "grey0", c.SCREEN_WIDTH + 60, 480)
      draw_text(": " + str(infos[world.level]["medium"]), text_font, "grey0", c.SCREEN_WIDTH + 60, 560)
      draw_text(": " + str(infos[world.level]["camouflaged"]), text_font, "grey0", c.SCREEN_WIDTH + 60, 640)
      draw_text(": " + str(infos[world.level]["strong"]), text_font, "grey0", c.SCREEN_WIDTH + 210, 480)
      draw_text(": " + str(infos[world.level]["elite"]), text_font, "grey0", c.SCREEN_WIDTH + 210, 560)
      draw_text(": " + str(infos[world.level]["armored"]), text_font, "grey0", c.SCREEN_WIDTH + 210, 640)

  #funçao para criar a torre
  def create_turret(mouse_pos, id):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    #calcula o número sequencial do tile
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
    #checa se a posiçao é válida
    if world.tile_map[mouse_tile_num] == 67 or world.tile_map[mouse_tile_num] == 109 or world.tile_map[mouse_tile_num] == 20:
      #checa se já tem alguma torre na posiçao
      space_is_free = True
      for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
          space_is_free = False
      #se o espaço estiver livre, cria a torre
      if space_is_free == True:
        new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx, id)
        turret_group.add(new_turret)
        #tira o custo da torre
        if id == 1:
          world.money -= c.BUY_COST
        if id == 2:
          world.money -= c.BUY_COST1
        if id == 3:
          world.money -= c.BUY_COST2
          
  #funçao para selecionar a torre
  def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        return turret

  #funçao para tirar a seleçao da torre
  def clear_selection():
    for turret in turret_group:
      turret.selected = False

  #cria o mundo do jogo
  world = World(world_data, map_image)
  world.process_data()
  world.process_enemies()

  #cria os grupos de torres e inimigos
  enemy_group = pg.sprite.Group()
  turret_group = pg.sprite.Group()

  #cria os botoes
  turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
  turret_button1 = Button(c.SCREEN_WIDTH + 30, 180, buy_turret_image1, True)
  turret_button2 = Button(c.SCREEN_WIDTH + 30, 240, buy_turret_image2, True)
  cancel_button = Button(c.SCREEN_WIDTH + 50, 300, cancel_image, True)
  upgrade_button = Button(c.SCREEN_WIDTH + 30, 300, upgrade_turret_image, True)
  begin_button = Button(c.SCREEN_WIDTH + 60, 360, begin_image, True)
  restart_button = Button(310, 300, restart_image, True)
  next_button = Button(310, 300, next_image, True)
  fast_forward_button = Button(c.SCREEN_WIDTH + 50, 360, fast_forward_image, False)

  #loop do jogo
  run = True
  while run:
    clock.tick(c.FPS)

    #update do jogo
    if game_over == False:
      #checa se o jogador perdeu
      if world.health <= 0:
        game_over = True
        game_outcome = -1
      #checa se o jogador ganhou
      if world.level > c.TOTAL_LEVELS:
        game_over = True
        game_outcome = 1
      
      #update dos grupos
      enemy_group.update(world)
      turret_group.update(enemy_group, world)

      #seleçao da torre
      if selected_turret:
        selected_turret.selected = True


    #desenhos
    world.draw(screen)

    #desenha os grupos
    enemy_group.draw(screen)
    for turret in turret_group:
      turret.draw(screen)

    display_data()

    if game_over == False:
      #checa se o jogador iniciou a rodada
      if level_started == False:
        if begin_button.draw(screen):
          level_started = True
      else:
        #botao de acelerar a rodada
        world.game_speed = 1
        if fast_forward_button.draw(screen):
          world.game_speed = 5
          spawn_cd=0.2
        else:
          spawn_cd=1
        #spawn dos inimigos
        if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN*spawn_cd:
          if world.spawned_enemies < len(world.enemy_list):
            enemy_type = world.enemy_list[world.spawned_enemies]
            enemy = Enemy(enemy_type, world.waypoints, enemy_images)
            enemy_group.add(enemy)
            world.spawned_enemies += 1
            last_enemy_spawn = pg.time.get_ticks()

      #checa se o grupo de inimigos terminou
      if world.check_level_complete() == True:
        world.money += c.LEVEL_COMPLETE_REWARD
        world.level += 1
        level_started = False
        last_enemy_spawn = pg.time.get_ticks()
        world.reset_level()
        world.process_enemies()

      #desenho dos botoes
      #botao para comprar as torres
      #pro botao das torres, tem que botar o custo e a imagem da moeda
      draw_text(str(c.BUY_COST), text_font, "grey0", c.SCREEN_WIDTH + 215, 135)
      draw_text(str(c.BUY_COST1), text_font, "grey0", c.SCREEN_WIDTH + 215, 195)
      draw_text(str(c.BUY_COST2), text_font, "grey0", c.SCREEN_WIDTH + 215, 255)
      screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
      screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
      screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 250))
      if turret_button.draw(screen):
        placing_turrets = True
        id = 1
      if turret_button1.draw(screen):
        placing_turrets = True
        id = 2
      if turret_button2.draw(screen):
        placing_turrets = True
        id = 3
      #se tiver clicado no botao de comprar torre, aparece o botao de cancelar
      if placing_turrets == True:
        #mostra a torre escolhida no cursor
        cursor_rect = cursor_turret.get_rect()
        cursor_pos = pg.mouse.get_pos()
        cursor_rect.center = cursor_pos
        if cursor_pos[0] <= c.SCREEN_WIDTH:
          if id == 1:
            screen.blit(cursor_turret, cursor_rect)
          if id == 2:
            screen.blit(cursor_turret1, cursor_rect)
          if id == 3:
            screen.blit(cursor_turret2, cursor_rect)
        if cancel_button.draw(screen):
          placing_turrets = False
      #se uma torre tiver selecionada, mostra o botao para fazer o upgrade
      if selected_turret:
        #se for possível dar upgrade na torre, aparece a opçao
        if selected_turret.upgrade_level < c.TURRET_LEVELS:
          #mostra o custo e desenha o botao
          draw_text(str(c.UPGRADE_COST), text_font, "grey0", c.SCREEN_WIDTH + 215, 312)
          screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 307))
          if upgrade_button.draw(screen):
            if world.money >= c.UPGRADE_COST:
              selected_turret.upgrade()
              world.money -= c.UPGRADE_COST
    else:
      #desenha a tela de fim de jogo, tanto para a vitória, quanto para a derrota
      pg.draw.rect(screen, (56, 75, 213), (200, 200, 400, 200), border_radius = 30)
      if game_outcome == -1:
        draw_text("FIM DE JOGO!", large_font, "grey0", 295, 230)
        #reinicia o nível
        if restart_button.draw(screen):
          game_over = False
          level_started = False
          placing_turrets = False
          selected_turret = None
          last_enemy_spawn = pg.time.get_ticks()
          world = World(world_data, map_image)
          world.process_data()
          world.process_enemies()
          #esvazia os grupos
          enemy_group.empty()
          turret_group.empty()
      elif game_outcome == 1:
        draw_text("VOCÊ VENCEU!", large_font, "grey0", 280, 230)
        if next_button.draw(screen):
          #caso vença, aparecerá o botao para ir para o próximo mapa
          if z != 1:
            main(z-1)
          break
            
    #captador de eventos
    for event in pg.event.get():
      #fechar o programa
      if event.type == pg.QUIT:
        run = False
      #click do mouse
      if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pg.mouse.get_pos()
        #checa se o mouse ta na área do jogo
        if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
          #limpa a seleçao da torre
          selected_turret = None
          clear_selection()
          if placing_turrets == True:
            #checa se tem dinheiro suficiente para comprar a torre
            if world.money >= c.BUY_COST:
                create_turret(mouse_pos, id)
          else:
            selected_turret = select_turret(mouse_pos)

    #update da tela
    pg.display.flip()    
    
  pg.quit()

#chamo a funçao principal da primeira fase e o resto é recursivo
main(3)
