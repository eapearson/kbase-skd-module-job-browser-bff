import json
import apsw
# import time
import hashlib
import math

from biokbase.GenericClient import GenericClient
# from DashboardService.Errors import ServiceError

MAX_SQL_VARIABLES = 500


def get_path(from_dict, path):
    current_dict = from_dict
    for el in path:
        if not isinstance(current_dict, dict):
            return None
        if el not in current_dict:
            return None
        current_dict = current_dict[el]
    return current_dict


class UserProfileCache:
    def __init__(self, path=None, user_profile_url=None, upstream_timeout=None):
        if path is None:
            raise ValueError('The "path" argument is required')

        if not isinstance(path, str):
            raise ValueError('The "path" argument must be a string')
        self.path = path

        if user_profile_url is None:
            raise ValueError('The "user_profile_url" argument is required')
        if not isinstance(user_profile_url, str):
            raise ValueError('The "user_profile_url" argument must be a string')
        self.user_profile_url = user_profile_url

        if upstream_timeout is None:
            raise ValueError('The "upstream_timeout" argument is required')
        if not isinstance(upstream_timeout, int):
            raise ValueError('The "upstream_timeout" argument must be an int')
        self.upstream_timeout = upstream_timeout

        self.conn = apsw.Connection(self.path)

    def initialize(self):
        self.create_schema()
        self.sync()

    def create_schema(self):
        alerts_schema = '''
        drop table if exists cache;
        create table cache (
            key text not null primary key,
            value text,
            size int not null,
            md5 blob not null
        );
        '''
        with self.conn:
            self.conn.cursor().execute(alerts_schema)

    def sync(self):
        temp_sql = '''
        create temporary table updater (
        key text not null primary key,
        value text not null,
        size int not null,
        md5 blob not null    
        )
        '''
        update_temp_sql = '''
        insert into updater
        (key, value, size, md5)
        values
        (?, ?, ?, ?)
        '''

        insert_sql = '''
        insert into cache
        (key, value, size, md5)
        select key, value, size, md5
        from updater where 
          not exists (select updater.key from cache where cache.key = updater.key)
        '''

        update_sql = '''
        with updates as (select * 
                            from updater a
                            join cache b
                                on a.key = b.key and
                                a.md5 != b.md5)
        update cache
        set (value, size, md5) = 
            (select value, size, md5 from updates where updates.key = cache.key)
        where cache.key in (select key from updates)
        '''

        profiles = self.fetch_profiles()
        # fetched_at = time.time()

        with self.conn:
            self.conn.cursor().execute(temp_sql)

            for profile in profiles:
                key = get_path(profile, ['user', 'username'])
                value = json.dumps(profile)
                hasher = hashlib.md5()
                hasher.update(value.encode('utf-8'))
                hash = hasher.digest()
                params = (key, value, len(value), memoryview(hash))
                self.conn.cursor().execute(update_temp_sql, params)

            self.conn.cursor().execute(insert_sql)
            self.conn.cursor().execute(update_sql)

    def clear_all(self):
        schema = '''
        delete * from cache;
        '''
        with self.conn:
            self.conn.cursor().execute(schema)

    def fetch_profiles(self):
        rpc = GenericClient(
            module='UserProfile',
            url=self.user_profile_url,
            timeout=self.upstream_timeout,
            token=None
        )
        users = rpc.call_func('filter_users', {
            'filter': ''
        })

        usernames = [user['username'] for user in users]

        profiles = []

        batches, rem = divmod(len(usernames), 1000)

        for batch_number in range(0, batches + 1):
            if batch_number == batches:
                start = batch_number * 1000
                stop = start + rem
            else:
                start = batch_number*1000
                stop = (batch_number+1)*1000

            username_group = usernames[start:stop]
            result = rpc.call_func('get_user_profile',
                                   username_group
                                   )

            profiles.extend(result)

        return profiles

    # public interface

    def reload(self):
        self.conn.cursor().execute('BEGIN TRANSACTION;')
        try:
            self.clear_all()
            self.sync()
            self.conn.cursor().execute('COMMIT;')
        except Exception:
            self.conn.cursor().execute('ROLLBACK;')

    def get(self, usernames):
        # TODO: handle usernames > 1000
        num_users = len(usernames)
        batches = math.ceil(num_users / MAX_SQL_VARIABLES)

        profiles = []
        for batch in range(0, batches):
            batch_from = batch * MAX_SQL_VARIABLES
            batch_to = batch_from + min(MAX_SQL_VARIABLES, num_users - batch_from)
            usernames_to_get = usernames[batch_from: batch_to]

            placeholders = ','.join(list('?' for _ in usernames_to_get))
            sql = '''
            select key, value
            from cache
            where key in (%s)
            ''' % (placeholders)

            with self.conn:
                for key, value in self.conn.cursor().execute(sql, usernames_to_get).fetchall():
                    profiles.append([key, json.loads(value)])

        return profiles
