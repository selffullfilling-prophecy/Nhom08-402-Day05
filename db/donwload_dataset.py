from pathlib import Path
import argparse
import shutil

import kagglehub


DEFAULT_DATASET = "sayeeduddin/netflix-2025user-behavior-dataset-210k-records"


def copy_dataset(source_dir: Path, destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)

    for item in source_dir.iterdir():
        target = destination_dir / item.name

        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a Kaggle dataset and store it in the project's dataset folder."
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help="Kaggle dataset handle in the format owner/dataset-name.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    dataset_dir = project_root / "dataset"

    print(f"Downloading dataset: {args.dataset}")
    cached_path = Path(kagglehub.dataset_download(args.dataset))
    print(f"Downloaded to Kaggle cache: {cached_path}")

    copy_dataset(cached_path, dataset_dir)
    print(f"Dataset copied to: {dataset_dir}")


if __name__ == "__main__":
    main()
