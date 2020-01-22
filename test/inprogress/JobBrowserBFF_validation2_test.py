# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.schemas.Schema import Schema
from JobBrowserBFF.Validation import Validation
from jsonschema import validate, RefResolver
from jsonschema.exceptions import ValidationError

import unittest


class JobBrowserBFFTest(TestBase):
    # @unittest.skip("skipped test_query_jobs_validation")
    def test_query_jobs_validation(self):
        try:
            # schemas = Schema(load_schemas=True)
            # schema = schemas.get('query_jobs')
            validation = Validation(load_schemas=True)
            param = {
                'limit': 1,
            }
            param2 = {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'ascending'
                    }
                ],
                'client_groups': ['njs'],
                'offset': 0,
                'limit': 10
            }
            param3 = {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': 1546375830000,  # 1/1/19
                    'to': 1567371030000  # 9/1/19
                },
                'offset': 0,
                # ok
                'limit': 10
            }
            result = validation.validate_params('query_jobs', param3)
            self.assertTrue(True)
        except Exception as ex:
            self.assertTrue(False, "Unexpected exception: {0}".format(str(ex)))

    # @unittest.skip("skipped test_query_jobs_validate_result")
    def test_query_jobs_validate_result(self):
        try:
            # schemas = Schema(load_schemas=True)
            # schema = schemas.get('query_jobs')
            validation = Validation(load_schemas=True)
            result1 = {
                'jobs': [
                    {
                        'job_id': '5dadda14e4b01826d75e2fb7',
                        'state': {
                            'type': 'create',
                            'create_at': 1571674644232,
                            # 'queue_at': 1571674644232,
                            # 'run_at': 1571674654295
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
                            'client_groups': ['njs'],
                        },
                        # 'client_group': None,
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
            self.assertTrue(False, "Unexpected exception: {0}".format(str(ex)))

    # @unittest.skip("skipped test_query_jobs_validate_result")
    def test_schema1(self):
        schema = {
            'type': 'object',
            'properties': {
                'prop1': {
                    'type': 'string'
                },
                'prop2': {
                    'type': 'integer'
                }
            }
        }
        instance = {
            'prop1': 'hi',
            'prop2': 42
        }
        try:
            validate(instance=instance, schema=schema)
            self.assertTrue(True)
        except Exception as ex:
            self.assertTrue(False, "EXCEPTION {0}".format(str(ex)))

    # @unittest.skip("skipped test_query_jobs_validate_result")
    def test_schema2(self):
        schema = {
            'type': 'object',
            'properties': {
                'prop1': {
                    'oneOf': [
                        {
                            'type': 'string'
                        },
                        {
                            'type': 'integer'
                        }
                    ]
                }
            }
        }
        instances = [{
            'prop1': 'hi'
        }, {
            'prop1': 123
        }]

        # happy
        try:
            for instance in instances:
                validate(instance=instance, schema=schema)
            self.assertTrue(True)
        except Exception as ex:
            self.assertTrue(False, "EXCEPTION {0}".format(str(ex)))

        # sad
        fails = [{
            'prop1': False
        }]
        for fail in fails:
            try:
                validate(instance=fail, schema=schema)
                self.assertTrue(False, 'Did not expect to succeed')
            except Exception:
                self.assertTrue(True)

    def test_schema3(self):
        schema = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'type': 'object',
            'definitions': {
                'colored': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'kind': {
                            'type': 'string',
                            'const': 'colored'
                        },
                        'color': {
                            'type': 'string'
                        }
                    }
                },
                'sized': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'kind': {
                            'type': 'string',
                            'const': 'sized'
                        },
                        'size': {
                            'type': 'string'
                        }
                    }
                },
                'fooed': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'kind': {
                            'type': 'string',
                            'const': 'fooed'
                        },
                        'size': {
                            'type': 'string'
                        }
                    }
                }
            },
            'properties': {
                'prop1': {
                    'type': 'object',
                    'oneOf': [
                        {
                            '$ref': '#/definitions/colored'
                        },
                        {
                            '$ref': '#/definitions/sized'
                        },
                        {
                            '$ref': '#/definitions/fooed'
                        }
                    ]
                }
            }
        }
        instances = [{
            'prop1': {
                'kind': 'colored',
                'color': 'red'
            }
        }, {
            'prop1': {
                'kind': 'sized',
                'size': 'large'
            }
        }, {
            'prop1': {
                'kind': 'fooed',
                'size': 'large'
            }
        }]

        # happy
        try:
            for instance in instances:
                validate(instance=instance, schema=schema)
            self.assertTrue(True)
        except Exception as ex:
            self.assertTrue(False, "EXCEPTION {0}".format(str(ex)))

        # sad
        fails = [{
            'prop1': {
                'type': 'colored',
                'weight': 'large'
            },
            'prop1': {
                'type': 'textured',
                'weight': 'large'
            }
        }]
        for fail in fails:
            try:
                validate(instance=fail, schema=schema)
                self.assertTrue(False, 'Did not expect to succeed')
            except Exception:
                self.assertTrue(True)

    def test_schema4(self):
        schema = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'type': 'object',
            'definitions': {
                "jsonrpc_error": {
                    "type": "object",
                    "title": "A JSONRPC compatible error",
                    "required": [
                        "code", "message"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "code": {
                            "type": "integer"
                        },
                        "message": {
                            "type": "string"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                            }
                        }
                    }
                },
                "error": {
                    "type": "object",
                    "title": "A job error",
                    "required": [
                        "code", "message"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "code": {
                            "type": "integer",
                            "enum": [0, 1, 2, 3, 4, 5]
                        },
                        "message": {
                            "type": "string"
                        },
                        "jsonrpc_error": {
                            "type": "object",
                            "$ref": "#/definitions/jsonrpc_error"
                        }
                    }
                },
                "termination_reason": {
                    "type": "object",
                    "title": "A job termination reason",
                    "required": [
                        "code"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "code": {
                            "type": "integer",
                            "enum": [0, 1, 2]
                        },
                        "message": {
                            "type": "string"
                        }
                    }
                },
                "job_state_create": {
                    "type": "object",
                    "title": "Job has been created",
                    "required": [
                        "type",
                        "create_at"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "create"
                        },
                        "create_at": {
                            "type": "integer"
                        }
                    }
                },
                "job_state_queue": {
                    "type": "object",
                    "title": "Job has been queued",
                    "required": [
                        "type",
                        "create_at",
                        "queue_at"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "queue"
                        },
                        "create_at": {
                            "type": "integer"
                        },
                        "queue_at": {
                            "type": "integer"
                        }
                    }
                },
                "job_state_run": {
                    "type": "object",
                    "title": "Job is running",
                    "required": [
                        "type",
                        "create_at",
                        "queue_at",
                        "run_at"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "run"
                        },
                        "create_at": {
                            "type": "integer"
                        },
                        "queue_at": {
                            "type": "integer"
                        },
                        "run_at": {
                            "type": "integer"
                        }
                    }
                },
                "job_state_complete": {
                    "type": "object",
                    "title": "Job is finished successfully",
                    "required": [
                        "type",
                        "create_at",
                        "queue_at",
                        "run_at",
                        "finish_at"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "complete"
                        },
                        "create_at": {
                            "type": "integer"
                        },
                        "queue_at": {
                            "type": "integer"
                        },
                        "run_at": {
                            "type": "integer"
                        },
                        "finish_at": {
                            "type": "integer"
                        }
                    }
                },
                "job_state_error": {
                    "type": "object",
                    "title": "Job is finished with error",
                    "required": [
                        "type",
                        "create_at",
                        "finish_at",
                        "error"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "error"
                        },
                        "create_at": {
                            "type": "integer"
                        },
                        "queue_at": {
                            "type": "integer"
                        },
                        "run_at": {
                            "type": "integer"
                        },
                        "finish_at": {
                            "type": "integer"
                        },
                        "error": {
                            "$ref": "#/definitions/error"
                        }
                    }
                },
                "job_state_terminate": {
                    "type": "object",
                    "title": "Job is finished by termination",
                    "required": [
                        "type",
                        "create_at",
                        "finish_at",
                        "reason"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "terminate"
                        },
                        "create_at": {
                            "type": "integer"
                        },
                        "queue_at": {
                            "type": "integer"
                        },
                        "run_at": {
                            "type": "integer"
                        },
                        "finish_at": {
                            "type": "integer"
                        },
                        "reason": {
                            "$ref": "#/definitions/termination_reason"
                        }
                    }
                },
                "job_state": {
                    "type": "object",
                    "title": "Job State",
                    "oneOf": [
                        {
                            "$ref": "#/definitions/job_state_create"
                        },
                        {
                            "$ref": "#/definitions/job_state_queue"
                        },
                        {
                            "$ref": "#/definitions/job_state_run"
                        },
                        {
                            "$ref": "#/definitions/job_state_complete"
                        },
                        {
                            "$ref": "#/definitions/job_state_error"
                        },
                        {
                            "$ref": "#/definitions/job_state_terminate"
                        }
                    ]
                },
                "job_context_narrative": {
                    "type": "object",
                    "title": "The context",
                    "required": [
                        "type"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "narrative"
                        },
                        "workspace": {
                            "type": "object",
                            "required": [
                                "id",
                                "is_accessible"
                            ],
                            "additionalProperties": False,
                            "properties": {
                                "id": {
                                    "type": "number"
                                },
                                "is_accessible": {
                                    "type": "boolean",
                                    "const": True
                                },
                                "is_deleted": {
                                    "type": "boolean"
                                },
                                "name": {
                                    "type": "string"
                                }
                            }
                        },
                        "narrative": {
                            "type": "object",
                            "required": [
                                "title"
                            ],
                            "additionalProperties": False,
                            "properties": {
                                "title": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                },
                "job_context_workspace": {
                    "type": "object",
                    "title": "The workspace context",
                    "required": [
                        "type",
                        "id",
                        "is_accessible"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "workspace"
                        },
                        "workspace": {
                            "type": "object",
                            "required": [

                            ],
                            "properties": {
                                "id": {
                                    "type": "number"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "is_accessible": {
                                    "type": "boolean"
                                },
                                "is_deleted": {
                                    "type": "boolean"
                                }
                            }
                        }
                    }
                },
                "job_context_export": {
                    "type": "object",
                    "title": "The export context",
                    "required": [
                        "type"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "export"
                        }
                    }
                },
                "job_context_unknown": {
                    "type": "object",
                    "title": "The unknown context",
                    "required": [
                        "type"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "const": "unknown"
                        }
                    }
                },
                "job_info": {
                    "type": "object",
                    "title": "The Items Schema",
                    "required": [
                        "job_id",
                        "owner",
                        "state",
                        "app",
                        "client_groups"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "job_id": {
                            "$id": "#/properties/jobs/items/properties/job_id",
                            "type": "string",
                            "title": "The Job_id Schema",
                            "default": "",
                            "examples": [
                                "abc"
                            ],
                            "pattern": "^(.*)$"
                        },
                        "owner": {
                            "$id": "#/properties/jobs/items/properties/owner",
                            "type": "object",
                            "title": "The Owner Schema",
                            "required": [
                                "username",
                                "realname"
                            ],
                            "properties": {
                                "username": {
                                    "$id": "#/properties/jobs/items/properties/owner/properties/username",
                                    "type": "string",
                                    "default": "",
                                    "examples": [
                                        "mmouse"
                                    ],
                                    "pattern": "^(.*)$"
                                },
                                "realname": {
                                    "$id": "#/properties/jobs/items/properties/owner/properties/realname",
                                    "type": "string",
                                    "default": "",
                                    "examples": [
                                        "Mickey Mouse"
                                    ],
                                    "pattern": "^(.*)$"
                                }
                            }
                        },
                        "state": {
                            "$ref": "#/definitions/job_state"
                        },
                        "app": {
                            "$id": "#/properties/jobs/items/properties/app",
                            "type": ["object", "null"],
                            "title": "The App Schema",
                            "required": [
                                "id",
                                "module_name",
                                "function_name",
                                "title"
                            ],
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "title": "The App ID"
                                },
                                "module_name": {
                                    "$id": "#/properties/jobs/items/properties/app/properties/module_name",
                                    "type": "string",
                                    "title": "The Module_name Schema",
                                    "default": "",
                                    "examples": [
                                        "Module"
                                    ],
                                    "pattern": "^(.*)$"
                                },
                                "function_name": {
                                    "$id": "#/properties/jobs/items/properties/app/properties/function_name",
                                    "type": "string",
                                    "title": "The Function_name Schema",
                                    "default": "",
                                    "examples": [
                                        "func1"
                                    ],
                                    "pattern": "^(.*)$"
                                },
                                "title": {
                                    "$id": "#/properties/jobs/items/properties/app/properties/title",
                                    "type": "string",
                                    "title": "The Title Schema",
                                    "default": "",
                                    "examples": [
                                        "My amazing method"
                                    ],
                                    "pattern": "^(.*)$"
                                }
                            }
                        },
                        "context": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "$ref": "#/definitions/job_context_narrative"
                                },
                                {
                                    "$ref": "#/definitions/job_context_workspace"
                                },
                                {
                                    "$ref": "#/definitions/job_context_unknown"
                                }
                            ]
                        },
                        "client_groups": {
                            "$id": "#/properties/jobs/items/properties/client_groups",
                            "type": "array",
                            "title": "The Client_groups Schema",
                            "items": {
                                "$id": "#/properties/jobs/items/properties/client_groups/items",
                                "type": "string",
                                "title": "The Items Schema",
                                "default": "",
                                "examples": [
                                    "njs"
                                ],
                                "pattern": "^(.*)$"
                            }
                        }
                    }
                }
            },
            'properties': {
                'test1': {
                    '$ref': '#/definitions/job_state'
                }
            }
        }
        instances = [{
            'test1': {
                'type': 'run',
                'create_at': 1,
                'queue_at': 2,
                'run_at': 4
            }
        }, {
            'test1': {
                'type': 'create',
                'create_at': 1
            }
        }, {
            'test1': {
                'type': 'queue',
                'create_at': 1,
                'queue_at': 2
            }
        }]

        # happy
        try:
            for instance in instances:
                validate(instance=instance, schema=schema)
            self.assertTrue(True)
        except Exception as ex:
            self.assertTrue(False, "EXCEPTION {0}".format(str(ex)))
