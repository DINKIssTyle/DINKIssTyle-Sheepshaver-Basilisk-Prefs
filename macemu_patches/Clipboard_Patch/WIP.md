# Clipboard Patch WIP

## Current Status (2026-01-12)
**Host (Linux) -> Mac (Guest) Image Transfer Pipeline is Functional & Verified.**

### Achievements
1.  **Transport Layer Established**: Successfully implemented new Opcode handlers in `emul_op.cpp` (`GET_IMG_SIZE`, `GET_IMG_DATA`).
2.  **"536MB Bug" Resolved**: Fixed the issue where returning large integers via `D0` register resulted in garbage values.
    -   **Solution**: Switched to **Stack-Based Pass-By-Reference**. The Guest passes a pointer, and the Host writes the value directly to memory.
3.  **"Illegal Instruction" Resolved**: Fixed crashes caused by CodeWarrior inline assembly.
    -   **Solution**: Used standard Opcode Function syntax (`= { 0x7131 }`) with C Calling Convention.
4.  **"Out of Memory" Resolved**: Confirmed that increasing the Mac App's memory partition allows loading 1.3MB+ images.
5.  **Data Integrity**: `TestApp` now reports the correct image size (e.g., `Size=1297592`) matching the Host's calculation.
6.  **"Black Image" Resolved**: Fixed issue where copied images appeared black on Mac.
    -   **Cause**: Pixel Format mismatch. Host sent `RGBA`, Mac expected `xRGB`. Mac also lacked a Color Window.
    -   **Solution 1 (Host)**: Changed `libpng` filler to `0xFF` (Opaque) and position to `BEFORE` (`0x00` -> `0xFF`, `ARGB` format).
    -   **Solution 2 (Guest)**: Updated `TestApp` to use `NewCWindow` instead of `NewWindow` to ensure a color-capable environment.

## Next Steps: Mac -> Host Implementation
### 1. Plan
The goal is to allow copying an image in Mac OS (e.g., from Paint) and pasting it into Linux (e.g., GIMP).

### 2. Mac Side (Guest)
-   **Hook into Clipboard**: Enhance `cdev_clipboard.c` (or `TestApp.c` for testing) to detect when PICT data is on the scrap.
-   **Convert PICT to RGB**:
    -   Use `GetScrap` to get PICT handle.
    -   Draw PICT into a GWorld.
    -   Extract RGB pixel data from GWorld (`GetPixBaseAddr`).
-   **Send to Host**:
    -   Call `M68K_EMUL_OP_CLIP_PUT_IMG` (Opcode `0x7133`).
    -   Pass `width`, `height`, `rowBytes`, and `buffer` pointer.

### 3. Host Side (Emulator)
-   **Implement Handler**: `M68K_EMUL_OP_CLIP_PUT_IMG` in `emul_op.cpp`.
-   **Encode to PNG**:
    -   Receive raw RGB/ARGB data.
    -   Use `libpng` (or `stb_image_write`) to encode to PNG format.
-   **Set Clipboard**:
    -   Use `SDL_SetClipboardData` (if available) or X11 specific calls to set `image/png` target.
