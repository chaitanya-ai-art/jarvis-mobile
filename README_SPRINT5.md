# Jarvis Sprint 5 - Voice Assistant

Version 7.4.0 adds phone push-to-talk and spoken replies using the browser speech APIs.

## Features
- Push-to-talk microphone button
- Live interim transcript
- Automatic sending after final recognition
- Spoken Jarvis replies
- English (India), Telugu, and Hindi voice language selection
- Speak replies toggle saved on the phone
- Test voice and stop speaking controls
- Voice commands use the same WebSocket, memory, conversation log, and Windows automation path as typed commands

## Important browser limitation
Chrome may require microphone permission. Browser speech recognition can depend on the device/browser speech service and is not guaranteed to work fully offline. Jarvis still supports text input whenever voice is unavailable.

## Install
1. Stop Jarvis with Ctrl+C.
2. Extract this ZIP.
3. Run INSTALL_SPRINT5.bat.
4. Restart D:\Jarvis\START_JARVIS_V7.bat.
5. Close the old phone tab and open the new exact PHONE APP URL.
6. Tap the microphone and allow microphone permission.
