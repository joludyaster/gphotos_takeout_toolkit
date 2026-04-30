import logging
import os
import sys
import time
import exiftool

from pathlib import Path
from typing import Optional
from .sorter import Sorter

logger = logging.getLogger(__name__)


def setup_logging(enable_verbosity: bool = True) -> None:
    """
    Parameters
    ----------
    enable_verbosity : bool, default True
        Whether the logs should be displayed in the console

    Function to set up logging.
    """

    Path("logs").mkdir(parents=True, exist_ok=True)

    error_handler = logging.FileHandler("logs/errors.log", mode="w")
    error_handler.setLevel(logging.ERROR)

    warning_handler = logging.FileHandler("logs/logs.log", mode="w")
    warning_handler.setLevel(logging.WARNING)

    info_handler = logging.FileHandler("logs/logs.log", mode="w")
    info_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(stream=open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False))

    handlers = [
        error_handler,
        warning_handler,
        info_handler,
        stream_handler if enable_verbosity else None
    ]

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
        handlers=filter(None, handlers)
    )


def check_exiftool_existence() -> bool:
    """
    Function to check ExifTool existence in the system

    Returns
    -------
    bool
        True if exists otherwise False
    """
    try:
        with exiftool.ExifToolHelper() as et:
            logger.info(f"ExifTool version: {et.version}")
            logger.info("Installation check successful.")
            return True
    except Exception as e:
        logger.info(f"Installation check failed: {e}")
        logger.info("Ensure 'exiftool' (the command-line tool) is installed and in your PATH.")
        return False


def process_folder(input_path: Path, destination_path: Path, owner: str = "user", additional_file_move: bool = False) -> None:
    """
    Extracted function to process folders

    Parameters
    ----------
    input_path : Path
        Path where Google Photos are located
    destination_path : Path
        Destination folder where the photos will be moved to
    owner : str, default "user"
        Owner of the files [matters not]
    additional_file_move : bool, default False
        Whether all files should be moved into a separate directory, purely for convenience
    """

    old_time = time.time()

    for subdir, dirs, files in os.walk(input_path):
        logger.info(f"Processing folder -> {subdir}")
        logger.info(f"Starting to transport files...")

        gphotos_takeout_toolkit = Sorter(
            origin_path=Path(subdir),
            destination_path=destination_path,
            owner_name=owner,
            files=files,
            additional_file_move=additional_file_move
        )
        gphotos_takeout_toolkit.file_mover()
        logger.info(f"Finished working with {subdir}")

    time_difference = time.time() - old_time
    logger.info("Program finished transporting all of the files.")
    logger.info(f"Program finished its job in {time_difference:.2f}s")


def get_path(question: str) -> Optional[Path]:
    """
    Function to process path, origin and destination

    Parameters
    -------
    question : str
        Message that's asked before the user inputs the path

    Returns
    -------
    Optional[Path]
        Path or None
    """

    path = Path(input(question).replace("\\", "/"))
    if not path.exists():
        logger.error("The path you provided doesn't exist.")
        return None
    return path


def main():

    if not check_exiftool_existence():
        return

    input_path = get_path(question="Enter the path of your Google Photos: ")
    if not input_path:
        return

    destination_path = get_path(question="Enter the destination path where your photos will be moved in to: ")
    if not destination_path:
        return

    owner = input("Enter owner name [default: user]: ").strip() or "user"

    additional_file_move = input("Move all files into one folder? [y/N]: ").strip().lower() == "y"

    enable_verbosity = input("Enable verbosity? [y/N]: ").strip().lower() == "y"

    # Re-setup logging now that we know verbosity preference
    setup_logging(enable_verbosity=enable_verbosity)

    logger.info(f"Starting to process files in folder -> {input_path}")
    try:
        process_folder(
            input_path=input_path,
            destination_path=destination_path,
            owner=owner,
            additional_file_move=additional_file_move
        )
    except Exception:
        logger.exception(f"Something went wrong while processing {input_path}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program was interrupted.")