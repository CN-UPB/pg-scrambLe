import pandas as pd
import numpy as np
import yaml
import json
import pymongo
from bson.objectid import ObjectId

from descriptorReader import read_dict
from descriptorWriter import write_dict


class setup():
    
    def __init__(self,client = None):
        
        self.client = client
        self.db_descriptors = self.client.descriptors
        self.db_mappings = self.client.mapping

    def get_source_nsd(self,received_ref):

        cursor = self.db_descriptors.list_collection_names()
        for ref in cursor:
            doc = self.db_descriptors.get_collection(ref)
            recieved_file = [ns for ns in doc.find({'_id': ObjectId(received_ref)})]
            if len(recieved_file)>0:
                break
        return recieved_file[0]


    def translate_to_osm(self,received_file):

        record = self.db_mappings.nsd_mapping
                
        if 'eu.5gtango' and 'virtual_deployment_units' in received_file:
        
            doc = self.db_descriptors["translated_vnfd"]
            
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            return translated_ref
            
        elif 'descriptor_schema' and 'network_functions' in received_file:
        
            doc = self.db_descriptors["translated_nsd"]
            
            sonata = received_file
            
            reader = read_dict()

            sonata_dataset = pd.DataFrame(reader.dict_parser(sonata, 'root', 1, '0|preroot|0'), 
                                          columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])
            sonata_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
            sonata_dataset.fillna('NULL', inplace=True)
            
            res = record.find()
            
            t = [i for i in res]
            
            if(len(t) ==0):
                insert = insert_into_db(self.client)
                insert.insert_mapping()
                res = record.find()
                t = [i for i in res]
                   
            
            map= transformation()
                                      
            osm_sonata = pd.DataFrame.from_dict(t[0])
            osm_son_vld = pd.DataFrame.from_dict(t[1])
            osm_son_vnffgd = pd.DataFrame.from_dict(t[2])
            
            dataset=pd.merge(sonata_dataset,osm_sonata,
                 left_on=['key','parent_key','level','parent_level'],
                 right_on=['son_key','son_parent_key','son_level','son_parent_level'],how='inner')

            dataset.fillna('NULL',inplace=True)
            dataset = dataset[['osm_parent_level','osm_level','osm_parent_key','osm_key','value','osm_lineage','lineage']]
            dataset.columns = ['parent_level','level','parent_key','key','value','osm_lineage','lineage']

            dataset = dataset.append(pd.DataFrame([[2,'nsd',3,'vnffgd','NULL','NULL','NULL'],
                                                [2,'nsd',3,'constituent-vnfd','NULL','NULL','NULL'],
                                                [2,'nsd',3,'vld','NULL','NULL','NULL'],
                                                [2,'nsd',3,'connection-point','NULL','NULL','NULL'],
                                                [0,'root',1,'nsd:nsd-catalog','NULL','NULL','NULL'],
                                                [1,'nsd:nsd-catalog',2,'nsd','NULL','NULL','NULL']],
                                               columns = ['parent_level','parent_key','level','key','value','osm_lineage','lineage']))

            dataset['lineage'] = dataset.apply(lambda x : x['osm_lineage'] + x['lineage'].split('|')[-1],axis=1)
            dataset=dataset.sort_values(by= 'lineage',ascending=True)
            
            df = map.ret_ds(sonata_dataset,'virtual_links',2)
            vl = map.son_vld(df,'value','key',':')
            vl['level'] = vl['level'].astype('int64')
            vl['parent_level'] = vl['parent_level'].astype('int64')

            df_son_vld = pd.merge(vl,osm_son_vld,
                             left_on=['key','parent_key','level','parent_level'],
                             right_on=['son_key','son_parent_key','son_level','son_parent_level'],how='inner')

            df_son_vld =  df_son_vld[['osm_parent_level','osm_level','osm_parent_key','osm_key','value','osm_lineage','lineage']]
            df_son_vld.columns = ['parent_level','level','parent_key','key','value','osm_lineage','lineage']
            df_son_vld = df_son_vld.append(pd.DataFrame([[3,'vld',4,'vnfd-connection-point-ref','NULL','NULL','NULL']],
                                      columns = ['parent_level','parent_key','level','key','value','osm_lineage','lineage']))

            df_son_vld.loc[(df_son_vld['level'] == 4) & (df_son_vld['parent_level'] == 3) & (df_son_vld['value'] != 'NULL'),'lineage'] = df_son_vld[(df_son_vld['level'] == 4) & (df_son_vld['parent_level'] == 3) & (df_son_vld['value'] != 'NULL')].apply(
                lambda x: x['osm_lineage'] + x['lineage'].split('|')[-1],axis=1)

            df_son_vld.loc[(df_son_vld['level'] == 5) & (df_son_vld['parent_level'] == 4) & (df_son_vld['value'] != 'NULL'),'osm_lineage'] = df_son_vld[(df_son_vld['level'] == 5) & (df_son_vld['parent_level'] == 4) & (df_son_vld['value'] != 'NULL')].apply(
            lambda x : ('|').join(x['osm_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-1] +'|'+ x['osm_lineage'].split('|')[-2],axis=1 )

            df =df_son_vld[(df_son_vld['level'] == 5) & (df_son_vld['parent_level'] == 4) & (df_son_vld['value'] != 'NULL')].copy()
            df['c'] = df.groupby(['key','osm_lineage']).cumcount()
            df['lineage'] = df.apply(lambda x : x['osm_lineage'] + '|' + str(x['c']),axis=1)
            df_son_vld[(df_son_vld['level'] == 5) & (df_son_vld['parent_level'] == 4) & (df_son_vld['value'] != 'NULL')] = df.copy()

            dataset = dataset.append(df_son_vld)
            dataset=dataset.sort_values(by= 'lineage',ascending=True)
            
            df = map.ret_ds(sonata_dataset,'forwarding_graphs',2)
            fg = map.son_fwdg(df,'value','key',':')
            fg['level'] = fg['level'].astype('int64')
            fg['parent_level'] = fg['parent_level'].astype('int64')
            df_son_vnffgd = pd.merge(fg,osm_son_vnffgd,
                             left_on=['key','parent_key','level','parent_level'],
                             right_on=['son_key','son_parent_key','son_level','son_parent_level'],how='inner')

            df_son_vnffgd =  df_son_vnffgd[['osm_parent_level','osm_level','osm_parent_key','osm_key','value','osm_lineage','lineage']]
            df_son_vnffgd.columns = ['parent_level','level','parent_key','key','value','osm_lineage','lineage']
            df_son_vnffgd = df_son_vnffgd.append(pd.DataFrame([[3,'vnffgd',4,'rsp','NULL','NULL','NULL'],
                                                              [4,'rsp',5,'vnfd-connection-point-ref','NULL','NULL','NULL']],
                                      columns = ['parent_level','parent_key','level','key','value','osm_lineage','lineage']))
           
            df_son_vnffgd.loc[(df_son_vnffgd['level'] == 4) & (df_son_vnffgd['parent_level'] == 3) & (df_son_vnffgd['value'] != 'NULL'),'lineage'] = df_son_vnffgd[(df_son_vnffgd['level'] == 4) & (df_son_vnffgd['parent_level'] == 3) & (df_son_vnffgd['value'] != 'NULL')].apply(
                lambda x: x['osm_lineage'] + x['lineage'].split('|')[-1],axis=1)

            df_son_vnffgd.loc[(df_son_vnffgd['level'] == 5) & (df_son_vnffgd['parent_level'] == 4) & (df_son_vnffgd['value'] != 'NULL'),'lineage'] = df_son_vnffgd[(df_son_vnffgd['level'] == 5) & (df_son_vnffgd['parent_level'] == 4) & (df_son_vnffgd['value'] != 'NULL')].apply(
                lambda x: x['osm_lineage'] + x['lineage'].split('|')[-1],axis=1)

            df_son_vnffgd.loc[(df_son_vnffgd['level'] == 6) & (df_son_vnffgd['parent_level'] == 5) & (df_son_vnffgd['value'] != 'NULL'),'lineage'] = df_son_vnffgd[(df_son_vnffgd['level'] == 6) & (df_son_vnffgd['parent_level'] == 5) & (df_son_vnffgd['value'] != 'NULL')].apply(
                lambda x : ('|').join(x['osm_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-3] +'|'+ x['osm_lineage'].split('|')[-2]+'|'+x['lineage'].split('|')[-1],axis=1 )

            
            dataset = dataset.append(df_son_vnffgd)
            
            dataset.drop('osm_lineage',axis=1,inplace=True)
            
            writer = write_dict()
            message = writer.translate_nsd(dataset)
            
            temp = doc.insert_one(message).inserted_id
            translate_ref = str(temp)
            
            return translate_ref


    def translate_to_sonata(self,received_file):

        record = self.db_mappings.nsd_mapping
    
        if 'nsd:nsd-catalog' in received_file:
        
            doc = self.db_descriptors["translated_nsd"]
            
            osm = received_file
            reader = read_dict()
            
            osm_dataset = pd.DataFrame(reader.dict_parser(osm, 'root', 1, '0|preroot|0'),
                                          columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])

            osm_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
            osm_dataset.fillna('NULL', inplace=True)
            
            res = record.find()
            t = [i for i in res]
            
            if(len(t) ==0):
                insert = insert_into_db(self.client)
                insert.insert_mapping()
                res = record.find()
                t = [i for i in res]     
            
            map= transformation()
           
            osm_sonata = pd.DataFrame.from_dict(t[0])
            osm_son_vld = pd.DataFrame.from_dict(t[1])
            osm_son_vnffgd = pd.DataFrame.from_dict(t[2])
            
            
            dataset=pd.merge(osm_dataset,osm_sonata,
                 left_on=['key','parent_key','level','parent_level'],
                 right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')
            dataset.fillna('NULL',inplace=True)
            dataset = dataset[['son_parent_level','son_level','son_parent_key','son_key','value','lineage','son_lineage']]
            dataset.columns = ['parent_level','level','parent_key','key','value','lineage','son_lineage']
            dataset=dataset.append(pd.DataFrame(
                [['NULL','virtual_links',1,'root',0,'NULL','NULL'],
                ['NULL','network_functions',1,'root',0,'NULL','NULL'],
                ['NULL','forwarding_graphs',1,'root',0,'NULL','NULL'],
                ['NULL','connection_points',1,'root',0,'NULL','NULL'],
                ['https://raw.githubusercontent.com/sonata-nfv/tng-schema/master/service-descriptor/nsd-schema.yml','description_schema',1,'root',0,'0|preroot|0','0|preroot|']],
               columns = ['value','key','level','parent_key','parent_level','lineage','son_lineage']))

            dataset.loc[dataset['value'] != 'NULL','lineage'] = dataset.loc[dataset['value'] != 'NULL'].apply(
                lambda x: ('|').join(x['son_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-3] +'|'+ x['son_lineage'].split('|')[-2]+'|'+x['lineage'].split('|')[-1],axis=1)

            
            dataset=dataset.sort_values(by= ['lineage','parent_key'],ascending=True)

            
            df = map.ret_ds(osm_dataset,'vld',4)
            vl = map.osm_vld(df)
            vl['level'] = vl['level'].astype('int64')
            vl['parent_level'] = vl['parent_level'].astype('int64')

            df_osm_vld = pd.merge(vl,osm_son_vld,
                             left_on=['key','parent_key','level','parent_level'],
                             right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')

            df_osm_vld =  df_osm_vld[['son_parent_level','son_level','son_parent_key','son_key','value','lineage','son_lineage']]
            df_osm_vld.columns = ['parent_level','level','parent_key','key','value','lineage','son_lineage']

            df_osm_vld.loc[(df_osm_vld['level'] == 2) & (df_osm_vld['parent_level'] == 1) & (df_osm_vld['value'] != 'NULL'),'lineage'] = df_osm_vld[(df_osm_vld['level'] == 2) & (df_osm_vld['parent_level'] == 1) & (df_osm_vld['value'] != 'NULL')].apply(
                lambda x: ('|').join(x['son_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-3] +'|'+ x['son_lineage'].split('|')[-2]+'|'+x['lineage'].split('|')[-1],axis=1)

            dataset= dataset.append(df_osm_vld)
            
            dataset=dataset.sort_values(by= ['lineage','parent_key'],ascending=True)

            df = map.ret_ds(osm_dataset,'vnffgd',4)

            if not df.empty:
                fg= map.osm_fwdg(df)
                fg['level'] = fg['level'].astype('int64')
                fg['parent_level'] = fg['parent_level'].astype('int64')

                df_osm_vnffgd = pd.merge(fg,osm_son_vnffgd,
                                 left_on=['key','parent_key','level','parent_level'],
                                 right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')

                df_osm_vnffgd =  df_osm_vnffgd[['son_parent_level','son_level','son_parent_key','son_key','value','lineage','son_lineage']]
                df_osm_vnffgd.columns = ['parent_level','level','parent_key','key','value','lineage','son_lineage']
                df_osm_vnffgd = df_osm_vnffgd.append(pd.DataFrame(
                    [[2,'network_forwarding_paths',3,'connection_points','NULL','NULL','NULL'],
                     [1,'forwarding_graphs',2,'network_forwarding_paths','NULL','NULL','NULL']],
                                           columns = ['parent_level','parent_key','level','key','value','lineage','son_lineage']))

                df_osm_vnffgd.loc[(df_osm_vnffgd['level'] == 2) & (df_osm_vnffgd['parent_level'] == 1) & (df_osm_vnffgd['value'] != 'NULL'),'lineage'] = df_osm_vnffgd[(df_osm_vnffgd['level'] == 2) & (df_osm_vnffgd['parent_level'] == 1) & (df_osm_vnffgd['value'] != 'NULL')].apply(
                lambda x: ('|').join(x['son_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-3] +'|'+ x['son_lineage'].split('|')[-2]+'|'+x['lineage'].split('|')[-1],axis=1)

                df_osm_vnffgd.loc[(df_osm_vnffgd['level'] == 3) & (df_osm_vnffgd['parent_level'] == 2) & (df_osm_vnffgd['value'] != 'NULL'),'lineage'] = df_osm_vnffgd[(df_osm_vnffgd['level'] == 3) & (df_osm_vnffgd['parent_level'] == 2) & (df_osm_vnffgd['value'] != 'NULL')].apply(
                lambda x: ('|').join(x['son_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-3] +'|'+ x['son_lineage'].split('|')[-2]+'|'+x['lineage'].split('|')[-1],axis=1)

                df_osm_vnffgd.loc[(df_osm_vnffgd['level'] == 4) & (df_osm_vnffgd['parent_level'] == 3) & (df_osm_vnffgd['value'] != 'NULL'),'son_lineage'] = df_osm_vnffgd[(df_osm_vnffgd['level'] == 4) & (df_osm_vnffgd['parent_level'] == 3) & (df_osm_vnffgd['value'] != 'NULL')].apply(
                lambda x: ('|').join(x['son_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-3] +'|'+ x['son_lineage'].split('|')[-2],axis=1)

                df =df_osm_vnffgd[(df_osm_vnffgd['level'] == 4) & (df_osm_vnffgd['parent_level'] == 3) & (df_osm_vnffgd['value'] != 'NULL')].copy()
                df['c'] = df.groupby(['key','son_lineage']).cumcount()
                df['lineage'] = df.apply(lambda x : x['son_lineage'] + '|' + str(x['c']),axis=1)
                df_osm_vnffgd.loc[(df_osm_vnffgd['level'] == 4) & (df_osm_vnffgd['parent_level'] == 3) & (df_osm_vnffgd['value'] != 'NULL')] = df.copy()

                dataset = dataset.append(df_osm_vnffgd)

                vl_val = dataset[(dataset['parent_key'] == 'virtual_links') & 
                        (dataset['key'] == 'id')].groupby(['key']).agg(
                    {'value' : lambda x : list(x)})['value'][0]

                nf_val = dataset[(dataset['parent_key'] == 'network_functions') & 
                        (dataset['key'] == 'vnf_id')].groupby(['key']).agg({'value' : lambda x : list(x)})['value'][0]

                dataset = dataset.append(pd.DataFrame([[1,'forwarding_graphs',2,'constituent_virtual_links',vl_val,'0|preroot|0|root|0','0|preroot|0|root|'],
                                                       [1,'forwarding_graphs',2,'constituent_vnfs',nf_val,'0|preroot|0|root|0','0|preroot|0|root|'],
                                                        [1,'forwarding_graphs',2,'number_of_virtual_links',len(vl_val),'0|preroot|0|root|0','0|preroot|0|root|'],
                                            ],
                                           columns = ['parent_level','parent_key','level','key','value','lineage','son_lineage']))
                
               
                dataset.drop('son_lineage',inplace=True,axis=1)
                
                dataset=dataset.sort_values(by= ['lineage','parent_key'],ascending=True)
            
            writer = write_dict()
            message = writer.translate_nsd(dataset)
            message = message['preroot']["root"][0]
            
            temp = doc.insert_one(message).inserted_id
            translated_ref = str(temp)
            
            return translated_ref
            
        elif 'osm' and 'management interface' in received_file:
        
            doc = self.db_descriptors["translated_nsd"]
            
            temp = doc.insert_one(translated)
            translated_ref = temp.inserted_id
            
            return translated_ref

class insert_into_db():
    
    def __init__(self, client = None):
        
        self.client = client
        self.db_mappings = self.client.mapping
        self.db_descriptors = self.client.descriptors
        
    def insert_mapping(self):
        '''
            creates 3 mongoDB documents to store the mapping Virtual Functions , Forwarding Graphs and the rest parameters

            Params
            ------
            record: pymongo.collection.Collection
                cursor to the MongoDb collection where mappings are stored

        '''
        osm_sonata_nsd_mapping= [
                ['0|preroot|0|root|0|nsd:nsd-catalog|',2,3,'nsd','description','0|preroot|',0,1,'root','description'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|',2,3,'nsd','vendor','0|preroot|',0,1,'root','vendor'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|',2,3,'nsd','name','0|preroot|',0,1,'root','name'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|',2,3,'nsd','version','0|preroot|',0,1,'root','version'],


                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'constituent-vnfd','member-vnf-index','0|preroot|0|root|',1,2,'network_functions','vnf_id'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'constituent-vnfd','vnfd-id-ref','0|preroot|0|root|',1,2,'network_functions','vnf_name'],


                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'connection-point','name','0|preroot|0|root|',1,2,'connection_points','id'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'connection-point','type','0|preroot|0|root|',1,2,'connection_points','type'],


                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'monitoring-param','description','0|preroot|0|root|',1,2,'monitoring_parameters','description'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'monitoring-param','units','0|preroot|0|root|',1,2,'monitoring_parameters','unit'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'monitoring-param','value-integer','0|preroot|0|root|',1,2,'monitoring_parameters','metric'],

                    ]

        osm_sonata_vld_mapping= [

                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'vld','id','0|preroot|0|root|',1,2,'virtual_links','id'],
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'vld','type','0|preroot|0|root|',1,2,'virtual_links','connectivity_type'],
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'virtual_links','connection_points_reference','0|preroot|0|root|',1,2,'virtual_links','connection_points_reference'],  
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|0|vld|',4,5,'vnfd-connection-point-ref','member-vnf-index-ref','0|preroot|0|root|',1,2,'virtual_links','member-vnf-index-ref'],
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|0|vld|',4,5,'vnfd-connection-point-ref','vnfd-connection-point-ref','0|preroot|0|root|',1,2,'virtual_links','vnfd-connection-point-ref'],

                    ]


        osm_sonata_vnffgd_mapping= [

                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'vnffgd','id','0|preroot|0|root|',1,2,'forwarding_graphs','fg_id'],
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|0|vnffgd|0|rsp|',5,6,'vnfd-connection-point-ref','member-vnf-index-ref','0|preroot|0|root|0|forwarding_graphs|0|network_forwarding_paths|',3,4,'connection_points','member-vnf-index-ref'],
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|0|vnffgd|0|rsp|',5,6,'vnfd-connection-point-ref','vnfd-connection-point-ref','0|preroot|0|root|0|forwarding_graphs|0|network_forwarding_paths|',3,4,'connection_points','vnfd-connection-point-ref'],
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|0|vnffgd|0|rsp|',5,6,'vnfd-connection-point-ref','order','0|preroot|0|root|0|forwarding_graphs|0|network_forwarding_paths|',3,4,'connection_points','position'],
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|0|vnffgd|0|rsp|',5,6,'connection_points','connection_point_ref','0|preroot|0|root|0|forwarding_graphs|0|network_forwarding_paths|',3,4,'connection_points','connection_point_ref'],
                        ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|0|vnffgd|',4,5,'rsp','id','0|preroot|0|root|0|forwarding_graphs|',2,3,'network_forwarding_paths','fp_id'],

                    ]
        osm_sonata = pd.DataFrame(osm_sonata_nsd_mapping,
                                  columns=["osm_lineage","osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_lineage","son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_vld=pd.DataFrame(osm_sonata_vld_mapping , 
             columns=["osm_lineage","osm_parent_level","osm_level","osm_parent_key","osm_key",
                      "son_lineage","son_parent_level","son_level","son_parent_key","son_key"]).sort_values(by=['son_level','osm_level'],ascending=True)


        osm_son_vnffgd=pd.DataFrame(osm_sonata_vnffgd_mapping , 
                     columns=["osm_lineage","osm_parent_level","osm_level","osm_parent_key","osm_key",
                              "son_lineage","son_parent_level","son_level","son_parent_key","son_key"]).sort_values(by=['son_level','osm_level'],ascending=True)

        osm_sonata.index = [str(i) for i in osm_sonata.index]
        osm_son_vld.index = [str(i) for i in osm_son_vld.index]
        osm_son_vnffgd.index = [str(i) for i in osm_son_vnffgd.index]
        
        
        record = self.db_mappings.nsd_mapping
        
        temp = json.loads(osm_sonata.to_json())
        id = record.insert_one(temp).inserted_id
        
        temp = json.loads(osm_son_vld.to_json())
        id = record.insert_one(temp).inserted_id
        
        temp = json.loads(osm_son_vnffgd.to_json())
        id = record.insert_one(temp).inserted_id


    def insert_nsd(self,framework):
        
        if framework == 'osm':
            nsd=yaml.load(open(r"hackfest_multivdu_nsd.yaml"))
        
        elif framework == 'sonata':
            nsd=yaml.load(open(r"sonata-demo.yml"), Loader=yaml.Loader)
        
        record = self.db_descriptors.source_nsd
        
        id = record.insert_one(nsd).inserted_id
        
        return id
    
class transformation():

    def sub_ds(self,df,parent,level) :   
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
        new_df = pd.DataFrame(columns=['parent_level','parent_key','level','key','value','lineage'])
       
        for index, row in df[(df['parent_key']==parent) & (df['level'] == level)].iterrows():
            
            new_df = new_df.append(row)
            
        return new_df

    def search_sub_ds(self,df,parent,level):
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
        
        if len(df[(df['parent_key'] == parent) & (df['level'] == level) & (df['value'] == 'NULL')]['key'].values) > 0:
            return df[(df['parent_key'] == parent) & (df['level'] == level) & (df['value'] == 'NULL')]['key'].values
        
        else:
            return []
        
    def ds_loop(self,ds,parent,level):  
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
        yield self.sub_ds(ds,parent,level)
        
        if len(self.search_sub_ds(ds,parent,level)) > 0:
            for k in np.unique(self.search_sub_ds(ds,parent,level)):
                for item in self.ds_loop(ds,k,level+1):
                    yield item
                    
    def ret_ds(self,ds,key,level):
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
        temp=list(self.ds_loop(ds,key,level))
        temp_ds=pd.DataFrame(columns=['parent_level','parent_key','level','key','value','lineage'])
        
        for i in range(len(temp)):
            temp_ds = pd.concat([temp_ds,temp[i]],axis=0)
            
        return temp_ds

    def osm_fwdg(self,df):
        
        temp = df[df['parent_key'].isin(['vnfd-connection-point-ref','classifier']) & 
           df['key'].isin(['vnfd-connection-point-ref','member-vnf-index-ref'])].groupby(
           ['parent_level','parent_key','level','lineage'])['value'].apply(
           lambda x : ':'.join(x.astype(str)) ).reset_index()
    
        temp = temp.assign(**{'key':'connection_point_ref', 
                              'parent_key': 'connection_points',
                              'level':6, 
                              'parent_level': 5
                             })
        
        temp2 = temp.copy()

        temp2['value'] = temp2.index 
        temp2['key'] = 'order'
        temp2['parent_key'] = 'vnfd-connection-point-ref'
        temp = temp.append(temp2)
        
        df = df.drop(df[df['parent_key'].isin(['vnfd-connection-point-ref','classifier']) & 
           df['key'].isin(['vnfd-connection-point-ref','order','member-vnf-index-ref'])].index,axis=0)
        
        return df.append(temp)


    def osm_vld(self,df):
        
        temp = df[df['parent_key'].isin(['vnfd-connection-point-ref']) & 
               df['key'].isin(['vnfd-connection-point-ref','member-vnf-index-ref'])].groupby(
                   ['parent_key','parent_level','level','lineage']).agg(
            {'value':lambda x : ':'.join(x.values.astype('str')) }).reset_index()

        temp['lineage'] = temp.apply(lambda x : '|'.join(x['lineage'].split('|')[:-2]),axis=1 )
        
        temp = temp.groupby(['parent_key','parent_level','level','lineage']).agg(
            {'value': lambda x :[' , '.join(x.values.astype('str'))] }).reset_index()

        temp = temp.groupby(['parent_key','parent_level','level','lineage']).agg(
            {'value': lambda x : x.values[0][0].split(' , ') }).reset_index()
        
        temp = temp.assign(**{'key':'connection_points_reference', 
                                  'parent_key': 'virtual_links',
                                  'level':4, 
                                  'parent_level': 3
                                 }) 

        df = df.drop(df[df['parent_key'].isin(['vnfd-connection-point-ref']) & 
               df['key'].isin(['vnfd-connection-point-ref','vnfd-id-ref','member-vnf-index-ref'])].index,axis=0)
        
        return df.append(temp) 



    def son_fwdg(self,df, column1='value',column2='key', sep=':'):
        '''
        Split the values of a column and expand so the new DataFrame has one split
        value per row. Filters rows where the column is missing.

        Params
        ------
        df : pandas.DataFrame
            dataframe with the column to split and expand
        column : str
            the column to split and expand
        sep : str
            the string used to split the column's values
        keep : bool
            whether to retain the presplit value as it's own row

        Returns
        -------
        pandas.DataFrame
            Returns a dataframe with the same columns as `df`.
        '''
        indexes = []
        new_values = []
        new_values2 = []
        df = df.dropna(subset=[column1])
        
        for i, presplit in enumerate(df[[column1,column2]].itertuples()):
            values = str(presplit[1]).split(sep)
            
            for j in range(len(values)):
                indexes.append(i)
                new_values.append(values[j])
                
                if len(values) > 1:
                    if (j == 0 and str(presplit[2]) == 'connection_point_ref'):
                        new_values2.append('member-vnf-index-ref')
                    elif (j > 0 and str(presplit[2]) == 'connection_point_ref') :
                        new_values2.append('vnfd-connection-point-ref')
                    elif (j == 0 and str(presplit[2]) == 'fp_id'):
                        new_values2.append('fg_id')
                    elif (j > 0 and str(presplit[2]) == 'fp_id'):
                        new_values2.append('fp_id')
                        
                else:
                    if str(presplit[2]) == 'connection_point_ref':
                        new_values2.append('vnfd-connection-point-ref')
                        
                    else:
                        new_values2.append(str(presplit[2]))
        
        new_df = df.iloc[indexes, :].copy()
        new_df[column1] = new_values
        new_df[column2] = new_values2
        
        return new_df



    def son_vld(self,df,column1='value',column2='key', sep=':'):
        '''
        Split the values of a column and expand so the new DataFrame has one split
        value per row. Filters rows where the column is missing.

        Params
        ------
        df : pandas.DataFrame
            dataframe with the column to split and expand
        column : str
            the column to split and expand
        sep : str
            the string used to split the column's values
        keep : bool
            whether to retain the presplit value as it's own row

        Returns
        -------
        pandas.DataFrame
            Returns a dataframe with the same columns as `df`.
        '''
        indexes = []
        new_values = []
        new_values2 = []
        df = df.dropna(subset=[column1])
        
        for i, presplit in enumerate(df[[column1,column2]].itertuples()):

            if(isinstance(presplit[1],list)):
                for item in presplit[1]:
                    values = str(item).split(sep) 
                    
                    for j in range(len(values)):
                        indexes.append(i)
                        new_values.append(values[j])
                        if len(values) > 1:
                            if j == 0:
                                new_values2.append('member-vnf-index-ref')
                            elif j > 0:
                                new_values2.append('vnfd-connection-point-ref')
                        else:
                            new_values2.append('vnfd-connection-point-ref')
                            
            else:
                indexes.append(i)
                new_values.append(presplit[1])
                new_values2.append(presplit[2])
                
        new_df = df.iloc[indexes, :].copy()
        new_df[column1] = new_values
        new_df[column2] = new_values2
        
        return new_df


