## Abstract




## How to run
1. Setup
    - Install Python 3.6 and all modules in requirements.txt.
    - Install PostgreSQL (tested with 10.1) and `POSTGRESQL_HOST`, `POSTGRESQL_PORT`, `POSTGRESQL_USER` and `POSTGRESQL_PASSWORD` in *config.py*.
2. Hydrological input data
    - Register at https://cds.climate.copernicus.eu/cdsapp#!/home and obtain access to download datasets.
    - Download snowmelt dataset from https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview. (ERA5-Land hourly data from 1950 to present)
3. Textual input data
    - Download the MUSE repository (https://github.com/facebookresearch/MUSE) to source folder (e.g., *MUSE/supervised.py*)
    - Run *5. get_word_embeddings.py*. This will download word embeddings from Facebook and create multilingual word embeddings using MUSE. This process is a lot faster when Faiss is installed.
4. General
    - Obtain a TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET from Twitter by registering as a developer at Twitter (https://developer.twitter.com/) and set keys in config.py.
    - Run 6. hydrate.py. This obtain text, date and language for tweets in the labelled data and place the hydrated data in data/labeled_data_hydrated.csv.
    - Run 7. create_input_data.py This will read data/labeled_data_hydrated.csv and outputs a pickle with word embeddings and hydrological data per tweet. The data is placed in data/input. 
    - Run 8. experiments.py. This will run all experiments. 
    - Run 9. analyze_results.py. The results of the experiments are placed in the results folder.