

# Only use _import_or_exit for simple imports
def _import_or_exit(module, pip_name=None):
    try:
        return __import__(module)
    except ImportError:
        pkg = pip_name if pip_name else module
        print(f"\n[ERROR] Required package '{pkg}' is not installed.\nPlease install it with: pip install {pkg}\n")
        exit(1)

os = _import_or_exit('os')
random = _import_or_exit('random')

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("\n[ERROR] Required package 'Pillow' is not installed.\nPlease install it with: pip install Pillow\n")
    exit(1)
try:
    from torchvision import transforms
except ImportError:
    print("\n[ERROR] Required package 'torchvision' is not installed.\nPlease install it with: pip install torchvision\n")
    exit(1)
try:
    import torchvision
except ImportError:
    print("\n[ERROR] Required package 'torchvision' is not installed.\nPlease install it with: pip install torchvision\n")
    exit(1)
try:
    from tqdm import tqdm
except ImportError:
    print("\n[ERROR] Required package 'tqdm' is not installed.\nPlease install it with: pip install tqdm\n")
    exit(1)

# Config
data_dir = "data"

def add_occlusion(img):
    draw = ImageDraw.Draw(img)
    for _ in range(random.randint(1, 2)):
        x1 = random.randint(0, img.width - 20)
        y1 = random.randint(0, img.height - 20)
        x2 = x1 + random.randint(20, 60)
        y2 = y1 + random.randint(10, 30)
        draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))
    return img

#Augmentation transforms
transform_base = transforms.Compose([
    transforms.RandomResizedCrop(size=(160, 160), scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=30),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.05),
    transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), shear=10),
    transforms.GaussianBlur(kernel_size=(3, 5), sigma=(0.1, 2.0)),
])

# Loop through each person's folder
for person in os.listdir(data_dir):
    person_path = os.path.join(data_dir, person)
    if not os.path.isdir(person_path):
        continue

    # Process each image
    for file in tqdm(os.listdir(person_path), desc=f"Processing {person}"):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        if "_aug" in file:
            continue  #skip already augmented

        img_path = os.path.join(person_path, file)
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"Failed to open {img_path}: {e}")
            continue

        filename_base = os.path.splitext(file)[0]
        for i in range(5):
            aug_img = transform_base(img)
            aug_img = add_occlusion(aug_img)
            aug_filename = f"{filename_base}_aug{i}.jpg"
            aug_img.save(os.path.join(person_path, aug_filename))

print("All augmentation done. Your image data has been increased successfully")





