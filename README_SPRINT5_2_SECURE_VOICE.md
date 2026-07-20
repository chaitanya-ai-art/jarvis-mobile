# Jarvis Sprint 5.2 - Secure Voice

This update fixes Android Chrome `Voice error: not-allowed` caused by opening Jarvis through an insecure HTTP LAN address.

## Install

1. Stop Jarvis with `Ctrl+C`.
2. Run `INSTALL_SPRINT5_2_SECURE_VOICE.bat` from the update folder.
3. Start `D:\Jarvis\START_JARVIS_SECURE_VOICE.bat`.
4. On the PC, open `D:\Jarvis\certs\jarvis-ca.crt` and copy it to the phone.
5. On Oppo/Android, install it as a **CA certificate** under Security / Credential storage. Android may require a screen lock.
6. Open the exact `https://.../mobile?token=...` PHONE APP URL printed by Jarvis in Google Chrome.
7. Allow microphone permission and tap the microphone.

Test: say **Open Excel**.

## Important

Do not use the old `http://...` address for voice. Text and buttons can work over HTTP, but Android Chrome blocks microphone recognition on insecure pages.
