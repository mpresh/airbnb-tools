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


def get_all_newport_zip_codes():
    return {"Newport": "02840"}


def get_all_nantucket_zip_codes():
    return {"Nantucket1": "02554",
            "Nantucket2": "02564",
            "Nantucket3": "02584"}


def get_all_marthas_vinyard_zip_codes():
    return {"Chilmark": "02535",
            "Edgartown": "02539",
            "OakBluffs": "02557",
            "Tisbury": "02568",
            "WestTisbury": "02575"}


if __name__ == "__main__":
   print(get_all_cape_cod_zip_codes())
