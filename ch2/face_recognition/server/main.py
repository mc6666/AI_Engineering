from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
from loguru import logger

app = FastAPI(
    title="Face Detection API",
    description="Detect faces using OpenCV Haar Cascade",
    version="1.0"
)

# Load Haar Cascade once during startup
FACE_CASCADE = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)

if FACE_CASCADE.empty():
    raise RuntimeError(
        "Failed to load haarcascade_frontalface_default.xml"
    )


@app.get("/")
def root():
    return {
        "message": "Face Detection API is running"
    }


@app.post("/detect")
async def detect_face(file: UploadFile = File(...)):
    """
    Upload an image and receive the image
    with face bounding boxes.
    """

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be an image"
        )

    contents = await file.read()

    np_arr = np.frombuffer(contents, np.uint8)

    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Unable to decode image"
        )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = FACE_CASCADE.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    logger.debug(f'no of faces:{len(faces)}')
    for (x, y, w, h) in faces:
        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    success, encoded_img = cv2.imencode(".jpg", image)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to encode output image"
        )

    return StreamingResponse(
        io.BytesIO(encoded_img.tobytes()),
        media_type="image/jpeg",
        headers={
            "Faces-Detected": str(len(faces))
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )