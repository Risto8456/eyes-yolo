# 基於 YOLOv11 的視線偵測（Eye & Pupil Detection）

本專案使用 **YOLOv11** 訓練眼睛（eye）與瞳孔（pupil）偵測模型，並支援 TensorRT 匯出與即時攝影機測試。

# 一、 TensorRT 環境與設備簡易說明

本專案使用 **Ultralytics YOLO11 + TensorRT + 攝影機即時推論**，目標平台為 **NVIDIA Jetson Orin Nano（JetPack 6.x）**，用於高效能、低延遲的即時視線偵測。

---

## 整體架構說明

```
攝影機
  ↓
YOLO11 (Ultralytics)
  ↓  PyTorch (訓練 / 測試)
TensorRT (Engine / trtexec)
  ↓
Jetson Orin Nano GPU (CUDA)
```

* **YOLO11**：負責物件偵測（eye / pupil）
* **PyTorch**：模型訓練與開發階段推論
* **TensorRT**：將模型轉為高效能 Engine，加速推論
* **Jetson Orin Nano**：邊緣運算裝置，負責即時推論

---

## 前置條件（系統層）

Jetson Orin Nano 已完成 **JetPack 6.x** 安裝，系統內已包含：

* CUDA（GPU 運算）
* cuDNN（深度學習加速）
* TensorRT 10.3（推論最佳化）

這些元件都屬於 **系統層套件**，安裝在 `/usr/lib/...`，不是 Python venv 的一部分。


# 二、資料集


# 三、訓練

## 1. 原始資料集結構

解壓縮後共有 **37,600 組圖片與標註**：

```text
boundingBox_jpg
├── images/        原始圖片 (.jpg)
├── labels/        標註檔案 (.txt)  
└── classes.txt    說明文件 (非必要)
```

---

## 2. 更新資料集結構（Train / Val Split）

使用 `split_train_val.py` 依 **9 : 1** 分配訓練集與驗證集：

```text
boundingBox_jpg/
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
├── split_train_val.py
└── eyes.yaml
```

---

## 3. eyes.yaml 設定

```yaml
path: /home/jetbot/final/boundingBox_jpg

train: images/train
val: images/val

names:
  0: eye
  1: pupil
```

---

## 4. 模型訓練

### 訓練指令
* 約 **30 分鐘 / epoch**
* 20 epochs 約 **10 小時**

```bash
yolo train \
  model=yolo11n.pt \
  data=eyes.yaml \
  epochs=20 \
  patience=5 \
  imgsz=512 \
  batch=4 \
  workers=1 \
  device=0 \
  amp=False \
  freeze=15 \
  cache=False
```

---

### 4.3 接續被中斷的訓練

```bash
yolo train \
  model=runs/detect/train3/weights/last.pt \
  data=eyes.yaml \
  resume=True
```

---

## 5.（補充）tmux 常用指令

```bash
tmux attach -t yolo_train
```

| 動作         | 指令                        |
| ---------- | ------------------------- |
| 開新 session | `tmux new -s 名稱`          |
| 離開不中斷      | `Ctrl + B → D`            |
| 列出 session | `tmux ls`                 |
| 回到 session | `tmux attach -t 名稱`       |
| 刪除 session | `tmux kill-session -t 名稱` |

---

## 6. 匯出 TensorRT（Engine）

模型來源：

```
/home/jetbot/final/boundingBox_jpg/runs/detect/train3/weights/best.pt
```

```bash
workon pt
cd /home/jetbot/final/boundingBox_jpg/runs/detect/train3/weights

yolo export \
  model=best.pt \
  format=engine \
  imgsz=512 \
  batch=1 \
  half=True \
  device=0
```

---

## 7. 影片測試

```bash
yolo predict \
  model=runs/detect/train3/weights/best.engine \
  source=eyes_test.mp4 \
  device=0 \
  half=True
```

---

## 8. 攝影機即時測試

```bash
workon pt
cd /home/jetbot/final/boundingBox_jpg

yolo predict \
  model=runs/detect/train3/weights/best.engine \
  source=0 \
  show=True \
  device=0 \
  half=True
```

---

**完成後即可使用 TensorRT 模型進行即時視線（眼睛 / 瞳孔）偵測**
