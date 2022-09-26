## Abstract


## Cite as
de Bruijn, Jens A., et al. "Improving the classification of flood tweets with contextual hydrological information in a multimodal neural network." Computers & Geosciences (2020): 104485.

## How to run
1. Setup
    - Install Python 3.6 and all modules in requirements.txt.
    - Install PostgreSQL (tested with 10.1) and `POSTGRESQL_HOST`, `POSTGRESQL_PORT`, `POSTGRESQL_USER` and `POSTGRESQL_PASSWORD` in *config.py*.
2. Hydrological input data
    
3. Textual input data
    - Download the MUSE repository (https://github.com/facebookresearch/MUSE) to source folder (e.g., *MUSE/supervised.py*)
    - Run *5. get_word_embeddings.py*. This will download word embeddings from Facebook and create multilingual word embeddings using MUSE. This process is a lot faster when Faiss is installed.
4. General
