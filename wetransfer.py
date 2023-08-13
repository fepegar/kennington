import json
import os
import subprocess
import zipfile
from pathlib import Path

import streamlit as st


WEDL_PATH_ENV = "WEDL_PATH"


class WeTransfer:
    def __init__(self, url: str):
        self.url = self._parse_url(url)

    @staticmethod
    def _parse_url(url: str) -> str:
        """Parse WeTransfer URL to remove tracking information."""
        return url.split("?")[0]

    @staticmethod
    def get_filename(url: str) -> Path | None:
        """Get filename from WeTransfer URL."""
        command = [os.environ[WEDL_PATH_ENV], url, "--info"]
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE)
        json_response = pipe.stdout.read().decode("utf-8")
        try:
            response = json.loads(json_response)
        except json.JSONDecodeError:
            return None
        filename = response["dl_filename"]
        return Path(filename)

    def download(self, force: bool = False) -> Path:
        path = WeTransfer.get_filename(self.url)
        if path is None:
            return None
        if path.is_file() and not force:
            st.toast(f'File "{path}" already exists')
        else:
            with st.spinner(f'Downloading to "{path}"...'):
                command = [
                    os.environ[WEDL_PATH_ENV],
                    self.url,
                    f"--output={path}",
                ]
                pipe = subprocess.Popen(command, stdout=subprocess.PIPE)
                stdout = pipe.stdout.read().decode("utf-8")
                if not path.is_file():
                    raise FileNotFoundError(f"File not downloaded: {stdout}")
                mb = int(path.stat().st_size / 2**20)
                st.toast(f"File downloaded to {path} ({mb} MB)")
        return path

    def unzip(self, zip_path: Path) -> Path:
        out_dir = zip_path.parent / zip_path.stem
        if out_dir.is_dir():
            st.toast(f'Files already exist in "{out_dir}"')
        else:
            with st.spinner(f'Extracting "{zip_path}"...'):
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(out_dir)
                st.toast(f'Files extracted to "{out_dir}"')
        return out_dir
