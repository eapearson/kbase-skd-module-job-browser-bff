# -*- coding: utf-8 -*-
from JobBrowserBFF.Validation import Validation
from JobBrowserBFF.TestBase import TestBase
import unittest
import os
import json


class ValidationTests(TestBase):
    def load_data_file(self, method_name, outcome_type, data_type, file_name):
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data',
                                 'methods', method_name, outcome_type, data_type, file_name)
        with open(data_path) as fin:
            return json.load(fin)

    def get_data_files(self, method_name, outcome_type, data_type):
        dir_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data',
                                'methods', method_name, outcome_type, data_type)
        dirs = []
        for file_name in os.listdir(dir_path):
            dirs.append(file_name)
        return dirs

    # Uncomment to skip this test
    @unittest.skip("skipped test_query_jobs_validate_params_happy")
    def test_query_jobs_validate_params_happy(self):
        try:
            validation = Validation(load_schemas=True)
            method_names = [
                'query_jobs', 'get_jobs', 'get_job_log',
                'cancel_job'
            ]
            for method_name in method_names:
                sample_files = self.get_data_files(method_name, 'happy', 'params')
                for sample_file in sample_files:
                    data = self.load_data_file(method_name, 'happy', 'params', sample_file)
                    validation.validate_params(method_name, data)

        except Exception as ex:
            self.assert_no_exception(ex)
            return

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_jobs_validate_result_happy")
    def test_get_jobs_validate_result_happy(self):
        try:
            validation = Validation(load_schemas=True)
            method_names = [
                'get_jobs', 'query_jobs', 'get_job_log',
                'cancel_job', 'get_client_groups',
                'get_job_states', 'get_job_types', 'get_log_levels',
                'get_searchable_job_fields'
            ]
            for method_name in method_names:
                sample_files = self.get_data_files(method_name, 'happy', 'result')
                for sample_file in sample_files:
                    data = self.load_data_file(method_name, 'happy', 'result', sample_file)
                    validation.validate_result(method_name, data)
        except Exception as ex:
            self.assert_no_exception(ex)
            return
