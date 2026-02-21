/* See LICENSE file for copyright and license details. */
/* Default settings; can be overriden by command line. */

/* appearance */
static const int  topbar      = 0;             /* 0 means bottom bar (default) */
static const char bgcolor[]   = "#1d2021"; /* dark0_hard */
static const char fgcolor[]   = "#504945"; /* dark2 */
static const char markcolor[] = "#fe8019"; /* bright orange */
static const char selcolor[]  = "#fbf1c7"; /* light0 */
static const char leterfont[] = "JetBrains Mono Medium:pixelsize=15:antialias=true:autohint=true";   //multiple fonts?
//static const char title[]     = "";            /* default "Sxiv -" */

/* global */
enum { WIN_WIDTH = 800, WIN_HEIGHT = 600 };    /* -g option; window dimensions */
static const float SLIDESHOW_DELAY = 4.5;      /* -S option; slideshow delay in seconds */
static const double GAMMA_MAX      = 10.0;     /* [-GAMMA_RANGE, 0] and (0, GAMMA_RANGE] are mapped.. */
static const int GAMMA_RANGE       = 32;       /* to the ranges [0, 1], and (1, GAMMA_MAX] */
static const int PAN_FRACTION      = 4;        /* 'i_scroll' pans image 1/PAN_FRACTION of screen width/height */
static const bool ANTI_ALIAS       = true;     /* false means pixelate images at zoom level != 100% */
static const bool ALPHA_LAYER      = false;    /* if true use checkerboard background for alpha layer (i_toggle_alpha) */
static const float zoom_levels[]   = {
 /* first/last value is used as min/max zoom percent level */
	12.5, 14,  25,  35,  45,  50,  75,
	100, 125,  150, 200, 400, 800, 900
};


/* thumbnail */
static const int THUMB_BORDERS[] = { 7 }; /* borders */
static const int THUMB_MARGIN    = -4;    /* margins between images, buggy with marks */
static const int THUMB_PADDING   = 0;     /* padding of the highlight or mark */
static const int THUMB_SIZE      = 3;     /* thumbnail size at startup, index into thumb_sizes[]: */
static const int squarethumb     = 1;     /* 0 means normal thumbs (default) */
static const int thumb_sizes[]   = {
 /* thumbnail sizes in pixels (width == height) */
	32, 64, 116, 145, 181, 286, 361, 412
};

/* cache size for imlib2, in bytes. For backwards compatibility reasons, the
 * size is kept at 4MiB. For most users, it is advised to pick a value close to
 * or above 128MiB for better image (re)loading performance. */
static const int cachesize = 256; /* 256MiB */

