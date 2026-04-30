import json
import logging
import re
import shutil

from datetime import datetime
from pathlib import Path
from typing import Optional
from .metadata import Metadata

logger = logging.getLogger(__name__)


class Sorter:
    def __init__(
            self,
            origin_path: Path,
            destination_path: Path,
            owner_name: str,
            files: list[str],
            additional_file_move: bool = False
    ):
        """
        Initialize class variables

        Parameters
        ----------
        origin_path : Path
            Folder from where the files will be moved
        destination_path : Path
            Folder to where the files will be moved
        owner_name : str
            Owner of the files [doesn't really matter]
        files : list[str]
            List of files to sort
        additional_file_move : bool, optional
            Whether all the files should be moved into one folder without sorting, by default False
        """

        self.origin_folder = origin_path
        self.files = files
        self.destination_folder = destination_path
        self.owner = owner_name
        self.additional_file_move = additional_file_move

        self.photo_formats = [
            "jpg",
            "jpeg",
            "png",
            "gif",
            "webp",
            "heic",
            "heif",
            "bmp",
            "tiff",
            "tif",
            "raw",
            "arw",  # Sony
            "cr2",  # Canon
            "cr3",  # Canon (newer)
            "dng",  # Adobe / Google Pixel
            "nef",  # Nikon
            "nrw",  # Nikon (compact)
            "orf",  # Olympus
            "raf",  # Fujifilm
            "rw2",  # Panasonic
            "srw",  # Samsung
            "x3f",  # Sigma
            "pef",  # Pentax
        ]

        self.video_formats = [
            "mp4",
            "m4v",
            "mov",
            "avi",
            "wmv",
            "flv",
            "webm",
            "mkv",
            "3gp",
            "3g2",
            "m2ts",
            "mts",
            "mpg",
            "mpeg",
            "ogv",
        ]

        self.photo_folder_format = "photos"
        self.video_folder_format = "videos"
        self.file_folder_format = "files"

    def file_mover(self) -> None:
        """
        Orchestrates file move
        """

        try:
            if not self.origin_folder.exists():
                logger.error(f"The path {self.origin_folder} is not valid.")
                return

            for file in self.files:
                if file.split(".")[-1] == "json":
                    logger.info(f"Skipping {self.origin_folder}/{file}...")
                    continue

                get_metadata = self._get_json_google_photo_data(folder=self.origin_folder, file=file)

                if not get_metadata:
                    logger.error(f"JSON data was not found for the file -> {self.origin_folder}/{file}")
                    self._move_failed_file(
                        file_path=self.origin_folder / file
                    )
                    continue

                if not type(get_metadata) is dict:
                    logger.error("Format of the metadata is not dictionary, skipping...")
                    continue

                get_photo_taken_time = get_metadata.get("photoTakenTime")

                if get_photo_taken_time is None:
                    logger.error(f"Photo taken time was not found. Checking next file...")
                    continue

                get_timestamp = int(get_photo_taken_time.get('timestamp', None))
                if get_timestamp is None:
                    logger.error(f"Photo taken time was not found. Checking next file...")
                    continue

                get_taken_data = datetime.fromtimestamp(get_timestamp)
                format_date = get_taken_data.strftime("%Y-%m-%d").replace("-", "_")

                format_selector = self._get_folder_format(extension=file.rsplit(".", 1)[-1])

                folder = self.destination_folder / format_selector / self.owner / f"{format_selector}_from_{format_date}_by_{self.owner}"

                logger.info(f"Trying to transport {self.origin_folder}/{file}...")

                self._move_file(
                    folder=Path(folder),
                    file=file,
                    metadata=get_metadata
                )

            logger.info(f"Finished transporting files in folder: {self.origin_folder}")

        except Exception:
            logger.exception("Something went wrong while processing information in transport_file() function.")
            return

    @staticmethod
    def _json_matches_file(json_path: Path, filename: str) -> bool:
        """
        This function matches the title of the JSON metadata with the filename itself

        Parameters
        ----------
        json_path : Path
            Path to JSON metadata
        filename : str
            Name of the file

        Returns
        -------
        bool
            Whether the title matches or not
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                title = json.load(f).get("title", "")

            if not title:
                return False

            normalized_filename = re.sub(r"\(\d+\)", "", filename).strip()

            if title == filename or title == normalized_filename:
                return True

            title_stem, _, title_ext = title.rpartition(".")
            file_stem, _, file_ext = normalized_filename.rpartition(".")

            # Match on stem only, ignoring extension mismatch (Google bug where
            # title has wrong extension e.g. "20250809_115744.jpg" for a .MP4 file)
            if title_stem == file_stem:
                return True

            if title_ext.lower() != file_ext.lower():
                return False

            return False

        except Exception:
            return False

    def _get_json_file_path(
            self,
            folder: Path,
            file: str
    ) -> Optional[str]:
        """
        This function searches for the JSON metadata
        file based on the name of the provided file

        Parameters
        ----------
        folder : Path
            Folder to search
        file : str
            Name of the file

        Returns
        -------
        Optional[str]
            JSON metadata or None
        """

        stem, ext = file.rsplit(".", 1) if "." in file else (file, "")
        dedup_stem = re.sub(r"\(\d+\)$", "", stem).rstrip()
        edited_stem = re.sub(r"[-_](edited|edit|bearbeitet|modifié|modificado)$", "", stem, flags=re.IGNORECASE)

        candidates = [
            folder / f"{stem}.json",
            folder / f"{file}.json",
            folder / f"{dedup_stem}.json",
            folder / f"{edited_stem}.json",
            folder / f"{edited_stem}.{ext}.json",
        ]

        SUPP = "supplemental-metadata"
        for i in range(len(SUPP), 0, -1):
            candidates.append(folder / f"{file}.{SUPP[:i]}.json")

        for path in candidates:
            if path.exists() and self._json_matches_file(path, file):
                return str(path)

        try:
            for path in sorted(folder.glob("*.json")):
                if self._json_matches_file(path, file):
                    return str(path)
        except Exception:
            pass

        return None

    def _get_folder_format(
            self,
            extension: str
    ) -> str:
        """
        Function to get a folder format based on the extension

        Parameters
        ----------
        extension : str
            Extension [jpg, jpeg, mp4 etc.]

        Returns
        -------
        str
            Folder format [videos, photos or files]
        """

        if extension.lower() in self.photo_formats:
            return self.photo_folder_format
        elif extension.lower() in self.video_formats:
            return self.video_folder_format

        return self.file_folder_format

    def _get_json_google_photo_data(
            self,
            folder: Path,
            file: str
    ) -> Optional[dict]:
        """
        Function to get JSON metadata and return it as dictionary.

        Parameters
        ----------
        folder : Path
            Folder to search
        file : str
            Name of the file that has a metadata

        Returns
        -------
        Optional[dict]
            JSON metadata or None
        """

        try:
            existing_path = self._get_json_file_path(folder=folder, file=file)

            if not existing_path:
                return None

            with open(existing_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except Exception:
            logger.exception(f"Something went wrong when trying to get JSON data for the file -> {folder}/{file}")
            return None

    @staticmethod
    def _restore_metadata(file_path: Path, metadata: dict) -> bool:
        metadata_restorer = Metadata(
            file_path=file_path,
            metadata=metadata
        )
        result = metadata_restorer.restore()
        return result

    def _move_failed_file(self, file_path: Path) -> bool:
        """
        Function to move a file for which JSON metadata wasn't found, purely for convenience

        Parameters
        ----------
        file_path : Path
            Path to the file that has to be moved

        Returns
        -------
        bool
            True if file was moved successfully, False otherwise
        """
        failed_files_path = self.destination_folder / "failed-files"
        try:
            Path(failed_files_path).mkdir(parents=True, exist_ok=True)
            shutil.copy2(
                src=file_path,
                dst=failed_files_path
            )
            return True
        except Exception:
            logger.exception(f"Failed when copying a failed {file_path} to {failed_files_path}")
            return False

    def _move_file(self, folder: Path, file: str, metadata: dict) -> None:
        """
        Function to move the file

        Parameters
        ----------
        folder : Path
            Folder in which the file will be located
        file : str
            File to move
        metadata : dict
            Metadata of the file
        """

        try:
            folder.mkdir(parents=True, exist_ok=True)
            file_path = folder / file

            if file_path.exists():
                logger.warning(f"The path {folder}/{file} already exists, skipping...")
                return

            if self.additional_file_move:
                Path(self.destination_folder / "all-files").mkdir(parents=True, exist_ok=True)
                shutil.copy2(
                    src=f"{self.origin_folder}/{file}",
                    dst=Path(self.destination_folder) / "all-files"
                )

            shutil.copy2(
                src=f"{self.origin_folder}/{file}",
                dst=folder
            )

            restore_metadata = self._restore_metadata(
                file_path=file_path,
                metadata=metadata
            )

            if not restore_metadata:
                logger.error(f"Couldn't restore metadata for the file: {file_path}")

        except Exception:
            logger.exception(f"Something went wrong while transporting {file} to -> {folder}")
            return
