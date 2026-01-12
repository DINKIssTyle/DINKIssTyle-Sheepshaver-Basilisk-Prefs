/*
 * X11 Clipboard Image Test
 * Checks if 'image/png' is available on the clipboard and saves it.
 * Compile with: g++ test_x11.cpp -o test_x11 -lX11
 */

#include <X11/Xatom.h>
#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>
#include <vector>

/* Atoms */
Atom clipboard_atom;
Atom targets_atom;
Atom image_png_atom;
Atom image_bmp_atom;
Atom incr_atom;

/* Helper to get atom name */
const char *GetAtomName(Display *d, Atom a) {
  char *name = XGetAtomName(d, a);
  static char buf[256];
  strncpy(buf, name ? name : "(null)", 255);
  if (name)
    XFree(name);
  return buf;
}

/* Read property data */
bool ReadProperty(Display *display, Window window, Atom property,
                  std::vector<unsigned char> &data) {
  Atom type;
  int format;
  unsigned long nitems, bytes_after;
  unsigned char *prop;

  int result = XGetWindowProperty(display, window, property, 0, (~0L), False,
                                  AnyPropertyType, &type, &format, &nitems,
                                  &bytes_after, &prop);

  if (result != Success)
    return false;
  if (!prop)
    return false;

  if (type == incr_atom) {
    printf("Incremental transfer not supported in test tool.\n");
    XFree(prop);
    return false;
  }

  data.resize(nitems * (format / 8));
  memcpy(data.data(), prop, data.size());
  XFree(prop);
  return true;
}

int main() {
  Display *display = XOpenDisplay(NULL);
  if (!display) {
    fprintf(stderr, "Cannot open display\n");
    return 1;
  }

  Window window = XCreateSimpleWindow(display, DefaultRootWindow(display), 0, 0,
                                      1, 1, 0, 0, 0);

  clipboard_atom = XInternAtom(display, "CLIPBOARD", False);
  targets_atom = XInternAtom(display, "TARGETS", False);
  image_png_atom = XInternAtom(display, "image/png", False);
  image_bmp_atom = XInternAtom(display, "image/bmp", False);
  incr_atom = XInternAtom(display, "INCR", False);

  /* 1. Request TARGETS */
  XConvertSelection(display, clipboard_atom, targets_atom, targets_atom, window,
                    CurrentTime);
  XFlush(display);

  /* Event loop */
  bool done = false;
  bool has_png = false;
  std::vector<unsigned char> img_data;

  XEvent event;
  while (!done) {
    XNextEvent(display, &event);

    switch (event.type) {
    case SelectionNotify: {
      if (event.xselection.selection != clipboard_atom)
        break;

      if (event.xselection.property == None) {
        printf("Selection conversion failed.\n");
        done = true;
        break;
      }

      std::vector<unsigned char> data;
      if (!ReadProperty(display, window, event.xselection.property, data)) {
        printf("Failed to read property.\n");
        done = true;
        break;
      }

      if (event.xselection.target == targets_atom) {
        /* Check available targets */
        Atom *atoms = (Atom *)data.data();
        int count = data.size() / sizeof(Atom);
        printf("Available targets:\n");
        for (int i = 0; i < count; i++) {
          printf(" - %s\n", GetAtomName(display, atoms[i]));
          if (atoms[i] == image_png_atom)
            has_png = true;
        }

        if (has_png) {
          printf("image/png found! Requesting...\n");
          XConvertSelection(display, clipboard_atom, image_png_atom,
                            image_png_atom, window, CurrentTime);
        } else {
          printf("No image/png found.\n");
          done = true;
        }
      } else if (event.xselection.target == image_png_atom) {
        /* PNG data received */
        printf("Received PNG data: %lu bytes\n", data.size());

        FILE *fp = fopen("/tmp/clipboard_test.png", "wb");
        if (fp) {
          fwrite(data.data(), 1, data.size(), fp);
          fclose(fp);
          printf("Saved to /tmp/clipboard_test.png\n");
        }
        done = true;
      }

      /* Delete property */
      XDeleteProperty(display, window, event.xselection.property);
      break;
    }
    }
  }

  XDestroyWindow(display, window);
  XCloseDisplay(display);
  return 0;
}
