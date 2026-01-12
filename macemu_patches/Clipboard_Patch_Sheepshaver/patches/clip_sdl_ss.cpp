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

#include "clip.h"
#include "cpu_emulation.h"
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
 *  In SheepShaver, this is called but we cannot easily inject data
 *  into the Mac clipboard without 68k traps.
 *
 *  Current limitation: Host->Mac clipboard not implemented for SheepShaver.
 */

void GetScrap(void **handle, uint32 type, int32 offset) {
  D(bug("GetScrap handle %p, type %08x, offset %d\n", handle, type, offset));

  // SheepShaver limitation: Cannot inject data into Mac clipboard
  // without PowerPC-native memory allocation calls
  // TODO: Implement using SheepShaver's thunk mechanism
}

/*
 *  Mac application wrote to clipboard (from guest to host)
 *  This works in SheepShaver - we receive the data directly.
 */

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

/*
 *  Stubs for X11 selection events (not used in SDL mode)
 */

void ClipboardSelectionClear(void *xev) {}

void ClipboardSelectionRequest(void *req) {}

/*
 *  SheepShaver NativeOp Clipboard Implementation
 */

// Check if host clipboard content has changed
bool ClipboardCheck(void) {
  if (!SDL_HasClipboardText()) {
    if (last_clipboard_text) {
      printf("[DEBUG] ClipboardCheck: Host clipboard empty, but had content. "
             "Changed.\n");
      free(last_clipboard_text);
      last_clipboard_text = NULL;
      return true;
    }
    return false;
  }

  char *text = SDL_GetClipboardText();
  if (!text)
    return false;

  bool changed = false;
  if (last_clipboard_text == NULL || strcmp(text, last_clipboard_text) != 0) {
    printf("[DEBUG] ClipboardCheck: Host clipboard changed.\n");
    printf("[DEBUG] New content: '%s'\n", text);
    if (last_clipboard_text)
      free(last_clipboard_text);
    last_clipboard_text = strdup(text);
    changed = true;
  }

  SDL_free(text);
  return changed;
}

// Get host clipboard data size
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
  return 0; // PICT not supported yet
}

// Get host clipboard data
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

// Put data to host clipboard
void ClipboardPutData(uint32 type, void *data, int32 size) {
  // Reuse PutScrap logic
  PutScrap(type, data, size);
}
