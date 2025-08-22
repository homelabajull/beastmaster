# 🐾 Beastmaster

A collection of command-line **beasts** to help tame your filesystem.
Each beast has its own ability:

* 🧜 **Duyung** — Pretty-print a directory tree
* 🐅 **Harimau** — Smart file finder (glob, regex, filters)
* 🪱 **Cacing-pita** — Copy files by name/extension into a target folder
* 🐂 **Seladang** — Copy or move arbitrary files to a target folder
* 🐊 **Buaya** — Report largest files/dirs (disk usage)
* 🦣 **Tapir** — Compute or verify SHA256 checksums

---

## 🚀 Run

```bash
# Using bash directly
./beastmaster.py <beast> [options]

# Or with Python
python3 beastmaster.py <beast> [options]
```

For help on a specific beast:

```bash
python3 beastmaster.py <beast> -h
```

---

## 📖 How to Summon

### Duyung — *Selam directory*

Pretty-print a directory tree.

```bash
python3 beastmaster.py duyung PATH
```

* **PATH** *(required)*: directory to print.

Example:

```bash
python3 beastmaster.py duyung /mnt/media
```

---

### Harimau — *Hunt Files*

Find files with smart filters.

```bash
python3 beastmaster.py harimau BASE [options]
```

* **BASE** *(required)*: base directory.

**Options:**

* `--name NAME` → exact filename match
* `--glob PATTERN` → glob pattern, e.g. `'*.mkv'`
* `--regex REGEX` → regex against filename
* `--min-size N` → minimum size (bytes)
* `--max-size N` → maximum size (bytes)
* `--changed-within-days N` → files modified within N days

Example:

```bash
python3 beastmaster.py harimau /mnt/media --glob '*.mkv' --changed-within-days 7
```

---

### Cacing-pita — *Kage Bunshin No Jutsu* on specific files

Clone files into a target folder.

```bash
python3 beastmaster.py cacing-pita SRC DST [options]
```

* **SRC** *(required)*: source directory
* **DST** *(required)*: destination directory

**Options:**

* `--name FILE` → copy specific filename (repeatable)
* `--ext EXT` → copy by extension, no dot (repeatable)
* `--days N` → only files modified in last N days
* `--limit N` → copy at most N files
* `--overwrite` → allow overwriting
* `--dry-run` → show actions without copying

Example:

```bash
python3 beastmaster.py cacing-pita /mnt/media /tmp/subs --ext srt --days 14 --dry-run
```

---

### Seladang — Tukang Pindah File

```bash
python3 beastmaster.py seladang DST FILE... [options]
```

* **DST** *(required)*: destination directory
* **FILE...** *(required)*: one or more files

**Options:**

* `--move` → move instead of copy
* `--overwrite` → allow overwriting
* `--dry-run` → show actions only

Example:

```bash
python3 beastmaster.py seladang /tmp/target file1.txt file2.mkv --move --overwrite
```

---

### Buaya — Usha Disk Usage

```bash
python3 beastmaster.py buaya BASE [options]
```

* **BASE** *(required)*: base directory

**Options:**

* `--top N` → show top N entries (default: 20)
* `--dirs` → include directories
* `--files` → include files
  *(if neither is given, both are included)*

Example:

```bash
python3 beastmaster.py buaya /mnt/media --top 30 --files
```

---

### Tapir — *Checksums* checker

```bash
python3 beastmaster.py tapir MODE [options]
```

**Modes (one required):**

* `--compute PATH...` → compute checksums
* `--verify MANIFEST` → verify against saved manifest

**Options:**

* `--output FILE` → write compute output to file

Examples:

```bash
# Compute
python3 beastmaster.py tapir --compute /mnt/media --output backup.sha256

# Verify
python3 beastmaster.py tapir --verify backup.sha256
```

---
