import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

ses_aygıtları = AudioUtilities.GetSpeakers()
arayuz = ses_aygıtları.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
ses = cast(arayuz, POINTER(IAudioEndpointVolume))

mp_hands = mp.solutions.hands
eller = mp_hands.Hands()
mp_cizim = mp.solutions.drawing_utils

kamera = cv2.VideoCapture(0)

while True:
    basarili, img = kamera.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    sonuclar = eller.process(img_rgb)

    if sonuclar.multi_hand_landmarks:
        for el in sonuclar.multi_hand_landmarks:
            lmlist = []

            for id, lm in enumerate(el.landmark):
                yukseklik, genislik, kanal = img.shape
                cx, cy = int(lm.x * genislik), int(lm.y * yukseklik)
                lmlist.append([id, cx, cy])

            if lmlist:
                x1, y1 = lmlist[4][1], lmlist[4][2]
                x2, y2 = lmlist[8][1], lmlist[8][2]

                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 4)

                uzunluk = math.hypot((x2 - x1), (y2 - y1))

                vol_range = ses.GetVolumeRange()
                min_vol = vol_range[0]
                max_vol = vol_range[1]
                vol = np.interp(uzunluk, [20, 200], [min_vol, max_vol])
                ses.SetMasterVolumeLevel(vol, None)

                vol_bar = np.interp(uzunluk, [20, 200], [400, 150])
                vol_yuzde = np.interp(uzunluk, [25, 200], [0, 100])

                cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
                cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f"Ses: {int(vol_yuzde)}%", (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)

    cv2.imshow("El İzleme ve Ses Kontrolü", img)
    cv2.waitKey(1)
    if not basarili:
        print("Boş kamera çerçevesini yok say")
        continue