from nameko.rpc import rpc
import pandas as pd
import numpy as np
import yaml

class read_dict():

    def dict_parser(self,dictionary, key, level, pk):
        
        if isinstance(dictionary, dict):
            for k, v in dictionary.items():
            
                if isinstance(v, str) or isinstance(v, int):
                    result = ['level= ' + str(level - 1), str(key), 'level= ' + str(level), str(k), str(v),
                              'id= ' + str(pk)]
                    yield result
                    
                if isinstance(v, dict):
                    yield ['level= ' + str(level - 1), str(key), 'level= ' + str(level), str(k), None, None]
                    for res in self.dict_parser(v, k, level + 1, None):
                        yield res
                        
                elif isinstance(v, list):
                
                    if (isinstance(v[0], str)):
                        yield ['level= ' + str(level - 1), str(key), 'level= ' + str(level), str(k), v,
                               'id= ' + str(pk)]
                               
                        for i in v:
                        
                            for res in self.dict_parser(i, k, level + 1, None):
                                yield res
                    else:
                    
                        yield ['level= ' + str(level - 1), str(key), 'level= ' + str(level), str(k), None, None]
                        for j, i in enumerate(v):
                            for res in self.dict_parser(i, k, level + 1, j + 1):
                                yield res
        else:
            pass

            
class write_dict():

    def append_dict(self,parent_key, lvl, dictionary):

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

    def getKey(self,item):
        return item[0]

    def make_json(self,dataset, level):

        parent_key = []
        parent_level = dataset[(dataset['level'] == level) & (dataset['value'] != 'NULL')]['parent_level'].unique()

        s = dataset[(dataset['level'] == level) & (dataset['value'] != 'NULL')].groupby(by=['parent_key']).agg(
            {'key': lambda x: x.nunique()})
        s = s.to_dict()
        lvl_dict = {}

        for parent, ele in s['key'].items():
		
            lvl = list(
                dataset[(dataset['level'] == level) & (dataset['value'] != 'NULL') & (dataset['parent_key'] == parent)][
                    ['id', 'key', 'value']].apply(lambda x: (x.id, x.key + ' : ' + str(x.value)), axis=1).values)
					
            lvl_dict.update(self.append_dict(parent, sorted(lvl, key=self.getKey), {}))
			
            parent_key.append(np.unique(
                    dataset[(dataset['key'] == parent) & (dataset['level'] == parent_level[0])]['parent_key'].values))

        parent_key = [x for x in parent_key if x]

        return lvl_dict, np.unique(parent_key)

    def reverse_loop(self,dictionary, key, value):

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

    def write(self,dataset, levels):

        full_dict = {}
        for level in levels:
            key_val = self.make_json(dataset, level)
            if key_val[1]:
                if not full_dict:
                    full_dict[key_val[1][0]] = key_val[0]
                else:
                    full_dict = self.reverse_loop(full_dict, key_val[1][0], key_val[0])
            elif not key_val[1] and level == 'level= 1':
                full_dict = key_val[0]

        return full_dict

    def translate_nsd(self,ds):
        return self.write(ds, ['level= 1', 'level= 2', 'level= 3', 'level= 4', 'level= 5', 'level= 6'])
    
class TranslatorService():
    name = "translator_service"
        
    @rpc
    def hello(self, name):


        osm=yaml.load(open(r"hackfest_multivdu_nsd.yaml"))
        
        sonata=yaml.load(open(r"sonata-demo.yml"), Loader=yaml.Loader)
        
        reader = read_dict()
        osm_dataset = pd.DataFrame(reader.dict_parser(osm, 'root', 1, 1),
                                   columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'id'])

        osm_dataset.sort_values(by=['level', 'parent_key'], ascending=True)
        
        sonata_dataset = pd.DataFrame(reader.dict_parser(sonata, 'root', 1, 1),
                                      columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'id'])

        sonata_dataset.sort_values(ascending=True, by=['level', 'parent_key'])

        sonata_dataset.fillna('NULL', inplace=True)
        osm_dataset.fillna('NULL', inplace=True)

        osm_sonata_nsd_mapping = [
            ['level= 2', 'level= 3', 'nsd', 'description', 'level= 0', 'level= 1', 'root', 'description'],
            ['level= 2', 'level= 3', 'nsd', 'vendor', 'level= 0', 'level= 1', 'root', 'vendor'],
            ['level= 2', 'level= 3', 'nsd', 'name', 'level= 0', 'level= 1', 'root', 'name'],
            ['level= 2', 'level= 3', 'nsd', 'version', 'level= 0', 'level= 1', 'root', 'version'],
            ['level= 3', 'level= 4', 'constituent-vnfd', 'member-vnf-index', 'level= 1', 'level= 2',
             'network_functions',
             'vnf_id'],
            ['level= 3', 'level= 4', 'constituent-vnfd', 'vnfd-id-ref', 'level= 1', 'level= 2', 'network_functions',
             'vnf_name'],
            ['level= 3', 'level= 4', 'vld', 'id', 'level= 1', 'level= 2', 'virtual_links', 'id'],
            ['level= 3', 'level= 4', 'vld', 'type', 'level= 1', 'level= 2', 'virtual_links', 'connectivity_type'],
            ['level= 3', 'level= 4', 'connection-point', 'name', 'level= 1', 'level= 2', 'connection_points', 'id'],
            ['level= 3', 'level= 4', 'connection-point', 'type', 'level= 1', 'level= 2', 'connection_points', 'type'],
            ['level= 4', 'level= 5', 'vld-ref', 'vld-id-ref', 'level= 1', 'level= 2', 'connection_points',
             'virtual_link_reference'],
            ['level= 3', 'level= 4', 'vnffgd', 'id', 'level= 1', 'level= 2', 'forwarding_graphs', 'id'],
            ['level= 6', 'level= 7', 'vnfd-connection-point-ref', 'member-vnf-index-ref', 'level= 1', 'level= 2',
             'forwarding_graphs', 'constituent_vnfs'],
            ['level= 3', 'level= 4', 'monitoring-param', 'description', 'level= 1', 'level= 2', 'monitoring_parameters',
             'description'],
            ['level= 3', 'level= 4', 'monitoring-param', 'units', 'level= 1', 'level= 2', 'monitoring_parameters',
             'unit'],
            ['level= 3', 'level= 4', 'monitoring-param', 'value-integer', 'level= 1', 'level= 2',
             'monitoring_parameters',
             'metric'],
        ]

        osm_sonata = pd.DataFrame(osm_sonata_nsd_mapping,
                                  columns=["osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        dataset = pd.merge(sonata_dataset, osm_sonata, left_on=['key', 'level'], right_on=['son_key', 'son_level'],
                           how='right')
        dataset.fillna('NULL', inplace=True)
        dataset = dataset[dataset['value'] != 'NULL'][
            ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'id']]
        dataset.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'id']
        dataset = dataset.append(osm_dataset[osm_dataset['value'] == 'NULL'])

        writer = write_dict()
        
        message = str(writer.translate_nsd(dataset))

        return message

    