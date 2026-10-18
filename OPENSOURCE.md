# Open-source components used

All components below are used unmodified as libraries. Versions are those actually installed and
running in the container on IBM LinuxONE (s390x), verified via `python3 -c "import ..."`.

## Machine learning

| Component | Version | Licence | Link |
|---|---|---|---|
| TensorFlow | 2.18.1 | Apache-2.0 | https://github.com/tensorflow/tensorflow |
| Keras | 3.14.0 | Apache-2.0 | https://github.com/keras-team/keras |
| XGBoost | 3.4.1 | Apache-2.0 | https://github.com/dmlc/xgboost |
| scikit-learn | 1.9.0 | BSD-3-Clause | https://github.com/scikit-learn/scikit-learn |
| NumPy | 2.0.2 | BSD-3-Clause | https://github.com/numpy/numpy |
| pandas | 3.0.6 | BSD-3-Clause | https://github.com/pandas-dev/pandas |
| SciPy | 1.13.1 | BSD-3-Clause | https://github.com/scipy/scipy |
| Matplotlib | 3.11.2 | PSF-based | https://github.com/matplotlib/matplotlib |
| ONNX | 1.22.0 | Apache-2.0 | https://github.com/onnx/onnx |

## Large language model runtime

| Component | Version | Licence | Link |
|---|---|---|---|
| llama-cpp-python | 0.3.36 | MIT | https://github.com/abetlen/llama-cpp-python |
| llama.cpp (upstream) | — | MIT | https://github.com/ggml-org/llama.cpp |
| IBM Granite 4.0 (350M base, GGUF) | — | Apache-2.0 | https://github.com/ibm-granite |

The Granite model runs **locally** on the LinuxONE instance via `llama.cpp` compiled with the
`-DGGML_ZDNN=ON` (IBM zDNN / NNPA) and `-DGGML_BLAS=ON` (OpenBLAS, VXE/VXE2) backends. No external
API calls are made and no data leaves the platform.

## Web service

| Component | Version | Licence | Link |
|---|---|---|---|
| FastAPI | 0.143.3 | MIT | https://github.com/fastapi/fastapi |
| Uvicorn | 0.54.0 | BSD-3-Clause | https://github.com/encode/uvicorn |
| Pydantic | 2.14.1 | MIT | https://github.com/pydantic/pydantic |
| pypdf | 6.19.0 | BSD-3-Clause | https://github.com/py-pdf/pypdf |

## Platform and reference material

| Item | Link |
|---|---|
| IBM LinuxONE Community Cloud | https://linuxone.cloud.marist.edu |
| IBM Z and LinuxONE AI/ML lab (base container, sample corpus) | https://github.com/linuxone-community-cloud/jupyter-lab-ml |
| IBM Z Datathon 2026 participant guidebook | https://community.ibm.com/zsystems/datathon/ |

## Data

| Dataset | Source | Use |
|---|---|---|
| Credit Card Fraud Detection (Sparkov / Brandon Harris) | https://www.kaggle.com/datasets/kartik2112/fraud-detection | Training and replay corpus, as distributed inside the IBM LinuxONE AI/ML lab container (`transactions_history.csv`, 245,865 records, 271 frauds) |

Customer profile fields (age band, guardian limit, linked relative, digital activity) are
**generated in-house** by `app/profiles.py` using a deterministic hash of the account identifier.
No real personal data is used.
