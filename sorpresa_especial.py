import os
import math
import random
import pygame
import pygame.gfxdraw
from pygame.locals import *
from pygame import mixer
import glob

# Inicialización de Pygame
pygame.init()
pygame.mixer.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 1280, 720  # Resolución más grande
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Para el Amor de Mi Vida ")

# Configuración de fuentes
try:
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 32)
except:
    font_large = pygame.font.SysFont('Arial', 72, bold=True)
    font_medium = pygame.font.SysFont('Arial', 48)
    font_small = pygame.font.SysFont('Arial', 32)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
PURPLE = (147, 112, 219)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
DARK_PINK = (199, 21, 133)
LIGHT_PINK = (255, 182, 193)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)
HOT_PINK = (255, 105, 180)

# Efecto de partículas mágicas mejorado
class Particle:
    def __init__(self, x, y, particle_type='magic', size=1.0):
        self.x = x
        self.y = y
        self.particle_type = particle_type
        self.size = size * random.uniform(0.8, 1.2)
        
        if particle_type == 'magic':
            self.color = random.choice([
                (255, 255, 200, 200),
                (255, 200, 255, 200),
                (200, 255, 255, 200),
                (255, 255, 255, 200)
            ])
            self.speed = random.uniform(0.5, 2.0)
            self.angle = random.uniform(0, 2 * math.pi)
            self.life = random.uniform(50, 150)
            self.decay = random.uniform(0.95, 0.99)
            self.gravity = 0.05
        elif particle_type == 'firework':
            self.color = (
                random.randint(200, 255),
                random.randint(100, 200),
                random.randint(50, 150),
                random.randint(200, 255)
            )
            self.speed = random.uniform(2, 6)
            self.angle = random.uniform(0, 2 * math.pi)
            self.life = random.uniform(80, 200)
            self.decay = random.uniform(0.97, 0.99)
            self.gravity = 0.1
        elif particle_type == 'heart':
            self.color = (
                255,
                random.randint(100, 200),
                random.randint(100, 200),
                200
            )
            self.speed = random.uniform(0.5, 1.5)
            self.angle = -math.pi/2 + random.uniform(-0.3, 0.3)
            self.life = random.uniform(100, 200)
            self.decay = 0.98
            self.gravity = -0.02
            self.wobble = random.uniform(0, 2 * math.pi)
            self.wobble_speed = random.uniform(0.02, 0.05)

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed + self.gravity
        self.life *= self.decay
        self.speed *= 0.98
        
        if self.particle_type == 'heart':
            self.wobble += self.wobble_speed
            self.x += math.sin(self.wobble) * 0.5
            
        return self.life > 5
    
    def draw(self, surface):
        alpha = min(255, int(self.life * 2.55))
        
        if self.particle_type == 'heart':
            # Dibujar un pequeño corazón
            heart_surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            points = []
            for i in range(20):
                t = i / 20 * math.pi * 2
                r = self.size * (0.8 + 0.2 * math.sin(t) * math.sin(t/2))
                px = self.size + math.cos(t) * r
                py = self.size * 0.8 - math.sin(t) * r * 0.7
                points.append((px, py))
            
            color = (*self.color[:3], alpha)
            pygame.draw.polygon(heart_surf, color, points)
            
            # Añadir brillo al corazón
            highlight = pygame.Surface((int(self.size*0.5), int(self.size*0.5)), pygame.SRCALPHA)
            pygame.draw.circle(highlight, (255, 255, 255, alpha//2), 
                             (int(self.size*0.25), int(self.size*0.25)), 
                             int(self.size*0.25))
            heart_surf.blit(highlight, (int(self.size*0.5), int(self.size*0.2)))
            
            # Rotar ligeramente el corazón
            heart_surf = pygame.transform.rotate(heart_surf, math.degrees(self.wobble*2))
            surface.blit(heart_surf, 
                        (int(self.x - heart_surf.get_width()//2), 
                         int(self.y - heart_surf.get_height()//2)))
        else:
            color = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

# Clase para fuegos artificiales
class Firework:
    def __init__(self, x, y, target_y=None):
        self.x = x
        self.y = y
        self.target_y = target_y if target_y is not None else random.randint(HEIGHT//4, HEIGHT//2)
        self.particles = []
        self.color = random.choice([
            (255, 50, 50, 255),    # Rojo
            (50, 200, 255, 255),   # Azul claro
            (200, 50, 255, 255),   # Púrpura
            (255, 200, 50, 255),   # Amarillo
            (50, 255, 100, 255)    # Verde
        ])
        self.speed = random.uniform(8, 12)
        self.exploded = False
        self.lifetime = 100
        self.size = random.uniform(1, 3)
        self.trail = []

    def update(self):
        if not self.exploded:
            # Add trail effect
            self.trail.append((self.x, self.y))
            if len(self.trail) > 10:  # Limit trail length
                self.trail.pop(0)
                
            self.y -= self.speed
            self.speed *= 0.98  # Slow down as it rises
            
            if self.y <= self.target_y or self.speed < 2:
                self.explode()
                return False
            return True
        else:
            self.particles = [p for p in self.particles if p.update()]
            return len(self.particles) > 0

    def explode(self):
        if self.exploded:
            return
            
        self.exploded = True
        particle_count = random.randint(50, 100)
        
        # Create explosion particles
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append(Particle(
                self.x, 
                self.y, 
                'firework',
                size=random.uniform(1, 4)
            ))
            
        # Add some heart particles
        for _ in range(5):
            self.particles.append(Particle(
                self.x,
                self.y,
                'heart',
                size=random.uniform(6, 12)
            ))

    def draw(self, surface):
        if not self.exploded:
            # Draw trail
            for i, (tx, ty) in enumerate(self.trail):
                alpha = int(200 * (i / len(self.trail)))
                color = (*self.color[:3], alpha)
                pygame.draw.circle(surface, color, (int(tx), int(ty)), 
                                 int(self.size * (i / len(self.trail) * 0.5 + 0.5)))
                
            # Draw firework head
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 
                             int(self.size * 1.5))
        
        # Draw all particles
        for particle in self.particles:
            particle.draw(surface)

# Clase para la niebla de fondo
class Fog:
    def __init__(self, count=10):
        self.particles = []
        for _ in range(count):
            self.add_particle()
    
    def add_particle(self):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.uniform(100, 300)
        speed = random.uniform(0.1, 0.3)
        alpha = random.uniform(10, 30)
        self.particles.append({
            'x': x,
            'y': y,
            'size': size,
            'speed': speed,
            'alpha': alpha
        })
    
    def update(self):
        for p in self.particles:
            p['y'] -= p['speed']
            if p['y'] < -p['size']:
                p['y'] = HEIGHT + p['size']
                p['x'] = random.randint(0, WIDTH)
    
    def draw(self, surface):
        for p in self.particles:
            s = pygame.Surface((int(p['size']*2), int(p['size']*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, p['alpha']), 
                             (int(p['size']), int(p['size'])), 
                             int(p['size']))
            surface.blit(s, (int(p['x'] - p['size']), int(p['y'] - p['size'])))

# Clase para corazones flotantes
class FloatingHeart:
    def __init__(self):
        self.reset()
        self.particles = []
        
    def reset(self):
        self.x = random.randint(50, WIDTH-50)
        self.y = HEIGHT + 50
        self.size = random.uniform(15, 30)
        self.speed = random.uniform(0.5, 1.5)
        self.wobble = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(0.02, 0.05)
        self.color = (
            random.randint(200, 255),
            random.randint(100, 200),
            random.randint(100, 200)
        )
        self.alpha = 255
        self.life = random.uniform(200, 500)
        self.decay = random.uniform(0.98, 0.995)
        
    def update(self):
        self.y -= self.speed
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.5
        self.life -= 1
        
        # Añadir partículas de estela
        if random.random() < 0.3:
            self.particles.append(Particle(
                self.x + random.uniform(-5, 5),
                self.y + random.uniform(-5, 5),
                'magic'
            ))
        
        # Actualizar partículas
        self.particles = [p for p in self.particles if p.update()]
        
        # Reiniciar si sale de la pantalla o se acaba su vida
        if self.y < -50 or self.life <= 0:
            self.reset()
            return False
        return True
    
    def draw(self, surface):
        # Dibujar partículas
        for p in self.particles:
            p.draw(surface)
        
        # Dibujar corazón
        heart_surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        points = []
        for i in range(20):
            t = i / 20 * math.pi * 2
            r = self.size * (0.8 + 0.2 * math.sin(t) * math.sin(t/2))
            px = self.size + math.cos(t) * r
            py = self.size * 0.8 - math.sin(t) * r * 0.7
            points.append((px, py))
        
        alpha = min(255, int(self.life * 0.5))
        color = (*self.color, alpha)
        pygame.draw.polygon(heart_surf, color, points)
        
        # Añadir brillo al corazón
        highlight = pygame.Surface((int(self.size*0.5), int(self.size*0.5)), pygame.SRCALPHA)
        pygame.draw.circle(highlight, (255, 255, 255, alpha//2), 
                         (int(self.size*0.25), int(self.size*0.25)), 
                         int(self.size*0.25))
        heart_surf.blit(highlight, (int(self.size*0.5), int(self.size*0.2)))
        
        # Rotar ligeramente el corazón
        heart_surf = pygame.transform.rotate(heart_surf, math.degrees(self.wobble*2))
        surface.blit(heart_surf, 
                    (int(self.x - heart_surf.get_width()//2), 
                     int(self.y - heart_surf.get_height()//2)))

# Clase para las flores mejoradas
class Flower:
    def __init__(self, x, y, size=1.0):
        self.x = x
        self.y = y
        self.size = size * random.uniform(0.8, 1.2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.petal_wobble = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(0.02, 0.05)
        self.petal_count = random.choice([5, 6, 7, 8, 9, 10])  # More petal variety
        self.petal_length = random.uniform(30, 50) * self.size  # Slightly larger petals
        self.time_offset = random.uniform(0, 10)
        
        # Enhanced color palettes with more natural gradients
        self.petal_palettes = [
            # Romantic pinks and reds
            [
                [(255, 220, 230, 230), (255, 150, 180, 240)],  # Soft pink to rose
                [(255, 200, 220, 220), (255, 100, 150, 240)],  # Light pink to deep rose
                [(255, 180, 200, 210), (220, 50, 100, 230)]    # Rose to deep red
            ],
            # Vibrant reds and purples
            [
                [(255, 180, 200, 220), (220, 0, 80, 240)],     # Pink to deep red
                [(240, 100, 200, 220), (180, 0, 100, 240)],    # Pink-purple to purple
                [(255, 150, 180, 230), (180, 50, 150, 250)]    # Rose to purple
            ],
            # Warm oranges and yellows
            [
                [(255, 240, 200, 230), (255, 200, 100, 250)],  # Cream to peach
                [(255, 220, 180, 220), (255, 160, 0, 240)],    # Light orange to orange
                [(255, 200, 150, 220), (255, 120, 0, 240)]     # Peach to deep orange
            ],
            # Cool purples and blues
            [
                [(230, 200, 255, 220), (190, 150, 250, 240)],  # Lavender to purple
                [(210, 180, 255, 220), (160, 120, 220, 240)],  # Light purple to deep purple
                [(200, 200, 255, 220), (140, 140, 220, 240)]   # Periwinkle to blue
            ],
            # Romantic pastels
            [
                [(255, 230, 240, 230), (255, 200, 220, 250)],  # Blush pink
                [(240, 230, 255, 230), (220, 200, 255, 250)],  # Lavender mist
                [(230, 255, 240, 230), (200, 255, 220, 250)]   # Mint cream
            ]
        ]
        
        # Select a random color palette
        palette_choice = random.choice(self.petal_palettes)
        self.petal_colors = random.choice(palette_choice)
        
        # Enhanced flower center with more detail
        self.center_size = random.uniform(12, 20) * self.size
        self.center_color = (
            random.randint(200, 255),  # Yellow/white center
            random.randint(150, 220),
            random.randint(0, 100)
        )
        
        # More realistic leaves with better color variation
        self.leaf_size = random.uniform(30, 45) * self.size
        self.leaf_angle = random.uniform(0, math.pi * 2)
        self.leaf_color = (
            random.randint(40, 80),
            random.randint(130, 200),
            random.randint(40, 100)
        )
        
        # Animation timing and state
        self.time = random.uniform(0, 10)
        self.particles = []
        self.animation_phase = random.uniform(0, 2 * math.pi)
        self.animation_speed = random.uniform(0.008, 0.015)  # Slower, more natural movement
        
        # Petal layer properties
        self.petal_layers = 2  # Number of petal layers for depth
        self.layer_offsets = [i * (math.pi / (self.petal_count * 2)) for i in range(self.petal_layers)]
        self.layer_scales = [1.0 - i * 0.15 for i in range(self.petal_layers)]
    
    def update(self):
        # Smoother, more organic animation
        self.time += 0.01
        self.animation_phase += self.animation_speed
        
        # Gentle swaying motion
        self.angle = math.sin(self.time * 0.25) * 0.15 * math.sin(self.animation_phase * 0.4)
        
        # More natural petal movement with multiple frequencies
        self.petal_wobble = (
            math.sin(self.time * 0.5 + self.time_offset) * 0.2 +
            math.sin(self.animation_phase * 1.2) * 0.15 +
            math.sin(self.time * 1.5) * 0.1
        )
        
        # Update particles with better timing
        self.particles = [p for p in self.particles if p.update()]
        
        # Add new particles with better distribution
        if random.random() < 0.1:  # Slightly less frequent but more particles
            for _ in range(random.randint(1, 3)):
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0, self.center_size * 0.4)
                self.particles.append(Particle(
                    self.x + math.cos(angle) * dist,
                    self.y + math.sin(angle) * dist,
                    'magic',
                    size=random.uniform(1, 4) * self.size * 0.8
                ))
    
    def draw_petal(self, surface, angle, length, layer=0):
        # Create petal surface with better anti-aliasing
        petal_width = length * (0.5 + 0.25 * math.sin(angle * 2 + self.animation_phase))
        petal_surf = pygame.Surface((int(length * 2.5), int(length * 1.4)), pygame.SRCALPHA)
        
        # Helper function to clamp color values
        def clamp_color(c):
            return max(0, min(255, int(c)))
        
        # Draw petal with improved gradient and shape
        for i in range(int(length)):
            t = i / length
            # More natural curve for petal width
            width_curve = (
                math.sin(t * math.pi) * 0.8 + 
                0.2 * math.sin(t * 3 * math.pi + self.animation_phase) *
                (1.0 + 0.1 * math.sin(angle * 3 + self.time * 2))
            )
            width = int(petal_width * width_curve)
            
            if width > 0:
                # More vibrant color variation
                color_variation = 0.9 + 0.2 * math.sin(t * 8 + self.animation_phase * 2)
                r = clamp_color(self.petal_colors[0][0] * (1-t) * color_variation + 
                              self.petal_colors[1][0] * t * color_variation)
                g = clamp_color(self.petal_colors[0][1] * (1-t) * color_variation + 
                              self.petal_colors[1][1] * t * color_variation)
                b = clamp_color(self.petal_colors[0][2] * (1-t) * color_variation + 
                              self.petal_colors[1][2] * t * color_variation)
                a = clamp_color(self.petal_colors[0][3] * (1-t) + 
                              self.petal_colors[1][3] * t)
                
                # Draw with subtle edge darkening
                edge_darken = 0.7 + 0.3 * math.sin(t * math.pi)
                r = clamp_color(r * edge_darken)
                g = clamp_color(g * edge_darken)
                b = clamp_color(b * edge_darken)
                
                # Ensure alpha is valid
                a = clamp_color(a)
                
                # Draw petal segment with anti-aliasing
                pygame.draw.line(petal_surf, (r, g, b, a), 
                               (int(length - width//2), i), 
                               (int(length + width//2), i), 
                               min(5, max(1, int(width//6 + 1))))
        
        # Add petal highlights
        highlight = pygame.Surface((int(length * 0.7), int(length * 0.7)), pygame.SRCALPHA)
        highlight_center = (highlight.get_width()//2, highlight.get_height()//2)
        for i in range(highlight_center[0], 0, -1):
            alpha = int(120 * (i / highlight_center[0]) * 0.8)
            pygame.draw.circle(highlight, (255, 255, 255, alpha), 
                             highlight_center, i)
        
        # Apply highlight with soft light blending
        petal_surf.blit(highlight, 
                       (int(length * 0.6), int(length * 0.1)),
                       special_flags=pygame.BLEND_RGBA_ADD)
        
        # Add subtle texture to petals
        for _ in range(int(length * 0.5)):
            x = random.randint(0, petal_surf.get_width()-1)
            y = random.randint(0, petal_surf.get_height()-1)
            if random.random() < 0.3:  # Sparse texture dots
                brightness = random.randint(220, 240)
                alpha = random.randint(10, 30)
                petal_surf.set_at((x, y), (brightness, brightness, brightness, alpha))
        
        # Rotate petal with natural movement
        rotation = math.degrees(angle + self.petal_wobble * 
                               (0.6 + 0.4 * math.sin(angle * 2 + self.animation_phase)))
        rotated_petal = pygame.transform.rotate(petal_surf, rotation)
        
        # Draw petal shadow for depth
        shadow = rotated_petal.copy()
        shadow.fill((0, 0, 0, 40), None, pygame.BLEND_RGBA_MULT)
        surface.blit(shadow, 
                    (int(self.x - rotated_petal.get_width()//2 + 2), 
                     int(self.y - rotated_petal.get_height()//2 + 2)),
                    special_flags=pygame.BLEND_RGBA_ADD)
        
        # Draw the main petal
        surface.blit(rotated_petal, 
                    (int(self.x - rotated_petal.get_width()//2), 
                     int(self.y - rotated_petal.get_height()//2)),
                    special_flags=pygame.BLEND_RGBA_ADD)
    
    def draw_center(self, surface):
        # Draw center with more detail and texture
        for i in range(int(self.center_size * 1.5), 0, -1):
            # Radial gradient
            t = i / self.center_size
            # Ensure t is within valid range [0, 1] to prevent complex numbers
            t = max(0.0, min(1.0, t))
            
            r = int(self.center_color[0] * (0.7 + 0.3 * t))
            g = int(self.center_color[1] * (0.6 + 0.4 * t))
            b = int(self.center_color[2] * (0.4 + 0.6 * t))
            alpha = int(255 * (0.2 + 0.8 * (1.0 - t)**1.3))
            
            # Draw center circle with safety checks
            if alpha > 0 and i > 0:
                pygame.draw.circle(
                    surface, 
                    (r, g, b, alpha),
                    (int(self.x), int(self.y)), 
                    int(i)
                )
    
    def draw_leaf(self, surface, angle, distance):
        # Create leaf surface with better anti-aliasing
        leaf_surf = pygame.Surface((int(self.leaf_size * 2.8), int(self.leaf_size * 2.0)), pygame.SRCALPHA)
        
        # Draw more realistic leaf shape
        points = []
        for i in range(21):
            t = i / 20
            # More organic leaf curve
            if t < 0.5:
                curve = 0.7 + 0.3 * math.sin(t * math.pi)
            else:
                curve = 0.7 + 0.3 * math.sin((1-t) * math.pi)
                
            # Add subtle waviness to leaf edge
            wave = math.sin(t * math.pi * 3 + self.animation_phase) * 0.1
            r = self.leaf_size * (curve + wave)
            
            # Calculate point with natural curve
            px = self.leaf_size + math.cos(t * math.pi * 0.9 - math.pi/2) * r
            py = self.leaf_size * 0.9 + math.sin(t * math.pi * 0.9 - math.pi/2) * r * 0.6
            points.append((px, py))
        
        # Fill leaf with gradient
        for i, (px, py) in enumerate(points):
            if i < len(points) - 1:
                next_px, next_py = points[i + 1]
                # More natural leaf color variation
                color_factor = 0.8 + 0.4 * math.sin(i/len(points) * math.pi)
                leaf_color = (
                    min(255, int(self.leaf_color[0] * color_factor)),
                    min(255, int(self.leaf_color[1] * (1.1 - 0.2 * color_factor))),
                    min(255, int(self.leaf_color[2] * 0.8 * color_factor)),
                    200
                )
                # Draw leaf segment with anti-aliasing
                pygame.draw.polygon(leaf_surf, leaf_color, 
                                  [(self.leaf_size, self.leaf_size * 0.9), 
                                   (px, py), (next_px, next_py)])
        
        # Draw more detailed veins
        vein_color = (0, 40, 0, 100)
        for i in range(1, 5):  # More main veins
            t = i / 5
            idx = int(t * (len(points)-1))
            if 0 < idx < len(points)-1:
                vein_start = (self.leaf_size, self.leaf_size * 0.9)
                vein_end = points[idx]
                
                # Main vein with gradient
                for j in range(3, 0, -1):
                    alpha = 80 - j * 20
                    pygame.draw.line(leaf_surf, (*vein_color[:3], alpha), 
                                   vein_start, vein_end, j)
                
                # Side veins
                for side in [-1, 1]:
                    vein_dir = (vein_end[0] - vein_start[0], 
                               vein_end[1] - vein_start[1])
                    # Perpendicular vector
                    perp = (-vein_dir[1] * 0.4, vein_dir[0] * 0.4)
                    vein_mid = (
                        vein_start[0] + (vein_end[0] - vein_start[0]) * 0.5,
                        vein_start[1] + (vein_end[1] - vein_start[1]) * 0.5
                    )
                    vein_tip = (
                        vein_mid[0] + perp[0] * side,
                        vein_mid[1] + perp[1] * side
                    )
                    # Draw side vein with slight curve
                    control = (
                        vein_mid[0] + perp[0] * side * 0.5,
                        vein_mid[1] + perp[1] * side * 0.5 - 5
                    )
                    # Draw curved vein
                    points = []
                    for t in range(0, 11):
                        t = t / 10
                        # Quadratic bezier curve
                        x = (1-t)**2 * vein_mid[0] + 2*(1-t)*t*control[0] + t**2 * vein_tip[0]
                        y = (1-t)**2 * vein_mid[1] + 2*(1-t)*t*control[1] + t**2 * vein_tip[1]
                        points.append((x, y))
                    
                    if len(points) > 1:
                        pygame.draw.lines(leaf_surf, vein_color, False, points, 1)
        
        # Draw leaf edge with subtle highlight
        if len(points) > 1:
            pygame.draw.lines(leaf_surf, (0, 50, 0, 180), True, points, 2)
            # Inner highlight
            highlight_points = []
            for i in range(1, len(points)-1):
                x = points[i][0] + (points[i][0] - self.leaf_size) * 0.05
                y = points[i][1] + (points[i][1] - self.leaf_size * 0.9) * 0.05
                highlight_points.append((x, y))
            
            if len(highlight_points) > 1:
                pygame.draw.lines(leaf_surf, (150, 180, 100, 80), False, highlight_points, 1)
        
        # Rotate and position leaf with natural movement
        rotation = math.degrees(angle + math.pi/2 + 
                               math.sin(self.time * 0.4 + angle) * 0.15)
        rotated_leaf = pygame.transform.rotate(leaf_surf, rotation)
        
        # Position with gentle movement
        move_x = math.sin(self.time * 0.3 + angle) * 3
        move_y = math.cos(self.time * 0.35 + angle + 1.5) * 2
        
        leaf_x = self.x + math.cos(angle) * distance + move_x
        leaf_y = self.y + math.sin(angle) * distance + move_y
        
        # Draw leaf shadow
        shadow = rotated_leaf.copy()
        shadow.fill((0, 0, 0, 50), None, pygame.BLEND_RGBA_MULT)
        surface.blit(shadow, 
                    (int(leaf_x - rotated_leaf.get_width()//2 + 3), 
                     int(leaf_y - rotated_leaf.get_height()//2 + 3)),
                    special_flags=pygame.BLEND_RGBA_ADD)
        
        # Draw the leaf
        leaf_rect = rotated_leaf.get_rect(center=(int(leaf_x), int(leaf_y)))
        surface.blit(rotated_leaf, leaf_rect)
    
    def draw_stem(self, surface):
        # Draw stem with more natural curve and texture
        stem_width = max(2, int(5 * self.size))
        stem_length = self.petal_length * (1.8 + 0.3 * math.sin(self.time * 0.3))
        
        # Control points for bezier curve
        start_x, start_y = self.x, self.y
        end_x, end_y = self.x, self.y + stem_length
        
        # Control point with natural movement
        control_x = self.x + math.sin(self.time * 0.25) * 25 * self.size
        control_y = (start_y + end_y) / 2 + math.sin(self.time * 0.35) * 15
        
        # Draw stem with gradient and texture
        for i in range(stem_width, 0, -1):
            alpha = int(240 * (i / stem_width))
            # More natural green gradient
            base_green = 80 + i * 10
            color = (
                max(0, min(50, 30 - i * 2)),
                min(255, base_green + random.randint(-5, 5)),
                max(0, min(50, 30 - i * 2)),
                alpha
            )
            
            # Draw stem curve with bezier
            points = []
            for t in range(0, 16):
                t = t / 15
                # Quadratic bezier curve
                x = (1-t)**2 * start_x + 2*(1-t)*t*control_x + t**2 * end_x
                y = (1-t)**2 * start_y + 2*(1-t)*t*control_y + t**2 * end_y
                points.append((x, y))
            
            # Draw stem with anti-aliasing
            if len(points) > 1:
                # Main stem
                pygame.draw.lines(surface, color, False, points, i)
                
                # Add subtle texture
                if i == stem_width:  # Only on top layer
                    for j in range(0, len(points)-1, 2):
                        if random.random() < 0.3:  # Sparse texture
                            px, py = points[j]
                            length = math.sqrt((points[j+1][0]-px)**2 + (points[j+1][1]-py)**2)
                            if length > 0:
                                dx = (points[j+1][0] - px) / length
                                dy = (points[j+1][1] - py) / length
                                # Draw small perpendicular lines for texture
                                perp_x = -dy * 2
                                perp_y = dx * 2
                                tx = px + dx * random.random() * length
                                ty = py + dy * random.random() * length
                                pygame.draw.line(
                                    surface,
                                    (255, 255, 255, 30),
                                    (int(tx - perp_x), int(ty - perp_y)),
                                    (int(tx + perp_x), int(ty + perp_y)),
                                    1
                                )
                
                # Add highlight on top
                if i == stem_width:
                    highlight_color = (
                        min(255, color[0] + 60),
                        min(255, color[1] + 40),
                        min(255, color[2] + 20),
                        alpha//2
                    )
                    highlight_points = [(p[0]-0.7, p[1]-0.7) for p in points]
                    pygame.draw.lines(surface, highlight_color, False, highlight_points, max(1, i//2))
    
    def draw(self, surface):
        # Draw particles first (behind)
        for particle in self.particles:
            particle.draw(surface)
        
        # Draw stem and leaves first (behind flower)
        self.draw_stem(surface)
        
        # Draw leaves with natural positioning
        leaf_angles = [
            self.leaf_angle,
            self.leaf_angle + math.pi * 0.7,
            self.leaf_angle + math.pi * 1.4,
            self.leaf_angle + math.pi * 2.1
        ]
        leaf_distances = [
            self.petal_length * 0.6,
            self.petal_length * 0.8,
            self.petal_length * 0.5,
            self.petal_length * 0.9
        ]
        
        for angle, dist in zip(leaf_angles, leaf_distances):
            self.draw_leaf(surface, angle, dist)
        
        # Draw multiple layers of petals for depth
        for layer in range(self.petal_layers):
            layer_scale = self.layer_scales[layer]
            layer_offset = self.layer_offsets[layer]
            
            for i in range(self.petal_count):
                # Stagger petals for more natural look
                angle = (self.angle + 
                        (2 * math.pi / self.petal_count) * i + 
                        layer_offset + 
                        math.sin(self.time * 0.4 + i * 0.5) * 0.15)
                
                # Vary petal size slightly for organic feel
                size_variation = 0.95 + 0.1 * math.sin(self.time * 0.6 + i * 0.7)
                self.draw_petal(
                    surface, 
                    angle, 
                    self.petal_length * layer_scale * size_variation,
                    layer
                )
        
        # Draw flower center last (on top)
        self.draw_center(surface)

# Clase para el slideshow de fotos
class PhotoSlideshow:
    def __init__(self):
        self.photos = []
        self.photo_files = []
        self.current_photo = 0
        self.alpha = 0
        self.fade_speed = 5
        self.photo_rect = pygame.Rect(WIDTH//4, HEIGHT//4, WIDTH//2, HEIGHT//2)
        self.showing_high = True
        self.load_photos()
        self.last_change = pygame.time.get_ticks()
        self.photo_delay = 4000  # 4 segundos por foto
        self.frame_surf = pygame.Surface((self.photo_rect.width + 20, self.photo_rect.height + 20), pygame.SRCALPHA)
        self.frame_surf.fill((255, 255, 255, 30))
        pygame.draw.rect(self.frame_surf, (255, 255, 255, 100), self.frame_surf.get_rect(), 5, border_radius=10)
    
    def load_photos(self):
        # Cargar todas las imágenes JPG/JPEG/PNG de la carpeta
        image_extensions = ('.jpg', '.jpeg', '.png')
        for filename in os.listdir('.'):
            if filename.lower().endswith(image_extensions) and not filename.lower().startswith('fondo'):
                self.photo_files.append(filename)
        
        # Ordenar los archivos numéricamente
        def extract_number(filename):
            import re
            numbers = re.findall(r'\d+', filename)
            return int(numbers[0]) if numbers else 0
        
        if self.photo_files:
            # Ordenar por número
            self.photo_files.sort(key=extract_number)
            
            # Cargar la primera imagen
            self._load_next_photo()
        else:
            # Crear una imagen de relleno si no hay fotos
            self._create_placeholder()
    
    def _load_next_photo(self):
        if not self.photo_files:
            self._create_placeholder()
            return
        
        # Alternar entre números altos y bajos
        if self.showing_high:
            # Tomar de los números más altos
            idx = len(self.photo_files) - 1 - (self.current_photo // 2) % len(self.photo_files)
        else:
            # Tomar de los números más bajos
            idx = (self.current_photo // 2) % len(self.photo_files)
        
        # Cambiar el orden para la siguiente vez
        self.showing_high = not self.showing_high
        self.current_photo += 1
        
        try:
            # Cargar y escalar la imagen
            image = pygame.image.load(self.photo_files[idx]).convert_alpha()
            self.photos = [self.scale_image(image, self.photo_rect.width - 20, self.photo_rect.height - 20)]
        except:
            print(f"No se pudo cargar la imagen: {self.photo_files[idx]}")
            self._create_placeholder()
    
    def _create_placeholder(self):
        # Crear una imagen de relleno
        surf = pygame.Surface((self.photo_rect.width - 20, self.photo_rect.height - 20), pygame.SRCALPHA)
        
        # Mensaje centrado
        text1 = font_medium.render("Coloca fotos en la carpeta", True, WHITE)
        text2 = font_small.render("(JPG, JPEG o PNG)", True, WHITE)
        
        text1_rect = text1.get_rect(center=(surf.get_width()//2, surf.get_height()//2 - 20))
        text2_rect = text2.get_rect(center=(surf.get_width()//2, surf.get_height()//2 + 20))
        
        surf.blit(text1, text1_rect)
        surf.blit(text2, text2_rect)
        
        self.photos = [surf]
    
    def scale_image(self, image, max_width, max_height):
        # Escalar la imagen manteniendo la relación de aspecto
        ratio = min(max_width / image.get_width(), max_height / image.get_height())
        new_width = int(image.get_width() * ratio)
        new_height = int(image.get_height() * ratio)
        return pygame.transform.smoothscale(image, (new_width, new_height))
    
    def update(self):
        # Actualizar transición de fotos
        now = pygame.time.get_ticks()
        if now - self.last_change > self.photo_delay:
            self.alpha = max(0, self.alpha - self.fade_speed)
            if self.alpha <= 0:
                self._load_next_photo()
                self.last_change = now
                self.alpha = 0
        else:
            self.alpha = min(255, self.alpha + self.fade_speed)
    
    def draw(self, surface):
        if not self.photos:
            return
            
        # Dibujar marco
        frame_rect = pygame.Rect(
            self.photo_rect.x - 10,
            self.photo_rect.y - 10,
            self.photo_rect.width + 20,
            self.photo_rect.height + 20
        )
        
        # Dibujar sombra
        shadow = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 50))
        surface.blit(shadow, (frame_rect.x + 5, frame_rect.y + 5))
        
        # Dibujar marco
        surface.blit(self.frame_surf, frame_rect)
        
        # Dibujar la foto actual
        current_surf = self.photos[0].copy()
        current_surf.set_alpha(self.alpha)
        
        # Centrar la foto en el marco
        x = self.photo_rect.x + (self.photo_rect.width - current_surf.get_width()) // 2
        y = self.photo_rect.y + (self.photo_rect.height - current_surf.get_height()) // 2
        
        surface.blit(current_surf, (x, y))

# Función para cargar y mejorar imágenes
def load_enhanced_image(filename, scale=1.0, alpha=255):
    try:
        # Cargar la imagen
        image = pygame.image.load(filename).convert_alpha()
        
        # Calcular el factor de escala para que la imagen ocupe más espacio
        # Aumentar el tamaño para que ocupe más pantalla
        screen_ratio = min(WIDTH / image.get_width(), HEIGHT / image.get_height())
        scale = min(scale * 1.5, screen_ratio * 0.9)  # Usar hasta el 90% del ancho o alto de la pantalla
        
        # Escalar la imagen
        new_width = int(image.get_width() * scale)
        new_height = int(image.get_height() * scale)
        image = pygame.transform.scale(image, (new_width, new_height))
        
        # Crear una superficie con alfa por píxel
        enhanced = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        
        # Mejorar la imagen (aumentar brillo y contraste)
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                color = image.get_at((x, y))
                if color[3] > 0:  # Solo procesar píxeles no transparentes
                    # Aumentar brillo y contraste
                    r = min(255, int(color[0] * 1.3))  # Aumentar más el brillo
                    g = min(255, int(color[1] * 1.3))
                    b = min(255, int(color[2] * 1.3))
                    a = min(255, int(color[3] * (alpha / 255.0)))
                    enhanced.set_at((x, y), (r, g, b, a))
        
        return enhanced
    except Exception as e:
        print(f"Error al cargar la imagen {filename}: {e}")
        return None

class Game:
    def __init__(self):
        # ... código existente ...
        
        # Cargar y mejorar imágenes
        self.images = []
        self.current_image_index = 0
        self.image_change_time = 0
        self.image_display_time = 5000  # 5 segundos por imagen
        self.load_images()
        
    def load_images(self):
        # Lista de nombres de archivos de imágenes
        image_extensions = ['.jpg', '.jpeg', '.png']
        image_files = []
        
        # Buscar archivos de imagen en el directorio
        for ext in image_extensions:
            image_files.extend(glob.glob(f"*{ext}"))
        
        # Cargar y mejorar cada imagen
        for img_file in image_files:
            try:
                # Cargar imagen con escala mejorada
                img = load_enhanced_image(img_file, scale=1.0, alpha=255)
                if img:
                    self.images.append(img)
                    print(f"Imagen cargada: {img_file} - Tamaño: {img.get_width()}x{img.get_height()}")
            except Exception as e:
                print(f"Error al procesar {img_file}: {e}")
        
        print(f"Total de imágenes cargadas: {len(self.images)}")
    
    def update(self):
        # ... código existente ...
        
        # Cambiar de imagen después del tiempo establecido
        current_time = pygame.time.get_ticks()
        if len(self.images) > 1 and current_time - self.image_change_time > self.image_display_time:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.image_change_time = current_time
    
    def draw(self):
        # ... código de dibujo existente ...
        
        # Dibujar la imagen actual
        if self.images:
            img = self.images[self.current_image_index]
            
            # Calcular posición para centrar la imagen
            img_x = (WIDTH - img.get_width()) // 2
            img_y = (HEIGHT - img.get_height()) // 2
            
            # Dibujar fondo oscuro semitransparente
            bg_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))  # Fondo oscuro semitransparente
            self.screen.blit(bg_surface, (0, 0))
            
            # Dibujar un marco blanco sutil
            border_size = 10
            border_rect = pygame.Rect(
                img_x - border_size,
                img_y - border_size,
                img.get_width() + border_size * 2,
                img.get_height() + border_size * 2
            )
            pygame.draw.rect(self.screen, (255, 255, 255, 100), border_rect, 2, border_radius=5)
            
            # Dibujar un brillo sutil alrededor de la imagen
            glow_surf = pygame.Surface(
                (img.get_width() + 20, img.get_height() + 20),
                pygame.SRCALPHA
            )
            pygame.draw.rect(
                glow_surf,
                (255, 255, 255, 30),
                (0, 0, img.get_width() + 20, img.get_height() + 20),
                border_radius=10
            )
            self.screen.blit(glow_surf, (img_x - 10, img_y - 10))
            
            # Dibujar la imagen
            self.screen.blit(img, (img_x, img_y))
            
            # Mostrar número de imagen actual
            if len(self.images) > 1:
                font = pygame.font.SysFont('Arial', 24)
                text = f"{self.current_image_index + 1}/{len(self.images)}"
                text_surf = font.render(text, True, (255, 255, 255, 200))
                text_rect = text_surf.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
                
                # Fondo para el texto
                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0, 150),
                    (text_rect.x - 10, text_rect.y - 5,
                     text_rect.width + 20, text_rect.height + 10),
                    border_radius=5
                )
                
                self.screen.blit(text_surf, text_rect)
        
        # ... resto del código de dibujo ...

# Función principal
def main():
    clock = pygame.time.Clock()
    running = True
    
    # Crear superficie para efectos de desenfoque
    blur_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Inicializar el slideshow de fotos
    slideshow = PhotoSlideshow()
    
    # Inicializar flores
    flowers_left = [
        Flower(random.randint(50, WIDTH//4), 
              random.randint(100, HEIGHT-200),  
              random.uniform(0.9, 1.3))  
        for _ in range(4)  
    ]
    
    flowers_right = [
        Flower(random.randint(WIDTH*3//4, WIDTH-50), 
              random.randint(100, HEIGHT-200),  
              random.uniform(0.9, 1.3))  
        for _ in range(4)  
    ]
    
    # Inicializar efectos
    fog = Fog(15)  
    floating_hearts = [FloatingHeart() for _ in range(5)]  
    fireworks = []  
    last_firework = 0
    firework_delay = 5000  
    
    # Mensajes románticos mejorados
    messages = [
        "Eres el amor de mi vida ",
        "Cada día a tu lado es un regalo precioso",
        "Eres mi razón de ser y mi mayor inspiración",
        "Te amo más que a nada en este mundo ",
        "Eres mi sueño hecho realidad ",
        "Contigo cada momento es especial y único",
        "Tu sonrisa ilumina mis días más oscuros",
        "Eres perfecta tal como eres ",
        "Mi corazón late al ritmo de tu nombre",
        "Eres mi persona favorita en todo el universo ",
        "Cada día te quiero un poco más",
        "Eres la estrella que ilumina mi camino",
        "Mi amor por ti crece con cada latido",
        "Eres la mejor decisión de mi vida",
        "Contigo el tiempo vuela y los momentos perduran"
    ]
    current_message = random.choice(messages)
    message_timer = 0
    message_delay = 300  
    
    # Cargar música de fondo
    music_files = ['rosas.mp3', 'rosas.wav', 'musica.mp3', 'cancion.mp3']
    music_loaded = False
    
    for music_file in music_files:
        try:
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(-1)  
                music_loaded = True
                print(f"Música cargada: {music_file}")
                break
        except Exception as e:
            print(f"Error al cargar {music_file}: {e}")
    
    if not music_loaded:
        print("No se pudo cargar ningún archivo de música")
    
    # Bucle principal
    while running:
        current_time = pygame.time.get_ticks()
        
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                # Crear un pequeño efecto al hacer clic
                if event.button == 1:  
                    for _ in range(10):
                        floating_hearts.append(FloatingHeart())
        
        # Actualizar efectos
        fog.update()
        
        # Actualizar corazones flotantes
        floating_hearts = [h for h in floating_hearts if h.update()]
        
        # Añadir nuevos corazones ocasionalmente
        if random.random() < 0.02 and len(floating_hearts) < 10:
            floating_hearts.append(FloatingHeart())
        
        # Actualizar fuegos artificiales
        fireworks = [fw for fw in fireworks if fw.update()]
        
        # Añadir nuevos fuegos artificiales
        if current_time - last_firework > firework_delay:
            fireworks.append(Firework(
                random.randint(WIDTH//4, 3*WIDTH//4),
                HEIGHT + 20
            ))
            last_firework = current_time
            firework_delay = random.randint(3000, 8000)  
        
        # Actualizar slideshow
        slideshow.update()
        
        # Actualizar flores
        for flower in flowers_left + flowers_right:
            flower.update()
        
        # Actualizar mensaje
        message_timer += 1
        if message_timer >= message_delay:
            current_message = random.choice([m for m in messages if m != current_message] or messages)
            message_timer = 0
        
        # Dibujar
        # Fondo con gradiente dinámico (cambia con el tiempo)
        time_factor = math.sin(pygame.time.get_ticks() * 0.0005) * 0.5 + 0.5
        for y in range(HEIGHT):
            # Interpolar entre dos esquemas de color
            r1, g1, b1 = 30, 20, 50  
            r2, g2, b2 = 100, 150, 255  
            
            r = r1 + (r2 - r1) * time_factor
            g = g1 + (g2 - g1) * time_factor
            b = b1 + (b2 - b1) * time_factor
            
            # Añadir gradiente vertical
            r = min(r + y//4, 255)
            g = min(g + y//6, 255)
            b = min(b + y//3, 255)
            
            pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (WIDTH, y))
        
        # Dibujar niebla
        fog.draw(screen)
        
        # Dibujar estrellas (efecto brillante)
        if random.random() < 0.1:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT//2)
            size = random.uniform(0.5, 2)
            alpha = random.randint(100, 200)
            pygame.draw.circle(screen, (255, 255, 255, alpha), (x, y), size)
        
        # Dibujar flores
        for flower in flowers_left + flowers_right:
            flower.draw(screen)
        
        # Dibujar corazones flotantes
        for heart in floating_hearts:
            heart.draw(screen)
        
        # Dibujar fuegos artificiales
        for firework in fireworks:
            firework.draw(screen)
        
        # Dibujar slideshow con efecto de vidrio
        slideshow.draw(screen)
        
        # Dibujar mensaje con sombra y efecto de gradiente
        text = font_medium.render(current_message, True, WHITE)
        text_shadow = font_medium.render(current_message, True, (0, 0, 0, 150))
        text_rect = text.get_rect(center=(WIDTH//2, 60))
        
        # Crear superficie para el fondo del texto con gradiente
        text_bg = pygame.Surface((text_rect.width + 40, text_rect.height + 20), pygame.SRCALPHA)
        
        # Dibujar fondo con gradiente y borde
        for i in range(text_bg.get_height()):
            alpha = int(150 * (1 - i/text_bg.get_height())**2)
            pygame.draw.line(text_bg, (200, 100, 200, alpha), 
                           (0, i), (text_bg.get_width(), i))
        
        # Añadir borde sutil
        pygame.draw.rect(text_bg, (255, 255, 255, 50), 
                        text_bg.get_rect(), 2, border_radius=10)
        
        # Dibujar fondo del texto en la pantalla
        screen.blit(text_bg, (text_rect.x - 20, text_rect.y - 10))
        
        # Sombra del texto
        screen.blit(text_shadow, (text_rect.x+3, text_rect.y+3))
        
        # Texto principal con gradiente
        text_surface = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
        for i in range(text_rect.height):
            alpha = int(255 * (0.7 + 0.3 * math.sin(i/5 + pygame.time.get_ticks()*0.005)))
            color = (255, 255 - i//2, 255 - i, alpha)
            pygame.draw.line(text_surface, color, (0, i), (text_rect.width, i))
        
        # Aplicar máscara de texto
        text_mask = pygame.mask.from_surface(text)
        text_surface.blit(text, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(text_surface, text_rect)
        
        # Efecto de brillo en el texto
        if pygame.time.get_ticks() % 2000 < 1000:  
            glow = font_medium.render(current_message, True, (255, 255, 200, 100))
            screen.blit(glow, (text_rect.x, text_rect.y))
        
        # Instrucciones
        instructions = font_small.render("Haz clic para más corazones | ESC para salir", True, (240, 240, 255))
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 40))
        
        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)  
    
    pygame.quit()

if __name__ == "__main__":
    main()
