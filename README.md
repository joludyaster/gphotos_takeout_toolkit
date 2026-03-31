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

> In `google_photos_sorter.py` change variable `owner` to the name of the user you want:
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

> Run the project by typing `python google_photos_sorter.py` or if you're in IDE, just run the file.

## Roadmap
* [ ] Merge metadata and a file that's being moved 