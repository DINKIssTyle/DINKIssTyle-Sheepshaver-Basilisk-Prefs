/*
 *  clip_sdl.cpp - Clipboard handling using SDL2 API with encoding conversion
 *
 *  Copyright (C) 2026 DINKIssTyle
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 */

#include "sysdeps.h"

#include <SDL.h>
#include <cstring>
#include <iconv.h>
#include <errno.h>

#include "macos_util.h"
#include "clip.h"
#include "prefs.h"
#include "cpu_emulation.h"
#include "main.h"
#include "emul_op.h"

#define DEBUG 0
#include "debug.h"

// Flag: Don't convert clipboard text
static bool no_clip_conversion;

// Flag for PutScrap(): the data was put by GetScrap(), don't bounce it back
static bool we_put_this_data = false;

// Encoding setting (from name_encoding pref)
static int name_encoding = 0;

// Get Mac encoding name from name_encoding value
static const char* get_mac_encoding(int enc)
{
    switch (enc) {
        case 1:  return "EUC-JP";            // Japanese
        case 2:  return "BIG5";              // Chinese Traditional
        case 3:  return "EUC-KR";            // Korean
        case 4:  return "ISO-8859-6";        // Arabic
        case 5:  return "ISO-8859-8";        // Hebrew
        case 6:  return "ISO-8859-7";        // Greek
        case 7:  return "KOI8-R";            // Cyrillic
        case 25: return "GB2312";            // Chinese Simplified
        default: return "MACINTOSH";         // Mac Roman (default)
    }
}

// Convert text from one encoding to another using iconv
static char* convert_encoding(const char* input, size_t input_len, 
                              const char* from_enc, const char* to_enc,
                              size_t* output_len)
{
    iconv_t cd = iconv_open(to_enc, from_enc);
    if (cd == (iconv_t)-1) {
        return NULL;
    }

    size_t out_size = input_len * 4 + 1;
    char* output = (char*)malloc(out_size);
    if (!output) {
        iconv_close(cd);
        return NULL;
    }

    char* in_ptr = (char*)input;
    char* out_ptr = output;
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

void ClipInit(void)
{
    no_clip_conversion = PrefsFindBool("noclipconversion");
    name_encoding = PrefsFindInt32("name_encoding");
}

/*
 *  Deinitialization
 */

void ClipExit(void)
{
}

/*
 *  Mac application reads clipboard (from host to guest)
 */

void GetScrap(void **handle, uint32 type, int32 offset)
{
    D(bug("GetScrap handle %p, type %08x, offset %d\n", handle, type, offset));

    if (type != FOURCC('T','E','X','T'))
        return;

    if (!SDL_HasClipboardText())
        return;

    char *text = SDL_GetClipboardText();
    if (!text || strlen(text) == 0) {
        if (text) SDL_free(text);
        return;
    }

    size_t len = strlen(text);
    char* mac_text = NULL;
    size_t mac_len = 0;
    
    if (!no_clip_conversion && name_encoding != 0) {
        const char* mac_enc = get_mac_encoding(name_encoding);
        mac_text = convert_encoding(text, len, "UTF-8", mac_enc, &mac_len);
    }
    
    if (!mac_text) {
        mac_text = (char*)malloc(len + 1);
        if (!mac_text) {
            SDL_free(text);
            return;
        }
        memcpy(mac_text, text, len);
        mac_text[len] = '\0';
        mac_len = len;
    }
    SDL_free(text);

    for (size_t i = 0; i < mac_len; i++) {
        if (mac_text[i] == '\n')
            mac_text[i] = '\r';
    }

    M68kRegisters r;
    r.d[0] = mac_len;
    Execute68kTrap(0xa71e, &r);
    uint32 scrap_area = r.a[0];

    if (scrap_area == 0) {
        free(mac_text);
        return;
    }

    Host2Mac_memcpy(scrap_area, mac_text, mac_len);

    static uint8 proc[] = {
        0x59, 0x8f,
        0xa9, 0xfc,
        0x2f, 0x3c, 0, 0, 0, 0,
        0x2f, 0x3c, 'T', 'E', 'X', 'T',
        0x2f, 0x3c, 0, 0, 0, 0,
        0xa9, 0xfe,
        0x58, 0x8f,
        M68K_RTS >> 8, M68K_RTS & 0xff
    };

    r.d[0] = sizeof(proc);
    Execute68kTrap(0xa71e, &r);
    uint32 proc_area = r.a[0];

    if (proc_area) {
        Host2Mac_memcpy(proc_area, proc, sizeof(proc));
        WriteMacInt32(proc_area + 6, mac_len);
        WriteMacInt32(proc_area + 18, scrap_area);
        we_put_this_data = true;
        Execute68k(proc_area, &r);

        r.a[0] = proc_area;
        Execute68kTrap(0xa01f, &r);
    }

    r.a[0] = scrap_area;
    Execute68kTrap(0xa01f, &r);

    free(mac_text);
}

/*
 *  Mac application wrote to clipboard (from guest to host)
 */

void PutScrap(uint32 type, void *scrap, int32 length)
{
    D(bug("PutScrap type %08x, data %p, length %d\n", type, scrap, length));

    if (we_put_this_data) {
        we_put_this_data = false;
        return;
    }

    if (type != FOURCC('T','E','X','T'))
        return;

    if (length <= 0 || scrap == NULL)
        return;

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

    char* utf8_text = NULL;
    size_t utf8_len = 0;
    
    if (!no_clip_conversion && name_encoding != 0) {
        const char* mac_enc = get_mac_encoding(name_encoding);
        utf8_text = convert_encoding(temp, length, mac_enc, "UTF-8", &utf8_len);
    }

    if (utf8_text) {
        SDL_SetClipboardText(utf8_text);
        free(utf8_text);
    } else {
        SDL_SetClipboardText(temp);
    }

    free(temp);
}

/*
 *  Stubs for X11 selection events (not used in SDL mode)
 */

void ClipboardSelectionClear(void *xev)
{
}

void ClipboardSelectionRequest(void *req)
{
}

/*
 *  Mac application calls ZeroScrap - SheepShaver only
 */

void ZeroScrap()
{
    we_put_this_data = false;
}
