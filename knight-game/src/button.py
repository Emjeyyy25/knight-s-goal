import pygame

# Helper function to draw rounded rectangles
def draw_rounded_rect(surface, color, rect, corner_radius):
    if rect.width < 2 * corner_radius or rect.height < 2 * corner_radius:
        raise ValueError(f"Both height and width of the rectangle must be > {2 * corner_radius}")

    # Draw the rectangle with rounded corners
    pygame.draw.rect(surface, color, (rect.left + corner_radius, rect.top, rect.width - 2 * corner_radius, rect.height))
    pygame.draw.rect(surface, color, (rect.left, rect.top + corner_radius, rect.width, rect.height - 2 * corner_radius))
    
    # Draw the four corners
    pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.top + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.right - corner_radius, rect.top + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.bottom - corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.right - corner_radius, rect.bottom - corner_radius), corner_radius)

class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color, corner_radius=20):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.corner_radius = corner_radius
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
    
    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)
    
    def checkInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False
    
    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
