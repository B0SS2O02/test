import tkinter as tk
from tkinter import Frame, Button, Label
import cv2
from PIL import Image, ImageTk
import numpy as np
import pygame

# Устанавливаем размеры окна
window_size_x = 800
window_size_y = 600

# Захват видео
cap = cv2.VideoCapture(0)

# Звуковой сигнал для уведомления
pygame.mixer.init()
sound = pygame.mixer.Sound('alert.mp3')

# Коэффициенты для масштабирования
scale = 1.5
center_x, center_y = 320, 240

# Параметры для расчета EAR
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 48
COUNTER = 0

# Функция для расчета EAR (Eye Aspect Ratio)
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Функция для перемещения
def move(direction):
    global center_x, center_y
    if direction == 'u':
        center_y -= 10
    elif direction == 'd':
        center_y += 10
    elif direction == 'l':
        center_x -= 10
    elif direction == 'r':
        center_x += 10

# Функции для кнопок
def plus():
    global scale
    scale += 0.1

def minus():
    global scale
    scale -= 0.1

def quit():
    global work
    work = False

# Создаем окно с tkinter
root = tk.Tk()
root.title("Face Detection")

root.geometry(f"{window_size_x}x{window_size_y}")  # Устанавливаем размер окна
root.config(bg="#2C3E50")  # Темный фон

# Создаем контейнер для кнопок
buttonConatiner = Frame(root, bg="#34495E")
buttonConatiner.pack(pady=20)

# Размещаем все кнопки в одной строке с отступами
buttonPlus = Button(buttonConatiner, text="+", command=plus, font=("Helvetica", 14), width=5, height=2, bg="#16A085", fg="white", relief="flat")
buttonPlus.grid(row=1, column=1)

buttonMinus = Button(buttonConatiner, text="-", command=minus, font=("Helvetica", 14), width=5, height=2, bg="#16A085", fg="white", relief="flat")
buttonMinus.grid(row=1, column=3)

buttonUp = Button(buttonConatiner, text="Up", command=lambda: move('u'), font=("Helvetica", 14), width=5, height=2, bg="#16A085", fg="white", relief="flat")
buttonUp.grid(row=1, column=2)

# buttonDown = Button(buttonConatiner, text="Down", command=lambda: move('d'), font=("Helvetica", 14), width=5, height=2, bg="#16A085", fg="white", relief="flat")
# buttonDown.grid(row=2, column=2)

# buttonLeft = Button(buttonConatiner, text="Left", command=lambda: move('l'), font=("Helvetica", 14), width=5, height=2, bg="#16A085", fg="white", relief="flat")
# buttonLeft.grid(row=2, column=1)

# buttonRight = Button(buttonConatiner, text="Right", command=lambda: move('r'), font=("Helvetica", 14), width=5, height=2, bg="#16A085", fg="white", relief="flat")
# buttonRight.grid(row=2, column=3)

# buttonQuit = Button(buttonConatiner, text="Exit", command=quit, font=("Helvetica", 14), width=5, height=2, bg="#E74C3C", fg="white", relief="flat")
# buttonQuit.grid(row=2, column=2)

# Создаем метку для отображения изображения
label = Label(root)
label.pack(pady=20)

# Функция для обновления изображения в окне tkinter
def update_image(frame_resized):
    # Преобразуем изображение OpenCV (BGR) в формат PIL (RGB)
    image_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
    image_tk = ImageTk.PhotoImage(image_pil)
    
    # Обновляем изображение в метке tkinter
    label.config(image=image_tk)
    label.image = image_tk

# Запуск основного цикла
work = True
while work:
    ret, frame = cap.read()
    if not ret:
        break

    # Масштабируем изображение под текущий коэффициент масштаба с учетом центра
    h, w = frame.shape[:2]

    # Обрезка изображения вокруг центра, чтобы увеличить область фокуса
    x_start = max(center_x - int(w / (2 * scale)), 0)
    y_start = max(center_y - int(h / (2 * scale)), 0)

    cropped_frame = frame[y_start:y_start + int(h / scale), x_start:x_start + int(w / scale)]

    # Масштабируем обрезанное изображение до размеров экрана
    frame_resized = cv2.resize(cropped_frame, (w, h), interpolation=cv2.INTER_LINEAR)

    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

    # Применение модели для обнаружения лица
    # Вставьте сюда код для использования модели (например, face_mesh из Mediapipe)

    # Если лица найдены, рисуем границу и другие элементы
    # Это примерный код, его нужно адаптировать под вашу модель

    # Обновляем изображение в tkinter
    update_image(frame_resized)

    # Обработка событий (для выхода)
    root.update_idletasks()
    root.update()

cap.release()
root.quit()
