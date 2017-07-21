import os

def get_all_cape_cod_zip_codes():
    cape_zip_path = os.path.join(os.path.dirname(__file__), "data/cape_cod_zip_codes.txt")
    zip_dict = {}
    with open(cape_zip_path) as f:
        txt = f.readlines()
        for line in txt:
            town, zipcode = line.split("-")
            zip_dict[town.strip()] = zipcode.strip()

    return zip_dict

if __name__ == "__main__":
   print(get_all_cape_cod_zip_codes())
