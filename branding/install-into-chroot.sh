#!/usr/bin/env bash
# Ember Linux — install the branding pack into a root filesystem
#
# SPDX-License-Identifier: MIT
#
# Usage:
#   sudo ./install-into-chroot.sh [--root DIR] [options]
#
# The script is deliberately conservative: every existing file is backed up,
# unchanged files are left alone, and nothing outside the selected root is
# modified. It can be run in the live root (--root /), in an installed target
# (--root /mnt/gentoo), or against a disposable test root.
#
# It does NOT partition, install packages, erase a disk, or rebuild an ISO.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
ROOT=""
DRY_RUN=0
QUIET=0
LIVE_USER=""
SET_OS_RELEASE=0
REFRESH_GRUB=0
REFRESH_INITRAMFS=0
DEFAULT_SESSION=""
DO_GRUB=1
DO_PLYMOUTH=1
DO_LIGHTDM=1
DO_CALAMARES=1
DO_FONTS=1
DO_ICONS=1
DO_PACK=1
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR=""

usage() {
    cat <<'EOF'
Ember Linux branding installer

  --root DIR              target root (default: /)
  --dry-run               print what would change, modify nothing
  --quiet                 reduce output
  --live-user NAME        also apply desktop defaults to /home/NAME
  --os-release            write an Ember /etc/os-release and /etc/issue
  --default-session NAME  set LightDM user-session (openbox|xfce|plasma|none)
  --refresh-grub          run grub-mkconfig after installing (root / only)
  --refresh-initramfs     rebuild the initramfs after installing (root / only)
  --no-grub               skip GRUB theme and /etc/default/grub
  --no-plymouth           skip Plymouth theme and plymouthd.conf
  --no-lightdm            skip LightDM greeter configuration
  --no-calamares          skip Calamares branding
  --no-fonts              skip Inter
  --no-icons              skip the Ember icon/cursor theme
  --no-pack               do not copy the pack to /usr/share/ember/branding-pack
  -h, --help              this help

Backups live under /var/backups/ember-branding/<timestamp>/ inside the target.
EOF
}

log()  { [ "$QUIET" -eq 1 ] || printf '  %s\n' "$*"; }
info() { [ "$QUIET" -eq 1 ] || printf ':: %s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

while [ $# -gt 0 ]; do
    case "$1" in
        --root)              [ $# -ge 2 ] || die "--root needs a directory"; ROOT="$2"; shift 2 ;;
        --dry-run)           DRY_RUN=1; shift ;;
        --quiet)             QUIET=1; shift ;;
        --live-user)         [ $# -ge 2 ] || die "--live-user needs a name"; LIVE_USER="$2"; shift 2 ;;
        --os-release)        SET_OS_RELEASE=1; shift ;;
        --default-session)   [ $# -ge 2 ] || die "--default-session needs a value"; DEFAULT_SESSION="$2"; shift 2 ;;
        --refresh-grub)      REFRESH_GRUB=1; shift ;;
        --refresh-initramfs) REFRESH_INITRAMFS=1; shift ;;
        --no-grub)           DO_GRUB=0; shift ;;
        --no-plymouth)       DO_PLYMOUTH=0; shift ;;
        --no-lightdm)        DO_LIGHTDM=0; shift ;;
        --no-calamares)      DO_CALAMARES=0; shift ;;
        --no-fonts)          DO_FONTS=0; shift ;;
        --no-icons)          DO_ICONS=0; shift ;;
        --no-pack)           DO_PACK=0; shift ;;
        -h|--help)           usage; exit 0 ;;
        *)                   die "unknown option: $1 (try --help)" ;;
    esac
done

ROOT="${ROOT:-/}"
ROOT="${ROOT%/}"
[ -n "$ROOT" ] || ROOT="/"
[ -d "$ROOT" ] || die "target root does not exist: $ROOT"
[ -d "$ROOT/etc" ] || die "target root has no /etc: $ROOT"
if [ "$ROOT" = "/" ] && [ "$(id -u)" -ne 0 ]; then
    die "installing into / requires root (or use --root with a disposable tree)"
