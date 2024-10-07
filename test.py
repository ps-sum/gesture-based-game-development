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
screen_width, screen_height = 640, 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Gesture Control Obstacle Course')

# Colors
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
white = (255, 255, 255)

# Player properties
player_x = screen_width // 2
player_y = screen_height - 50
player_radius = 20
move_speed = 10

# Obstacle properties
obstacle_width = 50
obstacle_height = 20
obstacles = []
num_obstacles = 5
obstacle_speed = 5

# Game variables
score = 0
font = pygame.font.Font(None, 36)
game_over = False
error_message = ""

# Function to create obstacles
def create_obstacles(num):
    for _ in range(num):
        x = random.randint(0, screen_width - obstacle_width)
        y = random.randint(-200, -50)
        obstacles.append([x, y])

create_obstacles(num_obstacles)

# OpenCV Video Capture
cap = cv2.VideoCapture(0)

def get_hand_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # Calculate distance between thumb and index finger tips
    distance = ((thumb_tip.x - index_finger_tip.x) ** 2 + (thumb_tip.y - index_finger_tip.y) ** 2) ** 0.5

    if distance < 0.05:
        return "left"
    elif thumb_tip.x < index_finger_tip.x:
        return "right"
    return None

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

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    result = hands.process(image_rgb)

    gesture = None
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = get_hand_gesture(hand_landmarks)

    # Update player position based on gesture
    if gesture == "left" and player_x - player_radius > 0:
        player_x -= move_speed
    elif gesture == "right" and player_x + player_radius < screen_width:
        player_x += move_speed

    # Update obstacle positions
    for obstacle in obstacles:
        obstacle[1] += obstacle_speed  # Move obstacle down

        # Reset obstacle position if it goes off screen
        if obstacle[1] > screen_height:
            obstacle[0] = random.randint(0, screen_width - obstacle_width)
            obstacle[1] = random.randint(-200, -50)
            score += 1  # Increment score when obstacle is avoided

        # Check for collision
        if (obstacle[0] < player_x < obstacle[0] + obstacle_width or
                obstacle[0] < player_x + player_radius < obstacle[0] + obstacle_width) and \
                (obstacle[1] < player_y < obstacle[1] + obstacle_height or
                 obstacle[1] < player_y + player_radius < obstacle[1] + obstacle_height):
            game_over = True
            error_message = "Game Over! You hit an obstacle."

    # Clear the screen
    screen.fill(black)

    # Draw the player
    pygame.draw.circle(screen, blue, (player_x, player_y), player_radius)

    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, red, (obstacle[0], obstacle[1], obstacle_width, obstacle_height))

    # Render the score
    score_text = font.render(f'Score: {score}', True, white)
    screen.blit(score_text, (10, 10))

    # Display error message if game over
    if game_over:
        error_text = font.render(error_message, True, white)
        screen.blit(error_text, (screen_width // 2 - error_text.get_width() // 2, screen_height // 2))

    # Update the display
    pygame.display.flip()

    # Display the resulting frame for debug purposes (can be commented out)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Release the capture and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()

