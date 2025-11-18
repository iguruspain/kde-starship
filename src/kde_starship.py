#!/usr/bin/env python3
import argparse
import configparser
import json
import shutil
import os
import re
import subprocess
from pathlib import Path

def get_active_color_scheme():
    try:
        result = subprocess.run(
            ["kreadconfig6", "--file", "kdeglobals", "--group", "General", "--key", "ColorScheme"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip() or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        kdeglobals = Path("~/.config/kdeglobals").expanduser()
        if kdeglobals.exists():
            config = configparser.ConfigParser()
            config.read(kdeglobals)
            return config.get("General", "ColorScheme", fallback=None)
    return None

def get_color_scheme_path(scheme_name):
    kde_colors_dir = Path("~/.local/share/color-schemes").expanduser()
    scheme_file = kde_colors_dir / f"{scheme_name}.colors"
    if scheme_file.exists():
        return scheme_file
    return None

def get_color(scheme_path, color_section, color_key):
    config = configparser.ConfigParser()
    config.read(scheme_path)
    try:
        color_value = config.get(color_section, color_key)
        match = re.match(r"#?([0-9A-Fa-f]{6})", color_value)
        if match:
            # Return in format #rrggbb (lowercase)
            return f"#{match.group(1).lower()}"
    except (configparser.NoSectionError, configparser.NoOptionError):
        pass
    return None


def normalize_color(c):
    """Normalize a color value to '#rrggbb' format or return None."""
    if not c:
        return None
    if not isinstance(c, str):
        return None
    s = c.strip()
    m = re.match(r"#?([0-9A-Fa-f]{6})", s)
    if not m:
        return None
    return f"#{m.group(1).lower()}"

def hex_to_rgb(hex_color):
    # Accept format with or without '#'
    if isinstance(hex_color, str) and hex_color.startswith('#'):
        hex_color = hex_color[1:]

    if not isinstance(hex_color, str) or len(hex_color) != 6:
        raise ValueError(f"Invalid hex color value: {hex_color}")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b

def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def get_accent_color():
    try:
        result = subprocess.run(
            ["kreadconfig6", "--file", "kdeglobals", "--group", "General", "--key", "AccentColor"],
            capture_output=True, text=True, check=True
        )
        accent_temp = result.stdout.strip()
        accent_hex = None
        accent_rgb = None
        
        # RGB format (r, g, b)
        if re.fullmatch(r'\d{1,3},\s*\d{1,3},\s*\d{1,3}', accent_temp):
            r, g, b = [int(c.strip()) for c in accent_temp.split(',')]
            accent_hex = rgb_to_hex(r, g, b)
            accent_rgb = (r, g, b)
            return accent_hex, accent_rgb
            
        # Hexadecimal format
        if re.fullmatch(r'#[0-9A-Fa-f]{6}', accent_temp):
            accent_hex = accent_temp
            accent_rgb = hex_to_rgb(accent_hex[1:])
            return accent_hex, accent_rgb
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    return None, None

def better_contrast_selection(base_color, colors=None):
    if colors is None:
        colors = []

    def srgb_channel_to_linear(c8):
        c = c8 / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    def luminance_from_rgb(rgb):
        r, g, b = rgb
        return 0.2126 * srgb_channel_to_linear(r) + \
               0.7152 * srgb_channel_to_linear(g) + \
               0.0722 * srgb_channel_to_linear(b)

    def contrast_ratio(lum1, lum2):
        L1, L2 = max(lum1, lum2), min(lum1, lum2)
        return (L1 + 0.05) / (L2 + 0.05)

    # normalize base_color and compute luminance
    base_rgb = hex_to_rgb(base_color)
    base_lum = luminance_from_rgb(base_rgb)

    best_color = None
    best_contrast = -1.0

    for c in colors:
        if not c:
            continue
        rgb = hex_to_rgb(c)
        lum = luminance_from_rgb(rgb)
        cr = contrast_ratio(base_lum, lum)
        if cr > best_contrast:
            best_contrast = cr
            best_color = c

    # If there are no valid candidates, choose between black/white
    if best_color is None:
        black_lum = luminance_from_rgb(hex_to_rgb('#000000'))
        white_lum = luminance_from_rgb(hex_to_rgb('#ffffff'))
        bcr = contrast_ratio(base_lum, black_lum)
        wcr = contrast_ratio(base_lum, white_lum)
        return '#000000' if bcr >= wcr else '#ffffff'

    return best_color

def darkest_brightest_color(colors):
    """Return the darkest and brightest colors from a list of hex colors."""
    if not colors:
        return '#000000', '#ffffff'
    
    # Filter out None values and normalize colors
    valid_colors = [normalize_color(c) for c in colors if normalize_color(c)]
    
    if not valid_colors:
        return '#000000', '#ffffff'
    
    def srgb_channel_to_linear(c8):
        c = c8 / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    def luminance_from_rgb(rgb):
        r, g, b = rgb
        return 0.2126 * srgb_channel_to_linear(r) + \
               0.7152 * srgb_channel_to_linear(g) + \
               0.0722 * srgb_channel_to_linear(b)
    
    darkest = valid_colors[0]
    brightest = valid_colors[0]
    min_lum = luminance_from_rgb(hex_to_rgb(darkest))
    max_lum = min_lum
    
    for color in valid_colors[1:]:
        rgb = hex_to_rgb(color)
        lum = luminance_from_rgb(rgb)
        
        if lum < min_lum:
            min_lum = lum
            darkest = color
        
        if lum > max_lum:
            max_lum = lum
            brightest = color
    
    return darkest, brightest

def build_starship_palette(scheme_path, accent_hex):
    # Load pywal colors
    json_path = Path('~/.cache/wal/colors.json').expanduser()
    special = {}
    colors = {}
    if json_path.exists():
        with open(json_path, 'r') as jf:
            data = json.load(jf)
            special = data.get('special', {})
            colors = data.get('colors', {})
        if accent_hex is None:
            accent_hex = colors.get('color1', '#ff0000')
        term_text = special.get('foreground', None)
    else:
        if accent_hex is None:
            accent_hex = '#ff0000'
        term_text = get_color(scheme_path, "Colors:Window", "ForegroundNormal")

    # Normalize `accent_hex` to a '#rrggbb' string
    accent_hex = normalize_color(accent_hex)
    text = normalize_color(get_color(scheme_path, "Colors:Window", "ForegroundNormal"))
    text2 = normalize_color(get_color(scheme_path, "Colors:Selection", "ForegroundActive"))
    term_text = normalize_color(special.get('foreground', None))
    accent_text = better_contrast_selection(accent_hex, [text, text2, term_text])
    dir_bg = normalize_color(get_color(scheme_path, "Colors:View", "DecorationHover"))
    other_bg = normalize_color(get_color(scheme_path, "Colors:View", "DecorationFocus"))
    git_bg = normalize_color(get_color(scheme_path, "Colors:Window", "BackgroundAlternate"))
    dir_fg = normalize_color(get_color(scheme_path, "Colors:Selection", "DecorationFocus"))
    other_fg = normalize_color(get_color(scheme_path, "Colors:View", "DecorationHover"))
    git_fg = normalize_color(get_color(scheme_path, "Colors:Window", "ForegroundInactive"))
    dir_text = better_contrast_selection(dir_bg, [dir_fg, text, text2, term_text])
    other_text = better_contrast_selection(other_bg, [other_fg, text, text2, term_text])

    return {
        'accent': accent_hex,
        'accent_text': accent_text,
        'dir_bg': dir_bg,
        'dir_fg': dir_fg,
        'dir_text': dir_text,
        'git_bg': git_bg,
        'git_fg': git_fg,
        'other_bg': other_bg,
        'other_fg': other_fg,
        'other_text': other_text,
        'text': text,
        'text2': text2
    }

def gen_starship_config(palette, template_file):
    # Accept either a Path or a string; expand variables/users if needed
    if isinstance(template_file, (str,)):
        template_path = Path(os.path.expanduser(os.path.expandvars(template_file)))
    else:
        template_path = Path(template_file)

    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    with open(template_path, 'r') as f:
        template = f.read()


    # replace colors in the template only in the [palette.colors] or [palettes.colors] section
    # Support both `{key}` and `{{key}}` placeholder styles.
    # Find the section header robustly (match as a line) so slight differences (plural) are handled.
    m = re.search(r"^\[(?:palette|palettes)\.colors\]\s*$", template, flags=re.M)
    if not m:
        return template

    # start index is the beginning of the matched header line
    start_index = m.start()
    # search for the next section header (a line that starts with '[') after the header
    rest = template[m.end():]
    m2 = re.search(r"^\[", rest, flags=re.M)
    if m2:
        end_index = m.end() + m2.start()
    else:
        end_index = len(template)

    palette_section = template[start_index:end_index]

    # Update existing key assignments inside the palette section (e.g. "accent = '#112233'")
    # If a key from `palette` exists, replace its RHS with the generated color.
    # If it does not exist, append a new line with the assignment at the end of the section.
    for key, color in palette.items():
        if not isinstance(color, str):
            continue
        # pattern matches a line that starts with the key followed by '=' and anything
        pat = re.compile(rf"^\s*{re.escape(key)}\s*=.*$", flags=re.M)
        replacement = f"{key} = '{color}'"
        if pat.search(palette_section):
            palette_section = pat.sub(replacement, palette_section)
        else:
            # ensure palette_section ends with a newline before appending
            if not palette_section.endswith('\n'):
                palette_section += '\n'
            palette_section += replacement + '\n'

    template = template[:start_index] + palette_section + template[end_index:]

    return template

def refresh_starship():
    if subprocess.run(['pgrep', 'kitty'], capture_output=True).stdout:
        subprocess.run(['pkill', 'kitty'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        subprocess.Popen(
            ['kitty'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def main():
    parser = argparse.ArgumentParser(description="Generate Starship configuration based on the active KDE color scheme.")
    parser.add_argument('-o', '--output', type=str, required=True, help="output file for the generated Starship configuration.")
    parser.add_argument('-t', '--template', type=str, required=True, help="template file for the Starship configuration.")
    parser.add_argument('-c', '--accent-color', type=str, dest='accent_color', default=None, help="optional accent color in hex format (e.g., #ff0000). If not provided, the system accent color will be used.")
    parser.add_argument('-r', '--restart', dest='restart_starship', action='store_true', help="restart Starship instance after generation.")
    args = parser.parse_args()

    scheme_name = get_active_color_scheme()
    if not scheme_name:
        print("Could not determine the active KDE color scheme.")
        return

    scheme_path = get_color_scheme_path(scheme_name)
    if not scheme_path:
        print(f"Could not find color scheme file: {scheme_name}")
        return

    accent_hex = args.accent_color if args.accent_color else get_accent_color()[0]

    # Expand user and env vars for template and output paths
    template_path = os.path.expanduser(os.path.expandvars(args.template))
    output_path = os.path.expanduser(os.path.expandvars(args.output))

    # Ensure template exists before proceeding
    if not Path(template_path).exists():
        print(f"Could not find template file: {template_path}")
        return

    palette = build_starship_palette(scheme_path, accent_hex)
    #print("Generated color palette:", palette)
    
    try:
        starship_config = gen_starship_config(palette, template_path)
    except FileNotFoundError as e:
        print(str(e))
        return

    # Ensure output directory exists
    out_dir = Path(output_path).expanduser().parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # backup existing file with shutil
    if os.path.exists(output_path):
        backup_path = output_path + ".bak"
        shutil.copy2(output_path, backup_path)

    with open(output_path, 'w') as f:
        f.write(starship_config)

    if args.restart_starship:
        refresh_starship()
    #print(f"Starship configuration generated at: {output_path}")

if __name__ == "__main__":
    main()
