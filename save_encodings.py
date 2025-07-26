# save_encodings.py
import os
import pickle
import face_recognition

data_path = "data/"
encodings_path = "encodings/face_encodings.pkl"

face_encodings = []
face_names = []

for person_name in os.listdir(data_path):
    person_folder = os.path.join(data_path, person_name)
    if os.path.isdir(person_folder):
        for file in os.listdir(person_folder):
            if file.lower().endswith(("jpg", "jpeg", "png")):
                img_path = os.path.join(person_folder, file)
                img = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(img)
                if encodings:
                    face_encodings.append(encodings[0])
                    face_names.append(person_name)

# Save encodings
os.makedirs("encodings", exist_ok=True)
with open(encodings_path, "wb") as f:
    pickle.dump((face_encodings, face_names), f)

print(f"✅ Encodings saved to {encodings_path}")
