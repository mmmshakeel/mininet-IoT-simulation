import argparse
import json
import logging
import os.path
import sys

import pandas as pd
import requests


def setup_logging(log_level=logging.INFO, log_file='app.log'):
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def load_config(config_file_path):
    try:
        with open(config_file_path, 'r') as config_file:
            configurations = json.load(config_file)
            logging.info(f"Loaded config from {config_file_path}")
            return configurations
    except FileNotFoundError:
        logging.error(f"Config file {config_file_path} not found")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        logging.error(f"Config file {config_file_path} is not valid JSON")
        sys.exit(1)
    except Exception as e:
        logging.error(e)
        sys.exit(1)


def download_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading data from {url}: {e}")
        sys.exit(1)


def save_file(file_path, data, overwrite=False):
    try:
        if os.path.exists(file_path) and not overwrite:
            logging.info(f"File {file_path} already exists")
            return

        with open(file_path, 'w') as file:
            file.write(data)
    except Exception as e:
        logging.error(f"An error occurred while downloading or saving the file: {e}")


def load_data(url, file_path, columns=None):
    try:
        data = download_data(url)
        save_file(file_path, data)
        return pd.read_csv(file_path, usecols=columns)
    except Exception as e:
        logging.error(f"An error occurred while loading data from {file_path}: {e}")


def get_airport_counts_by_country(airports_df, countries_df):
    # create a new data frame 1st column iso_country and 2nd column airport_count
    airports_per_country = airports_df['iso_country'].value_counts().reset_index()
    airports_per_country.columns = ['iso_country', 'airport_count']

    # merge countries data to get country names
    airports_per_country = airports_per_country.merge(countries_df, left_on='iso_country', right_on='code', how='left')

    print(airports_per_country.head())

    # get top 3 and bottom 10 countries
    top3_countries = airports_per_country.nlargest(3, 'airport_count')
    bottom10_countries = airports_per_country.nsmallest(10, 'airport_count')

    return top3_countries, bottom10_countries


def get_longest_runways_per_country(airports_df, runways_df, countries_df):
    runways_with_airports = runways_df.merge(
        airports_df[['id', 'iso_country', 'name']],
        left_on='airport_ref',
        right_on='id',
        how='left')

    longest_runways = runways_with_airports.loc[runways_with_airports.groupby('iso_country')['length_ft'].idxmax()]
    longest_runways_info = longest_runways[['iso_country', 'name', 'length_ft', 'width_ft']]

    longest_runways_info = longest_runways_info.merge(
        countries_df[['code', 'name']],
        left_on='iso_country',
        right_on='code',
        how='left',
        suffixes=('_airport', '_country'))

    return longest_runways_info[['name_country', 'name_airport', 'length_ft', 'width_ft']]

def main(app_config):
    # load the datasets
    airports_data_df = load_data(
        app_config['airports_dataset_url'],
        app_config['airports_dataset_file_path'],
        ['id', 'name', 'iso_country'])

    countries_data_df = load_data(
        app_config['countries_dataset_url'],
        app_config['countries_dataset_file_path'],
        ['name', 'code'])

    runways_data_df = load_data(
        app_config['runways_dataset_url'],
        app_config['runways_dataset_file_path'],
        ['airport_ref', 'length_ft', 'width_ft'])

    # print(airports_data_df.head())
    # print(countries_data_df.head())
    # print(runways_data_df.head())

    top3_countries, bottom10_countries = get_airport_counts_by_country(airports_data_df, countries_data_df)
    print("Top 3 countries by air port count:")
    print(top3_countries[['name', 'airport_count']])

    print("Bottom 10 countries by air port count:")
    print(bottom10_countries[['name', 'airport_count']])

    longest_runways_per_countries = get_longest_runways_per_country(airports_data_df, runways_data_df, countries_data_df)
    print("Longest runways per country:")
    print(longest_runways_per_countries.to_string())

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Analyze airport and runway data.')
    parser.add_argument('--config', type=str, default='config.json', help='Path to the configuration file')
    args = parser.parse_args()

    # setup logging
    setup_logging()

    # Load configuration
    config = load_config(args.config)

    # Run the main function
    main(config)