fi

BACKUP_DIR="$ROOT/var/backups/ember-branding/$STAMP"

target_path() {
    case "$ROOT" in
        /) printf '%s' "$1" ;;
        *) printf '%s%s' "$ROOT" "$1" ;;
    esac
}

backup_path() {
    [ "$DRY_RUN" -eq 1 ] && return 0
    local path="$1" rel dest
    { [ -e "$path" ] || [ -L "$path" ]; } || return 0
    rel="${path#"$ROOT"}"
    rel="${rel#/}"
    dest="$BACKUP_DIR/$rel"
    if [ -e "$dest" ] || [ -L "$dest" ]; then
        return 0
    fi
    mkdir -p "$(dirname "$dest")"
    cp -a "$path" "$dest"
    log "backup /$rel"
}

install_file() {
    local src="$SCRIPT_DIR/$1" dest mode
    dest="$(target_path "$2")"
    mode="${3:-644}"
    [ -f "$src" ] || die "missing pack file: $src"
    if [ -f "$dest" ] && cmp -s "$src" "$dest"; then
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        info "would install $2"
        return 0
    fi
    backup_path "$dest"
    mkdir -p "$(dirname "$dest")"
    install -m "$mode" "$src" "$dest"
    log "installed $2"
}

install_tree() {
    local src="$SCRIPT_DIR/$1" dest
    dest="$(target_path "$2")"
    [ -d "$src" ] || die "missing pack directory: $src"
    if [ -d "$dest" ] && diff -qr "$src" "$dest" >/dev/null 2>&1; then
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        info "would install tree $2"
        return 0
    fi
    backup_path "$dest"
    rm -rf "$dest"
    mkdir -p "$dest"
    cp -a "$src/." "$dest/"
    log "installed tree $2"
}

# Replace a line in a small config file, backing it up once if it changes.
replace_line() {
    local file="$1" pattern="$2" replacement="$3" tmp
    [ -f "$file" ] || return 0
    tmp="$(mktemp)"
    cp -a "$file" "$tmp"
    sed -i "s|$pattern|$replacement|" "$tmp"
    if cmp -s "$file" "$tmp"; then
        rm -f "$tmp"
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        info "would update $file"
        rm -f "$tmp"
        return 0
    fi
    backup_path "$file"
    cat "$tmp" > "$file"
    rm -f "$tmp"
    log "updated $file"
}

set_grub_var() {
    local key="$1" value="$2" file tmp
    file="$(target_path /etc/default/grub)"
    tmp="$(mktemp)"
    if [ -f "$file" ]; then
        cp -a "$file" "$tmp"
    else
        {
            printf '# Generated by Ember branding\n'
            printf 'GRUB_DISTRIBUTOR="Gentoo"\n'
        } > "$tmp"
    fi
    if grep -qE "^[#[:space:]]*${key}=" "$tmp"; then
        sed -i "s|^[#[:space:]]*${key}=.*|${key}=\"${value}\"|" "$tmp"
    else
        printf '%s="%s"\n' "$key" "$value" >> "$tmp"
    fi
    if [ -f "$file" ] && cmp -s "$file" "$tmp"; then
        rm -f "$tmp"
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        info "would set $key in /etc/default/grub"
        rm -f "$tmp"
        return 0
    fi
    if [ -f "$file" ]; then
        backup_path "$file"
    fi
    mkdir -p "$(dirname "$file")"
    cat "$tmp" > "$file"
    rm -f "$tmp"
    log "set $key"
}

