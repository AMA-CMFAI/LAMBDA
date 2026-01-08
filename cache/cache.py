import pandas as pd
import os
import shutil


class data_cache:

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.data_cache_path = os.path.dirname(file_path)
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.csv':
            self.data = pd.read_csv(self.file_path, encoding='utf-8')
        elif file_extension in ['.xlsx', '.xls']:
            self.data = pd.read_excel(self.file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        self.general_info = {}

    def get_description(self) -> dict:
        # self.general_info["info"] = get_info(self.data)
        general_info = get_general_info(self.data)
        self.general_info["num_rows"], self.general_info["num_features"], self.general_info["features"], \
            self.general_info["col_type"], self.general_info["missing_val"] = general_info["num_rows"], \
            general_info["num_features"], general_info["features"], general_info["col_type"], general_info[
            "missing_val"]

        self.general_info["describe"] = self.data.describe()
        # self.general_info["label_counts"] = self.data["label"].value_counts()
        return self.general_info


def get_general_info(data: pd.DataFrame):
    return {"num_rows": data.shape[0], "num_features": data.shape[1], "features": data.columns,
            "col_type": data.dtypes, "missing_val": data.isnull().sum()}

