

# Only use _import_or_exit for simple imports
def _import_or_exit(module, pip_name=None):
    try:
        return __import__(module)
    except ImportError:
        pkg = pip_name if pip_name else module
        print(f"\n[ERROR] Required package '{pkg}' is not installed.\nPlease install it with: pip install {pkg}\n")
        exit(1)

os = _import_or_exit('os')
pickle = _import_or_exit('pickle')
face_recognition = _import_or_exit('face_recognition')

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
