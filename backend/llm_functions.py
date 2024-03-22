import google.generativeai as genai
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from google.api_core import exceptions

def get_gemini_response(input, image, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([input, image[0], prompt])
        return response.text
    except exceptions.RetryError as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with the LLM service: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

def input_image_details(uploaded_file: UploadFile):
    if uploaded_file is not None:
        try:
            # Open the image using PIL directly from the UploadFile
            image = Image.open(uploaded_file.file)
            # Convert the image to bytes
            bytes_io = BytesIO()
            image.save(bytes_io, format=image.format)
            bytes_data = bytes_io.getvalue()
            image_parts = [
                {
                    "mime_type": uploaded_file.content_type,  # Get the mime type
                    "data": bytes_data
                }
            ]
            return image_parts
        except UnidentifiedImageError:
            raise HTTPException(status_code=400, detail="Invalid image file")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    else:
        raise FileNotFoundError('No file uploaded')