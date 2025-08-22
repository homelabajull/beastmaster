######-BEASTS-######

Duyung — Pretty-print a directory tree
Harimau — Smart file finder (glob, regex, filters)
Cacing-pita — Copy files by name/extension into a target folder
Seladang — Copy or move arbitrary files to a target folder
Buaya — Report largest files/dirs (disk usage)
Tapir — Compute or verify SHA256 checksums

---
Run with: bash

./beastmaster.py <beast> [options]
Or:
python3 beastmaster.py <beast> [options]

for help:
python3 beastmaster.py <beast> -h
---

######-HOW TO SUMMON-######

====================Duyung — Selam directory====================
python3 beastmaster.py duyung PATH
Arguments:
- PATH (required): directory to print.

python3 beastmaster.py duyung /mnt/media

====================Harimau — Hunt Files====================
python3 beastmaster.py harimau BASE [options]
Arguments:
- BASE (required): base directory.

Options:
	--name NAME : 	exact filename match.
	--glob PATTERN :	glob pattern, e.g. '*.mkv'.
	--regex REGEX :	regex against filename.
	--min-size N :	minimum size in bytes.
	--max-size N :	maximum size in bytes.
	--changed-within-days N :	only files modified within N days.

python3 beastmaster.py harimau /mnt/media --glob '*.mkv' --changed-within-days 7

====================Cacing Pita — Kage Bunshin No Jutsu====================
python3 beastmaster.py cacing-pita SRC DST [options]
Arguments:
- SRC (required): source directory.
- DST (required): destination directory.

Options:
	--name FILE :	specific filename to copy (repeatable).
	--ext EXT :	extension without dot (repeatable).
	--days N :	only files modified within last N days.
	--limit N :	copy at most N files.
	--overwrite :	allow overwriting existing files.
	--dry-run :	show actions without copying.

python3 beastmaster.py cacing-pita /mnt/media /tmp/subs --ext srt --days 14 --dry-run

====================Seladang — Copy/Move Files====================
python3 beastmaster.py seladang DST FILE... [options]
Arguments:
- DST (required): destination directory.
- FILE... (required): one or more files to copy/move.

Options:
	--move :	move instead of copy.
	--overwrite :	allow overwriting existing files.
	--dry-run :	show actions without changing anything.

python3 beastmaster.py seladang /tmp/target file1.txt file2.mkv --move --overwrite

====================Buaya — Disk Usage Report====================
python3 beastmaster.py buaya BASE [options]
Arguments:
- BASE (required): base directory.

Options:
	--top N : show top N entries (default: 20).
	--dirs : include directories.
	--files : include files.
	*If neither --dirs nor --files is given, both are included.

python3 beastmaster.py buaya /mnt/media --top 30 --files

====================Tapir — Checksums====================
python3 beastmaster.py tapir --compute /mnt/media --output backup.sha256
Modes (one required):
	--compute PATH... : compute checksums for files or directories.
	--verify MANIFEST : verify against a previously saved manifest.

Options:
	--output FILE : write compute output to a file.

python3 beastmaster.py tapir --verify backup.sha256
