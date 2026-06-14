# WARING! UPDATE AND TRANSLATE INTO ENG BEFORE SUBMISSION

# AIoT Smart Recycling System

라즈베리파이, 카메라, YOLO 객체 인식, PIR 센서, 초음파 센서, I2C LCD를 이용한 스마트 분리수거 안내 시스템입니다.

사용자가 분리수거함 앞에 접근하면 PIR 센서가 움직임을 감지하고, 초음파 센서가 실제로 지정된 판이나 영역 위에 물체가 놓였는지 확인합니다. 물체가 일정 시간 안정적으로 감지되면 LCD에 카운트다운을 출력한 뒤 카메라로 사진을 촬영하고, YOLO 모델로 물체를 인식해 LCD와 로그에 분리배출 안내를 표시합니다.

## 주요 기능

1. PIR 센서로 사용자 접근 또는 움직임 감지
2. 초음파 센서로 물체가 판 위에 안정적으로 놓였는지 확인
3. LCD에 `3`, `2`, `1` 카운트다운 출력
4. Pi Camera로 이미지 촬영
5. YOLO 모델로 물체 인식
6. 물체 종류에 따라 재활용 안내 메시지 출력
7. 촬영 이미지, YOLO 결과 이미지, 이벤트 로그 저장
8. 센서가 아직 없어도 mock 모드로 전체 흐름 테스트 가능

## 프로젝트 구조

```text
IoT26_Team_project/
  project/
    main.py
    config.toml
    README.md
    smart_recycling/
      app.py
      config.py
      camera/
        pi_camera.py
      display/
      sensors/
      storage/
      vision/
  test/
    test_camera.py
    test_model.py
    test_lcd.py
    test_motion.py
    test_ultrasonic.py
    run_once.py
```

## 동작 흐름

```text
대기
  -> PIR 움직임 감지
  -> 초음파 거리 측정
  -> 기준 거리 이하인지 확인
  -> 거리값이 일정 시간 안정적인지 확인
  -> LCD 카운트다운
  -> 카메라 촬영
  -> YOLO 추론
  -> 재활용 안내 출력
  -> 이벤트 로그 저장
  -> 쿨타임 후 다시 대기
```

PIR만 감지되었다고 바로 촬영하지 않습니다. 초음파 센서 거리값이 `config.toml`의 기준 안에 들어오고, 흔들림이 적은 상태로 `stable_required_seconds` 동안 유지될 때만 촬영합니다.

## 빠른 실행

라즈베리파이에서 프로젝트 폴더로 이동합니다.

```sh
cd ~/IoT26_Team_project/project
```

카메라와 YOLO만 한 번 테스트합니다. PIR, 초음파, LCD가 없어도 실행됩니다.

```sh
python3 main.py --once --no-lcd
```

센서가 아직 없을 때 전체 흐름을 가짜 센서로 테스트합니다.

```sh
python3 main.py --mock-sensors --no-lcd
```

실제 PIR, 초음파 센서, LCD까지 연결한 뒤 통합 실행합니다.

```sh
python3 main.py
```

## 개별 테스트 명령

카메라 테스트:

```sh
python3 ../test/test_camera.py
```

YOLO 모델 테스트:

```sh
python3 ../test/test_model.py
```

LCD 테스트:

```sh
python3 ../test/test_lcd.py --message "AIoT Ready" --line2 "LCD test"
```

PIR 센서 테스트:

```sh
python3 ../test/test_motion.py --seconds 15
```

초음파 센서 테스트:

```sh
python3 ../test/test_ultrasonic.py --seconds 15
```

## 기본 설정

설정 파일은 `config.toml`입니다.

```toml
[app]
stable_required_seconds = 1.2

[sensors.pir]
enabled = true
pin = 17

[sensors.ultrasonic]
enabled = true
trigger_pin = 23
echo_pin = 24
object_distance_cm = 18.0
stable_tolerance_cm = 2.5

[lcd]
bus = 1
addresses = ["0x27", "0x3f"]

[yolo]
model = "yolov8n.pt"
confidence = 0.35

[sensors.temp_humidity]
pin = 4        

[sensors.bin_ultrasonic]
trigger_pin = 25
echo_pin = 8
bin_depth_cm = 40.0
full_threshold_cm = 10.0

[firebase]
enabled = true
url = "https://smarttrash-dbf88-default-rtdb.asia-southeast1.firebasedatabase.app/"
timeout_seconds = 5.0
min_interval_seconds = 5.0
```

## 라즈베리파이 핀 번호 기준

- BCM GPIO 번호: 코드에서 사용하는 번호입니다. 예: `GPIO17`
- 물리 핀 번호: 라즈베리파이 보드의 실제 40핀 위치입니다. 예: `physical pin 11`

