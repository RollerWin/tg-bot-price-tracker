class CSSParser:
    WILDBERRIES_SITE = 'wildberries.ru'
    WILDBERRIES_SITE_RESERVE = 'www.wildberries.ru'
    WILDBERRIES_TITLE = "product-page__title"
    WILDBERRIES_PRICE = "price-block__final-price"

    MEGAMARKET_SITE = 'megamarket.ru'
    MEGAMARKET_SITE_RESERVE = 'www.megamarket.ru'
    MEGAMARKET_TITLE = "pdp-header__title"
    MEGAMARKET_PRICE = "sales-block-offer-price__price-final"

    OZON_SITE = 'ozon.ru'
    OZON_SITE_RESERVE = 'www.ozon.ru'
    OZON_TITLE = "tsHeadline550Medium"
    OZON_PRICE = "zl0_27"
    OZON_RESERVE_CLASS = "l5z_27"

    LAMODA_SITE = 'lamoda.ru'
    LAMODA_SITE_RESERVE = 'www.lamoda.ru'
    LAMODA_TITLE = "_modelName_1lw0e_21"
    LAMODA_PRICE = "_price_fow3x_11"

    def get_classes_wildberries(self):
        title_class = self.WILDBERRIES_TITLE
        price_class = self.WILDBERRIES_PRICE
        return title_class, price_class

    def get_classes_megamarket(self):
        title_class = self.MEGAMARKET_TITLE
        price_class = self.MEGAMARKET_PRICE
        return title_class, price_class

    def get_classes_ozon(self):
        title_class = self.OZON_TITLE
        price_class = self.OZON_PRICE
        return title_class, price_class

    def get_classes_lamoda(self):
        title_class = self.LAMODA_TITLE
        price_class = self.LAMODA_PRICE
        return title_class, price_class

    async def get_classes(self, netloc):
        match netloc:
            # case 'www.wildberries.ru' | 'wildberries.ru':
            case self.WILDBERRIES_SITE | self.WILDBERRIES_SITE_RESERVE:
                return self.get_classes_wildberries()
            # case 'www.megamarket.ru' | 'megamarket.ru':
            case self.MEGAMARKET_SITE | self.MEGAMARKET_SITE_RESERVE:
                return self.get_classes_megamarket()
            # case 'www.ozon.ru' | 'ozon.ru':
            case self.OZON_SITE | self.OZON_SITE_RESERVE:
                return self.get_classes_ozon()
            case self.LAMODA_SITE | self.LAMODA_SITE_RESERVE:
                return self.get_classes_lamoda()
            case _:
                raise ValueError("Unsupported website")

    async def get_reserve_class(self, netloc):
        match netloc:
            case self.OZON_SITE | self.OZON_SITE_RESERVE:
                return self.OZON_RESERVE_CLASS
