import pygame as pg
import math
import constants as c
from turret_data import TURRET_DATA_NORMAL
from turret_data import TURRET_DATA_CAMOUFLAGED
from turret_data import TURRET_DATA_ARMORED

class Turret(pg.sprite.Sprite):
  def __init__(self, sprite_sheets, tile_x, tile_y, shot_fx, id):
    pg.sprite.Sprite.__init__(self)
    self.upgrade_level = 1
    self.id = id
    if self.id == 1:
      self.range = TURRET_DATA_NORMAL[self.upgrade_level - 1].get("range")
      self.cooldown = TURRET_DATA_NORMAL[self.upgrade_level - 1].get("cooldown")
      self.special = TURRET_DATA_NORMAL[self.upgrade_level - 1].get("special")
    elif self.id == 2:
      self.range = TURRET_DATA_CAMOUFLAGED[self.upgrade_level - 1].get("range")
      self.cooldown = TURRET_DATA_CAMOUFLAGED[self.upgrade_level - 1].get("cooldown")
      self.special = TURRET_DATA_CAMOUFLAGED[self.upgrade_level - 1].get("special")
    elif self.id == 3:
      self.range = TURRET_DATA_ARMORED[self.upgrade_level - 1].get("range")
      self.cooldown = TURRET_DATA_ARMORED[self.upgrade_level - 1].get("cooldown")
      self.special = TURRET_DATA_ARMORED[self.upgrade_level - 1].get("special")
    self.last_shot = pg.time.get_ticks()
    self.selected = False
    self.target = None

    #variáveis da posiçao
    self.tile_x = tile_x
    self.tile_y = tile_y
    #calcula o centro da coordenada
    self.x = (self.tile_x + 0.5) * c.TILE_SIZE
    self.y = (self.tile_y + 0.5) * c.TILE_SIZE
    #som do disparo
    self.shot_fx = shot_fx

    #variáveis da animaçao
    self.sprite_sheets = sprite_sheets
    if self.id == 1:
      self.animation_list = self.load_images(self.sprite_sheets[(self.upgrade_level - 1)])
    if self.id == 2:
      self.animation_list = self.load_images(self.sprite_sheets[(self.upgrade_level + 3)])
    if self.id == 3:
      self.animation_list = self.load_images(self.sprite_sheets[(self.upgrade_level + 7)])
    self.frame_index = 0
    self.update_time = pg.time.get_ticks()

    #update da imagem
    self.angle = 90
    self.original_image = self.animation_list[self.frame_index]
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)

    #cria circulo transparente para mostrar o alcance
    self.range_image = pg.Surface((self.range * 2, self.range * 2))
    self.range_image.fill((0, 0, 0))
    self.range_image.set_colorkey((0, 0, 0))
    pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
    self.range_image.set_alpha(100)
    self.range_rect = self.range_image.get_rect()
    self.range_rect.center = self.rect.center

  def load_images(self, sprite_sheet):
    #extrai as imagens do spritesheet
    size = sprite_sheet.get_height()
    animation_list = []
    for x in range(c.ANIMATION_STEPS):
      temp_img = sprite_sheet.subsurface(x * size, 0, size, size)
      animation_list.append(temp_img)
    return animation_list

  def update(self, enemy_group, world):
    #se um alvo for selecionado, ativa a animaçao de disparo
    if self.target:
      self.play_animation()
    else:
      #procura um novo alvo caso esteja parada
      if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
        self.pick_target(enemy_group)

  def pick_target(self, enemy_group):
    #procura o alvo
    x_dist = 0
    y_dist = 0
    #verifica a distancia de cada inimigo para saber se eles estao no alcance
    for enemy in enemy_group:
      if enemy.health > 0:
        if self.id ==  enemy.special+1 or enemy.special == 0:
          x_dist = enemy.pos[0] - self.x
          y_dist = enemy.pos[1] - self.y
          dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
          if dist < self.range:
            self.target = enemy
            self.angle = math.degrees(math.atan2(-y_dist, x_dist))
            #da dano no inimigo
            self.target.health -= c.DAMAGE * self.id
            #realiza o som do disparo
            self.shot_fx.play()
            break

  def play_animation(self):
    #update da imagem
    self.original_image = self.animation_list[self.frame_index]
    #checa se já passou tempo suficiente desde a ultima animaçao
    if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
      self.update_time = pg.time.get_ticks()
      self.frame_index += 1
      #checa se a animaçao terminou e reseta para o repouso
      if self.frame_index >= len(self.animation_list):
        self.frame_index = 0
        self.last_shot = pg.time.get_ticks()
        self.target = None

  #funçao para dar o upgrade na torre
  def upgrade(self):
    self.upgrade_level += 1
    if self.id == 1:
      self.range = TURRET_DATA_NORMAL[self.upgrade_level - 1].get("range")
      self.cooldown = TURRET_DATA_NORMAL[self.upgrade_level - 1].get("cooldown")
      self.animation_list = self.load_images(self.sprite_sheets[(self.upgrade_level - 1)])
    if self.id == 2:
      self.range = TURRET_DATA_CAMOUFLAGED[self.upgrade_level - 1].get("range")
      self.cooldown = TURRET_DATA_CAMOUFLAGED[self.upgrade_level - 1].get("cooldown")
      self.animation_list = self.load_images(self.sprite_sheets[(self.upgrade_level + 3)])
    if self.id == 3:
      self.range = TURRET_DATA_ARMORED[self.upgrade_level - 1].get("range")
      self.cooldown = TURRET_DATA_ARMORED[self.upgrade_level - 1].get("cooldown")
      self.animation_list = self.load_images(self.sprite_sheets[(self.upgrade_level + 7)])
    #mudança da imagem pós upgrade
    self.original_image = self.animation_list[self.frame_index]

    #upgrade do alcance
    self.range_image = pg.Surface((self.range * 2, self.range * 2))
    self.range_image.fill((0, 0, 0))
    self.range_image.set_colorkey((0, 0, 0))
    pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
    self.range_image.set_alpha(100)
    self.range_rect = self.range_image.get_rect()
    self.range_rect.center = self.rect.center

  #funçao de desenhar na tela
  def draw(self, surface):
    self.image = pg.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)
    surface.blit(self.image, self.rect)
    if self.selected:
      surface.blit(self.range_image, self.range_rect)