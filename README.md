<div align="center" dir="auto">
<pre>
 ██████╗ ██████╗ ███████╗
██╔════╝ ██╔══██╗██╔════╝
██║  ███╗██████╔╝███████╗
██║   ██║██╔═══╝ ╚════██║
╚██████╔╝██║     ███████║
 ╚═════╝ ╚═╝     ╚══════╝
----------------------------
                  google photos sorter                  
</pre>
</div>

## Why did I create this?

Well, my parents asked me to move all of their google photos to an external SSD drive. I saw how many photos they had and didn't want to do it manually so I decided to create an application that will do it for me.

## How to run?

Firstly, I wanna warn you that code creates `photos` or `videos` or `files` folders depending on the file extension, if you want to change it, go ahead, application is all yours.
Application creates folders that look like these:

```
...
├── videos
    ├── user (you could name it however you want, it sets to `user` folder by default)
        ├── photos_from_2024-11-05_by_user
            ├── photo.jpg
```

Okay, now let's see the steps to actually run the project.

> Clone the project on your local machine:
```git
https://github.com/joludyaster/google_photos_sorter.git
```

> In `main.py` in `main()` change variable `owner` to the name of the user you want:
```python
def main():
  ...
  owner = "anything"
```

> Additionally, set `additional_file_move` to `True` if you want all of your files to be moved into one folder, it adds extra space:
```python
def main():
  ...
  additional_file_move = True
```

> Run the project by typing `python main.py` or if you're in IDE, just run the file.

## Dependencies
- [PyExifTool](https://pypi.org/project/PyExifTool/)

## Prerequisites

To run the script, you need to have [ExifTool](https://exiftool.org/) installed on your machine as that is the required tool to restore metadata. Script checks whether you have it installed or not.

> Windows/Mac
```python
https://exiftool.org
```

> Ubuntu
```bash
sudo apt install libimage-exiftool-perl
```

> CentOS/RHEL
```bash
yum install perl-Image-ExifTool
```

> Arch
```bash
sudo pacman -S perl-image-exiftool
```

## Edge cases
Script currently performs well with files that have not been corrupted or incorrectly renamed. But there are cases when this script might break:

### Webp files that were renamed to be .jpg
Google renames files with extensions .webp to .jpg and so when the script tries to restore metadata, error would occur because the file has an invalid extension.

### Files from different apps or sources
If files were added to Google Photos from TikTok, Instagram, or any related social media, Google Takeout modifies the names of those files and it's hard to determine which .json metadata belongs to that file. If you have a solution, feel free to modify the code :D

## Roadmap
* [x] Merge metadata and a file that's being moved 

