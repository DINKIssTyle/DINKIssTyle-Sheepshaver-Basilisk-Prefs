/*
 *  clip_sdl_ss.cpp - Clipboard handling for SheepShaver using SDL2 API
 *
 *  Copyright (C) 2026 DINKIssTyle
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  SheepShaver-specific implementation without 68k trap calls.
 */

#include "sysdeps.h"

#include <SDL.h>
#include <cstring>
#include <errno.h>
#include <iconv.h>
#include <unistd.h>
#include <vector>

// X11 and PNG Headers
#include <X11/Xatom.h>
#include <X11/Xlib.h>
#include <png.h>

#include "clip.h"
#include "cpu_emulation.h"
#include "emul_op.h"
#include "macos_util.h"
#include "main.h"
#include "prefs.h"

#define DEBUG 0
#include "debug.h"

// Flag: Don't convert clipboard text
static bool no_clip_conversion;

// Flag for PutScrap(): the data was put by GetScrap(), don't bounce it back
static bool we_put_this_data = false;

// Cache for ClipboardCheck
static char *last_clipboard_text = NULL;

// Cache for Image Data (ARGB format)
static void *last_img_data = NULL;
static int32 last_img_size = 0;

// Encoding setting (from name_encoding pref)
static int name_encoding = 0;

// Get Mac encoding name from name_encoding value
static const char *get_mac_encoding(int enc) {
  switch (enc) {
  case 1:
    return "EUC-JP"; // Japanese
  case 2:
    return "BIG5"; // Chinese Traditional
  case 3:
    return "EUC-KR"; // Korean
  case 4:
    return "ISO-8859-6"; // Arabic
  case 5:
    return "ISO-8859-8"; // Hebrew
  case 6:
    return "ISO-8859-7"; // Greek
  case 7:
    return "KOI8-R"; // Cyrillic
  case 25:
    return "GB2312"; // Chinese Simplified
  default:
    return "MACINTOSH"; // Mac Roman (default)
  }
}

// Convert text from one encoding to another using iconv
static char *convert_encoding(const char *input, size_t input_len,
                              const char *from_enc, const char *to_enc,
                              size_t *output_len) {
  iconv_t cd = iconv_open(to_enc, from_enc);
  if (cd == (iconv_t)-1) {
    return NULL;
  }

  size_t out_size = input_len * 4 + 1;
  char *output = (char *)malloc(out_size);
  if (!output) {
    iconv_close(cd);
    return NULL;
  }

  char *in_ptr = (char *)input;
  char *out_ptr = output;
  size_t in_left = input_len;
  size_t out_left = out_size - 1;

  size_t result = iconv(cd, &in_ptr, &in_left, &out_ptr, &out_left);

  if (result == (size_t)-1) {
    free(output);
    iconv_close(cd);
    return NULL;
  }

  *out_ptr = '\0';
  *output_len = out_ptr - output;

  iconv_close(cd);
  return output;
}

/*
 * X11 / PNG Helper Functions
 */

struct PngReadData {
  const unsigned char *buffer;
  size_t size;
  size_t offset;
};

static void png_mem_read(png_structp png_ptr, png_bytep data,
                         png_size_t length) {
  PngReadData *p = (PngReadData *)png_get_io_ptr(png_ptr);
  if (p->offset + length > p->size) {
    png_error(png_ptr, "Read Error");
  }
  memcpy(data, p->buffer + p->offset, length);
  p->offset += length;
}

