import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId


class read_dict():

    def dict_parser(self, dictionary, key, level, lineage):
        '''
        reads a dictionary and iterate over its items in a heirarchy and returns all
        information (parent key, parent level, current key, current level, current value, primary key)
        at each level.

        Params
        ------
        dictionary : dict
            dictionary containing the descriptor details
        key : str
            the name of the root node/key (while calling this function for the first time this variable can be any string).
        level : int
            the level of the root node/key (default : 1)
        lineage : str
            variable to maintain and determine the lineage of items

        Returns
        -------
        python.iterator
            yields a a list of [parent level valule, parent key value, current level value, current key value, item index value]
        at each level of iteration

        '''

        if isinstance(dictionary, dict):

            for k, v in dictionary.items():

                if isinstance(v, str) or isinstance(v, int):
                    result = [level - 1, str(key), level, str(k), v, lineage]
                    yield result

                if isinstance(v, dict):
                    yield [level - 1, str(key), level, str(k), None, None]
                    for res in self.dict_parser(v, k, level + 1, str(lineage) + '|' + key + '|0'):
                        yield res

                elif isinstance(v, list):
                    if (isinstance(v[0], str)):
                        yield [level - 1, str(key), level, str(k), v, lineage]
                    else:
                        yield [level - 1, str(key), level, str(k), None, None]
                        for j, i in enumerate(v):
                            for res in self.dict_parser(i, k, level + 1, (str(lineage) + '|' + key + '|' + str(j))):
                                yield res

        else:
            pass


