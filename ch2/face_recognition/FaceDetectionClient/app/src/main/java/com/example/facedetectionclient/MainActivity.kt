package com.example.facedetectionclient

import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.text.method.ScrollingMovementMethod
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.IOException
import java.io.FileOutputStream

class MainActivity : AppCompatActivity() {
    private val apiUrl = "http://192.168.1.105:8000/detect"
    private val uploadPartName = "file"
    private val client = OkHttpClient()

    private lateinit var captureButton: Button
    private lateinit var selectButton: Button
    private lateinit var uploadButton: Button
    private lateinit var backButton: Button
    private lateinit var captureContainer: View
    private lateinit var resultContainer: View
    private lateinit var capturedImageView: ImageView
    private lateinit var resultImageView: ImageView
    private lateinit var statusTextView: TextView
    private lateinit var resultTextView: TextView
    private lateinit var progressBar: ProgressBar

    private var currentPhotoFile: File? = null
    private var currentPhotoUri: Uri? = null

    private val takePicture = registerForActivityResult(ActivityResultContracts.TakePicture()) { success ->
        if (success) {
            showCapturedImage()
            setStatus("Photo captured. Upload when ready.")
            uploadButton.isEnabled = true
        } else {
            setStatus("Camera canceled.")
        }
    }

    private val selectImage = registerForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        if (uri == null) {
            setStatus("Selection canceled.")
            return@registerForActivityResult
        }

