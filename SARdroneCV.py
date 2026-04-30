from ultralytics import YOLO
import cv2

# model
model = YOLO('C:/Users/youruserprofliehere/runs/detect/train2/weights/best.pt')

cap = cv2.VideoCapture(0)

# set camera resolution, figure out changing later
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting live detection... Press 'q' to quit")

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break
    
# Run YOLO inference
    results = model(frame, conf=0.4, classes=[0, 1])

# Check if results is not empty
    if len(results) == 0:
        print("No results from model")
        continue

    # Draw bounding boxes on frame
    annotated_frame = results[0].plot()  # Fixed: use results

    # Display frame
    cv2.imshow('YOLO11 Live Detection', annotated_frame)
    
    # Print detections
    for result in results:
        if len(result.boxes) > 0:
            print(f"Detected {len(result.boxes)} objects")
            for box in result.boxes:
                cls = int(box.cls)
                conf = float(box.conf)
                print(f"  {model.names[cls]}: {conf:.2f}")
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
