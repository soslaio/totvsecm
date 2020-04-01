
import os
from unittest import TestCase
from totvsecm.BaseService import BaseService

URL_SERVIDOR = os.environ.get('URL_SERVIDOR')


class WorkflowServiceTest(TestCase):
    def setUp(self):
        self.service = BaseService(
            url_servidor='http://ecmhomolog.pa.sebrae.com.br/',
            usuario='teste_servicedesk',
            senha='teste_servicedesk',
            usuario_responsavel='teste_servicedesk',
            id_processo=''
        )
