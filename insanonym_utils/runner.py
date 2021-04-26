from os import path
from pandas import read_json, read_csv
from .models import FileConfigModel, FileModel, CustomAlgorithm
from .algorithms import *
import importlib

class Runner:
    """
    Class used to create dataframe and execute algorithms
    """
    def __init__(self, model: FileConfigModel):
        _file = FileModel(name=model.name, path=path.join(model.path, model.name))
        self.model = model
        """`FileConfigModel` to use in the runner"""
        self.dataframe = None
        """The resulting `DataFrame`"""
        self._verifyRows(_file.path)
        if model.file_type == 'json':
            self.dataframe = read_json(path_or_buf=_file.path, orient='index')
        elif model.file_type == 'csv':
            self.dataframe = read_csv(filepath_or_buffer=_file.path, sep=model.columns_delimiter)
        column_names = list(map(lambda x: x.name, model.columns))
        self.dataframe.columns = column_names

    def _verifyRows(self, file):
        with open(file, 'r') as csv:
            first_line = csv.readline()
        if first_line.count(self.model.columns_delimiter) + 1 != len(self.model.columns):
            raise Exception('Number of columns differ')


    def execute(self):
        """
        Execute algorithms specified in model on dataframe
        """
        for algo in self.model.algorithms:
            if not isinstance(algo, CustomAlgorithm):
                globals()[algo.name](self.dataframe, algo.options)
            else: 
                mod = importlib.import_module(algo.name)
                mod.main(self.dataframe, algo.options)
        if self.model.export: self.save()

    def save(self):
        """
        Save the resulting dataframe to the specified location in model
        """
        exporter = self.model.export_rules
        if exporter.output_format == 'csv':
            self.dataframe.to_csv(path_or_buf=exporter.output_name, sep=self.model.columns_delimiter, index=False)
        elif exporter.output_format == 'json':
            self.dataframe.to_json(exporter.output_name, index=False)
        else: raise NotImplementedError