static bool FetchHostImage(void) {
  // 1. Open X11 Display
  Display *display = XOpenDisplay(NULL);
  if (!display) {
    printf("[CLIP] Failed to open X display\n");
    return false;
  }

  Window window = XCreateSimpleWindow(display, DefaultRootWindow(display), 0, 0,
                                      1, 1, 0, 0, 0);
  Atom clipboard_atom = XInternAtom(display, "CLIPBOARD", False);
  Atom image_png_atom = XInternAtom(display, "image/png", False);

  // 2. Request image/png
  XConvertSelection(display, clipboard_atom, image_png_atom, image_png_atom,
                    window, CurrentTime);
  XFlush(display);

  // 3. Wait for SelectionNotify
  bool done = false;
  bool success = false;
  std::vector<unsigned char> png_data;
  XEvent event;
  int retries = 0;

  while (!done && retries < 100) { // Timeout safety (approx 1 sec)
    if (XCheckTypedEvent(display, SelectionNotify, &event)) {
      if (event.xselection.selection == clipboard_atom) {
        if (event.xselection.property != None) {
          // Read property
          Atom type;
          int format;
          unsigned long nitems, bytes_after;
          unsigned char *prop;

          int result = XGetWindowProperty(
              display, window, event.xselection.property, 0, (~0L), False,
              AnyPropertyType, &type, &format, &nitems, &bytes_after, &prop);

          if (result == Success && prop) {
            png_data.resize(nitems * (format / 8));
            memcpy(png_data.data(), prop, png_data.size());
            XFree(prop);
            success = true;
          }
          XDeleteProperty(display, window, event.xselection.property);
        }
        done = true;
      }
    }
    if (!done) {
      usleep(10000); // 10ms wait
      retries++;
    }
  }

  XDestroyWindow(display, window);
  XCloseDisplay(display);

  if (!success || png_data.empty()) {
    printf("[CLIP] No PNG data found on X clipboard\n");
    return false;
  }

  // 4. Decode PNG using libpng
  if (last_img_data) {
    free(last_img_data);
    last_img_data = NULL;
    last_img_size = 0;
  }

  if (png_sig_cmp(png_data.data(), 0, 8))
    return false;

  png_structp png_ptr =
      png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (!png_ptr)
    return false;

  png_infop info_ptr = png_create_info_struct(png_ptr);
  if (!info_ptr) {
    png_destroy_read_struct(&png_ptr, NULL, NULL);
    return false;
  }

  PngReadData read_data = {png_data.data(), png_data.size(), 0};
  png_set_read_fn(png_ptr, &read_data, png_mem_read);

  if (setjmp(png_jmpbuf(png_ptr))) {
    png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
    return false;
  }

  png_read_info(png_ptr, info_ptr);

  int width = png_get_image_width(png_ptr, info_ptr);
  int height = png_get_image_height(png_ptr, info_ptr);
  png_byte color_type = png_get_color_type(png_ptr, info_ptr);
  png_byte bit_depth = png_get_bit_depth(png_ptr, info_ptr);

  // Transform to 8-bit RGB/RGBA
  if (bit_depth == 16)
    png_set_strip_16(png_ptr);
  if (color_type == PNG_COLOR_TYPE_PALETTE)
    png_set_palette_to_rgb(png_ptr);
  if (color_type == PNG_COLOR_TYPE_GRAY && bit_depth < 8)
    png_set_expand_gray_1_2_4_to_8(png_ptr);
  if (png_get_valid(png_ptr, info_ptr, PNG_INFO_tRNS))
    png_set_tRNS_to_alpha(png_ptr);

  // Ensure 32-bit ARGB
  if (color_type == PNG_COLOR_TYPE_RGB || color_type == PNG_COLOR_TYPE_GRAY ||
      color_type == PNG_COLOR_TYPE_PALETTE)
    png_set_filler(png_ptr, 0xFF, PNG_FILLER_AFTER);

  if (color_type == PNG_COLOR_TYPE_GRAY ||
      color_type == PNG_COLOR_TYPE_GRAY_ALPHA)
    png_set_gray_to_rgb(png_ptr);

  png_read_update_info(png_ptr, info_ptr);

  // Read rows
  int rowbytes = png_get_rowbytes(png_ptr, info_ptr);
  // Header size + Data size
  last_img_size = 16 + (height * rowbytes); // 16 bytes header

  printf("[CLIP] Dimensions: %dx%d, RowBytes: %d, CalcSize: %d\n", width,
         height, rowbytes, last_img_size);

  // Safety check: Limit to 50MB
  if (last_img_size > 50 * 1024 * 1024) {
    printf("[CLIP] Image too large (%d bytes). Ignoring.\n", last_img_size);
    png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
    return false;
  }

  last_img_data = malloc(last_img_size);
  unsigned char *pHeaders = (unsigned char *)last_img_data;

  // Write header (Big Endian for Mac)
  // Width
  pHeaders[0] = (width >> 24) & 0xFF;
  pHeaders[1] = (width >> 16) & 0xFF;
  pHeaders[2] = (width >> 8) & 0xFF;
  pHeaders[3] = width & 0xFF;
  // Height
  pHeaders[4] = (height >> 24) & 0xFF;
  pHeaders[5] = (height >> 16) & 0xFF;
  pHeaders[6] = (height >> 8) & 0xFF;
  pHeaders[7] = height & 0xFF;
  // RowBytes
  pHeaders[8] = (rowbytes >> 24) & 0xFF;
  pHeaders[9] = (rowbytes >> 16) & 0xFF;
  pHeaders[10] = (rowbytes >> 8) & 0xFF;
  pHeaders[11] = rowbytes & 0xFF;
  // Depth (32)
  pHeaders[12] = 0;
  pHeaders[13] = 0;
  pHeaders[14] = 0;
  pHeaders[15] = 32;

  png_bytep *row_pointers = (png_bytep *)malloc(sizeof(png_bytep) * height);
  for (int y = 0; y < height; y++) {
    row_pointers[y] = (png_bytep)last_img_data + 16 + (y * rowbytes);
  }

  png_read_image(png_ptr, row_pointers);
  png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
  free(row_pointers);

  printf("[CLIP] Processed PNG: %dx%d, rowbytes=%d, total=%d\n", width, height,
         rowbytes, last_img_size);
  return true;
}

