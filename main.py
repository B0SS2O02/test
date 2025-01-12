import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import Label, Button, Frame
from pygame import mixer
from scipy.spatial import distance as dist
from PIL import Image, ImageTk
import numpy as np

work = True

# Инициализация pygame mixer
mixer.init()
sound = mixer.Sound('alert.mp3')  # Замените на путь к вашему звуковому файлу

# Инициализация mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Функция для вычисления EAR
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Пороговые значения
EYE_AR_THRESH = 1.4
EYE_AR_CONSEC_FRAMES = 2
COUNTER = 0

window_size_x= 640
window_size_y= 480

# Начальный коэффициент масштаба и координаты центра
scale = 1.0
center_x, center_y = 320, 240  # Центральные координаты изображения для увеличения

# Захват видео с камеры
cap = cv2.VideoCapture(0)

def plus():
    global scale
    print('plus')
    scale = scale + 0.1  # Увеличиваем масштаб немного

def minus():
    global scale
    print('minus')
    scale = scale - 0.1  # Уменьшаем масштаб немного

def move(s):
    global center_x , center_y
    if s=='u':
        print('up')
        if center_y -10 > (window_size_y * scale) /4 :
            center_y -= 10 
    if s=='d':
        print('down')
        if center_y +10 < (window_size_y * scale)/2 :
            center_y += 10 
    if s=='l':
        print('left')
        if center_x -10 > 0 :
            center_x -= 10 
    if s=='r':
        print('right')
        if center_x +10 < (window_size_x * scale)/2 :
            center_x += 10 
    print(center_x, window_size_x * scale, center_y, window_size_y * scale)

def move_up():
    global center_y
    print('move up',center_y,center_x)
    if center_y -10 > 0 :
        center_y -= 10  # Сдвигаем центр увеличения вверх

def move_down():
    global center_y
    print('move down',center_y,center_x)
    if center_y+ 10 < window_size_y / scale:
        center_y += 10  # Сдвигаем центр увеличения вниз
    

def move_left(a):
    print(a)
    global center_x
    print('move left',center_y,center_x)
    if center_x -10 > 0 :
        center_x -= 10  # Сдвигаем центр увеличения влево

def move_right():
    global center_x
    print('move right',center_y,center_x)
    if center_x + 10 < window_size_x /scale:
        center_x += 10  # Сдвигаем центр увеличения вправо

def quit():
    global work
    print('quit')
    work = False

# Создаем окно с tkinter
root = tk.Tk()
root.title("Face Detection")


root.geometry(f"{window_size_x}x{window_size_y}")  # Устанавливаем размер окна

buttonConatiner = Frame(root)
buttonConatiner.pack()

buttonPlus = Button(buttonConatiner, text="+", command=plus)
buttonPlus.grid(row=1, column=1)

buttonMinus = Button(buttonConatiner, text="-", command=minus)
buttonMinus.grid(row=1, column=2)

buttonUp = Button(buttonConatiner, text="Up", command=lambda : move('u'))
buttonUp.grid(row=2, column=1)

buttonDown = Button(buttonConatiner, text="Down", command=lambda : move('d'))
buttonDown.grid(row=2, column=2)

buttonLeft = Button(buttonConatiner, text="Left", command=lambda : move('l'))
buttonLeft.grid(row=2, column=3)

buttonRight = Button(buttonConatiner, text="Right", command=lambda: move('r'))
buttonRight.grid(row=2, column=4)

buttonQuit = Button(buttonConatiner, text="exit", command=quit)
buttonQuit.grid(row=3, column=2)

# Создаем метку для отображения изображения
label = Label(root)
label.pack()

# Функция для обновления изображения в окне tkinter
def update_image(frame_resized):
    # Преобразуем изображение OpenCV (BGR) в формат PIL (RGB)
    image_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
    image_tk = ImageTk.PhotoImage(image_pil)
    
    # Обновляем изображение в метке tkinter
    label.config(image=image_tk)
    label.image = image_tk

# Запуск основного цикла
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

    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Координаты всех точек лица
            face_points = [
                (int(point.x * w), int(point.y * h))
                for point in face_landmarks.landmark
            ]

            # Границы лица
            x_min = min([point[0] for point in face_points])
            x_max = max([point[0] for point in face_points])
            y_min = min([point[1] for point in face_points])
            y_max = max([point[1] for point in face_points])

            # Рисуем квадрат вокруг лица
            face_color = (0, 255, 0)  # Зелёный по умолчанию
            
            # Координаты глаз
            left_eye_points = [
                (int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h))
                for i in [33, 133, 159, 145, 153, 386]
            ]
            right_eye_points = [
                (int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h))
                for i in [263, 362, 382, 380, 374, 387]
            ]
            


            # Корректируем координаты прямоугольников для глаз, уменьшая размеры
            # Для левого глаза
            
            right_eye_bbox = cv2.boundingRect(np.array(right_eye_points))
            
            
            left_eye_bbox = cv2.boundingRect(np.array(left_eye_points))
            left_eye_bbox = (
                left_eye_bbox[0] ,  # Сдвиг влево
                left_eye_bbox[1] ,  # Сдвиг вверх
                right_eye_bbox[2], # Уменьшаем ширину
                left_eye_bbox[3]   # Уменьшаем высоту
            )
            
            # Для правого глаза
     
            # right_eye_bbox = (
            #     right_eye_bbox[0] + 5,  # Сдвиг влево
            #     right_eye_bbox[1] + 5,  # Сдвиг вверх
            #     right_eye_bbox[2] - 10, # Уменьшаем ширину
            #     right_eye_bbox[3] - 10  # Уменьшаем высоту
            # )

            # Рисуем квадрат вокруг левого глаза
            cv2.rectangle(frame_resized, (left_eye_bbox[0], left_eye_bbox[1]),
                          (left_eye_bbox[0] + left_eye_bbox[2], left_eye_bbox[1] + left_eye_bbox[3]),
                          (255, 0, 0), 2)  # Красный цвет

            # Рисуем квадрат вокруг правого глаза
            cv2.rectangle(frame_resized, (right_eye_bbox[0], right_eye_bbox[1]),
                          (right_eye_bbox[0] + right_eye_bbox[2], right_eye_bbox[1] + right_eye_bbox[3]),
                          (255, 0, 0), 2)  # Красный цвет

            # Вычисление EAR
            leftEAR = eye_aspect_ratio(left_eye_points)
            rightEAR = eye_aspect_ratio(right_eye_points)
            ear = (leftEAR + rightEAR) / 2.0

            # Логика закрытия глаз
            if ear < EYE_AR_THRESH:
                COUNTER += 1
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    sound.play()
                    face_color = (0, 0, 255)  # Красный, если глаза закрыты
                    # Вывод текста "Закрыты" на кадре
                    cv2.putText(frame_resized, "Закрыты", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                COUNTER = 0
            
            
            cv2.rectangle(frame_resized, (x_min, y_min), (x_max, y_max), face_color, 2)

    # Обновляем изображение в tkinter
    update_image(frame_resized)

    # Обработка событий (для выхода)
    root.update_idletasks()
    root.update()

cap.release()
root.quit()
