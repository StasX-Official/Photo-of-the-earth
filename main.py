import requests

API_KEY = " "

url = f"https://api.nasa.gov/EPIC/api/natural/images?api_key={API_KEY}"
response = requests.get(url)
data = response.json()

image_name = data[0]['image']
date = data[0]['date'].split()[0].replace('-', '/')
image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{date}/png/{image_name}.png"

img_data = requests.get(image_url).content
with open("earth.png", "wb") as f:
    f.write(img_data)
    
# BY KOZOSVYST STAS
