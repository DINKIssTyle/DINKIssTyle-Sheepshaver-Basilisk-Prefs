# Bidirectional Clipboard Image Transfer Walkthrough

This document details the implementation of full image clipboard synchronization between the Linux Host (X11) and the Mac OS Guest (Basilisk II/SheepShaver).

## 1. Architecture Overview

The system uses a custom Emulator Opcode to transfer raw pixel data between the Guest and Host.

*   **Host -> Mac**: Host detects image (PNG) on X11 clipboard, decodes to raw ARGB, sends to Guest. Guest creates a GWorld, copies pixels, creates a PICT, and puts it on the Mac Scrap.
*   **Mac -> Host**: Mac takes PICT from Scrap, draws to GWorld to get RGB pixels, sends to Host. Host encodes to PNG and sets to X11 clipboard.

## 2. Host -> Mac Implementation Details (Completed)

*   **Challenge**: 68k Register Return Values.
    *   **Fix**: Modified Opcodes to write results to memory addresses passed in A0/A1 registers (pass-by-reference) instead of returning in D0.
*   **Challenge**: Inline Assembly in CodeWarrior.
    *   **Fix**: Used hex codes for opcodes (`= { 0x7131 }`) to avoid compiler specific inline assembly issues.
*   **Challenge**: Black Image Transfer.
    *   **Cause**: `libpng` default RGBA format vs Mac `0RGB` expectation, and Alpha channel handling.
    *   **Fix**: Configured `libpng` to use `PNG_FILLER_BEFORE` (0xFF filler) to produce `ARGB` (interpreted as `xRGB` by Mac), and ensured Mac uses `NewCWindow` for color contexts.

## 3. Mac -> Host Implementation Details (Completed)

*   **Guest Side ([TestApp.c](file:///home/dinki/github/DINKIssTyle-Sheepshaver-Basilisk-Prefs/macemu_patches/Clipboard_Patch/Extension/src/TestApp.c))**:
    *   Added [SyncImageToHost](file:///home/dinki/github/DINKIssTyle-Sheepshaver-Basilisk-Prefs/macemu_patches/Clipboard_Patch/Extension/src/TestApp.c#90-209) function triggered by 'S' key.
    *   Reads [PICT](file:///home/dinki/github/DINKIssTyle-Sheepshaver-Basilisk-Prefs/macemu_patches/Clipboard_Patch/Extension/src/test_gworld.c#28-82) from Scrap, draws to a 32-bit `GWorld`.
    *   Extracts raw pixels and prepends a 16-byte header (Width, Height, RowBytes, Depth).
    *   Sends to Host via `M68K_EMUL_OP_CLIP_PUT_IMG` (0x7133).

*   **Host Side ([clip_sdl.cpp](file:///home/dinki/github/DINKIssTyle-Sheepshaver-Basilisk-Prefs/macemu/BasiliskII/src/SDL/clip_sdl.cpp) / [emul_op.cpp](file:///home/dinki/github/DINKIssTyle-Sheepshaver-Basilisk-Prefs/macemu/BasiliskII/src/emul_op.cpp))**:
    *   Implemented [ClipboardPutData](file:///home/dinki/github/DINKIssTyle-Sheepshaver-Basilisk-Prefs/macemu_patches/Clipboard_Patch/patches/clip_sdl.cpp#613-617) to detect `IMG ` type.
    *   **Color Correction**: The Mac sends pixels as `00 RR GG BB`. Libpng expects `RR GG BB` for RGB or `RR GG BB AA` for RGBA.
    *   **Fix**: Used `png_set_filler(png, 0, PNG_FILLER_BEFORE)` with `PNG_COLOR_TYPE_RGB` to correctly strip the leading zero byte and save as a standard 24-bit RGB PNG.
    *   **X11 Integration**: Used `xclip` system command to take the generated PNG file ([/tmp/mac_clipboard.png](file:///tmp/mac_clipboard.png)) and set it to the X11 clipboard selection.

## 4. Verification

### Host -> Mac
1. Copy image in Linux (Firefox, etc.).
2. Click inside `TestApp` window on Mac.
3. Image is displayed and copied to Mac clipboard. (Verified with Paint)

### Mac -> Host
1. Draw/Copy content in Mac Paint.
2. Press **'S'** key in `TestApp`.
3. Application reports "Sent to Host!".
4. Verify [/tmp/mac_clipboard.png](file:///tmp/mac_clipboard.png) exists and has correct colors.
5. Paste into Linux application (e.g. GIMP, Telegram) or check `xclip -selection clipboard -t image/png -o > test.png`.

## 5. Artifacts
*   [TestApp.c](file:///home/dinki/github/DINKIssTyle-Sheepshaver-Basilisk-Prefs/macemu_patches/Clipboard_Patch/Extension/src/TestApp.c): Updated source code with bidirectional sync.
*   [clip_sdl.cpp](file:///home/dinki/github/DINKIssTyle-Sheepshaver-Basilisk-Prefs/macemu/BasiliskII/src/SDL/clip_sdl.cpp): Patched host SDL clipboard handling with PNG support and Color fixing.