set_plymouth_theme() {
    local file tmp
    file="$(target_path /etc/plymouth/plymouthd.conf)"
    tmp="$(mktemp)"
    if [ -f "$file" ]; then
        cp -a "$file" "$tmp"
    else
        printf '[Daemon]\n' > "$tmp"
    fi
    if grep -qE '^[#[:space:]]*Theme=' "$tmp"; then
        sed -i 's|^[#[:space:]]*Theme=.*|Theme=ember|' "$tmp"
    elif grep -q '^\[Daemon\]' "$tmp"; then
        sed -i '/^\[Daemon\]/a Theme=ember' "$tmp"
    else
        printf '\n[Daemon]\nTheme=ember\n' >> "$tmp"
    fi
    if [ -f "$file" ] && cmp -s "$file" "$tmp"; then
        rm -f "$tmp"
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        info "would set Plymouth theme to ember"
        rm -f "$tmp"
        return 0
    fi
    if [ -f "$file" ]; then
        backup_path "$file"
    fi
    mkdir -p "$(dirname "$file")"
    cat "$tmp" > "$file"
    rm -f "$tmp"
    log "set Plymouth theme to ember"
}

patch_calamares_settings() {
    local file
    file="$(target_path /etc/calamares/settings.conf)"
    if [ ! -f "$file" ]; then
        warn "no /etc/calamares/settings.conf; install branding as 'default' or set branding: ember manually"
        return 0
    fi
    if grep -qE '^[[:space:]]*branding:[[:space:]]*ember[[:space:]]*$' "$file"; then
        return 0
    fi
    if grep -qE '^[[:space:]]*branding:' "$file"; then
        replace_line "$file" '^[[:space:]]*branding:.*$' 'branding: ember'
        return 0
    fi
    tmp="$(mktemp)"
    cp -a "$file" "$tmp"
    printf '\nbranding: ember\n' >> "$tmp"
    if [ "$DRY_RUN" -eq 1 ]; then
        info "would append branding: ember to /etc/calamares/settings.conf"
        rm -f "$tmp"
        return 0
    fi
    backup_path "$file"
    cat "$tmp" > "$file"
    rm -f "$tmp"
    log "appended branding: ember to /etc/calamares/settings.conf"
}

info "Ember branding → $ROOT"

# ----------------------------------------------------------------------- fonts
if [ "$DO_FONTS" -eq 1 ]; then
    install_tree desktop/fonts/inter /usr/share/fonts/inter
    install_file licenses/OFL-1.1-Inter.txt /usr/share/doc/ember/licenses/OFL-1.1-Inter.txt 644
fi

# ---------------------------------------------------------------- icons/cursors
if [ "$DO_ICONS" -eq 1 ]; then
    install_tree desktop/icons/Ember /usr/share/icons/Ember
fi

# --------------------------------------------------------------------- themes
install_tree desktop/themes/Ember /usr/share/themes/Ember
if [ "$DO_LIGHTDM" -eq 1 ]; then
    install_tree desktop/themes/Ember-Greeter /usr/share/themes/Ember-Greeter
fi

# -------------------------------------------------------------------- rofi
install_file desktop/rofi/ember.rasi /usr/share/rofi/themes/ember.rasi 644
install_file desktop/rofi/config.rasi /etc/xdg/rofi/config.rasi 644
install_file desktop/rofi/config.rasi /etc/skel/.config/rofi/config.rasi 644

# --------------------------------------------------------------- wallpapers
if [ -d "$SCRIPT_DIR/wallpapers" ]; then
    for res in 1920x1080 2560x1440; do
        for name in ember-ridge ember-halo ember-login ember-grub ember-plymouth; do
            install_file "wallpapers/$res/${name}-${res}.png" "/usr/share/backgrounds/ember/${name}-${res}.png" 644
        done
    done
fi

# ------------------------------------------------------------------- pixmaps
install_file identity/ember-logo-256.png /usr/share/pixmaps/ember/ember-logo.png 644
install_file identity/ember-mark-256.png /usr/share/pixmaps/ember/ember-mark.png 644
install_file desktop/pixmaps/ember-avatar.png /usr/share/pixmaps/ember/ember-avatar.png 644

# ------------------------------------------------ identity sources for docs
install_file identity/ember-logo.svg /usr/share/ember/branding/identity/ember-logo.svg 644
install_file identity/ember-mark.svg /usr/share/ember/branding/identity/ember-mark.svg 644
install_file identity/ember-wordmark.svg /usr/share/ember/branding/identity/ember-wordmark.svg 644
install_file identity/ember-lockup.svg /usr/share/ember/branding/identity/ember-lockup.svg 644

