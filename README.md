# AIoT Smart Recycling System  
Gachon University Introduction to Internet of Things (13966_001)  
2026-1 Semester Team C  
- Cho Wooyoung: Basic functionality & Structure  
- Seol Jaemin: Dashboard, final bugfix/test & Model finetuning   
- Lim Youbin: Sensor, RPI firebase integration

This is a smart recycling guidance system built using a Raspberry Pi, camera, YOLO object detection, PIR sensor, ultrasonic sensor, and an I2C LCD.

When a user approaches the recycling station, the PIR sensor detects movement, and the ultrasonic sensor verifies that an object has been placed on the designated platform or detection area. Once the object remains stable for a specified period, a countdown is displayed on the LCD before the camera captures an image. The captured image is then analyzed by a YOLO model, and recycling instructions are displayed on the LCD and recorded in the system log.
The system also includes an SG90 servo motor that automatically opens the lid during the disposal process.

Additionally, the system reports temperature and humidity sensor data, along with its own operational statistics, to Firebase.
These data can be monitored remotely through a web-based dashboard, allowing users to track environmental conditions and system status in real time.

## Key Features

1. Detects user approach or movement using a PIR sensor
2. Confirms that an object has been stably placed on the platform using an ultrasonic sensor
3. Displays a countdown (3, 2, 1) on the LCD
4. Captures an image using the Pi Camera
5. Classifies the object using a fine-tuned YOLO classification model
6. Displays recycling guidance based on the detected object type
7. Saves captured images, YOLO result images, and event logs
8. Supports a mock mode for testing the entire workflow even without physical sensors
9. Reports temperature and humidity sensor data and bin capacity as well as system statistics, to Firebase
10. Provides remote monitoring through a web dashboard

## Pipeline

```text
Idle
  -> PIR motion detected
  -> Measure distance using ultrasonic sensor
  -> Check whether the distance is below the threshold
  -> Verify that the distance remains stable for a specified period
  -> Display countdown on LCD
  -> Capture image with camera
  -> Run YOLO inference
  -> Display recycling guidance & open servo
  -> Save event log
  -> Return to idle state after cooldown
```

The system does not capture an image immediately when the PIR sensor detects motion. Image capture is triggered only when the ultrasonic sensor’s measured distance falls within the threshold defined in config.toml and remains stable, with minimal fluctuation, for the duration specified by stable_required_seconds.

In addition, a dedicated background thread is responsible for system status reporting. This thread operates independently of the main processing thread and periodically reports system status and monitoring data without interrupting the object detection workflow.

## Quick Start

Navigate to the project directory on the Raspberry Pi.

```sh
python project/run.py
```

After starting the dashboard server, open a web browser and navigate to the reported address (127.0.0.1:5000) to view the dashboard.
```sh
python dashboard/run.py
```

Note: It is recommended to use a combination of system packages and a Python virtual environment (venv) when installing dependencies. Some packages may have compatibility issues on Raspberry Pi 5, and certain libraries are more stable when installed through the system package manager.

Raspberry Pi storage space can be limited, so installing the entire ultralytics package is generally not recommended.
Important: Avoid installing packages that are not supported on Raspberry Pi, such as CUDA-related libraries. These packages are unnecessary on Raspberry Pi systems and may cause installation or dependency issues.

## Basic Configuration

The system configuration is stored in the config.toml file.   
For best compatibility, it is recommended to use the default settings and configure the hardware accordingly.

## Hardware Components

- Raspberry Pi 5
- Raspberry Pi Camera Module
- HC-SR04 Ultrasonic Sensor ×2
- PIR Motion Sensor
- DHT11 Temperature/Humidity Sensor
- SG90 Servo Motor
- I2C 16x2 LCD
- Registors for Voltage Divider (1kΩ + 2kΩ)
  
## Raspberry Pi Pin Numbering

* BCM GPIO Numbering: The numbering scheme used by the software. Example: GPIO17
* Physical Pin Numbering: The actual pin positions on the Raspberry Pi’s 40-pin header. Example: Physical Pin 11

