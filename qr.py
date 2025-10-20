import qrcode

# 1. Define the link you want in the QR code
link_to_encode = "https://cwf8nj4f-5000.uks1.devtunnels.ms/"  # <-- Put your own link here!

# 2. Create the QR code image
# You can adjust box_size (how big each "pixel" is) and border (how thick the white edge is)
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# 3. Add the data (your link) to the QR code
qr.add_data(link_to_encode)
qr.make(fit=True)

# 4. Create the image file (using PIL/Pillow)
img = qr.make_image(fill_color="black", back_color="white")

# 5. Save the image to a file
img.save("my_qr_code.png")

print(f"Successfully created QR code and saved it as 'my_qr_code.png'")