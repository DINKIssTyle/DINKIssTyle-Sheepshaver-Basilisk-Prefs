# GLSL Shader Support for Basilisk II and SheepShaver

This patch integrates GLSL shader support into the SDL2 video backend of Basilisk II and SheepShaver, allowing for visual effects such as CRT simulation, scanlines, and color correction.

## Features

- **GLSL Support**: Load and apply standard GLSL shaders.
- **Multipass Rendering**: Support for chaining multiple shaders (e.g., a blur pass followed by a scanline pass).
- **RetroArch Shader Compatibility**: Supports a subset of RetroArch-style GLSL shaders (single-file shaders with `#pragma parameter` support - though parameters are currently ignored).
- **Correct Orientation**: Automatically handles texture coordinate differences between SDL surfaces and OpenGL FBOs.

## Usage

**Use the Sheepshaver & Basilisk II Preferences Editor to add it to the shader list and configure the settings.**

## Implementation Details

The implementation consists of the following components:

1.  **`src/SDL/video_shader.cpp` & `src/SDL/video_shader.h`**:
    - Core logic for loading, compiling, and linking GLSL shaders.
    - Manages Framebuffer Objects (FBOs) for multipass rendering.
    - Handles the rendering loop ("ping-pong" rendering between FBOs).

2.  **`src/SDL/video_sdl2.cpp`**:
    - Hooks into the SDL2 video initialization (`init_sdl_video`) to setup OpenGL.
    - Hooks into the video presentation (`present_sdl_video`) to inject the shader rendering pipeline before the frame is shown.

3.  **`src/Unix/configure.ac`**:
    - Updated to include `video_shader.cpp` in the build.
    - Links against OpenGL (`-lGL`) when SDL video is enabled.

4.  **`src/prefs_items.cpp`**:
    - Registers the new `shader` preference keyword so it can be parsed from config files and command line arguments.

## Build Requirements

- **SDL2**: The video backend must be SDL2 (configured with `--enable-sdl-video`).
- **OpenGL**: Requires an OpenGL-capable driver and libraries (`libGL`).

## Building

**Basilisk II:**
```bash
cd BasiliskII/src/Unix
./autogen.sh
./configure --enable-sdl-video --enable-sdl-audio --with-gtk=GTK3
make
```

**SheepShaver:**
```bash
cd SheepShaver/src/Unix
./autogen.sh
./configure --enable-sdl-video --enable-sdl-audio --with-gtk=GTK3
make
```
