from nameko.rpc import rpc
import pandas as pd
import numpy as np
import yaml
import pymongo
from bson.objectid import ObjectId


# from Translator_main import test


class Reader():

    def dict_parser(self, dictionary, key, level, pk):
        if isinstance(dictionary, dict):
            for k, v in dictionary.items():
                if isinstance(v, int) or isinstance(v, str):
                    result = [level - 1, str(key), level, str(k), v, pk]
                    yield result

                if isinstance(v, dict):
                    yield [level - 1, str(key), level, str(k), None, None]
                    for res in self.dict_parser(v, k, level + 1, pk):
                        yield res

                elif isinstance(v, list):
                    if (isinstance(v[0], str)):
                        yield [level - 1, str(key), level, str(k), v, pk]
                        for i in v:
                            for res in self.dict_parser(i, k, level + 1, None):
                                yield res

                    else:
                        yield [level - 1, str(key), level, str(k), None, None]
                        for j, i in enumerate(v):
                            for res in self.dict_parser(i, k, level + 1, (10 * (pk) + j + 1)):
                                yield res

        else:
            pass


class write_dict():

    def append_dict(self, parent_key, lvl, dictionary):

        inner_dict = {}
        list_dict = []

        k, v = lvl[0][1].split(' : ')
        inner_dict.update({k: v})

        for i in range(1, len(lvl)):

            if (lvl[i - 1][0] == lvl[i][0]):
                k, v = lvl[i][1].split(' : ')
                inner_dict.update({k: v})

            elif (lvl[i - 1][0] != lvl[i][0]):
                list_dict.append(inner_dict)
                inner_dict = {}
                k, v = lvl[i][1].split(' : ')
                inner_dict.update({k: v})

        list_dict.append(inner_dict)
        dictionary[parent_key] = list_dict

        return dictionary

    def getKey(self, item):
        return item[0]

    def make_json(self, dataset, level):


        parent_level = dataset[(dataset['level'] == level) & (dataset['value'] != 'NULL')][
            'parent_level'].unique()  # getting the parent level from the dataframe
        s = dataset[(dataset['level'] == level) & (dataset['value'] != 'NULL')].groupby(by=['parent_key']).agg(
            {'key': lambda x: x.nunique()})  # getting the unique set of keys whose values are at higher levels
        # along with the number of items
        # (in case the values at the higher levels are repeated in an array)
        s = s.to_dict()  # converting the set of keys

        for parent, ele in s['key'].items():  # iterating over each keys found in previous step
            lvl_dict = {}
            parent_key = []

            lvl = list(
                dataset[(dataset['level'] == level) & (dataset['value'] != 'NULL') & (dataset['parent_key'] == parent)][
                    ['id', 'key', 'value']].apply(lambda x: (x.id, x.key + ' : ' + str(x.value)), axis=1).values)
            # list containing the id ( which is used to maintain an enumeration of arrays ) and a concatenation of key,value

            lvl_dict.update(self.append_dict(parent, sorted(lvl, key=self.getKey),
                                             {}))  # calling append function to tidy up the dictionary

            parent_key.append(np.unique(dataset[(dataset['key'] == parent) & (dataset['level'] == parent_level[0]) & (
                        dataset['value'] == 'NULL')]['parent_key'].values))  # creating a list of parents at this level

            yield parent_key, lvl_dict

    def reverse_loop(self, dictionary, key, value):

        if (isinstance(dictionary, dict)):
            for k, v in dictionary.items():
                if (k == key):
                    if (isinstance(v, dict)):
                        dictionary[k].update(value)
                    elif (isinstance(v, list)):
                        for val in dictionary[k]:
                            val.update(value)
                else:
                    self.reverse_loop(dictionary[k], key, value)
        elif (isinstance(dictionary, list)):
            for d in dictionary:
                self.reverse_loop(d, key, value)

        return dictionary

    def write(self, dataset, levels):
        full_dict = {}
        for level in levels:  # iterating at each level and creating a dictionary and mapping it further down with higher levels
            for key, val in self.make_json(dataset, level):
                if len(key[0]) >= 1:
                    if not full_dict:  # check to ensure this the first iteration and full_dict is empty
                        full_dict[key[0][0]] = val
                    else:  # for iterations when full_dict already been populated with values
                        full_dict = self.reverse_loop(full_dict, key[0][0], val)
                elif len(key[0]) == 0 and level == 1:
                    full_dict = val

        return full_dict

    def translate_nsd(self, ds):
        return self.write(ds, range(8))


