#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install torch torchvision Pillow


# In[41]:


import os
import torch
from torchvision import transforms
from PIL import Image,ImageDraw
import random


# In[43]:


image_path="Sample_image.jpg"
image= Image.open(image_path).convert("RGB")


# In[45]:


output_folder = "C:/Users/Pearl Narang/Desktop/augment"
os.makedirs(output_folder, exist_ok=True)


# In[47]:


def add_occlusion(img):
    draw=ImageDraw.Draw(img)
    for _ in range(random.randint(1,2)):
        x1=random.randint(0,img.width-20)
        y1=random.randint(0,img.height-20)
        x2=x1+random.randint(20,60)
        y2=y1+random.randint(10,30)
        draw.rectangle([x1,y1,x2,y2], fill=(0,0,0))
    return img


# In[49]:


transform_base=transforms.Compose([
    transforms.RandomResizedCrop(size=image.size, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=30),
    transforms.ColorJitter(brightness=0.3,contrast=0.3,saturation=0.3,hue=0.05),
    transforms.RandomAffine(degrees=0,translate=(0.05,0.05),shear=10),
    transforms.GaussianBlur(kernel_size=(3, 5), sigma=(0.1, 2.0)),
])

for i in range(50):
    img_aug=transform_base(image)
    img_aug=add_occlusion(img_aug)
    img_aug.save(os.path.join(output_folder, f"aug_{i}.jpg"))
print("50 augmented images saved to:", output_folder)


# In[53]:


pip install nbcovert


# In[55]:


jupyter nbconvert Data_Augmentation.ipynb --to python


# In[ ]:




