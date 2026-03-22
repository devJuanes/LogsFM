package com.logsfm.radio

import android.annotation.SuppressLint
import android.content.pm.ActivityInfo
import android.graphics.Bitmap
import android.os.Bundle
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var statusText: TextView

    private val baseUrl = "https://radio.logsfm.com"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Lock to portrait mode
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT

        webView = findViewById(R.id.webView)
        progressBar = findViewById(R.id.progressBar)
        statusText = findViewById(R.id.statusText)

        setupWebView()

        // Load the radio page
        webView.loadUrl(baseUrl)

        statusText.text = "Cargando..."
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        val settings = webView.settings

        // Enable JavaScript
        settings.javaScriptEnabled = true

        // Enable DOM storage
        settings.domStorageEnabled = true

        // Enable database
        settings.databaseEnabled = true

        // Allow media playback without user gesture (for autoplay)
        settings.mediaPlaybackRequiresUserGesture = false

        // Enable hardware acceleration
        webView.setLayerType(WebView.LAYER_TYPE_HARDWARE, null)

        // Cache mode
        settings.cacheMode = WebSettings.LOAD_DEFAULT

        // Allow cross-origin requests
        settings.allowUniversalAccessFromFileURLs = true
        settings.allowFileAccessFromFileURLs = true

        // Disable zoom on double tap
        settings.setSupportZoom(false)
        settings.displayZoomControls = false

        // WebViewClient to handle page navigation internally
        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                progressBar.visibility = android.view.View.VISIBLE
                statusText.text = "Cargando..."
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = android.view.View.GONE
                statusText.text = if (view?.url == baseUrl) "Conectado" else "Cargando..."
            }

            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                // Open external links in external browser
                if (url != null && !url.startsWith(baseUrl) && !url.startsWith("https://logsfm.com")) {
                    return false // Let system handle external URLs
                }
                return false // Let WebView handle internal navigation
            }
        }

        // WebChromeClient for progress updates
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                super.onProgressChanged(view, newProgress)
                progressBar.progress = newProgress
            }
        }
    }

    override fun onBackPressed() {
        // Handle back button - go back in WebView if possible
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
