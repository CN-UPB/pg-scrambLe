from nameko.rpc import rpc
import pandas as pd
import numpy as np
import yaml
import pymongo
from bson.objectid import ObjectId

class read_dict():

    def dict_parser(self,dictionary, key, level, pk):
        
        if isinstance(dictionary, dict):
            for k,v in dictionary.items():
                if isinstance(v,str) or isinstance(v, int):
                    result = [level-1,str(key),level,str(k),v,pk]
                    yield result
                    
                if isinstance(v, dict):
                    yield [level-1,str(key),level,str(k),None,None]
                    for res in self.dict_parser(v,k,level+1,pk):
                        yield res
                        
                elif isinstance(v, list):
                    if(isinstance(v[0],str)):
                        yield [level-1,str(key),level,str(k),v,pk]
                        for i in v:
                            for res in self.dict_parser(i,k,level+1,None):
                                yield res
                    else:
                        yield [level-1,str(key),level,str(k),None,None]
                        for j,i in enumerate(v):
                            for res in self.dict_parser(i,k,level+1,(10*(pk) + j+1)):
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

    
        parent_level = dataset[(dataset['level'] == level) & (dataset['value']!= 'NULL')]['parent_level'].unique()
        s=dataset[(dataset['level'] == level) & (dataset['value']!= 'NULL')].groupby(by=['parent_key']).agg({'key':lambda x: x.nunique() })
        s=s.to_dict()
            
        for parent,ele in s['key'].items():
            lvl_dict={}
            parent_key=[]
            
            lvl=list(dataset[(dataset['level'] == level) & (dataset['value']!= 'NULL') & (dataset['parent_key']== parent )][['id','key','value']].apply(lambda x : (x.id,x.key+' : '+str(x.value)), axis=1).values)
            lvl_dict.update(self.append_dict(parent,sorted(lvl,key=self.getKey),{}))
            parent_key.append(np.unique(dataset[(dataset['key'] == parent) & (dataset['level'] == parent_level[0])  & (dataset['value']== 'NULL')]['parent_key'].values))
            
            yield parent_key, lvl_dict
        
        
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
            for key,val in self.make_json(dataset, level):
                if len(key[0]) >= 1:
                    if not full_dict:
                        full_dict[key[0][0]] = val
                    else:
                        full_dict = self.reverse_loop(full_dict, key[0][0], val)
                elif len(key[0])==0 and level == 1:
                    full_dict = val

        return full_dict

    def translate_nsd(self,ds):
        return self.write(ds,range(8))

