import cv2
from pyzbar.pyzbar import decode
from playsound import playsound
import threading
import json


def draw_l_shape_corners(frame, pt1, pt2, line_length=30, color=(0, 255, 0), thickness=3):
    cv2.line(frame, pt1, (pt1[0] + line_length, pt1[1]), color, thickness)
    cv2.line(frame, pt1, (pt1[0], pt1[1] + line_length), color, thickness)

    # Yuqori o'ng burchak
    cv2.line(frame, (pt2[0] - line_length, pt1[1]), (pt2[0], pt1[1]), color, thickness)
    cv2.line(frame, (pt2[0], pt1[1]), (pt2[0], pt1[1] + line_length), color, thickness)

    # Pastki chap burchak
    cv2.line(frame, (pt1[0], pt2[1] - line_length), (pt1[0], pt2[1]), color, thickness)
    cv2.line(frame, (pt1[0], pt2[1]), (pt1[0] + line_length, pt2[1]), color, thickness)

    # Pastki o'ng burchak
    cv2.line(frame, (pt2[0] - line_length, pt2[1]), pt2, color, thickness)
    cv2.line(frame, (pt2[0], pt2[1] - line_length), (pt2[0], pt2[1]), color, thickness)


def play_sound(sound_path):
    playsound(sound_path)


def read_barcode_from_camera():
    ip_camera_url = "rtsp://192.168.1.161:8080/h264.sdp"
    cap = cv2.VideoCapture(ip_camera_url)
    data = ""
    data_list = []
    sound_path = "sound/signal.wav"  # Sound file path
    cv2.namedWindow("Shtrix Kod O'qish", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Shtrix Kod O'qish", 400, 400)

    # Load product data from JSON
    with open('Data/data.json') as f:
        product_data = json.load(f)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error connecting to the camera.")
            break

        barcodes = decode(frame)
        if barcodes:
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                if barcode_data != data:
                    data = barcode_data
                    data_list.append(data)
                    print("Barcode data:", data)
                    threading.Thread(target=play_sound, args=(sound_path,)).start()

                    # Search for the product in the data.json file
                    product = next((item for item in product_data if item["barcode"] == data), None)
                    if product:
                        product_info = f"Name: {product['name']}, Price: {product['price']}, Count: {product['count']}"
                        print(product_info)  # Display product information
                    else:
                        print("Product not found.")

        # Draw frame with L-shape corners
        height, width, _ = frame.shape
        pt1 = (100, 100)
        pt2 = (width - 100, height - 100)
        draw_l_shape_corners(frame, pt1, pt2)
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect  # Burchak koordinatalarini olish
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Yarimchikma yaratish

        cv2.imshow("Shtrix Kod O'qish", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(len(data_list))
            for i in data_list:
                print(i)
            break

    cap.release()
    cv2.destroyAllWindows()


read_barcode_from_camera()
