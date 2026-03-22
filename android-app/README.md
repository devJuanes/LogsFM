# Radio Android App

Aplicación Android basada en WebView que carga radio.logsfm.com

## Estructura

```
android-app/
├── app/
│   └── src/
│       └── main/
│           ├── java/com/logsfm/radio/
│           │   └── MainActivity.kt
│           ├── res/
│           │   ├── layout/activity_main.xml
│           │   └── values/colors.xml, strings.xml, styles.xml
│           └── AndroidManifest.xml
├── build.gradle
├── settings.gradle
└── gradle.properties
```

## Instalación

1. Abrir en Android Studio
2. Build > Build APK
3. Instalar en dispositivo/emulator

## Permisos

- INTERNET
- ACCESS_NETWORK_STATE

## Características

- WebView con hardware acceleration
- MediaPlaybackRequiresUserGesture = false para autoplay
- JavaScript habilitado
- Navegación mejorada para links externos
