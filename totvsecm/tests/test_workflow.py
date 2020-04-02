
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
            id_processo='teste_servicedesk'
        )

    def test_iniciar_solicitacao(self):
        formulario = dict(
            email='quigonjinn@jeditemple.com',
            solicitacao='Mey the force be with you'
        )
        resultado = self.service.iniciar_solicitacao(
            dados_formulario=formulario,
            ids_destinatarios=['teste_servicedesk'],
            comentarios='Iniciado via formulário web'
        )
        print(resultado)
        self.assertTrue(True)
