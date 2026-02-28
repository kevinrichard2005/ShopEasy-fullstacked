import os
import urllib.request

os.makedirs('e:/shopeasy/static/images', exist_ok=True)
url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/200px-QR_code_for_mobile_English_Wikipedia.svg.png'
urllib.request.urlretrieve(url, 'e:/shopeasy/static/images/payment_qr.png')
print("Downloaded successfully.")
