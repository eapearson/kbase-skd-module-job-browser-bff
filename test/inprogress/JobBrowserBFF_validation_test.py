# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.Validation import Validation
import os
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

class JobBrowserBFFTest(TestBase):
    def test_load_schemas_happy(self):
        try:
            validation = Validation()
            schema_dir = os.path.dirname(__file__) + '/../data/schemas'
            schemas = validation.load_schemas(schema_dir)
            self.assertIsInstance(schemas, dict)
            self.assertEqual(len(schemas), 1)
            schema1 = schemas['schema1']
            self.assertIsInstance(schema1, dict)

        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return

    def test_get_jobs_params_happy(self):
        try:
            validation = Validation()
            schema_path = os.path.dirname(__file__) + '/../../lib/JobBrowserBFF/schemas/'
            schema_file_name = 'get_jobs_params.json'
            schema = validation.load_schema(schema_file_name, path=schema_path)
            self.assertIsInstance(schema, dict)

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
                    validate(instance=sample_param, schema=schema)
                except ValidationError as ve:
                    self.assertTrue(False, 'Unexpected validation failure: ' + ve.message)
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return


    def test_get_jobs_params_sad(self):
        try:
            validation = Validation()
            schema_path = os.path.dirname(__file__) + '/../../lib/JobBrowserBFF/schemas/'
            schema_file_name = 'get_jobs_params.json'
            schema = validation.load_schema(schema_file_name, path=schema_path)
            self.assertIsInstance(schema, dict)

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
                with self.assertRaises(ValidationError):
                    validate(instance=sample_param, schema=schema)
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return

    def test_get_jobs_result_happy(self):
        try:
            validation = Validation()
            schema_path = os.path.dirname(__file__) + '/../../lib/JobBrowserBFF/schemas/'
            schema_file_name = 'get_jobs_result.json'
            schema = validation.load_schema(schema_file_name, path=schema_path)
            data_path = os.path.dirname(__file__) + '/../data/methods/get_jobs/'
            data_file_name = 'sample1.json'
            with open(os.path.join(data_path, data_file_name)) as fin:
                sample_result = json.load(fin)
            self.assertIsInstance(schema, dict)

            try:
                validate(instance=sample_result, schema=schema)
            except ValidationError as ve:
                self.assertTrue(False, 'Unexpected validation failure: ' + ve.message)
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return