class write_dict():

    def append_dict(self, parent_key, lvl, dictionary):
        '''
        reads a parent key , a list of values that should be mapped to the parent key and an empty dictionary
        to contain the result.

        Params
        ------
        parent_key : str
            contains the key which is to be assigned a value
        lvl : list
            contains an array of items which needs to be transformed properly before assigning to the key
       dictionary : dict
            empty dictionary for the result

        Returns
        -------
        dict
            returns a full dictionary containing a key and a value which is another dictionary

        '''
        inner_dict = {}
        list_dict = []

        k = list(lvl[0][1].keys())[0]
        v = list(lvl[0][1].values())[0]
        inner_dict.update({k: v})

        for i in range(1, len(lvl)):

            k = list(lvl[i][1].keys())[0]
            v = list(lvl[i][1].values())[0]

            if k in inner_dict.keys():
                list_dict.append(inner_dict)
                inner_dict = {}
                inner_dict.update({k: v})

            else:
                inner_dict.update({k: v})

        list_dict.append(inner_dict)
        dictionary[parent_key] = list_dict

        return dictionary

    def make_json(self, dataset, level):
        '''
        takes a python DataFrame and iterate over all the keys at a particular level
        which are mapped to higher levels

        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the details at a particular level
        levels : int
            current level to be checked

        Returns
        -------
        list , dict , pos
            returns an iterator containing both a list of parent key values and a current level dictionary

        '''

        s = dataset[(dataset['level'] == level) & (dataset['value'] != 'NULL')].groupby(by=['parent_key']).agg(
            {'key': lambda x: x.nunique()})  # getting the unique set of keys whose values are at higher levels
        # along with the number of items
        # (in case the values at the higher levels are repeated in an array)
        s = s.to_dict()  # converting the set of keys

        for parent, _ in s['key'].items():  # iterating over each keys found in previous step
            lvl_dict = []
            parent_key = []
            parent_pos = []

            lvl = pd.DataFrame(list(dataset[(dataset['level'] == level) & (dataset['value'] != 'NULL') &
                                            (dataset['parent_key'] == parent)][['lineage', 'key', 'value']].apply(
                lambda x: [x.lineage[:-2], {x.key: x.value}]
                if (x.lineage[-2] == '|')
                else [x.lineage, {x.key: x.value}], axis=1).values))

            val = [x.values for _, x in lvl.groupby(lvl[0])]

            length = 2
            for i in range(2, dataset['level'].max(), 2):
                if len(np.unique(lvl[0].apply(lambda x: x.split("|")[:-i]).values)) == 1:
                    length = i
                    break

            for g, l in enumerate(val):

                lvl_dict.append(self.append_dict(parent, l, {}))  # calling append function to tidy up the dictionary
                parent_temp = []
                parent_pos_temp = []

                for j in range(0, length, 2):
                    parent_temp.append(val[g][0][0].split('|')[-j - 1])
                    parent_pos_temp.append(val[g][0][0].split('|')[-j - 2])

                parent_key.append(parent_temp)
                parent_pos.append(parent_pos_temp)

            yield parent_key, lvl_dict, parent_pos

    def reverse_loop(self, dictionary, key, value, pos):
        '''
        takes a dictionary and a key value pair. The key is searched in the dictionary,
        when found the value is mapped to the key.

        Params
        ------
        dictionary : python dict / python list
            variable containing the values at a particular level
        key : list
            contains the lineage of parent keys
        value : int / list / str
            contains the item/s which is mapped to the key
        pos : list
            contains the positions of the lineage of parent keys

        Returns
        -------
        dict
            returns a complete dictionary/list of a particular level
        '''
        if (isinstance(dictionary, dict)):

            for k, v in dictionary.items():
                if len(key) == 0:
                    return dictionary

                if (k == key[-1]):
                    key.pop()

                    if len(key) == 0:
                        if (isinstance(v, dict)):
                            dictionary[k].update(value)

                        elif (isinstance(v, list)):
                            dictionary[k][int(pos[-1])].update(value)

                        return dictionary

                    else:
                        p = int(pos.pop())
                        self.reverse_loop(dictionary[k][p], key, value, pos)
                else:
                    self.reverse_loop(dictionary[k], key, value, pos)

        elif (isinstance(dictionary, list)):

            for d in dictionary:
                self.reverse_loop(d, key, value, pos)

        return dictionary

    def write(self, dataset, levels):
        '''
        takes a pandas.DataFrame and an array containing the number of levels
        and iterates over each level to call make_json and reverse_loop functions in order to create
        a full dictionary at each level together with mapping/connecting it with its previous level key

        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the descriptor details
        levels : array
            array of levels in the descriptor

        Returns
        -------
        dict
            returns a dictionary of the translated descriptor

        '''
        full_dict = {}

        for level in levels:  # iterating at each level and creating a dictionary and mapping it further down with higher levels
            for key, val, pos in self.make_json(dataset.sort_values(by='lineage'), level):

                if not full_dict:  # check to ensure this the first iteration and full_dict is empty
                    for i in range(len(key)):
                        full_dict[key[i][0]] = val[i]

                else:  # for iterations when full_dict already been populated with values
                    for i in range(len(key)):
                        pos[i] = [int(p) for p in pos[i]]
                        full_dict = self.reverse_loop(full_dict, key[i], val[i], pos[i])

        return full_dict

    def translate_nsd(self, ds):
        '''
        takes a pandas.DataFrame and pass it as parameter to write function
        along with an array containing the number of levels

        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the descriptor details

        Returns
        -------
        dict
            returns a dictionary of the translated descriptor

        '''
        return self.write(ds.sort_values(by='lineage'), range(8))


