# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.schemas.Schema import Schema
from JobBrowserBFF.Validation import Validation
import unittest
import json

ENV = 'ci'
UPSTREAM_SERVICE = 'metrics'
USER_CLASS = 'user'
TIMEOUT_MS = 10000
TIMESTAMP_FROM = 0
# 11/1/19
TIMESTAMP_TO = 1575158400000
TOTAL_COUNT = 19


class JobBrowserBFFTest(TestBase):
    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_happy")
    def test_query_jobs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.query_jobs(context, {
                'time_span': {
                    'from': 1496275200000,  # 6/1/17
                    'to': 1527811200000  # 6/1/18
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, 8)
            self.assertEqual(total_count, TOTAL_COUNT)
            self.assertEqual(len(jobs), 8)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_with_time_span_happy")
    def test_query_jobs_with_sort_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.query_jobs(context, {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': 1496275200000,  # 6/1/17
                    'to': 1527811200000  # 6/1/18
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(total_count, TOTAL_COUNT)
            self.assertEqual(found_count, 8)
            self.is_in_ascending_order(jobs, ['state', 'create_at'])
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_with_sort_descending_happy")
    def test_query_jobs_with_sort_descending_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.query_jobs(context, {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'descending'
                    }
                ],
                'time_span': {
                    'from': 1496275200000,  # 6/1/17
                    'to': 1527811200000  # 6/1/18
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(total_count, TOTAL_COUNT)
            self.assertEqual(found_count, 8)
            self.is_in_descending_order(jobs, ['state', 'create_at'])
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_validation")
    def test_query_jobs_validation(self):
        try:
            validation = Validation(load_schemas=True)
            param = {
                'limit': 1,
            }
            param2 = {
                'sort': [
                    {
                        'key': 'narrative',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': 0,
                    'to': 1567371030000  # 9/1/19
                },
                'client_groups': ['njs'],
                'offset': 0,
                'limit': 10
            }
            param3 = {
                'sort': [
                    {
                        'key': 'narrative',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': 0,
                    'to': 1567371030000  # 9/1/19
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

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_happy")
    def test_query_jobs_context_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.query_jobs(context, {
                'time_span': {
                    'from': TIMESTAMP_FROM,
                    'to': TIMESTAMP_TO
                },
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'descending'
                    }
                ],
                'offset': 0,
                'limit': 20,
                'admin': 0
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, 19)
            self.assertEqual(total_count, 19)
            self.assertEqual(len(jobs), 19)

            job1 = jobs[0]
            self.assertEqual(job1['job_id'], '5cf1522aaa5a4d298c5dc2ff')
            self.assertEqual(job1['context']['type'], 'narrative')
            self.assertEqual(job1['context']['narrative']['title'], 'Job Browser Testing')

            job2 = jobs[3]
            self.assertEqual(job2['job_id'], '5981eee1e4b06f68bf751ee6')
            self.assertEqual(job2['context']['type'], 'narrative')
            self.assertEqual(job2['context']['narrative']['title'],
                             'Read-Only Parameters Test [TASK-938]')

            job3 = jobs[15]
            self.assertEqual(job3['job_id'], '57eeefefe4b0b05cf8996c05')
            self.assertEqual(job3['context']['type'], 'unknown')

            job4 = jobs[16]
            self.assertEqual(job4['job_id'], '57eeefb5e4b0b05cf8996c04')
            self.assertEqual(job4['context']['type'], 'export')

        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_happy")
    def test_query_jobs_filter_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)

            base_params = {
                'time_span': {
                    'from': 1496275200000,  # 6/1/17
                    'to': 1527811200000  # 6/1/18
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS,
            }

            cases = [
                {
                    'param': {
                        'filter': {
                            'status': ['queue', 'run', 'complete', 'error', 'terminate']
                        }
                    },
                    'expected': {
                        'found_count': 8,
                        'job_count': 8
                    }
                },
                {
                    'param': {
                        'filter': {
                            'status': ['queue']
                        }
                    },
                    'expected': {
                        'found_count': 0,
                        'job_count': 0
                    }
                },
                {
                    'param': {
                        'filter': {
                            'status': ['error']
                        }
                    },
                    'expected': {
                        'found_count': 2,
                        'job_count': 2
                    }
                },
                {
                    'param': {
                        'filter': {
                            'status': ['complete']
                        }
                    },
                    'expected': {
                        'found_count': 6,
                        'job_count': 6
                    }
                }
            ]

            for case in cases:
                params = base_params.copy()
                params.update(case['param'])
                ret = impl.query_jobs(context, params)
                jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
                # print('JOBS', jobs)
                self.assertEqual(found_count, case['expected']['found_count'])
                self.assertEqual(total_count, TOTAL_COUNT)
                self.assertEqual(len(jobs), case['expected']['job_count'])

        except Exception as ex:
            self.assert_no_exception(ex)
