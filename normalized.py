def convertTrainedDataArr(lstData):
    tData = []
    for doc in lstData:
        temp_value = ''
        temp_cat = ''
        for key, value in doc.items():
            
            if key =='data_field':
                if len(value) != 0: 
                    temp_value = str(value).strip()
            if key == 'data_category':
                if len(value) != 0: 
                    temp_cat = str(value).strip()
        if temp_value and temp_cat:
            tData.append((temp_value, temp_cat))

    return tData


def convertCategoryDataArr(lstData):
    cData = []
    for cat in lstData:
        for key, value in cat.items():
            if key == 'name' and value:
                cData.append(str(value).strip())
    
    return cData
