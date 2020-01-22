# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.schemas.Schema import Schema
from JobBrowserBFF.Validation import Validation
import unittest

UPSTREAM_SERVICE = 'mock'
ENV='mock'
USER_CLASS='user'
TIMEOUT = 10000
# 10/1/19
TIMESTAMP_FROM = 0
# 11/1/19
TIMESTAMP_TO = 1575158400000

class JobBrowserBFFTest(TestBase):

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_validation")
    def test_query_jobs_validation(self):
        try:
            validation = Validation(load_schemas=True)
            param = {
                'limit': 1,
            }
            param2 ={
                'sort': [
                    {
                        'key': 'narrative',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': 0, 
                    'to': 1567371030000 # 9/1/19
                },
                'client_groups': ['njs'],
                'offset': 0,
                'limit': 10
            }
            param3 =  {
                'sort': [
                    {
                        'key': 'narrative',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': 0,
                    'to': 1567371030000 # 9/1/19
                },
                'offset': 0,
                # ok
                'limit': 10
            }
            result = validation.validate_params('query_jobs', param3)
            self.assertTrue(True)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_validate_result")
    def test_query_jobs_validate_result(self):
        try:
            validation = Validation(load_schemas=True)
            result1 = {
                'jobs': [
                    {
                        'job_id': '5dadda14e4b01826d75e2fb7',
                        'state': {
                            'status': 'create',
                            'create_at': 1571674644232,
                        },
                        'owner': {
                            'username': 'kimbrel1',
                            'realname': 'Jeff Kimbrel'
                        },
                        'app': {
                            'id': 'kb_uploadmethods/import_genbank_as_genome_from_staging',
                            'module_name': 'kb_uploadmethods',
                            'function_name': 'import_genbank_as_genome_from_staging',
                            'title': 'Import GenBank File as Genome from Staging Area',
                            'client_groups': ['njs']
                        },
                        'context': {
                            'type': 'workspace',
                            'workspace': {
                                'id': 32798,
                                'is_accessible': True,
                                'name': 'wsname',
                                'is_deleted': False
                            }
                        }
                    }
                ],
                'total_count': 1
            }
            # , 
            result = validation.validate_result('query_jobs', result1)
            self.assertTrue(True)
        except Exception as ex:
            self.assert_no_exception(ex)
