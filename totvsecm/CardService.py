
from zeep import Client


class CardService:
    def __init__(self, server, user, password, company_id, user_id, process_id=None):
        self.url = 'http://%s/webdesk/CardService?wsdl' % server
        self.client = Client(self.url)
        self.user = user
        self.password = password
        self.company_id = company_id
        self.user_id = user_id
        self.process_id = process_id

    def __get_card_data(self, data):
        """Transforma o dicionário em parâmetros."""

        if bool(data):
            # Obtém classes do webservice.
            try:
                cf_dto_array = self.client.get_type('ns0:cardFieldDtoArray')
                cf_dto = self.client.get_type('ns0:cardFieldDto')
            except:
                cf_dto_array = self.client.get_type('ns1:cardFieldDtoArray')
                cf_dto = self.client.get_type('ns1:cardFieldDto')

            fields = []
            for k, v in data.items():
                field = cf_dto(field=k, value=v)
                fields.append(field)

            # Transforma o dicionário recebido nos objetos do webservice.
            parametros = cf_dto_array(item=fields)
            return parametros
        else:
            return {}

    def update_card_data(self, card_id, card_data):
        """Retorna o byte do arquivo físico de um documento, caso o usuário tenha permissão para acessá-lo."""
        result = self.client.service.updateCardData(self.company_id, self.user, self.password,  card_id,
                                                    cardData=self.__get_card_data(card_data))
        return result
