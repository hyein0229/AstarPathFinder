import pygame
pygame.font.init()

class Radio:
    def __init__(self, surface, x, y, color, text, ID):
        self.surface = surface
        self.x = x
        self.y = y
        self.text = text
        self.id = ID
        self.color = color
        self.isChecked = False
        self.fontsize = 25
        self.fontstyle = 'calibri'
        self.to = (28, 1)

    def make_button(self):
        if self.isChecked:
            pygame.draw.rect(self.surface, self.color, (self.x, self.y, 12, 12))
            pygame.draw.rect(self.surface, (0,0,0), (self.x, self.y, 12, 12), 1)
            pygame.draw.circle(self.surface, (0,0,0), (self.x + 6, self.y + 6), 4)

        elif not self.isChecked:
            pygame.draw.rect(self.surface, self.color, (self.x, self.y, 12, 12))
            pygame.draw.rect(self.surface, (0,0,0), (self.x, self.y, 12, 12), 1)
        
        self.font = pygame.font.SysFont(self.fontstyle, self.fontsize)
        self.font_surf = self.font.render(self.text, True, (0, 0, 0))
        w, h = self.font.size(self.text)
        self.font_pos = (self.x + self.to[0], self.y + 12/2 - h/2 + self.to[1])
        self.surface.blit(self.font_surf, self.font_pos)

    def update(self, pos):
        if self.x < pos[0] < self.x + 12 and self.y < pos[1] < self.y + 12:
            if not self.isChecked: 
                self.isChecked = True