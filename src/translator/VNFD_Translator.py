import pandas as pd
import numpy as np
import yaml


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


class Writer():

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

    def translate_vnfd(self, ds):

        return self.write(ds, range(8))


class mapping():

    def insert_mapping(self, record):
        osm_sonata_vnfd_mapping = [
            [1, 2, 'vnfd-catalog', 'schema-version', 0, 1, 'root', 'descriptor_version'],
            [2, 3, 'vnfd', 'name', 0, 1, 'root', 'name'],
            [2, 3, 'vnfd', 'vendor', 0, 1, 'root', 'vendor'],
            [2, 3, 'vnfd', 'description', 0, 1, 'root', 'description'],
            [2, 3, 'vnfd', 'version', 0, 1, 'root', 'version'],
            [2, 3, 'vnfd', 'internal-vld', 0, 1, 'root', 'virtual_links'],
            [2, 3, 'vnfd', 'connection-point', 0, 1, 'root', 'connections_points'],
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
            [3, 4, 'connection-point', 'type', 1, 2, 'connection_points', 'id'],
        ]

        osm_sonata_vdu_mapping = [
            [3, 4, 'vdu', 'id', 1, 2, 'virtual_deployment_units', 'id'],
            [3, 4, 'vdu', 'vm-flavor', 1, 2, 'virtual_deployment_units', 'resource_requirements'],
            [3, 4, 'vdu', 'image', 1, 2, 'virtual_deployment_units', 'vm_image'],
            [3, 4, 'vdu', 'image-checksum', 1, 2, 'virtual_deployment_units', 'vm_image_md5'],
            [3, 4, 'vdu', 'internal-connection-point', 1, 2, 'virtual_deployment_units', 'connection_points'],
        ]

        mapping = pd.DataFrame(osm_sonata_vnfd_mapping,
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





