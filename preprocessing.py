"""
File to preprocess the data.
"""

import pandas as pd


class PreprocessData:
    def __init__(self, file_path):
        """
        Initialize the PreprocessData class with the file path.

        :param file_path: Path to the CSV file containing the data.
        """
        self.file_path = file_path
        self.data = None

    def load_data(self) -> None:
        """
        Load the data from the CSV file.
        """
        self.data = pd.read_csv(self.file_path)

    def export_df_to_csv(self, output_path: str) -> None:
        """
        Export the DataFrame to a CSV file.

        :param output_path: Path where the CSV file will be saved.
        """
        assert self.data is not None, "Data not loaded. Please load the data first."
        assert output_path is not None, "Output path not loaded. Please load the data first."

        self.data.to_csv(output_path, index=False)

    def export_df_to_value(self) -> pd.DataFrame:
        """
        Export the DataFrame to a value.

        :return: DataFrame containing the data.
        """
        assert self.data is not None, "Data not loaded. Please load the data first."

        return self.data

    def check_missing_values(self) -> pd.DataFrame:
        """
        Check for missing values in the data.

        :return: DataFrame with missing values.
        """
        assert self.data is not None, "Data not loaded. Please load the data first."

        return self.data.isnull().sum()

    def check_duplicates_values(self) -> pd.DataFrame:
        """
        Check for duplicate values in the data.

        :return: DataFrame with duplicate values.
        """
        assert self.data is not None, "Data not loaded. Please load the data first."

        return self.data.duplicated().sum()

    def fill_missing_values(self, method="mean") -> None:
        """
        Fill missing values in the data.

        :param method: Method to fill missing values ('mean', 'median').
        """
        assert self.data is not None, "Data not loaded. Please load the data first."

        self.data = self.data.fillna(
            self.data.mean()
            if method == "mean"
            else self.data.median() if method == "median" else self.data
        )

    def drop_duplicates(self) -> None:
        """
        Drop duplicate rows from the data.
        """
        assert self.data is not None, "Data not loaded. Please load the data first."

        self.data = self.data.drop_duplicates()