/*
 *  Initialization
 */

void ClipInit(void) {
  no_clip_conversion = PrefsFindBool("noclipconversion");
  name_encoding = PrefsFindInt32("name_encoding");
  D(bug("ClipInit: SheepShaver SDL clipboard, encoding=%d\n", name_encoding));
}

/*
 *  Deinitialization
 */

void ClipExit(void) { D(bug("ClipExit\n")); }

/*
 *  ZeroScrap - Called before Mac app writes to clipboard
 */

void ZeroScrap() {
  D(bug("ZeroScrap\n"));
  we_put_this_data = false;
}

/*
 *  Mac application reads clipboard (from host to guest)
 */

void GetScrap(void **handle, uint32 type, int32 offset) {
  D(bug("GetScrap handle %p, type %08x, offset %d\n", handle, type, offset));

  // Only handle TEXT type for now
  if (type != FOURCC('T', 'E', 'X', 'T'))
    return;

  // Check if host has clipboard text
  if (!SDL_HasClipboardText())
    return;

  char *text = SDL_GetClipboardText();
  if (!text || strlen(text) == 0) {
    if (text)
      SDL_free(text);
    return;
  }

  // Convert from UTF-8 to Mac encoding if needed
  char *mac_text = NULL;
  size_t mac_len = 0;
  size_t src_len = strlen(text);

  if (!no_clip_conversion && name_encoding != 0) {
    const char *mac_enc = get_mac_encoding(name_encoding);
    mac_text = convert_encoding(text, src_len, "UTF-8", mac_enc, &mac_len);
  }

  const char *src_data = mac_text ? mac_text : text;
  int32 data_len = mac_text ? (int32)mac_len : (int32)src_len;

  if (data_len <= 0) {
    if (mac_text)
      free(mac_text);
    SDL_free(text);
    return;
  }

  // Allocate space for new scrap in MacOS side
  M68kRegisters r;
  r.d[0] = data_len;
  Execute68kTrap(0xa71e, &r); // NewPtrSysClear()
  uint32 scrap_area = r.a[0];

  if (scrap_area) {
    // Copy and convert data: LF -> CR for Mac
    uint8 *p = Mac2HostAddr(scrap_area);
    for (int32 i = 0; i < data_len; i++) {
      uint8 c = src_data[i];
      if (c == '\n')
        c = '\r';
      *p++ = c;
    }

    // Build 68k procedure to call ZeroScrap() and PutScrap()
    static uint8 proc[] = {
        0x59,          0x8f,                       // subq.l  #4,sp
        0xa9,          0xfc,                       // ZeroScrap()
        0x2f,          0x3c,           0, 0, 0, 0, // move.l  #length,-(sp)
        0x2f,          0x3c,           0, 0, 0, 0, // move.l  #type,-(sp)
        0x2f,          0x3c,           0, 0, 0, 0, // move.l  #outbuf,-(sp)
        0xa9,          0xfe,                       // PutScrap()
        0x58,          0x8f,                       // addq.l  #4,sp
        M68K_RTS >> 8, M68K_RTS & 0xff};

    r.d[0] = sizeof(proc);
    Execute68kTrap(0xa71e, &r); // NewPtrSysClear()
    uint32 proc_area = r.a[0];

    if (proc_area) {
      // Copy procedure to Mac memory
      Host2Mac_memcpy(proc_area, proc, sizeof(proc));
      WriteMacInt32(proc_area + 6, data_len);
      WriteMacInt32(proc_area + 12, type);
      WriteMacInt32(proc_area + 18, scrap_area);

      // Mark that we're putting this data to avoid bounce-back
      we_put_this_data = true;
      Execute68k(proc_area, &r);

      // Dispose procedure memory
      r.a[0] = proc_area;
      Execute68kTrap(0xa01f, &r); // DisposePtr
    }

    // Dispose scrap memory
    r.a[0] = scrap_area;
    Execute68kTrap(0xa01f, &r); // DisposePtr
  }

  if (mac_text)
    free(mac_text);
  SDL_free(text);

  D(bug("GetScrap: Copied %d bytes from host to Mac clipboard\n", data_len));
}

