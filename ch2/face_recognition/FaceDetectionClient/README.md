# FaceDetectionClient

Android Kotlin client that:

- captures a photo with the device camera app
- uploads the image to `http://192.168.1.105:8000/detect`
- displays the returned image or response text on screen

## Notes

- The upload form field is set to `file` in `MainActivity.kt`. If your backend expects a different multipart field name, change `uploadPartName`.
- The app uses cleartext HTTP because the API URI is not HTTPS.
- Camera capture uses `ActivityResultContracts.TakePicture` and a `FileProvider`.

## Project structure

- `app/src/main/java/com/example/facedetectionclient/MainActivity.kt`
- `app/src/main/res/layout/activity_main.xml`
- `app/src/main/AndroidManifest.xml`

