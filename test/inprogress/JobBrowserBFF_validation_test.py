# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.Validation import Validation
import os
import json
import unittest
from jsonschema import validate
from jsonrpcbase import InvalidParamsError
from jsonschema.exceptions import ValidationError

class JobBrowserBFFTest(TestBase):

    # Uncomment to skip this test
    # @unittest.skip("skipped test_load_schemas_happy")
    # def test_load_schemas_happy(self):
    #     try:
    #         validation = Validation(load_schemas=True)
    #         # schema_dir = os.path.dirname(__file__) + '/../data/schemas'
    #         # schemas = validation.load_schemas(schema_dir)
    #         self.assertIsInstance(schemas, dict)
    #         self.assertEqual(len(schemas), 1)
    #         schema1 = schemas['schema1']
    #         self.assertIsInstance(schema1, dict)

    #     except Exception as ex:
    #         #    traceback.print_tb(ex)
    #        self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
    #        return

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_jobs_params_happy")
    def test_get_jobs_params_happy(self):
        try:
            validation = Validation(load_schemas=True)
            # schema_path = os.path.dirname(__file__) + '/../../lib/JobBrowserBFF/schemas/'
            # schema_file_name = 'get_jobs_params.json'
            # schema = validation.load_schema(schema_file_name, path=schema_path)
            # self.assertIsInstance(schema, dict)

            sample_params = [
                {
                    'job_ids': []
                },
                {
                    'job_ids': ['hi']
                },
                {
                    'job_ids': ['a', 'b', 'c']
                }
            ]
            for sample_param in sample_params:
                try:
                    validation.validate_params('get_jobs', sample_param)
                except InvalidParamsError as ve:
                    self.assertTrue(False, 'Unexpected validation failure: ' + ve.message)
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_jobs_params_sad")
    def test_get_jobs_params_sad(self):
        try:
            validation = Validation(load_schemas=True)

            sample_params = [
                {},
                {
                    'job_ids': None
                },
                {
                    'job_ids': 1
                },
                {
                    'job_ids': 'hello'
                },
                {
                    'job_ids': [None]
                },
                {
                    'job_ids': [1]
                },
                {
                    'job_ids': [['a']]
                },
                {
                    'job_ids': [{'a': 'b'}]
                }
            ]
            for sample_param in sample_params:
                with self.assertRaises(InvalidParamsError):
                    validation.validate_params('get_jobs', sample_param)
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_jobs_result_happy")
    def test_get_jobs_result_happy(self):
        try:
            validation = Validation(load_schemas=True)
            # validation = Validation()
            # schema_path = os.path.dirname(__file__) + '/../../lib/JobBrowserBFF/schemas/'
            # schema_file_name = 'get_jobs_result.json'
            # schema = validation.load_schema(schema_file_name, path=schema_path)
            data_path = os.path.dirname(__file__) + '/../data/methods/get_jobs/happy/result'
            data_file_name = 'sample1.json'
            with open(os.path.join(data_path, data_file_name)) as fin:
                sample_result = json.load(fin)
            # self.assertIsInstance(schema, dict)

            try:
                validation.validate_result('get_jobs', sample_result)
            except ValidationError as ve:
                self.assertTrue(False, 'Unexpected validation failure: ' + ve.message)
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return
