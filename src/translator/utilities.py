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

    def translate_to_osm_vnfd(self,received_file):
        '''
        reads a dictionary and is converted to a DataFrame with columns containing :
        enumerated 'parent level', enumerated 'level', 'parent key', 'key', 
        'value' and complete 'lineage'. 
        Since the input dict contains further nested dict as well, storing 
        the level information and the complete lineage helps in selecting out 
        particular key-value pair and transforming it for osm to sonata values
        and vice-versa.
        
        Params
        ------
        received_file : dict
            dictionary containing the full set of sonata vnf descriptor
        
        Returns
        -------
        message : dict
            returns a translated osm vnf descriptor dictionary
            
        '''                
        
        sonata = received_file

        ### reading a dict/ json content into a pandas dataframe
        reader = read_dict()
        sonata_dataset = pd.DataFrame(reader.dict_parser(sonata, 'root', 1, '0|preroot|0'), 
                                          columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])
        sonata_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
        sonata_dataset.fillna('NULL', inplace=True)

        
        ### retrieving the vnfd mappings from DB
        record = self.db_mappings.vnfd_mapping
        res = record.find()

        t = [i for i in res]
        
        ### if the mapping is not found then insert them
        if(len(t) ==0):
            insert = insert_into_db(self.client)
            insert.insert_vnfd_mapping()
            res = record.find()
            t = [i for i in res]


        transformation_obj= transformation()

        mapping_vnfd = pd.DataFrame.from_dict(t[0]) ## mapping for only the 1st level keys 
        osm_son_vl = pd.DataFrame.from_dict(t[1])   ## mapping for only virtual links
        osm_son_cp = pd.DataFrame.from_dict(t[2])   ## mapping for only connection points
        osm_son_vdu = pd.DataFrame.from_dict(t[3])  ## mapping for only vdu
        osm_son_vdu_ext = pd.DataFrame.from_dict(t[4]) ## mapping for only external cps in vdu


        ### joining/ merging the 1st level vnfd mapping with the input sonata file to get the corresponding osm values
        
        dataset = pd.merge(sonata_dataset, mapping_vnfd,
                           left_on=['key', 'parent_key', 'level', 'parent_level'],
                           right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
        dataset.fillna('NULL', inplace=True)
        dataset = dataset[
            ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
        dataset.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']

        dataset=dataset.append(pd.DataFrame([
            ['NULL',0, 1, 'root', 'vnfd:vnfd-catalog','NULL','NULL'],
            ['NULL',1, 2, 'vnfd:vnfd-catalog', 'vnfd','NULL','NULL'],
            ['NULL',2, 3, 'vnfd', 'internal-vld','NULL','NULL'],
            ['NULL',2, 3, 'vnfd', 'connection-point', 'NULL','NULL'],
            ['NULL',2, 3, 'vnfd', 'vdu', 'NULL','NULL'],
            ['NULL',2, 3, 'vnfd', 'monitoring-param','NULL','NULL']
        ],
             columns = ['osm_lineage','parent_level','level','parent_key','key','lineage','value']))

        dataset['lineage'] = dataset.apply(lambda x : x['osm_lineage'] + x['lineage'].split('|')[-1] 
                                                      if x['lineage'] !='NULL' else 'NULL',axis=1)
        temp = dataset[(dataset['key'] == 'name') & 
                       (dataset['parent_key'] == 'vnfd')].copy()
        temp['key'] = 'id'
        dataset = dataset.append(temp)

        dataset.sort_values(by=['parent_level','parent_key','lineage','key','level'],
                                ascending=[True,True,True,True,True],inplace=True)
        dataset.reset_index(inplace=True,drop=True)


        ### translating and transforming the sonata connection points to osm
        
        df_cp = transformation_obj.ret_ds(sonata_dataset, 'connection_points', 2)
        df_cp['level'] = df_cp['level'].astype('int64')
        df_cp['parent_level'] = df_cp['parent_level'].astype('int64')
        
        df_son_cp = pd.merge(df_cp, osm_son_cp,
                             left_on=['key', 'parent_key', 'level', 'parent_level'],
                             right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')

        df_son_cp = df_son_cp[
            ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
        df_son_cp.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']
        df_son_cp['lineage'] = df_son_cp.apply(lambda x: x['osm_lineage'] + x['lineage'].split('|')[-1] if x['lineage'] !='NULL' else 'NULL', axis=1)

        temp = df_son_cp[(df_son_cp['key'] == 'id') & 
                                (df_son_cp['parent_key'] == 'connection-point')].copy()
        temp['key'] = 'name'
        df_son_cp = df_son_cp.append(temp)

        df_son_cp.sort_values(['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,True,True],inplace=True)
        df_son_cp.loc[df_son_cp[(df_son_cp['key'] == 'type') & 
                                (df_son_cp['parent_key'] == 'connection-point')].index,'value'] = df_son_cp[(df_son_cp['key'] == 'type') & 
                                                                                                            (df_son_cp['parent_key'] == 'connection-point')].apply(lambda x : 'VPORT' if x.value in ['management','internal','external'] else 'NULL',axis=1 )

        dataset = dataset.append(df_son_cp)

        
        
        if 'mgmt' in dataset[(dataset['parent_key']=='connection-point') & (dataset['key']=='name')]['value'].tolist():
        
            dataset= dataset.append(pd.DataFrame([
                        ['NULL',2, 3, 'vnfd', 'mgmt-interface','NULL','NULL'],
                        ['NULL',3, 4, 'mgmt-interface', 'cp','0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0','mgmt']],
                          columns = ['osm_lineage','parent_level','level','parent_key','key','lineage','value']))

        elif len(dataset[(dataset['parent_key']=='connection-point') & (dataset['key']=='name')]['value'].tolist()) ==1:
        
            mgmt_cp=dataset[(dataset['parent_key']=='connection-point') & (dataset['key']=='name')]['value'].tolist()[0]
            dataset= dataset.append(pd.DataFrame([
                        ['NULL',2, 3, 'vnfd', 'mgmt-interface','NULL','NULL'],
                        ['NULL',3, 4, 'mgmt-interface', 'cp','0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0',str(mgmt_cp)]],
                          columns = ['osm_lineage','parent_level','level','parent_key','key','lineage','value']))
        
        
        
        ### translating and transforming the sonata vdu keys to osm
        df_vdu = transformation_obj.ret_ds(sonata_dataset, 'virtual_deployment_units', 2)
        df_vdu['level'] = df_vdu['level'].astype('int64')
        df_vdu['parent_level'] = df_vdu['parent_level'].astype('int64')
        df_vdu['value'] = df_vdu['value'].astype('object')

        if(len(df_vdu[(df_vdu['key']=='id') & ( df_vdu['parent_key'] == 'virtual_deployment_units')]) == 1):
      
            df_vdu.drop(df_vdu[( df_vdu['parent_key'] == 'connection_points')].index,inplace=True,axis=0)


        df_son_vdu = pd.merge(df_vdu, osm_son_vdu,
                              left_on=['key', 'parent_key', 'level', 'parent_level'],
                              right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
        df_son_vdu.sort_values(['osm_level'], inplace=True)
        df_son_vdu = df_son_vdu[
            ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
        df_son_vdu.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']

        df_son_vdu=df_son_vdu.append(pd.DataFrame([
        ['NULL',3, 4, 'vdu', 'vm-flavor','NULL','NULL'],
        ['NULL',3, 4, 'vdu', 'internal-connection-point','NULL','NULL'],
        ['NULL',3, 4, 'vdu', 'interface','NULL','NULL']],
                                           columns = ['osm_lineage','parent_level','level','parent_key','key','lineage','value']))


        df_son_vdu.loc[(df_son_vdu['level'] == 4) & 
                       (df_son_vdu['parent_level'] == 3), 'lineage'] = df_son_vdu[(df_son_vdu['level'] == 4) & 
                                                                                  (df_son_vdu['parent_level'] == 3)].apply(lambda x: 
                                                                                    x['osm_lineage'] + x['lineage'].split('|')[-1] if x['lineage'] !='NULL' else 'NULL', axis=1)
        df_son_vdu.loc[(df_son_vdu['level'] == 5) & 
                       (df_son_vdu['parent_level'] == 4), 'lineage'] = df_son_vdu[(df_son_vdu['level'] == 5) & 
                                                                                  (df_son_vdu['parent_level'] == 4)].apply(lambda x: 
                                                                                    ('|').join(x['osm_lineage'].split('|')[:8])+'|' +x['lineage'].split('|')[4] +'|'+ x['osm_lineage'].split('|')[9]+'|'+x['lineage'].split('|')[-1] if x['lineage'] !='NULL' else 'NULL', axis=1)

        df_son_vdu.loc[(df_son_vdu['level']==5) & 
                       (df_son_vdu['key'] == 'storage-gb') & 
                       (df_son_vdu['value'].isin(['GB','MB','TB','KB'])),'value'] = df_son_vdu[(df_son_vdu['level']==5) & 
                       (df_son_vdu['key'] == 'storage-gb') & 
                       (df_son_vdu['value'].isin(['GB','MB','TB','KB']))]['value'].apply(
                        lambda x : 1 if x == 'GB' else (1/1024.0 if x == 'MB' else (1/(1024.0*1024.0) if x== 'KB' else 0))) 


        df_son_vdu.loc[(df_son_vdu['level']==5) & 
                       (df_son_vdu['key'] == 'memory-mb') & 
                       (df_son_vdu['value'].isin(['GB','MB','TB','KB'])),'value'] = df_son_vdu[(df_son_vdu['level']==5) & 
                       (df_son_vdu['key'] == 'memory-mb') & 
                       (df_son_vdu['value'].isin(['GB','MB','TB','KB']))]['value'].apply(
                        lambda x : 1 if x == 'MB' else (1024 if x == 'GB' else (1024*1024 if x== 'KB' else 0))) 

        temp = df_son_vdu[(df_son_vdu['level']==5) & 
                       (df_son_vdu['key'].isin(['memory-mb','storage-gb']))].groupby(['lineage','key'])['value'].apply(
                            lambda x : np.prod(x)).reset_index()

        temp = temp.assign(**{
                      'osm_lineage' : '0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',
                      'parent_key': 'vm-flavor',
                      'level': 5, 
                      'parent_level': 4
                     })

        df_son_vdu.drop(df_son_vdu[(df_son_vdu['level']==5) & 
                       (df_son_vdu['key'].isin(['memory-mb','storage-gb']))].index,inplace =True, axis=0)

        df_son_vdu=df_son_vdu.append(temp)
        df_son_vdu.sort_values(by=['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,True,True],inplace=True)

        if 'internal-connection-point' in df_son_vdu['parent_key'].values:
            df_son_vdu.loc[df_son_vdu[(df_son_vdu['key'] == 'type') & 
                                (df_son_vdu['parent_key'] == 'internal-connection-point')].index,'value'] = df_son_vdu[(df_son_vdu['key'] == 'type') & 
                                                                                                            (df_son_vdu['parent_key'] == 'internal-connection-point')].apply(
                lambda x : 'VPORT' if x.value in ['management','internal','external'] else 'NULL',axis=1 )

            df_son_vdu.drop(df_son_vdu[df_son_vdu['parent_key'] == 'interface'].index,inplace=True,axis=0)
            
        else:
            df_son_vdu.loc[df_son_vdu[(df_son_vdu['key'] == 'name') & 
                                (df_son_vdu['parent_key'] == 'interface')].index,'key'] = 'id'
            df_son_vdu.loc[df_son_vdu[(df_son_vdu['key'] == 'type') & 
                                (df_son_vdu['parent_key'] == 'interface')].index,'value'] = df_son_vdu[(df_son_vdu['key'] == 'type') & 
                                                                                                            (df_son_vdu['parent_key'] == 'interface')].apply(
                lambda x : 'VPORT' if x.value in ['management','internal','external'] else 'NULL',axis=1 )   
            
        dataset = dataset.append(df_son_vdu)

        dataset.drop('osm_lineage',inplace=True,axis=1)

        ### translating and transforming the sonata virtual links keys to osm
        df_vl = transformation_obj.ret_ds(sonata_dataset, 'virtual_links', 2)
        df_vl['level'] = df_vl['level'].astype('int64')
        df_vl['parent_level'] = df_vl['parent_level'].astype('int64')
        df_vl['value'] = df_vl['value'].astype('object')
        df_son_vdu_int_ext = pd.merge(df_vl, osm_son_vdu_ext,
                             left_on=['key', 'parent_key', 'level', 'parent_level'],
                             right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
        df_son_vdu_int_ext.sort_values(['osm_level'], inplace=True)
        df_son_vdu_int_ext = df_son_vdu_int_ext[
            ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
        df_son_vdu_int_ext.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']


        df_son_vdu_int_ext = transformation_obj.son_vld_int_ext_vnfd(df_son_vdu_int_ext)

        if (len(df_son_vdu_int_ext) >0): 
            
            df_son_vdu_int_ext['temp'] = df_son_vdu_int_ext.apply(lambda x: x.value.split(':')[0] if 1==1 else 'NULL',axis=1)
            df_son_vdu_int_ext['value'] = df_son_vdu_int_ext.apply(lambda x: x.value.split(':')[-1] if 1==1 else 'NULL',axis=1)
            df_son_vdu_int_ext['temp'] = df_son_vdu_int_ext['temp'].astype('category').cat.codes

            df_son_vdu_int_ext.loc[(df_son_vdu_int_ext['parent_level'] ==4) & 
                                   (df_son_vdu_int_ext['level']==5),'lineage'] = df_son_vdu_int_ext[(df_son_vdu_int_ext['parent_level'] ==4) & 
                                   (df_son_vdu_int_ext['level']==5)].apply(lambda x : '|'.join(x['osm_lineage'].split('|')[:-3])+
                                                                 '|'+str(x['temp'])+
                                                                 '|'+x['osm_lineage'].split('|')[-2]+
                                                                 '|'+x['lineage'].split('|')[-1],axis=1)

            df_son_vdu_int_ext.loc[(df_son_vdu_int_ext['parent_level'] ==5) & 
                                   (df_son_vdu_int_ext['level']==6),'lineage'] = df_son_vdu_int_ext[(df_son_vdu_int_ext['parent_level'] ==5) & 
                                   (df_son_vdu_int_ext['level']==6)].apply(lambda x : '|'.join(x['osm_lineage'].split('|')[:-5])+
                                                                 '|'+str(x['temp'])+
                                                                 '|'+x['osm_lineage'].split('|')[-4]+
                                                                 '|'+x['lineage'].split('|')[-1]+ '|'+
                                                                ('|').join(x['osm_lineage'].split('|')[-2:]),axis=1)

            df_son_vdu_int_ext['osm_lineage']= df_son_vdu_int_ext['lineage'].apply(lambda x : '|'.join(x.split('|')[:9]))
            df_son_vdu_int_ext.reset_index(drop=True,inplace=True)
            interface_lineage= df_son_vdu_int_ext.groupby('osm_lineage')['lineage'].apply(
                lambda x : pd.Categorical([val.split('|')[10] for val in x.values]).codes).reset_index()
            for row in interface_lineage.itertuples():
                df_son_vdu_int_ext.loc[df_son_vdu_int_ext[df_son_vdu_int_ext['osm_lineage'] == row[1]].index,'temp'] = np.array(row[2])

            df_son_vdu_int_ext.loc[(df_son_vdu_int_ext['parent_level'] ==4) & 
                                   (df_son_vdu_int_ext['level']==5),'lineage']= df_son_vdu_int_ext[(df_son_vdu_int_ext['parent_level'] ==4) & 
                                   (df_son_vdu_int_ext['level']==5)].apply(
                lambda x : '|'.join(x['lineage'].split('|')[:10]) + '|' + str(x.temp),axis=1)


            df_son_vdu_int_ext.loc[(df_son_vdu_int_ext['parent_level'] ==5) & 
                                   (df_son_vdu_int_ext['level']==6),'lineage']= df_son_vdu_int_ext[(df_son_vdu_int_ext['parent_level'] ==5) & 
                                   (df_son_vdu_int_ext['level']==6)].apply(
                lambda x : '|'.join(x['lineage'].split('|')[:10]) + '|' + str(x.temp) + '|'+'|'.join(x['lineage'].split('|')[11:]),axis=1)

            df_son_vdu_int_ext.drop(['temp','osm_lineage'],axis=1,inplace=True)
            df_son_vdu_int_ext.sort_values(by=['parent_level','parent_key','lineage','key','level'],
                                           ascending=[True,True,True,False,True],inplace=True)
            df_son_vdu_int_ext.reset_index(drop=True,inplace=True)
            df_son_vdu_int_ext=df_son_vdu_int_ext.append(pd.DataFrame([
            [4, 5, 'interface', 'virtual-interface','NULL','NULL']],
                                               columns = ['parent_level','level','parent_key','key','lineage','value']))

            dataset=dataset.append(df_son_vdu_int_ext)
            
        if (len(dataset[(dataset['key'] == 'id') & (dataset['parent_key'] == 'internal-connection-point')]) > 0 ):
            
            df_vl = transformation_obj.ret_ds(sonata_dataset, 'virtual_links', 2)
            df_vl['level'] = df_vl['level'].astype('int64')
            df_vl['parent_level'] = df_vl['parent_level'].astype('int64')
            df_vl['value'] = df_vl['value'].astype('object')

            index = []
            for i,row in enumerate(df_vl[['value']].itertuples()):
                if len(row[1][0].split(':')) ==2 & len(row[1][1].split(':')) ==2:
                    index.append(row[0])

            df_vl=df_vl[df_vl['lineage'].isin(df_vl.loc[index,'lineage'].values)]

            df_son_vl = pd.merge(df_vl, osm_son_vl,
                                 left_on=['key', 'parent_key', 'level', 'parent_level'],
                                 right_on=['son_key', 'son_parent_key', 'son_level', 'son_parent_level'], how='inner')
            df_son_vl.sort_values(['osm_level'], inplace=True)
            df_son_vl = df_son_vl[
                ['osm_parent_level', 'osm_level', 'osm_parent_key', 'osm_key', 'value', 'osm_lineage', 'lineage']]
            df_son_vl.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'osm_lineage', 'lineage']

            df_son_vl = df_son_vl.append(pd.DataFrame([
            ['NULL',3, 4, 'internal-vld', 'internal-connection-point','NULL','NULL']],
                                               columns = ['osm_lineage','parent_level','level','parent_key','key','lineage','value']))


            df_son_vl['temp'] = df_son_vl[df_son_vl['lineage'] != 'NULL']['lineage'].astype('category').cat.codes
            df_son_vl.loc[df_son_vl['lineage'] != 'NULL', 'lineage'] = df_son_vl[df_son_vl['lineage'] != 'NULL'].apply(lambda x : '|'.join(x['lineage'].split('|')[:-1]) + '|' + str(x.temp),axis=1)

            df_son_vl.loc[(df_son_vl['level'] != 5), 'lineage'] = df_son_vl[(df_son_vl['level'] != 5)].apply(
                lambda x: x['osm_lineage'] + x['lineage'].split('|')[-1] if x['lineage'] !='NULL' else 'NULL', axis=1)
            df_son_vl.loc[(df_son_vl['level'] == 5) & (df_son_vl['parent_key'] == 'internal-connection-point'),
                          'lineage'] = df_son_vl[(df_son_vl['level'] == 5) & (df_son_vl['parent_key'] == 'internal-connection-point')].apply(
                                               lambda x: ('|').join(x['osm_lineage'].split('|')[:-3])+'|'+ 
                                                         x['lineage'].split('|')[-1]+'|'+x['osm_lineage'].split('|')[-2]+'|'+'0' 
                                                         if x['lineage'] !='NULL' else 'NULL', axis=1)


            df_son_vl= transformation_obj.son_vld_vnfd(df_son_vl)
            df_son_vl.sort_values(by=['parent_level','parent_key','lineage','key','level'],
                                  ascending=[True,True,True,True,True],inplace=True)
            df_son_vl.loc[df_son_vl[(df_son_vl['key'] == 'type') & 
                                    (df_son_vl['parent_key'] == 'internal-vld')].index,'value'] = df_son_vl[(df_son_vl['key'] == 'type') & 
                                    (df_son_vl['parent_key'] == 'internal-vld')].apply(lambda x : 'ELAN' if x.value == 'E-LAN' 
                                                                                        else ( 'ELINE' if x.value == 'E-Line' else 'ELAN'),axis=1 )
            dataset = dataset.append(df_son_vl)

        dataset.drop(dataset[(dataset['lineage']=='NULL')&(dataset['value']!='NULL')].index,axis=0,inplace=True)
        dataset.loc[(dataset['parent_key'] == 'interface') & 
                    ( dataset['key'] == 'position'),'value'] = dataset[(dataset['parent_key'] == 'interface') & 
                      ( dataset['key'] == 'position')]['value'].astype('int64')
        dataset.reset_index(inplace=True,drop=True)
        
        writer = write_dict()
        message = writer.translate(dataset)

        if 'root' in message:
            message = message['root']

        return message

    def translate_to_osm_nsd(self,received_file):
        '''
        reads a dictionary and is converted to a DataFrame with columns containing :
        enumerated 'parent level', enumerated 'level', 'parent key', 'key', 
        'value' and complete 'lineage'. 
        Since the input dict contains further nested dict as well, storing 
        the level information and the complete lineage helps in selecting out 
        particular key-value pair and transforming it for osm to sonata values
        and vice-versa.
        
        Params
        ------
        received_file : dict
            dictionary containing the full set of sonata ns descriptor
       
        Returns
        -------
        message : dict
            returns a translated osm ns descriptor dictionary
            
        '''

        
        sonata = received_file
        
        ### reading a dict/ json content into a pandas dataframe
        reader = read_dict()

        sonata_dataset = pd.DataFrame(reader.dict_parser(sonata, 'root', 1, '0|preroot|0'), 
                          columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])
        sonata_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
        sonata_dataset.fillna('NULL', inplace=True)

        ### if the mapping is not found then insert them
        record = self.db_mappings.nsd_mapping
        res = record.find()

        t = [i for i in res]

        ### if the mapping is not found then insert them
        if(len(t) ==0):
            insert = insert_into_db(self.client)
            insert.insert_nsd_mapping()
            res = record.find()
            t = [i for i in res]


        transformation_obj = transformation()

        osm_sonata = pd.DataFrame.from_dict(t[0])
        osm_son_vld = pd.DataFrame.from_dict(t[1])
        osm_son_vnffgd = pd.DataFrame.from_dict(t[2])
        
        
        ### joining/ merging the 1st level nsd mapping with the input sonata file to get the corresponding osm values
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

        dataset.loc[(dataset['key'] == 'type') & 
                       (dataset['parent_key'] == 'connection-point'),'value']=dataset[(dataset['key'] == 'type') & 
                                                                               (dataset['parent_key'] == 'connection-point')].apply(lambda x : 'VPORT' if x.value in ['management','internal','external'] else 'NULL',axis=1)

        dataset['lineage'] = dataset.apply(lambda x : x['osm_lineage'] + x['lineage'].split('|')[-1],axis=1)

        dataset.loc[dataset['parent_key'] == 'constituent-vnfd','value'] = dataset[dataset['parent_key'] == 'constituent-vnfd'].apply(lambda x :
                                                                   (int(x['lineage'].split('|')[-1]) + 1) if x['key']=='member-vnf-index' else x['value'],axis=1 )

        dataset=dataset.sort_values(by= 'lineage',ascending=True)
        
        temp = dataset[(dataset['key'] == 'name') & 
                       (dataset['parent_key'] == 'nsd')].copy()
        temp['key'] = 'id'
        dataset= dataset.append(temp)      
        
        ### translating and transforming the sonata virtual links to osm
        df = transformation_obj.ret_ds(sonata_dataset,'virtual_links',2)
        vl_list = df[(df['key'] == 'connectivity_type') & ( df['value'] == 'E-Line')]['lineage'].values

        if len(vl_list) == 2:
            
            df.loc[(df['lineage'] == vl_list[0]) & 
                   (df['key'] == 'id'),'value'] = df.loc[(df['lineage'] == vl_list[0]) & 
                                                   (df['key'] == 'id'),'value'].values[0] + '-' + df.loc[(df['lineage'] == vl_list[-1]) & 
                                                    (df['key'] == 'id'),'value'].values[0]
                
            df.drop(df[(df['lineage'] == vl_list[-1]) & 
                   (df['key'].isin(['id','connectivity_type']))].index,inplace=True,axis=0)

            df.loc[(df['lineage'] == vl_list[-1]),'lineage'] = vl_list[0]
            
        elif len(vl_list) > 2:
            
            df.drop(df[(df['lineage'] == vl_list[0])].index,inplace=True,axis=0)
            
            for i,l in enumerate(vl_list[1:]):
                df.loc[df[(df['lineage'] == vl_list[i])].index,'lineage'] = vl_list[i-1]
                
            df.drop(df[(df['lineage'] == vl_list[-1])].index,inplace=True,axis=0)
            
        vl = transformation_obj.son_vld_nsd(df,':')
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

        df_son_vld.loc[(df_son_vld['key'] == 'type') & 
                       (df_son_vld['parent_key'] == 'vld'),'value']=df_son_vld[(df_son_vld['key'] == 'type') & 
                                                                               (df_son_vld['parent_key'] == 'vld')].apply(lambda x : 'ELAN' if x.value == 'E-LAN'
                                                                                             else ( 'ELINE' if x.value == 'E-Line' else 'NULL'),axis=1)

        temp = df_son_vld[(df_son_vld['parent_key'] == 'vld') & (df_son_vld['key'] == 'id')].copy()
        temp['key'] = 'name'
        df_son_vld = df_son_vld.append(temp)

        temp = df_son_vld[(df_son_vld['parent_key'] == 'vnfd-connection-point-ref') & (df_son_vld['key'] == 'member-vnf-index-ref')].copy()
        temp['key'] = 'vnfd-id-ref'
        df_son_vld = df_son_vld.append(temp)

        def lookup_value(value):
            vnf_lkup = dataset[(dataset['parent_key'] == 'constituent-vnfd')
                              ][['lineage','key','value']].pivot(index='lineage',
                                                                 columns='key',
                                                                 values='value').reset_index().copy()
            
            mask_vnf_name = vnf_lkup['vnfd-id-ref'] == value
            values = vnf_lkup.loc[mask_vnf_name,'member-vnf-index'].values[0]
            
            return int(values)
        
        df_son_vld.loc[(df_son_vld['parent_key'] == 'vnfd-connection-point-ref') & 
        (df_son_vld['key'] == 'member-vnf-index-ref'),'value'] =df_son_vld[(df_son_vld['parent_key'] == 'vnfd-connection-point-ref') & 
        (df_son_vld['key'] == 'member-vnf-index-ref')].apply(lambda x : lookup_value(x['value']) if 1==1 else 'NULL',axis=1)

        df_son_vld.sort_values(by=['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,True,True],inplace=True)
        dataset = dataset.append(df_son_vld)
        dataset=dataset.sort_values(by= 'lineage',ascending=True)
        
        ### translating and transforming the sonata forwarding graphs to osm
        if len(dataset[(dataset['parent_key'] == 'constituent-vnfd') & (dataset['key'] == 'vnfd-id-ref')]) > 1:
            df = transformation_obj.ret_ds(sonata_dataset,'forwarding_graphs',2)
            fg = transformation_obj.son_fwdg_nsd(df,':')
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

            temp = df_son_vnffgd[(df_son_vnffgd['parent_key'] == 'vnfd-connection-point-ref') & (df_son_vnffgd['key'] == 'member-vnf-index-ref')].copy()
            temp['key'] = 'vnfd-id-ref'
            df_son_vnffgd = df_son_vnffgd.append(temp)  
                
            df_son_vnffgd.loc[(df_son_vnffgd['parent_key'] == 'vnfd-connection-point-ref') & 
            (df_son_vnffgd['key'] == 'member-vnf-index-ref'),'value'] =df_son_vnffgd[(df_son_vnffgd['parent_key'] == 'vnfd-connection-point-ref') & 
            (df_son_vnffgd['key'] == 'member-vnf-index-ref')].apply(lambda x :
                                                                                lookup_value(x['value']) if 1==1 else 'NULL',axis=1)

            df_son_vnffgd.sort_values(by=['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,True,True],inplace=True)
            dataset = dataset.append(df_son_vnffgd)

        dataset.drop('osm_lineage',axis=1,inplace=True)

        writer = write_dict()
        message = writer.translate(dataset.sort_values(by='lineage'))

        return message

    def translate_to_sonata_nsd(self,received_file):
        '''
        reads a dictionary and is converted to a DataFrame with columns containing :
        enumerated 'parent level', enumerated 'level', 'parent key', 'key', 
        'value' and complete 'lineage'. 
        Since the input dict contains further nested dict as well, storing 
        the level information and the complete lineage helps in selecting out 
        particular key-value pair and transforming it for osm to sonata values
        and vice-versa.
        
        Params
        ------
        received_file : dict
            dictionary containing the full set of osm ns descriptor
        
        Returns
        -------
        message : dict
            returns a translated sonata ns descriptor dictionary
            
        '''

        osm = received_file
        
        ### reading a dict/ json content into a pandas dataframe
        reader = read_dict()

        osm_dataset = pd.DataFrame(reader.dict_parser(osm, 'root', 1, '0|preroot|0'),
                          columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])

        osm_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
        osm_dataset.fillna('NULL', inplace=True)
        
        ### if the mapping is not found then insert them
        record = self.db_mappings.nsd_mapping
        res = record.find()
        t = [i for i in res]
        
        ### if the mapping is not found then insert them
        if(len(t) ==0):
            insert = insert_into_db(self.client)
            insert.insert_nsd_mapping()
            res = record.find()
            t = [i for i in res]     

        transformation_obj= transformation()

        osm_sonata = pd.DataFrame.from_dict(t[0])
        osm_son_vld = pd.DataFrame.from_dict(t[1])
        osm_son_vnffgd = pd.DataFrame.from_dict(t[2])


        dataset=pd.merge(osm_dataset,osm_sonata,
             left_on=['key','parent_key','level','parent_level'],
             right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')
        dataset.fillna('NULL',inplace=True)
        dataset = dataset[['son_parent_level','son_level','son_parent_key','son_key','value','lineage','son_lineage']]
        dataset.columns = ['parent_level','level','parent_key','key','value','lineage','son_lineage']

        for i in range(dataset[dataset['parent_key'] == 'network_functions'].groupby(['key']).agg({'value': 'count'}).values[0][0]):
            dataset = dataset.append(pd.DataFrame(
                    [['pg-scramble','vnf_vendor',2,'network_functions',1,'0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|'+str(i),'0|preroot|0|root|'],
                     ['0.3','vnf_version',2,'network_functions',1,'0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|'+str(i),'0|preroot|0|root|']],
                           columns = ['value','key','level','parent_key','parent_level','lineage','son_lineage']))

        dataset=dataset.append(pd.DataFrame(
            [['NULL','virtual_links',1,'root',0,'NULL','NULL'],
            ['NULL','network_functions',1,'root',0,'NULL','NULL'],
            ['NULL','forwarding_graphs',1,'root',0,'NULL','NULL'],
            ['NULL','connection_points',1,'root',0,'NULL','NULL'],
            ['pg-scramble','vendor',1,'root',0,'0|preroot|0|root|0|nsd:nsd-catalog|0','0|preroot|'],
             ],
           columns = ['value','key','level','parent_key','parent_level','lineage','son_lineage']))

        dataset.loc[dataset['value'] != 'NULL','lineage'] = dataset.loc[dataset['value'] != 'NULL'].apply(
            lambda x: ('|').join(x['son_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-3] +'|'+ x['son_lineage'].split('|')[-2]+'|'+x['lineage'].split('|')[-1],axis=1)

        dataset.loc[dataset['key'] == 'vnf_name','value'] = dataset.loc[dataset['key'] == 'vnf_id','value'].values
            
        
        temp = dataset[(dataset['parent_key'] == 'connection_points') & (dataset['key'] == 'type')].copy()
        temp['key'] = 'interface'
        temp['value'] = 'ipv4'
        dataset = dataset.append(temp)
        if(len(dataset[dataset['parent_key'] == 'connection_points']) >0):
            dataset.loc[(dataset['key'] == 'type') & 
                           (dataset['parent_key'] == 'connection_points'),'value']=dataset[(dataset['key'] == 'id') & 
                                                                                   (dataset['parent_key'] == 'connection_points')].apply(lambda x : 'management' if x.value == 'mgmt' else 'external' , axis=1).values

        dataset=dataset.sort_values(by= ['lineage','parent_key'],ascending=True)
        dataset['value'] = dataset['value'].astype('str')

        ### translating and transforming the osm virtual links to sonata
        df = transformation_obj.ret_ds(osm_dataset,'vld',4)
        df.sort_values(by=['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,False,True],inplace=True)
        vl = transformation_obj.osm_vld_nsd(df)
        vl['level'] = vl['level'].astype('int64')
        vl['parent_level'] = vl['parent_level'].astype('int64')

        df_osm_vld = pd.merge(vl,osm_son_vld,
                         left_on=['key','parent_key','level','parent_level'],
                         right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')

        df_osm_vld =  df_osm_vld[['son_parent_level','son_level','son_parent_key','son_key','value','lineage','son_lineage']]
        df_osm_vld.columns = ['parent_level','level','parent_key','key','value','lineage','son_lineage']

        df_osm_vld.loc[(df_osm_vld['level'] == 2) & (df_osm_vld['parent_level'] == 1) & (df_osm_vld['value'] != 'NULL'),'lineage'] = df_osm_vld[(df_osm_vld['level'] == 2) & (df_osm_vld['parent_level'] == 1) & (df_osm_vld['value'] != 'NULL')].apply(
            lambda x: ('|').join(x['son_lineage'].split('|')[:-3])+'|'+x['lineage'].split('|')[-3] +'|'+ x['son_lineage'].split('|')[-2]+'|'+x['lineage'].split('|')[-1],axis=1)

        df_osm_vld.loc[df_osm_vld[df_osm_vld['key'] == 'connectivity_type'].index,'value'] = df_osm_vld[df_osm_vld['key'] == 'connectivity_type'].apply(lambda x : 'E-LAN' if x.value == 'ELAN' else ( 'E-Line' if x.value == 'ELINE' else 'NULL'),axis=1 )
        dataset= dataset.append(df_osm_vld)

        dataset=dataset.sort_values(by= ['lineage','parent_key'],ascending=True)

        ### translating and transforming the osm forwarding graphs to sonata
        df = transformation_obj.ret_ds(osm_dataset,'vnffgd',4)

        if not df.empty:
            fg= transformation_obj.osm_fwdg_nsd(df)
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
        message = writer.translate(dataset.sort_values(by='lineage'))
        message = message['preroot']['root'][0]

        return message

    def translate_to_sonata_vnfd(self,received_file):
        '''
        reads a dictionary and is converted to a DataFrame with columns containing :
        enumerated 'parent level', enumerated 'level', 'parent key', 'key', 
        'value' and complete 'lineage'. 
        Since the input dict contains further nested dict as well, storing 
        the level information and the complete lineage helps in selecting out 
        particular key-value pair and transforming it for osm to sonata values
        and vice-versa.
        
        Params
        ------
        received_file : dict
            dictionary containing the full set of osm vnf descriptor
        
        Returns
        -------
        message : dict
            returns a translated sonata vnf descriptor dictionary
            
        '''

        osm = received_file
        
        ### reading a dict/ json content into a pandas dataframe
        reader = read_dict()

        osm_dataset = pd.DataFrame(reader.dict_parser(osm, 'root', 1, '0|preroot|0'),
                          columns=['parent_level', 'parent_key', 'level', 'key', 'value', 'lineage'])

        osm_dataset.sort_values(ascending=True, by=['level', 'parent_key'])
        osm_dataset.fillna('NULL', inplace=True)

        ### if the mapping is not found then insert them
        record = self.db_mappings.vnfd_mapping
        res = record.find()
        t = [i for i in res]

        if(len(t) ==0):
            insert = insert_into_db(self.client)
            insert.insert_vnfd_mapping()
            res = record.find()
            t = [i for i in res]     

        transformation_obj= transformation()

        mapping_vnfd = pd.DataFrame.from_dict(t[0])
        osm_son_vl = pd.DataFrame.from_dict(t[1])
        osm_son_cp = pd.DataFrame.from_dict(t[2])
        osm_son_vdu = pd.DataFrame.from_dict(t[3])
        osm_son_vdu_ext = pd.DataFrame.from_dict(t[4])



        dataset=pd.merge(osm_dataset,mapping_vnfd,
                     left_on=['key','parent_key','level','parent_level'],
                     right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')
        dataset.fillna('NULL',inplace=True)
        dataset = dataset[['son_parent_level','son_level','son_parent_key','son_key','value','lineage','son_lineage']]
        dataset.columns = ['parent_level','level','parent_key','key','value','lineage','son_lineage']
        dataset['lineage'] = dataset.apply(lambda x: x['son_lineage'] + x['lineage'].split('|')[-1] if x['lineage'] !='NULL' else 'NULL', axis=1)    
        #dataset.loc[dataset[(dataset['parent_key'] == 'root') &(dataset['key'] == 'vendor')].index,'value'] = 'pg-scramble'
        dataset=dataset.append(pd.DataFrame([
        ['NULL',0, 1, 'root', 'connection_points','NULL','NULL'],
        ['NULL',0, 1, 'root', 'virtual_deployment_units','NULL','NULL'],
        #['0|preroot|',0,1,'root','descriptor_schema','0|preroot|0','https://raw.githubusercontent.com/sonata-nfv/tng-schema/master/service-descriptor/nsd-schema.yml'],
        ['0|preroot|',0,1,'root','vendor','0|preroot|0','pg-scramble']],
                                           columns = ['son_lineage','parent_level','level','parent_key','key','lineage','value']))

        dataset.sort_values(by=['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,True,True],inplace=True)
        dataset.reset_index(inplace=True,drop=True)

        ### translating and transforming the osm connection points to sonata
        df_cp = transformation_obj.ret_ds(osm_dataset,'connection-point',4)
        df_cp['level'] = df_cp['level'].astype('int64')
        df_cp['parent_level'] = df_cp['parent_level'].astype('int64')
        df_osm_cp = pd.merge(df_cp, osm_son_cp,
                             left_on=['key', 'parent_key', 'level', 'parent_level'],
                             right_on=['osm_key', 'osm_parent_key', 'osm_level', 'osm_parent_level'], how='inner')

        df_osm_cp = df_osm_cp[
            ['son_parent_level', 'son_level', 'son_parent_key', 'son_key', 'value', 'son_lineage', 'lineage']]
        df_osm_cp.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'son_lineage', 'lineage']


        df_osm_cp['lineage'] = df_osm_cp.apply(lambda x: x['son_lineage'] + 
                                                x['lineage'].split('|')[-1] if x['lineage'] !='NULL' else 'NULL', axis=1)

        temp = df_osm_cp[(df_osm_cp['parent_key'] == 'connection_points') & 
                        (df_osm_cp['key'] == 'type')&
                        (df_osm_cp['level'] == 2) & 
                        (df_osm_cp['parent_level'] == 1)].copy()
        temp['key'] = 'interface'
        temp['value'] = 'ipv4'
        df_osm_cp = df_osm_cp.append(temp)

        df_osm_cp.sort_values(['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,True,True],inplace=True)
        df_osm_cp.loc[(df_osm_cp['key']=='type') & 
                                (df_osm_cp['parent_key']=='connection_points')&
                                 (df_osm_cp['level']==2) & 
                                  (df_osm_cp['parent_level']==1),'value'] = 'external'



        dataset = dataset.append(df_osm_cp)
        
        
        ### translating and transforming the osm vdu to sonata
        df_vl = transformation_obj.ret_ds(osm_dataset,'vdu',4)
        df_vl = transformation_obj.osm_vld_vnfd(df_vl)
        
        df_vl['level'] = df_vl['level'].astype('int64')
        df_vl['parent_level'] = df_vl['parent_level'].astype('int64')
        df_osm_vl =  pd.merge(df_vl, osm_son_vl,
                             left_on=['key', 'parent_key', 'level', 'parent_level'],
                             right_on=['osm_key', 'osm_parent_key', 'osm_level', 'osm_parent_level'], how='inner')
        df_osm_vl = df_osm_vl[
            ['son_parent_level', 'son_level', 'son_parent_key', 'son_key', 'value', 'son_lineage', 'lineage']]
        df_osm_vl.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'son_lineage', 'lineage']
        df_osm_vl['lineage'] = df_osm_vl.apply(lambda x: x['son_lineage'] + x['lineage'].split('|')[-1] if x['lineage'] !='NULL' else 'NULL', axis=1)
        df_osm_vl.sort_values(['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,True,True],inplace=True)
        dataset = dataset.append(df_osm_vl)

        df_vdu = transformation_obj.ret_ds(osm_dataset,'vdu',4)
        if 'internal-connection-point' in df_vdu['parent_key'].values:
            df_vdu.drop(df_vdu[df_vdu['parent_key']=='interface'].index,inplace=True,axis=0)
            
        else :
            df_vdu.drop(df_vdu[df_vdu['lineage'].isin(df_vdu[(df_vdu['parent_key']=='interface') & (df_vdu['value']=='INTERNAL')]['lineage']) &
              (df_vdu['parent_key']=='interface') ].index,inplace=True,axis=0)
            
        df_vdu['level'] = df_vdu['level'].astype('int64')
        df_vdu['parent_level'] = df_vdu['parent_level'].astype('int64')
        df_vdu['value'] = df_vdu['value'].astype('object')
        df_osm_vdu = pd.merge(df_vdu, osm_son_vdu,
                              left_on=['key', 'parent_key', 'level', 'parent_level'],
                              right_on=['osm_key', 'osm_parent_key', 'osm_level', 'osm_parent_level'], how='inner')
        df_osm_vdu.sort_values(['son_level'], inplace=True)
        df_osm_vdu = df_osm_vdu[
            ['son_parent_level', 'son_level', 'son_parent_key', 'son_key', 'value', 'son_lineage', 'lineage']]
        df_osm_vdu.columns = ['parent_level', 'level', 'parent_key', 'key', 'value', 'son_lineage', 'lineage']

        df_osm_vdu['son_lineage'] = df_osm_vdu.apply(lambda x: x['son_lineage'] + x['lineage'].split('|')[-1] if x['lineage'] !='NULL' else 'NULL', axis=1)
        df_osm_vdu.loc[(df_osm_vdu['parent_level']==1) & 
                       (df_osm_vdu['level'] == 2),'lineage'] = df_osm_vdu[(df_osm_vdu['parent_level']==1) & (df_osm_vdu['level'] == 2)].apply(
            lambda x: x['son_lineage'] , axis=1)

        df_osm_vdu.loc[(df_osm_vdu['parent_level']==2) & 
                       (df_osm_vdu['level'] == 3),'lineage'] = df_osm_vdu[(df_osm_vdu['parent_level']==2) & (df_osm_vdu['level'] == 3)].apply(lambda x: ('|').join(x['son_lineage'].split('|')[:-3]) + '|'+x['lineage'].split('|')[-3] 
                                                                                                        + '|' + ('|').join(x['son_lineage'].split('|')[-2:]) if x['lineage'] !='NULL' else 'NULL', axis=1)

        df_osm_vdu.loc[(df_osm_vdu['parent_level']==3) & 
                       (df_osm_vdu['level'] == 4),'lineage'] = df_osm_vdu[(df_osm_vdu['parent_level']==3) &(df_osm_vdu['level'] == 4)].apply(lambda x: ('|').join(x['son_lineage'].split('|')[:-5]) + '|'+x['lineage'].split('|')[-3] 
                                                                                                        + '|' + ('|').join(x['son_lineage'].split('|')[-4:]) if x['lineage'] !='NULL' else 'NULL', axis=1)
        df_osm_vdu.loc[(df_osm_vdu['parent_level']==3) & 
                       (df_osm_vdu['level'] == 4),'value'] = df_osm_vdu[(df_osm_vdu['parent_level']==3) &(df_osm_vdu['level'] == 4)].apply(lambda x: 'MB' if                                                            ((x['key'] =='size_unit') & (x['parent_key'] =='memory')) 
                                                                                else ( 'GB' if ((x['key'] =='size_unit') & (x['parent_key'] =='storage'))
                                                                                else x['value']),axis=1)

        df_osm_vdu=df_osm_vdu.append(pd.DataFrame([
        ['NULL',1, 2, 'virtual_deployment_units', 'connection_points','NULL','NULL'],
        ['NULL',1, 2, 'virtual_deployment_units', 'resource_requirements','NULL','NULL'],
        ['NULL',2, 3, 'resource_requirements', 'cpu','NULL','NULL'],
        ['NULL',2, 3, 'resource_requirements', 'memory','NULL','NULL'],
        ['NULL',2, 3, 'resource_requirements', 'storage','NULL','NULL']
        ],
         columns = ['son_lineage','parent_level','level','parent_key','key','lineage','value']))


        for i in range(len(df_osm_vdu[(df_osm_vdu['level'] == 2) & (df_osm_vdu['value'] != 'NULL')]['lineage'].unique())):                                                                                                                      
            df_osm_vdu=df_osm_vdu.append(pd.DataFrame([
            ['NULL',2, 3, 'resource_requirements', 'cpu','0|preroot|0|root|'+str(i)+'|virtual_deployment_units|0','1'],
            ['NULL',2, 3, 'resource_requirements', 'memory','0|preroot|0|root|'+str(i)+'|virtual_deployment_units|0','2'],
            ['NULL',2, 3, 'resource_requirements', 'storage','0|preroot|0|root|'+str(i)+'|virtual_deployment_units|0','3']],
            columns = ['son_lineage','parent_level','level','parent_key','key','lineage','value']))



        temp = df_osm_vdu[(df_osm_vdu['parent_key'] == 'connection_points') & 
                                (df_osm_vdu['key'] == 'type') &
                                 (df_osm_vdu['level']==3) & 
                                  (df_osm_vdu['parent_level']==2)].copy()
        temp['key'] = 'interface'
        temp['value'] = 'ipv4'
        df_osm_vdu = df_osm_vdu.append(temp)

        df_osm_vdu.sort_values(by= ['parent_level','parent_key','lineage','key','level'],ascending=[True,True,True,True,True],inplace=True)

        df_osm_vdu.loc[(df_osm_vdu['key']=='type') & 
                                  (df_osm_vdu['parent_key']=='connection_points') &
                                 (df_osm_vdu['level']==3) & 
                                  (df_osm_vdu['parent_level']==2),'value'] = 'internal'

        df_osm_vdu.loc[(df_osm_vdu['key'].isin(['size','vcpus'])) & 
                                  (df_osm_vdu['parent_key'].isin(['memory','storage','cpu'])) &
                                 (df_osm_vdu['level']==4) & 
                                  (df_osm_vdu['parent_level']==3),'value'] = df_osm_vdu[(df_osm_vdu['key'].isin(['size','vcpus'])) & 
                                  (df_osm_vdu['parent_key'].isin(['memory','storage','cpu'])) &
                                 (df_osm_vdu['level']==4) & 
                                  (df_osm_vdu['parent_level']==3)]['value'].astype('int64')

        dataset = dataset.append(df_osm_vdu)
        dataset.drop('son_lineage',inplace=True,axis=1)
        dataset.reset_index(inplace=True,drop=True)

        writer = write_dict()
        message = writer.translate(dataset)
        message = message['preroot']['root'][0]

        return message

class insert_into_db():
    
    def __init__(self, client = None):
        
        self.client = client
        self.db_mappings = self.client.mapping
        self.db_descriptors = self.client.descriptors
        
    def insert_nsd_mapping(self):
        '''
            creates 3 mongoDB documents to store the mapping Virtual Functions , Forwarding Graphs and the rest parameters

            Params
            ------
            record: pymongo.collection.Collection
                cursor to the MongoDb collection where mappings are stored

        '''
        osm_sonata_nsd_mapping= [
                ['0|preroot|0|root|0|nsd:nsd-catalog|',2,3,'nsd','description','0|preroot|',0,1,'root','description'],
                #['0|preroot|0|root|0|nsd:nsd-catalog|',2,3,'nsd','name','0|preroot|',0,1,'root','vendor'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|',2,3,'nsd','name','0|preroot|',0,1,'root','name'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|',2,3,'nsd','version','0|preroot|',0,1,'root','version'],


                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'constituent-vnfd','vnfd-id-ref','0|preroot|0|root|',1,2,'network_functions','vnf_id'],
                ['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'constituent-vnfd','member-vnf-index','0|preroot|0|root|',1,2,'network_functions','vnf_name'],
                #['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'constituent-vnfd','vnfd-id-ref','0|preroot|0|root|',1,2,'network_functions','vnf_version'],
                #['0|preroot|0|root|0|nsd:nsd-catalog|0|nsd|',3,4,'constituent-vnfd','vnfd-id-ref','0|preroot|0|root|',1,2,'network_functions','vnf_vendor'],

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
        

    def insert_vnfd_mapping(self):
        '''
            creates 5 mongoDB documents to store the mapping Virtual Functions , Forwarding Graphs and the rest parameters

            Params
            ------
            record: pymongo.collection.Collection
                cursor to the MongoDb collection where mappings are stored

        '''
        
        osm_sonata_vnfd_mapping = [
            ['0|preroot|0|root|',1, 2, 'vnfd:vnfd-catalog', 'schema-version','0|preroot|', 0, 1, 'root', 'descriptor_version'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|',2, 3, 'vnfd', 'name','0|preroot|', 0, 1, 'root', 'name'],
            #['0|preroot|0|root|0|vnfd:vnfd-catalog|',2, 3, 'vnfd', 'name','0|preroot|', 0, 1, 'root', 'vendor'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|',2, 3, 'vnfd', 'description','0|preroot|', 0, 1, 'root', 'description'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|',2, 3, 'vnfd', 'version','0|preroot|', 0, 1, 'root', 'version']
        ]

        osm_sonata_vl_mapping = [
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|',2, 3, 'vnfd', 'internal-vld', '0|preroot|',0, 1, 'root', 'virtual_links'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|',3, 4, 'internal-vld', 'id','0|preroot|0|root|', 1, 2, 'virtual_links', 'id'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|',3, 4, 'internal-vld', 'type','0|preroot|0|root|', 1, 2, 'virtual_links', 'connectivity_type'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|',3, 4, 'internal-vld' , 'internal-connection-point', '0|preroot|0|root|',1, 2, 'virtual_links',
             'connection_points_reference'],
        ]

        osm_sonata_cp_mapping = [
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|',2, 3, 'vnfd', 'connection-point', '0|preroot|',0, 1, 'root', 'connection_points'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|',3, 4, 'connection-point', 'name', '0|preroot|0|root|',1, 2, 'connection_points', 'id'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|',3, 4, 'connection-point', 'type', '0|preroot|0|root|',1, 2, 'connection_points', 'type'],
        ]

        osm_sonata_vdu_mapping = [
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|',2, 3, 'vnfd', 'vdu', '0|preroot|',0, 1, 'root', 'virtual_deployment_units'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|',3, 4, 'vdu', 'id', '0|preroot|0|root|',1, 2, 'virtual_deployment_units', 'id'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|',3, 4, 'vdu', 'image', '0|preroot|0|root|',1, 2, 'virtual_deployment_units', 'vm_image'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|',3, 4, 'vdu', 'image-checksum','0|preroot|0|root|', 1, 2, 'virtual_deployment_units', 'vm_image_md5'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'vm-flavor', 'vcpu-count','0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|', 3, 4, 'cpu', 'vcpus'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'vm-flavor', 'memory-mb','0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|', 3, 4, 'memory', 'size'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'vm-flavor', 'memory-mb', '0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|',3, 4, 'memory', 'size_unit'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'vm-flavor', 'storage-gb', '0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|',3, 4, 'storage', 'size'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'vm-flavor', 'storage-gb','0|preroot|0|root|0|virtual_deployment_units|0|resource_requirements|' ,3, 4, 'storage', 'size_unit'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'internal-connection-point', 'id','0|preroot|0|root|0|virtual_deployment_units|', 2, 3, 'connection_points', 'id'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'internal-connection-point', 'type','0|preroot|0|root|0|virtual_deployment_units|', 2, 3, 'connection_points', 'type'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'interface', 'name','0|preroot|0|root|0|virtual_deployment_units|', 2, 3, 'connection_points', 'id'],
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'interface', 'type','0|preroot|0|root|0|virtual_deployment_units|', 2, 3, 'connection_points', 'type'],
        
        ]


        osm_sonata_vdu_ext_mapping = [
            ['0|preroot|0|root|0|vnfd:vnfd-catalog|0|vnfd|0|vdu|',4, 5, 'interface', 'name','0|preroot|0|root|',1, 2, 'virtual_links',
             'connection_points_reference']
        ]


        mapping_vnfd = pd.DataFrame(osm_sonata_vnfd_mapping,
                                    columns=["osm_lineage","osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                             "son_lineage","son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_vl = pd.DataFrame(osm_sonata_vl_mapping,
                                  columns=["osm_lineage","osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_lineage","son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_cp = pd.DataFrame(osm_sonata_cp_mapping,
                                  columns=["osm_lineage","osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_lineage","son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)


        osm_son_vdu = pd.DataFrame(osm_sonata_vdu_mapping,
                                   columns=["osm_lineage","osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                            "son_lineage","son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_vdu_ext = pd.DataFrame(osm_sonata_vdu_ext_mapping,
                                  columns=["osm_lineage","osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_lineage","son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        
        mapping_vnfd.index = [str(i) for i in mapping_vnfd.index]
        osm_son_vl.index = [str(i) for i in osm_son_vl.index]
        osm_son_cp.index = [str(i) for i in osm_son_cp.index]
        osm_son_vdu.index = [str(i) for i in osm_son_vdu.index]
        osm_son_vdu_ext.index = [str(i) for i in osm_son_vdu_ext.index]

        record = self.db_mappings.vnfd_mapping
        
        temp = mapping_vnfd.to_dict()
        id = record.insert_one(temp)

        temp = osm_son_vl.to_dict()
        id = record.insert_one(temp)

        temp = osm_son_cp.to_dict()
        id = record.insert_one(temp)

        temp = osm_son_vdu.to_dict()
        id = record.insert_one(temp)  
        
        temp = osm_son_vdu_ext.to_dict()
        id = record.insert_one(temp)
        

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

    def osm_fwdg_nsd(self,df):
        '''
        reads a pandas.DataFrame
        
        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the forwarding graph details of osm ns descriptor
       
        Returns
        -------
        pandas.DataFrame
            returns a subset dataframe
            
        '''        
        temp = df[df['parent_key'].isin(['vnfd-connection-point-ref','classifier']) & 
           df['key'].isin(['vnfd-connection-point-ref','vnfd-id-ref'])].groupby(
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
           df['key'].isin(['vnfd-connection-point-ref','order','vnfd-id-ref'])].index,axis=0)
        
        return df.append(temp)


    def osm_vld_nsd(self,df):
        '''
        reads a pandas.DataFrame
        
        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the virtual link details of osm ns descriptor
       
        Returns
        -------
        pandas.DataFrame
            returns a subset dataframe
            
        '''        
        temp = df[df['parent_key'].isin(['vnfd-connection-point-ref']) & 
               df['key'].isin(['vnfd-connection-point-ref','vnfd-id-ref'])].groupby(
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

    def osm_vld_vnfd(self,df):
        '''
        reads a pandas.DataFrame
        
        Params
        ------
        ds : pandas.DataFrame
            dataframe containing the virtual link details of osm vnf descriptor
       
        Returns
        -------
        pandas.DataFrame
        returns a subset dataframe
        
        '''        
        vdu_name = df[df['key'].isin(['id']) & (df['parent_key'] == 'vdu')].copy()
        vdu_name[['parent_key','parent_level','level']] = ['interface',4,5]
        vdu_name['key'] = 'internal-connection-point-ref'
        vdu_name['temp'] = vdu_name['value'].astype('category').cat.codes
        vdu_name['lineage'] = vdu_name.apply(lambda x : '|'.join(x['lineage'].split('|')[:-1]) + '|' + str(x['temp']),axis=1)
        vdu_name.drop(['temp'],axis=1,inplace=True)

        ext_conn_pts = df[(df['key'] =='external-connection-point-ref') & (df['parent_key'] == 'interface')].copy()
        ext_conn_pts['lineage'] = ext_conn_pts.apply(lambda x : ('|').join(x['lineage'].split('|')[:-2]),axis=1)
        ext_conn_pts['temp'] = ext_conn_pts['value'].astype('category').cat.codes
        ext_conn_pts['lineage'] = ext_conn_pts.apply(lambda x : '|'.join(x['lineage'].split('|')[:-1]) + '|' + str(x['temp']),axis=1)
        ext_conn_pts.drop(['temp'],axis=1,inplace=True)



        ext_conn_pts_typ=ext_conn_pts.copy()
        ext_conn_pts_typ['key'] = 'type'
        ext_conn_pts_typ['value'] = ext_conn_pts_typ['value'].apply(lambda x : 'E-LAN' if 'mgmt' in x else 'E-Line')

        ext_conn_pts_id = ext_conn_pts.copy()
        ext_conn_pts_id['key'] = 'id'

        int_conn_pts= df[(df['key'] =='name') & (df['parent_key'] == 'interface')].copy()
        int_conn_pts['key'] = 'internal-connection-point-ref'

        int_conn_pts_vdu= df[(df['key'] =='internal-connection-point-ref') & (df['parent_key'] == 'interface')].copy()
        if len(int_conn_pts_vdu) > 0 : 
            int_conn_pts_vdu['key'] = 'internal-connection-point-ref2'
            int_conn_pts_vdu = int_conn_pts[int_conn_pts['lineage'].isin(list(int_conn_pts_vdu['lineage'].values))]
            int_conn_pts = int_conn_pts[~int_conn_pts['lineage'].isin(list(int_conn_pts_vdu['lineage'].values))]

        int_conn_pts['lineage'] = int_conn_pts.apply(lambda x : ('|').join(x['lineage'].split('|')[:-2]),axis=1)
        int_conn_pts['temp'] = int_conn_pts['value'].astype('category').cat.codes
        int_conn_pts['lineage'] = int_conn_pts.apply(lambda x : '|'.join(x['lineage'].split('|')[:-1]) + '|' + str(x['temp']),axis=1)
        int_conn_pts.drop(['temp'],axis=1,inplace=True)

        ext_int_conn_pts_merge = pd.merge(vdu_name[['key','value','lineage']],
                         int_conn_pts[['value','lineage']],on=['lineage'],how='inner',
                       )

        int_conn_pts.loc[int_conn_pts.index,'value'] = ext_int_conn_pts_merge.apply(
            lambda x : x.value_x + ':' + x.value_y,axis=1).values
        int_conn_pts.loc[int_conn_pts.index,'key'] = ext_int_conn_pts_merge['key'].values

        ext_conn_pts_id.loc[ext_conn_pts_id.index,'lineage']  = int_conn_pts['lineage'].unique()
        ext_conn_pts.loc[ext_conn_pts.index,'lineage']  = int_conn_pts['lineage'].unique()

        if len(int_conn_pts_vdu) > 0 :     
            lineage_number = len(int_conn_pts['lineage'].unique())
            int_conn_pts_vdu['vdu_name']=int_conn_pts_vdu['value'].apply(lambda x : x.split('-')[0])
            int_conn_pts_vdu['lineage'] = int_conn_pts_vdu.apply(lambda x : ('|').join(x['lineage'].split('|')[:-3]) +'|'+ str(lineage_number),axis=1)
            int_conn_pts_vdu.loc[int_conn_pts_vdu.index,'value']= int_conn_pts_vdu.apply(lambda x : x.vdu_name + ':' + x.value,axis=1).values
            int_conn_pts_vdu.loc[int_conn_pts_vdu.index,'value'] = int_conn_pts_vdu.groupby(['key'])['value'].apply(lambda x: (',').join(x).split(',')).values
            int_conn_pts_vdu.drop(['vdu_name'],axis=1 , inplace= True)
            int_conn_pts_vdu = int_conn_pts_vdu.loc[int_conn_pts_vdu.astype('str').drop_duplicates().index]
            int_conn_pts_vdu['key'] = 'internal-connection-point'
            temp = int_conn_pts_vdu.copy()
            temp['key'] = 'id'
            temp['value'] = 'internal'
            int_conn_pts_vdu=int_conn_pts_vdu.append(temp)
            temp['key'] = 'type'
            temp['value'] = 'ELAN'
            int_conn_pts_vdu= int_conn_pts_vdu.append(temp)


        vl_conn_pts= ext_conn_pts.append(ext_conn_pts_typ.append(ext_conn_pts_id.append(int_conn_pts.append(int_conn_pts_vdu))))
        vl_conn_pts['parent_key']='internal-vld'
        vl_conn_pts['level'] = 4
        vl_conn_pts['parent_level']=3
        vl_conn_pts.reset_index(drop=True,inplace=True)
        vl_conn_pts.loc[vl_conn_pts['key']=='internal-connection-point-ref','value']=vl_conn_pts[
            vl_conn_pts['key'].isin(['external-connection-point-ref','internal-connection-point-ref'])].groupby(['lineage'])['value'].apply(
            lambda x : (',').join(x).split(',')).values
        vl_conn_pts.loc[vl_conn_pts['key']=='internal-connection-point-ref','key']= 'internal-connection-point'
        vl_conn_pts.reset_index(drop=True,inplace=True)
        vl_conn_pts.drop(vl_conn_pts[vl_conn_pts['key'].isin(['external-connection-point-ref'])].index,inplace=True,axis=0)
        
        return vl_conn_pts

    def son_fwdg_nsd(self,df,sep=':'):
        '''
        Split the values of a column and expand so the new DataFrame has one split
        value per row. Filters rows where the column is missing.

        Params
        ------
        df : pandas.DataFrame
            dataframe with the column to split and expand
        sep : str
            the string used to split the column's values

        Returns
        -------
        pandas.DataFrame
            Returns a dataframe with the same columns as `df`.
        '''
        
        column1 = 'value'
        column2 = 'key'
        column3 = 'lineage'
        indexes = []
        new_values = []
        new_values2 = []
        df = df.dropna(subset=[column1])
        
        for i, presplit in enumerate(df[[column1,column2,column3]].itertuples()):
            values = str(presplit[1]).split(sep)
            if( len(values) > 1) and ( str(presplit[2]) != 'connection_point_ref'):
                values = str(presplit[1]).split(sep)[1:]
            if len(values) == 1 and str(presplit[2]) == 'connection_point_ref':
                lineage = presplit[3]
                continue 
            if (str(presplit[2]) == 'position' and presplit[3] == lineage):
                continue
            for j in range(len(values)):
                indexes.append(i)
                if (str(presplit[2]) == 'position'):
                    new_values.append(int(values[j]) -1 ) 
                    new_values2.append(str(presplit[2]))
                    continue
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

    def son_vld_nsd(self,df,sep=':'):
        '''
        Split the values of a column and expand so the new DataFrame has one split
        value per row. Filters rows where the column is missing.

        Params
        ------
        df : pandas.DataFrame
            dataframe with the column to split and expand
        sep : str
            the string used to split the column's values

        Returns
        -------
        pandas.DataFrame
            Returns a dataframe with the same columns as `df`.
        '''
        indexes = []
        new_values = []
        new_values2 = []
        
        
        column1 = 'value'
        column2 = 'key'
        
        df = df.dropna(subset=[column1])

        for i, presplit in enumerate(df[[column1,column2]].itertuples()):

            if(isinstance(presplit[1],list)):
                for item in presplit[1]:
                    values = str(item).split(sep) 

                    for j in range(len(values)):
                    
                        if len(values) > 1:
                            new_values.append(values[j])
                            indexes.append(i)
                            if j == 0:
                                new_values2.append('member-vnf-index-ref')
                            elif j == 1:
                                new_values2.append('vnfd-connection-point-ref')

            else:
                indexes.append(i)
                new_values.append(presplit[1])
                new_values2.append(presplit[2])

        new_df = df.iloc[indexes, :].copy()
        new_df[column1] = new_values
        new_df[column2] = new_values2
        
        return new_df

    def son_vld_int_ext_vnfd(self,df,sep=':'):
        '''
        Split the values of a column and expand so the new DataFrame has one split
        value per row. Filters rows where the column is missing.

        Params
        ------
        df : pandas.DataFrame
            dataframe with the column to split and expand
        sep : str
            the string used to split the column's values

        Returns
        -------
        pandas.DataFrame
            Returns a dataframe with the same columns as df.
        '''
        index = []
        new_value = []
        new_key = []
        new_lineage = []
        new_parentKey = []
        new_level = []
        new_parentLevel = []
        new_osm_lineage = []

        j=0

        column1 = 'value'
        column2 = 'key'
        column3 = 'parent_key'
        column4 = 'level'
        column5 = 'parent_level'
        column6 = 'lineage'
        column7 = 'osm_lineage'

        for i, row in enumerate(df[[column1,column2,column3,column4,column5,column6,column7]].itertuples()):
            
            if ((len(row[1][0].split(sep)) >1) & (len(row[1][1].split(sep)) ==1)) :
                
                internal = row[1][0].split(sep)[1]
                vdu = row[1][0].split(sep)[0]
                external = row[1][1]

            elif ((len(row[1][1].split(sep)) >1) & (len(row[1][0].split(sep)) ==1) ) :
                internal = row[1][1].split(sep)[1]
                vdu = row[1][1].split(sep)[0]
                external = row[1][0]
                
            elif ((len(row[1][0].split(sep)) ==1)) :
                internal = row[1]
                vdu = ''
                external = row[1]

            elif (len(row[1][1].split(sep)) >1) & (len(row[1][0].split(sep)) >1) :
                
                internal1 = row[1][1].split(sep)[1]
                vdu1 = row[1][1].split(sep)[0]
                internal2 = row[1][0].split(sep)[1]
                vdu2 = row[1][0].split(sep)[0]
                
                new_value.append(vdu1 + sep + internal1 + '-int')
                new_key.append('name')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal1)
                new_parentKey.append(row[3])
                new_parentLevel.append(row[5])
                new_level.append(row[4])
                new_osm_lineage.append(row[7])

                new_value.append(vdu1 +sep+ str(j+1))
                new_key.append('position')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal1)
                new_parentKey.append(row[3])
                new_parentLevel.append(row[5])
                new_level.append(row[4])
                new_osm_lineage.append(row[7])

                new_value.append(vdu1  +sep+'INTERNAL' )
                new_key.append('type')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal1)
                new_parentKey.append(row[3])
                new_parentLevel.append(row[5])
                new_level.append(row[4])
                new_osm_lineage.append(row[7])

                new_value.append(vdu1 + sep +internal1)
                new_key.append('internal-connection-point-ref')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal1)
                new_parentKey.append(row[3])
                new_parentLevel.append(row[5])
                new_level.append(row[4])
                new_osm_lineage.append(row[7])


                new_value.append(vdu1 + sep+ 'PARAVIRT')
                new_key.append('type')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal1)
                new_parentKey.append('virtual-interface')
                new_parentLevel.append(row[5]+1)
                new_level.append(row[4]+1)
                new_osm_lineage.append(row[7]+'|interface|0')

                new_value.append(vdu2 + sep + internal2 + '-int')
                new_key.append('name')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal2)
                new_parentKey.append(row[3])
                new_parentLevel.append(row[5])
                new_level.append(row[4])
                new_osm_lineage.append(row[7])

                new_value.append(vdu2 +sep+ str(j+1))
                new_key.append('position')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal2)
                new_parentKey.append(row[3])
                new_parentLevel.append(row[5])
                new_level.append(row[4])
                new_osm_lineage.append(row[7])

                new_value.append(vdu2  +sep+'INTERNAL' )
                new_key.append('type')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal2)
                new_parentKey.append(row[3])
                new_parentLevel.append(row[5])
                new_level.append(row[4])
                new_osm_lineage.append(row[7])

                new_value.append(vdu2 + sep +internal2)
                new_key.append('internal-connection-point-ref')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal2)
                new_parentKey.append(row[3])
                new_parentLevel.append(row[5])
                new_level.append(row[4])
                new_osm_lineage.append(row[7])


                new_value.append(vdu2 + sep+ 'PARAVIRT')
                new_key.append('type')
                index.append(i)
                new_lineage.append(row[6][:-1] +internal2)
                new_parentKey.append('virtual-interface')
                new_parentLevel.append(row[5]+1)
                new_level.append(row[4]+1)
                new_osm_lineage.append(row[7]+'|interface|0')
                
                j+=1
                
                continue  

            new_value.append(vdu + sep + internal)
            new_key.append('name')
            index.append(i)
            new_lineage.append(row[6][:-1] +external)
            new_parentKey.append(row[3])
            new_parentLevel.append(row[5])
            new_level.append(row[4])
            new_osm_lineage.append(row[7])

            new_value.append(vdu +sep+ str(j+1))
            new_key.append('position')
            index.append(i)
            new_lineage.append(row[6][:-1] +external)
            new_parentKey.append(row[3])
            new_parentLevel.append(row[5])
            new_level.append(row[4])
            new_osm_lineage.append(row[7])

            new_value.append(vdu  +sep+'EXTERNAL' )
            new_key.append('type')
            index.append(i)
            new_lineage.append(row[6][:-1] +external)
            new_parentKey.append(row[3])
            new_parentLevel.append(row[5])
            new_level.append(row[4])
            new_osm_lineage.append(row[7])

            new_value.append(vdu + sep +external)
            new_key.append('external-connection-point-ref')
            index.append(i)
            new_lineage.append(row[6][:-1] +external)
            new_parentKey.append(row[3])
            new_parentLevel.append(row[5])
            new_level.append(row[4])
            new_osm_lineage.append(row[7])


            new_value.append(vdu + sep+ 'PARAVIRT')
            new_key.append('type')
            index.append(i)
            new_lineage.append(row[6][:-1] +external)
            new_parentKey.append('virtual-interface')
            new_parentLevel.append(row[5]+1)
            new_level.append(row[4]+1)
            new_osm_lineage.append(row[7]+'|interface|0')

            j+=1
            
        new_df = df.loc[index,:].copy()
        new_df[column1] = new_value
        new_df[column2] = new_key
        new_df[column3] = new_parentKey
        new_df[column4] = new_level
        new_df[column5] = new_parentLevel
        new_df[column6] = new_lineage
        new_df[column7] = new_osm_lineage

        return new_df

    def son_vld_vnfd(self,df,sep=':'):
        '''
        Split the values of a column and expand so the new DataFrame has one split
        value per row. Filters rows where the column is missing.

        Params
        ------
        df : pandas.DataFrame
            dataframe with the column to split and expand
        sep : str
            the string used to split the column's values

        Returns
        -------
        pandas.DataFrame
            Returns a dataframe with the same columns as df.
        '''
        indexes = []
        new_values = []
        new_key = []
        new_parentKey = []
        new_parentLevel = []
        new_level = []
        new_lineage =[]
        
        df = df.dropna(subset=[column1])
        column1 = 'value'
        column2 = 'key'
        column3 = 'parent_key'
        column4 ='level'
        column5 = 'parent_level'
        column6 = 'lineage'
        
        for i, presplit in enumerate(df[[column1,column2,column3,column4,column5,column6]].itertuples()):

            if(isinstance(presplit[1],list)):
                j=0
                for item in presplit[1]:
                    values = str(item).split(sep) 
                    
                    if len(values) > 1:
                        
                        indexes.append(i) 
                        new_values.append(values[1])
                        new_key.append('id-ref')
                        new_parentKey.append('internal-connection-point')
                        new_level.append(5)
                        new_parentLevel.append(4)
                        new_lineage.append(presplit[6]+'|internal-vld|' + str(j))
                        j=j+1
            else:
                if(presplit[2] == 'id'):
                    new_values.append(presplit[1]+'-vld')
                    new_key.append(presplit[2])
                    indexes.append(i)
                    new_parentKey.append(presplit[3])
                    new_level.append(presplit[4])
                    new_parentLevel.append(presplit[5])
                    new_lineage.append(presplit[6])
                else:
                    indexes.append(i)
                    new_values.append(presplit[1])
                    new_key.append(presplit[2])
                    new_parentKey.append(presplit[3])
                    new_level.append(presplit[4])
                    new_parentLevel.append(presplit[5])
                    new_lineage.append(presplit[6])
          
        new_df = df.iloc[indexes, :].copy()
        new_df[column1] = new_values
        new_df[column2] = new_key
        new_df[column3] = new_parentKey
        new_df[column4] = new_level
        new_df[column5] = new_parentLevel
        new_df[column6] = new_lineage
        
        return new_df