코드와 `config.toml`에는 BCM 번호를 사용합니다.

## 전체 배선 요약

| 부품 | 부품 핀 | 라즈베리파이 연결 | 설명 |
| --- | --- | --- | --- |
| PIR 센서 | VCC | 5V, physical pin 2 또는 4 | 센서 전원 |
| PIR 센서 | GND | GND, physical pin 6 등 | 공통 접지 |
| PIR 센서 | OUT | GPIO17, physical pin 11 | 움직임 감지 신호 |
| HC-SR04 | VCC | 5V, physical pin 2 또는 4 | 센서 전원 |
| HC-SR04 | GND | GND, physical pin 6 등 | 공통 접지 |
| HC-SR04 | TRIG | GPIO23, physical pin 16 | 초음파 발신 트리거 |
| HC-SR04 | ECHO | GPIO24, physical pin 18 | 전압 분배 후 입력 |
| I2C LCD | VCC | 5V, physical pin 2 또는 4 | LCD 전원 |
| I2C LCD | GND | GND, physical pin 6 등 | 공통 접지 |
| I2C LCD | SDA | GPIO2/SDA, physical pin 3 | I2C 데이터 |
| I2C LCD | SCL | GPIO3/SCL, physical pin 5 | I2C 클럭 |
| I2C LCD | LED+ 또는 LED A | 5V 또는 220Ω 거쳐 5V | 백라이트 양극 |
| I2C LCD | LED- 또는 LED K | GND | 백라이트 음극 |

모든 센서의 GND는 라즈베리파이 GND와 반드시 공통으로 연결해야 합니다.

## PIR 센서 연결

PIR 센서는 사람이나 물체 움직임을 감지하는 역할입니다. 이 프로젝트에서는 PIR 감지를 시스템 시작 신호로 사용합니다.

| PIR 핀 | 연결 |
| --- | --- |
| VCC | Raspberry Pi 5V, physical pin 2 또는 4 |
| GND | Raspberry Pi GND, physical pin 6, 9, 14, 20, 25, 30, 34, 39 중 하나 |
| OUT | Raspberry Pi GPIO17, physical pin 11 |

테스트:

```sh
cd ~/IoT26_Team_project/project
python3 ../test/test_motion.py --seconds 15
```

손을 센서 앞에서 움직였을 때 `motion=1`이 나오면 정상입니다.

## 초음파 센서 HC-SR04 연결

초음파 센서는 물체가 실제로 판 위에 올라왔는지 확인하는 역할입니다. PIR만 사용하면 사람이 지나가기만 해도 촬영될 수 있으므로, 초음파 거리값으로 한 번 더 확인합니다.

| HC-SR04 핀 | 연결 |
| --- | --- |
| VCC | Raspberry Pi 5V, physical pin 2 또는 4 |
| GND | Raspberry Pi GND |
| TRIG | Raspberry Pi GPIO23, physical pin 16 |
| ECHO | 전압 분배 후 Raspberry Pi GPIO24, physical pin 18 |

주의: HC-SR04의 ECHO 핀은 5V 신호입니다. 라즈베리파이 GPIO는 3.3V만 안전합니다. ECHO를 GPIO에 바로 연결하면 라즈베리파이가 손상될 수 있습니다.

### ECHO 전압 분배 연결

저항 2개를 사용해 5V ECHO 신호를 약 3.3V로 낮춥니다.

추천 저항:

- R1: 1k ohm
- R2: 2k ohm 또는 2.2k ohm

연결:

```text
HC-SR04 ECHO ---- R1(1k) ----+---- Raspberry Pi GPIO24, physical pin 18
                             |
                            R2(2k 또는 2.2k)
                             |
                            GND
```

TRIG는 라즈베리파이에서 센서로 나가는 신호라서 GPIO23에서 TRIG로 바로 연결해도 됩니다. 위험한 쪽은 센서에서 라즈베리파이로 들어오는 ECHO입니다.

테스트:

```sh
cd ~/IoT26_Team_project/project
python3 ../test/test_ultrasonic.py --seconds 15
```

출력 예시:

```text
[ultrasonic] trig=23 echo=24 distance_cm=12.4
```

물체를 가까이 가져가면 거리값이 줄고, 멀리 두면 커져야 정상입니다.

## I2C LCD 연결

일반적인 16x2 I2C LCD 모듈 기준입니다. LCD 뒤에 작은 I2C 백팩 보드가 붙어 있고 기본 통신 핀이 `GND`, `VCC`, `SDA`, `SCL`이라면 이 방식입니다.