# ------------------------------------------------------------------- welcome
install_tree desktop/welcome /usr/share/ember/welcome
install_file copy/installer-copy.md /usr/share/doc/ember/installer-copy.md 644
install_file licenses/NOTICE.md /usr/share/doc/ember/NOTICE.md 644
install_file licenses/CC-BY-SA-4.0.txt /usr/share/doc/ember/licenses/CC-BY-SA-4.0.txt 644
install_file licenses/MIT.txt /usr/share/doc/ember/licenses/MIT.txt 644

# ------------------------------------------------------------------ apps
install_file desktop/bin/ember-welcome /usr/local/bin/ember-welcome 755
install_file desktop/bin/ember-about /usr/local/bin/ember-about 755
install_file desktop/bin/ember-wallpaper /usr/local/bin/ember-wallpaper 755
install_file desktop/applications/ember-welcome.desktop /usr/share/applications/ember-welcome.desktop 644
install_file desktop/applications/ember-about.desktop /usr/share/applications/ember-about.desktop 644

# ------------------------------------------------------------------ openbox
install_file desktop/openbox/rc.xml /etc/xdg/openbox/rc.xml 644
install_file desktop/openbox/menu.xml /etc/xdg/openbox/menu.xml 644
install_file desktop/openbox/autostart /etc/xdg/openbox/autostart 644
install_file desktop/openbox/rc.xml /etc/skel/.config/openbox/rc.xml 644
install_file desktop/openbox/menu.xml /etc/skel/.config/openbox/menu.xml 644
install_file desktop/openbox/autostart /etc/skel/.config/openbox/autostart 644

# -------------------------------------------------------------------- tint2
install_file desktop/tint2/tint2rc /etc/xdg/tint2/tint2rc 644
install_file desktop/tint2/tint2rc /etc/skel/.config/tint2/tint2rc 644

# --------------------------------------------------------------------- gtk
install_file desktop/gtk-3.0/settings.ini /etc/gtk-3.0/settings.ini 644
install_file desktop/gtk-3.0/settings.ini /etc/skel/.config/gtk-3.0/settings.ini 644
install_file desktop/gtk-2.0/gtkrc /etc/gtk-2.0/gtkrc 644

# --------------------------------------------------------------- calamares
if [ "$DO_CALAMARES" -eq 1 ]; then
    install_tree calamares /usr/share/calamares/branding/ember
    patch_calamares_settings
fi

# ------------------------------------------------------------------ lightdm
if [ "$DO_LIGHTDM" -eq 1 ]; then
    install_file boot/lightdm/lightdm-gtk-greeter.conf /etc/lightdm/lightdm-gtk-greeter.conf 644
    install_file boot/lightdm/99-ember.conf /etc/lightdm/lightdm.conf.d/99-ember.conf 644
    if [ -n "$DEFAULT_SESSION" ]; then
        case "$DEFAULT_SESSION" in
            openbox|xfce|plasma|kde|none) ;;
            *) die "--default-session must be openbox, xfce, plasma or none" ;;
        esac
        # Keep the session in its own drop-in. 99-ember.conf stays byte-for-byte
        # identical to the source so reruns do not replace it and lose state.
        session_file="$(target_path /etc/lightdm/lightdm.conf.d/98-ember-session.conf)"
        if [ "$DEFAULT_SESSION" = "none" ]; then
            if [ -e "$session_file" ]; then
                if [ "$DRY_RUN" -eq 1 ]; then
                    info "would remove /etc/lightdm/lightdm.conf.d/98-ember-session.conf"
                else
                    backup_path "$session_file"
                    rm -f "$session_file"
                    log "removed LightDM session override"
                fi
            fi
        else
            session="$DEFAULT_SESSION"
            [ "$session" = "kde" ] && session="plasma"
            tmp="$(mktemp)"
            printf '[Seat:*]\nuser-session=%s\n' "$session" > "$tmp"
            if [ -f "$session_file" ] && cmp -s "$session_file" "$tmp"; then
                rm -f "$tmp"
            elif [ "$DRY_RUN" -eq 1 ]; then
                info "would set LightDM user-session=$session"
                rm -f "$tmp"
            else
                backup_path "$session_file"
                cat "$tmp" > "$session_file"
                rm -f "$tmp"
                log "set LightDM user-session=$session"
            fi
        fi
    fi
