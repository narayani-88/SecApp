# Steganography Implementation Explained

## How It Works

Your app uses **LSB (Least Significant Bit) Steganography** to hide encrypted messages inside images. Here's the flow:

### 1. **Sending a Message** (`/send` route)

1. User uploads an image and enters a secret message
2. **Encryption**: The message is encrypted using Fernet (symmetric encryption)
3. **Embedding**: The encrypted data is embedded into the image using LSB steganography:
   - The encrypted bytes are converted to bits
   - Each bit is hidden in the least significant bit of RGB channels
   - The original image looks identical (changes are invisible to the human eye)
4. **Saving**: The stego image (with hidden data) is saved as PNG with no compression
5. **Database**: The file path is stored in MongoDB

### 2. **Viewing a Message** (`/view/<token>` route)

1. User enters the secret code
2. The stego image is displayed (looks like a normal image)
3. JavaScript calls `/api/reveal/<token>` to extract the message

### 3. **Extracting the Message** (`/api/reveal/<token>` route)

1. The stego image is loaded from disk
2. **Extraction**: LSB bits are read from RGB channels
3. Bits are converted back to bytes
4. **Decryption**: The encrypted data is decrypted using Fernet
5. The original message is revealed
6. Image is deleted after viewing

## Key Points

✅ **The stego image looks identical to the original** - that's the point of steganography!
✅ **Data is hidden in pixel values**, not visible in the image
✅ **Only the recipient with the secret code can decrypt** the message
✅ **The image file itself contains the hidden data** - that's correct!

## Verification

To verify steganography is working:

1. **Send a test message** with a known secret text
2. **Check the uploaded file**: `uploads/stego_*.png` should exist
3. **View the message** - it should extract and display correctly
4. **Compare images**: The stego image should look identical to the original (visually)

## Troubleshooting

### "Image just has data, not encrypted"

If you mean the data is visible in the image file:
- ✅ **This is correct!** The data IS in the image file (hidden via LSB)
- The image looks normal, but contains hidden encrypted data
- You can't see the data by looking at the image - it's in the pixel bits

### "Data not being embedded"

Check:
1. Is the stego image being saved? (check `uploads/` folder)
2. Are there any error messages in the logs?
3. Run `python test_steganography.py` to verify the functions work

### "Can't extract the message"

Check:
1. Is the secret code correct?
2. Is the image file still on disk? (it gets deleted after viewing)
3. Check browser console for JavaScript errors
4. Check server logs for extraction errors

## Technical Details

- **LSB Method**: Uses least significant bit of R, G, B channels (3 bits per pixel)
- **Capacity**: ~3 bits per pixel (e.g., 100x100 image = ~3.75 KB of data)
- **Format**: PNG with no compression to preserve exact pixel values
- **Encryption**: Fernet symmetric encryption before embedding
- **Security**: Data is encrypted, then hidden, then requires secret code to decrypt

## Testing

Run the test script:
```bash
python test_steganography.py
```

This will:
1. Create a test image
2. Embed a test message
3. Extract it back
4. Verify it matches

If this test passes, your steganography is working correctly!

