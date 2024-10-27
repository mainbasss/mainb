from Promotion.stream_promotion import StreamPromotionAPI
from Promotion.justanotherpanel import JastAnotherPanelAPI
import random

class PromotionManager:
    def __init__(self):
        self.stream_api = StreamPromotionAPI()
        self.justanother_api = JastAnotherPanelAPI()


    def distribute_views(self, link, total_views):

        # Допустим, 10% через Stream Promotion
        #stream_views = int(total_views * 0.1)
        diap = total_views.split(' ')
        total_views = random.randint(int(diap[0]), int(diap[1]))
        print('manager total_views', total_views)
        stream = self.stream_api.create_order(link=link, value=int(total_views*0.33))
        justanotherpanel = self.justanother_api.create_order(link=link, value=int(total_views*0.66))
        print('####### stream',stream)
        print('####### justanotherpanel',justanotherpanel)
        # Остальные просмотры через другой сервис
        # self.justanother_api.create_order(...)
