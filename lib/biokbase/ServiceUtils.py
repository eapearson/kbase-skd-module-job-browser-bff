import dateutil.parser
import datetime
import re

class ServiceUtils:

    @staticmethod
    def ws_info_to_object(ws_info):
        is_narratorial = True if ws_info[8].get('narratorial') == '1' else False
        is_public = True if ws_info[6] == 'r' else False
        mod_date_ms = ServiceUtils.iso8601ToMillisSinceEpoch(ws_info[3])

        return {'id': ws_info[0],
                'name': ws_info[1],
                'owner': ws_info[2],
                'moddate': ws_info[3],
                'object_count': ws_info[4],
                'user_permission': ws_info[5],
                'globalread': ws_info[6],
                'lockstat': ws_info[7],
                'metadata': ws_info[8],
                'modDateMs': mod_date_ms,
                'isPublic': is_public,
                'isNarratorial': is_narratorial}

    @staticmethod
    def obj_info_to_object(data):
        dtype = re.split(r"-|\.", data[2])
        return {'id': data[0],
                'name': data[1],
                'type': data[2],
                'save_date': data[3],
                'version': data[4],
                'saved_by': data[5],
                'wsid': data[6],
                'ws': data[7],
                'checksum': data[8],
                'size': data[9],
                'metadata': data[10],
                'ref': str(data[6]) + '/' + str(data[0]) + '/' + str(data[4]),
                'obj_id': 'ws.' + str(data[6]) + '.obj.' + str(data[0]),
                'typeModule': dtype[0],
                'typeName': dtype[1],
                'typeMajorVersion': dtype[2],
                'typeMinorVersion': dtype[3],
                'saveDateMs': ServiceUtils.iso8601ToMillisSinceEpoch(data[3])}

    @staticmethod
    def iso8601ToMillisSinceEpoch(date):
        epoch = datetime.datetime.utcfromtimestamp(0)
        dt = dateutil.parser.parse(date)
        utc_naive = dt.replace(tzinfo=None) - dt.utcoffset()
        return int((utc_naive - epoch).total_seconds() * 1000.0)

    @staticmethod
    def parse_app_key(key):
        parts = (list(filter(
                    lambda part: len(part) > 0,
                    key.split('/'))))
        if len(parts) == 1:
            return {
                'name': parts[0],
                'shortRef': parts[0],
                'ref': parts[0]
            }
        elif len(parts) == 3:
            return {
                'module': parts[0],
                'name': parts[1],
                'gitCommitHash': parts[2],
                'shortRef': parts[0] + '/' + parts[1],
                'ref': parts[0] + '/' + parts[1] + '/' + parts[2]
            }
        elif len(parts) == 2:
            return {
                'module': parts[0],
                'name': parts[1],
                'shortRef': parts[0] + '/' + parts[1],
                'ret': parts[0] + '/' + parts[1]
            }
        else:
            return None