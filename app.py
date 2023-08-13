from pathlib import Path

import streamlit as st

from video import Video
from wetransfer import WeTransfer


def main() -> None:
    st.title("Thurs Footy @ Kennington")
    url = st.text_input(
        "Enter WeTransfer URL:",
    )

    if st.button("Accept"):
        process(url)


def process(url: str) -> None:
    wetransfer = WeTransfer(url)
    zip_path = wetransfer.download()
    if zip_path is None:
        st.toast(f'Invalid URL: "{url}"')
        return
    videos_dir = wetransfer.unzip(zip_path)
    videos_paths = sorted(videos_dir.iterdir())
    st.write(f"{len(videos_paths)} files found")
    videos = [Video(video_path) for video_path in videos_paths]

    my_bar = st.progress(0)
    for i, video in enumerate(videos):
        my_bar.progress(
            value=i / len(videos),
            text=f"Processing ({i + 1}/{len(videos)})...",
        )
        video.check_encoding()
        st.write(f"**{video.alias}**")
        st.write(Path(video.name))
        video.show()
    my_bar.empty()
    st.toast("All videos processed successfully")


if __name__ == "__main__":
    main()
