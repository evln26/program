import cv2
from pyzbar.pyzbar import decode
import requests
from time import sleep
from rpi_lcd import LCD

# Ubidots API Credentials
TOKEN = "BBFF-HRGwpx4IeRlvLnblG1tRny0YehPjWz"
DEVICE_LABEL = "demo"
BARCODE_LABEL = "barcode"
COUNT_LABEL_PREFIX1 = "1111_count"
COUNT_LABEL_PREFIX2 = "2222_count"
COUNT_LABEL_PREFIX3 = "3333_count"
COUNT_LABEL_PREFIX4 = "4444_count"
COUNT_LABEL_PREFIX5 = "5555_count"

# Initialize the camera
cap = cv2.VideoCapture(0)  # 0 indicates the default camera (usually the laptop's built-in camera)

# Initialize the LCD
lcd = LCD()

# Dictionary to store individual barcode counts
barcode_counts = {
    "1111": 0,
    "2222": 0,
    "3333": 0,
    "4444": 0,
    "5555": 0
}

def send_data_to_ubidots(barcode_data):
    # Send the barcode data to the respective variable
    barcode_payload = {
        BARCODE_LABEL: barcode_data
    }

    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    try:
        response = requests.post(url=url, headers=headers, json=barcode_payload)
        if response.status_code == 200:
            print(f"Barcode sent to Ubidots: {barcode_data}")
        else:
            print("Failed to send barcode to Ubidots. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Connection error:", e)

def display_on_lcd(text):
    lcd.text(text, 1)

item_count = 0

lcd.text("Scan the Code... ", 1)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Decode the barcode in the frame
    barcodes = decode(frame)

    # Loop through all detected barcodes
    for barcode in barcodes:
        # Extract the data from the barcode
        barcode_data = barcode.data.decode('utf-8')

        # Check if the scanned barcode is one of the fixed barcodes
        if barcode_data in barcode_counts:
            # Update the count for the barcode
            barcode_counts[barcode_data] += 1

            # Send both barcode data and count data to Ubidots
            send_data_to_ubidots(barcode_data)

            # Display the barcode data on the LCD
            display_on_lcd(f"Scanned Barcode is {barcode_data}")
            sleep(2)  # Display for 2 seconds
            display_on_lcd("   Item Added")
            sleep(2)

            # Update and display the total item count
            item_count += 1
            display_on_lcd(f"  Total Item = {item_count}")
            sleep(1)

    # Display the frame with detected barcodes
    cv2.imshow('Barcode Reader', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
