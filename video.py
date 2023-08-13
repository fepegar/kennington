import shutil
import tempfile
from pathlib import Path

import ffmpeg
import streamlit as st
from names_generator import generate_name


class Video:
    def __init__(self, path: Path):
        self.path = path

    @property
    def alias(self) -> str:
        return generate_name(style="capital", seed=hash(self.name))

    @property
    def name(self) -> str:
        return self.path.name

    def show(self) -> None:
        with open(self.path, "rb") as f:
            video_bytes = f.read()
            st.video(video_bytes)

    @property
    def format_name(self) -> str:
        return ffmpeg.probe(self.path)["format"]["format_name"]

    @staticmethod
    def reencode(path: Path) -> None:
        with tempfile.NamedTemporaryFile(suffix=path.suffix, delete=False) as f:
            out_temp_path = f.name
            stream = ffmpeg.input(path)
            stream = ffmpeg.output(
                stream,
                str(out_temp_path),
                pix_fmt="yuv420p",
            )
            ffmpeg.run(stream, overwrite_output=True)
            shutil.move(out_temp_path, path)
        st.toast(f"{path.name} reencoded successfully")

    def check_encoding(self) -> None:
        if self.format_name == "matroska,webm":
            with st.spinner(f'Reencoding "{self.name}"...'):
                self.reencode(self.path)