class transformation():

    def sub_ds(self, df, parent, level):

        new_df = pd.DataFrame(columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'id'])

        for index, row in df[(df['parent_key'] == parent) & (df['level'] == level)].iterrows():
            new_df = new_df.append(row)

        return new_df

    def search_sub_ds(self, df, parent, level):

        if len(df[(df['parent_key'] == parent) & (df['level'] == level) & (df['value'].isnull())]['key'].values) > 0:
            return df[(df['parent_key'] == parent) & (df['level'] == level) & (df['value'].isnull())]['key'].values
        else:
            return []

    def ds_loop(self, ds, parent, level):

        yield self.sub_ds(ds,parent,level)

        if len(self.search_sub_ds(ds, parent, level)) > 0:
            for k in np.unique(self.search_sub_ds(ds, parent, level)):
                for item in self.ds_loop(ds, k, level + 1):
                    yield item

    def ret_ds(self, ds, key, level):

        temp = list(self.ds_loop(ds, key, level))
        temp_ds = pd.DataFrame(columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'id'])
        for i in range(len(temp)):
            temp_ds = pd.concat([temp_ds, temp[i]], axis=0)

        return temp_ds


class mapping():

    def insert_mapping(self, record):

        osm_sonata_vnfd_mapping = [
            [1, 2, 'vnfd-catalog', 'schema-version', 0, 1, 'root', 'descriptor_version'],
            [2, 3, 'vnfd', 'name', 0, 1, 'root', 'name'],
            [2, 3, 'vnfd', 'vendor', 0, 1, 'root', 'vendor'],
            [2, 3, 'vnfd', 'description', 0, 1, 'root', 'description'],
            [2, 3, 'vnfd', 'version', 0, 1, 'root', 'version'],
            [2, 3, 'vnfd', 'internal-vld', 0, 1, 'root', 'virtual_links'],
            [2, 3, 'vnfd', 'connection-point', 0, 1, 'root', 'connection_points'],
            [2, 3, 'vnfd', 'vdu', 0, 1, 'root', 'virtual_deployment_units'],
            [2, 3, 'vnfd', 'monitoring-param', 0, 1, 'root', 'monitoring_rules'],
        ]

        osm_sonata_vl_mapping = [
            [3, 4, 'internal-vld', 'id', 1, 2, 'virtual_links', 'id'],
            [3, 4, 'internal-vld', 'type', 1, 2, 'virtual_links', 'connectivity_type'],
            [3, 4, 'internal-vld', 'internal-connection-point-ref', 1, 2, 'virtual_links',
             'connection_points_reference'],
        ]

        osm_sonata_cp_mapping = [
            [3, 4, 'connection-point', 'id', 1, 2, 'connection_points', 'id'],
            [3, 4, 'connection-point', 'type', 1, 2, 'connection_points', 'type'],
        ]

        osm_sonata_vdu_mapping = [
            [3, 4, 'vdu', 'id', 1, 2, 'virtual_deployment_units', 'id'],
            [3, 4, 'vdu', 'vm-flavor', 1, 2, 'virtual_deployment_units', 'resource_requirements'],
            [3, 4, 'vdu', 'image', 1, 2, 'virtual_deployment_units', 'vm_image'],
            [3, 4, 'vdu', 'image-checksum', 1, 2, 'virtual_deployment_units', 'vm_image_md5'],
            [3, 4, 'vdu', 'internal-connection-point', 1, 2, 'virtual_deployment_units', 'connection_points'],
            [4, 5, 'vm-flavor', 'vcpu-count', 2, 3, 'resource_requirements', 'cpu'],
            [4, 5, 'vm-flavor', 'vcpu-count', 3, 4, 'cpu', 'vcpus'],
            [4, 5, 'vm-flavor', 'memory-mb', 2, 3, 'resource_requirements', 'memory'],
            [4, 5, 'vm-flavor', 'memory-mb', 3, 4, 'memory', 'size'],
            [4, 5, 'vm-flavor', 'memory-mb', 3, 4, 'memory', 'size_unit'],
            [4, 5, 'vm-flavor', 'storage-gb', 2, 3, 'resource_requirements', 'storage'],
            [4, 5, 'vm-flavor', 'memory-mb', 3, 4, 'storage', 'size'],
            [4, 5, 'vm-flavor', 'memory-mb', 3, 4, 'storage', 'size_unit'],
            [4, 5, 'internal-connection-point', 'id', 2, 3, 'connection_points', 'id'],
            [4, 5, 'internal-connection-point', 'type', 2, 3, 'connection_points', 'type'],
        ]

        mapping_vnfd = pd.DataFrame(osm_sonata_vnfd_mapping,
                                    columns=["osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                             "son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_vl = pd.DataFrame(osm_sonata_vl_mapping,
                                  columns=["osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_cp = pd.DataFrame(osm_sonata_cp_mapping,
                                  columns=["osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_vdu = pd.DataFrame(osm_sonata_vdu_mapping,
                                   columns=["osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                            "son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        mapping_vnfd.index = [str(i) for i in mapping_vnfd.index]
        osm_son_vl.index = [str(i) for i in osm_son_vl.index]
        osm_son_cp.index = [str(i) for i in osm_son_cp.index]
        osm_son_vdu.index = [str(i) for i in osm_son_vdu.index]

        temp = mapping_vnfd.to_dict()
        id = record.insert(temp)

        temp = osm_son_vl.to_dict()
        id = record.insert(temp)

        temp = osm_son_cp.to_dict()
        id = record.insert(temp)

        temp = osm_son_vdu.to_dict()
        id = record.insert(temp)

    def insert_vnfd(self, record, framework):
        if framework == 'osm':
            vnfd = yaml.load(open(r"firewall-vnfd.yaml"))

        elif framework == 'sonata':
            vnfd = yaml.load(open(r"hackfest_http_vnfd.yaml"))

        id = record.insert(vnfd)

        return id

    def translate_to_osm(self, received_file):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client.descriptors
        db2 = client.mapping_vnfd
        record = db2.vnfd_test
        print(client.list_database_names())
        received_file = yaml.load(open(r"/home/suheel/Documents/SONATA_vnfd/iperf-vnfd.yaml"))

        if 'eu.5gtango' or 'virtual_deployment_units' in received_file:
            print("Yes")
            # doc = db["osm_vnfd"]
            sonata = received_file
            reader = Reader()
            sonata_dataset = pd.DataFrame(reader.dict_parser(sonata, 'root', 1, 1), columns=
            ['parent_level', 'parent_key', 'level', 'key', 'value', 'id'])
            sonata_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
            sonata_dataset.fillna('NULL', inplace=True)
            res = record.find()
            t = [i for i in res]

            if (len(t) == 0):
                insert = mapping()
                insert.insert_mapping(record)

                res = record.find()
                t = [i for i in res]
                print(t[1])
            else:
                pass

            map = transformation()
            osm_sonata = pd.DataFrame.from_dict(t[0])
            # osm_sonata_vl = pd.DataFrame.from_dict(t[1])
            osm_sonata_cp = pd.DataFrame.from_dict(t[2])
            # osm_sonata_vdu = pd.DataFrame.from_dict(t[3])

            sonata_dataset = pd.DataFrame(reader.dict_parser(sonata, 'root', 1, 1), columns=
            ['parent_level', 'parent_key', 'level', 'key', 'value', 'id'])

            dataset = pd.merge(sonata_dataset, osm_sonata,
                               left_on=['key', 'parent_key', 'level', 'parent_level'],
                               right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')

            dataset.fillna('NULL', inplace=True)
            dataset = dataset[['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'id']]
            dataset.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']

            df_cp = map.ret_ds(sonata_dataset, 'connection_points', 2)
            df_cp['level'] = df_cp['level'].astype('int64')
            df_cp['parent_level'] = df_cp['parent_level'].astype('int64')
            df_son_cp = pd.merge(df_cp, osm_sonata_cp,
                                 left_on=['key', 'parent_key', 'level', 'parent_level'],
                                 right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
            df_son_cp.fillna('NULL', inplace=True)
            df_son_cp = df_son_cp[['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'id']]
            df_son_cp.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']
            df_son_cp.sort_values(['id'], inplace=True)
            dataset = dataset.append(df_son_cp)

            df_vdu = map.ret_ds(sonata_dataset, 'virtual_deployment_units', 2)
            df_vdu['level'] = df_vdu['level'].astype('int64')
            df_vdu['parent_level'] = df_vdu['parent_level'].astype('int64')
            df_vdu['value'] = df_vdu['value'].astype('object')
            df_son_vdu = pd.merge(df_vdu, osm_sonata_vdu,
                                  left_on=['key', 'parent_key', 'level', 'parent_level'],
                                  right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')

            df_son_vdu.sort_values(['osm_level'], inplace=True)
            df_son_vdu = df_son_vdu[['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'id']]
            df_son_vdu.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']
            df_son_vdu.sort_values(['id'], inplace=True)





    def translate_to_sonata(self, received_file):
        record = self.db_mappings.vnfd_mapping

        if 'vnfd:vnfd-catalog' in received_file:

            doc = self.db_descriptors["translated_vnfd"]

            osm = received_file
            reader = Reader()

            osm_dataset = pd.DataFrame(reader.dict_parser(osm, 'root', 1, 0),
                                       columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'id'])

            osm_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
            osm_dataset.fillna('NULL', inplace=True)

            res = record.find()
            t = [i for i in res]

            if (len(t) == 0):
                insert = insert_into_db(self.client)
                insert.insert_mapping()
                res = record.find()
                t = [i for i in res]

            map = transformation()

            osm_sonata = pd.DataFrame.from_dict(t[0])
            osm_son_vl = pd.DataFrame.from_dict(t[1])
            osm_son_cp = pd.DataFrame.from_dict(t[2])
            osm_son_vdu = pd.DataFrame.from_dict(t[3])

            dataset = pd.merge(osm_dataset, osm_sonata,
                               left_on=['key', 'parent_key', 'level', 'parent_level'],
                               right_on=['osm_key', 'osm_parent_key', 'osm_level', 'osm_parent_level'], how='inner')
            dataset.fillna('NULL', inplace=True)
            dataset = dataset[['son_parent_level', 'son_level', 'son_parent_key', 'son_key', 'value', 'id']]
            dataset.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']

            df = map.ret_ds(osm_dataset, 'internal-vld', 4)
            vl = map.osm_vld(df)
            vl['level'] = vl['level'].astype('int64')
            vl['parent_level'] = vl['parent_level'].astype('int64')

            df_osm_vld = pd.merge(vl, osm_son_vld,
                                  left_on=['key', 'parent_key', 'level', 'parent_level'],
                                  right_on=['osm_key', 'osm_parent_key', 'osm_level', 'osm_parent_level'], how='inner')

            df_osm_vld = df_osm_vld[['son_parent_level', 'son_level', 'son_parent_key', 'son_key', 'value', 'id']]
            df_osm_vld.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']

            dataset = dataset.append(df_osm_vld)