| LCD 핀 | 연결 |
| --- | --- |
| GND | Raspberry Pi GND |
| VCC | Raspberry Pi 5V |
| SDA | Raspberry Pi GPIO2/SDA, physical pin 3 |
| SCL | Raspberry Pi GPIO3/SCL, physical pin 5 |

사용 중인 LCD처럼 `LED` 핀이 두 개 더 있는 경우, 그 두 핀은 보통 LCD 백라이트 전원입니다. 보드 표기가 `LED+`, `LED-`, `A`, `K`처럼 되어 있다면 아래처럼 연결합니다.

| LCD 백라이트 핀 | 연결 |
| --- | --- |
| LED+ 또는 A | Raspberry Pi 5V |
| LED- 또는 K | Raspberry Pi GND |

백라이트가 너무 밝거나 모듈에 전류 제한 저항이 있는지 확실하지 않다면 `LED+`와 5V 사이에 220 ohm 저항을 하나 넣습니다.

```text
Raspberry Pi 5V ---- 220Ω ---- LCD LED+
Raspberry Pi GND -------------- LCD LED-
```

두 핀이 둘 다 그냥 `LED`라고만 적혀 있고 +/− 구분이 없다면 바로 5V와 GND를 꽂지 않는 것이 안전합니다. 먼저 `GND`, `VCC`, `SDA`, `SCL` 네 개만 연결해서 LCD 통신 테스트를 하고, 백라이트는 모듈 뒷면 표기, 판매 페이지, 데이터시트, 또는 멀티미터 다이오드 모드로 극성을 확인한 뒤 연결합니다.

LCD 글자는 출력되는데 화면이 어둡다면 백라이트 LED만 연결되지 않은 상태일 수 있습니다. 반대로 LCD 백라이트만 켜지고 글자가 안 나오면 `SDA`, `SCL`, I2C 주소, 또는 LCD 대비 조절 가변저항을 확인합니다.

I2C 장치 확인:

```sh
ls /dev/i2c*
```

`/dev/i2c-1`이 없으면 I2C가 비활성화된 상태일 수 있습니다.

현재처럼 `/dev/i2c-10`, `/dev/i2c-13`, `/dev/i2c-14`, `/dev/i2c-6`만 보이고 `/dev/i2c-1`이 없다면 LCD 배선보다 라즈베리파이 I2C 설정 문제일 가능성이 큽니다. GPIO 헤더의 `SDA`/`SCL`은 보통 `/dev/i2c-1`로 잡혀야 합니다.

I2C 활성화:

```sh
sudo raspi-config nonint do_i2c 0
sudo reboot
```

재부팅 후 다시 확인:

```sh
ls /dev/i2c*
i2cdetect -y 1
```

`i2cdetect -y 1` 결과에서 `27` 또는 `3f` 같은 주소가 보이면 LCD가 I2C 장치로 잡힌 것입니다.

I2C 주소 확인:

```sh
i2cdetect -y 1
```

보통 LCD 주소는 `0x27` 또는 `0x3f`입니다. 이 프로젝트는 두 주소를 순서대로 자동 시도합니다.

LCD 테스트:

```sh
cd ~/IoT26_Team_project/project
python3 ../test/test_lcd.py --message "AIoT Ready" --line2 "LCD test"
```

참고: 일반 16x2 LCD는 한글 표시가 거의 안 됩니다. 그래서 실제 LCD 출력 문구는 영어로 구성했습니다.

## Pi Camera 연결

Pi Camera는 라즈베리파이 CSI 카메라 포트에 연결합니다.

1. 라즈베리파이 전원을 끕니다.
2. 카메라 리본 케이블을 CSI 포트에 꽂습니다.
3. 케이블 방향을 확인합니다. 은색 접점 방향이 보드/카메라 모델에 따라 다를 수 있으므로, 카메라가 인식되지 않으면 방향을 다시 확인합니다.
4. 라즈베리파이를 다시 켭니다.
5. 카메라 목록을 확인합니다.

```sh
rpicam-hello --list-cameras
```

정상 출력 예시:

```text
Available cameras
0 : ov5647 [...]
```

카메라 촬영 테스트:

```sh
cd ~/IoT26_Team_project/project
python3 ../test/test_camera.py
```

촬영 이미지는 `~/Pictures/aiot-smart-recycling/`에 저장됩니다.

## 통합 실행 전 체크리스트

1. 카메라가 `rpicam-hello --list-cameras`에서 보이는지 확인
2. `python3 ../test/test_camera.py` 성공 확인
3. PIR 센서에서 `motion=1`이 나오는지 확인
4. 초음파 센서 거리값이 정상적으로 변하는지 확인
5. LCD에 테스트 문구가 출력되는지 확인
6. `config.toml`의 거리 기준이 실제 판 높이와 맞는지 확인