The code and config.toml use BCM GPIO numbering. When configuring or modifying pin assignments, always refer to the BCM pin numbers rather than the physical pin numbers.
| GPIO   | Physical Pin | Connection             |
|---------|-------------|------------------------|
| GPIO2   | Pin 3       | LCD SDA                |
| GPIO3   | Pin 5       | LCD SCL                |
| GPIO4   | Pin 7       | Temp/Humidity DATA     |
| GPIO17  | Pin 11      | PIR OUT                |
| GPIO18  | Pin 12      | Lid Servo Control      |
| GPIO23  | Pin 16      | Main Ultrasonic TRIG   |
| GPIO24  | Pin 18      | Main Ultrasonic ECHO   |
| GPIO25  | Pin 22      | Bin Ultrasonic TRIG    |
| GPIO8   | Pin 24      | Bin Ultrasonic ECHO    |

Since the HC-SR04 Echo pin outputs 5V, a voltage divider is required to reduce the signal to 3.3V before connecting it to the Raspberry Pi GPIO pin.
```text
HC-SR04 ECHO ---- R1(1k) ----+---- Raspberry Pi GPIO
                             |
                            R2(2k)
                             |
                            GND
```

## Adjusting the Distance Threshold

The ultrasonic sensor detection threshold can be configured in config.toml.

```toml
[sensors.ultrasonic]
object_distance_cm = 18.0
stable_tolerance_cm = 2.5
```

- object_distance_cm: Objects closer than this distance are considered present.
- stable_tolerance_cm: Maximum allowed fluctuation in distance measurements while determining stability.
- stable_required_seconds: The amount of time the measured distance must remain stable before image capture is triggered. This setting is located in the [app] section.

## YOLO Model Fine-Tuning

The yolo26s-cls model was fine-tuned on a custom dataset consisting of 10 waste classification categories.

```text
Battery
Biological
Cardboard
Clothes
Glass
Metal
Paper
Plastic
Trash
Vinyl
```

By using a dedicated classification model instead of a general-purpose pretrained model, the inference pipeline could be simplified significantly. This approach reduced implementation complexity while also providing better classification performance for the target recycling categories.

The fine-tuned model is optimized specifically for the waste-sorting scenarios used in this project, resulting in higher accuracy and more reliable predictions than a generic off-the-shelf model.
<img width="3000" height="2250" alt="confusion_matrix_normalized" src="https://github.com/user-attachments/assets/3e359a3c-2105-4240-8755-32de800b4901" />

After training was completed, the following confusion matrix was obtained during evaluation.

The results indicate strong classification performance across all classes, with most predictions concentrated along the diagonal of the matrix. This suggests that the model is able to distinguish the target waste categories accurately and achieves a high overall level of classification performance.

For information regarding the Ultralytics software license, please refer to:
https://www.ultralytics.com/

This model was fine-tuned using datasets that include content licensed under CC BY-SA 4.0, CC BY, and MIT licenses.

Datasets used:
* https://www.kaggle.com/datasets/vencerlanz09/plastic-paper-garbage-bag-synthetic-images
* https://www.kaggle.com/datasets/sumn2u/garbage-classification-v2
* https://www.kaggle.com/datasets/joebeachcapital/realwaste

CC BY-SA 4.0 License:
https://creativecommons.org/licenses/by-sa/4.0/

This notice applies only to the model file yolo26s_Finetuned.pt.

Other files in this project may be subject to separate licenses, notices, or terms where applicable. No additional rights or restrictions regarding other project components are implied by this notice.

Special thanks to the authors and contributors of the original datasets.

## Stored Output Files

Captured Images
```text
~/Pictures/aiot-smart-recycling/capture_YYYYMMDD_HHMMSS.jpg
```

YOLO Result Images
```text
~/Pictures/aiot-smart-recycling/annotated_YYYYMMDD_HHMMSS.jpg
```

Event Log
```text
~/IoT26_Team_project/project/events.jsonl
```

## Demo
### Dashboard Demo
<img width="1235" height="677" alt="Screenshot 2026-06-16 at 1 15 26" src="https://github.com/user-attachments/assets/3b3806b2-78dc-4640-95e0-c4ad7605fd1b" />

### Main classification Demo
[Demo.webm](https://github.com/user-attachments/assets/7cabc889-3dd9-46df-b7af-532c45dbb053)

### Image classification example
<img width="320" height="320" alt="annotated_20260615_045323" src="https://github.com/user-attachments/assets/a054769b-afcb-48b8-8924-b5162026bc6e" />