        try {
            currentPhotoFile = copyUriToCacheFile(uri)
            currentPhotoUri = null
            showCapturedImage()
            uploadButton.isEnabled = true
            setStatus("Image selected. Upload when ready.")
        } catch (e: Exception) {
            setStatus("Failed to read image: ${e.message ?: e::class.java.simpleName}")
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        captureButton = findViewById(R.id.captureButton)
        selectButton = findViewById(R.id.selectButton)
        uploadButton = findViewById(R.id.uploadButton)
        backButton = findViewById(R.id.backButton)
        captureContainer = findViewById(R.id.captureContainer)
        resultContainer = findViewById(R.id.resultContainer)
        capturedImageView = findViewById(R.id.capturedImageView)
        resultImageView = findViewById(R.id.resultImageView)
        statusTextView = findViewById(R.id.statusTextView)
        resultTextView = findViewById(R.id.resultTextView)
        progressBar = findViewById(R.id.progressBar)

        statusTextView.movementMethod = ScrollingMovementMethod()
        resultTextView.movementMethod = ScrollingMovementMethod()

        captureButton.setOnClickListener { launchCamera() }
        selectButton.setOnClickListener { selectImage.launch("image/*") }
        uploadButton.setOnClickListener { uploadCurrentPhoto() }
        backButton.setOnClickListener { showCaptureView() }
        uploadButton.isEnabled = false

        if (savedInstanceState != null) {
            restoreState(savedInstanceState)
        } else {
            showCaptureView()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString(KEY_PHOTO_PATH, currentPhotoFile?.absolutePath)
    }

    private fun restoreState(savedInstanceState: Bundle) {
        savedInstanceState.getString(KEY_PHOTO_PATH)?.let { path ->
            val file = File(path)
            if (file.exists()) {
                currentPhotoFile = file
                currentPhotoUri = FileProvider.getUriForFile(
                    this,
                    "${packageName}.fileprovider",
                    file,
                )
                showCapturedImage()
                uploadButton.isEnabled = true
            }
        }
    }

    private fun launchCamera() {
        val photoFile = createImageFile()
        currentPhotoFile = photoFile
        val photoUri = FileProvider.getUriForFile(
            this,
            "${packageName}.fileprovider",
            photoFile,
        )
        currentPhotoUri = photoUri
        takePicture.launch(photoUri)
        setStatus("Opening camera...")
    }

    private fun copyUriToCacheFile(uri: Uri): File {
        val imagesDir = File(cacheDir, "images")
        if (!imagesDir.exists()) {
            imagesDir.mkdirs()
        }

        val outputFile = File(imagesDir, "selected_${System.currentTimeMillis()}.jpg")
        contentResolver.openInputStream(uri).use { input ->
            if (input == null) {
                throw IOException("Unable to open selected image")
            }
            FileOutputStream(outputFile).use { output ->
                input.copyTo(output)
            }
        }
        return outputFile
    }

    private fun uploadCurrentPhoto() {
        val photoFile = currentPhotoFile
        if (photoFile == null || !photoFile.exists()) {
            setStatus("Capture a photo first.")
            return
        }

        lifecycleScope.launch {
            setBusy(true, "Uploading to $apiUrl")
            try {
                val result = withContext(Dispatchers.IO) { uploadAndReadResponse(photoFile) }
                renderResponse(result.bytes, result.contentType)
            } catch (e: Exception) {
                setStatus("Upload failed: ${e.message ?: e::class.java.simpleName}")
            } finally {
                setBusy(false, null)
            }
        }
    }

    private fun uploadAndReadResponse(photoFile: File): UploadResult {
        val requestBody = photoFile.asRequestBody("image/jpeg".toMediaType())
        val multipartBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(uploadPartName, photoFile.name, requestBody)
            .build()

        val request = Request.Builder()
            .url(apiUrl)
            .post(multipartBody)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("HTTP ${response.code}: ${response.message}")
            }

            val body = response.body ?: throw IOException("Empty response body")
            return UploadResult(
                bytes = body.bytes(),
                contentType = body.contentType()?.toString().orEmpty(),
            )
        }
    }

    private fun renderResponse(bytes: ByteArray, contentType: String) {
        val lowerType = contentType.lowercase()
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)

        showResultView()

        if (lowerType.startsWith("image/") || bitmap != null) {
            if (bitmap != null) {
                resultImageView.setImageBitmap(bitmap)
                resultImageView.visibility = View.VISIBLE
                resultTextView.text = ""
                resultTextView.visibility = View.GONE
                return
            }
        }

        resultImageView.setImageDrawable(null)
        resultImageView.visibility = View.GONE
        val textPreview = bytes.toString(Charsets.UTF_8)
        resultTextView.visibility = View.VISIBLE
        resultTextView.text = if (textPreview.isBlank()) {
            "Response content-type: $contentType"
        } else {
            textPreview
        }
    }

    private fun showCapturedImage() {
        val file = currentPhotoFile ?: return
        if (!file.exists()) return
        val bitmap = decodeImageFile(file)
        if (bitmap != null) {
            capturedImageView.setImageBitmap(bitmap)
        } else {
            capturedImageView.setImageDrawable(null)
        }
    }

    private fun decodeImageFile(file: File): android.graphics.Bitmap? {
        // Decode the image as-is. Do not apply EXIF orientation correction.
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeFile(file.absolutePath, bounds)

        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) {
            return null
        }

        val options = BitmapFactory.Options().apply {
            inPreferredConfig = android.graphics.Bitmap.Config.ARGB_8888
            inSampleSize = calculateInSampleSize(bounds.outWidth, bounds.outHeight, 2048, 2048)
        }
        return BitmapFactory.decodeFile(file.absolutePath, options)
    }

    private fun calculateInSampleSize(
        sourceWidth: Int,
        sourceHeight: Int,
        reqWidth: Int,
        reqHeight: Int,
    ): Int {
        var sampleSize = 1

        while (sourceWidth / sampleSize > reqWidth || sourceHeight / sampleSize > reqHeight) {
            sampleSize *= 2
        }

        return sampleSize.coerceAtLeast(1)
    }

    private fun createImageFile(): File {
        val imagesDir = File(cacheDir, "images")
        if (!imagesDir.exists()) {
            imagesDir.mkdirs()
        }
        return File(imagesDir, "capture_${System.currentTimeMillis()}.jpg")
    }

    private fun setBusy(isBusy: Boolean, message: String?) {
        progressBar.visibility = if (isBusy) View.VISIBLE else View.GONE
        captureButton.isEnabled = !isBusy
        selectButton.isEnabled = !isBusy
        uploadButton.isEnabled = !isBusy && currentPhotoFile?.exists() == true
        message?.let { setStatus(it) }
    }

    private fun setStatus(message: String) {
        statusTextView.text = message
    }

    private fun showCaptureView() {
        captureContainer.visibility = View.VISIBLE
        resultContainer.visibility = View.GONE
    }

    private fun showResultView() {
        captureContainer.visibility = View.GONE
        resultContainer.visibility = View.VISIBLE
    }

    private data class UploadResult(
        val bytes: ByteArray,
        val contentType: String,
    )

    companion object {
        private const val KEY_PHOTO_PATH = "photo_path"
    }
}