void PutScrap(uint32 type, void *scrap, int32 length) {
  D(bug("PutScrap type %08x, data %p, length %d\n", type, scrap, length));

  // Don't bounce back data we just put
  if (we_put_this_data) {
    we_put_this_data = false;
    return;
  }

  // Only handle TEXT type
  if (type != FOURCC('T', 'E', 'X', 'T'))
    return;

  if (length <= 0 || scrap == NULL)
    return;

  // Create temporary buffer with CR->LF conversion
  char *temp = (char *)malloc(length + 1);
  if (!temp)
    return;

  const uint8 *src = (const uint8 *)scrap;
  for (int32 i = 0; i < length; i++) {
    uint8 c = src[i];
    if (c == '\r')
      c = '\n';
    temp[i] = c;
  }
  temp[length] = '\0';

  // Convert from Mac encoding to UTF-8
  char *utf8_text = NULL;
  size_t utf8_len = 0;

  if (!no_clip_conversion && name_encoding != 0) {
    const char *mac_enc = get_mac_encoding(name_encoding);
    utf8_text = convert_encoding(temp, length, mac_enc, "UTF-8", &utf8_len);
  }

  if (utf8_text) {
    D(bug("PutScrap: Setting %zu bytes (converted) to SDL clipboard\n",
          utf8_len));
    SDL_SetClipboardText(utf8_text);
    free(utf8_text);
  } else {
    D(bug("PutScrap: Setting %d bytes (original) to SDL clipboard\n", length));
    SDL_SetClipboardText(temp);
  }

  free(temp);
}

void ClipboardSelectionClear(void *xev) {}
void ClipboardSelectionRequest(void *req) {}

/*
 *  SheepShaver NativeOp Clipboard Implementation
 */

