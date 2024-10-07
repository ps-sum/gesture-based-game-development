import cv2
import mediapipe as mp
import pygame
import sys
import random

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize Pygame
pygame.init()
screen_width, screen_height = 300, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Gesture-Controlled Tetris')

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
colors = [(0, 255, 255), (255, 165, 0), (0, 255, 0), (255, 0, 0), (128, 0, 128)]

# Tetris shapes
shapes = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
]

# Tetris piece class
class TetrisPiece:
    def __init__(self):
        self.shape = random.choice(shapes)
        self.color = random.choice(colors)
        self.x = screen_width // 2 // 30 * 30
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]  # Rotate clockwise

# Game variables
board = [[0 for _ in range(10)] for _ in range(20)]
current_piece = TetrisPiece()
game_over = False
font = pygame.font.Font(None, 36)

# OpenCV Video Capture
cap = cv2.VideoCapture(0)

def get_hand_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # Check for thumbs up gesture
    if thumb_tip.y < index_finger_tip.y:
        return "rotate"  # Thumbs up
    # Check for closed fist gesture
    elif index_finger_tip.y > thumb_tip.y:
        return "left"  # Super gesture (closed fist)
    # Check for open palm gesture
    elif thumb_tip.y < index_finger_tip.y and index_finger_tip.x > thumb_tip.x:
        return "right"  # Open palm
    return None

def draw_board():
    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x]:
                pygame.draw.rect(screen, colors[board[y][x] - 1], (x * 30, y * 30, 30, 30))

def check_collision(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                if (x + piece.x // 30 < 0 or
                    x + piece.x // 30 >= 10 or
                    y + piece.y // 30 >= 20 or
                    board[y + piece.y // 30][x + piece.x // 30]):
                    return True
    return False

def merge_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                board[y + piece.y // 30][x + piece.x // 30] = colors.index(piece.color) + 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    if game_over:
        continue

    # Capture frame-by-frame
    success, image = cap.read()
    if not success:
        continue

    # Flip the image horizontally
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    result = hands.process(image_rgb)
    gesture = None

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = get_hand_gesture(hand_landmarks)

    # Handle gestures
    if gesture == "rotate":
        current_piece.rotate()
        if check_collision(current_piece):
            current_piece.rotate()  # Undo rotation if collision
    elif gesture == "left":
        current_piece.x -= 30
        if check_collision(current_piece):
            current_piece.x += 30  # Undo move if collision
    elif gesture == "right":
        current_piece.x += 30
        if check_collision(current_piece):
            current_piece.x -= 30  # Undo move if collision

    # Move piece down
    current_piece.y += 30
    if check_collision(current_piece):
        current_piece.y -= 30  # Undo move if collision
        merge_piece(current_piece)
        current_piece = TetrisPiece()
        if check_collision(current_piece):
            game_over = True

    # Clear the screen
    screen.fill(black)
    draw_board()

    # Draw current piece
    for y, row in enumerate(current_piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, current_piece.color, ((x + current_piece.x // 30) * 30, 
                                                               (y + current_piece.y // 30) * 30, 30, 30))

    # Render game over message if needed
    if game_over:
        error_text = font.render("Game Over!", True, white)
        screen.blit(error_text, (screen_width // 2 - error_text.get_width() // 2, screen_height // 2))

    # Update the display
    pygame.display.flip()
    pygame.time.delay(100)

    # Display the resulting frame for debug purposes (can be commented out)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Release the capture and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()