## 실제 실행

센서와 LCD가 모두 연결된 상태:

```sh
cd ~/IoT26_Team_project/project
python3 main.py
```

동작 중 출력 예시:

```text
[INFO] System ready. Press Ctrl-C to stop.
[INFO] Motion detected. Checking target area.
[SENSOR] distance=12.0cm near=True steady=True
[DISPLAY] Item detected | 12.0 cm
[DISPLAY] Hold still | Capture in 3
[DISPLAY] Hold still | Capture in 2
[DISPLAY] Hold still | Capture in 1
[DISPLAY] AI checking | Please wait
[RESULT] Bottle / Check PET
```

## 거리 기준 조정

초음파 센서가 판 위 물체를 감지하는 기준은 `config.toml`에서 조정합니다.

```toml
[sensors.ultrasonic]
object_distance_cm = 18.0
stable_tolerance_cm = 2.5
```

- `object_distance_cm`: 이 거리보다 가까우면 물체가 있다고 판단합니다.
- `stable_tolerance_cm`: 거리값 흔들림 허용 범위입니다.
- `stable_required_seconds`: 안정 상태가 유지되어야 하는 시간입니다. 이 값은 `[app]` 섹션에 있습니다.

예를 들어 판이 센서에서 25cm 아래에 있고, 쓰레기를 올렸을 때 12cm 정도가 나온다면 `object_distance_cm = 18.0` 정도가 적당합니다.

## YOLO 모델과 분류 한계

현재는 커스텀 모델을 학습하지 않고 `yolov8n.pt`를 사용합니다. 이 모델은 COCO 데이터셋 기반이라 다음과 같은 일반 물체는 어느 정도 인식합니다.

- `bottle`
- `cup`
- `book`
- `cell phone`
- `laptop`

하지만 `plastic`, `metal can`, `paper waste`처럼 재활용 재질을 정확히 분류하는 전용 모델은 아닙니다. 따라서 최종 시연에서는 YOLO가 잘 인식하는 물체를 사용하고, `smart_recycling/vision/recycling_rules.py`에서 해당 물체를 재활용 안내로 매핑합니다.

분류 안내 규칙 파일:

```text
smart_recycling/vision/recycling_rules.py
```

예시:

```python
"bottle": RecyclingAdvice("plastic", "Bottle", "Check PET", "If it is PET, remove cap/label and rinse.")
```


```toml
[yolo]
model = "best.pt"
```

## 저장되는 결과물

촬영 이미지:

```text
~/Pictures/aiot-smart-recycling/capture_YYYYMMDD_HHMMSS.jpg
```

YOLO 결과 이미지:

```text
~/Pictures/aiot-smart-recycling/annotated_YYYYMMDD_HHMMSS.jpg
```

이벤트 로그:

```text
~/IoT26_Team_project/project/events.jsonl
```

로그 확인:

```sh
tail -5 ~/IoT26_Team_project/project/events.jsonl
```
## 라즈베리파이 파이어베이스 설치

```sh
pip install firebase-admin --break-system-packages
```

## 설치 관련 주의

라즈베리파이 저장 공간이 부족할 수 있으므로 `ultralytics`를 전체 재설치하지 않는 것이 좋습니다. 현재 프로젝트는 이미 설치된 패키지를 재사용합니다.

작은 의존성이 하나 빠졌을 때만 아래처럼 최소 설치합니다.

```sh
python3 -m pip install --user --break-system-packages --no-cache-dir --no-deps PACKAGE_NAME
```

## 문제 해결

카메라가 안 보일 때:

```sh
rpicam-hello --list-cameras
```

`No cameras available`이 나오면 전원을 끄고 리본 케이블 방향을 다시 확인한 뒤 재부팅합니다.

LCD가 안 보일 때:

```sh
ls /dev/i2c*
i2cdetect -y 1
```

`/dev/i2c-1`이 없으면 I2C 활성화가 필요합니다.

초음파 값이 계속 `None`일 때:

1. TRIG/ECHO 핀이 `config.toml`과 맞는지 확인
2. GND가 공통으로 연결되어 있는지 확인
3. ECHO 전압 분배 연결이 맞는지 확인
4. 물체와 센서가 너무 가깝거나 너무 멀지 않은지 확인

PIR이 계속 감지될 때:

1. 센서 앞 움직임이 없는지 확인
2. 센서의 감도/지연 가변저항을 조정
3. 테스트 시간을 늘려 안정화 대기

커스텀 모델을 만들지 않는 경우, 시연 물체는 `bottle`처럼 COCO YOLO가 잘 인식하는 물체를 사용하는 것이 안정적입니다.