static const keymap_t keys[] = {
	/* modifiers    key               function              argument */
	{ 0,            XK_q,             g_quit,               None },
	{ 0,            XK_Return,        g_switch_mode,        None },
	{ 0,            XK_f,             g_toggle_fullscreen,  None },
	{ 0,            XK_b,             g_toggle_bar,         None },
	{ 0,		    XK_x,		      g_unmark_all,		    None },
	{ 0,            XK_g,             g_first,              None },
	{ 0,            XK_G,             g_n_or_last,          None },
	{ 0,            XK_r,             g_reload_image,       None },
	{ 0,            XK_D,             g_remove_image,       None },

	{ ControlMask,  XK_h,             g_scroll_screen,      DIR_LEFT },
	{ ControlMask,  XK_Left,          g_scroll_screen,      DIR_LEFT },
	{ ControlMask,  XK_j,             g_scroll_screen,      DIR_DOWN },
	{ ControlMask,  XK_Down,          g_scroll_screen,      DIR_DOWN },
	{ ControlMask,  XK_k,             g_scroll_screen,      DIR_UP },
	{ ControlMask,  XK_Up,            g_scroll_screen,      DIR_UP },
	{ ControlMask,  XK_l,             g_scroll_screen,      DIR_RIGHT },
	{ ControlMask,  XK_Right,         g_scroll_screen,      DIR_RIGHT },

	{ 0,            XK_m,             g_toggle_image_mark,  None },
	{ 0,            XK_M,             g_mark_range,         None },
	{ ControlMask,  XK_m,             g_reverse_marks,      None },
	{ ControlMask,  XK_u,             g_unmark_all,         None },
	{ 0,            XK_N,             g_navigate_marked,    +1 },
	{ 0,            XK_P,             g_navigate_marked,    -1 },
	{ 0,            XK_braceleft,     g_change_gamma,       -1 },
	{ 0,            XK_braceright,    g_change_gamma,       +1 },
	{ ControlMask,  XK_g,             g_change_gamma,        0 },

	{ 0,            XK_h,             t_move_sel,           DIR_LEFT },
	{ 0,            XK_Left,          t_move_sel,           DIR_LEFT },
	{ 0,            XK_j,             t_move_sel,           DIR_DOWN },
	{ 0,            XK_Down,          t_move_sel,           DIR_DOWN },
	{ 0,            XK_k,             t_move_sel,           DIR_UP },
	{ 0,            XK_Up,            t_move_sel,           DIR_UP },
	{ 0,            XK_l,             t_move_sel,           DIR_RIGHT },
	{ 0,            XK_Right,         t_move_sel,           DIR_RIGHT },
	{ 0,            XK_R,             t_reload_all,         None },

	{ 0,            XK_n,             i_navigate,           +1 },
	{ 0,            XK_n,             i_scroll_to_edge,     DIR_LEFT | DIR_UP },
	{ 0,            XK_space,         i_navigate,           +1 },
	{ 0,            XK_p,             i_navigate,           -1 },
	{ 0,            XK_p,             i_scroll_to_edge,     DIR_LEFT | DIR_UP },
	{ 0,            XK_BackSpace,     i_navigate,           -1 },
	{ 0,            XK_bracketright,  i_navigate,           +10 },
	{ 0,            XK_bracketleft,   i_navigate,           -10 },
	{ ControlMask,  XK_6,             i_alternate,          None },
	{ ControlMask,  XK_n,             i_navigate_frame,     +1 },
	{ ControlMask,  XK_p,             i_navigate_frame,     -1 },
	{ ControlMask,  XK_space,         i_toggle_animation,   None },
	{ 0,            XK_h,             i_scroll,             DIR_LEFT },
	{ 0,            XK_Left,          i_scroll,             DIR_LEFT },
	{ 0,            XK_j,             i_scroll,             DIR_DOWN },
	{ 0,            XK_Down,          i_scroll,             DIR_DOWN },
	{ 0,            XK_k,             i_scroll,             DIR_UP },
	{ 0,            XK_Up,            i_scroll,             DIR_UP },
	{ 0,            XK_l,             i_scroll,             DIR_RIGHT },
	{ 0,            XK_Right,         i_scroll,             DIR_RIGHT },
	{ 0,            XK_H,             i_scroll_to_edge,     DIR_LEFT },
	{ 0,            XK_J,             i_scroll_to_edge,     DIR_DOWN },
	{ 0,            XK_K,             i_scroll_to_edge,     DIR_UP },
	{ 0,            XK_L,             i_scroll_to_edge,     DIR_RIGHT },

	{ 0,            XK_equal,         g_zoom,               +1 },
	{ 0,            XK_plus,          i_set_zoom,           100 },
	{ 0,            XK_KP_Add,        i_set_zoom,           100 },
	{ 0,            XK_minus,         g_zoom,               -1 },
	{ 0,            XK_KP_Subtract,   g_zoom,               -1 },

	{ 0,            XK_w,             i_fit_to_win,         SCALE_DOWN },
	{ 0,            XK_W,             i_fit_to_win,         SCALE_FIT },
	{ 0,            XK_e,             i_fit_to_win,         SCALE_WIDTH },
	{ 0,            XK_E,             i_fit_to_win,         SCALE_HEIGHT },
	{ 0,            XK_less,          i_rotate,             DEGREE_270 },
	{ 0,            XK_greater,       i_rotate,             DEGREE_90 },
	{ 0,            XK_question,      i_rotate,             DEGREE_180 },
	{ 0,            XK_bar,           i_flip,               FLIP_HORIZONTAL },
	{ 0,            XK_underscore,    i_flip,               FLIP_VERTICAL },
	{ 0,            XK_a,             i_toggle_antialias,   None },
	{ 0,            XK_A,             i_toggle_alpha,       None },
	{ 0,            XK_s,             i_slideshow,          None },
};

/* button definitions */
static const button_t buttons[] = {
	/* modifiers	button		function		argument */
	{ 0,		1,		i_cursor_navigate,	None },
	{ 0,		2,		g_switch_mode,		None },
	{ 0,		3,		i_drag,		        DRAG_ABSOLUTE },
	{ 0,        4,      g_scroll_screen,    DIR_UP },
	{ 0,        5,      g_scroll_screen,    DIR_DOWN },
};
