#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <Imlib2.h>
#include <math.h>
#include "wallpaper.h"

void set_wallpaper_fill(const char *path)
{
    Display *dpy = XOpenDisplay(NULL);
    if (!dpy) {
        fprintf(stderr, "Cannot open display\n");
        return;
    }

    int screen = DefaultScreen(dpy);
    Window root = RootWindow(dpy, screen);

    int sw = DisplayWidth(dpy, screen);
    int sh = DisplayHeight(dpy, screen);

    Imlib_Image img = imlib_load_image(path);
    if (!img) {
        fprintf(stderr, "Failed to load image: %s\n", path);
        XCloseDisplay(dpy);
        return;
    }

    imlib_context_set_display(dpy);
    imlib_context_set_visual(DefaultVisual(dpy, screen));
    imlib_context_set_colormap(DefaultColormap(dpy, screen));
    imlib_context_set_image(img);

    /* create a pixmap for the wallpaper */
    Pixmap pm = XCreatePixmap(dpy, root, sw, sh, DefaultDepth(dpy, screen));
    imlib_context_set_drawable(pm);

    /* scale to fill the screen */
    int iw = imlib_image_get_width();
    int ih = imlib_image_get_height();

    double scale = fmax((double)sw / iw, (double)sh / ih);
    int nw = (int)(iw * scale + 0.5);
    int nh = (int)(ih * scale + 0.5);

    int x = (sw - nw) / 2;
    int y = (sh - nh) / 2;

    imlib_render_image_on_drawable_at_size(x, y, nw, nh);

    /* set wallpaper on root window */
    XSetWindowBackgroundPixmap(dpy, root, pm);

    Atom prop_root = XInternAtom(dpy, "_XROOTPMAP_ID", False);
    Atom prop_eset = XInternAtom(dpy, "ESETROOT_PMAP_ID", False);

    XChangeProperty(dpy, root, prop_root, XA_PIXMAP, 32,
                    PropModeReplace, (unsigned char *)&pm, 1);
    XChangeProperty(dpy, root, prop_eset, XA_PIXMAP, 32,
                    PropModeReplace, (unsigned char *)&pm, 1);

    XClearWindow(dpy, root);
    XFlush(dpy);

    imlib_free_image();
    XCloseDisplay(dpy);
}
