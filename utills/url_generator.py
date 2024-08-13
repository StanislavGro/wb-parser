class GenerateImgUrl:
  def __init__(self, nmId, photoSize="big", photoNumber=1, format="webp"):
    if not isinstance(nmId, int) or nmId < 0:
      raise ValueError("Invalid nmId value")
    self.nmId = nmId
    self.size = photoSize
    self.number = photoNumber
    self.format = format

  def getHost(self, id):
    url_parts = [
      {"range": [0, 143], "url": "//basket-01.wbbasket.ru"},
      {"range": [144, 287], "url": "//basket-02.wbbasket.ru"},
      {"range": [288, 431], "url": "//basket-03.wbbasket.ru"},
      {"range": [432, 719], "url": "//basket-04.wbbasket.ru"},
      {"range": [720, 1007], "url": "//basket-05.wbbasket.ru"},
      {"range": [1008, 1061], "url": "//basket-06.wbbasket.ru"},
      {"range": [1062, 1115], "url": "//basket-07.wbbasket.ru"},
      {"range": [1116, 1169], "url": "//basket-08.wbbasket.ru"},
      {"range": [1170, 1313], "url": "//basket-09.wbbasket.ru"},
      {"range": [1314, 1601], "url": "//basket-10.wbbasket.ru"},
      {"range": [1602, 1655], "url": "//basket-11.wbbasket.ru"},
      {"range": [1656, 1919], "url": "//basket-12.wbbasket.ru"},
      {"range": [1920, 2045], "url": "//basket-13.wbbasket.ru"},
      {"range": [2046, 2189], "url": "//basket-14.wbbasket.ru"},
      {"range": [2190, 2405], "url": "//basket-15.wbbasket.ru"},
      {"range": [2406, 2621], "url": "//basket-16.wbbasket.ru"},
      {"range": [2622, float('inf')], "url": "//basket-17.wbbasket.ru"},
    ]

    for part in url_parts:
      if id >= part["range"][0] and id <= part["range"][1]:
        return part["url"]

  def url(self):
    vol = self.nmId // 100000
    part = self.nmId // 1000
    return f"https:{self.getHost(vol)}/vol{vol}/part{part}/{self.nmId}/images/{self.size}/{self.number}.{self.format}"