class transformation():

    def sub_ds(self, df, parent, level):
        '''
        reads a pandas.DataFrame, a parent key and a current level

        Params
        ------
        df : pandas.DataFrame
            dataframe containing the full set
        parent : str
            the parent key based on which a subset dataframe is created
        level : int
            the current level which is also added as a filter parameter with parent

        Returns
        -------
        pandas.DataFrame
            returns a subset dataframe filtered by the parent key and current level


        '''
        new_df = pd.DataFrame(columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])

        for index, row in df[(df['parent_key'] == parent) & (df['level'] == level)].iterrows():
            new_df = new_df.append(row)

        return new_df

    def search_sub_ds(self, df, parent, level):
        '''
        reads a pandas.DataFrame, a parent key and a current level

        Params
        ------
        df : pandas.DataFrame
            dataframe containing the full set
        parent : str
            the parent key based on which a subset dataframe is created
        level : int
            the current level which is also added as a filter parameter with parent

        Returns
        -------
        list
            returns an array


        '''

        if len(df[(df['parent_key'] == parent) & (df['level'] == level) & (df['value'] == 'NULL')][
                   'key'].values) > 0:
            return df[(df['parent_key'] == parent) & (df['level'] == level) & (df['value'] == 'NULL')]['key'].values

        else:
            return []

    def ds_loop(self, ds, parent, level):
        '''
        reads a pandas.DataFrame, a parent key and a current level

        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the full set
        parent : str
            the parent key based on which a subset dataframe is created
        level : int
            the current level which is also added as a filter parameter with parent

        Returns
        -------
        python.iterator
            returns a iterator


        '''
        yield self.sub_ds(ds, parent, level)

        if len(self.search_sub_ds(ds, parent, level)) > 0:
            for k in np.unique(self.search_sub_ds(ds, parent, level)):
                for item in self.ds_loop(ds, k, level + 1):
                    yield item

    def ret_ds(self, ds, key, level):
        '''
        reads a pandas.DataFrame, a parent key and a current level

        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the full set
        key : str
            the parent key based on which a subset dataframe is created
        level : int
            the current level which is also added as a filter parameter with parent

        Returns
        -------
        pandas.DataFrame
            returns a subset dataframe filtered by the parent key and current level


        '''
        temp = list(self.ds_loop(ds, key, level))
        temp_ds = pd.DataFrame(columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])

        for i in range(len(temp)):
            temp_ds = pd.concat([temp_ds, temp[i]], axis=0)

        return temp_ds


