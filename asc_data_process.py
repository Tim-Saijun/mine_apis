import numpy as np
import os
from collections import defaultdict
import pandas as pd

def asc_2_npz(source_dir: str, target_dir: str) -> dict:
    """Convert asc data to npz data
    Args:
        source_dir: Source folder/file
        target_dir: Output folder
    Return:
        file names : pd.DataFrame
    """
    
    assert os.path.exists(source_dir),f"source_dir not exist:{source_dir}"
    # Target direction
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    # Asc files
    if os.path.isdir(source_dir):
        asc_file_list = list(
            filter(lambda x: '.asc' in x.lower(), os.listdir(source_dir)))
    else:
        asc_file_list=list(
            filter(lambda x: '.asc' in x.lower(), [os.path.split(source_dir)[1]]))
        source_dir=os.path.split(source_dir)[0]
    record_list = []
    save_fname_list=[]
    # Processing
    for file_name in asc_file_list:

        with open(os.path.join(source_dir, file_name), 'r') as f:
            # Data of 8 channels
            data_cols = defaultdict(list)
            row_count = 0
            for line in f.readlines()[1:]:
                # Delete space char
                row_data_list = line.strip('\n').split()
                if '' in row_data_list:
                    continue
                row_data_list = [float(x) for x in row_data_list]
                # Save in dict
                for i in range(len(row_data_list)):
                    data_cols[i].append([0., 0., row_data_list[i]])
                row_count += 1
            print(file_name, ':', row_count)
            for k in data_cols.keys():
                save_name = '{}_{}.npz'.format(file_name, k)
                save_name=save_name.replace(' ', '_')
                save_fname_list.append(save_name)
                npz_file_path=os.path.join(target_dir, save_name)
                np.savez(npz_file_path, data=np.array(data_cols[k]))
                # map_file_len[save_name] = row_count
                record_list.append({"fname":save_name,"itp":"","its":"","channels":""})
    print(len(data_cols[0]),len(data_cols[1]))
    return pd.DataFrame(record_list),save_fname_list


def generate_csv(name:str, target_dir=''):
    
    csv_name=name+".csv"
    header = 'fname,itp,its,channels\n'
    body = name + ',' + '' + ',' + '' + ',' + '' + '\n'
    file_path=os.path.join(target_dir, csv_name)
    with open(file_path, 'w') as f:
        f.write(header + body)
    print('CSV file saved:',file_path)
    return file_path



# def generate_df(record_list:list):
#     df=pd.DataFrame(record_list)
#     # df.columns=[]
#     for name, count in map_file_len.items():
#         df.loc[df.shape[0],"fname"]=name
#     return df
    

def process(source_dir,target_dir,rtype):
    
    fname_df,save_fname_list = asc_2_npz(source_dir=source_dir, target_dir=target_dir)
    if rtype.lower()=='df':
        return fname_df
    elif rtype.lower()=='csv':
        csv_path_list=[]
        for fname in save_fname_list:
            fpath=generate_csv(name=fname,target_dir=target_dir)
            csv_path_list.append(fpath)
        return csv_path_list
    else:
        raise ValueError("Parameter 'rtype' must be 'csv' or 'df'")

if __name__ == '__main__':
    source_dir = r"2020-12-01 16.37.17 095.W.asc"
    target_dir = r"Npz_data"
    # map_file_len = asc_2_npz(source_dir=source_dir, target_dir=target_dir)
    # generate_csv(map_file_len=map_file_len, csv_name='waveform_asc.csv')
    df=process(source_dir,target_dir,rtype='csv')
    p = generate_csv('waveform_asc.csv',target_dir=target_dir)
    print(p)
