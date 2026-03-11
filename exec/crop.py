#!/usr/bin/env python3
"""
crop — sxiv-integrated cropping tool
Usage:  crop <image>

Keys:
  0  free    1  1:1    2  16:9    3  3:4    4  4:3    5  9:16
  Shift      constrain while dragging
  Enter / c  crop & save  (.bak backup created)
  r          reset selection
  Escape / q quit
"""

import sys, os, shutil
import cv2
import numpy as np

RATIOS = {
    ord('0'): (None,   "Free"),
    ord('1'): ((1,1),  "1:1"),
    ord('2'): ((16,9), "16:9"),
    ord('3'): ((3,4),  "3:4"),
    ord('4'): ((4,3),  "4:3"),
    ord('5'): ((9,16), "9:16"),
}

ACCENT     = (170, 212, 0)    # BGR
HANDLE_COL = (15,  15,  15)
INFO_COL   = (200, 200, 200)
HINT_COL   = (80,  80,  80)
THIRDS_COL = (100, 160, 0)
HANDLE_SZ  = 5
MIN_PX     = 4
BAR_H      = 28

def norm(r):
    x0,y0,x1,y1 = r
    return (min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1))

def clamp(v,lo,hi): return max(lo,min(v,hi))

def constrain(x0,y0,x1,y1,ratio,shift):
    if ratio is None and not shift: return x0,y0,x1,y1
    rw,rh = ratio if ratio else (1,1)
    w,h = abs(x1-x0),abs(y1-y0)
    if w==0 and h==0: return x0,y0,x1,y1
    if h==0 or (w>0 and w/rw>=h/rh): h = w*rh/rw
    else: w = h*rw/rh
    return x0,y0, x0+(1 if x1>=x0 else -1)*w, y0+(1 if y1>=y0 else -1)*h

def constrain_handle(mode,x0,y0,x1,y1,ratio,shift):
    if ratio is None and not shift: return x0,y0,x1,y1
    rw,rh = ratio if ratio else (1,1)
    w,h = abs(x1-x0),abs(y1-y0)
    if 'n' in mode or 's' in mode:
        nw = h*rw/rh
        if 'w' in mode: x0=x1-nw
        else:           x1=x0+nw
    else:
        nh = w*rh/rw
        if 'n' in mode: y0=y1-nh
        else:           y1=y0+nh
    return x0,y0,x1,y1

def handle_positions(sel):
    x0,y0,x1,y1 = norm(sel)
    mx,my = (x0+x1)//2,(y0+y1)//2
    return {
        'nw':(x0,y0),'n':(mx,y0),'ne':(x1,y0),
        'e': (x1,my),
        'se':(x1,y1),'s':(mx,y1),'sw':(x0,y1),
        'w': (x0,my),
    }

def hit_handle(sel,x,y):
    for name,(hx,hy) in handle_positions(sel).items():
        if abs(x-hx)<=HANDLE_SZ+4 and abs(y-hy)<=HANDLE_SZ+4:
            return name
    return None

def hit_interior(sel,x,y):
    x0,y0,x1,y1=norm(sel)
    return x0<x<x1 and y0<y<y1