class mapping_logic():

    def sub_ds(self,df,parent,level) :   
        
        new_df = pd.DataFrame(columns=['parent_level','parent_key','level','key','value','id'])
       
        for index, row in df[(df['parent_key']==parent) & (df['level'] == level)].iterrows():
            
            new_df = new_df.append(row)
            
        return new_df

    def search_sub_ds(self,df,parent,level):
        
        if len(df[(df['parent_key'] == parent) & (df['level'] == level) & (df['value'] == 'NULL')]['key'].values) > 0:
            return df[(df['parent_key'] == parent) & (df['level'] == level) & (df['value'] == 'NULL')]['key'].values
        else:
            return []
        
    def ds_loop(self,ds,parent,level):  
        
        yield self.sub_ds(ds,parent,level)
        
        if len(self.search_sub_ds(ds,parent,level)) > 0:
            for k in np.unique(self.search_sub_ds(ds,parent,level)):
                for item in self.ds_loop(ds,k,level+1):
                    yield item
                    
    def ret_ds(self,ds,key,level):
    
        temp=list(self.ds_loop(ds,key,level))
        temp_ds=pd.DataFrame(columns=['parent_level','parent_key','level','key','value','id'])
        for i in range(len(temp)):
            temp_ds = pd.concat([temp_ds,temp[i]],axis=0)
        return temp_ds




    def osm_fwdg(self,df):
        
        temp = df[df['parent_key'].isin(['vnfd-connection-point-ref','classifier']) & 
               df['key'].isin(['vnfd-connection-point-ref','member-vnf-index-ref'])].groupby(
               ['parent_level','parent_key','level','id'])['value'].apply(
               lambda x : ':'.join(x.astype(str)) ).reset_index()
        
        temp = temp.assign(**{'key':'connection_point_ref', 
                              'parent_key': 'connection_points',
                              'level':6, 
                              'parent_level': 5
                             })
        
        temp['id'] = (1000*1 +100 *1 + 10 *1 + temp.index) + 1
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
                   ['parent_key','parent_level','level','id']).agg({'value':lambda x : ':'.join(x.values.astype('str')) }).reset_index()

        temp['id'] = temp.apply(lambda x : int(x['id'])/10,axis=1 )
        temp = temp.groupby(['parent_key','parent_level','level','id']).agg({'value': 
                                                                             lambda x : 
                                                                             [','.join(x.values.astype('str'))] }).reset_index()

        temp = temp.assign(**{'key':'connection_points_reference', 
                                  'parent_key': 'virtual_links',
                                  'level':4, 
                                  'parent_level': 3
                                 }) 

        df = df.drop(df[df['parent_key'].isin(['vnfd-connection-point-ref']) & 
               df['key'].isin(['vnfd-connection-point-ref','vnfd-id-ref','member-vnf-index-ref'])].index,axis=0)
        return df.append(temp) 



    def son_fwdg(self,df, column1,column2, sep=':', keep=False):
        """
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
        """
        indexes = list()
        new_values = list()
        new_values2 = list()
        df = df.dropna(subset=[column1])
        for i, presplit in enumerate(df[[column1,column2]].itertuples()):
            #print str(presplit[1]),str(presplit[2])
            values = str(presplit[1]).split(sep)
            #print values ,len(values) 
            if keep and len(values) > 1:
                indexes.append(i)
                new_values.append(str(presplit[1]))
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
        return new_df.drop_duplicates()



    def son_vld(self,df, column1,column2, sep=':', keep=False):
        """
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
        """
        indexes = list()
        new_values = list()
        new_values2 = list()
        df = df.dropna(subset=[column1])
        for i, presplit in enumerate(df[[column1,column2]].itertuples()):
            #print type(presplit[1]),str(presplit[1])
            if(isinstance(presplit[1],list)):
                for item in presplit[1]:
                    values = str(item).split(sep)
                    #print values ,len(values) 
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
        #print len(indexes) ,len(new_values2)
        new_df = df.iloc[indexes, :].copy()
        new_df[column1] = new_values
        new_df[column2] = new_values2
        return new_df.drop_duplicates()


class insert_into_db():

    def insert_mapping(self, record):

        osm_sonata_nsd_mapping= [
                        [2,3,'nsd','description',0,1,'root','description'],
                        [2,3,'nsd','vendor',0,1,'root','vendor'],
                        [2,3,'nsd','name',0,1,'root','name'],
                        [2,3,'nsd','version',0,1,'root','version'],
                        
                        
                        [3,4,'constituent-vnfd','member-vnf-index',1,2,'network_functions','vnf_id'],
                        [3,4,'constituent-vnfd','vnfd-id-ref',1,2,'network_functions','vnf_name'],
                        
                        
                        [3,4,'connection-point','name',1,2,'connection_points','id'],
                        [3,4,'connection-point','type',1,2,'connection_points','type'],
                        
                        
                        [3,4,'monitoring-param','description',1,2,'monitoring_parameters','description'],
                        [3,4,'monitoring-param','units',1,2,'monitoring_parameters','unit'],
                        [3,4,'monitoring-param','value-integer',1,2,'monitoring_parameters','metric'],

                            ]
        osm_sonata_vld_mapping= [
    
                        [3,4,'vld','id',1,2,'virtual_links','id'],
                        [3,4,'vld','type',1,2,'virtual_links','connectivity_type'],
                        [3,4,'virtual_links','connection_points_reference',1,2,'virtual_links','connection_points_reference'],  
                        [4,5,'vnfd-connection-point-ref','member-vnf-index-ref',1,2,'virtual_links','member-vnf-index-ref'],
                        [4,5,'vnfd-connection-point-ref','vnfd-connection-point-ref',1,2,'virtual_links','vnfd-connection-point-ref'],
                        
                    ]


        osm_sonata_vnffgd_mapping= [
            
                        [3,4,'vnffgd','id',1,2,'forwarding_graphs','fg_id'],
                        [5,6,'vnfd-connection-point-ref','member-vnf-index-ref',3,4,'connection_points','member-vnf-index-ref'],
                        [5,6,'vnfd-connection-point-ref','vnfd-connection-point-ref',3,4,'connection_points','vnfd-connection-point-ref'],
                        [5,6,'vnfd-connection-point-ref','order',3,4,'connection_points','position'],
                        [5,6,'connection_points','connection_point_ref',3,4,'connection_points','connection_point_ref'],
                        [4,5,'rsp','id',2,3,'network_forwarding_paths','fp_id'],

                    ]
        mapping = pd.DataFrame(osm_sonata_nsd_mapping,
                                  columns=["osm_parent_level", "osm_level", "osm_parent_key", "osm_key",
                                           "son_parent_level", "son_level", "son_parent_key", "son_key"]).sort_values(
            by=['son_level', 'osm_level'], ascending=True)

        osm_son_vld=pd.DataFrame(osm_sonata_vld_mapping , 
             columns=["osm_parent_level","osm_level","osm_parent_key","osm_key",
                      "son_parent_level","son_level","son_parent_key","son_key"]).sort_values(by=['son_level','osm_level'],ascending=True)


        osm_son_vnffgd=pd.DataFrame(osm_sonata_vnffgd_mapping , 
                     columns=["osm_parent_level","osm_level","osm_parent_key","osm_key",
                              "son_parent_level","son_level","son_parent_key","son_key"]).sort_values(by=['son_level','osm_level'],ascending=True)
        
        mapping.index = [str(i) for i in mapping.index]
        osm_son_vld.index = [str(i) for i in osm_son_vld.index]
        osm_son_vnffgd.index = [str(i) for i in osm_son_vnffgd.index]
        
        temp = mapping.to_dict()
        id = record.insert(temp)
        
        temp = osm_son_vld.to_dict()
        id = record.insert(temp)
        
        temp = osm_son_vnffgd.to_dict()
        id = record.insert(temp)
        #return id


    def insert_nsd(self, record):

        pass
        

