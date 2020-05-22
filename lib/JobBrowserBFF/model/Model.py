from JobBrowserBFF.model.EE2Model import EE2Model
from JobBrowserBFF.model.MockModel import MockModel


class Model(object):
    def __init__(self, config, context, timeout=None):
        self.config = config
        self.context = context
        self.timeout = timeout or config['default-timeout']

    def get_model(self, context):
        if self.config.get('upstream-service', None) == 'ee2':
            return EE2Model(
                config=self.config,
                token=self.context['token'],
                timeout=self.timeout,
                username=self.context['user_id'])
        elif self.config.get('upstream-service', None) == 'mock':
            return MockModel(
                config=self.config,
                token=self.context['token'],
                timeout=self.timeout,
                username=self.context['user_id'])
        else:
            # TODO: should never occur
            raise ValueError('No upstream service defined (should never occur)')
