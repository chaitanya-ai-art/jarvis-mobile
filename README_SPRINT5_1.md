# Jarvis Sprint 5.1 — Command Router

This update connects typed and spoken input to the same safe Windows command router.

## Improvements

- Recognizes `Open Excel` from text and voice.
- Accepts wake-word and polite forms such as `Jarvis, please open Excel`.
- Routes approved commands directly to the Windows agent before normal chat handling.
- Keeps arbitrary shell commands, deletion, registry edits, and installations blocked.
- Returns a spoken confirmation after the action result.

## Supported examples

- Open Excel / Chrome / Edge / Notepad / Calculator / VS Code
- Open Downloads / Documents / Desktop / Pictures / Jarvis
- Find report.xlsx
- System info
- Recent actions
- Lock PC
