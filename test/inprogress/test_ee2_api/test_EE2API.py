# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.model.EE2Api import EE2Api
from JobBrowserBFF.schemas.Schema import Schema

ENV = 'ci'
USER_CLASS = 'user'
UPSTREAM_SERVICE = 'ee2'
JOB_ID_HAPPY = '5e8285adefac56a4b4bc2b14'
JOB_ID_LOG_HAPPY = '5e8647c576f5df12d4fa6953'
JOB_ID_NOT_FOUND = '5dcb4324fdf6d14ac59ea916'
WORKSPACE_ID_HAPPY = 47458
# Note timeout in seconds since we are dealing directly with the ee2 api
TIMEOUT = 60

START_TIME_1 = 0
END_TIME_1 = 1609459200000
USER = 'kbaseuitest'


class EE2APITest(TestBase):
    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_jobs_happy")
    def test_ver(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        # impl, context = self.impl_for(ENV, USER_CLASS)
        # params = {
        #     'job_ids': [JOB_ID_HAPPY],
        #     'timeout': TIMEOUT
        # }
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            version = api.ver()
            self.assertEqual(version, '0.0.1')
        except Exception as ex:
            self.assert_no_exception(ex)

    def test_status(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            status = api.status()
            self.assertEqual(status['version'], '0.0.1')
            self.assertEqual(status['service'], 'KBase Execution Engine')
            self.assertIsInstance(status['server_time'], float)
            self.assertIsInstance(status['git_commit'], str)
        except Exception as ex:
            self.assert_no_exception(ex)

    def test_list_config(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            expected = {
                "external-url": "https://ci.kbase.us/services/ee2",
                "kbase-endpoint": "https://ci.kbase.us/services",
                "workspace-url": "https://ci.kbase.us/services/ws",
                "catalog-url": "https://ci.kbase.us/services/catalog",
                "shock-url": "https://ci.kbase.us/services/shock-api",
                "handle-url": "https://ci.kbase.us/services/handle_service",
                "srv-wiz-url": "https://ci.kbase.us/services/service_wizard",
                "auth-service-url":
                    "https://ci.kbase.us/services/auth/api/legacy/KBase/Sessions/Login",
                "auth-service-url-v2": "https://ci.kbase.us/services/auth/api/V2/token",
                "auth-service-url-allow-insecure": "false",
                "scratch": "/kb/module/work/tmp",
                "executable": "execute_runner.sh",
                "docker_timeout": "604805",
                "initialdir": "/condor_shared",
                "transfer_input_files": "/condor_shared/JobRunner.tgz"
            }
            config = api.list_config()
            self.assertEqual(config, expected)
        except Exception as ex:
            self.assert_no_exception(ex)

    def test_check_job(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'job_id': JOB_ID_HAPPY
            }
            job = api.check_job(params)
            schema.validate('check_job', job)
            self.assertEqual(job['user'], 'kbaseuitest')

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_check_jobs(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'job_ids': [JOB_ID_HAPPY]
            }
            jobs = api.check_jobs(params)
            schema.validate('check_jobs', jobs)
            self.assertEqual(jobs['job_states'][0]['user'], 'kbaseuitest')

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_check_workspace_jobs(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'workspace_id': WORKSPACE_ID_HAPPY
            }
            jobs = api.check_workspace_jobs(params)
            schema.validate('check_workspace_jobs', jobs)
            self.assertEqual(jobs['job_states'][0]['user'], 'kbaseuitest')

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_cancel_job(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'job_id': JOB_ID_HAPPY
            }
            result = api.cancel_job(params)
            schema.validate('cancel_job', result)
            self.assertIsNone(result)

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_check_job_canceled(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'job_id': JOB_ID_HAPPY
            }
            result = api.check_job_canceled(params)
            schema.validate('check_job_canceled', result)
            self.assertEqual(result['canceled'], False)

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_check_job_status(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'job_id': JOB_ID_HAPPY
            }
            result = api.get_job_status(params)
            schema.validate('get_job_status', result)
            self.assertEqual(result['status'], 'completed')

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_get_job_logs(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'job_id': JOB_ID_LOG_HAPPY
            }
            result = api.get_job_logs(params)
            schema.validate('get_job_logs', result)
            self.assertEqual(result['lines'][0]['ts'], 1585858534288)

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_check_jobs_date_range_for_user(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'start_time': START_TIME_1,
                'end_time': END_TIME_1,
                'user': USER,
                'offset': 0,
                'limit': 10
            }
            result = api.check_jobs_date_range_for_user(params)
            schema.validate('check_jobs_date_range_for_user', result)
            self.assertEqual(result['jobs'][0]['job_id'], '5e8285adefac56a4b4bc2b14')

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_check_jobs_date_range_for_all(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, 'admin')
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            params = {
                'start_time': START_TIME_1,
                'end_time': END_TIME_1,
                'user': USER,
                'offset': 0,
                'limit': 10
            }
            result = api.check_jobs_date_range_for_all(params)
            schema.validate('check_jobs_date_range_for_all', result)
            self.assertEqual(result['jobs'][0]['job_id'], '54b02da8e4b06e6b5555476d')

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_is_admin_is_not(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            result = api.is_admin()
            schema.validate('is_admin', result)
            self.assertEqual(result, False)

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_is_admin_is(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, 'admin')
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            result = api.is_admin()
            schema.validate('is_admin', result)
            self.assertEqual(result, True)

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_get_admin_permission_not_admin(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, USER_CLASS)
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            result = api.get_admin_permission()
            schema.validate('get_admin_permission', result)
            self.assertEqual(result['permission'], 'n')

        except Exception as ex:
            self.assert_no_exception(ex)

    def test_get_admin_permission_admin(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        token = self.token_for(ENV, 'admin')
        schema = Schema(schema_dir="ee2_api", load_schemas=True)
        try:
            api = EE2Api(self.get_config('ee2-url'), token, TIMEOUT)
            result = api.get_admin_permission()
            schema.validate('get_admin_permission', result)
            self.assertEqual(result['permission'], 'w')

        except Exception as ex:
            self.assert_no_exception(ex)
