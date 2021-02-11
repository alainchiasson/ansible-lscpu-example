import os
import json

def get_lscpu():

    # Call lscpu and just return the output
    stream = os.popen('lscpu -J')
  
    # Convert from JSON to a python internal structure
    output = json.load(stream)
  
    # I'm converting the array to K,V pairs
    output['lscpu_data'] = {}


    for item in output['lscpu']:
      # Converts Array of Field:thing, data:value 
      # To Dictionary of Thing:Value
      # and strips leading and trailing :
      output['lscpu_data'][item['field'].strip(':')] = item['data']

    # I'm removing the original lscpu output
    # del(output['lscpu'])

    # only return the new dict
    return output['lscpu_data']

def main():
    lscpu = get_lscpu()
    print(lscpu['Architecture'])
    print(lscpu)


if __name__ == '__main__':
    main()
