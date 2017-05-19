# -*- coding: utf-8 -*-

from zeep import Client


class DocumentService:
    def __init__(self, server, user, password, company_id, user_id, process_id=None):
        self.url = 'http://%s/webdesk/DocumentService?wsdl' % server
        self.client = Client(self.url)
        self.user = user
        self.password = password
        self.company_id = company_id
        self.user_id = user_id
        self.process_id = process_id

    def get_active_document(self, nr_document_id, colleague_id):
        """Retorna um documento ativo.

        Args:
            nr_document_id(int): Número do documento.
            colleague_id(str): Matrícula do colaborador.

        Returns:
            list: Informações do documento.
        """
        result = self.client.service.getActiveDocument(self.user, self.password, self.company_id, nr_document_id,
                                                       colleague_id)
        return result

    def get_document_content(self, nr_document_id, colleague_id, documento_versao, nome_arquivo):
        """Retorna o byte do arquivo físico de um documento, caso o usuário tenha permissão para acessá-lo.

        Args:
            nr_document_id(int): Número do documento.
            colleague_id(str): Matrícula do colaborador.
            documento_versao(int): Número da versão do documento.
            nome_arquivo(str): Nome do arquivo.

        Returns:
            str: Conteúdo do documento.
        """
        result = self.client.service.getDocumentContent(self.user, self.password, self.company_id, nr_document_id,
                                                        colleague_id,
                                                        documento_versao,
                                                        nome_arquivo)
        return result