def main():
    if len(sys.argv)<2: print(__doc__); sys.exit(1)
    path=sys.argv[1]
    if not os.path.isfile(path):
        print(f"Error: {path} not found",file=sys.stderr); sys.exit(1)

    # load image as BGR numpy array
    img_orig = cv2.imread(path, cv2.IMREAD_COLOR)
    if img_orig is None:
        # fallback via PIL for weird formats
        from PIL import Image
        pil = Image.open(path).convert("RGB")
        img_orig = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    IH, IW = img_orig.shape[:2]

    cv2.namedWindow("crop", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("crop", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # get screen size from a dummy read
    sw = cv2.getWindowImageRect("crop")  # may return 0,0 before first imshow
    # safer: use env or just do first imshow to get real size
    dummy = np.zeros((100,100,3), dtype=np.uint8)
    cv2.imshow("crop", dummy)
    cv2.waitKey(1)
    rect = cv2.getWindowImageRect("crop")
    SW, SH = rect[2], rect[3]
    if SW <= 0 or SH <= 0:
        SW, SH = 1920, 1080  # fallback

    CH = SH - BAR_H  # canvas height (below bar)

    # fit image
    scale  = min(SW/IW, CH/IH)
    DW,DH  = int(IW*scale), int(IH*scale)
    OX = (SW-DW)//2
    OY = BAR_H + (CH-DH)//2

    # pre-scale image once — this is the hot path
    img_disp = cv2.resize(img_orig, (DW,DH), interpolation=cv2.INTER_AREA)

    # pre-build the static background (BG + image, no overlay)
    # We'll copy this each frame and draw overlays on top — all in numpy, very fast
    base = np.full((SH, SW, 3), 15, dtype=np.uint8)
    base[OY:OY+DH, OX:OX+DW] = img_disp

    def clamp_img(x0,y0,x1,y1):
        return (clamp(x0,OX,OX+DW), clamp(y0,OY,OY+DH),
                clamp(x1,OX,OX+DW), clamp(y1,OY,OY+DH))

    def to_img(cx,cy):
        return (cx-OX)/scale, (cy-OY)/scale

    def apply_ratio(sel,ratio):
        if sel is None or ratio is None: return sel
        x0,y0,x1,y1=norm(sel); w=x1-x0; rw,rh=ratio
        nh=w*rh/rw; max_h=OY+DH-y0
        if nh>max_h: nh=max_h; w=nh*rw/rh
        return (x0,y0,x0+w,y0+nh)

    # state
    ratio       = None
    ratio_label = "Free [0]"
    shift       = False
    sel         = None
    drag_mode   = None
    drag_start  = (0,0)
    move_orig   = None

    def draw():
        # start from pre-built base (fast numpy copy)
        frame = base.copy()

        if sel:
            sx0,sy0,sx1,sy1 = (int(v) for v in norm(sel))
            w,h = sx1-sx0, sy1-sy0

            # dim everything outside selection using numpy slice multiply
            # top
            frame[OY:sy0,   OX:OX+DW] = (frame[OY:sy0,   OX:OX+DW]//3)
            # bottom
            frame[sy1:OY+DH, OX:OX+DW] = (frame[sy1:OY+DH, OX:OX+DW]//3)
            # left
            frame[sy0:sy1,  OX:sx0]   = (frame[sy0:sy1,  OX:sx0]//3)
            # right
            frame[sy0:sy1,  sx1:OX+DW] = (frame[sy0:sy1, sx1:OX+DW]//3)

            # selection border
            cv2.rectangle(frame,(sx0,sy0),(sx1,sy1),ACCENT,1)

            # rule of thirds
            if w>0 and h>0:
                for i in (1,2):
                    cv2.line(frame,(sx0+w*i//3,sy0),(sx0+w*i//3,sy1),THIRDS_COL,1)
                    cv2.line(frame,(sx0,sy0+h*i//3),(sx1,sy0+h*i//3),THIRDS_COL,1)

            # handles
            for name,(hx,hy) in handle_positions(norm(sel)).items():
                hx,hy=int(hx),int(hy); s=HANDLE_SZ
                cv2.rectangle(frame,(hx-s,hy-s),(hx+s,hy+s),(15,15,15),-1)
                cv2.rectangle(frame,(hx-s,hy-s),(hx+s,hy+s),ACCENT,1)

        # top bar
        frame[0:BAR_H] = (20,20,20)
        frame[BAR_H-1] = (40,40,40)

        # ratio label
        cv2.putText(frame, ratio_label, (10, BAR_H-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, ACCENT, 1, cv2.LINE_AA)

        # selection info
        if sel:
            sx0,sy0,sx1,sy1=norm(sel)
            ix0,iy0=to_img(sx0,sy0); ix1,iy1=to_img(sx1,sy1)
            ix0=int(round(clamp(ix0,0,IW))); iy0=int(round(clamp(iy0,0,IH)))
            ix1=int(round(clamp(ix1,0,IW))); iy1=int(round(clamp(iy1,0,IH)))
            txt=f"{ix0},{iy0} -> {ix1},{iy1}  {ix1-ix0}x{iy1-iy0}px"
            cv2.putText(frame,txt,(170,BAR_H-8),
                        cv2.FONT_HERSHEY_SIMPLEX,0.45,INFO_COL,1,cv2.LINE_AA)

        # hint
        hint="Enter/c:crop  r:reset  q:quit  Shift:constrain"
        tw,_ = cv2.getTextSize(hint,cv2.FONT_HERSHEY_SIMPLEX,0.4,1)[0]
        cv2.putText(frame,hint,(SW-tw-10,BAR_H-8),
                    cv2.FONT_HERSHEY_SIMPLEX,0.4,HINT_COL,1,cv2.LINE_AA)

        cv2.imshow("crop", frame)

    # mouse callback
    def on_mouse(event, x, y, flags, _):
        nonlocal sel, drag_mode, drag_start, move_orig, shift
        shift = bool(flags & cv2.EVENT_FLAG_SHIFTKEY)

        if event == cv2.EVENT_LBUTTONDOWN:
            if y < BAR_H: return
            if sel and hit_handle(sel,x,y):
                drag_mode=hit_handle(sel,x,y); drag_start=(x,y); move_orig=norm(sel)
            elif sel and hit_interior(sel,x,y):
                drag_mode='move'; drag_start=(x,y); move_orig=norm(sel)
            else:
                cx=clamp(x,OX,OX+DW); cy=clamp(y,OY,OY+DH)
                drag_mode='create'; drag_start=(cx,cy); sel=(cx,cy,cx,cy)
            draw()

        elif event == cv2.EVENT_MOUSEMOVE and drag_mode:
            if drag_mode=='create':
                x0,y0=drag_start
                x0,y0,x1,y1=constrain(x0,y0,x,y,ratio,shift)
                sel=clamp_img(x0,y0,x1,y1)
            elif drag_mode=='move':
                dx,dy=x-drag_start[0],y-drag_start[1]
                o=move_orig; w,h=o[2]-o[0],o[3]-o[1]
                nx0=clamp(o[0]+dx,OX,OX+DW-w); ny0=clamp(o[1]+dy,OY,OY+DH-h)
                sel=(nx0,ny0,nx0+w,ny0+h)
            else:
                x0,y0,x1,y1=move_orig
                if 'n' in drag_mode: y0=y
                if 's' in drag_mode: y1=y
                if 'w' in drag_mode: x0=x
                if 'e' in drag_mode: x1=x
                x0,y0,x1,y1=constrain_handle(drag_mode,x0,y0,x1,y1,ratio,shift)
                sel=clamp_img(x0,y0,x1,y1)
            draw()

        elif event == cv2.EVENT_LBUTTONUP:
            if sel:
                sx0,sy0,sx1,sy1=norm(sel)
                if abs(sx1-sx0)<MIN_PX or abs(sy1-sy0)<MIN_PX: sel=None
                else: sel=norm(sel)
            drag_mode=None; move_orig=None
            draw()

    cv2.setMouseCallback("crop", on_mouse)
    draw()

    while True:
        key = cv2.waitKey(0) & 0xFF

        if key in (27, ord('q')):   # Escape or q
            break

        elif key in (13, ord('c')): # Enter or c
            if sel:
                sx0,sy0,sx1,sy1=norm(sel)
                ix0,iy0=to_img(sx0,sy0); ix1,iy1=to_img(sx1,sy1)
                ix0=int(round(clamp(ix0,0,IW))); iy0=int(round(clamp(iy0,0,IH)))
                ix1=int(round(clamp(ix1,0,IW))); iy1=int(round(clamp(iy1,0,IH)))
                if ix1-ix0>=1 and iy1-iy0>=1:
                    base2,ext=os.path.splitext(path)
                    bak=base2+".bak"+ext
                    if not os.path.exists(bak): shutil.copy2(path,bak)
                    cv2.imwrite(path, img_orig[iy0:iy1, ix0:ix1])
                    print(f"Saved: {path}  ({ix1-ix0}x{iy1-iy0})")
                    break

        elif key == ord('r'):
            sel=None; draw()

        elif key in RATIOS:
            ratio, rlabel = RATIOS[key]
            ratio_label = f"{rlabel} [{chr(key)}]"
            if sel and ratio: sel=apply_ratio(sel,ratio)
            draw()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