class TranslatorService():
    name = "translator_service"
        
    @rpc
    def hello(self, name):

        client = pymongo.MongoClient('mongodb://mongo:27017/')
        db = client.mapping_nsd
        record = db.nsd_test2
        
        
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

        
        res = record.find()
        
        t = [i for i in res]
        
        if(len(t) ==0):
            insert = insert_into_db()
            insert.insert_mapping(record)
            
            res = record.find()
            t = [i for i in res]
        
        else:
            pass        
        
        map= mapping_logic()
        
        if name =='son_to_osm':
                
            osm_sonata = pd.DataFrame.from_dict(t[0])
            osm_son_vld = pd.DataFrame.from_dict(t[1])
            osm_son_vnffgd = pd.DataFrame.from_dict(t[2])
            
            dataset=pd.merge(sonata_dataset,osm_sonata,
                             left_on=['key','parent_key','level','parent_level'],
                             right_on=['son_key','son_parent_key','son_level','son_parent_level'],how='inner')
            dataset.fillna('NULL',inplace=True)
            dataset = dataset[['osm_parent_level','osm_level','osm_parent_key','osm_key','value','id']]
            dataset.columns = ['parent_level','level','parent_key','key','value','id']
            dataset=dataset.append(pd.DataFrame([[2,'nsd',3,'vnffgd','NULL','NULL'],
                                                [2,'nsd',3,'constituent-vnfd','NULL','NULL'],
                                                [2,'nsd',3,'vld','NULL','NULL'],
                                                [2,'nsd',3,'connection-point','NULL','NULL'],
                                                [0,'root',1,'nsd:nsd-catalog','NULL','NULL'],
                                                [1,'nsd:nsd-catalog',2,'nsd','NULL','NULL']],
                                               columns = ['parent_level','parent_key','level','key','value','id']))


            df = map.ret_ds(sonata_dataset,'virtual_links',2)
            df2_son = map.son_vld(df,'value','key',':')

            df_son_vld = pd.merge(df2_son,osm_son_vld,
                             left_on=['key','parent_key','level','parent_level'],
                             right_on=['son_key','son_parent_key','son_level','son_parent_level'],how='inner')

            df_son_vld =  df_son_vld[['osm_parent_level','osm_level','osm_parent_key','osm_key','value','id']]
            df_son_vld.columns = ['parent_level','level','parent_key','key','value','id']
            df_son_vld = df_son_vld.append(pd.DataFrame([[3,'vld',4,'vnfd-connection-point-ref','NULL','NULL'],
                                                        ],
                                      columns = ['parent_level','parent_key','level','key','value','id']))

            dataset = dataset.append(df_son_vld)





            df=map.ret_ds(sonata_dataset,'forwarding_graphs',2)
            df2_son=map.son_fwdg(df,'value','key',':')
            df_son_vnffgd = pd.merge(df2_son,osm_son_vnffgd,
                             left_on=['key','parent_key','level','parent_level'],
                             right_on=['son_key','son_parent_key','son_level','son_parent_level'],how='inner')
            df_son_vnffgd =  df_son_vnffgd[['osm_parent_level','osm_level','osm_parent_key','osm_key','value','id']]
            df_son_vnffgd.columns = ['parent_level','level','parent_key','key','value','id']
            df_son_vnffgd = df_son_vnffgd.append(pd.DataFrame([[3,'vnffgd',4,'rsp','NULL','NULL'],
                                                              [4,'rsp',5,'vnfd-connection-point-ref','NULL','NULL']],
                                      columns = ['parent_level','parent_key','level','key','value','id']))


            dataset = dataset.append(df_son_vnffgd)
            dataset.drop_duplicates(inplace=True)

            writer = write_dict()
            
            message = str(writer.translate_nsd(dataset))

        elif name =='osm_to_son':
            
            osm_sonata = pd.DataFrame.from_dict(t[0])
            osm_son_vld = pd.DataFrame.from_dict(t[1])
            osm_son_vnffgd = pd.DataFrame.from_dict(t[2])
            
            
            dataset=pd.merge(osm_dataset,osm_sonata,
                             left_on=['key','parent_key','level','parent_level'],
                             right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')
            dataset.fillna('NULL',inplace=True)
            dataset = dataset[['son_parent_level','son_level','son_parent_key','son_key','value','id']]
            dataset.columns = ['parent_level','level','parent_key','key','value','id']
            dataset=dataset.append(pd.DataFrame([['NULL','virtual_links',1,'root',0,'NULL'],
                                                ['NULL','network_functions',1,'root',0,'NULL'],
                                                ['NULL','forwarding_graphs',1,'root',0,'NULL'],
                                                ['NULL','connection_points',1,'root',0,'NULL'],
                                                ['https://raw.githubusercontent.com/sonata-nfv/tng-schema/master/service-descriptor/nsd-schema.yml','description_schema',1,'root',0,1]],
                                               columns = ['value','key','level','parent_key','parent_level','id']))



            df = map.ret_ds(osm_dataset,'vld',4)
            df_osm = map.osm_vld(df)
            df_osm_vld = pd.merge(df_osm,osm_son_vld,
                             left_on=['key','parent_key','level','parent_level'],
                             right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')

            df_osm_vld =  df_osm_vld[['son_parent_level','son_level','son_parent_key','son_key','value','id']]
            df_osm_vld.columns = ['parent_level','level','parent_key','key','value','id']

            dataset= dataset.append(df_osm_vld)


            df =map.ret_ds(osm_dataset,'vnffgd',4)
            if not df.empty:
                df_osm= map.osm_fwdg(df)
                df_osm_vnffgd = pd.merge(df_osm,osm_son_vnffgd,
                                 left_on=['key','parent_key','level','parent_level'],
                                 right_on=['osm_key','osm_parent_key','osm_level','osm_parent_level'],how='inner')
                df_osm_vnffgd =  df_osm_vnffgd[['son_parent_level','son_level','son_parent_key','son_key','value','id']]
                df_osm_vnffgd.columns = ['parent_level','level','parent_key','key','value','id']
                df_osm_vnffgd = df_osm_vnffgd.append(pd.DataFrame([[2,'network_forwarding_paths',3,'connection_points','NULL','NULL'],
                                                                  [1,'forwarding_graphs',2,'network_forwarding_paths','NULL','NULL']],
                                           columns = ['parent_level','parent_key','level','key','value','id']))


                dataset = dataset.append(df_osm_vnffgd)
                vl_val = dataset[(dataset['parent_key'] == 'virtual_links') & 
                        (dataset['key'] == 'id')].groupby(['key']).agg({'value' : lambda x : list(x)})['value'][0]
                nf_val = dataset[(dataset['parent_key'] == 'network_functions') & 
                        (dataset['key'] == 'vnf_id')].groupby(['key']).agg({'value' : lambda x : list(x)})['value'][0]

                dataset = dataset.append(pd.DataFrame([[1,'forwarding_graphs',2,'constituent_virtual_links',vl_val,1],
                                                       [1,'forwarding_graphs',2,'constituent_vnfs',nf_val,1],
                                                        [1,'forwarding_graphs',2,'number_of_virtual_links',len(vl_val),1],
                                            ],
                                           columns = ['parent_level','parent_key','level','key','value','id']))


            writer = write_dict()
            
            message = str(writer.translate_nsd(dataset))
            
        else:
            message='Sorry still working on that!!!! '

        return message

    