fi

# -------------------------------------------------------------------- grub
if [ "$DO_GRUB" -eq 1 ]; then
    if [ -d "$(target_path /boot)" ]; then
        install_tree boot/grub /boot/grub/themes/ember
        set_grub_var GRUB_DISTRIBUTOR "Ember Linux"
        set_grub_var GRUB_THEME "/boot/grub/themes/ember/theme.txt"
        set_grub_var GRUB_TIMEOUT "5"
        set_grub_var GRUB_TIMEOUT_STYLE "menu"
        set_grub_var GRUB_GFXMODE "1920x1080,auto"
        set_grub_var GRUB_GFXPAYLOAD_LINUX "keep"
    else
        warn "no /boot in target; skipped GRUB theme"
    fi
fi

# ---------------------------------------------------------------- plymouth
if [ "$DO_PLYMOUTH" -eq 1 ]; then
    install_tree boot/plymouth/ember /usr/share/plymouth/themes/ember
    if [ -d "$(target_path /etc/plymouth)" ] || command -v plymouth-set-default-theme >/dev/null 2>&1; then
        set_plymouth_theme
        if [ "$ROOT" = "/" ] && command -v plymouth-set-default-theme >/dev/null 2>&1; then
            plymouth-set-default-theme ember >/dev/null 2>&1 || warn "plymouth-set-default-theme failed"
        fi
    else
        warn "Plymouth is not installed; theme staged at /usr/share/plymouth/themes/ember"
        warn "install sys-boot/plymouth, enable dracut's 'plymouth' USE flag, then rebuild the initramfs"
    fi
fi

# ------------------------------------------------------------- live user home
if [ -n "$LIVE_USER" ]; then
    if grep -qE "^${LIVE_USER}:" "$(target_path /etc/passwd)" 2>/dev/null; then
        for rel in \
            .config/openbox/rc.xml .config/openbox/menu.xml .config/openbox/autostart \
            .config/tint2/tint2rc .config/rofi/config.rasi .config/gtk-3.0/settings.ini
        do
            case "$rel" in
                .config/openbox/rc.xml) src=desktop/openbox/rc.xml ;;
                .config/openbox/menu.xml) src=desktop/openbox/menu.xml ;;
                .config/openbox/autostart)
                    if [ -x "$(target_path /usr/bin/calamares)" ]; then
                        src=desktop/openbox/autostart-live
                    else
                        src=desktop/openbox/autostart
                    fi
                    ;;
                .config/tint2/tint2rc) src=desktop/tint2/tint2rc ;;
                .config/rofi/config.rasi) src=desktop/rofi/config.rasi ;;
                .config/gtk-3.0/settings.ini) src=desktop/gtk-3.0/settings.ini ;;
            esac
            install_file "$src" "/home/$LIVE_USER/$rel" 644
        done
        if [ "$DRY_RUN" -eq 0 ]; then
            uid="$(awk -F: -v u="$LIVE_USER" '$1 == u { print $3; exit }' "$(target_path /etc/passwd)")"
            gid="$(awk -F: -v u="$LIVE_USER" '$1 == u { print $4; exit }' "$(target_path /etc/passwd)")"
            if [ -n "$uid" ] && [ -n "$gid" ]; then
                chown -R "$uid:$gid" "$(target_path "/home/$LIVE_USER/.config")" 2>/dev/null || true
            fi
        fi
    else
        warn "user $LIVE_USER not found in target /etc/passwd; skipped home config"
    fi
fi

# --------------------------------------------------------------- os-release
if [ "$SET_OS_RELEASE" -eq 1 ]; then
    tmp="$(mktemp)"
    cat > "$tmp" <<'EOF'