class mapping():

    def insert_mapping(self, record):

        osm_sonata_vnfd_mapping = [
            ['0|preroot|0|root|0', 1, 2, 'vnfd-catalog', 'schema-version', '0|preroot|0', 0, 1, 'root',
             'descriptor_version'],
            ['0|preroot|0|root|0|vnfd-catalog|0', 2, 3, 'vnfd', 'name', '0|preroot|0', 0, 1, 'root', 'name'],
            ['0|preroot|0|root|0|vnfd-catalog|0', 2, 3, 'vnfd', 'vendor', '0|preroot|0', 0, 1, 'root', 'vendor'],
            ['0|preroot|0|root|0|vnfd-catalog|0', 2, 3, 'vnfd', 'description', '0|preroot|0', 0, 1, 'root',
             'description'],
            ['0|preroot|0|root|0|vnfd-catalog|0', 2, 3, 'vnfd', 'version', '0|preroot|0', 0, 1, 'root', 'version'],
            ['0|preroot|0|root|0|vnfd-catalog|0', 2, 3, 'vnfd', 'internal-vld', '0|preroot|0', 0, 1, 'root',
             'virtual_links'],
            ['0|preroot|0|root|0|vnfd-catalog|0', 2, 3, 'vnfd', 'connection-point', '0|preroot|0', 0, 1, 'root',
             'connection_points'],
            ['0|preroot|0|root|0|vnfd-catalog|0', 2, 3, 'vnfd', 'vdu', '0|preroot|0', 0, 1, 'root',
             'virtual_deployment_units'],
            ['0|preroot|0|root|0|vnfd-catalog|0', 2, 3, 'vnfd', 'monitoring-param', '0|preroot|0', 0, 1, 'root',
             'monitoring_rules'],
        ]

        osm_sonata_vl_mapping = [
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'internal-vld', 'id', '0|preroot|0|root|0', 1, 2,
             'virtual_links', 'id'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'internal-vld', 'type', '0|preroot|0|root|0', 1, 2,
             'virtual_links', 'connectivity_type'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'internal-vld', 'internal-connection-point',
             '0|preroot|0|root|0', 1, 2, 'virtual_links', 'connection_points_reference'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'internal-connection-point', 'id-ref',
             '0|preroot|0|root|0', 1, 2, 'virtual_links', 'connection_points_reference'],
        ]

        osm_sonata_cp_mapping = [
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'connection-point', 'id', '0|preroot|0|root|0', 1, 2,
             'connection_points', 'id'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'connection-point', 'type', '0|preroot|0|root|0', 1, 2,
             'connection_points', 'type'],
        ]

        osm_sonata_vdu_mapping = [
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'vdu', 'id', '0|preroot|0|root|0', 1, 2,
             'virtual_deployment_units', 'id'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'vdu', 'vm-flavor', '0|preroot|0|root|0', 1, 2,
             'virtual_deployment_units', 'resource_requirements'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'vdu', 'image', '0|preroot|0|root|0', 1, 2,
             'virtual_deployment_units', 'vm_image'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'vdu', 'image-checksum', '0|preroot|0|root|0', 1, 2,
             'virtual_deployment_units', 'vm_image_md5'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0', 3, 4, 'vdu', 'internal-connection-point', '0|preroot|0|root|0',
             1, 2, 'virtual_deployment_units', 'connection_points'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'vm-flavor', 'vcpu-count',
             '0|preroot|0|root|0|virtual_deployment_units|0', 2, 3, 'resource_requirements', 'cpu'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'vm-flavor', 'vcpu-count',
             '0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|0', 3, 4, 'cpu', 'vcpus'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'vm-flavor', 'memory-mb',
             '0|preroot|0|root|0|virtual_deployment_units|0', 2, 3, 'resource_requirements', 'memory'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'vm-flavor', 'memory-mb',
             '0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|0', 3, 4, 'memory', 'size'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'vm-flavor', 'memory-mb',
             '0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|0', 3, 4, 'memory', 'size_unit'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'vm-flavor', 'storage-gb',
             '0|preroot|0|root|0|virtual_deployment_units|0', 2, 3, 'resource_requirements', 'storage'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'vm-flavor', 'storage-gb',
             '0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|0', 3, 4, 'storage', 'size'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'vm-flavor', 'storage-gb',
             '0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|0', 3, 4, 'storage', 'size_unit'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'internal-connection-point', 'id',
             '0|preroot|0|root|0|virtual_deployment_units|0', 2, 3, 'connection_points', 'id'],
            ['0|preroot|0|root|0|vnfd-catalog|0|vnfd|0|internal-vld|0', 4, 5, 'internal-connection-point', 'type',
             '0|preroot|0|root|0|virtual_deployment_units|0', 2, 3, 'connection_points', 'type'],
        ]

        mapping_vnfd = pd.DataFrame(osm_sonata_vnfd_mapping,
                                    columns=["osm_lineage", "osm_parent_level", "osm_level", "osm_parent_key",
                                             "osm_key",
                                             "son_lineage", "son_parent_level", "son_level", "son_parent_key",
                                             "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_vl = pd.DataFrame(osm_sonata_vl_mapping,
                                  columns=["osm_lineage", "osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_lineage", "son_parent_level", "son_level", "son_parent_key",
                                           "son_key"]).sort_values(by=['son_level', 'osm_level'], ascending=True)

        osm_son_cp = pd.DataFrame(osm_sonata_cp_mapping,
                                  columns=["osm_lineage", "osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_lineage", "son_parent_level", "son_level", "son_parent_key",
                                           "son_key"]).sort_values(by=['son_level', 'osm_level'], ascending=True)

        osm_son_vdu = pd.DataFrame(osm_sonata_vdu_mapping,
                                   columns=["osm_lineage", "osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                            "son_lineage", "son_parent_level", "son_level", "son_parent_key",
                                            "son_key"]).sort_values(by=['son_level', 'osm_level'], ascending=True)

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

    def translate_to_osm_vnfd(self, received_file):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client.descriptors
        db2 = client.mapping_vnfd
        record = db2.vnfd_test
        print(client.list_database_names())
        received_file = yaml.load(open(r"/home/suheel/Documents/SONATA_vnfd/iperf-vnfd.yaml"))

        if 'eu.5gtango' or 'virtual_deployment_units' in received_file:
            # print("Yes")
            # doc = db["osm_vnfd"]
            sonata = received_file
            reader = read_dict()

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
            osm_sonata_vl = pd.DataFrame.from_dict(t[1])
            osm_sonata_cp = pd.DataFrame.from_dict(t[2])
            osm_sonata_vdu = pd.DataFrame.from_dict(t[3])

            sonata_dataset = pd.DataFrame(reader.dict_parser(sonata, 'root', 1, '0|preroot|0'), columns=
            ['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])
            sonata_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
            sonata_dataset.fillna('NULL', inplace=True)

            dataset = pd.merge(sonata_dataset, osm_sonata,
                               left_on=['key', 'parent_key', 'level', 'parent_level'],
                               right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
            dataset.fillna('', inplace=True)
            dataset = dataset[
                ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
            dataset.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']

            df_cp = map.ret_ds(sonata_dataset, 'connection_points', 2)
            df_cp['level'] = df_cp['level'].astype('int64')
            df_cp['parent_level'] = df_cp['parent_level'].astype('int64')
            df_son_cp = pd.merge(df_cp, osm_sonata_cp,
                                 left_on=['key', 'parent_key', 'level', 'parent_level'],
                                 right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
            df_son_cp.fillna('', inplace=True)
            df_son_cp = df_son_cp[
                ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
            df_son_cp.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']
            dataset['lineage'] = dataset.apply(lambda x: x['osm_lineage'] + x['lineage'].split('|')[-1], axis=1)
            df_son_cp.sort_values(['lineage'], inplace=True)
            dataset = dataset.append(df_son_cp)

            df_vl = map.ret_ds(sonata_dataset, 'virtual_links', 2)
            df_vl['level'] = df_vl['level'].astype('int64')
            df_vl['parent_level'] = df_vl['parent_level'].astype('int64')
            df_vl['value'] = df_vl['value'].astype('object')
            df_son_vl = pd.merge(df_vl, osm_sonata_vl,
                                 left_on=['key', 'parent_key', 'level', 'parent_level'],
                                 right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
            df_son_vl.sort_values(['osm_level'], inplace=True)
            df_son_vl = df_son_vl[
                ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
            df_son_vl.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']
            dataset['lineage'] = dataset.apply(lambda x: x['osm_lineage'] + x['lineage'].split('|')[-1], axis=1)
            df_son_vl.sort_values(['lineage'], inplace=True)
            for i, row in df_son_vl.iterrows():
                if isinstance(row['value'], list) and (row['key'] == 'id-ref'):
                    df_son_vl.at[i, 'value'] = row['value'][0].split(':')[1]
                elif (row['parent_key'] == 'internal-vld' and row['key'] == 'internal-connection-point'):
                    df_son_vl.at[i, 'value'] = ''
            dataset = dataset.append(df_son_vl)

            df_vdu = map.ret_ds(sonata_dataset, 'virtual_deployment_units', 2)
            df_vdu['level'] = df_vdu['level'].astype('int64')
            df_vdu['parent_level'] = df_vdu['parent_level'].astype('int64')
            df_vdu['value'] = df_vdu['value'].astype('object')
            df_son_vdu = pd.merge(df_vdu, osm_sonata_vdu,
                                  left_on=['key', 'parent_key', 'level', 'parent_level'],
                                  right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
            df_son_vdu.sort_values(['osm_level'], inplace=True)
            df_son_vdu = df_son_vdu[
                ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
            df_son_vdu.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']
            dataset['lineage'] = dataset.apply(lambda x: x['osm_lineage'] + x['lineage'].split('|')[-1], axis=1)
            df_son_vdu.sort_values(['lineage'], inplace=True)

            dataset = dataset.append(df_son_vdu)
            dataset.fillna('', inplace=True)




    def translate_to_sonata_vnfd(self, received_file):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client.descriptors
        db2 = client.mapping_vnfd
        record = db2.vnfd_test
        print(client.list_database_names())
        received_file = yaml.load(open(r"/home/suheel/Documents/OSM_vnfd/hackfest_cloudinit_vnfd.yaml"))

        # record = self.db_mappings.vnfd_mapping

        if 'vnfd:vnfd-catalog' in received_file:

            # doc = self.db_descriptors["translated_vnfd"]

            osm = received_file
            reader = Reader()

            osm_dataset = pd.DataFrame(reader.dict_parser(osm, 'root', 1, 0),
                                       columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'id'])

            osm_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
            # osm_dataset.fillna('NULL', inplace=True)

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

            cp = map.ret_ds(osm_dataset, 'connection-point', 4)
            cp['level'] = cp['level'].astype('int64')
            cp['parent_level'] = cp['parent_level'].astype('int64')

            df_osm_cp = pd.merge(cp, osm_son_cp,
                                 left_on=['key', 'parent_key', 'level', 'parent_level'],
                                 right_on=['osm_key', 'osm_parent_key', 'osm_level', 'osm_parent_level'], how='inner')

            df_osm_cp = df_osm_cp[['son_parent_level', 'son_level', 'son_parent_key', 'son_key', 'value', 'id']]
            df_osm_cp.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']
            df_osm_cp.sort_values(['id'], inplace=True)
            df_osm_cp

            dataset = dataset.append(df_osm_cp)

            vl = map.ret_ds(osm_dataset, 'internal-vld', 4)
            # vl = map.osm_vld(df)
            vl['level'] = vl['level'].astype('int64')
            vl['parent_level'] = vl['parent_level'].astype('int64')

            df_osm_vl = pd.merge(vl, osm_son_vl,
                                 left_on=['key', 'parent_key', 'level', 'parent_level'],
                                 right_on=['osm_key', 'osm_parent_key', 'osm_level', 'osm_parent_level'], how='inner')

            df_osm_vl = df_osm_vl[['son_parent_level', 'son_level', 'son_parent_key', 'son_key', 'value', 'id']]
            df_osm_vl.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']

            dataset = dataset.append(df_osm_vl)

            vdu = map.ret_ds(osm_dataset, 'vdu', 4)
            vdu['level'] = vdu['level'].astype('int64')
            vdu['parent_level'] = vdu['parent_level'].astype('int64')

            df_osm_vdu = pd.merge(vdu, osm_son_vdu,
                                  left_on=['key', 'parent_key', 'level', 'parent_level'],
                                  right_on=['osm_key', 'osm_parent_key', 'osm_level', 'osm_parent_level'], how='inner')

            df_osm_vdu = df_osm_vdu[['son_parent_level', 'son_level', 'son_parent_key', 'son_key', 'value', 'id']]
            df_osm_vdu.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']

            # f_osm_vdu.sort_values(['id'], inplace = True)
            dataset = dataset.append(df_osm_vdu)


class TranslatorService():
    name = "translator_service"

    @rpc
    def hello(self, name):

        client = pymongo.MongoClient("mongodb://mongo:27017/")
        set = setup(client)

        if name == 'sonata_to_osm':

            insert = insert_into_db(client)
            ref = insert.insert_nsd('sonata')
            rcvd_file = set.get_source_nsd(ref)
            var = set.translate_to_osm(rcvd_file)
            trnsltd_file = set.get_source_nsd(var)

        elif name == 'osm_to_sonata':

            insert = insert_into_db(client)
            ref = insert.insert_nsd('osm')
            rcvd_file = set.get_source_nsd(ref)
            var = set.translate_to_sonata(rcvd_file)
            trnsltd_file = set.get_source_nsd(var)

        else:
            var = 'wrong choice!!!'

        return str(str(rcvd_file) + '\n\n\n has been converted to \n\n\n' + str(trnsltd_file))  # str(var)#
