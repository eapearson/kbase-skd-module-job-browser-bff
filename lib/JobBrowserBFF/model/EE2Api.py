from biokbase.GenericClient import GenericClient
from biokbase.Errors import ServiceError


class EE2Api(object):
    def __init__(self, url, token, timeout):
        self.url = url
        self.token = token
        self.timeout = timeout
        self.module = 'execution_engine2'
        self.rpc = GenericClient(url=self.url,
                                 module=self.module,
                                 timeout=self.timeout,
                                 token=self.token)

    def list_config(self):
        try:
            return self.rpc.call_func('list_config')
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(err)
            })

    def ver(self):
        try:
            return self.rpc.call_func('ver')
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(err)
            })

    def get_job_params(self, params):
        try:
            return self.rpc.call_func('get_job_params', params)
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(err)
            })

    def status(self):
        try:
            return self.rpc.call_func('status')
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(err)
            })

    def check_job(self, params):
        try:
            return self.rpc.call_func('check_job', params)
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(err)
            })

    def check_jobs(self, params):
        try:
            return self.rpc.call_func('check_jobs', params)
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(
                code=1,
                message='Unknown error',
                data={
                    'original_message': str(err)
                })

    def check_workspace_jobs(self, params):
        try:
            return self.rpc.call_func('check_workspace_jobs', params)
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(
                code=1,
                message='Unknown error',
                data={
                    'original_message': str(err)
                })

    def check_job_canceled(self, params):
        try:
            return self.rpc.call_func('check_job_canceled', params)
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(
                code=1,
                message='Unknown error',
                data={
                    'original_message': str(err)
                })

    def get_job_status(self, params):
        try:
            return self.rpc.call_func('get_job_status', params)
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(
                code=1,
                message='Unknown error',
                data={
                    'original_message': str(err)
                })

    def get_job_logs(self, params):
        try:
            return self.rpc.call_func('get_job_logs', params)
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(
                code=1,
                message='Unknown error',
                data={
                    'original_message': str(err)
                })

    def get_admin_permission(self):
        try:
            result = self.rpc.call_func('get_admin_permission')
            return result
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(ex)
            })

    def is_admin(self):
        try:
            result = self.rpc.call_func('is_admin')
            return result
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(ex)
            })

    def check_jobs_date_range_for_user(self, params):
        try:
            return self.rpc.call_func('check_jobs_date_range_for_user', params)
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(ex)
            })

    def check_jobs_date_range_for_all(self, params):
        try:
            return self.rpc.call_func('check_jobs_date_range_for_all', params)
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(ex)
            })

    def cancel_job(self, params):
        try:
            return self.rpc.call_func('cancel_job', params)
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(ex)
            })
