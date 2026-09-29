#!/usr/bin/env python3

"""
===============
POV-Ray Mosaic
===============
-----------------------------------------------------------------------
Converting 2D images into mosaic of solid 3D objects in POV-Ray format.
-----------------------------------------------------------------------

Input: PNG, PPM, PGM.

Output: POV-Ray.

History:
--------

1.14.1.0    Single task standalone programs 63zaika, 44zaika and 36zaika
replaced with common GUI and zaika63, zaika44 and zaika36 modules correspondingly.
Apparently PNM input support added with PyPNM; PNG support reworked to more common.

1.16.20.20  New minimalistic menu-based GUI.

1.27.4.22   Keep having usability improvements.

1.33.29.9 Since version 2 development is being restarted again,
    version 1 gets one more maintenance update.

    "But this time will be the last!" (c) Soviet anecdote.

---
Main site: `The Toad's Slimy Mudhole`_ - more Python freeware developed by Ilyich the Toad.

`POV-Ray Mosaic`_ page with info and renderings.

POV-Ray Mosaic Git repositories `@Github`_ and `@Gitflic`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

.. _POV-Ray Mosaic: https://dnyarri.github.io/povzaika.html

.. _@Github: https://github.com/Dnyarri/POVmosaic

.. _@Gitflic: https://gitflic.ru/project/dnyarri/povmosaic

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2025-2026 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.33.29.9'  # 29 Sep 2026
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from pathlib import Path
from random import randbytes  # Used for random icon only
from time import ctime
from tkinter import Button, Frame, Label, Menu, PhotoImage, Tk, filedialog
from tkinter.messagebox import showinfo

from povzaika import zaika36, zaika44, zaika63
from pypng import png2list
from pypnm import list2bin, pnm2list


def DisMiss(event=None) -> None:
    """Kill dialog and continue."""

    sortir.destroy()


def ShowMenu(event) -> None:
    """Pop menu up (or sort of drop it down)."""

    menu_file.post(event.x_root, event.y_root)


def ShowInfo(event=None) -> None:
    """Show image information."""

    file_size = Path(sourcefilename).stat().st_size
    file_size_str = f'{file_size / 1048576:.2f} Mb' if (file_size > 1048576) else f'{file_size / 1024:.2f} Kb' if (file_size > 1024) else f'{file_size} bytes'
    showinfo(
        title='Image information',
        message=f'File properties:\nLocation: {sourcefilename}\nSize: {file_size_str}\nLast modified: {ctime(Path(sourcefilename).stat().st_mtime)}',
        detail=f'Image properties, as represented internally:\nWidth: {X} px\nHeight: {Y} px\nChannels: {Z} channel{"s" if Z > 1 else ""}\nColor depth: {maxcolors + 1} gradations/channel',
    )


def UINormal() -> None:
    """Normal UI state, buttons enabled."""

    for widget in frame_img.winfo_children():
        if widget.winfo_class() in ('Label', 'Button'):
            widget['state'] = 'normal'
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])
    sortir.update()


def UIBusy() -> None:
    """Busy UI state, buttons disabled."""

    for widget in frame_img.winfo_children():
        if widget.winfo_class() in ('Label', 'Button'):
            widget['state'] = 'disabled'
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.update()


def UIFit() -> None:
    """Readopting 'sortir.minsize' to fit the screen."""

    sortir.update()
    fit_width, fit_height = (
        min(sortir.winfo_reqwidth(), 9 * sortir.winfo_screenwidth() // 10),
        min(sortir.winfo_reqheight(), 9 * sortir.winfo_screenheight() // 10),
    )
    sortir.minsize(fit_width, fit_height)


def GetSource(event=None) -> None:
    """Open source image and redefine other controls state."""

    global zoom_factor, zoom_do, zoom_show, preview, preview_data
    global sourcefilename, X, Y, Z, maxcolors, image3D
    global info_normal

    zoom_factor = 0

    old_sourcefilename = sourcefilename  # Temporary saving info in case of "Open.." cancel
    sourcefilename = filedialog.askopenfilename(
        title='Open image file',
        filetypes=[
            ('Supported formats', '.png .ppm .pgm .pbm .pnm'),
            ('Portable network graphics', '.png'),
            ('Portable any map', '.ppm .pgm .pbm .pnm'),
        ],
    )
    if sourcefilename == '':
        sourcefilename = old_sourcefilename
        return

    info_normal = {'txt': f'{Path(sourcefilename).name}', 'fg': 'grey', 'bg': 'grey90'}

    UIBusy()

    if Path(sourcefilename).suffix.lower() == '.png':
        # ↓ Reading image as list
        X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    elif Path(sourcefilename).suffix.lower() in ('.ppm', '.pgm', '.pbm', '.pnm'):
        # ↓ Reading image as list
        X, Y, Z, maxcolors, image3D = pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)

    preview = PhotoImage(data=preview_data)

    zoom_show = {  # What to show below preview
        -4: 'Zoom 1:5',
        -3: 'Zoom 1:4',
        -2: 'Zoom 1:3',
        -1: 'Zoom 1:2',
        0: 'Zoom 1:1',
        1: 'Zoom 2:1',
        2: 'Zoom 3:1',
        3: 'Zoom 4:1',
        4: 'Zoom 5:1',
    }
    zoom_do = {  # What to do to preview; "zoom" zooms in, "subsample" zooms out
        -4: preview.subsample(5, 5),
        -3: preview.subsample(4, 4),
        -2: preview.subsample(3, 3),
        -1: preview.subsample(2, 2),
        0: preview,  # 1:1
        1: preview.zoom(2, 2),
        2: preview.zoom(3, 3),
        3: preview.zoom(4, 4),
        4: preview.zoom(5, 5),
    }

    if X + 16 > sortir.winfo_screenwidth() or Y + 152 > sortir.winfo_screenheight():
        zoomOut()  # We'be better be on a safe side of the zoom
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none', background=zanyato.master['background'], relief='flat', borderwidth=1)
    zanyato.pack_configure(pady=max(0, 16 - (preview.height() // 2)))
    # ↓ Binding everything that need opened image
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Control-+>', zoomIn)
    zanyato.bind('<Control-=>', zoomIn)
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    zanyato.bind('<Control-minus>', zoomOut)
    zanyato.bind('<Control-Key-1>', zoomOne)
    sortir.bind_all('<MouseWheel>', zoomWheel)  # Wheel
    sortir.bind_all('<Control-i>', ShowInfo)
    # ↓ enabling zoom buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    # ↓ updating zoom label display
    label_zoom.config(text=zoom_show[zoom_factor])
    # ↓ enabling "Save as..."
    menu_file.entryconfig('Export 6³ Mosaic...', state='normal')  # Instead of name numbers from 0 may be used
    menu_file.entryconfig('Export 4⁴ Mosaic...', state='normal')
    menu_file.entryconfig('Export 3⁶ Mosaic...', state='normal')
    menu_file.entryconfig('Image Info...', state='normal')
    UINormal()
    UIFit()
    sortir.geometry(f'{sortir.winfo_reqwidth()}x{sortir.winfo_reqheight()}+{(sortir.winfo_screenwidth() - sortir.winfo_reqwidth()) // 2}+64')
    zanyato.focus_set()


def SaveAs63() -> None:
    """Once selected Export 6³ Mosaic..."""

    savefilename = filedialog.asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov'),
            ('All Files', '*.*'),
        ],
        defaultextension='.pov',
        initialfile=Path(sourcefilename).stem + '_Mosaic_63.pov',
    )
    if savefilename == '':
        return
    UIBusy()
    zaika63.zaika63(image3D, maxcolors, savefilename)
    UINormal()


def SaveAs44() -> None:
    """Once selected Export 4⁴ Mosaic..."""

    savefilename = filedialog.asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov'),
            ('All Files', '*.*'),
        ],
        defaultextension='.pov',
        initialfile=Path(sourcefilename).stem + '_Mosaic_44.pov',
    )
    if savefilename == '':
        return
    UIBusy()
    zaika44.zaika44(image3D, maxcolors, savefilename)
    UINormal()


def SaveAs36() -> None:
    """Once selected Export 3⁶ Mosaic..."""

    savefilename = filedialog.asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov'),
            ('All Files', '*.*'),
        ],
        defaultextension='.pov',
        initialfile=Path(sourcefilename).stem + '_Mosaic_36.pov',
    )
    if savefilename == '':
        return
    UIBusy()
    zaika36.zaika36(image3D, maxcolors, savefilename)
    UINormal()


def zoomIn(event=None) -> None:
    """Zoom preview in."""

    global zoom_factor, preview
    zoom_factor = min(zoom_factor + 1, 4)  # max zoom 5
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none')
    UIFit()
    # ↓ updating zoom factor display
    label_zoom.config(text=zoom_show[zoom_factor])
    # ↓ reenabling +/- buttons
    butt_minus.config(state='normal', cursor='hand2')
    if zoom_factor == 4:  # max zoom 5
        butt_plus.config(state='disabled', cursor='arrow')
    else:
        butt_plus.config(state='normal', cursor='hand2')


def zoomOut(event=None) -> None:
    """Zoom preview out."""

    global zoom_factor, preview
    zoom_factor = max(zoom_factor - 1, -4)  # min zoom 1/5
    # preview = PhotoImage(data=preview_data)
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none')
    UIFit()
    # ↓ updating zoom factor display
    label_zoom.config(text=zoom_show[zoom_factor])
    # ↓ reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    if zoom_factor == -4:  # min zoom 1/5
        butt_minus.config(state='disabled', cursor='arrow')
    else:
        butt_minus.config(state='normal', cursor='hand2')


def zoomOne(event=None) -> None:
    """Zoom 1:1."""

    global zoom_factor, preview

    zoom_factor = 0
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none')
    UIFit()
    # ↓ updating zoom factor display
    label_zoom.config(text=zoom_show[zoom_factor])
    # ↓ Reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    sortir.update()


def zoomWheel(event) -> None:
    """zoomIn or zoomOut by mouse wheel."""

    if event.delta < 0:
        zoomOut()
    if event.delta > 0:
        zoomIn()


""" ╔═══════════╗
    ║ Main body ║
    ╚═══════════╝ """

zoom_factor = 0
sourcefilename = X = Y = Z = maxcolors = None

# ↓ Info statuses dictionaries
info_normal = {
    'txt': f'POV-Ray Mosaic {__version__}',
    'fg': 'grey',
    'bg': 'grey90',
}
info_busy = {
    'txt': 'BUSY, PLEASE WAIT',
    'fg': 'red',
    'bg': 'yellow',
}

sortir = Tk()
sortir.title('POV-Ray Mosaic')
sortir.iconphoto(True, PhotoImage(data=b''.join(('P6\n4 4\n255\n'.encode(encoding='ascii'), randbytes(4 * 4 * 3)))))

# ↓ Info string
info_string = Label(
    sortir,
    text=info_normal['txt'],
    font=('courier', 7),
    foreground=info_normal['fg'],
    background=info_normal['bg'],
    relief='groove',
)
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')

menu_file = Menu(sortir, tearoff=False)  # Drop-down
menu_file.add_command(label='Open...', state='normal', accelerator='Ctrl+O', command=GetSource)
menu_file.add_separator()
menu_file.add_command(label='Export 6³ Mosaic...', state='disabled', command=SaveAs63)
menu_file.add_command(label='Export 4⁴ Mosaic...', state='disabled', command=SaveAs44)
menu_file.add_command(label='Export 3⁶ Mosaic...', state='disabled', command=SaveAs36)
menu_file.add_separator()
menu_file.add_command(label='Image Info...', accelerator='Ctrl+I', state='disabled', command=ShowInfo)
menu_file.add_separator()
menu_file.add_command(label='Exit', state='normal', accelerator='Ctrl+Q', command=DisMiss)

frame_img = Frame(sortir, borderwidth=2, relief='groove')
frame_img.pack(side='top', anchor='center', expand=True)

zanyato = Label(
    frame_img,
    text='Preview area.\n  Double click to open image,\n  Right click or Alt+F for "File..." menu.\nWith image opened,\n  Ctrl+Click to zoom in,\n  Alt+Click to zoom out,\n  Ctrl+1 to zoom 1:1,\n  Wheel to zoom in/out.',
    font=('helvetica', 12),
    justify='left',
    borderwidth=2,
    padx=24,
    pady=24,
    relief='groove',
    background='grey90',
    cursor='arrow',
)
zanyato.pack(side='top', padx=0, pady=(0, 2))

frame_zoom = Frame(frame_img, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text='Zoom 1:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

# ↓ Binding everything that does not need opened image
zanyato.bind('<Double-Button-1>', GetSource)
frame_img.bind('<Double-Button-1>', GetSource)
sortir.bind('<Button-3>', ShowMenu)
sortir.bind_all('<Alt-f>', ShowMenu)
sortir.bind_all('<Alt-F>', ShowMenu)
sortir.bind_all('<Control-o>', GetSource)
sortir.bind_all('<Control-O>', GetSource)
sortir.bind_all('<Control-q>', DisMiss)
sortir.bind_all('<Control-Q>', DisMiss)
sortir.bind_all('<Control-w>', DisMiss)
sortir.bind_all('<Control-W>', DisMiss)

# ↓ Center window horizontally, +64 vertically
sortir.update()
h_spacer = max(frame_img.winfo_reqwidth(), info_string.winfo_reqwidth())
v_spacer = sortir.winfo_reqheight()
sortir.minsize(h_spacer, v_spacer)
sortir.geometry(f'{sortir.winfo_reqwidth()}x{sortir.winfo_reqheight()}+{(sortir.winfo_screenwidth() - sortir.winfo_reqwidth()) // 2}+64')
sortir.mainloop()