bool ClipboardCheck(void) {
  // Check TEXT
  if (!SDL_HasClipboardText()) {
    if (last_clipboard_text) {
      printf("[DEBUG] ClipboardCheck: Host clipboard empty, but had content. "
             "Changed.\n");
      free(last_clipboard_text);
      last_clipboard_text = NULL;
      return true;
    }
    // Also check IMAGE here?
    // Ideally we should monitor clipboard ownership or sequence number.
    // For now, let's keep TEXT priority.
    // If we want to detect Image changes, we'd need to poll X11 or use Fixes
    // ext. Polling X11 is expensive. Let's assume user triggers copy manually
    // for now.
    return false;
  }

  char *text = SDL_GetClipboardText();
  if (!text)
    return false;

  bool changed = false;
  if (last_clipboard_text == NULL || strcmp(text, last_clipboard_text) != 0) {
    printf("[DEBUG] ClipboardCheck: Host clipboard changed.\n");
    if (last_clipboard_text)
      free(last_clipboard_text);
    last_clipboard_text = strdup(text);
    changed = true;
  }

  SDL_free(text);
  return changed;
}

int32 ClipboardGetSize(uint32 type) {
  printf("[DEBUG] ClipboardGetSize: Requesting type '%c%c%c%c'\n",
         (type >> 24) & 0xff, (type >> 16) & 0xff, (type >> 8) & 0xff,
         type & 0xff);
  if (type == 0x54455854) { // 'TEXT'
    if (SDL_HasClipboardText()) {
      char *text = SDL_GetClipboardText();
      if (text) {
        // Let's do the conversion to be safe if encoding is involved
        size_t mac_len = 0;
        char *mac_text = NULL;

        if (!no_clip_conversion && name_encoding != 0) {
          const char *mac_enc = get_mac_encoding(name_encoding);
          mac_text =
              convert_encoding(text, strlen(text), "UTF-8", mac_enc, &mac_len);
        }

        if (mac_text) {
          free(mac_text);
        } else {
          mac_len = strlen(text);
        }

        SDL_free(text);
        printf("[DEBUG] ClipboardGetSize: Returning size %ld\n", (long)mac_len);
        return (int32)mac_len;
      }
    }
  }
  return 0;
}

int32 ClipboardGetData(uint32 type, void *buffer, int32 size) {
  printf("[DEBUG] ClipboardGetData: Requesting type '%c%c%c%c', size %d\n",
         (type >> 24) & 0xff, (type >> 16) & 0xff, (type >> 8) & 0xff,
         type & 0xff, size);
  if (type == 0x54455854) { // 'TEXT'
    if (SDL_HasClipboardText()) {
      char *text = SDL_GetClipboardText();
      if (!text)
        return 0;

      char *src_data = text;
      char *converted_text = NULL;
      size_t src_len = strlen(text);

      // Convert UTF-8 -> Mac Encoding
      if (!no_clip_conversion && name_encoding != 0) {
        const char *mac_enc = get_mac_encoding(name_encoding);
        size_t out_len;
        converted_text =
            convert_encoding(text, src_len, "UTF-8", mac_enc, &out_len);
        if (converted_text) {
          src_data = converted_text;
          src_len = out_len;
        }
      }

      int32 copy_len = (int32)src_len;
      if (copy_len > size)
        copy_len = size;

      if (copy_len > 0 && buffer) {
        memcpy(buffer, src_data, copy_len);
        // Convert LF to CR
        char *p = (char *)buffer;
        for (int32 i = 0; i < copy_len; i++) {
          if (p[i] == '\n')
            p[i] = '\r';
        }
      }

      if (converted_text)
        free(converted_text);
      SDL_free(text);
      printf("[DEBUG] ClipboardGetData: Copied %ld bytes\n", (long)copy_len);
      return copy_len;
    }
  }
  return 0;
}

void ClipboardPutData(uint32 type, void *data, int32 size) {
  // Reuse PutScrap logic
  PutScrap(type, data, size);
}

/*
 *  IMAGE CLIPBOARD
 */

int32 ClipboardGetImageSize(void) {
  if (FetchHostImage()) {
    return last_img_size;
  }
  return 0;
}

int32 ClipboardGetImageData(void *buffer, int32 size) {
  if (last_img_data && size >= last_img_size) {
    memcpy(buffer, last_img_data, last_img_size);
    // We can keep the cache valid for multiple reads or clear it if triggered
    // by new copy
    return last_img_size;
  }
  return 0;
}
