# Examples

## Get help

```shell
adreader capture --help
```
## Get initial coordinates

On MacOS keybind is command+shift. Use -K to alter the keybind

```shell
adreader coord
```

## Start capturing

Capture first 3 pages with button

```shell
adreader capture "<title>" --capture -B -P 3
```

Capture until end of pages

```shell
adreader capture <title> --capture
```

# Windows instructions

User powershell
```shell
C:\Users\gigio\PROJS\adreader\.venv\Scripts\activate.bat
C:\Users\gigio\PROJS\adreader\.venv\Scripts\adreader coord -B
```