NAME="Ember Linux"
PRETTY_NAME="Ember Linux 1.0"
VERSION_ID="1.0"
VERSION="1.0 (Cinder)"
VERSION_CODENAME=cinder
ID=ember
ID_LIKE=gentoo
HOME_URL="https://emberlinux.org/"
SUPPORT_URL="https://emberlinux.org/help/"
BUG_REPORT_URL="https://emberlinux.org/help/installer"
DOCUMENTATION_URL="https://emberlinux.org/help/"
ANSI_COLOR="38;2;242;106;61"
EOF
    dest="$(target_path /etc/os-release)"
    if [ -f "$dest" ] && cmp -s "$dest" "$tmp"; then
        rm -f "$tmp"
    elif [ "$DRY_RUN" -eq 1 ]; then
        info "would write /etc/os-release"
        rm -f "$tmp"
    else
        backup_path "$dest"
        cat "$tmp" > "$dest"
        rm -f "$tmp"
        log "wrote /etc/os-release"
    fi
    issue_tmp="$(mktemp)"
    printf '\n  Ember Linux 1.0 \e[1;31m"Cinder"\e[0m - Gentoo-based\n\n' > "$issue_tmp"
    dest="$(target_path /etc/issue)"
    if [ -f "$dest" ] && cmp -s "$dest" "$issue_tmp"; then
        rm -f "$issue_tmp"
    elif [ "$DRY_RUN" -eq 1 ]; then
        info "would write /etc/issue"
        rm -f "$issue_tmp"
    else
        backup_path "$dest"
        cat "$issue_tmp" > "$dest"
        rm -f "$issue_tmp"
        log "wrote /etc/issue"
    fi
fi

# --------------------------------------------------------------------- pack
if [ "$DO_PACK" -eq 1 ]; then
    src_real="$(readlink -f "$SCRIPT_DIR")"
    dst="$(target_path /usr/share/ember/branding-pack)"
    case "$src_real" in
        "$dst"|"$dst"/*) log "branding pack already at $dst" ;;
        *)
            if [ -d "$dst" ] && diff -qr "$src_real" "$dst" >/dev/null 2>&1; then
                :
            elif [ "$DRY_RUN" -eq 1 ]; then
                info "would copy the branding pack to /usr/share/ember/branding-pack"
            else
                backup_path "$dst"
                rm -rf "$dst"
                mkdir -p "$dst"
                cp -a "$src_real/." "$dst/"
                log "copied branding pack to /usr/share/ember/branding-pack"
            fi
            ;;
    esac
fi

# ------------------------------------------------------------- caches/refresh
if [ "$DRY_RUN" -eq 0 ] && [ "$ROOT" = "/" ]; then
    if command -v fc-cache >/dev/null 2>&1; then
        fc-cache -f >/dev/null 2>&1 || warn "fc-cache failed"
    fi
    if [ "$DO_ICONS" -eq 1 ] && command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t /usr/share/icons/Ember >/dev/null 2>&1 || true
    fi
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
    fi
    if [ "$REFRESH_GRUB" -eq 1 ] && command -v grub-mkconfig >/dev/null 2>&1; then
        grub-mkconfig -o /boot/grub/grub.cfg >/dev/null 2>&1 || warn "grub-mkconfig failed"
    fi
    if [ "$REFRESH_INITRAMFS" -eq 1 ]; then
        if command -v dracut >/dev/null 2>&1; then
            dracut -f >/dev/null 2>&1 || warn "dracut failed"
        elif command -v plymouth-set-default-theme >/dev/null 2>&1; then
            plymouth-set-default-theme -R ember >/dev/null 2>&1 || warn "plymouth-set-default-theme -R failed"
        fi
    fi
fi

if [ "$DRY_RUN" -eq 1 ]; then
    info "dry run complete; no files were changed"
else
    if [ -d "$BACKUP_DIR" ]; then
        info "done; backups: $BACKUP_DIR"
    else
        info "done"
    fi
fi
