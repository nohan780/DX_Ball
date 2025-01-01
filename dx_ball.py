from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math



paddle_colors = [
    (0.0, 0.5, 0.5),  #teal
    (0.0, 1.0, 1.0),  # Cyan
    (1.0, 0.75, 0.8),  # Pink
    (0.5, 0.0, 0.0),  # Maroon
    (0.0, 1.0, 0.0)   # Green
]


current_paddle_color = (1.0, 1.0, 1.0)  # Default to white color


powerup_radius = 8
paddle_x = 250
ball_x = 250
ball_y = 100
ball_dx = random.choice([-2, 2])
ball_dy = 2
base_ball_speed = 2
paddle_width = 60
ball_radius = 5
score = 0
level = 1
game_over = False
bricks = []
powerups = []
start_time = 0
level_clear = False
speed_multiplier = 1.0

paused = False

WHITE = (1.0, 1.0, 1.0)
RED = (1.0, 0.0, 0.0)
YELLOW = (1.0, 1.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
GRAY = (0.5, 0.5, 0.5)
BLACK = (0.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
CYAN = (0.0, 1.0, 1.0)
MAGENTA = (1.0, 0.0, 1.0)

def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)  
    for char in text:
        glutBitmapCharacter(font, ord(char))




def draw_circle(center_x, center_y, radius):
    x = 0
    y = radius
    decision_parameter = 1 - radius

    draw_circle_points(center_x, center_y, x, y)

    while x <= y:
        x += 1
        if decision_parameter < 0:
            decision_parameter += 2 * x + 1
        else:
            y -= 1
            decision_parameter += 2 * (x - y) + 1
        draw_circle_points(center_x, center_y, x, y)


def draw_circle_points(center_x, center_y, x, y):

    points = [
        (center_x + x, center_y + y),
        (center_x - x, center_y + y),
        (center_x + x, center_y - y),
        (center_x - x, center_y - y),
        (center_x + y, center_y + x),
        (center_x - y, center_y + x),
        (center_x + y, center_y - x),
        (center_x - y, center_y - x),
    ]
    glBegin(GL_POINTS)
    for px, py in points:
        glVertex2f(px, py)
    glEnd()


# Midpoint Line Algorithm
def draw_line(x1, y1, x2, y2):

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1

    step_x = 1 if x2 > x1 else -1
    step_y = 1 if y2 > y1 else -1

    glBegin(GL_POINTS)
    if dx > dy:
        decision_parameter = 2 * dy - dx
        while x != x2:
            glVertex2f(x, y)
            x += step_x
            if decision_parameter > 0:
                y += step_y
                decision_parameter -= 2 * dx
            decision_parameter += 2 * dy
    else:
        decision_parameter = 2 * dx - dy
        while y != y2:
            glVertex2f(x, y)
            y += step_y
            if decision_parameter > 0:
                x += step_x
                decision_parameter -= 2 * dy
            decision_parameter += 2 * dx
    glVertex2f(x2, y2)
    glEnd()



def draw_points(x, y):
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def draw_button_symbols():
    # Restart button
    glColor3fv(GREEN)
    draw_line(30, 520, 40, 530)
    draw_line(30, 520, 50, 520)
    draw_line(30, 520, 40, 510)

    # Pause/Play button
    glColor3fv(YELLOW)
    if not paused:
        # Pause button
        draw_line(240, 530, 240, 510)
        draw_line(250, 530, 250, 510)
    else:
        # Play button (triangle)
        draw_line(240, 530, 240, 510)
        draw_line(240, 530, 260, 520)
        draw_line(240, 510, 260, 520)

    # Quit button
    glColor3fv(RED)
    draw_line(450, 530, 470, 510)
    draw_line(450, 510, 470, 530)


def create_level_bricks(level_num):
    global bricks
    bricks = []

    patterns = {
        1: [(row, col) for row in range(5) for col in range(10)],
        2: [(row, col) for row in range(6) for col in range(12) if (row + col) % 2 == 0],
        3: [(row, col) for row in range(7) for col in range(14) if abs(col - 7) <= row]
    }

    # Use level pattern or generate random if level > 3
    brick_positions = patterns.get(level_num,
                                   [(row, col) for row in range(8) for col in range(15) if random.random() > 0.3])

    for row, col in brick_positions:
        x = col * 45 + 25
        y = 450 - row * 20
        durability = min(3, 1 + level_num // 2)

        # unbreakable bricks for levels > 2
        if level_num > 2 and random.random() < 0.1:
            durability = -1  # Unbreakable

        bricks.append({
            'x': x,
            'y': y,
            'width': 40,
            'height': 15,
            'durability': durability,
            'active': True
        })


def update_ball_speed():
    global ball_dx, ball_dy, speed_multiplier

    # Calculate speed multiplier based on score
    base_multiplier = 1.0
    score_thresholds = [1000, 1500, 2000, 2500, 3000]

    for threshold in score_thresholds:
        if score >= threshold:
            base_multiplier += 0.2

    speed_multiplier = base_multiplier

    # Normalize the ball direction and apply speed
    magnitude = math.sqrt(ball_dx * ball_dx + ball_dy * ball_dy)
    if magnitude > 0:
        ball_dx = (ball_dx / magnitude) * base_ball_speed * speed_multiplier
        ball_dy = (ball_dy / magnitude) * base_ball_speed * speed_multiplier


def check_level_complete():
    global level, level_clear, score
    active_bricks = sum(1 for brick in bricks if brick['active'] and brick['durability'] != -1)

    if active_bricks == 0:
        level_clear = True
        score += 1000  # Bonus for clearing level
        level += 1
        create_level_bricks(level)
        reset_ball_position()


def reset_ball_position():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = 250
    ball_y = 100
    ball_dx = random.choice([-2, 2])
    ball_dy = 2



def draw_paddle():
    glColor3f(*current_paddle_color) 
    draw_line(paddle_x - paddle_width, 20, paddle_x + paddle_width, 20)



def draw_ball():
    draw_circle(int(ball_x), int(ball_y), ball_radius)


def draw_bricks():
    for brick in bricks:
        if brick['active']:
            x, y = brick['x'], brick['y']
            w, h = brick['width'], brick['height']

            if brick['durability'] == -1:
                # Unbreakable brick - White
                glColor3f(1.0, 1.0, 1.0)
            elif brick['durability'] == 3:
                glColor3f(1.0, 0.0, 0.0)  # Red
            elif brick['durability'] == 2:
                glColor3f(0.0, 1.0, 0.0)  # Green
            else:
                glColor3f(0.0, 0.0, 1.0)  # Blue

            draw_line(x - w // 2, y - h // 2, x + w // 2, y - h // 2)
            draw_line(x - w // 2, y + h // 2, x + w // 2, y + h // 2)
            draw_line(x - w // 2, y - h // 2, x - w // 2, y + h // 2)
            draw_line(x + w // 2, y - h // 2, x + w // 2, y + h // 2)



def draw_hud():
    """Display Score, Level, and Ball Speed on the screen."""
    glColor3f(1.0, 1.0, 0.0)  # Yellow for Score
    draw_text(10, 470, f"Score: {score}")

    glColor3f(0.0, 1.0, 1.0)  # Cyan for Level
    draw_text(200, 470, f"Level: {level}")

    
    ball_speed = math.sqrt(ball_dx ** 2 + ball_dy ** 2)

    
    glColor3f(1.0, 0.5, 0.0)  # Orange for Ball Speed
    draw_text(350, 470, f"Speed: {int(ball_speed)}")




def draw_game_over():
    glColor3f(1.0, 0.0, 0.0)  # Red for Game Over Text
    draw_text(200, 300, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)

    glColor3f(1.0, 1.0, 0.0)  # Yellow for Final Score
    draw_text(200, 250, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)

    glColor3f(0.0, 1.0, 1.0)  # Cyan for Restart Instruction
    draw_text(200, 200, "Press 'R' to Restart", GLUT_BITMAP_HELVETICA_18)



def check_paddle_collision():
    global ball_dy, ball_dx

    closest_x = max(paddle_x - paddle_width, min(ball_x, paddle_x + paddle_width))
    paddle_y = 20

    distance = euclidean_distance(ball_x, ball_y, closest_x, paddle_y)

    if distance <= ball_radius:
        ball_dy = abs(ball_dy)
        hit_position = (ball_x - paddle_x) / paddle_width
        ball_dx = hit_position




def apply_powerup(powerup_type):
    global paddle_width, ball_dx, ball_dy, level_clear, score, ball_radius, level, current_paddle_color
    ball_speed = math.sqrt(ball_dx ** 2 + ball_dy ** 2)
    if powerup_type == 'extend':
        paddle_width = min(100, paddle_width + 20)  # Increase paddle width
        # Randomly change paddle color
        current_paddle_color = random.choice(paddle_colors)

    elif powerup_type == 'shrink':
        paddle_width = max(30, paddle_width - 20)
    elif powerup_type == 'speed':
        ball_dx *= 2.0
        ball_dy *= 2.0
    elif powerup_type == 'slow' and ((ball_speed/2) > 1):
        ball_dx *= 0.5
        ball_dy *= 0.5
    elif powerup_type == 'level_clear':
        # Clear level and move to the next
        score += 1000
        level_clear = True
        level += 1 
        create_level_bricks(level)
        reset_ball_position()
    elif powerup_type == 'power_ball':
        # 'Power Ball' that clears bricks directly
        ball_dx *= 1.2 
        ball_dy *= 1.2
        ball_radius += 10 





def check_brick_collision():
    global ball_dy, score, ball_dx, powerups

    for brick in bricks:
        if not brick['active']:
            continue

        closest_x = max(brick['x'] - brick['width'] // 2,
                        min(ball_x, brick['x'] + brick['width'] // 2))
        closest_y = max(brick['y'] - brick['height'] // 2,
                        min(ball_y, brick['y'] + brick['height'] // 2))

        distance = euclidean_distance(ball_x, ball_y, closest_x, closest_y)

        if distance <= ball_radius:
            if brick['durability'] == -1:
                # Unbreakable brick
                if abs(ball_x - brick['x']) > abs(ball_y - brick['y']):
                    ball_dx = -ball_dx
                else:
                    ball_dy = -ball_dy
            else:
                brick['durability'] -= 1
                if brick['durability'] <= 0:
                    brick['active'] = False
                    score += 100 * level

                    # Drop normal power-up randomly
                    if random.random() < 0.2:
                        powerups.append({
                            'x': brick['x'],
                            'y': brick['y'],
                            'type': random.choice(['extend', 'shrink', 'speed', 'slow'])
                        })

                    # Drop special balls randomly
                    if random.random() < 0.1:
                        special_ball_type = random.choice(['level_clear', 'power_ball'])
                        powerups.append({
                            'x': brick['x'],
                            'y': brick['y'],
                            'type': special_ball_type
                        })

                if abs(ball_x - brick['x']) > abs(ball_y - brick['y']):
                    ball_dx = -ball_dx
                else:
                    ball_dy = -ball_dy

                check_level_complete()
                #update_ball_speed()
                return


def check_powerup_collision():
    for powerup in powerups[:]:
        powerup['y'] -= 2
        if powerup['y'] < 0:
            powerups.remove(powerup)
        else:
            
            distance = euclidean_distance(powerup['x'], powerup['y'], paddle_x, 20)
            if distance <= paddle_width + 5:
                apply_powerup(powerup['type'])
                powerups.remove(powerup)




def update():
    global ball_x, ball_y, ball_dx, ball_dy, game_over

    if not game_over:
        ball_x += ball_dx
        ball_y += ball_dy

        if ball_x - ball_radius <= 5 or ball_x + ball_radius >= 495:
            ball_dx = -ball_dx
        if ball_y + ball_radius >= 470:
            ball_dy = -ball_dy

        if ball_y - ball_radius <= 0:
            game_over = True
            return
        
        check_paddle_collision()
        check_brick_collision()
        check_powerup_collision()


def reset_game():
    global paddle_x, ball_x, ball_y, ball_dx, ball_dy, paddle_width, paused, ball_radius, score, game_over, bricks, powerups, level, speed_multiplier, start_time

    paddle_x = 250
    ball_x = 250
    ball_y = 100
    ball_dx = random.choice([-base_ball_speed, base_ball_speed])
    ball_dy = 2
    paddle_width = 60
    ball_radius = 5
    score = 0
    level = 1
    game_over = False
    paused = False
    bricks = []
    powerups = []
    speed_multiplier = 1.0
    start_time = glutGet(GLUT_ELAPSED_TIME)
    create_level_bricks(level)


def keyboard(key, x, y):
    global paddle_x
    if (key == b'a' or key == b'A') and paused !=  True:
        paddle_x = max(paddle_width, paddle_x - 30)
    elif (key == b'd' or key == b'D') and paused !=  True:
        paddle_x = min(500 - paddle_width, paddle_x + 30)
    elif (key == b'r' or key == b'R') and paused !=  True:
        reset_game()

def mouse_listener(button, state, x, y):        
    global paused, game_over
    y = glutGet(GLUT_WINDOW_HEIGHT) - y
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Restart
        if 20 <= x <= 60 and 510 <= y <= 540:
            reset_game()
        
        # Pause & Play
        elif 230 <= x <= 270 and 500 <= y <= 540:
            paused = not paused
            print("Game Paused" if paused else "Game Resumed")
        
        # Quit
        elif 440 <= x <= 480 and 500 <= y <= 540:
            print(f"Goodbye! Final Score: {score}")
            draw_game_over()
            glutLeaveMainLoop()

def iterate():
    glViewport(0, 0, 500, 550)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 550, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()

    if not game_over:
        # Draw HUD
        draw_hud()

        # Draw paddle
        glColor3f(1.0, 1.0, 1.0)
        draw_paddle()
        
        # Draw ball
        glColor3f(1.0, 1.0, 0.0)
        draw_ball()

        # Draw bricks
        draw_bricks()

        for powerup in powerups:
            if powerup['type'] == 'level_clear':
                glColor3f(1.0, 0.84, 0.0)  # Golden color for Level Clear Ball
            elif powerup['type'] == 'power_ball':
                glColor3f(0.8, 0.0, 0.8)  # Purple for Power Ball
            elif powerup['type'] == 'shrink':
                glColor3f(1.0, 0.0, 0.0)  # Red for Shrink Paddle
            elif powerup['type'] == 'extend':
                glColor3f(0.7, 0.3, 0.1)  # Rust for Extend Paddle
            elif powerup['type'] == 'speed':
                glColor3f(0.5, 0.0, 0.0)  # Maroon for Speed Ball
            elif powerup['type'] == 'slow':
                glColor3f(0.0, 1.0, 0.0)  # Green for Slow Ball

            
            draw_circle(int(powerup['x']), int(powerup['y']), powerup_radius)
        if not paused:
            update()
    else:
        draw_game_over()
    draw_button_symbols()


    glutSwapBuffers()




glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(500, 550)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"DX Ball Game")
create_level_bricks(level)
start_time = glutGet(GLUT_ELAPSED_TIME)
glutDisplayFunc(showScreen)
glutIdleFunc(showScreen)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse_listener)
glutMainLoop()